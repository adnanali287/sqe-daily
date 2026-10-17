"""Check the deployed static package, internal links, SEO metadata, route lock and future exclusion."""
import html
import json
import os
import re
import struct
import subprocess
import tempfile
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo
import generate

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set(); self.links = []; self.headings = 0; self.icons = []
        self.title = ''; self.description = None; self.noindex = False; self.json_ld = []; self._capture = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id: {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'h1': self.headings += 1
        if tag == 'link' and a.get('rel') == 'icon': self.icons.append(a)
        if tag == 'title': self._capture = 'title'
        if tag == 'script' and a.get('type') == 'application/ld+json': self._capture = 'json'; self.json_ld.append('')
        if tag == 'meta' and a.get('name') == 'description': self.description = a.get('content')
        if tag == 'meta' and a.get('name') == 'robots' and 'noindex' in a.get('content', ''): self.noindex = True
        for key in ['href', 'src']:
            if a.get(key): self.links.append(a[key])
    def handle_endtag(self, tag):
        if tag in ['title', 'script']: self._capture = None
    def handle_data(self, data):
        if self._capture == 'title': self.title += data
        if self._capture == 'json': self.json_ld[-1] += data

def iso(value):
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), value
    return date.fromisoformat(value)

def check_package(root, today, repo):
    favicon = (root / 'assets/favicon.png').read_bytes()
    assert favicon[:8] == b'\x89PNG\r\n\x1a\n', 'Raster favicon must be a real PNG'
    assert struct.unpack('>II', favicon[16:24]) == (96, 96), 'Favicon must match its declared square size'
    bank = json.loads((root / 'content/questions.json').read_text())
    assert all(q.get('available_from', q['publish_date']) <= today for q in bank)
    routes = {q['id']: q['route'] for q in bank}
    lock_path = repo / generate.LOCK
    lock = json.loads(lock_path.read_text())['questions'] if lock_path.exists() else {}
    assert all(routes[i] == lock[i]['route'] for i in routes if i in lock), 'Deployed routes must match the route lock'
    docs = {}
    for path in root.rglob('*.html'):
        text = path.read_text()
        document = Document(); document.feed(text); docs[path] = document
        assert document.headings == 1, f'Expected one h1: {path}'
        assert 'rel="canonical"' in text
        assert any(icon.get('href') == '/assets/favicon.png' and icon.get('type') == 'image/png' and icon.get('sizes') == '96x96' for icon in document.icons), f'Missing Google-compatible favicon: {path}'
        assert any(icon.get('href') == '/assets/favicon.svg' and icon.get('sizes') == 'any' for icon in document.icons), f'Missing SVG browser favicon: {path}'
        assert '"Person"' not in text, f'No Person entity may be published: {path}'
        for block in document.json_ld:
            data = json.loads(block)
            for item in data if isinstance(data, list) else [data]:
                if item.get('@type') in ['Quiz', 'WebPage']:
                    assert item['author']['@type'] == 'Organization' and item['publisher']['@type'] == 'Organization', path
    for path, doc in docs.items():
        for link in doc.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc: continue
            target = root / unquote(parsed.path).lstrip('/') if parsed.path.startswith('/') else path.parent / unquote(parsed.path)
            if not parsed.path: target = path
            if target.is_dir(): target /= 'index.html'
            assert target.exists(), f'Broken link {path}: {link}'
            if parsed.fragment and target in docs:
                assert parsed.fragment in docs[target].ids, f'Broken fragment {path}: {link}'
    indexable = [doc for doc in docs.values() if not doc.noindex]
    titles = [doc.title for doc in indexable]; descriptions = [doc.description for doc in indexable]
    assert len(set(titles)) == len(titles), 'Page titles must be unique'
    assert all(descriptions) and len(set(descriptions)) == len(descriptions), 'Meta descriptions must exist and be unique'

    # Sitemap: every URL is in the package; lastmod only where publication or a genuine change backs it.
    sitemap = ET.parse(root / 'sitemap.xml')
    entries = {node.find('{*}loc').text: node.find('{*}lastmod') for node in sitemap.findall('{*}url')}
    latest = max(date.fromisoformat(today), datetime.now(ZoneInfo('Europe/London')).date())
    for url, lastmod in entries.items():
        target = root / urlsplit(url).path.lstrip('/') / 'index.html'
        assert target.exists(), f'Sitemap URL not in package: {url}'
        if lastmod is not None: assert iso(lastmod.text) <= latest, url
    for q in bank:
        assert entries[generate.BASE + q['route']].text == (q['modified'] or q.get('available_from', q['publish_date']))
    for url in ['/about/', '/sponsor/', '/privacy/']:
        assert entries[generate.BASE + url] is None, f'No dated change backs {url}'
    assert {f'/q/{p.parent.name}/' for p in (root / 'q').glob('*/index.html')} == set(routes.values())
    daily = generate.published(bank, today)
    check_feed(root, daily)
    check_latest(root, bank, daily, today, repo)

    # Homepage: the current question, its permanent link and the no-JavaScript reveal are in the HTML.
    home = (root / 'index.html').read_text()
    if daily:
        current = daily[-1]
        assert html.escape(current['scenario']) in home and home.count('class="option"') == 5
        assert f'id="permalink" href="{current["route"]}"' in home
        assert generate.NOSCRIPT_STYLE in home and 'id="home-question-data"' in home

    # Unapproved or later-release pages are never built; everything generated is packaged.
    pages_path = repo / 'content/pages.json'
    content = json.loads(pages_path.read_text()) if pages_path.exists() else {}
    for name, entry in content.get('pages', {}).items():
        assert (root / name).exists() == generate.is_approved(entry), f'Approval gate failed for {name}'
    for name, entry in content.get('guides', {}).items():
        assert (root / 'guides' / name).exists() == generate.is_approved(entry), f'Approval gate failed for guide {name}'
    for name, entry in content.get('subjects', {}).items():
        page = root / 'archive' / generate.SUBJECTS[name] / 'index.html'
        if page.exists():
            assert ('id="rules-heading"' in page.read_text()) == generate.is_approved(entry), f'Approval gate failed for {name} introduction'
    for name in generate.OWNED:
        source = repo / name
        if source.is_dir():
            assert {p.relative_to(source) for p in source.rglob('*.html')} == {p.relative_to(root / name) for p in (root / name).rglob('*.html')}, f'Generated pages missing from package: {name}'
        elif source.exists():
            assert (root / name).exists(), f'Generated file missing from package: {name}'
    print(f'PASS: {len(docs)} HTML pages, links/fragments, metadata, JSON-LD, sitemap, RSS, routes, approval gate and packaging')

def check_feed(root, daily):
    """RSS lists due daily issues only, newest first, dated London midnight of the feature day, with route GUIDs."""
    items = ET.parse(root / 'feed.xml').findall('.//item')
    expected = list(reversed(daily))
    assert [item.findtext('link') for item in items] == [generate.BASE + q['route'] for q in expected], 'Feed must list due daily issues only, newest first'
    assert [item.findtext('guid') for item in items] == [generate.BASE + q['route'] for q in expected], 'Feed GUIDs are the locked routes'
    for item, q in zip(items, expected):
        offset = '+0100' if datetime.fromisoformat(q['publish_date']).replace(tzinfo=ZoneInfo('Europe/London')).utcoffset() else '+0000'
        assert item.findtext('pubDate') == f'{datetime.fromisoformat(q["publish_date"]):%a, %d %b %Y} 00:00:00 {offset}', item.findtext('pubDate')

def check_latest(root, bank, daily, today, repo):
    """latest.json: the current daily, then the next daily only if it is already released with approved content."""
    latest = json.loads((root / 'content/latest.json').read_text())
    assert latest[:1] == daily[-1:], 'latest.json must start with the homepage question'
    embedded = re.search(r'id="home-question-data">(.*?)</script>', (root / 'index.html').read_text())
    if daily:
        assert json.loads(embedded.group(1)) == latest[0], 'latest.json and the embedded homepage question must match'
    authoring = json.loads((repo / 'content/questions.json').read_text())
    upcoming = sorted((q for q in authoring if q['publish_date'] and q['publish_date'] > today), key=lambda q: (q['publish_date'], q['number']))
    released = {q['id']: q for q in bank}
    expected_next = [released[upcoming[0]['id']]] if upcoming and upcoming[0]['id'] in released else []
    assert latest[len(daily[-1:]):] == expected_next, 'latest.json may add only the next daily, and only once released'
    assert all(q['publish_date'] and not q.get('library_number') for q in latest), 'Library-only questions never enter latest.json'

def temporary_checkout(tmp):
    root = Path(tmp)
    for name in ['scripts', 'assets', 'content']:
        generate.shutil.copytree(generate.ROOT / name, root / name)
    for name in ['CNAME', '.nojekyll']:
        generate.shutil.copy2(generate.ROOT / name, root / name)
    return root

def build(root, day, write_lock=False):
    with patch.object(generate, 'ROOT', root):
        return generate.generate(day, True, write_lock)

def future_test(today):
    # Use a temporary checkout with an appended future fixture; never touch the real bank.
    with tempfile.TemporaryDirectory() as tmp:
        root = temporary_checkout(tmp)
        data = json.loads((root / 'content/questions.json').read_text())
        fixture = {**data[0], 'id': 'future-fixture', 'number': 99999, 'title': 'FUTURE_SENTINEL_NEVER_PUBLISH', 'publish_date': '2099-12-31'}
        data.append(fixture)
        (root / 'content/questions.json').write_text(json.dumps(data))
        lock_before = (root / generate.LOCK).read_bytes()
        build(root, today)
        before = {str(f.relative_to(root / '_site')): f.read_bytes() for f in (root / '_site').rglob('*') if f.is_file()}
        build(root, today)
        after = {str(f.relative_to(root / '_site')): f.read_bytes() for f in (root / '_site').rglob('*') if f.is_file()}
        assert before == after, 'Generation must be reproducible'
        assert (root / generate.LOCK).read_bytes() == lock_before, 'Preview builds must not write the route lock'
        for file in (root / '_site').rglob('*'):
            if file.suffix in ['.html', '.json', '.xml']:
                assert 'FUTURE_SENTINEL_NEVER_PUBLISH' not in file.read_text()
        check_package(root / '_site', today, root)
    print('PASS: reproducible generation; future fixture absent; preview leaves the route lock unchanged')

def expect_error(root, day, message):
    try:
        build(root, day)
    except ValueError as error:
        assert message in str(error), error
    else:
        raise AssertionError(f'Expected build to fail: {message}')

def content_test(today):
    """Route lock, subject guard, optional fields and the pages.json approval gate."""
    with tempfile.TemporaryDirectory() as tmp:
        root = temporary_checkout(tmp)
        bank_path = root / 'content/questions.json'
        original = bank_path.read_text()
        build(root, today, write_lock=True)
        first = json.loads(original)[0]
        locked = json.loads((root / generate.LOCK).read_text())['questions'][first['id']]['route']
        lastmod = lambda url: re.search(re.escape(generate.BASE + url) + r'</loc><lastmod>([\d-]+)<', (root / 'sitemap.xml').read_text()).group(1)
        real_today = generate.london_today()
        baseline_lastmod = lastmod(locked)
        baseline_page = (root / locked.lstrip('/') / 'index.html').read_text()
        baseline_modified = re.findall(r'"dateModified": "[^"]+"', baseline_page)

        # A title edit changes the title and h1, never the URL.
        data = json.loads(original); data[0]['title'] += ' (edited)'
        bank_path.write_text(json.dumps(data))
        questions = build(root, today)
        assert questions[0]['route'] == locked and (root / locked.lstrip('/') / 'index.html').exists()
        page = (root / locked.lstrip('/') / 'index.html').read_text()
        assert data[0]['title'].replace("'", '&#x27;') in page
        # ...and a title-only edit is a genuine modification: lastmod and dateModified move to the build date.
        assert lastmod(locked) == real_today and f'"dateModified": "{real_today}"' in page

        # A source re-check alone (last_reviewed) is not a modification.
        data = json.loads(original); data[0]['last_reviewed'] = data[0]['publish_date']
        bank_path.write_text(json.dumps(data))
        build(root, today)
        assert lastmod(locked) == baseline_lastmod
        assert re.findall(r'"dateModified": "[^"]+"', (root / locked.lstrip('/') / 'index.html').read_text()) == baseline_modified

        # Hand-editing the lock for a published page fails the build.
        bank_path.write_text(original)
        lock = json.loads((root / generate.LOCK).read_text()); lock['questions'][first['id']]['route'] = f'/q/{first["number"]}-moved/'
        (root / generate.LOCK).write_text(json.dumps(lock))
        expect_error(root, today, 'would move a published page')
        lock['questions'][first['id']]['route'] = locked
        (root / generate.LOCK).write_text(json.dumps(lock))

        # Unknown subjects and invalid optional fields are rejected.
        data = json.loads(original); data[0]['subject'] = 'Wills and Administration of Estates'
        bank_path.write_text(json.dumps(data)); expect_error(root, today, 'Unknown subject')
        data = json.loads(original); data[0]['why_wrong'] = {'A': 'Only one reason.'}
        bank_path.write_text(json.dumps(data)); expect_error(root, today, 'why_wrong')
        data = json.loads(original); data[0]['last_reviewed'] = '2099-01-01'
        bank_path.write_text(json.dumps(data)); expect_error(root, today, 'cannot be in the future')

        # Optional fields render; last_modified drives lastmod, last_reviewed drives only the checked line.
        data = json.loads(original)
        q = data[0]
        q['why_wrong'] = {k: f'Reason {k}.' for k in 'ABCDE' if k != q['answer']}
        q['tags'] = ['test topic']; q['last_reviewed'] = q['publish_date']; q['last_modified'] = q['publish_date']
        data[1]['last_reviewed'] = data[1]['publish_date']
        bank_path.write_text(json.dumps(data))
        build(root, today)
        page = (root / locked.lstrip('/') / 'index.html').read_text()
        wrong = next(k for k in 'ABCDE' if k != q['answer'])
        assert f'Why {wrong} is wrong: Reason {wrong}.' in page and f'\n{wrong} is wrong:' not in page
        assert f'Checked against primary source on {generate.long_date(q["publish_date"])}' in page
        assert '"dateModified"' in page

        # pages.json: nothing is built until approved, then it joins the footer, sitemap and question pages.
        pages_path = root / 'content/pages.json'
        entry = {'title': 'Editorial standards', 'meta_description': 'How SQE Daily writes and checks questions.', 'h1': 'Editorial standards', 'intro': 'How we write questions.\n\nSee [the SRA](https://www.sra.org.uk/).', 'sections': [{'heading': 'Corrections', 'body': 'Email us.'}], 'sources': [], 'approved': False}
        sitting = {'label': 'Test sitting', 'flk1_date': '2099-01-11', 'flk2_date': None, 'booking_closes': None, 'results_date': None, 'source_url': 'https://www.sra.org.uk/', 'approved': False}
        pages_path.write_text(json.dumps({'sittings': [sitting], 'pages': {'editorial-standards': entry}}))
        build(root, today)
        assert not (root / 'editorial-standards').exists() and '/editorial-standards/' not in (root / 'index.html').read_text()
        # Setting approved by hand, without the approval hash, publishes nothing.
        entry['approved'] = True
        pages_path.write_text(json.dumps({'sittings': [sitting], 'pages': {'editorial-standards': entry}}))
        build(root, today)
        assert not (root / 'editorial-standards').exists()
        with patch.object(generate, 'ROOT', root):
            generate.approve('pages.editorial-standards'); generate.approve('sittings.0')
        build(root, today)
        assert (root / 'editorial-standards').exists() and 'NEXT UP · TEST SITTING' in (root / 'index.html').read_text()
        # Editing approved copy withdraws the approval until it is approved again.
        approved_copy = json.loads(pages_path.read_text())
        edited = json.loads(pages_path.read_text())
        edited['pages']['editorial-standards']['intro'] += ' Unreviewed sentence.'
        edited['sittings'][0]['flk1_date'] = '2099-02-01'
        pages_path.write_text(json.dumps(edited))
        build(root, today)
        assert not (root / 'editorial-standards').exists() and 'Unreviewed sentence' not in (root / 'sitemap.xml').read_text()
        assert 'NEXT UP · JANUARY 2027' in (root / 'index.html').read_text(), 'An edited sitting must not drive the countdown'
        assert generate.stale_approvals(edited) == ['sittings.0', 'pages.editorial-standards']
        assert generate.stale_approvals(approved_copy) == []
        with patch.object(generate, 'ROOT', root):
            generate.approve('pages.editorial-standards')
        build(root, today)
        standards = (root / '_site/editorial-standards/index.html').read_text()
        assert '<a href="https://www.sra.org.uk/">the SRA</a>' in standards
        assert '/editorial-standards/' in (root / 'index.html').read_text()
        assert 'How we check questions' in (root / locked.lstrip('/') / 'index.html').read_text()
        assert generate.BASE + '/editorial-standards/' in (root / 'sitemap.xml').read_text()
        check_package(root / '_site', today, root)

        # Subject introductions (rendered from PR 2): an approved intro change records a modification.
        intro = {'intro': 'An overview of contract.', 'approved': False}
        pages_path.write_text(json.dumps({'subjects': {'Contract': intro}}))
        with patch.object(generate, 'ROOT', root), patch.object(generate, 'SUBJECT_INTROS_LIVE', True):
            generate.approve('subjects.Contract')
            generate.generate(today, True, True)
            contract = json.loads((root / generate.LOCK).read_text())['subjects']['Contract']
            assert contract['intro_hash'] and contract['modified'] == real_today
            assert lastmod('/archive/contract/') == real_today
            first_hash = contract['intro_hash']
            data = json.loads(pages_path.read_text()); data['subjects']['Contract']['intro'] += ' More.'
            pages_path.write_text(json.dumps(data)); generate.approve('subjects.Contract')
            generate.generate(today, True, True)
            assert json.loads((root / generate.LOCK).read_text())['subjects']['Contract']['intro_hash'] != first_hash
    print('PASS: route lock, subject guard, optional fields, title and intro modification dates, approval gate and re-approval')

def editorial_test(today):
    """The full editorial batch: approval gating, page dates, discoverability, related questions and re-approval."""
    real_today = generate.london_today()
    # Every question in the bank is published by its last publish_date (no longer hard-coded, so appending questions keeps this test valid).
    full = max(q['publish_date'] for q in json.loads((generate.ROOT / 'content/questions.json').read_text()) if q['publish_date'])
    with tempfile.TemporaryDirectory() as tmp:
        root = temporary_checkout(tmp)
        pages_path = root / 'content/pages.json'
        if not pages_path.exists():
            print('SKIP: no content/pages.json'); return
        bank_path = root / 'content/questions.json'
        bank = json.loads(bank_path.read_text())
        # Shared tags across papers: tags outrank subject and paper.
        bank[0]['tags'] = ['shared topic']; bank[-1]['tags'] = ['shared topic']
        bank_path.write_text(json.dumps(bank))
        # This fixture tests first publication, not the real pages' historical dates.
        lock_path = root / generate.LOCK
        fixture_lock = json.loads(lock_path.read_text())
        fixture_lock['pages'] = {}
        for subject in fixture_lock['subjects'].values():
            if isinstance(subject, dict):
                subject.update(intro_hash=None, modified=None)
        lock_path.write_text(json.dumps(fixture_lock))
        data = json.loads(pages_path.read_text())
        # Start from an unapproved copy so the gate is tested whatever the real approval state is.
        for _, entry in generate.approval_entries(data):
            entry['approved'] = False; entry.pop('approved_hash', None)
        pages_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        labels = [label for label, _ in generate.approval_entries(data)]
        build(root, full)
        assert not any((root / name).exists() for name in [*generate.PAGES, 'guides']), 'Unapproved copy must not publish'

        with patch.object(generate, 'ROOT', root):
            fingerprint = generate.content_hash(json.loads(pages_path.read_text())['pages']['editorial-standards'], generate.APPROVAL_FIELDS)[:12]
            try:
                generate.approve('pages.editorial-standards', '000000000000')
            except SystemExit as error:
                assert 'has changed since it was presented' in str(error)
            else:
                raise AssertionError('A wrong fingerprint must refuse approval')
            generate.approve('pages.editorial-standards', fingerprint)
            for label in labels:
                generate.approve(label)
        questions = build(root, full, write_lock=True)
        site = root / '_site'
        for path in [*[f'{name}/index.html' for name in generate.PAGES], 'guides/index.html', *[f'guides/{name}/index.html' for name in data['guides']]]:
            assert (site / path).exists(), path
        home = (site / 'index.html').read_text()
        for link in ['/sqe1-practice-questions/', '/sqe1-exam-dates/', '/guides/', '/editorial-standards/']:
            assert f'href="{link}"' in home, f'Footer must link {link}'
        hub = (site / 'sqe1-practice-questions/index.html').read_text()
        assert 'href="/flk1/"' in hub and 'href="/flk2/"' in hub and all(f'href="/guides/{name}/"' in hub for name in data['guides'])
        flk2 = (site / 'flk2/index.html').read_text()
        latest_flk2 = [q for q in reversed(questions) if q['flk'] == 'FLK2'][:generate.LATEST]
        assert all(q['route'] in flk2 for q in latest_flk2) and not any(f'href="{q["route"]}"' in flk2 for q in questions if q['flk'] == 'FLK1')
        dates = (site / 'sqe1-exam-dates/index.html').read_text()
        assert 'FLK1: 11–15 January 2027' in dates and 'Booking closes: 23 November 2026' in dates and 'Results: 9 March 2027' in dates
        assert 'NEXT UP · JANUARY 2027' in home
        guide = (site / 'guides/sqe1-revision-timetable/index.html').read_text()
        assert '"@type": "Article"' in guide and f'"datePublished": "{real_today}"' in guide and '"Person"' not in guide
        contract = (site / 'archive/contract/index.html').read_text()
        assert '<title>SQE1 Contract practice questions (free, with answers) | SQE Daily</title>' in contract and 'id="rules-heading"' in contract
        assert all(q['key_rule'].replace("'", '&#x27;') in contract for q in questions if q['subject'] == 'Contract')
        lock = json.loads((root / generate.LOCK).read_text())
        assert lock['pages']['guides.sqe1-revision-timetable'] == {'hash': lock['pages']['guides.sqe1-revision-timetable']['hash'], 'published': real_today, 'modified': None}
        assert lock['subjects']['Contract']['modified'] == real_today

        # Related questions: up to three, never the question itself, locked routes, shared tags first.
        routes = {q['route'] for q in questions}
        for q in questions:
            page = (root / q['route'].lstrip('/') / 'index.html').read_text()
            if 'id="related-heading"' not in page:
                continue
            related = re.findall(r'<h3><a href="([^"]+)"', page.split('id="related-heading"')[1].split('</section>')[0])
            assert 1 <= len(related) <= generate.RELATED and q['route'] not in related and set(related) <= routes, q['id']
        first = (root / questions[0]['route'].lstrip('/') / 'index.html').read_text().split('id="related-heading"')[1]
        tagged = next(q for q in questions if q['id'] == bank[-1]['id'])
        assert re.findall(r'<h3><a href="([^"]+)"', first)[0] == tagged['route'], 'A shared tag must outrank subject and paper'
        check_package(site, full, root)

        # Editing approved copy withdraws it; links to it become plain text, never broken links.
        edited = json.loads(pages_path.read_text())
        edited['guides']['sqe1-revision-timetable']['intro'] += ' An unreviewed sentence.'
        pages_path.write_text(json.dumps(edited))
        build(root, full)
        assert not (site / 'guides/sqe1-revision-timetable').exists()
        assert 'href="/guides/sqe1-revision-timetable/"' not in (site / 'sqe1-exam-dates/index.html').read_text()
        assert 'SQE1 revision timetable' in (site / 'sqe1-exam-dates/index.html').read_text()
        check_package(site, full, root)
        # Re-approval republishes it and records the change date.
        with patch.object(generate, 'ROOT', root):
            generate.approve('guides.sqe1-revision-timetable')
        build(root, full, write_lock=True)
        assert json.loads((root / generate.LOCK).read_text())['pages']['guides.sqe1-revision-timetable']['modified'] == real_today
        assert (site / 'guides/sqe1-revision-timetable/index.html').exists()
    print('PASS: editorial batch gating, fingerprinted approval, page dates, discoverability, related questions, withdrawal and re-approval')

def homepage_feed_test(today):
    """latest.json and RSS against the release gate, later dates and BST/GMT boundaries."""
    with tempfile.TemporaryDirectory() as tmp:
        root = temporary_checkout(tmp)
        authoring = json.loads((root / 'content/questions.json').read_text())
        dates = sorted(q['publish_date'] for q in authoring if q['publish_date'])
        practice_path = root / 'content/practice.json'
        practice = json.loads(practice_path.read_text())
        upcoming = sorted((q for q in authoring if q['publish_date'] and q['publish_date'] > today), key=lambda q: (q['publish_date'], q['number']))
        if not upcoming:
            print('SKIP: no future daily question to test the release gate'); return
        target = upcoming[0]
        latest = lambda: [q['id'] for q in json.loads((root / '_site/content/latest.json').read_text())]
        current = [q['id'] for q in generate.published(authoring, today)][-1:]
        build(root, today)
        released = any(entry['id'] == target['id'] and practice_content_approved(entry) for entry in practice['releases'])
        assert latest() == current + ([target['id']] if released else [])

        # An unreleased next daily is excluded, as is one whose content changed after its release was approved.
        practice['releases'] = [entry for entry in practice['releases'] if entry['id'] != target['id']]
        practice_path.write_text(json.dumps(practice))
        build(root, today)
        assert latest() == current, 'An unreleased next daily must not appear in latest.json'
        assert target['title'] not in (root / '_site/feed.xml').read_text()
        check_package(root / '_site', today, root)
        generate.shutil.copy2(generate.ROOT / 'content/practice.json', practice_path)
        edited = [{**q, 'stem': q['stem'] + ' UNAPPROVED_EDIT'} if q['id'] == target['id'] else q for q in authoring]
        (root / 'content/questions.json').write_text(json.dumps(edited))
        build(root, today)
        assert latest() == current, 'Content changed after approval must not appear in latest.json'
        assert not any('UNAPPROVED_EDIT' in f.read_text() for f in (root / '_site').rglob('*') if f.suffix in ['.json', '.xml', '.html'])
        (root / 'content/questions.json').write_text(json.dumps(authoring))

        # Later builds add exactly the newly due issues to the feed; earlier items keep their GUIDs and dates.
        build(root, today)
        before = {item.findtext('guid'): item.findtext('pubDate') for item in ET.parse(root / '_site/feed.xml').findall('.//item')}
        later = upcoming[min(2, len(upcoming) - 1)]['publish_date']
        build(root, later)
        after = {item.findtext('guid'): item.findtext('pubDate') for item in ET.parse(root / '_site/feed.xml').findall('.//item')}
        assert all(after[guid] == date for guid, date in before.items()), 'Existing feed items must keep their GUID and date'
        assert len(after) - len(before) == sum(1 for q in authoring if q['publish_date'] and today < q['publish_date'] <= later)
        check_package(root / '_site', later, root)

        # BST and GMT: 25 October 2026 is the change back to GMT.
        assert generate.london_midnight('2026-10-24') == 'Sat, 24 Oct 2026 00:00:00 +0100'
        assert generate.london_midnight('2026-10-26') == 'Mon, 26 Oct 2026 00:00:00 +0000'
        assert generate.london_midnight('2027-03-29') == 'Mon, 29 Mar 2027 00:00:00 +0100'
        gmt_day = next((d for d in dates if d >= '2026-10-26'), None)
        if gmt_day:
            build(root, gmt_day)
            check_package(root / '_site', gmt_day, root)
            assert '+0000</pubDate>' in (root / '_site/feed.xml').read_text() and '+0100</pubDate>' in (root / '_site/feed.xml').read_text()

        # After the last daily: latest.json keeps the last past question only.
        build(root, '2099-01-01')
        assert latest() == [q['id'] for q in generate.published(authoring, '2099-01-01')][-1:]
        check_package(root / '_site', '2099-01-01', root)
    print('PASS: latest.json release gate (unreleased and edited next daily excluded), daily-only RSS, stable GUIDs, BST/GMT pubDate and last-daily fallback')

def practice_content_approved(entry):
    return generate.practice_content.approved(entry)

def lock_unchanged():
    """Committed route-lock entries may be added to, never changed or removed."""
    result = subprocess.run(['git', 'show', 'HEAD:' + generate.LOCK], cwd=generate.ROOT, capture_output=True, text=True)
    if result.returncode:
        print('SKIP: no committed route lock to compare'); return
    committed = json.loads(result.stdout); current = json.loads((generate.ROOT / generate.LOCK).read_text())
    # Only the route or slug is permanent; content hashes and modification dates move with edits.
    permanent = lambda value, field: value if isinstance(value, str) else value and value[field]
    for kind, field in [('questions', 'route'), ('subjects', 'slug')]:
        for key, value in committed[kind].items():
            assert permanent(current[kind].get(key), field) == permanent(value, field), f'Route lock entry changed: {kind}.{key}'
    print('PASS: committed route-lock entries unchanged')

if __name__ == '__main__':
    today = datetime.now(ZoneInfo('Europe/London')).date().isoformat()
    check_package(generate.ROOT / '_site', today, generate.ROOT)
    if os.environ.get('STRICT_APPROVALS') == '1':
        # Pull-request checks: approved copy must carry the hash of the exact text approved.
        pages_path = generate.ROOT / 'content/pages.json'
        stale = generate.stale_approvals(json.loads(pages_path.read_text())) if pages_path.exists() else []
        assert not stale, f'Approved content changed since approval: {stale}. Ask the owner, then run generate.py --approve.'
        print('PASS: every approved entry matches the text that was approved')
    lock_unchanged()
    future_test(today)
    future_test('2026-11-01')
    homepage_feed_test(today)
    content_test(today)
    editorial_test(today)
