"""Use isolated fixtures; never approve or rewrite the real authoring bank."""
import copy
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import generate
import practice_content as p
from test_site import temporary_checkout, check_package

today = generate.london_today()
bank = json.loads((generate.ROOT / 'content/questions.json').read_text())
with tempfile.TemporaryDirectory() as tmp:
    root = temporary_checkout(tmp)
    data = {'version': 1, 'releases': [], 'mocks': []}
    for q in bank:
        e = {'id': q['id'], 'available_from': today, 'question_hash': p.question_hash(q), 'approved': False}
        data['releases'].append(e)
    assert len(p.library(bank, data, today)) == len(generate.published(bank, today))
    for e in data['releases']:
        e.update(approved=True, approved_hash=p.fingerprint(e))
    assert len(p.library(bank, data, today)) == len(bank)
    changed = copy.deepcopy(bank); changed[-1]['answer'] = 'B' if changed[-1]['answer'] != 'B' else 'A'
    assert len(p.library(changed, data, today)) == len(bank)-1
    (root / 'content/practice.json').write_text(json.dumps(data))
    with patch.object(generate, 'ROOT', root):
        generated = generate.generate(today, True, False)
    assert len(generated) == len(bank)
    check_package(root / '_site', today, root)
    home = (root / 'index.html').read_text()
    current = generate.published(bank, today)[-1]
    assert current['scenario'].replace('&','&amp;').replace("'",'&#x27;') in home
    assert generated[-1]['available_from'] == today
    assert generated[-1]['publish_date'] == bank[-1]['publish_date'], 'daily/email dates must not move'
    bad = copy.deepcopy(data); bad['releases'][0]['available_from'] = '2000-01-01'
    (root / 'content/practice.json').write_text(json.dumps(bad))
    try: p.read(root)
    except ValueError: pass
    else: raise AssertionError('Edited approval accepted')
    (root / 'content/practice.json').write_text(json.dumps(data))
    try: p.approve(root, 'releases.'+bank[0]['id'], '0'*12)
    except ValueError: pass
    else: raise AssertionError('Wrong fingerprint accepted')
    library_only = {**bank[-1], 'id': 'library-only-fixture', 'number': 9999, 'publish_date': None, 'title': 'Library-only fixture', 'scenario': 'Library-only fixture. ' + bank[-1]['scenario']}
    assert not any(q['id'] == library_only['id'] for q in p.library(bank+[library_only], data, today))
    entry = {'id': library_only['id'], 'available_from': today, 'question_hash': p.question_hash(library_only), 'approved': False}
    data['releases'].append(entry)
    (root / 'content/questions.json').write_text(json.dumps(bank+[library_only]))
    (root / 'content/practice.json').write_text(json.dumps(data))
    p.approve(root, 'releases.'+entry['id'], p.fingerprint(entry)[:12])
    with patch.object(generate, 'ROOT', root):
        generated = generate.generate(today, True, False)
    assert any(q['publish_date'] is None for q in generated)
    assert library_only['id'] not in [q['id'] for q in generate.published(generated, today)]
    check_package(root / '_site', today, root)
    # Re-approval works after changing an entry; editing never silently preserves approval.
    changed_data = json.loads((root / 'content/practice.json').read_text())
    changed_data['releases'][-1]['question_hash'] = '0'*64
    (root / 'content/practice.json').write_text(json.dumps(changed_data))
    p.approve(root, 'releases.'+entry['id'], p.fingerprint(changed_data['releases'][-1])[:12])
    assert p.read(root)['releases'][-1]['approved']
    # Mock manifest readiness is a separate gate from library availability.
    groups = [['Business Law & Practice', 'Dispute Resolution', 'Legal Services'], ['Contract', 'Tort', 'Legal System of England and Wales', 'Constitutional & Administrative Law']]
    fixtures = [{**bank[0], 'id': f'fixture-{i}', 'subject': groups[i//85][i % len(groups[i//85])]} for i in range(170)]
    e = {'id':'fixture','title':'Fixture','paper':'FLK1','law_cutoff':'2026-09-11','source_url':'https://sqe.sra.org.uk/assessments/assessment-days/SQE1',
         'sessions':[[q['id'] for q in fixtures[:85]],[q['id'] for q in fixtures[85:]]],
         'question_hashes':{q['id']:p.question_hash(q) for q in fixtures},'approved':False}
    data['mocks']=[e]
    assert p.mocks(fixtures,fixtures,data)==[]
    e.update(approved=True,approved_hash=p.fingerprint(e))
    assert len(p.mocks(fixtures,fixtures,data))==1
    old_subject = fixtures[0]['subject']; fixtures[0]['subject']='Trusts'
    try: p.mocks(fixtures,fixtures,data)
    except ValueError: pass
    else: raise AssertionError('Wrong session subject accepted')
    fixtures[0]['subject']=old_subject
    assert p.mocks(fixtures,fixtures[:-1],data)==[]
    fixtures[0]['answer']='E'; assert p.mocks(fixtures,fixtures,data)==[]
    e['sessions'][1][0]=e['sessions'][0][0]
    e['approved_hash']=p.fingerprint(e)
    try: p.mocks(fixtures,fixtures,data)
    except ValueError: pass
    else: raise AssertionError('Duplicate mock IDs accepted')
print('PASS: early release approval/correction gates, original daily dates, library SEO, mock readiness and duplicates')
