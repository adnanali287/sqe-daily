# Content handover for Hark

Keep `content/questions.json` in its existing schema. Existing `publish_date`
continues to mean daily-feature/email date; do not change it for library access.
New library/mock-only questions may use `publish_date: null`: they have no daily
feature or email assignment and become available only through an approved library
release. This extension is implemented on the feature branch, not main yet; keep
such questions in draft files until integration. Never change the existing 49 dates.
Do not invent additional fields in the shared bank.

Codex owns `content/practice.json` and validation. It has `version: 1`, `releases`
and `mocks` arrays. Each entry uses the existing `approved` + `approved_hash`
fingerprint procedure. No entry is approved by this implementation.

A release contains `id` (question ID), `available_from` (real first library date),
`question_hash` (SHA256 of that exact question, ignoring only route/modified), plus
approval fields. Changing the question withdraws its early-release permission.
Without a valid release, the original daily date controls availability.

A full mock contains `id` (lowercase slug), `title`, `paper` (`FLK1` or `FLK2`),
`law_cutoff`, `source_url` (official assessment-format/specification link), and
`sessions`: two arrays of exactly 85 distinct question IDs. It also contains
`question_hashes`: ID-to-question-fingerprint mapping, plus approval fields.
No ID may repeat across sessions. All questions must be available, from the same
paper and unchanged since approval. Hark must verify session subject allocations,
coverage and legal cutoff before asking the owner to approve the manifest.
Only approved, complete manifests are offered by the test engine.
Question order is shuffled within each session when an attempt starts, then
preserved in its saved state. Session membership never changes.

The validator checks that each session contains every required main subject and
no subjects from the other session (ethics may appear in either). This is a basic
coverage floor, not proof of appropriate weighting or legal quality. Accounts
questions need Hark's contextual review because the subject appears in both FLK2
sessions. Never infer blueprint quality from a passing structural check alone.

Mini tests sample 10 or 20 distinct available questions from the selected paper
and optional subject. Pools below the requested size cannot start. Mini tests do
not claim official weighting or difficulty equivalence.

For new content please deliver current-schema question drafts and a separate
allocation table: mock ID, paper, session, position, question ID, topic and review
notes. Codex will integrate this without making Hark edit application files.

After owner approval, record a practice entry with:
`python3 scripts/generate.py --approve-practice releases.q005 --expect HASH`
or `--approve-practice mocks.flk1-a --expect HASH`. Fingerprints cover the whole
entry except approval fields. Obtain the exact fingerprint before asking approval.

Do not change Buttondown schedules. Early library availability does not mean an
email was sent early or that a question is today's featured question.

## Hark's draft PRs checked on 17 October

PR #7 contains the existing-bank content audit; PR #8 contains 319 separate
unapproved drafts and a composition table. Neither is merged by this feature.
The `lib-*` IDs can remain stable. Integration still needs a display-number
allocation that does not consume future daily issue numbers, and an explicit
mapping of accounts/ethics contexts from the composition table. Draft-only
review quotes and uncertainties must not enter the public question payload.
Do not import and approve the batch just because structural checks pass.
