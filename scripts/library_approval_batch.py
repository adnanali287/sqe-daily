"""Generate a review inventory, fingerprints and exact proposed copy; never approve."""
import json
from pathlib import Path
import generate as g
import practice_content as p

bank = g.load_bank()
practice = p.read(g.ROOT)
by_id = {q['id']: q for q in bank}
lines = ['# Library and mock approval batch', '', 'Review only. No approval is recorded by this document. Do not merge or publish yet.', '',
    'Fingerprints cover exact imported content and composition. Planned release dates must be refreshed to the real launch date before final approval if launch is later than 17 October 2026.', '',
    '## Library releases', '', '| ID | Display | Subject | Exact release fingerprint |', '|---|---|---|---|']
for e in practice['releases']:
    q = by_id[e['id']]
    lines.append(f'| {q["id"]} | {g.question_number(q)} | {q["subject"]} | `{p.fingerprint(e)}` |')
lines += ['', 'Exact question text is in content/questions.json (existing daily bank) and content/library.json (new library-only bank). The latter never consumes daily issue numbers. Original reviewer notes and source quotes remain in drafts/library-2027-01; those review fields are never packaged.', '', '## Mock compositions', '']
for e in practice['mocks']:
    lines += [f'### {e["title"]}', '', f'Fingerprint: `{p.fingerprint(e)}`', '', f'Law cutoff: {e["law_cutoff"]}. Source: {e["source_url"]}', '']
    for n, session in enumerate(e['sessions'],1):
        lines += [f'Session {n} (85 IDs):', '', ', '.join(session), '']
lines += ['## Exact editorial proposals', '', 'The following proposed entries replace only their corresponding approved entries after explicit sign-off. They are not loaded automatically.', '']
proposals = json.loads((g.ROOT/'content/library-editorial-proposals.json').read_text())
for name, entry in proposals.items():
    lines += [f'### pages.{name}', '', f'Fingerprint: `{g.content_hash(entry,g.APPROVAL_FIELDS)}`', '', '```json', json.dumps(entry,ensure_ascii=False,indent=2), '```', '']
lines += ['## Additional functional copy for approval', '',
    '- Homepage: "A fresh SQE1 question every day" becomes "One featured SQE1 question every day" once early library releases exist.',
    '- Homepage answer footer: "A fresh question tomorrow." becomes "Another featured question tomorrow."',
    '- Homepage source promise: "Every question is original and checked against primary sources: legislation and case law." becomes "Every question is original and checked against its linked source."',
    '- Library-only answers: "Source · opens in a new tab", "Checked against source on [date]", and "A little more practice done." No blanket primary-source claim for guidance-based questions.',
    '- About: "Each question is written for SQE Daily and checked against primary sources: legislation and case law." becomes "Each question is written for SQE Daily and checked against its linked source." when the library is released.',
    '- Privacy: recent practice history is added to the device-only storage disclosure; clearing browser site data removes attempts and history.', '',
    '## Scheduled email reconciliation', '', 'Do not change send dates or send anything. The content audit changes the fields below; Hark must compare the affected campaigns and the following day\'s worked-answer section before confirming that no copy updates are needed.', '', '| Question | Daily date (unchanged) | Changed campaign-relevant fields |', '|---|---|---|']
for entry in json.loads((g.ROOT/'docs/library-email-impact.json').read_text()):
    lines.append(f'| {entry["id"]} | {entry["publish_date"]} | {", ".join(entry["fields"])} |')
(g.ROOT/'docs/library-approval-batch.md').write_text('\n'.join(lines)+'\n')
print('Wrote review batch; no approvals recorded.')
