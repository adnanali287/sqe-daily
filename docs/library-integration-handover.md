# Integration handover for Codex: library, mini tests and mocks (draft, 16 Oct 2026)

Hark owns the content. Codex owns the schema, test engine, frontend, publishing and tests. Nothing in this PR changes the live schema, the generator, the tests or `content/questions.json`.

## What is in this PR
- `drafts/library-2027-01/questions/<code>.json`: 319 new draft questions, ids `lib-<code>-NNN`.
  - Codes: blp, dr, ls, con, tor, sys, wil, sa, tru, lan, ppl, crl, crp, eth.
  - Each object uses the **current question fields** (subject, flk, difficulty, title, scenario, stem, options, answer, explanation, why_wrong, key_rule, authority, verified_source_url, tags, last_reviewed).
  - Each also has a non-schema `_draft` block: session, spec_topic, context_subject, source_type, source_quote, status, hold_reason, uncertainty.
  - There is **no `number` and no `publish_date`**: library questions have no daily date.
  - The explanations contain no "X is wrong" lines; `why_wrong` carries them.
- `drafts/library-2027-01/composition.json`:
  - per-question session/group metadata for all 368 questions (49 existing plus 319 new);
  - the two mock lists (`mocks.FLK1-S1`, etc.);
  - the allocation table.
- `docs/mock-blueprint.md`, `docs/mock-coverage-and-composition.md`, `docs/mini-test-pools.md`, `docs/library-editorial-proposals.md`.

All of this is unapproved draft content. Nothing should render on the site until the owner approves it.

## Facts the engine should encode (verified on SRA pages, 16 Oct 2026)
- 170 questions per FLK, two sessions of 85, each 153 minutes.
- A 60-minute scheduled break after Session 1; the SRA asks candidates to return within 50 minutes.
- Session subject groupings:
  - FLK1 S1: BLP, DR, Legal Services.
  - FLK1 S2: Tort, Contract, Legal Systems.
  - FLK2 S1: Wills, Accounts (Wills), Trusts, Land.
  - FLK2 S2: Property, Accounts (Property), Criminal Liability, Criminal Law and Practice.
  - Ethics can appear in any session.
- Order is randomised within a session.
- Target sitting: January 2027. Law cutoff: 11 Sep 2026.

## Schema decisions for Codex (unresolved; Hark has not decided them)
1. **Library ids and routes.** Do library-only questions get ids and URLs?
   - Options: keep `lib-*` ids with new `/library/...` or `/q/...` routes; or assign `number`s continuing from 50.
   - Daily numbers run to #49, and future daily emails use the next numbers. Reusing 50+ for library questions would collide with future daily issues unless numbering is decoupled. Hark recommends a separate library id space, with daily featuring as a pointer.
2. **Availability vs featuring.** Add a field such as `library_available_from` (or a global flag) separate from `publish_date`. The existing q001–q049 `publish_date` values must stay the daily featured dates, unchanged, and locked routes must not move.
3. **Session metadata.** The SRA session depends on context, not on the site subject: Ethics and Solicitors Accounts follow their context. Proposed fields: `session` ("FLK1-S1" and so on) and `context_subject`. Values for all 368 questions are in composition.json.
4. **Mock membership.** Either a separate `mocks.json` (recommended: id lists per session, in the composition.json shape) or a `mocks` array on each question.
5. **Draft-only fields.** `_draft.source_quote`, `uncertainty` and `status` are review aids. Decide whether `source_quote` is stored, never rendered, or dropped at import.
6. **Approval gating for questions.** Questions currently have no approval fingerprint (pages.json does). Library questions need an `approved` gate plus fingerprint like pages.json, so that drafts in the repo never render. Hark will never run `--approve` on the owner's behalf.
7. **Subject labels.** The site uses "Criminal Law" and "Criminal Practice". The SRA's names are "Criminal Liability" and "Criminal Law and Practice". Hark's content uses the site labels; the mapping is in composition.json.
8. **Difficulty.** Editorial labels only. Never display them as predicted exam difficulty.

## Test/fixture issue found
- `scripts/test_site.py` (around line 187) assumes the first published question has never been modified. Adding `why_wrong` to q001 (an approved-in-principle format fix) makes `content_test` fail.
- PR #7 therefore leaves q001 out. Please make the fixture independent of q001's lock state; Hark will then add q001's `why_wrong`.

## Checks run by Hark
- Every draft file: valid JSON, all keys present, five options, an answer letter, exactly 4 `why_wrong` letters, unique ids, session matches flk, https source, no future `last_reviewed`, stems end in "?", and no AI or tool wording. Result: 319 of 319 pass.
- Near-duplicate check (title and key-rule shingles, Jaccard > 0.3) across all 368 questions: no pairs found.
- Mock lists: 4 × 85, with no repeats within or across mocks.
- PR #7 (`content/questions.json` corrections): `generate.py --package`, `test_site.py` with STRICT_APPROVALS=1, `test_dates.cjs` and `test_answers.cjs` all pass locally. html-validate was not run locally; it runs in CI.
- None of these checks is a legal review.
