# Library integration review, 17 October 2026

## Recommendation

The technical preview is ready for owner review, not publication. There are 368
questions (49 existing plus 319 new), two distinct 170-question mock lists and
398 generated HTML pages in the full local preview. No real release, mock or
editorial approval has been recorded. This is not a qualified legal review or a
claim that all 319 answers have been independently re-verified by Codex.

## Content findings

1. **lib-sa-003: correction prepared.** The explanation made a charity indemnity
   sound mandatory. The SRA permits a charity without one. The import now says to
   retain confirmation of any indemnity provided, rather than requiring one.
   The answer stays A. [SRA prescribed circumstances](https://www.sra.org.uk/solicitors/standards-regulations/withdraw-client-money/),
   conditions 4(b) and additional guidance, checked 17 October.
2. **lib-ls-016: assumption made explicit.** Article 33(d) has an insurance
   condition. The original scenario left non-insurance unstated. The import adds
   that the introduction is not made with a view to an insurance transaction and
   explains the condition. The answer stays A. Checked the official
   [article 33 XML](https://www.legislation.gov.uk/uksi/2001/544/article/33/data.xml)
   on 17 October; no reliance on an unavailable web rendering.
3. **Guidance is not a judgment.** Library-only answer panels now say "source",
   not "primary source". Galbraith's linked law report is a primary judgment
   hosted by a third party; Turnbull's linked Compendium is official guidance,
   not the original judgment. Both links loaded and the relevant rules matched
   the proposed answers. No unsupported claim of official assessment equivalence.
4. **Review notes remain review notes.** Inspected the 201 non-empty uncertainty
   notes and closely read 12 targeted scenarios/answers: blp-022/025,
   crp-016/017, dr-017, eth-023, lan-015, ls-016/021, sa-003, tru-007 and wil-002
   (all have the `lib-` prefix). Many notes disclose unfetched supporting points,
   later judgments restating older law, assumptions, or future amendments said
   not to affect the answer. That is not independent clearance of every point.
   A qualified reviewer would improve confidence before launch.
5. **Law cutoff needs care.** Current Law Commission material still describes
   wills reform as proposed and describes the existing common-law capacity
   distinction, supporting wil-002 rather than a claim that the draft Bill is
   law. HMRC's updated valuation manual still discusses the investment-business
   exclusion under IHTA s.105(3), supporting the distinction tested in wil-020.
   These are corroborating checks, not a complete audit of every commencement
   provision as at 11 September 2026. Hark should retain a final cutoff sign-off.

The 49 existing answers, IDs, daily numbers and daily dates are unchanged. The
PR #7 corrections are incorporated into this draft, including q006/q035's FLK2
allocation and q001's why_wrong format correction. URLs remain locked.

## Official format verification

Read the SRA's [10 September change notice](https://sqe.sra.org.uk/news-item/2026/09/10/important-changes-to-sqe1-for-january-2027-onwards),
[Annex 4](https://sqe.sra.org.uk/assessments/sqe1-assessments/sqe1-specification/sqe1-annex4)
and [booking dates](https://sqe.sra.org.uk/booking/assessment-dates-locations/booking-windows).
The two-session size, timing, contextual Accounts groupings and January cutoff
match the implementation. Ethics can pervade all sessions. Editorial allocations
and difficulty targets are practice choices, not official statistical calibration.

Additional source evidence: [Law Commission wills project](https://lawcom.gov.uk/project/wills/),
[Clitheroe judgment](https://caselaw.nationalarchives.gov.uk/ewhc/ch/2021/1102),
[HMRC SVM111150](https://www.gov.uk/hmrc-internal-manuals/shares-and-assets-valuation-manual/svm111150),
[Compendium, section 15](https://www.judiciary.uk/wp-content/uploads/2022/06/Crown-Court-Compendium-Part-I-Oct-25-Mar-26-update.pdf).

## Email dependency

Do not confirm "no email changes needed" yet. The earlier audit concerned
exclusivity wording, not the later content corrections. Seventeen existing
questions change a campaign-relevant field. Hark must compare those campaigns
and the following day's worked answer with the final bank. In particular q006
and q035 change paper, and q010/q024/q038 change scenario. See the exact table in
library-approval-batch.md. Codex has not accessed or modified Buttondown, sent
emails, changed recipients or altered send dates in this integration.

## Owner decisions, one batch

- Accept the two new question corrections and the existing-bank corrections.
- Approve the proposed library releases and two exact mock lists after Hark's
  cutoff/content sign-off, accepting the disclosed source-review limitations or
  commissioning qualified review first.
- Approve the editorial proposals, functional copy and screenshot set.
- Authorise launch separately. Refresh release dates/fingerprints to the real
  first publication day; do not backdate a later launch to this preview date.

No PR has been merged and no production content approval has been recorded.

## Final Hark review: follow-up corrections

Hark confirmed the two library corrections and reported that the 319 drafts and
both mock compositions match its intended January-cutoff bank. Its final review
also found two shortened daily key rules needing repair. Both are now prepared
in the draft, with the same IDs, dates, answers and URLs:

- q042 restores "or above" to the authorising officer's rank. Verified against
  [PACE s.42](https://www.legislation.gov.uk/ukpga/1984/60/section/42/data.xml).
- q044 restores the claimant's application timing and removes the ambiguous
  "that party". Verified against [CPR 24.3 and 24.4](https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part24).

Their release hashes and all affected mock hashes are refreshed; every new
approval remains false. Regression checks preserve these two important details.

Hark reports that 14 scheduled campaign bodies need updates, rather than 17:
the earlier list counted question fields, not campaign bodies. Its campaign
inspection is not independently repeated by Codex. See
library-email-reconciliation.md for the exact plan and deployment timing rule.
