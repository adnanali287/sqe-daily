"""Check the deployed static package, internal links and future exclusion."""
import json
import tempfile
from datetime import datetime
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
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            assert a['id'] not in self.ids, f'Duplicate id: {a["id"]}'
            self.ids.add(a['id'])
        if tag == 'h1': self.headings += 1
        for key in ['href', 'src']:
            if a.get(key): self.links.append(a[key])

def check_package(root, today):
    bank = json.loads((root / 'content/questions.json').read_text())
    assert all(q['publish_date'] <= today for q in bank)
    docs = {}
    for path in root.rglob('*.html'):
        document = Document(); document.feed(path.read_text()); docs[path] = document
        assert document.headings == 1, f'Expected one h1: {path}'
        assert 'rel="canonical"' in path.read_text()
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
    sitemap = ET.parse(root / 'sitemap.xml')
    urls = {node.text for node in sitemap.findall('.//{*}loc')}
    assert all(generate.BASE + generate.route(q) in urls for q in bank)
    assert len(list((root / 'q').glob('*/index.html'))) == len(bank)
    ET.parse(root / 'feed.xml')
    print(f'PASS: {len(docs)} HTML pages, links/fragments, sitemap, RSS, dates and headings')

def future_test(today):
    # Use a temporary checkout with an appended future fixture; never touch the real bank.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name in ['scripts', 'assets', 'content']:
            generate.shutil.copytree(generate.ROOT / name, root / name)
        for name in ['CNAME', '.nojekyll']:
            generate.shutil.copy2(generate.ROOT / name, root / name)
        data = json.loads((root / 'content/questions.json').read_text())
        fixture = {**data[0], 'id': 'future-fixture', 'number': 99999, 'title': 'FUTURE_SENTINEL_NEVER_PUBLISH', 'publish_date': '2099-12-31'}
        data.append(fixture)
        (root / 'content/questions.json').write_text(json.dumps(data))
        with patch.object(generate, 'ROOT', root): generate.generate(today, True)
        for file in (root / '_site').rglob('*'):
            if file.suffix in ['.html', '.json', '.xml']:
                assert 'FUTURE_SENTINEL_NEVER_PUBLISH' not in file.read_text()
        check_package(root / '_site', today)
    print('PASS: appended future fixture absent from every deployed HTML/JSON/XML file')

if __name__ == '__main__':
    today = datetime.now(ZoneInfo('Europe/London')).date().isoformat()
    check_package(generate.ROOT / '_site', today)
    future_test(today)
    future_test('2026-11-01')
