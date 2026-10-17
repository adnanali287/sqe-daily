# Integrated library QA, 17 October 2026

The fully populated preview uses temporary approvals in a separate folder. The
repository retains 368 unapproved release entries, two unapproved mock entries
and unapproved editorial proposals. Normal generation still publishes only the
daily-date-eligible questions. No production deployment was performed.

## Automated

- Existing strict site, date and 245 daily-answer tests.
- Practice release/withdrawal/fingerprint checks and fake-clock test engine tests.
- New real-batch checks: 398 HTML pages, independent library numbering, locked
  URLs after title corrections, unchanged daily dates/answers, no draft review
  fields in public data, two disjoint full mocks and contextual Accounts checks.
- New pool checks: 181 FLK1, 187 FLK2; session pools 91/90/93/94;
  combined Legal Systems 26; cross-paper Ethics 30; Accounts 10. Insufficient
  pools reject a 20-question attempt rather than duplicating questions.
- Weighted coverage and recent-history preference; withdrawn/changed mock
  manifests cannot resume from an older saved attempt.
- Both the normal package and full preview pass the existing HTML rules. PR
  checks also build and validate a full isolated preview, never a deployment.

## Browser

1440px desktop and 390px mobile checks, using the actual integrated question
bank and mock manifests (no synthetic questions):

- Full mock selection for each paper; law cutoff and official source shown.
- FLK1 timed session starts at 2:33:00 and survives reload/resume. Long expiry
  and break boundaries are tested with fake clocks, not hours of browser waiting.
- FLK2 untimed: flagged/answered question, first-session submission, break,
  second session beginning at question 86 with Previous disabled, final results
  and 170 worked-answer review entries.
- Cross-paper Ethics 20-question test, save/reload/resume and results.
- Session-pool selection and counts; independent pool/unit tests cover all mixes.
- Filtered Accounts library, an L-numbered permanent question, correct-answer
  reveal, source and related-question navigation.
- Homepage still shows daily question 05 on 17 October, not question 49 or a
  library-only question. No horizontal overflow on inspected mobile views.

Screenshots are in screenshots/integration/. The first pass exposed duplicate
"Paper" labels on full mock setup; the second label now says "Mock". A later
copy pass removes misleading "fresh/unseen" and blanket primary-source claims
when the library is released. No layout or palette redesign was made.

## Limits

No real newsletter signup or subscriber email was sent. No browser test forces
storage denial; corruption and source corrections are covered by unit tests.
There has been no qualified legal review of the full bank. Hark must reconcile
the 17 campaign-relevant corrections and retain final cutoff/content sign-off.
See library-review-findings.md and library-approval-batch.md before approval.
