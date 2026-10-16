"""Generate SQE Daily's static pages using only Python's standard library."""
import argparse
import hashlib
import html
import json
import re
import shutil
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
# content/pages.json entries this release can build; the others are validated and wait for a later release.
PAGE_SLUGS = {'sqe1-exam-dates': 'SQE1 EXAM DATES', 'editorial-standards': 'SQE DAILY'}
LATER_PAGE_SLUGS = ['sqe1-practice-questions', 'flk1', 'flk2']
# The countdown's existing sitting, used until an approved sitting is added to content/pages.json.
DEFAULT_SITTING = {'label': 'January 2027', 'flk1_date': '2027-01-11', 'flk2_date': '2027-01-18'}
LOCK = 'content/routes.lock.json'
OWNED = ['index.html', '404.html', 'q', 'archive', 'about', 'sponsor', 'privacy', *PAGE_SLUGS, 'sitemap.xml', 'feed.xml', 'robots.txt']
RECENT = 5
NAV = '<nav aria-label="Main navigation">' + ''.join(f'<a href="{url}">{name}</a>' for name, url in [('Today', '/'), ('Archive', '/archive/'), ('About', '/about/'), ('Sponsor', '/sponsor/'), ('Privacy', '/privacy/')]) + '</nav>'
# Without JavaScript the homepage shows the worked answer below the options; the style lives in <head>.
NOSCRIPT_STYLE = '<noscript><style>#result[hidden]{display:block!important}</style></noscript>'
NOSCRIPT_NOTE = '<noscript><p>The worked answer is below the options.</p></noscript>'
WRONG_LINE = re.compile(r'^[A-E] is wrong\b')
esc = lambda value: html.escape(str(value), quote=True)

def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def route(q):
    """The route a question receives when first published. Afterwards the lock file decides."""
    return f'/q/{q["number"]}-{slug(q["title"])}/'

def published(bank, day):
    return sorted((q for q in bank if q['publish_date'] <= day), key=lambda q: (q['publish_date'], q['number']))

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

def rich(text):
    """Escape page copy, keeping blank-line paragraphs and [text](https://…) links."""
    paragraphs = []
    for paragraph in text.strip().split('\n\n'):
        body = re.sub(r'\[([^\]]+)\]\((https://[^)\s]+)\)', lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', esc(paragraph))
        paragraphs.append('<p>' + body.replace('\n', '<br>') + '</p>')
    return ''.join(paragraphs)

def explanation_html(q):
    paragraphs = q['explanation'].split('\n\n')
    if not q.get('why_wrong'):
        return ''.join(f'<p>{esc(p)}</p>' for p in paragraphs)
    kept = ['\n'.join(line for line in p.split('\n') if not WRONG_LINE.match(line)) for p in paragraphs]
    return ''.join(f'<p>{esc(p)}</p>' for p in kept if p) + ''.join(f'<p>Why {k} is wrong: {esc(v)}</p>' for k, v in sorted(q['why_wrong'].items()))

def write(path, content):
    target = ROOT / path.lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix == '.html':
        for name in ['app.js', 'site.js', 'config.js', 'styles.css']:
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
    if not isinstance(data, dict) or set(data) - {'sittings', 'pages', 'subjects'}:
        raise ValueError('content/pages.json may only contain sittings, pages and subjects')
    https = lambda value: isinstance(value, str) and value.startswith('https://')
    def approved(entry, label):
        if not isinstance(entry.get('approved'), bool):
            raise ValueError(f'{label} needs approved: true or false')
    for i, sitting in enumerate(data.get('sittings', [])):
        label = f'sittings[{i}]'
        if not isinstance(sitting.get('label'), str) or not https(sitting.get('source_url')):
            raise ValueError(f'{label} needs a label and an https source_url')
        for key in ['flk1_date', 'flk2_date', 'booking_closes', 'results_date']:
            value = sitting.get(key)
            if value is None and key != 'flk1_date':
                continue
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError(f'{key} in {label} must be an ISO date' + ('' if key == 'flk1_date' else ' or null'))
            date.fromisoformat(value)
        approved(sitting, label)
    for name, page in data.get('pages', {}).items():
        label = f'pages.{name}'
        if name not in PAGE_SLUGS and name not in LATER_PAGE_SLUGS:
            raise ValueError(f'Unknown page {name}')
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

def lock_routes(questions, write_lock):
    """Give every published question a permanent route; title edits never move a page."""
    path = ROOT / LOCK
    lock = json.loads(path.read_text()) if path.exists() else {'questions': {}, 'subjects': {}}
    before = json.dumps(lock, sort_keys=True)
    # Published pages already in the repository are the record of what is live.
    live = {int(p.name.split('-', 1)[0]): f'/q/{p.name}/' for p in (ROOT / 'q').glob('*-*') if p.is_dir() and p.name.split('-', 1)[0].isdigit()} if (ROOT / 'q').exists() else {}
    used = set(lock['questions'].values())
    for q in questions:
        locked = lock['questions'].get(q['id'])
        if q['number'] in live:
            if locked and locked != live[q['number']]:
                raise ValueError(f'Route lock for {q["id"]} would move a published page from {live[q["number"]]} to {locked}')
            locked = live[q['number']]
        if not locked:
            locked = route(q)
            if locked in used:
                raise ValueError(f'Route {locked} is already used')
        if not re.fullmatch(r'/q/' + str(q['number']) + r'-[a-z0-9-]+/', locked):
            raise ValueError(f'Invalid locked route for {q["id"]}: {locked}')
        lock['questions'][q['id']] = locked
        used.add(locked)
        if lock['subjects'].setdefault(q['subject'], SUBJECTS[q['subject']]) != SUBJECTS[q['subject']]:
            raise ValueError(f'Subject slug for {q["subject"]} differs from the route lock')
    existing = {p.name for p in (ROOT / 'archive').iterdir() if p.is_dir()} if (ROOT / 'archive').exists() else set()
    if existing - set(SUBJECTS.values()):
        raise ValueError(f'Published subject archives missing from SUBJECTS: {sorted(existing - set(SUBJECTS.values()))}')
    lock = {'questions': dict(sorted(lock['questions'].items())), 'subjects': dict(sorted(lock['subjects'].items()))}
    if write_lock and json.dumps(lock, sort_keys=True) != before:
        path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return [{**q, 'route': lock['questions'][q['id']]} for q in questions]

def generate(day, package=False, write_lock=False):
    bank = json.loads((ROOT / 'content/questions.json').read_text())
    validate_bank(bank, london_today())
    content = load_pages(london_today())
    questions = lock_routes(published(bank, day), write_lock)
    pages = {name: page for name, page in content.get('pages', {}).items() if page['approved'] and name in PAGE_SLUGS}
    for name, page in content.get('pages', {}).items():
        if page['approved'] and name not in PAGE_SLUGS:
            print(f'Note: approved page {name} is not built until a later release.')
    sittings = sorted((s for s in content.get('sittings', []) if s['approved']), key=lambda s: s['flk1_date'])
    sitting = next((s for s in sittings if s['flk1_date'] >= day), DEFAULT_SITTING)
    subject_slug = lambda subject: SUBJECTS[subject]

    template = (ROOT / 'scripts/templates/home.html').read_text()
    template = template.replace('class="countdown" aria-label=', 'class="countdown" role="group" aria-label=')
    template = template.replace('id="result-heading" tabindex="-1"></h3>', 'id="result-heading" tabindex="-1">Worked answer</h3>')
    newsletter = template.split('    <section class="email-band"')[1].split('    <section class="how-band')[0]
    newsletter = '    <section class="email-band"' + newsletter
    footer_links = [('Exam dates', '/sqe1-exam-dates/')] * ('sqe1-exam-dates' in pages) + [('Editorial standards', '/editorial-standards/')] * ('editorial-standards' in pages)
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
            body = body.replace('<time id="today"></time>', f'<time datetime="{q["publish_date"]}">{q["publish_date"]}</time>')
        values = {**q, 'question-number': str(q['number']).zfill(2), 'difficulty': q['difficulty'].capitalize()}
        for key in ['scenario', 'stem', 'subject', 'flk', 'difficulty', 'question-number']:
            body = body.replace(f'id="{key}"></', f'id="{key}">{esc(values[key])}</')
        options = ''.join(f'<button type="button" class="option" data-letter="{letter}" aria-label="{letter}. {esc(text)}"><span class="option-letter" aria-hidden="true">{letter}</span><span class="option-text">{esc(text)}</span><span class="option-symbol" aria-hidden="true"></span></button>' for letter, text in q['options'].items())
        body = body.replace('aria-labelledby="stem"></div>', f'aria-labelledby="stem">{options}</div>')
        body = body.replace('id="correct-answer" class="correct-answer"></p>', f'id="correct-answer" class="correct-answer">Correct answer {q["answer"]}: {esc(q["options"][q["answer"]])}</p>')
        body = body.replace('id="key-rule"></p>', f'id="key-rule">{esc(q["key_rule"])}</p>')
        body = body.replace('id="question-title"></h4>', f'id="question-title">{esc(q["title"])}</h4>')
        body = body.replace('id="explanation" class="explanation"></div>', f'id="explanation" class="explanation">{explanation_html(q)}</div>')
        body = body.replace('id="authority-link" target=', f'id="authority-link" href="{esc(q["verified_source_url"])}" target=').replace('rel="noopener noreferrer"></a>', f'rel="noopener noreferrer">{esc(q["authority"])}</a>')
        checked = f'<span class="source-note" id="checked-note">Checked against primary source on {long_date(q["last_reviewed"])}</span>' if q.get('last_reviewed') else ('<span class="source-note" id="checked-note" hidden></span>' if home else '')
        body = body.replace('<span class="source-note" id="checked-note" hidden></span>', checked)
        standards = '<a href="/editorial-standards/">How we check questions</a> · ' if 'editorial-standards' in pages else ''
        body = body.replace('<a id="report-link" href="mailto:hello@sqedaily.co.uk">Report an error</a>', f'{standards}<a id="report-link" href="mailto:hello@sqedaily.co.uk?subject=Question%20{q["number"]}">Report an error</a>')
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
        payload = json.dumps(q, ensure_ascii=False).replace('<', '\\u003c')
        body += f'<script type="application/json" id="question-data">{payload}</script><script src="/assets/app.js" defer></script>' + newsletter
        quiz = {'@context': 'https://schema.org', '@type': 'Quiz', 'name': q['title'], 'url': BASE + q['route'], 'datePublished': q['publish_date'], 'inLanguage': 'en-GB', 'educationalLevel': 'SQE1', 'about': {'@type': 'Thing', 'name': q['subject']}, 'educationalAlignment': {'@type': 'AlignmentObject', 'alignmentType': 'educationalSubject', 'educationalFramework': 'SRA Functioning Legal Knowledge', 'targetName': f'{q["flk"]}: {q["subject"]}'}, 'author': ORGANIZATION, 'publisher': ORGANIZATION, 'hasPart': {'@type': 'Question', 'name': q['stem'], 'text': q['scenario'], 'suggestedAnswer': [{'@type': 'Answer', 'text': f'{k}. {v}'} for k, v in q['options'].items()], 'acceptedAnswer': {'@type': 'Answer', 'text': q['options'][q['answer']], 'answerExplanation': q['explanation']}}}
        if q.get('last_modified'):
            quiz['dateModified'] = q['last_modified']
        crumbs = breadcrumbs(('SQE Daily', '/'), (f'{q["subject"]} questions', f'/archive/{subject_slug(q["subject"])}/'), (q['title'], q['route']))
        meta = f'<meta property="article:published_time" content="{q["publish_date"]}"><meta property="article:section" content="{esc(q["subject"])}">'
        page(q['route'], question_title(q), question_description(q), body, [quiz, crumbs], 'article', meta)
        question_urls.append(q['route'])

    subjects = sorted({q['subject'] for q in questions})
    def archive(subject=None):
        selected = [q for q in reversed(questions) if subject is None or q['subject'] == subject]
        title = subject or 'Question archive'
        filters = '<div class="archive-filters" role="group" aria-label="Filter questions" hidden><label>Subject<select id="subject-filter"><option value="">All subjects</option>' + ''.join(f'<option>{esc(s)}</option>' for s in subjects) + '</select></label><label>Paper<select id="flk-filter"><option value="">FLK1 and FLK2</option><option>FLK1</option><option>FLK2</option></select></label></div>'
        links = '<nav class="subject-index" aria-label="Subject archives">' + ''.join(f'<a href="/archive/{subject_slug(s)}/">{esc(s)}</a>' for s in subjects) + '</nav>'
        items = ''.join(f'<li data-subject="{esc(q["subject"])}" data-flk="{q["flk"]}"><div class="archive-meta"><time datetime="{q["publish_date"]}">{q["publish_date"]}</time><span>{esc(q["subject"])} · {q["flk"]}</span><span>No. {q["number"]:02}</span></div><h2><a href="{q["route"]}">{esc(q["title"])}</a></h2><p>{esc(q["stem"])}</p></li>' for q in selected)
        url = '/archive/' + (subject_slug(subject) + '/' if subject else '')
        schema = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'url': BASE + url, 'publisher': ORGANIZATION, 'mainEntity': {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i, 'url': BASE + q['route'], 'name': q['title']} for i, q in enumerate(selected, 1)]}}
        body = f'<section class="reading wrap"><p class="eyebrow">THE DAILY PRACTICE</p><h1>{esc(title)}</h1><p class="lead">One question. One rule to remember. Browse the published practice.</p>{filters}{links}<ol class="archive-list">{items}</ol><p id="archive-empty" hidden>No questions match these filters.</p></section>' + newsletter
        return body, schema
    body, schema = archive()
    page('/archive/', 'Question archive', 'Browse published SQE1 questions, worked answers and primary legal sources by subject and paper.', body, [schema])
    for subject in subjects:
        body, schema = archive(subject)
        page('/archive/' + subject_slug(subject) + '/', subject + ' questions', f'Free SQE1 practice questions in {subject}, with worked answers and primary sources.', body, [schema, breadcrumbs(('SQE Daily', '/'), ('Question archive', '/archive/'), (f'{subject} questions', f'/archive/{subject_slug(subject)}/'))])

    standards_note = ' Read our <a href="/editorial-standards/">editorial standards</a>.' if 'editorial-standards' in pages else ''
    copy = {
        'about': ('About SQE Daily', [('A little practice. Every day.', 'SQE Daily is a free site and newsletter for aspiring solicitors preparing for SQE1. One original Single Best Answer question, five options, a worked answer and the legal source. A few minutes of practice, wherever your day takes you.'), ('Written for revision. Checked at the source.', 'Each question is written for SQE Daily and checked against primary sources: legislation and case law. The worked answer explains the correct option, the alternatives and the key rule. Follow the authority link to read the source for yourself.' + standards_note), ('Independent by design.', 'SQE Daily is provider-neutral, sells no course, and is not affiliated with the SRA or any training provider. It is a revision resource, not legal advice or a substitute for comprehensive exam preparation.'), ('Say hello.', 'Questions, corrections or feedback? Email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a>.')]),
        'sponsor': ('Sponsor SQE Daily', [('Support a daily habit.', 'SQE Daily reaches SQE1 candidates: law students, career changers and paralegals building a daily revision habit, often on their phones between other commitments.'), ('One considered placement.', 'One sponsor slot per daily email and one on the site. Sponsorship keeps the daily question free. SQE Daily remains independent and provider-neutral.'), ('Start a conversation.', 'Media kit on request. Email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a> to discuss a placement. No course is sold by SQE Daily.')]),
        'privacy': ('Privacy', [('Newsletter subscriptions.', 'When you subscribe, your email address is sent to Buttondown, which stores subscriber emails and handles confirmation, delivery and unsubscribe requests. Confirm your address to activate your subscription. Unsubscribe using the link in an email. Read <a href="https://buttondown.com/legal/privacy">Buttondown’s privacy policy</a>.'), ('Website analytics.', 'Cloudflare Web Analytics is configured but disabled until a site token is added. When enabled, it collects cookie-free website usage and performance measurements. We do not add advertising trackers. Read <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare’s privacy policy</a>.'), ('Hosting and links.', 'GitHub Pages hosts this site. Hosting providers may process technical request information to serve and protect their services. Legal-source links take you to external websites, which have their own privacy policies.'), ('Contact and your information.', 'For privacy questions, access or deletion requests, email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a>. SQE Daily does not sell your subscriber email address or share it with sponsors.')])}
    for name, (title, sections) in copy.items():
        body = '<section class="reading wrap"><p class="eyebrow">SQE DAILY</p><h1>' + title + '</h1>' + ''.join(f'<section class="reading-section"><h2>{heading}</h2><p>{text}</p></section>' for heading, text in sections) + '</section>'
        page('/' + name + '/', title, sections[0][1], body + (newsletter if name != 'privacy' else ''))

    # Approved copy from content/pages.json. Nothing here is built until approved is true.
    for name, entry in pages.items():
        body = f'<section class="reading wrap"><p class="eyebrow">{PAGE_SLUGS[name]}</p><h1>{esc(entry["h1"])}</h1><section class="reading-section">{rich(entry["intro"])}</section>'
        if name == 'sqe1-exam-dates':
            for s in sittings:
                lines = [f'FLK1: {long_date(s["flk1_date"])}', f'FLK2: {long_date(s["flk2_date"]) if s.get("flk2_date") else "not yet announced"}', f'Booking closes: {long_date(s["booking_closes"]) if s.get("booking_closes") else "not yet announced"}', f'Results: {long_date(s["results_date"]) if s.get("results_date") else "not yet announced"}']
                body += f'<section class="reading-section"><h2>{esc(s["label"])}</h2><p>' + '<br>'.join(lines) + f'<br><a href="{esc(s["source_url"])}">Source</a></p></section>'
        body += ''.join(f'<section class="reading-section"><h2>{esc(s["heading"])}</h2>{rich(s["body"])}</section>' for s in entry.get('sections', []))
        if entry.get('sources'):
            checked = f'<span class="source-note">Checked against these sources on {long_date(entry["last_reviewed"])}</span>' if entry.get('last_reviewed') else ''
            body += '<section class="reading-section"><h2>Sources</h2><p>' + '<br>'.join(f'<a href="{esc(s["url"])}">{esc(s["label"])}</a>' for s in entry['sources']) + f'</p>{checked}</section>'
        body += '</section>' + newsletter
        schema = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': entry['title'], 'url': f'{BASE}/{name}/', 'author': ORGANIZATION, 'publisher': ORGANIZATION}
        if entry.get('last_modified'):
            schema['dateModified'] = entry['last_modified']
        page(f'/{name}/', entry['title'], entry['meta_description'], body, [schema])

    page('/not-found/', 'Page not found', 'Find today’s free SQE1 question or browse the archive.', '<section class="reading wrap"><p class="eyebrow">404</p><h1>This page has moved on.</h1><p class="lead">There is still a good question waiting.</p><p><a href="/">Today’s question</a> · <a href="/archive/">Browse the archive</a></p></section>')
    error_page = (ROOT / 'not-found/index.html').read_text().replace(BASE + '/not-found/', BASE + '/404.html').replace('</head>', '<meta name="robots" content="noindex"></head>')
    write('404.html', error_page)
    shutil.rmtree(ROOT / 'not-found')

    home = template.replace('<footer class="wrap">' + template.split('<footer class="wrap">')[1].split('</footer>')[0] + '</footer>', footer)
    home = home.replace('<p class="masthead-note">Independent practice.<br>A daily habit.</p>', NAV)
    home_schema = [{'@context': 'https://schema.org', **ORGANIZATION}, {'@context': 'https://schema.org', '@type': 'WebSite', '@id': BASE + '/#website', 'name': 'SQE Daily', 'url': BASE + '/', 'inLanguage': 'en-GB', 'publisher': {'@id': ORGANIZATION['@id']}}]
    home = home.replace('</head>', extras + json_ld(home_schema) + (NOSCRIPT_STYLE if questions else '') + '</head>').replace('assets/app.js?v=buttondown-2', '/assets/app.js')
    home = home.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
    exam_link = '<br><a href="/sqe1-exam-dates/">SQE1 exam dates</a>' if 'sqe1-exam-dates' in pages else ''
    flk2 = date.fromisoformat(sitting['flk2_date']) if sitting.get('flk2_date') else None
    days = max(0, (date.fromisoformat(sitting['flk1_date']) - date.fromisoformat(day)).days)
    countdown = f'<div class="countdown" role="group" aria-label="Next SQE1 sitting" data-flk1="{sitting["flk1_date"]}"><p class="eyebrow">NEXT UP · {esc(sitting["label"].upper())}</p><p class="count-number"><span id="days">{days}</span><span class="count-unit" id="days-label">{"day to go" if days == 1 else "days to go"}</span></p><div class="count-line"></div><p class="count-details">SQE1 · FLK1 begins {date.fromisoformat(sitting["flk1_date"]).day} {date.fromisoformat(sitting["flk1_date"]):%B}<br><span>{f"FLK2 begins {flk2.day} {flk2:%B}" if flk2 else "FLK2 date to be confirmed"}</span>{exam_link}</p></div>'
    home = re.sub(r'<div class="countdown".*?</p></div>', lambda m: countdown, home, count=1, flags=re.S)
    if questions:
        current = questions[-1]
        band = practice(current, home=True)
        end = '      </div>\n    </section>'
        assert band.endswith(end + '\n'), 'Unexpected practice band markup'
        band = band[:-len(end) - 1] + f'      <nav class="question-navigation" aria-label="Question links"><a id="permalink" href="{current["route"]}">Permanent link to this question</a><a href="/archive/">Browse the archive</a></nav>\n' + end + '\n'
        payload = json.dumps(current, ensure_ascii=False).replace('<', '\\u003c')
        band += f'<script type="application/json" id="home-question-data">{payload}</script>\n'
        recent = list(reversed(questions[:-1]))[:RECENT]
        if recent:
            items = ''.join(f'<li><div class="archive-meta"><time datetime="{q["publish_date"]}">{q["publish_date"]}</time><span>{esc(q["subject"])} · {q["flk"]}</span><span>No. {q["number"]:02}</span></div><h3><a href="{q["route"]}">{esc(q["title"])}</a></h3><p>{esc(q["stem"])}</p></li>' for q in recent)
            band += f'    <section class="recent-questions wrap" aria-labelledby="recent-heading"><div class="section-heading"><h2 id="recent-heading">Recent questions</h2><a href="/archive/">All questions</a></div><ol class="archive-list">{items}</ol></section>\n'
        assert practice_source in home
        home = home.replace(practice_source, band)
    else:
        home = home.replace('id="stem"></h2>', 'id="stem">Daily practice</h2>').replace('id="question-title"></h4>', 'id="question-title">Explanation</h4>').replace('id="authority-link" target=', 'id="authority-link" href="/archive/" target=')
    write('index.html', home)

    # lastmod only where a real date backs it: publication or a genuine content change, never a review.
    changed = lambda qs: max((q.get('last_modified') or q['publish_date'] for q in qs), default=None)
    urls = [('/', changed(questions)), ('/archive/', changed(questions)), ('/about/', None), ('/sponsor/', None), ('/privacy/', None)]
    urls += [(f'/{name}/', entry.get('last_modified')) for name, entry in pages.items()]
    urls += [('/archive/' + subject_slug(s) + '/', changed([q for q in questions if q['subject'] == s])) for s in subjects]
    urls += [(q['route'], q.get('last_modified') or q['publish_date']) for q in questions]
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
    print(f'Generated {len(questions)} published questions for {day}.')
    return questions

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=london_today())
    parser.add_argument('--package', action='store_true')
    parser.add_argument('--owned', action='store_true', help='List generator-owned paths for the publish commit.')
    args = parser.parse_args()
    if args.owned:
        print('\n'.join([*OWNED, LOCK]))
    else:
        datetime.strptime(args.date, '%Y-%m-%d')
        # Previews of other dates must never add future routes to the lock.
        generate(args.date, args.package, write_lock=args.date == london_today())
