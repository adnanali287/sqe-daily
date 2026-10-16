# Proposed editorial copy changes (DRAFT, not applied, 16 Oct 2026)

These go live only when Codex ships the library and tests, so the copy never describes features that don't exist yet.

## pages.editorial-standards
1. **intro.** Old: "SQE Daily publishes one free SQE1 practice question a day. This page explains how those questions are put together, what the dates on the site mean, and how to tell us about a mistake."
   New: "SQE Daily is a free library of SQE1 practice questions, with one featured question each day, mini tests and full mock papers. This page explains how the questions are put together, what the dates on the site mean, and how to tell us about a mistake."
2. **Original questions, last sentence.** Old: "...checked against the source it relies on before it is scheduled for publication."
   New: "...checked against the source it relies on before it is published."
3. **What the dates mean, first sentence.** Old: "Each question shows the date it was published."
   New: "Each question shows the date it was first published on the site." (This depends on what Codex shows for library questions.)
4. **New section after "What our checks are, and are not": "Mini tests and mock papers".**
   "Our mini tests and mock papers are our own practice design. Each full mock follows the format the SRA has published for the sitting it targets: 170 questions in two sessions of 85, each lasting 2 hours 33 minutes, with the SRA's subject groupings for each session. The mix of subjects and the difficulty labels are our editorial choices. They are not the SRA's question selection, and they do not reproduce the real assessment's difficulty. A score on our tests does not predict an SQE1 result."
5. **The law at a point in time.** Append:
   "Each mock paper states the law as at the SRA's examinable law cut-off date for the sitting it targets: for January 2027, 11 September 2026."

## pages.sqe1-practice-questions
6. **intro.** Old: "SQE Daily publishes one original SQE1 practice question every day, with a worked answer..."
   New: "SQE Daily has a free library of original SQE1 practice questions, each with a worked answer, the rule to remember and a link to the source behind the answer. One question is featured each day."
   The rest of the sentence is unchanged.

## Flag for Codex (frontend templates, not Hark's to edit)
- scripts/templates/home.html: "A fresh SQE1 question every day" and "One free, original SQE1 question a day" are acceptable for the daily featured question. "Fresh" could be read as previously unseen once the library is open, so Codex may want "Today's featured question".

## Emails
- All 45 scheduled emails, and the 3 sent ones, were checked: none says exclusive, unseen, brand-new or first time. The two "fresh" hits are legal content (a "fresh offer" and "fresh consideration").
- The confirmation and welcome Buttondown templates (unchanged, Free plan) say "one original SQE1 practice question every day". This stays true for the daily featured email.
- No email change is needed.
