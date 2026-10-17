"""Mechanical draft import. Never records approval or changes daily dates."""
import copy
import json
import re
import subprocess
from pathlib import Path
import practice_content as p

ROOT = Path(__file__).resolve().parents[1]


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    source = ROOT / 'drafts/library-2027-01'
    composition = json.loads((source / 'composition.json').read_text())
    metadata = {q['id']: q for q in composition['items']}
    original = json.loads((ROOT / 'content/questions.json').read_text())
    baseline_path = ROOT / 'docs/library-daily-baseline.json'
    if not baseline_path.exists():
        historical = json.loads(subprocess.check_output(['git','show','8d21f41:content/questions.json'],cwd=ROOT))
        write(baseline_path, [{k:q[k] for k in ['id','number','publish_date','answer']} for q in historical])
    audited = json.loads(subprocess.check_output(['git', 'show', 'origin/content/audit-corrections-q001-q049:content/questions.json'], cwd=ROOT))
    assert [(q['id'], q['number'], q['publish_date']) for q in original] == [(q['id'], q['number'], q['publish_date']) for q in audited]
    # q001's format correction was held only because of a now-fixed test fixture.
    first = audited[0]
    first['why_wrong'] = dict(re.findall(r'^([A-E]) is wrong:\s*(.+)$', first['explanation'], re.M))
    assert set(first['why_wrong']) == set('ABCDE') - {first['answer']}
    rule_corrections = {
        'q042': 'A superintendent or above responsible for the station may extend detention without charge for an indictable (including either-way) offence to 36 hours from the relevant time, after the second review and within 24 hours.',
        'q044': 'A claimant may apply for summary judgment once the defendant files an acknowledgment of service or defence; it is given against a party with no real prospect of success and no other compelling reason for trial.',
    }
    for q in audited:
        if q['id'] in rule_corrections:
            q['key_rule'] = rule_corrections[q['id']]
    draft_questions = sorted([q for path in sorted((source / 'questions').glob('*.json')) for q in json.loads(path.read_text())], key=lambda q: q['id'])
    old = {q['id']: q for q in json.loads((ROOT / 'content/library.json').read_text())} if (ROOT / 'content/library.json').exists() else {}
    next_number = max([q['library_number'] for q in old.values()] + [0])
    library = []
    for raw in draft_questions:
        q = {k: v for k, v in raw.items() if k != '_draft'}
        if q['id'] in old:
            number = old[q['id']]['library_number']
        else:
            next_number += 1; number = next_number
        q.update(number=-number, library_number=number, publish_date=None)
        if q['id'] == 'lib-sa-003':
            q['explanation'] = q['explanation'].replace("the charity's receipt and indemnity", "the charity's receipt and confirmation of any indemnity provided")
            q['last_reviewed'] = '2026-10-17'
        if q['id'] == 'lib-ls-016':
            q['scenario'] += ' The introduction is not made with a view to any transaction relating to a contract of insurance.'
            q['explanation'] += ' Article 33(d) also requires the non-insurance condition (or the separate article 33B route); the facts expressly satisfy the non-insurance condition.'
            q['last_reviewed'] = '2026-10-17'
        library.append(q)
    for q in audited + library:
        item = metadata[q['id']]
        q['session'] = item['session']
        q['context_subject'] = {'Accounts (Wills)': 'Wills & Administration of Estates', 'Accounts (Property)': 'Property Practice'}.get(item['group'], item['group'])
        assert q['session'].startswith(q['flk'])
    bank = audited + library
    impact_path = ROOT / 'docs/library-email-impact.json'
    if not impact_path.exists():
        historical = json.loads(subprocess.check_output(['git','show','8d21f41:content/questions.json'],cwd=ROOT))
        relevant = ['flk','scenario','stem','options','answer','explanation','key_rule','authority','verified_source_url','title']
        impact = [{'id':after['id'],'publish_date':after['publish_date'],'fields':[k for k in relevant if before.get(k)!=after.get(k)]} for before,after in zip(historical,audited)]
        write(impact_path,[entry for entry in impact if entry['fields']])
    data = {'version': 1, 'releases': [], 'mocks': []}
    for q in bank:
        data['releases'].append({'id': q['id'], 'available_from': '2026-10-17', 'question_hash': p.question_hash(q), 'approved': False})
    for paper in ['FLK1', 'FLK2']:
        sessions = [composition['mocks'][f'{paper}-S{i}'] for i in [1, 2]]
        ids = set(sum(sessions, []))
        data['mocks'].append({'id': paper.lower() + '-january-2027', 'title': paper + ' mock · January 2027', 'paper': paper,
            'law_cutoff': '2026-09-11', 'source_url': 'https://sqe.sra.org.uk/news-item/2026/09/10/important-changes-to-sqe1-for-january-2027-onwards',
            'sessions': sessions, 'question_hashes': {q['id']: p.question_hash(q) for q in bank if q['id'] in ids}, 'approved': False})
    write(ROOT / 'content/questions.json', audited)
    write(ROOT / 'content/library.json', library)
    write(ROOT / 'content/practice.json', data)
    pages = copy.deepcopy(json.loads((ROOT / 'content/pages.json').read_text()))['pages']
    standards = pages['editorial-standards']
    standards['intro'] = 'SQE Daily is a free library of SQE1 practice questions, with one featured question each day, mini tests and full mock papers. This page explains how the questions are put together, what the dates on the site mean, and how to tell us about a mistake.'
    for section in standards['sections']:
        section['body'] = section['body'].replace('before it is scheduled for publication.', 'before it is published.').replace('Each question shows the date it was published.', 'Each question shows the date it was first published on the site.')
        section['body'] = section['body'].replace('A “Checked against primary source” date', 'A source-check date')
        if section['heading'] == 'The law at a point in time':
            section['body'] += ' Each mock paper states the law as at the SRA\'s examinable law cut-off date for the sitting it targets: for January 2027, 11 September 2026.'
    standards['sections'].insert(3, {'heading': 'Mini tests and mock papers', 'body': "Our mini tests and mock papers are our own practice design. Each full mock follows the format the SRA has published for the sitting it targets: 170 questions in two sessions of 85, each lasting 2 hours 33 minutes, with the SRA's subject groupings for each session. The mix of subjects and the difficulty labels are our editorial choices. They are not the SRA's question selection, and they do not reproduce the real assessment's difficulty. A score on our tests does not predict an SQE1 result."})
    hub = pages['sqe1-practice-questions']
    hub['intro'] = 'SQE Daily has a free library of original SQE1 practice questions, each with a worked answer, the rule to remember and a link to the source behind the answer. One question is featured each day. This page brings the questions together by paper and subject, so you can practise the areas you need most.'
    proposals = {name: pages[name] for name in ['editorial-standards', 'sqe1-practice-questions']}
    for entry in proposals.values():
        entry['approved'] = False; entry.pop('approved_hash', None)
    write(ROOT / 'content/library-editorial-proposals.json', proposals)
    print(f'Imported {len(library)} unapproved library drafts; no approvals recorded.')


if __name__ == '__main__':
    main()
