# SQE Daily: 90-day content and outreach backlog

Covers roughly 19 October 2026 to 17 January 2027, the run-up to the January 2027 SQE1 (FLK1 11–15 January, FLK2 18–22 January; booking closes 23 November 2026, per the SRA). Rows are ordered by priority. **Owner** means you. **Hark** means the question-bank writer. **Claude** means a coding session.

Every piece of new copy goes through the approval batch (`scripts/approval_batch.py`, then `--approve` after your approval in chat). Nothing is posted off-site, and no profile is created, without your explicit go-ahead. There are no paid links, link exchanges or mass posting.

## Priority 0: this week (blocking)

| # | Item | Who | Why |
|---|---|---|---|
| 0.1 | **Extend the question bank past 9 November 2026.** The last scheduled question is 9 Nov, so after that the homepage shows "Latest question" and no new pages are published. Keep the bank at least 30 days ahead. | Hark | Daily publishing is the site's freshness signal and the reason to come back. |
| 0.2 | Review and approve (or edit) the editorial approval batch. | Owner, then Claude records it | 23 entries of written copy are built but unpublished. |
| 0.3 | Merge PR #1, then the follow-up PR, after sign-off. | Owner | Nothing in either PR is live until merged. |
| 0.4 | Search Console: submit `https://sqedaily.co.uk/sitemap.xml`; use URL Inspection to request indexing of `/`, `/sqe1-exam-dates/` and `/sqe1-practice-questions/` once live. | Owner | No Search Console access from this environment. |
| 0.5 | Bing Webmaster Tools: import the site from Search Console. | Owner | Second search engine at no cost. |

## Priority 1: weeks 1–4 (to 16 November)

| # | Item | Who | Notes |
|---|---|---|---|
| 1.1 | Add `tags` to all 28 questions, using a shared, consistent vocabulary. | Hark | Related questions then match on topic, not just subject or paper. |
| 1.2 | Add `why_wrong` to the live questions first, then the scheduled ones. | Hark | Clearer answers; same-page corrections are picked up automatically. |
| 1.3 | Set `last_reviewed` only when a question is actually re-checked against its source. | Hark | Never estimate a date. |
| 1.4 | Guide: **"Booking SQE1 for January 2027: a checklist"**. Facts from the SRA booking pages, published before 23 November. | Claude drafts, Owner approves | Time-sensitive search demand. |
| 1.5 | Outreach drafts 1–3 (see `docs/outreach-drafts.md`): you review, personalise and send them from hello@sqedaily.co.uk. | Owner | Resource-list inclusion is the most natural link for a free tool. |
| 1.6 | Ask the r/LawUK moderators for permission before any post (draft 4). | Owner | Self-promotion rules; never post without permission. |

## Priority 2: weeks 5–8 (17 November to 14 December)

| # | Item | Who | Notes |
|---|---|---|---|
| 2.1 | Guide: **"Solicitors accounts questions: a method for the numbers"**. Primary source: the SRA Accounts Rules. | Claude drafts, Owner approves | Commonly feared topic; links to the Solicitors Accounts subject page. |
| 2.2 | Guide: **"Ethics in SQE1: how it appears across both papers"**. Sources: the SRA Principles and Code of Conduct. | Claude drafts, Owner approves | Ethics is assessed pervasively, so it suits a cross-linking guide. |
| 2.3 | Law society outreach using the template (draft 5), to university law societies you choose. Ideally before the end of term. | Owner | One personalised email per society; no bulk sending. |
| 2.4 | Check that every subject page with a live question has an approved introduction (new subjects appear as the bank grows). | Claude, Owner approves | New subjects otherwise show the plain archive. |
| 2.5 | First monthly measurement entry in `docs/measurement-baseline.md`. | Owner exports, Claude records | See that file for the exact exports. |

## Priority 3: weeks 9–13 (15 December to 17 January)

| # | Item | Who | Notes |
|---|---|---|---|
| 3.1 | Guide: **"The final week before SQE1"**: practical, non-legal preparation, sourced to the SRA's assessment-day pages where factual. | Claude drafts, Owner approves | Publish in late December. |
| 3.2 | Update `/sqe1-exam-dates/` when the SRA publishes July 2027 booking and results dates (add them to the July 2027 sitting, then re-approve). | Claude, Owner approves | Edits withdraw approval automatically until re-approved. |
| 3.3 | Guide: **"Understanding your SQE1 result"**. Source: the SRA results pages. Publish before results on 9 March 2027. | Claude drafts, Owner approves | Plan now; publish in February. |
| 3.4 | Follow up once on outreach that got no reply after 3 weeks (one polite follow-up only). | Owner | |
| 3.5 | Second monthly measurement entry; compare with the baseline. | Owner, Claude | |

## Deferred or parked (not in the 90 days unless you decide otherwise)

- IndexNow ping and the embeddable question widget (deferred by decision).
- Social profiles: none are created without your approval. Once created, add them to `Organization.sameAs`.
- Cloudflare Web Analytics: off until you supply the public beacon token.
- Per-question social images.
