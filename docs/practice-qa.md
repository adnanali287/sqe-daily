# Practice feature verification, 17 October 2026

## Scope

Technical foundation only. No content approvals, early releases, newsletter
schedules, domain settings or production deployments were changed. The real
practice configuration is empty. Hark's draft PRs #7 and #8 remain separate.

## Automated checks

- Strict site checks: links, fragments, metadata, structured data, RSS, sitemap,
  fixed URLs, reproducible generation, editorial approvals and full-bank build.
- Practice checks: exact-content release approval, corrections withdrawing an
  early release, unchanged daily dates, library-only questions, 49-question
  library packaging and 170-question mock readiness/subject coverage.
- Test engine: sampling, scoring, corrupt/corrected saves, absolute deadlines,
  session locking, 60-minute break, closed-tab catch-up and session shuffling.
- Existing daily-date tests and all 245 answer-marker tests.
- HTML validation of the deployment package.

## Browser checks

An isolated 49-question preview uses temporary approvals, never production data
changes. Desktop 1440px and mobile 390px screenshots are in screenshots/practice/.
Checked setup, running questions and results; no horizontal overflow. Native
radio Space/arrow keys selected an answer and produced the expected score.
Tested 10- and 20-question attempts, flags, navigation, save/reload/resume,
submission warnings, subject pools too small to start, and unavailable full
mocks. A missing mock-data response produces an error; Try again recovers after
the response is restored.

A separate disposable synthetic fixture exercised both 85-question sessions,
the locked first session, break and final 170-question results. It is not a real
mock and is not committed or deployed. Long timer boundaries use fake-clock unit
tests, not hours of browser waiting. Storage-denied behaviour is implemented but
has not been forced in the browser. Cross-tab protection is implemented; only
shared saved-attempt visibility has been checked interactively.

## Visual review

The first pass exposed an oversized active-page introduction, question focus
skipping the scenario and a misleading heading for completed saves. These were
fixed. The second pass added a sticky-header Review action so mobile users need
not scroll past the question to submit. Final captures show the revised layout.

## Before launch

Owner: sign off screenshots and the small local-storage privacy addition.
Codex/Hark: reconcile the content audit and new draft bank, allocate library
display identifiers without consuming daily numbers, import only approved copy,
validate contextual session composition, then record exact release/mock
approvals. Run the complete suite and live smoke checks after the approved merge.
No full mock should be advertised as available before that work is complete.
