"""Generate SQE Daily's static pages using only Python's standard library."""
import argparse
import hashlib
import html
import json
import re
import shutil
import practice_content
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://sqedaily.co.uk'
# Only needed if Bing's import from Search Console fails to verify the site.
BING_VERIFICATION = ''
ORGANIZATION = {'@type': 'Organization', '@id': BASE + '/#organization', 'name': 'SQE Daily', 'url': BASE + '/', 'logo': BASE + '/assets/mark.svg', 'email': 'hello@sqedaily.co.uk'}
# Official SRA FLK subjects as named in the bank. Slugs are frozen: never edit one that is published.
SUBJECTS = {
    'Business Law & Practice': 'business-law-practice',
    'Dispute Resolution': 'dispute-resolution',
    'Contract': 'contract',
    'Tort': 'tort',
    'Legal System of England and Wales': 'legal-system-of-england-and-wales',
    'Constitutional & Administrative Law': 'constitutional-administrative-law',
    'Legal Services': 'legal-services',
    'Ethics & Professional Conduct': 'ethics-professional-conduct',
    'Property Practice': 'property-practice',
    'Wills & Administration of Estates': 'wills-administration-of-estates',
    'Solicitors Accounts': 'solicitors-accounts',
    'Land Law': 'land-law',
    'Trusts': 'trusts',
    'Criminal Law': 'criminal-law',
    'Criminal Practice': 'criminal-practice',
}
# content/pages.json pages (slug: eyebrow). Each is built only while its exact copy is approved.
PAGES = {'sqe1-practice-questions': 'SQE1 PRACTICE', 'flk1': 'SQE1 · FLK1', 'flk2': 'SQE1 · FLK2', 'sqe1-exam-dates': 'SQE1 EXAM DATES', 'editorial-standards': 'SQE DAILY'}
PAPERS = {'flk1': 'FLK1', 'flk2': 'FLK2'}
# The countdown's existing sitting, used until an approved sitting is added to content/pages.json.
DEFAULT_SITTING = {'label': 'January 2027', 'flk1_date': '2027-01-11', 'flk2_date': '2027-01-18'}
LOCK = 'content/routes.lock.json'
# Fields a content hash ignores: they change no visible page text (last_reviewed is a check, not an edit).
HASH_IGNORED = {'tags', 'last_reviewed', 'last_modified', 'route', 'modified', 'available_from', 'session', 'context_subject'}
APPROVAL_FIELDS = {'approved', 'approved_hash'}
# Approved subject introductions render on subject archives, so their changes are modifications.
SUBJECT_INTROS_LIVE = True
OWNED = ['index.html', '404.html', 'q', 'archive', 'tests', 'about', 'sponsor', 'privacy', *PAGES, 'guides', 'sitemap.xml', 'feed.xml', 'robots.txt']
RECENT = 5
RELATED = 3
LATEST = 10
NAV = '<nav aria-label="Main navigation">' + ''.join(f'<a href="{url}">{name}</a>' for name, url in [('Today', '/'), ('Library', '/archive/'), ('Tests', '/tests/'), ('About', '/about/'), ('Sponsor', '/sponsor/'), ('Privacy', '/privacy/')]) + '</nav>'
# Without JavaScript the homepage shows the worked answer below the options; the style lives in <head>.
NOSCRIPT_STYLE = '<noscript><style>#result[hidden]{display:block!important}</style></noscript>'
NOSCRIPT_NOTE = '<noscript><p>The worked answer is below the options.</p></noscript>'
WRONG_LINE = re.compile(r'^[A-E] is wrong\b')
esc = lambda value: html.escape(str(value), quote=True)

def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def route(q):
    """The route a question receives when first published. Afterwards the lock file decides."""
    prefix = q['id'] if q.get('library_number') else q['number']
    return f'/q/{prefix}-{slug(q["title"])}/'

def question_number(q):
    return f'L{q["library_number"]:03}' if q.get('library_number') else f'{q["number"]:02}'

def load_bank():
    bank = json.loads((ROOT / 'content/questions.json').read_text())
    library_path = ROOT / 'content/library.json'
    library = json.loads(library_path.read_text()) if library_path.exists() else []
    for q in library:
        if q.get('publish_date') is not None or not re.fullmatch(r'lib-[a-z]+-\d{3}', q.get('id', '')) or not isinstance(q.get('library_number'), int) or q['library_number'] < 1 or q['number'] != -q['library_number']:
            raise ValueError('Library questions need stable library IDs/numbers and no daily date')
    if any(q['number'] < 1 for q in bank):
        raise ValueError('Daily issue numbers must be positive')
    return bank + library

def subject_questions(subject):
    """'Contract practice questions', but 'Property Practice questions' rather than a doubled word."""
    return f'{subject} questions' if subject.endswith('Practice') else f'{subject} practice questions'

def published(bank, day):
    return sorted((q for q in bank if q['publish_date'] and q['publish_date'] <= day), key=lambda q: (q['publish_date'], q['number']))

def london_today():
    return datetime.now(ZoneInfo('Europe/London')).date().isoformat()

def long_date(value):
    d = date.fromisoformat(value)
    return f'{d.day} {d:%B %Y}'

def summary(text, limit=150):
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(' ', 1)[0].rstrip(',;:') + '…'

LINK = re.compile(r'\[([^\]]+)\]\(((?:https://|mailto:|/)[^)\s]*)\)')
# Paths of approved copy pages built in this run; rich() links to unbuilt pages render as plain text.
LIVE_PATHS = set()

def internal_live(path):
    path = path.split('#')[0]
    return path == '/' or path.startswith(('/q/', '/archive/')) or path in LIVE_PATHS

def rich(text):
    """Escape page copy, keeping blank-line paragraphs and [text](https://…, mailto: or /path) links."""
    def link(m):
        label, href = m.group(1), m.group(2)
        return label if href.startswith('/') and not internal_live(href) else f'<a href="{href}">{label}</a>'
    return ''.join('<p>' + LINK.sub(link, esc(paragraph)).replace('\n', '<br>') + '</p>' for paragraph in text.strip().split('\n\n'))

def explanation_html(q):
    paragraphs = q['explanation'].split('\n\n')
    if not q.get('why_wrong'):
        return ''.join(f'<p>{esc(p)}</p>' for p in paragraphs)
    kept = ['\n'.join(line for line in p.split('\n') if not WRONG_LINE.match(line)) for p in paragraphs]
    return ''.join(f'<p>{esc(p)}</p>' for p in kept if p) + ''.join(f'<p>Why {k} is wrong: {esc(v)}</p>' for k, v in sorted(q['why_wrong'].items()))

def content_hash(entry, ignored):
    return hashlib.sha256(json.dumps({k: v for k, v in entry.items() if k not in ignored}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def is_approved(entry):
    """Approval covers the exact text approved: any later edit needs approving again."""
    return entry.get('approved') is True and entry.get('approved_hash') == content_hash(entry, APPROVAL_FIELDS)

def approval_entries(data):
    yield from ((f'sittings.{i}', entry) for i, entry in enumerate(data.get('sittings', [])))
    for kind in ['pages', 'guides', 'subjects']:
        yield from ((f'{kind}.{name}', entry) for name, entry in data.get(kind, {}).items())

def stale_approvals(data):
    return [label for label, entry in approval_entries(data) if entry.get('approved') is True and not is_approved(entry)]

def approve(label, expect=None):
    """Record the owner's approval of one content/pages.json entry, bound to its current text.

    expect is the fingerprint shown in docs/editorial-approval-batch.md; approval is refused if the
    text has changed since the owner saw it.
    """
    path = ROOT / 'content/pages.json'
    data = json.loads(path.read_text())
    load_pages(london_today())
    entries = dict(approval_entries(data))
    if label not in entries:
        raise SystemExit(f'No entry {label}; choose from: {", ".join(entries)}')
    digest = content_hash(entries[label], APPROVAL_FIELDS)
    if expect and not digest.startswith(expect):
        raise SystemExit(f'{label} has changed since it was presented for approval ({expect}); present the current text again.')
    entries[label]['approved'] = True
    entries[label]['approved_hash'] = digest
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Approved {label}.')

def write(path, content):
    target = ROOT / path.lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix == '.html':
        for name in ['app.js', 'site.js', 'config.js', 'styles.css', 'test-core.js', 'tests.js', 'tests.css']:
            if not (ROOT / 'assets' / name).exists():
                continue
            version = hashlib.sha256((ROOT / 'assets' / name).read_bytes()).hexdigest()[:12]
            content = re.sub(r'((?:src|href)="/assets/' + re.escape(name) + r')(?:\?[^" ]*)?"', rf'\1?v={version}"', content)
    target.write_text('\n'.join(line.rstrip() for line in content.splitlines()) + '\n', encoding='utf-8')

def check_date(value, label, today, earliest=None):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f'{label} must be an ISO date')
    date.fromisoformat(value)
    if value > today:
        raise ValueError(f'{label} cannot be in the future')
    if earliest and value < earliest:
        raise ValueError(f'{label} cannot be before {earliest}')

def validate_bank(bank, today):
    ids, numbers, paths = set(), set(), set()
    for q in bank:
        for field in ['id', 'number', 'publish_date', 'subject', 'flk', 'difficulty', 'title', 'scenario', 'stem', 'options', 'answer', 'explanation', 'key_rule', 'authority', 'verified_source_url']:
            if field not in q:
                raise ValueError(f'Missing {field}: {q.get("id")}')
        if q['publish_date'] is not None:
            datetime.strptime(q['publish_date'], '%Y-%m-%d')
        if q['id'] in ids or q['number'] in numbers or route(q) in paths:
            raise ValueError('Duplicate question id, number or route')
        if q['flk'] not in ['FLK1', 'FLK2'] or q['answer'] not in 'ABCDE' or set(q['options']) != set('ABCDE') or not q['verified_source_url'].startswith('https://'):
            raise ValueError(f'Invalid question: {q["id"]}')
        if q['subject'] not in SUBJECTS:
            raise ValueError(f'Unknown subject "{q["subject"]}" in {q["id"]}; use a name from SUBJECTS in scripts/generate.py')
        # Optional fields written by the content team.
        if 'why_wrong' in q:
            wrong = q['why_wrong']
            if not isinstance(wrong, dict) or set(wrong) != set('ABCDE') - {q['answer']} or not all(isinstance(v, str) and v.strip() for v in wrong.values()):
                raise ValueError(f'why_wrong in {q["id"]} needs one non-empty reason for each of the four wrong letters')
        if 'tags' in q:
            tags = q['tags']
            if not isinstance(tags, list) or not 1 <= len(tags) <= 5 or not all(isinstance(t, str) and t.strip() and t == t.strip().lower() for t in tags):
                raise ValueError(f'tags in {q["id"]} must be 1-5 lowercase strings')
        if 'last_reviewed' in q:
            check_date(q['last_reviewed'], f'last_reviewed in {q["id"]}', today)
        if 'last_modified' in q:
            check_date(q['last_modified'], f'last_modified in {q["id"]}', today, q['publish_date'])
        ids.add(q['id']); numbers.add(q['number']); paths.add(route(q))

def load_pages(today):
    path = ROOT / 'content/pages.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(data, dict) or set(data) - {'sittings', 'pages', 'guides', 'subjects'}:
        raise ValueError('content/pages.json may only contain sittings, pages, guides and subjects')
    https = lambda value: isinstance(value, str) and value.startswith('https://')
    def approved(entry, label):
        if not isinstance(entry.get('approved'), bool):
            raise ValueError(f'{label} needs approved: true or false')
        if 'approved_hash' in entry and not isinstance(entry['approved_hash'], str):
            raise ValueError(f'{label}.approved_hash is written by --approve; do not edit it')
    for i, sitting in enumerate(data.get('sittings', [])):
        label = f'sittings[{i}]'
        if not isinstance(sitting.get('label'), str) or not https(sitting.get('source_url')):
            raise ValueError(f'{label} needs a label and an https source_url')
        for key in ['flk1_date', 'flk1_end', 'flk2_date', 'flk2_end', 'booking_closes', 'results_date']:
            value = sitting.get(key)
            if value is None and key != 'flk1_date':
                continue
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError(f'{key} in {label} must be an ISO date' + ('' if key == 'flk1_date' else ' or null'))
            date.fromisoformat(value)
        approved(sitting, label)
    pages = [(f'pages.{name}', page) for name, page in data.get('pages', {}).items()] + [(f'guides.{name}', page) for name, page in data.get('guides', {}).items()]
    for name in data.get('pages', {}):
        if name not in PAGES:
            raise ValueError(f'Unknown page {name}; pages are {", ".join(PAGES)}')
    for name in data.get('guides', {}):
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', name):
            raise ValueError(f'Guide slug {name} must be lowercase words joined by hyphens')
    for label, page in pages:
        for key in ['title', 'meta_description', 'h1', 'intro']:
            if not isinstance(page.get(key), str) or not page[key].strip():
                raise ValueError(f'{label} needs {key}')
        if len(page['meta_description']) > 155:
            raise ValueError(f'{label}.meta_description is longer than 155 characters')
        if not isinstance(page.get('sections', []), list) or not all(isinstance(s, dict) and isinstance(s.get('heading'), str) and isinstance(s.get('body'), str) for s in page.get('sections', [])):
            raise ValueError(f'{label}.sections must be a list of heading/body objects')
        if not isinstance(page.get('sources', []), list) or not all(isinstance(s, dict) and isinstance(s.get('label'), str) and https(s.get('url')) for s in page.get('sources', [])):
            raise ValueError(f'{label}.sources must be a list of label/https url objects')
        for key in ['last_reviewed', 'last_modified']:
            if key in page:
                check_date(page[key], f'{label}.{key}', today)
        approved(page, label)
    for name, subject in data.get('subjects', {}).items():
        label = f'subjects.{name}'
        if name not in SUBJECTS or not isinstance(subject.get('intro'), str):
            raise ValueError(f'{label} must name a subject in SUBJECTS and have an intro')
        for key in ['last_reviewed', 'last_modified']:
            if key in subject:
                check_date(subject[key], f'{label}.{key}', today)
        approved(subject, label)
    return data

def lock_routes(questions, write_lock, content=None, page_hashes=None):
    """Give every published question a permanent route, and record the date its visible content changes.

    Title edits never move a page. A changed content hash (title included) records today's London
    date as a genuine modification; first publication and seeding record none, so no date is invented.
    Approved pages and guides record the day they were first built and the day their copy last changed.
    """
    path = ROOT / LOCK
    lock = json.loads(path.read_text()) if path.exists() else {'questions': {}, 'subjects': {}}
    before = json.dumps(lock, sort_keys=True)
    # Entries from the first lock format held only the route or slug.
    lock['questions'] = {k: v if isinstance(v, dict) else {'route': v, 'hash': None, 'modified': None} for k, v in lock['questions'].items()}
    lock['subjects'] = {k: v if isinstance(v, dict) else {'slug': v, 'intro_hash': None, 'modified': None} for k, v in lock['subjects'].items()}
    lock.setdefault('pages', {})
    today = london_today()
    for key, digest in (page_hashes or {}).items():
        entry = lock['pages'].get(key)
        if entry is None:
            lock['pages'][key] = {'hash': digest, 'published': today, 'modified': None}
        elif entry['hash'] != digest:
            lock['pages'][key] = {**entry, 'hash': digest, 'modified': today}
    # Published pages already in the repository are the record of what is live.
    live = {int(p.name.split('-', 1)[0]): f'/q/{p.name}/' for p in (ROOT / 'q').glob('*-*') if p.is_dir() and p.name.split('-', 1)[0].isdigit()} if (ROOT / 'q').exists() else {}
    used = {entry['route'] for entry in lock['questions'].values()}
    for q in questions:
        entry = lock['questions'].get(q['id'])
        locked = entry and entry['route']
        if q['number'] in live:
            if locked and locked != live[q['number']]:
                raise ValueError(f'Route lock for {q["id"]} would move a published page from {live[q["number"]]} to {locked}')
            locked = live[q['number']]
        if not locked:
            locked = route(q)
            if locked in used:
                raise ValueError(f'Route {locked} is already used')
        prefix = q['id'] if q.get('library_number') else str(q['number'])
        if not re.fullmatch(r'/q/' + re.escape(prefix) + r'-[a-z0-9-]+/', locked):
            raise ValueError(f'Invalid locked route for {q["id"]}: {locked}')
        digest = content_hash(q, HASH_IGNORED)
        if entry is None or entry.get('hash') is None:
            entry = {'route': locked, 'hash': digest, 'modified': entry.get('modified') if entry else None}
        elif entry['hash'] != digest:
            entry = {'route': locked, 'hash': digest, 'modified': today}
        lock['questions'][q['id']] = {**entry, 'route': locked}
        used.add(locked)
        subject = lock['subjects'].setdefault(q['subject'], {'slug': SUBJECTS[q['subject']], 'intro_hash': None, 'modified': None})
        if subject['slug'] != SUBJECTS[q['subject']]:
            raise ValueError(f'Subject slug for {q["subject"]} differs from the route lock')
    if SUBJECT_INTROS_LIVE:
        intros = {name: entry for name, entry in (content or {}).get('subjects', {}).items() if is_approved(entry)}
        for name, subject in lock['subjects'].items():
            digest = content_hash({'intro': intros[name]['intro']}, set()) if name in intros else None
            if digest != subject['intro_hash']:
                lock['subjects'][name] = {**subject, 'intro_hash': digest, 'modified': today}
    existing = {p.name for p in (ROOT / 'archive').iterdir() if p.is_dir()} if (ROOT / 'archive').exists() else set()
    if existing - set(SUBJECTS.values()):
        raise ValueError(f'Published subject archives missing from SUBJECTS: {sorted(existing - set(SUBJECTS.values()))}')
    lock = {'questions': dict(sorted(lock['questions'].items())), 'subjects': dict(sorted(lock['subjects'].items())), 'pages': dict(sorted(lock['pages'].items()))}
    if write_lock and json.dumps(lock, sort_keys=True) != before:
        path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    modified = lambda q: max(filter(None, [q.get('last_modified'), lock['questions'][q['id']]['modified']]), default=None)
    return [{**q, 'route': lock['questions'][q['id']]['route'], 'modified': modified(q)} for q in questions], lock

def generate(day, package=False, write_lock=False):
    bank = load_bank()
    validate_bank(bank, london_today())
    content = load_pages(london_today())
    for label in stale_approvals(content):
        print(f'Warning: {label} changed after approval, so it is not published. Approve it again with --approve {label}.')
    # Only copy whose exact text is approved is built; everything else stays unpublished.
    pages = {name: page for name, page in content.get('pages', {}).items() if is_approved(page)}
    guides = {name: guide for name, guide in content.get('guides', {}).items() if is_approved(guide)}
    intros = {name: entry for name, entry in content.get('subjects', {}).items() if is_approved(entry)} if SUBJECT_INTROS_LIVE else {}
    LIVE_PATHS.clear(); LIVE_PATHS.update({f'/{name}/' for name in pages} | {f'/guides/{name}/' for name in guides} | ({'/guides/'} if guides else set()))
    sittings = sorted((s for s in content.get('sittings', []) if is_approved(s)), key=lambda s: s['flk1_date'])
    copy_ignored = APPROVAL_FIELDS | {'last_reviewed'}
    page_hashes = {f'pages.{name}': content_hash({**entry, **({'sittings': sittings} if name == 'sqe1-exam-dates' else {})}, copy_ignored) for name, entry in pages.items()}
    page_hashes.update({f'guides.{name}': content_hash(guide, copy_ignored) for name, guide in guides.items()})
    practice_data = practice_content.read(ROOT)
    available = practice_content.library(bank, practice_data, day)
    mock_papers = practice_content.mocks(bank, available, practice_data)
    questions, lock = lock_routes(available, write_lock, content, page_hashes)
    daily = published(questions, day)
    sitting = next((s for s in sittings if s['flk1_date'] >= day), DEFAULT_SITTING)
    subject_slug = lambda subject: SUBJECTS[subject]

    template = (ROOT / 'scripts/templates/home.html').read_text()
    if any(q['publish_date'] is None or q['publish_date'] > day for q in questions):
        template = template.replace('A fresh SQE1 question every day', 'One featured SQE1 question every day')
        template = template.replace('A fresh question tomorrow.', 'Another featured question tomorrow.')
        template = template.replace('Every question is original and checked against primary sources: legislation and case law.', 'Every question is original and checked against its linked source.')
    template = template.replace('class="countdown" aria-label=', 'class="countdown" role="group" aria-label=')
    template = template.replace('id="result-heading" tabindex="-1"></h3>', 'id="result-heading" tabindex="-1">Worked answer</h3>')
    newsletter = template.split('    <section class="email-band"')[1].split('    <section class="how-band')[0]
    newsletter = '    <section class="email-band"' + newsletter
    footer_links = [(name, url) for name, url, built in [('Practice questions', '/sqe1-practice-questions/', 'sqe1-practice-questions' in pages), ('Exam dates', '/sqe1-exam-dates/', 'sqe1-exam-dates' in pages), ('Guides', '/guides/', bool(guides)), ('Editorial standards', '/editorial-standards/', 'editorial-standards' in pages)] if built]
    footer_nav = NAV.replace('Main navigation', 'Footer navigation').replace('</nav>', ''.join(f'<a href="{url}">{name}</a>' for name, url in footer_links) + '</nav>')
    footer = '<footer class="wrap"><a class="footer-brand" href="/">SQE Daily.</a>' + footer_nav + '<p>Independent. Not affiliated with the SRA or any training provider.<br>For revision only. Not legal advice.</p><a href="mailto:hello@sqedaily.co.uk">Say hello</a></footer>'
    header = '<a class="skip-link" href="#main">Skip to content</a><header class="masthead wrap"><a class="brand" href="/" aria-label="SQE Daily home"><img src="/assets/mark.svg" width="52" height="52" alt=""><span class="brand-name">SQE Daily<span class="brand-dot">.</span></span></a>' + NAV + '</header>'
    extras = (f'<meta name="msvalidate.01" content="{esc(BING_VERIFICATION)}">\n' if BING_VERIFICATION else '') + '''<link rel="alternate" type="application/rss+xml" title="SQE Daily" href="https://sqedaily.co.uk/feed.xml">
<link rel="preload" href="/assets/dm-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/newsreader.woff2" as="font" type="font/woff2" crossorigin>
<script src="/assets/config.js" defer></script><script src="/assets/site.js" defer></script>'''
    json_ld = lambda schemas: ''.join('<script type="application/ld+json">' + json.dumps(s, ensure_ascii=False).replace('<', '\\u003c') + '</script>' for s in schemas)

    def page(path, title, description, body, schemas=(), og_type='website', meta=''):
        description = re.sub('<[^>]+>', '', description)
        full = f'{esc(title)} | SQE Daily'
        write(path + 'index.html', f'''<!DOCTYPE html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#142f2b"><title>{full}</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{BASE}{path}"><meta property="og:type" content="{og_type}"><meta property="og:title" content="{full}"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}/assets/social.png">{meta}<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{full}"><meta name="twitter:description" content="{esc(description)}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/styles.css">{extras}{json_ld(schemas)}</head><body>{header}<main id="main">{body}</main>{footer}</body></html>''')

    # Rebuild generator-owned directories, removing stale scheduled or unapproved pages.
    for name in OWNED:
        if (ROOT / name).is_dir():
            shutil.rmtree(ROOT / name)
    (ROOT / 'q').mkdir(); (ROOT / 'archive').mkdir()

    practice_source = '    <section class="practice-band"' + template.split('    <section class="practice-band"')[1].split('    <section class="email-band"')[0]

    def practice(q, home):
        """Fill the shared practice band for the homepage or a permanent question page."""
        body = practice_source.replace('id="practice-content" hidden', 'id="practice-content"')
        if q.get('library_number'):
            body = body.replace('Primary source · opens in a new tab', 'Source · opens in a new tab')
            body = re.sub(r'<p class="tomorrow-note">.*?</p>', '<p class="tomorrow-note">A little more practice done.</p>', body)
        if home:
            body = body.replace('class="load-state">', 'class="load-state" hidden>')
            body = re.sub(r'<noscript>.*?</noscript>', NOSCRIPT_NOTE, body, flags=re.S)
            body = body.replace('id="question"', f'id="question" data-question-id="{esc(q["id"])}"')
            body = body.replace('<h2 id="practice-heading">Today\'s question</h2>', '<h2 id="practice-heading">' + ("Today's question" if q['publish_date'] == day else 'Latest question') + '</h2>')
            body = body.replace('<time id="today"></time>', f'<time id="today" datetime="{q["publish_date"]}">{long_date(q["publish_date"])}</time>')
        else:
            body = re.sub(r'<div id="load-state".*?</noscript>', '', body, flags=re.S)
            body = body.replace('id="question"', 'id="question" data-static-question')
            body = body.replace('<h2 id="practice-heading">Today\'s question</h2>', f'<h1 id="practice-heading">{esc(q["title"])}</h1>')
            body = body.replace('<time id="today"></time>', f'<time datetime="{q["available_from"]}">{q["available_from"]}</time>')
        values = {**q, 'question-number': question_number(q), 'difficulty': q['difficulty'].capitalize()}
        for key in ['scenario', 'stem', 'subject', 'flk', 'difficulty', 'question-number']:
            body = body.replace(f'id="{key}"></', f'id="{key}">{esc(values[key])}</')
        options = ''.join(f'<button type="button" class="option" data-letter="{letter}" aria-label="{letter}. {esc(text)}"><span class="option-letter" aria-hidden="true">{letter}</span><span class="option-text">{esc(text)}</span><span class="option-symbol" aria-hidden="true"></span></button>' for letter, text in q['options'].items())
        body = body.replace('aria-labelledby="stem"></div>', f'aria-labelledby="stem">{options}</div>')
        body = body.replace('id="correct-answer" class="correct-answer"></p>', f'id="correct-answer" class="correct-answer">Correct answer {q["answer"]}: {esc(q["options"][q["answer"]])}</p>')
        body = body.replace('id="key-rule"></p>', f'id="key-rule">{esc(q["key_rule"])}</p>')
        body = body.replace('id="question-title"></h4>', f'id="question-title">{esc(q["title"])}</h4>')
        body = body.replace('id="explanation" class="explanation"></div>', f'id="explanation" class="explanation">{explanation_html(q)}</div>')
        body = body.replace('id="authority-link" target=', f'id="authority-link" href="{esc(q["verified_source_url"])}" target=').replace('rel="noopener noreferrer"></a>', f'rel="noopener noreferrer">{esc(q["authority"])}</a>')
        source_label = 'source' if q.get('library_number') else 'primary source'
        checked = f'<span class="source-note" id="checked-note">Checked against {source_label} on {long_date(q["last_reviewed"])}</span>' if q.get('last_reviewed') else ('<span class="source-note" id="checked-note" hidden></span>' if home else '')
        body = body.replace('<span class="source-note" id="checked-note" hidden></span>', checked)
        standards = '<a href="/editorial-standards/">How we check questions</a> · ' if 'editorial-standards' in pages else ''
        body = body.replace('<a id="report-link" href="mailto:hello@sqedaily.co.uk">Report an error</a>', f'{standards}<a id="report-link" href="mailto:hello@sqedaily.co.uk?subject=Question%20{question_number(q)}">Report an error</a>')
        return body

    def breadcrumbs(*items):
        return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'name': name, 'item': BASE + url} for i, (name, url) in enumerate(items, 1)]}

    def question_title(q):
        for title in [f'{q["title"]}: SQE1 {q["subject"]} practice question', f'{q["title"]}: SQE1 practice question']:
            if len(title) <= 60:
                return title
        return q['title']

    def question_description(q):
        source = f' Worked answer and source: {q["authority"].rstrip(".")}.'
        return summary(q['scenario'], max(80, 160 - len(source))) + source

    def question_item(q, heading='h3'):
        q = {**q, 'publish_date': q['available_from']}
        return f'<li><div class="archive-meta"><time datetime="{q["publish_date"]}">{q["publish_date"]}</time><span>{esc(q["subject"])} · {q["flk"]}</span><span>No. {question_number(q)}</span></div><{heading}><a href="{q["route"]}">{esc(q["title"])}</a></{heading}><p>{esc(q["stem"])}</p></li>'

    def related(q):
        """Up to three other published questions: shared tags first, then the same subject, then the same paper."""
        tags = set(q.get('tags', []))
        def rank(other):
            return (len(tags & set(other.get('tags', []))), other['subject'] == q['subject'], other['flk'] == q['flk'], other['available_from'], other['number'])
        candidates = [o for o in questions if o['id'] != q['id'] and (tags & set(o.get('tags', [])) or o['subject'] == q['subject'] or o['flk'] == q['flk'])]
        return sorted(candidates, key=rank, reverse=True)[:RELATED]

    # lastmod only where a real date backs it: publication or a genuine content change, never a review.
    changed = lambda qs: max((q['modified'] or q['available_from'] for q in qs), default=None)
    question_urls = []
    for i, q in enumerate(questions):
        body = practice(q, home=False)
        body += '<nav class="wrap question-navigation" aria-label="Question navigation">'
        if i > 0:
            body += f'<a href="{questions[i-1]["route"]}">← Previous question</a>'
        body += f'<a href="/archive/{subject_slug(q["subject"])}/">{esc(q["subject"])} archive</a>'
        if i + 1 < len(questions):
            body += f'<a href="{questions[i+1]["route"]}">Next question →</a>'
        body += '</nav><noscript><style>#result[hidden]{display:block!important}</style><p class="wrap">The worked answer is below the options.</p></noscript>'
        if related_questions := related(q):
            body += '<section class="recent-questions wrap" aria-labelledby="related-heading"><div class="section-heading"><h2 id="related-heading">Related questions</h2></div><ol class="archive-list">' + ''.join(question_item(o) for o in related_questions) + '</ol></section>'
        payload = json.dumps(q, ensure_ascii=False).replace('<', '\\u003c')
        body += f'<script type="application/json" id="question-data">{payload}</script><script src="/assets/app.js" defer></script>' + newsletter
        quiz = {'@context': 'https://schema.org', '@type': 'Quiz', 'name': q['title'], 'url': BASE + q['route'], 'datePublished': q['publish_date'], 'inLanguage': 'en-GB', 'educationalLevel': 'SQE1', 'about': {'@type': 'Thing', 'name': q['subject']}, 'educationalAlignment': {'@type': 'AlignmentObject', 'alignmentType': 'educationalSubject', 'educationalFramework': 'SRA Functioning Legal Knowledge', 'targetName': f'{q["flk"]}: {q["subject"]}'}, 'author': ORGANIZATION, 'publisher': ORGANIZATION, 'hasPart': {'@type': 'Question', 'name': q['stem'], 'text': q['scenario'], 'suggestedAnswer': [{'@type': 'Answer', 'text': f'{k}. {v}'} for k, v in q['options'].items()], 'acceptedAnswer': {'@type': 'Answer', 'text': q['options'][q['answer']], 'answerExplanation': q['explanation']}}}
        if q['modified']:
            quiz['dateModified'] = q['modified']
        quiz['datePublished'] = q['available_from']
        crumbs = breadcrumbs(('SQE Daily', '/'), (f'{q["subject"]} questions', f'/archive/{subject_slug(q["subject"])}/'), (q['title'], q['route']))
        meta = f'<meta property="article:published_time" content="{q["available_from"]}"><meta property="article:section" content="{esc(q["subject"])}">'
        page(q['route'], question_title(q), question_description(q), body, [quiz, crumbs], 'article', meta)
        question_urls.append(q['route'])

    subjects = sorted({q['subject'] for q in questions})
    def archive(subject=None):
        selected = [q for q in reversed(questions) if subject is None or q['subject'] == subject]
        selected = [{**q, 'publish_date': q['available_from']} for q in selected]
        intro = intros.get(subject)
        title = f'SQE1 {subject_questions(subject)}' if intro else subject or 'Question archive'
        filters = '<div class="archive-filters" role="group" aria-label="Filter questions" hidden><label>Subject<select id="subject-filter"><option value="">All subjects</option>' + ''.join(f'<option>{esc(s)}</option>' for s in subjects) + '</select></label><label>Paper<select id="flk-filter"><option value="">FLK1 and FLK2</option><option>FLK1</option><option>FLK2</option></select></label></div>'
        links = '<nav class="subject-index" aria-label="Subject archives">' + ''.join(f'<a href="/archive/{subject_slug(s)}/">{esc(s)}</a>' for s in subjects) + '</nav>'
        items = ''.join(f'<li data-subject="{esc(q["subject"])}" data-flk="{q["flk"]}"><div class="archive-meta"><time datetime="{q["publish_date"]}">{q["publish_date"]}</time><span>{esc(q["subject"])} · {q["flk"]}</span><span>No. {question_number(q)}</span></div><h2><a href="{q["route"]}">{esc(q["title"])}</a></h2><p>{esc(q["stem"])}</p></li>' for q in selected)
        url = '/archive/' + (subject_slug(subject) + '/' if subject else '')
        schema = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'url': BASE + url, 'publisher': ORGANIZATION, 'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'url': BASE + q['route'], 'name': q['title']} for i, q in enumerate(selected, 1)]}}
        overview = ''
        if intro:
            rules = ''.join(f'<p>{esc(q["key_rule"])} <a href="{q["route"]}">Question {question_number(q)}</a></p>' for q in reversed(selected))
            overview = f'<section class="reading-section">{rich(intro["intro"])}</section><section class="reading-section" aria-labelledby="rules-heading"><h2 id="rules-heading">Rules to remember</h2>{rules}</section>'
        body = f'<section class="reading wrap"><p class="eyebrow">THE DAILY PRACTICE</p><h1>{esc(title)}</h1><p class="lead">One question. One rule to remember. Browse the published practice.</p>{overview}{filters}{links}<ol class="archive-list">{items}</ol><p id="archive-empty" hidden>No questions match these filters.</p></section>' + newsletter
        return body, schema
    body, schema = archive()
    page('/archive/', 'Question archive', 'Browse published SQE1 questions, worked answers and primary legal sources by subject and paper.', body, [schema])
    for subject in subjects:
        body, schema = archive(subject)
        if subject in intros:
            title = f'SQE1 {subject_questions(subject)}' + (' (free, with answers)' if len(subject_questions(subject)) <= 33 else '')
            description = f'Free SQE1 {subject} practice questions with worked answers, the rules to remember and links to the primary sources.'
        else:
            title, description = subject + ' questions', f'Free SQE1 practice questions in {subject}, with worked answers and primary sources.'
        page('/archive/' + subject_slug(subject) + '/', title, description, body, [schema, breadcrumbs(('SQE Daily', '/'), ('Question archive', '/archive/'), (f'{subject} questions', f'/archive/{subject_slug(subject)}/'))])

    standards_note = ' Read our <a href="/editorial-standards/">editorial standards</a>.' if 'editorial-standards' in pages else ''
    copy = {
        'about': ('About SQE Daily', [('A little practice. Every day.', 'SQE Daily is a free site and newsletter for aspiring solicitors preparing for SQE1. One original Single Best Answer question, five options, a worked answer and the legal source. A few minutes of practice, wherever your day takes you.'), ('Written for revision. Checked at the source.', 'Each question is written for SQE Daily and checked against primary sources: legislation and case law. The worked answer explains the correct option, the alternatives and the key rule. Follow the authority link to read the source for yourself.' + standards_note), ('Independent by design.', 'SQE Daily is provider-neutral, sells no course, and is not affiliated with the SRA or any training provider. It is a revision resource, not legal advice or a substitute for comprehensive exam preparation.'), ('Say hello.', 'Questions, corrections or feedback? Email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a>.')]),
        'sponsor': ('Sponsor SQE Daily', [('Support a daily habit.', 'SQE Daily reaches SQE1 candidates: law students, career changers and paralegals building a daily revision habit, often on their phones between other commitments.'), ('One considered placement.', 'One sponsor slot per daily email and one on the site. Sponsorship keeps the daily question free. SQE Daily remains independent and provider-neutral.'), ('Start a conversation.', 'Media kit on request. Email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a> to discuss a placement. No course is sold by SQE Daily.')]),
        'privacy': ('Privacy', [('Newsletter subscriptions.', 'When you subscribe, your email address is sent to Buttondown, which stores subscriber emails and handles confirmation, delivery and unsubscribe requests. Confirm your address to activate your subscription. Unsubscribe using the link in an email. Read <a href="https://buttondown.com/legal/privacy">Buttondown’s privacy policy</a>.'), ('Website analytics.', 'Cloudflare Web Analytics is configured but disabled until a site token is added. When enabled, it collects cookie-free website usage and performance measurements. We do not add advertising trackers. Read <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare’s privacy policy</a>.'), ('Hosting and links.', 'GitHub Pages hosts this site. Hosting providers may process technical request information to serve and protect their services. Legal-source links take you to external websites, which have their own privacy policies.'), ('Contact and your information.', 'For privacy questions, access or deletion requests, email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a>. SQE Daily does not sell your subscriber email address or share it with sponsors.')])}
    copy['privacy'][1].insert(1, ('Practice test progress.', 'Practice tests store your answers, flags, timing and recent practice history on this device using browser storage. No test results are sent to SQE Daily or Buttondown. Other people using the same browser may be able to see saved attempts. Starting a new test or discarding a saved test clears the previous attempt. Clearing browser site data removes saved attempts and recent practice history.'))
    if any(q.get('library_number') for q in questions):
        heading, text = copy['about'][1][1]
        copy['about'][1][1] = (heading, text.replace('checked against primary sources: legislation and case law.', 'checked against its linked source.'))
    for name, (title, sections) in copy.items():
        body = '<section class="reading wrap"><p class="eyebrow">SQE DAILY</p><h1>' + title + '</h1>' + ''.join(f'<section class="reading-section"><h2>{heading}</h2><p>{text}</p></section>' for heading, text in sections) + '</section>'
        page('/' + name + '/', title, sections[0][1], body + (newsletter if name != 'privacy' else ''))

    # Approved copy from content/pages.json. Nothing here is built until its exact text is approved.
    def page_dates(key, entry):
        record = lock['pages'][key]
        return record['published'], max(filter(None, [record['modified'], entry.get('last_modified')]), default=None)

    def copy_page(path, key, eyebrow, entry, before='', after='', article=False, crumbs=()):
        body = f'<section class="reading wrap"><p class="eyebrow">{esc(eyebrow)}</p><h1>{esc(entry["h1"])}</h1><section class="reading-section">{rich(entry["intro"])}</section>{before}'
        body += ''.join(f'<section class="reading-section"><h2>{esc(s["heading"])}</h2>{rich(s["body"])}</section>' for s in entry.get('sections', []))
        body += after
        if entry.get('sources'):
            checked = f'<span class="source-note">Checked against these sources on {long_date(entry["last_reviewed"])}</span>' if entry.get('last_reviewed') else ''
            body += '<section class="reading-section"><h2>Sources</h2><p>' + '<br>'.join(f'<a href="{esc(s["url"])}">{esc(s["label"])}</a>' for s in entry['sources']) + f'</p>{checked}</section>'
        body += '</section>' + newsletter
        published, modified = page_dates(key, entry)
        schema = {'@context': 'https://schema.org', '@type': 'Article' if article else 'WebPage', 'headline' if article else 'name': entry['title'], 'url': BASE + path, 'inLanguage': 'en-GB', 'author': ORGANIZATION, 'publisher': ORGANIZATION, 'datePublished': published}
        if modified:
            schema['dateModified'] = modified
        meta = f'<meta property="article:published_time" content="{published}">' if article else ''
        page(path, entry['title'], entry['meta_description'], body, [schema] + ([breadcrumbs(*crumbs)] if crumbs else []), 'article' if article else 'website', meta)
        return modified or published

    def question_list(heading_id, heading, qs):
        return f'<section class="reading-section" aria-labelledby="{heading_id}"><h2 id="{heading_id}">{heading}</h2><ol class="archive-list">' + ''.join(question_item(q) for q in qs) + '</ol></section>' if qs else ''

    def subject_links(label, names):
        return f'<nav class="subject-index" aria-label="{esc(label)}">' + ''.join(f'<a href="/archive/{subject_slug(s)}/">{esc(s)}</a>' for s in names) + '</nav>' if names else ''

    def date_span(start, end):
        first, last = date.fromisoformat(start), date.fromisoformat(end) if end else None
        if not last or last == first:
            return long_date(start)
        return f'{first.day}–{last.day} {last:%B %Y}' if (first.year, first.month) == (last.year, last.month) else f'{long_date(start)} to {long_date(end)}'

    papers = {flk: [s for s in subjects if any(q['subject'] == s and q['flk'] == flk for q in questions)] for flk in PAPERS.values()}
    hub = '/sqe1-practice-questions/' if 'sqe1-practice-questions' in pages else '/archive/'
    guide_links = ''.join(f'<p><a href="/guides/{name}/">{esc(guide["h1"])}</a></p>' for name, guide in sorted(guides.items()))
    copy_lastmod = {}
    for name, entry in pages.items():
        before = after = ''
        if name == 'sqe1-exam-dates':
            for s in sittings:
                lines = [f'FLK1: {date_span(s["flk1_date"], s.get("flk1_end"))}', f'FLK2: {date_span(s["flk2_date"], s.get("flk2_end")) if s.get("flk2_date") else "not yet announced"}', f'Booking closes: {long_date(s["booking_closes"]) if s.get("booking_closes") else "not yet announced"}', f'Results: {long_date(s["results_date"]) if s.get("results_date") else "not yet announced"}']
                before += f'<section class="reading-section"><h2>{esc(s["label"])} SQE1</h2><p>' + '<br>'.join(lines) + f'<br><a href="{esc(s["source_url"])}">SRA source</a></p></section>'
        elif name == 'sqe1-practice-questions':
            paper_links = ' · '.join(f'<a href="/{slug}/">{flk} practice questions</a>' for slug, flk in PAPERS.items() if slug in pages)
            after += f'<section class="reading-section"><h2>Practise by paper</h2>' + (f'<p>{paper_links}</p>' if paper_links else '') + ''.join(f'<h3>{flk}</h3>{subject_links(f"{flk} subjects", papers[flk])}' for flk in PAPERS.values() if papers[flk]) + '</section>'
            after += question_list('latest-heading', 'Latest questions', list(reversed(questions))[:LATEST])
            if guide_links:
                after += f'<section class="reading-section"><h2>Guides</h2>{guide_links}</section>'
        elif name in PAPERS:
            flk = PAPERS[name]
            other = next(slug for slug in PAPERS if slug != name)
            after += f'<section class="reading-section"><h2>{flk} subjects on SQE Daily</h2>{subject_links(f"{flk} subjects", papers[flk]) or "<p>The first questions for this paper are on their way.</p>"}</section>'
            after += question_list('latest-heading', f'Latest {flk} questions', [q for q in reversed(questions) if q['flk'] == flk][:LATEST])
            more = [f'<a href="{hub}">All SQE1 practice questions</a>'] + ([f'<a href="/{other}/">{PAPERS[other]} practice questions</a>'] if other in pages else [])
            after += '<section class="reading-section"><h2>Keep practising</h2><p>' + ' · '.join(more) + '</p></section>'
        crumbs = (('SQE Daily', '/'), ('SQE1 practice questions', '/sqe1-practice-questions/'), (entry['h1'], f'/{name}/')) if name in PAPERS and 'sqe1-practice-questions' in pages else ()
        copy_lastmod[f'/{name}/'] = copy_page(f'/{name}/', f'pages.{name}', PAGES[name], entry, before, after, crumbs=crumbs)
        if name in ['sqe1-practice-questions', *PAPERS]:
            listed = questions if name == 'sqe1-practice-questions' else [q for q in questions if q['flk'] == PAPERS[name]]
            copy_lastmod[f'/{name}/'] = max(filter(None, [copy_lastmod[f'/{name}/'], changed(listed)]))
    for name, guide in guides.items():
        after = f'<section class="reading-section"><h2>Keep practising</h2><p><a href="/">Today’s question</a> · <a href="{hub}">Browse SQE1 practice questions</a></p></section>'
        copy_lastmod[f'/guides/{name}/'] = copy_page(f'/guides/{name}/', f'guides.{name}', 'SQE1 GUIDE', guide, after=after, article=True, crumbs=(('SQE Daily', '/'), ('Guides', '/guides/'), (guide['h1'], f'/guides/{name}/')))
    if guides:
        items = ''.join(f'<li><h2><a href="/guides/{name}/">{esc(guide["h1"])}</a></h2><p>{esc(guide["meta_description"])}</p></li>' for name, guide in sorted(guides.items()))
        schema = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'SQE1 guides', 'url': BASE + '/guides/', 'publisher': ORGANIZATION, 'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'url': f'{BASE}/guides/{name}/'} for i, name in enumerate(sorted(guides), 1)]}}
        page('/guides/', 'SQE1 guides', 'Free, practical guides to preparing for SQE1, written alongside the daily practice question.', f'<section class="reading wrap"><p class="eyebrow">SQE1 GUIDES</p><h1>SQE1 guides</h1><p class="lead">Practical help with preparing for SQE1, written alongside the daily question.</p><ol class="archive-list">{items}</ol></section>' + newsletter, [schema])
        copy_lastmod['/guides/'] = max(copy_lastmod[f'/guides/{name}/'] for name in guides)

    test_body = (ROOT / 'scripts/templates/tests.html').read_text()
    page('/tests/', 'Free SQE1 mini tests and mock practice', 'Take a free SQE1 mini test by paper or subject, or practise an approved full mock. Review your answers with worked explanations and legal sources.', test_body, [breadcrumbs(('SQE Daily', '/'), ('Practice tests', '/tests/'))])

    page('/not-found/', 'Page not found', 'Find today’s free SQE1 question or browse the archive.', '<section class="reading wrap"><p class="eyebrow">404</p><h1>This page has moved on.</h1><p class="lead">There is still a good question waiting.</p><p><a href="/">Today’s question</a> · <a href="/archive/">Browse the archive</a></p></section>')
    error_page = (ROOT / 'not-found/index.html').read_text().replace(BASE + '/not-found/', BASE + '/404.html').replace('</head>', '<meta name="robots" content="noindex"></head>')
    write('404.html', error_page)
    shutil.rmtree(ROOT / 'not-found')

    home = template.replace('<footer class="wrap">' + template.split('<footer class="wrap">')[1].split('</footer>')[0] + '</footer>', footer)
    home = home.replace('<p class="masthead-note">Independent practice.<br>A daily habit.</p>', NAV)
    home_schema = [{'@context': 'https://schema.org', **ORGANIZATION}, {'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '/#website', 'name': 'SQE Daily', 'url': BASE + '/', 'inLanguage': 'en-GB', 'publisher': {'@id': ORGANIZATION['@id']}}]
    home = home.replace('</head>', extras + json_ld(home_schema) + (NOSCRIPT_STYLE if daily else '') + '</head>').replace('assets/app.js?v=buttondown-2', '/assets/app.js')
    home = home.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
    exam_link = '<br><a href="/sqe1-exam-dates/">SQE1 exam dates</a>' if 'sqe1-exam-dates' in pages else ''
    flk2 = date.fromisoformat(sitting['flk2_date']) if sitting.get('flk2_date') else None
    days = max(0, (date.fromisoformat(sitting['flk1_date']) - date.fromisoformat(day)).days)
    countdown = f'<div class="countdown" role="group" aria-label="Next SQE1 sitting" data-flk1="{sitting["flk1_date"]}"><p class="eyebrow">NEXT UP · {esc(sitting["label"].upper())}</p><p class="count-number"><span id="days">{days}</span><span class="count-unit" id="days-label">{"day to go" if days == 1 else "days to go"}</span></p><div class="count-line"></div><p class="count-details">SQE1 · FLK1 begins {date.fromisoformat(sitting["flk1_date"]).day} {date.fromisoformat(sitting["flk1_date"]):%B}<br><span>{f"FLK2 begins {flk2.day} {flk2:%B}" if flk2 else "FLK2 date to be confirmed"}</span>{exam_link}</p></div>'
    home = re.sub(r'<div class="countdown".*?</p></div>', lambda m: countdown, home, count=1, flags=re.S)
    if daily:
        current = daily[-1]
        band = practice(current, home=True)
        end = '      </div>\n    </section>'
        assert band.endswith(end + '\n'), 'Unexpected practice band markup'
        band = band[:-len(end) - 1] + f'      <nav class="question-navigation" aria-label="Question links"><a id="permalink" href="{current["route"]}">Permanent link to this question</a><a href="/archive/">Browse the archive</a></nav>\n' + end + '\n'
        payload = json.dumps(current, ensure_ascii=False).replace('<', '\\u003c')
        band += f'<script type="application/json" id="home-question-data">{payload}</script>\n'
        recent = list(reversed([q for q in questions if q['id'] != current['id']]))[:RECENT]
        recent = [{**q, 'publish_date': q['available_from']} for q in recent]
        if recent:
            items = ''.join(f'<li><div class="archive-meta"><time datetime="{q["publish_date"]}">{q["publish_date"]}</time><span>{esc(q["subject"])} · {q["flk"]}</span><span>No. {question_number(q)}</span></div><h3><a href="{q["route"]}">{esc(q["title"])}</a></h3><p>{esc(q["stem"])}</p></li>' for q in recent)
            band += f'    <section class="recent-questions wrap" aria-labelledby="recent-heading"><div class="section-heading"><h2 id="recent-heading">Recent questions</h2><a href="/archive/">All questions</a></div><ol class="archive-list">{items}</ol></section>\n'
        assert practice_source in home
        home = home.replace(practice_source, band)
    else:
        home = home.replace('id="stem"></h2>', 'id="stem">Daily practice</h2>').replace('id="question-title"></h4>', 'id="question-title">Explanation</h4>').replace('id="authority-link" target=', 'id="authority-link" href="/archive/" target=')
    write('index.html', home)

    urls = [('/', changed(daily)), ('/archive/', changed(questions)), ('/tests/', None), ('/about/', None), ('/sponsor/', None), ('/privacy/', None)]
    urls += sorted(copy_lastmod.items())
    subject_changed = lambda s: max(filter(None, [changed([q for q in questions if q['subject'] == s]), lock['subjects'][s]['modified']]))
    urls += [('/archive/' + subject_slug(s) + '/', subject_changed(s)) for s in subjects]
    urls += [(q['route'], q['modified'] or q['available_from']) for q in questions]
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for url, lastmod in urls:
        item = ET.SubElement(sitemap, 'url'); ET.SubElement(item, 'loc').text = BASE + url
        if lastmod:
            ET.SubElement(item, 'lastmod').text = lastmod
    write('sitemap.xml', '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(sitemap, encoding='unicode'))
    rss = ET.Element('rss', version='2.0'); channel = ET.SubElement(rss, 'channel')
    for tag, value in [('title', 'SQE Daily'), ('link', BASE), ('description', 'One free SQE1 practice question every day, with a worked answer and the legal source.'), ('language', 'en-gb')]:
        ET.SubElement(channel, tag).text = value
    for q in reversed(questions):
        q = {**q, 'publish_date': q['available_from']}
        item = ET.SubElement(channel, 'item')
        for tag, value in [('title', q['title']), ('link', BASE + q['route']), ('guid', BASE + q['route']), ('description', q['scenario'] + '\n\n' + q['stem']), ('pubDate', datetime.fromisoformat(q['publish_date']).strftime('%a, %d %b %Y 00:00:00 +0000'))]:
            ET.SubElement(item, tag).text = value
    write('feed.xml', '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding='unicode'))
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    if package:
        public = ROOT / '_site'
        if public.exists(): shutil.rmtree(public)
        public.mkdir()
        for name in [*OWNED, 'CNAME', '.nojekyll', 'assets']:
            source = ROOT / name
            if source.is_dir(): shutil.copytree(source, public / name)
            elif source.exists(): shutil.copy2(source, public / name)
        (public / 'content').mkdir()
        (public / 'content/questions.json').write_text(json.dumps(questions, ensure_ascii=False, indent=2) + '\n')
        (public / 'content/practice-tests.json').write_text(json.dumps({'version': 1, 'mocks': mock_papers}, ensure_ascii=False) + '\n')
    print(f'Generated {len(questions)} published questions for {day}.')
    return questions

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=london_today())
    parser.add_argument('--package', action='store_true')
    parser.add_argument('--owned', action='store_true', help='List generator-owned paths for the publish commit.')
    parser.add_argument('--approve', metavar='ENTRY', help='Record owner approval of a content/pages.json entry, e.g. pages.editorial-standards')
    parser.add_argument('--approve-practice', metavar='ENTRY', help='Record exact owner approval of releases.ID or mocks.ID')
    parser.add_argument('--expect', metavar='FINGERPRINT', help='With --approve: the fingerprint the owner approved (from docs/editorial-approval-batch.md)')
    args = parser.parse_args()
    if args.approve_practice:
        practice_content.approve(ROOT, args.approve_practice, args.expect)
    elif args.approve:
        approve(args.approve, args.expect)
    elif args.owned:
        print('\n'.join([*OWNED, LOCK]))
    else:
        datetime.strptime(args.date, '%Y-%m-%d')
        # Previews of other dates must never add future routes to the lock.
        generate(args.date, args.package, write_lock=args.date == london_today())
