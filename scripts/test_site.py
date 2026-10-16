"""Check the deployed static package, internal links, SEO metadata, route lock and future exclusion."""
import html
import json
import re
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
        self.ids = set(); self.links = []; self.headings = 0
        self.title = ''; self.description = None; self.noindex = False; self.json_ld = []; self._capture = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id: {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'h1': self.headings += 1
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
    bank = json.loads((root / 'content/questions.json').read_text())
    assert all(q['publish_date'] <= today for q in bank)
    routes = {q['id']: q['route'] for q in bank}
    lock_path = repo / generate.LOCK
    lock = json.loads(lock_path.read_text())['questions'] if lock_path.exists() else {}
    assert all(routes[i] == lock[i] for i in routes if i in lock), 'Deployed routes must match the route lock'
    docs = {}
    for path in root.rglob('*.html'):
        text = path.read_text()
        document = Document(); document.feed(text); docs[path] = document
        assert document.headings == 1, f'Expected one h1: {path}'
        assert 'rel="canonical"' in text
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
        assert entries[generate.BASE + q['route']].text == q.get('last_modified', q['publish_date'])
    for url in ['/about/', '/sponsor/', '/privacy/']:
        assert entries[generate.BASE + url] is None, f'No dated change backs {url}'
    assert {f'/q/{p.parent.name}/' for p in (root / 'q').glob('*/index.html')} == set(routes.values())
    assert {node.text for node in ET.parse(root / 'feed.xml').findall('.//item/link')} == {generate.BASE + r for r in routes.values()}

    # Homepage: the current question, its permanent link and the no-JavaScript reveal are in the HTML.
    home = (root / 'index.html').read_text()
    if bank:
        current = sorted(bank, key=lambda q: (q['publish_date'], q['number']))[-1]
        assert html.escape(current['scenario']) in home and home.count('class="option"') == 5
        assert f'id="permalink" href="{current["route"]}"' in home
        assert generate.NOSCRIPT_STYLE in home and 'id="home-question-data"' in home

    # Unapproved or later-release pages are never built; everything generated is packaged.
    pages_path = repo / 'content/pages.json'
    for name, entry in (json.loads(pages_path.read_text()).get('pages', {}) if pages_path.exists() else {}).items():
        assert (root / name).exists() == (entry['approved'] and name in generate.PAGE_SLUGS), f'Approval gate failed for {name}'
    for name in generate.OWNED:
        source = repo / name
        if source.is_dir():
            assert {p.relative_to(source) for p in source.rglob('*.html')} == {p.relative_to(root / name) for p in (root / name).rglob('*.html')}, f'Generated pages missing from package: {name}'
        elif source.exists():
            assert (root / name).exists(), f'Generated file missing from package: {name}'
    print(f'PASS: {len(docs)} HTML pages, links/fragments, metadata, JSON-LD, sitemap, RSS, routes, approval gate and packaging')

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
        locked = json.loads((root / generate.LOCK).read_text())['questions'][first['id']]

        # A title edit changes the title and h1, never the URL.
        data = json.loads(original); data[0]['title'] += ' (edited)'
        bank_path.write_text(json.dumps(data))
        questions = build(root, today)
        assert questions[0]['route'] == locked and (root / locked.lstrip('/') / 'index.html').exists()
        assert data[0]['title'].replace("'", '&#x27;') in (root / locked.lstrip('/') / 'index.html').read_text()

        # Hand-editing the lock for a published page fails the build.
        lock = json.loads((root / generate.LOCK).read_text()); lock['questions'][first['id']] = f'/q/{first["number"]}-moved/'
        (root / generate.LOCK).write_text(json.dumps(lock))
        expect_error(root, today, 'would move a published page')
        build_lock = json.loads((root / generate.LOCK).read_text()); build_lock['questions'][first['id']] = locked
        (root / generate.LOCK).write_text(json.dumps(build_lock))

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
        entry = {'title': 'Editorial standards', 'meta_description': 'How SQE Daily writes and checks questions.', 'h1': 'Editorial standards', 'intro': 'How we write questions.\n\nSee [the SRA](https://www.sra.org.uk/).', 'sections': [{'heading': 'Corrections', 'body': 'Email us.'}], 'sources': [], 'approved': False}
        (root / 'content/pages.json').write_text(json.dumps({'pages': {'editorial-standards': entry}}))
        build(root, today)
        assert not (root / 'editorial-standards').exists() and '/editorial-standards/' not in (root / 'index.html').read_text()
        entry['approved'] = True
        (root / 'content/pages.json').write_text(json.dumps({'pages': {'editorial-standards': entry}}))
        build(root, today)
        standards = (root / '_site/editorial-standards/index.html').read_text()
        assert '<a href="https://www.sra.org.uk/">the SRA</a>' in standards
        assert '/editorial-standards/' in (root / 'index.html').read_text()
        assert 'How we check questions' in (root / locked.lstrip('/') / 'index.html').read_text()
        assert generate.BASE + '/editorial-standards/' in (root / 'sitemap.xml').read_text()
        check_package(root / '_site', today, root)
    print('PASS: route lock, subject guard, optional fields, lastmod rules and approval gate')

def lock_unchanged():
    """Committed route-lock entries may be added to, never changed or removed."""
    result = subprocess.run(['git', 'show', 'HEAD:' + generate.LOCK], cwd=generate.ROOT, capture_output=True, text=True)
    if result.returncode:
        print('SKIP: no committed route lock to compare'); return
    committed = json.loads(result.stdout); current = json.loads((generate.ROOT / generate.LOCK).read_text())
    for kind in ['questions', 'subjects']:
        for key, value in committed[kind].items():
            assert current[kind].get(key) == value, f'Route lock entry changed: {kind}.{key}'
    print('PASS: committed route-lock entries unchanged')

if __name__ == '__main__':
    today = datetime.now(ZoneInfo('Europe/London')).date().isoformat()
    check_package(generate.ROOT / '_site', today, generate.ROOT)
    lock_unchanged()
    future_test(today)
    future_test('2026-11-01')
    content_test(today)
