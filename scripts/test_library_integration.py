"""Review-preview regression tests; all temporary approvals stay outside the repo."""
import copy
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import generate as g
import practice_content as p
from preview_library import build_preview
from test_site import check_package

bank = g.load_bank()
before_manifest = (g.ROOT/'content/practice.json').read_text()
assert len(bank) >= 368
pending = p.read(g.ROOT)
disabled = copy.deepcopy(pending)
for entry in disabled['releases'] + disabled['mocks']:
    entry['approved'] = False
assert len(p.library(bank, disabled, g.london_today())) == len(g.published(bank,g.london_today()))
assert p.mocks(bank,bank,disabled) == []
assert all(q['number'] > 0 if q['publish_date'] else q['number'] < 0 for q in bank)
assert len({q['id'] for q in bank}) == len({g.route(q) for q in bank}) == len(bank)
original = json.loads((g.ROOT/'docs/library-daily-baseline.json').read_text())
daily = json.loads((g.ROOT/'content/questions.json').read_text())
assert [(q['id'],q['number'],q['publish_date']) for q in original] == [(q['id'],q['number'],q['publish_date']) for q in daily[:len(original)]]
assert all(q['answer'] == before['answer'] for q,before in zip(daily,original))
assert not any('_draft' in q or 'source_quote' in q or 'uncertainty' in q for q in bank)
next_issue = max(q['number'] for q in bank)+1
future_daily = {**bank[0],'id':'future-daily-issue-fixture','number':next_issue,'publish_date':'2099-01-01','title':'Future daily issue numbering fixture'}
g.validate_bank(bank+[future_daily],g.london_today())
assert g.route(future_daily).startswith(f'/q/{next_issue}-')
with tempfile.TemporaryDirectory() as temporary:
    root = build_preview(Path(temporary)/'preview')
    site = root/'_site'
    public = json.loads((site/'content/questions.json').read_text())
    papers = json.loads((site/'content/practice-tests.json').read_text())['mocks']
    assert len(public) >= 368 and len(papers) == 2
    check_package(site, g.london_today(), root)
    for paper in papers:
        assert len(set(sum(paper['sessions'],[]))) == 170
    assert not set(papers[0]['sessions'][0]+papers[0]['sessions'][1]) & set(papers[1]['sessions'][0]+papers[1]['sessions'][1])
    assert all(g.route(q).startswith('/q/lib-') and 'L' in g.question_number(q) for q in public if q.get('library_number'))
    library_question = next(q for q in public if q.get('library_number'))
    page = (site/library_question['route'].lstrip('/')/'index.html').read_text()
    assert f'"datePublished": "{g.london_today()}"' in page and 'Checked against source on' in page
    assert '-1-' not in library_question['route']
    # Session and contextual Accounts metadata must agree with the manifest.
    data = p.read(root)
    altered = copy.deepcopy(bank)
    account = next(q for q in altered if q['subject']=='Solicitors Accounts')
    account['context_subject'] = 'Contract'
    try: p.mocks(altered, altered, data)
    except ValueError: pass
    else: raise AssertionError('Wrong Accounts context accepted')
    with patch.object(g, 'ROOT', root):
        g.generate(g.london_today(), True, True)
        library_path = root/'content/library.json'
        library = json.loads(library_path.read_text())
        selected = next(q for q in library if q['id'] == library_question['id'])
        selected['title'] += ' (title correction fixture)'
        library_path.write_text(json.dumps(library))
        current_manifest = p.read(root)
        release = next(e for e in current_manifest['releases'] if e['id'] == selected['id'])
        release['question_hash'] = p.question_hash(selected)
        release['approved_hash'] = p.fingerprint(release)
        (root/'content/practice.json').write_text(json.dumps(current_manifest))
        refreshed = g.generate(g.london_today(), True, True)
        corrected = next(q for q in refreshed if q['id'] == selected['id'])
        assert corrected['route'] == library_question['route']
        assert corrected['library_number'] == library_question['library_number']
assert before_manifest == (g.ROOT/'content/practice.json').read_text()
print('PASS: 368 gated drafts, unchanged daily schedule/answers, library numbering, public packaging, contextual mocks and no real approvals')
