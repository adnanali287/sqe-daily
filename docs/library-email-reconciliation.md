# Proposed email reconciliation, final Hark review

**Unapproved; not applied.** Hark reports inspecting all 45 scheduled campaigns:
14 need body changes relative to PR #10; 31 do not. Subjects, recipients and
send dates remain unchanged. Codex has not accessed Buttondown to independently
repeat that campaign inspection or to apply any edits.

The 17-entry question-field impact list remains a conservative audit trail, not
a count of campaigns. q013's source URL and q026's explanation do not appear in
the campaigns according to Hark. Key-rule changes appear in the next email.

| Email | Send date, 07:00 Europe/London | Section | Replacement source |
|---|---|---|---|
| #6 | 2026-10-18 | Header | Question 6 · Ethics & Professional Conduct · FLK2 |
| #10 | 2026-10-22 | Today's scenario | q010 house-purchase context |
| #17 | 2026-10-29 | Yesterday's rule | q016 key_rule |
| #19 | 2026-10-31 | Yesterday's rule | q018 key_rule |
| #20 | 2026-11-01 | Yesterday's rule | q019 key_rule |
| #23 | 2026-11-04 | Yesterday's rule | q022 key_rule |
| #24 | 2026-11-05 | Today's scenario | q024 freehold-premises context |
| #30 | 2026-11-11 | Yesterday's rule | q029 key_rule |
| #35 | 2026-11-16 | Header and yesterday's rule | Question 35 · Ethics & Professional Conduct · FLK2; q034 key_rule |
| #37 | 2026-11-18 | Yesterday's rule | q036 key_rule |
| #38 | 2026-11-19 | Today's scenario | q038 estates context |
| #41 | 2026-11-22 | Yesterday's rule | q040 key_rule |
| #43 | 2026-11-24 | Yesterday's rule | Corrected q042 key_rule |
| #45 | 2026-11-26 | Yesterday's rule | Corrected q044 key_rule |

## Deployment order, subject to separate owner approval

1. Obtain approval for the final site content, copy, screenshots and launch.
2. Refresh release dates and fingerprints to the actual launch day. Publish the
   approved site and verify the live pages against that exact bank revision.
3. Only then may Hark apply separately approved edits to campaigns that are
   **still scheduled and unsent**, using the deployed bank as the source of truth.
4. Preserve send times, recipients, subjects and scheduling state. Do not resend
   or revise an already-sent campaign. If deployment misses a campaign's send
   time, leave that campaign matching the version live at its original send.
5. Recheck each changed body, its schedule and duplicate status; report results.

In particular, #6 stays FLK1 unless the FLK2 site correction is live before
2026-10-18 07:00 Europe/London. No promise of a last-minute deployment is made.

The full replacement bodies are held by Hark according to its report; they have
not been supplied to or independently compared by Codex. The final q042/q044
wording is in content/questions.json and protected by regression tests.
