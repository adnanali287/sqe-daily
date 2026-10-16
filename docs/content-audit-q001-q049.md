# SQE Daily bank audit: q001 to q049

- **Bank:** content/questions.json at git main 8d21f41 (HEAD 8d21f416f359eda1498bd691e11cbbc84a9e42a3). Read only; no repo file was edited.
- **Standard:** the internal writing brief (January 2027 sitting; law cutoff 11 September 2026).
- **Audit date:** 16 October 2026 (Europe/London). Every verified_source_url was fetched today: legislation.gov.uk, justice.gov.uk and the Law Society PDF by direct download; SRA pages and the Woollin opinion by web fetch; BAILII judgments after clearing its bot check. The 'changes to legislation' boxes were checked on every legislation.gov.uk page. Where there were unapplied changes (MA 1967 s.2, TA 1968 s.9, PACE ss.42 and 58, CJPOA s.34, CA 2006 ss.168, 177 and 190, LTA 1954 s.25, LRR r.131), none touches the provision tested.
- **Machine-readable version:** the companion audit data file (not in the repo). It holds the full why_wrong objects proposed for q001 to q028.

## Counts
- ready: 13
- needs correction: 36
  - 19 format only: add why_wrong (and last_reviewed where it is missing), built word for word from the existing 'X is wrong' lines. Those lines already cover all four wrong letters. These questions are legally sound. Questions: q001, q002, q003, q004, q005, q007, q008, q009, q011, q012, q014, q015, q017, q020, q021, q023, q025, q027, q028.
  - 17 with a substantive or metadata fix: q006, q010, q013, q016, q018, q019, q022, q024, q026, q029, q034, q035, q036, q038, q040, q042, q044.
- hold: 0

No question has a wrong answer, a second defensible answer, or law that changed by 11 September 2026. No question needs a hold.

**Rendering note.** scripts/generate.py (explanation_html) drops 'X is wrong' lines from the explanation whenever why_wrong exists. So adding why_wrong to q001 to q028 is enough, and their explanations need not be edited. q029 to q049 already have why_wrong; the duplicated lines in their explanations are hidden on the site and are recorded only as a minor note.

## Subject to SRA mapping used
Business Law & Practice, Dispute Resolution and Legal Services map to FLK1-S1. Contract (Contract Law) and Tort map to FLK1-S2. Legal System of England and Wales and Constitutional & Administrative Law both map to **Legal Systems**, FLK1-S2. Wills, Trusts and Land Law map to FLK2-S1. Property Practice, Criminal Law (**Criminal Liability**) and Criminal Practice (**Criminal Law and Practice**) map to FLK2-S2. Ethics follows its context. Solicitors Accounts follows its Wills (FLK2-S1) or Property (FLK2-S2) context. The site's own subject labels were left as they are; the SRA name is in context_subject.

## Summary table
| id | site subject | flk | session | context / SRA subject | answer | status | substantive fix |
|---|---|---|---|---|---|---|---|
| q001 | Business Law & Practice | FLK1 | FLK1-S1 | Business Law and Practice | C | needs correction | add why_wrong |
| q002 | Dispute Resolution | FLK1 | FLK1-S1 | Dispute Resolution | B | needs correction | add why_wrong |
| q003 | Contract | FLK1 | FLK1-S2 | Contract Law | D | needs correction | add why_wrong |
| q004 | Tort | FLK1 | FLK1-S2 | Tort | A | needs correction | add why_wrong |
| q005 | Constitutional & Administrative Law | FLK1 | FLK1-S2 | Legal Systems (Constitutional and Administrative Law and EU Law) | E | needs correction | add why_wrong |
| q006 | Ethics & Professional Conduct | FLK1 | FLK2-S2 | Property Practice (commercial lease acquisition) | B | needs correction | flk |
| q007 | Property Practice | FLK2 | FLK2-S2 | Property Practice | C | needs correction | add why_wrong |
| q008 | Wills & Administration of Estates | FLK2 | FLK2-S1 | Wills and the Administration of Estates | A | needs correction | add why_wrong |
| q009 | Wills & Administration of Estates | FLK2 | FLK2-S1 | Wills and the Administration of Estates | D | needs correction | add why_wrong |
| q010 | Solicitors Accounts | FLK2 | FLK2-S2 | Property Practice (only once the proposed scenario correction is made; currently no context) | E | needs correction | scenario |
| q011 | Land Law | FLK2 | FLK2-S1 | Land Law | B | needs correction | add why_wrong |
| q012 | Trusts | FLK2 | FLK2-S1 | Trusts | C | needs correction | add why_wrong |
| q013 | Criminal Law | FLK2 | FLK2-S2 | Criminal Liability | A | needs correction | verified_source_url; tags |
| q014 | Criminal Practice | FLK2 | FLK2-S2 | Criminal Law and Practice | D | needs correction | add why_wrong |
| q015 | Business Law & Practice | FLK1 | FLK1-S1 | Business Law and Practice | B | needs correction | add why_wrong |
| q016 | Dispute Resolution | FLK1 | FLK1-S1 | Dispute Resolution | E | needs correction | key_rule |
| q017 | Contract | FLK1 | FLK1-S2 | Contract Law | A | needs correction | add why_wrong |
| q018 | Tort | FLK1 | FLK1-S2 | Tort | C | needs correction | key_rule |
| q019 | Legal System of England and Wales | FLK1 | FLK1-S2 | Legal Systems (Legal System of England and Wales) | D | needs correction | key_rule |
| q020 | Constitutional & Administrative Law | FLK1 | FLK1-S2 | Legal Systems (Constitutional and Administrative Law and EU Law) | B | needs correction | add why_wrong |
| q021 | Ethics & Professional Conduct | FLK1 | FLK1-S1 | Dispute Resolution (debt claim) | E | needs correction | add why_wrong |
| q022 | Property Practice | FLK2 | FLK2-S2 | Property Practice | C | needs correction | key_rule |
| q023 | Wills & Administration of Estates | FLK2 | FLK2-S1 | Wills and the Administration of Estates | E | needs correction | add why_wrong |
| q024 | Solicitors Accounts | FLK2 | FLK2-S2 | Property Practice (only once the proposed scenario correction is made; currently a business sale) | A | needs correction | scenario |
| q025 | Land Law | FLK2 | FLK2-S1 | Land Law | D | needs correction | add why_wrong |
| q026 | Trusts | FLK2 | FLK2-S1 | Trusts | B | needs correction | explanation |
| q027 | Criminal Law | FLK2 | FLK2-S2 | Criminal Liability | A | needs correction | add why_wrong |
| q028 | Criminal Practice | FLK2 | FLK2-S2 | Criminal Law and Practice | E | needs correction | add why_wrong |
| q029 | Business Law & Practice | FLK1 | FLK1-S1 | Business Law and Practice | D | needs correction | key_rule |
| q030 | Dispute Resolution | FLK1 | FLK1-S1 | Dispute Resolution | A | ready | - |
| q031 | Contract | FLK1 | FLK1-S2 | Contract Law | C | ready | - |
| q032 | Tort | FLK1 | FLK1-S2 | Tort | E | ready | - |
| q033 | Legal System of England and Wales | FLK1 | FLK1-S2 | Legal Systems (Legal System of England and Wales) | B | ready | - |
| q034 | Constitutional & Administrative Law | FLK1 | FLK1-S2 | Legal Systems (Constitutional and Administrative Law and EU Law) | A | needs correction | key_rule |
| q035 | Ethics & Professional Conduct | FLK1 | FLK2-S2 | Property Practice (residential conveyancing) | D | needs correction | flk |
| q036 | Property Practice | FLK2 | FLK2-S2 | Property Practice | E | needs correction | key_rule |
| q037 | Wills & Administration of Estates | FLK2 | FLK2-S1 | Wills and the Administration of Estates | B | ready | - |
| q038 | Solicitors Accounts | FLK2 | FLK2-S1 | Wills and the Administration of Estates (only once the proposed scenario correction is made; currently no context) | C | needs correction | scenario |
| q039 | Land Law | FLK2 | FLK2-S1 | Land Law | A | ready | - |
| q040 | Trusts | FLK2 | FLK2-S1 | Trusts | D | needs correction | key_rule |
| q041 | Criminal Law | FLK2 | FLK2-S2 | Criminal Liability | B | ready | - |
| q042 | Criminal Practice | FLK2 | FLK2-S2 | Criminal Law and Practice | E | needs correction | key_rule |
| q043 | Business Law & Practice | FLK1 | FLK1-S1 | Business Law and Practice | C | ready | - |
| q044 | Dispute Resolution | FLK1 | FLK1-S1 | Dispute Resolution | E | needs correction | key_rule |
| q045 | Contract | FLK1 | FLK1-S2 | Contract Law | A | ready | - |
| q046 | Tort | FLK1 | FLK1-S2 | Tort | B | ready | - |
| q047 | Legal Services | FLK1 | FLK1-S1 | Legal Services | D | ready | - |
| q048 | Constitutional & Administrative Law | FLK1 | FLK1-S2 | Legal Systems (Constitutional and Administrative Law and EU Law) | C | ready | - |
| q049 | Ethics & Professional Conduct | FLK2 | FLK2-S1 | Wills and the Administration of Estates (will instructions) | A | ready | - |

## Substantive corrections (exact text)
**q006 · flk**
- old: `FLK1`
- new: `FLK2`

**q010 · scenario**
- old: `A firm holds £3,000 in client account, received from a client 'on account of costs' at the start of a matter.`
- new: `A firm acting for a client on the purchase of a house holds £3,000 in client account, received from the client 'on account of costs' at the start of the matter.`

**q013 · verified_source_url**
- old: `https://www.supremecourt.uk/cases/uksc-2016-0213`
- new: `https://www.bailii.org/uk/cases/UKSC/2017/67.html`

**q013 · tags**
- old: `['dishonesty', 'theft', 'ivey v genting']`
- new: `['dishonesty', 'fraud', 'ivey v genting']`

**q016 · key_rule**
- old: `Once an acknowledgment of service is filed, the defence is due 28 days after service of the particulars of claim, and judgment in default of defence is available only after that period expires with no defence filed at the date judgment is entered.`
- new: `Once an acknowledgment of service is filed, the defence is due 28 days after service of the particulars of claim, and default judgment is available only if that period expires with no defence filed.`

**q018 · key_rule**
- old: `After Paul v Royal Wolverhampton NHS Trust, a secondary victim must have witnessed an accident (an unexpected and unintended event causing injury by violent external means) or its immediate aftermath; witnessing a death from negligently untreated disease does not ground a claim.`
- new: `After Paul v Royal Wolverhampton NHS Trust, a secondary victim must witness an accident or its immediate aftermath; witnessing death or injury from negligently untreated disease does not ground a claim.`

**q019 · key_rule**
- old: `The Court of Appeal (Civil Division) is bound by its own decisions except where they conflict, cannot stand with a decision of the House of Lords, or were given per incuriam, and a larger panel has no greater power to depart.`
- new: `The Court of Appeal (Civil Division) is bound by its own decisions unless they conflict, cannot stand with a House of Lords decision, or were given per incuriam; a larger panel has no greater power.`

**q022 · key_rule**
- old: `Under SCS 6.8, a notice to complete requires completion within ten working days, excluding the day of service, with time of the essence, and a buyer who paid less than 10% must top the deposit up to 10% at once.`
- new: `Under SCS 6.8, a notice to complete requires completion within ten working days (excluding the day given), time being of the essence; a buyer who paid under 10% must top up the deposit immediately.`

**q024 · scenario**
- old: `Hartley & Rowe LLP acted for Tomasz on the sale of his café.`
- new: `Hartley & Rowe LLP acted for Tomasz on the sale of the freehold premises of his former café.`

**q026 · explanation**
- old: `Scarman LJ said there must be clear evidence from what is said or done of an intention to create a trust.`
- new: `Scarman LJ accepted that there must be clear evidence from what is said or done of an intention to create a trust.`

**q029 · key_rule**
- old: `A company buying from, or selling to, a director a non-cash asset worth more than £100,000, or more than 10% of its net assets and over £5,000, needs a members' resolution (ordinary unless the articles say otherwise) or a contract conditional on one.`
- new: `A company buying a non-cash asset from, or selling one to, a director needs members' approval (or a conditional contract) if it is worth over £100,000, or over 10% of net assets and over £5,000.`

**q034 · key_rule**
- old: `A public Bill (not a Money Bill or one extending Parliament's life) rejected by the Lords in two successive sessions can receive Royal Assent without them, provided a year has passed between its first Commons second reading and its second Commons passage.`
- new: `A public Bill (not a Money Bill or one extending Parliament's life) rejected by the Lords in two successive sessions can receive Royal Assent without them if a year separates the required Commons stages.`

**q035 · flk**
- old: `FLK1`
- new: `FLK2`

**q036 · key_rule**
- old: `A section 25 notice must be in the prescribed form, given 6 to 12 months before a termination date no earlier than the contractual expiry date, and must state whether the landlord opposes a new tenancy and, if so, on which s.30(1) grounds.`
- new: `A s.25 notice must be in prescribed form, given 6 to 12 months before a termination date no earlier than contractual expiry, stating whether the landlord opposes a new tenancy and on which s.30(1) grounds.`

**q038 · scenario**
- old: `two separate designated deposit client accounts for clients with large sums on long-term matters.`
- new: `two separate designated deposit client accounts holding large sums for estates in long-running administrations.`

**q040 · key_rule**
- old: `For trusts created or arising after 1 October 2014, trustees may advance capital up to the whole of a beneficiary's presumptive share, even where the interest is contingent, subject to bringing it into account and to the consent of anyone with a prior interest.`
- new: `For trusts created or arising after 1 October 2014, trustees may advance up to a beneficiary's whole presumptive share, even if contingent, subject to bringing it into account and any prior interest holder's consent.`

**q042 · key_rule**
- old: `A superintendent or above responsible for the station may extend detention without charge for an indictable (including either-way) offence up to 36 hours from the relevant time, normally arrival at the station, after the second review and within the first 24 hours.`
- new: `A superintendent responsible for the station may extend detention without charge for an indictable (including either-way) offence to 36 hours from the relevant time, after the second review and within the first 24 hours.`

**q044 · key_rule**
- old: `The court may give summary judgment for or against either party, on a whole claim or an issue, if the other side has no real prospect of success and there is no other compelling reason for a trial; a claimant may apply once an acknowledgment of service or defence is filed (CPR 24.3, 24.4(1)).`
- new: `Summary judgment may be given for or against either party, on a claim or issue, if that party has no real prospect of success and there is no other compelling reason for a trial (CPR 24.3).`

## Per-question notes
### q001 · Removing a company director: ordinary resolution and special notice
- Status: **needs correction**. Session FLK1-S1; context Business Law and Practice; answer C; difficulty medium; tags directors, removal of directors, special notice, members' resolutions.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/2006/46/section/168
- Quote: "A company may by ordinary resolution at a meeting remove a director before the expiration of his period of office, notwithstanding anything in any agreement between it and him. (2)Special notice is required of a resolution to remove a director under this section"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Explanation is 70 words (brief floor 80). Style only. s.288(2)(a) and s.312(1) were checked on their own legislation.gov.uk pages today; s.168 page has unapplied changes only to Sch 11A (not relevant).
- Correction: add `why_wrong` for A, B, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.

### q002 · Time limit for serving a claim form within the jurisdiction (CPR 7.5)
- Status: **needs correction**. Session FLK1-S1; context Dispute Resolution; answer B; difficulty medium; tags service, claim form, time limits.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part07
- Quote: "before 12.00 midnight on the calendar day four months after the date of issue of the claim form. ... First class post ... Posting"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Explanation 64 words (below 80). Date check: 10 Feb 2026 + 4 calendar months = 10 June 2026.
- Correction: add `why_wrong` for A, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.

### q003 · Counter-offers and the rejection of an original offer
- Status: **needs correction**. Session FLK1-S2; context Contract Law; answer D; difficulty easy; tags offer and acceptance, counter-offer, formation.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/ew/cases/EWHC/Ch/1840/J90.html
- Quote: "the Plaintiff made an offer of his own, to purchase the property for £950, and he thereby rejected the offer previously made by the Defendant. I think that it was not afterwards competent for him to revive the proposal of the Defendant"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Explanation 54 words (below 80). Option C is weak as a distractor but not arguably right.
- Correction: add `why_wrong` for A, B, C, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.

### q004 · Occupiers' liability to skilled visitors and risks incident to their calling
- Status: **needs correction**. Session FLK1-S2; context Tort; answer A; difficulty medium; tags occupiers' liability, visitors, skilled visitors.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Eliz2/5-6/31/section/2
- Quote: "an occupier may expect that a person, in the exercise of his calling, will appreciate and guard against any special risks ordinarily incident to it, so far as the occupier leaves him free to do so."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Explanation 77 words (below 80). Roles v Nathan cited in authority; not separately fetched (statute directly supports).
- Correction: add `why_wrong` for B, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.

### q005 · Judicial review time limits: promptly and within three months
- Status: **needs correction**. Session FLK1-S2; context Legal Systems (Constitutional and Administrative Law and EU Law); answer E; difficulty medium; tags judicial review, time limits.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part54
- Quote: "(1) The claim form must be filed – (a) promptly; and (b) in any event not later than 3 months after the grounds to make the claim first arose. (2) The time limits in this rule may not be extended by agreement between the parties."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Explanation 66 words (below 80). CPR 54.5 now also refers to Public Contracts Regulations decisions; irrelevant here. Grounds arose 2 March 2026, so the long-stop is 2 June 2026.
- Correction: add `why_wrong` for A, B, C, D. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q006 · Acting for clients competing for the same objective (SRA Code 6.2)
- Status: **needs correction**. Session FLK2-S2; context Property Practice (commercial lease acquisition); answer B; difficulty medium; tags conflict of interest, sra code of conduct.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.sra.org.uk/solicitors/standards-regulations/code-conduct-solicitors/
- Quote: "the clients are competing for the same objective, and the conditions below are met, namely that: (I) all the clients have given informed consent, given or evidenced in writing, to you acting; (II) where appropriate, you put in place effective safeguards"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Paper/session: an Ethics question set in a commercial lease acquisition, a Property Practice context (FLK2, session 2). As written it sits on FLK1. Changing flk moves it between the site's FLK pages; route is number-locked, so the URL does not change.
- Correction: add `why_wrong` for A, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.
- Correction: `flk`, see 'Substantive corrections' above.

### q007 · Priority period of an official search of registered land (OS1)
- Status: **needs correction**. Session FLK2-S2; context Property Practice; answer C; difficulty medium; tags official search, priority period, registered land.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/uksi/2003/1417/rule/131
- Quote: "“priority period” means the period beginning at the time when an application for an official search is entered on the day list and ending at midnight marking the end of the thirtieth working day thereafter"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- LRR r.131 uses 'working day', matching the question. Page lists unapplied changes only to r.72(5A) and form CH1, not r.131.
- Correction: add `why_wrong` for A, B, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q008 · Gifts to a witness's spouse under section 15 Wills Act 1837
- Status: **needs correction**. Session FLK2-S1; context Wills and the Administration of Estates; answer A; difficulty easy; tags witnesses, gifts, wills act 1837.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Will4and1Vict/7/26/section/15
- Quote: "so far only as concerns such person attesting the execution of such will, or the wife or husband of such person ... be utterly null and void, and such person so attesting shall be admitted as a witness to prove the execution of such will"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- s.15 text says 'wife or husband'; legislation.gov.uk notes s.15 applied to civil partners by Civil Partnership Act 2004 Sch 4 para 3, so the explanation's 'civil partner' gloss is supported. Wills Act 1968 s.1 checked. Explanation 79 words.
- Correction: add `why_wrong` for B, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q009 · Intestacy and the 28-day spousal survivorship rule
- Status: **needs correction**. Session FLK2-S1; context Wills and the Administration of Estates; answer D; difficulty hard; tags intestacy, survivorship, spouse.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Geo5/15-16/23/section/46
- Quote: "Where the intestate’s spouse or civil partner survived the intestate but died before the end of the period of 28 days beginning with the day on which the intestate died, this section shall have effect ... as if the spouse or civil partner had not survived the intestate."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Explanation 74 words (below 80).
- Correction: add `why_wrong` for A, B, C, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q010 · Transferring client money for costs: bill first (SRA Accounts Rules 4.3)
- Status: **needs correction**. Session FLK2-S2; context Property Practice (only once the proposed scenario correction is made; currently no context); answer E; difficulty medium; tags client account, costs, sra accounts rules.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.sra.org.uk/solicitors/standards-regulations/accounts-rules/
- Quote: "(a) you must give a bill of costs, or other written notification of the costs incurred, to the client or the paying party; (b) this must be done before you transfer any client money from a client account to make the payment; and (c) any such payment must be for the specific sum identified"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- No Wills or Property context, which the brief requires for Solicitors Accounts. The proposed minimal change adds a Property context without altering the point tested.
- Correction: add `why_wrong` for A, B, C, D. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.
- Correction: `scenario`, see 'Substantive corrections' above.

### q011 · Freehold covenants: the burden of a positive covenant does not run
- Status: **needs correction**. Session FLK2-S1; context Land Law; answer B; difficulty medium; tags freehold covenants, positive covenants, burden.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/uk/cases/UKHL/1994/3.html
- Quote: "I do not consider that it follows that section 79 of the Act of 1925 had the corresponding effect of making the burden of positive covenants run with the land."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Rhone v Stephens on BAILII is the primary judgment.
- Correction: add `why_wrong` for A, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q012 · The rule in Saunders v Vautier: ending a trust early
- Status: **needs correction**. Session FLK2-S1; context Trusts; answer C; difficulty hard; tags saunders v vautier, beneficiaries, ending a trust.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/ew/cases/EWHC/Ch/1841/J82.html
- Quote: "There is no gift over ... I am clearly of opinion that he is entitled to it. ... The order for a transfer of the funds, upon the regular evidence of the legatee having attained twenty-one, will follow this decision"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Saunders v Vautier on BAILII supports the vested-with-postponed-enjoyment reading and the transfer at 21 (then majority). Option A says 'testator' of a grandmother (testatrix): cosmetic only.
- Correction: add `why_wrong` for A, B, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.

### q013 · The test for dishonesty after Ivey v Genting and R v Barton
- Status: **needs correction**. Session FLK2-S2; context Criminal Liability; answer A; difficulty medium; tags dishonesty, theft, ivey v genting.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, implied by the Fraud Act 2006. No ambiguity found.
- Source checked (2026-10-16): https://www.supremecourt.uk/cases/uksc-2016-0213 (fetched; case page only) ; https://www.bailii.org/uk/cases/UKSC/2017/67.html
- Quote: "When dishonesty is in question the fact-finding tribunal must first ascertain (subjectively) the actual state of the individual’s knowledge or belief as to the facts. ... There is no requirement that the defendant must appreciate that what he has done is, by those standards, dishonest."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- verified_source_url is the UKSC case-information page (dates, links, justices). It does not contain the test. The judgment on BAILII (para 74) does. Barton [2020] EWCA Crim 575 was also checked on caselaw.nationalarchives.gov.uk: 'We are satisfied that the decision in Ivey is correct ... applied as the law of England and Wales'.
- Tag 'theft' is wrong for this question, which concerns fraud by false representation (Fraud Act 2006 s.2). Fetched s.2 today: '(1)A person is in breach of this section if he— (a)dishonestly makes a false representation'.
- Correction: add `why_wrong` for B, C, D, E. Full text is in audit.json.
- Correction: `last_reviewed` null to `2026-10-16`.
- Correction: `verified_source_url` and `tags`, see 'Substantive corrections' above.

### q014 · Delaying access to legal advice at the police station (PACE s.58)
- Status: **needs correction**. Session FLK2-S2; context Criminal Law and Practice; answer D; difficulty medium; tags police station, legal advice, pace.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1984/60/section/58
- Quote: "(6)Delay in compliance with a request is only permitted— (a)in the case of a person who is in police detention for an indictable offence; and (b)if an officer of at least the rank of superintendent authorises it."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- s.58 page: unapplied changes listed are to other PACE sections (38, 47A, 63B, 64A, Sch 1A), not s.58.
- Correction: add `why_wrong` for A, B, C, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q015 · Declaring an interest in a proposed transaction (CA 2006 s.177)
- Status: **needs correction**. Session FLK1-S1; context Business Law and Practice; answer B; difficulty medium; tags directors, declaration of interest, directors' duties.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/2006/46/section/177
- Quote: "If a director of a company is in any way, directly or indirectly, interested in a proposed transaction or arrangement with the company, he must declare the nature and extent of that interest to the other directors. ... (4)Any declaration required by this section must be made before the company enters into the transaction"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Key rule 36 words (about the limit).
- Correction: add `why_wrong` for A, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q016 · Default judgment after an acknowledgment of service (CPR 10.3, 15.4, 12.3)
- Status: **needs correction**. Session FLK1-S1; context Dispute Resolution; answer E; difficulty medium; tags default judgment, acknowledgment of service, time limits.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part15
- Quote: "(b)if the defendant files an acknowledgment of service under Part 10, 28 days after service of the particulars of claim."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Key rule is 43 words (limit about 35). CPR 12.3(2)(a) and 12.4 were also checked on justice.gov.uk Part 12 today.
- Correction: add `why_wrong` for A, B, C, D. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q017 · Part payment of a debt (Foakes v Beer)
- Status: **needs correction**. Session FLK1-S2; context Contract Law; answer A; difficulty medium; tags consideration, part payment, promissory estoppel.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/uk/cases/UKHL/1884/1.html
- Quote: ""that payment of a lesser sum on the day" (it would of course be the same after the day), "in satisfaction of a greater, cannot be any satisfaction for the whole""
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Foakes v Beer (BAILII) supports the Pinnel rule. D & C Builders v Rees [1965] EWCA Civ 3 and Rock Advertising [2018] UKSC 24 were also fetched from BAILII. D&C: 'Where there has been a true accord ... But he is not bound unless there has been truly an accord'. Rock para 18: 'practical expectation of benefit was the very thing which the House of Lords held not to be adequate'. The 'true accord' reasoning is Lord Denning MR's. Key rule 39 words. The facts track D & C Builders closely; that is acceptable as an application, but note it for originality.
- Correction: add `why_wrong` for B, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q018 · Secondary victims after Paul v Royal Wolverhampton NHS Trust
- Status: **needs correction**. Session FLK1-S2; context Tort; answer C; difficulty hard; tags psychiatric injury, secondary victims, negligence.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/uk/cases/UKSC/2024/1.html
- Quote: "the persons whom doctors ought reasonably to have in contemplation when directing their minds to the care of a patient do not include members of the patient's close family who might be psychologically affected by witnessing the effects of a disease"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Key rule is 42 words. Paul on BAILII also supports B ('no justification for super-imposing an additional, separate requirement that the event witnessed ... was "horrifying"'), D (length of time irrelevant) and E ('wrong turn').
- Correction: add `why_wrong` for A, B, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q019 · Court of Appeal and its own previous decisions (Young v Bristol Aeroplane)
- Status: **needs correction**. Session FLK1-S2; context Legal Systems (Legal System of England and Wales); answer D; difficulty medium; tags precedent, court of appeal, stare decisis.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/ew/cases/EWCA/Civ/1944/1.html
- Quote: "This was clearly a case where the earlier decision was given per incuriam. It depended on the true meaning ... of a rule of the Supreme Court to which the court was apparently not referred and which it obviously had not in mind. The Rules of the Supreme Court have statutory force"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Key rule is 41 words. Young on BAILII: 'what is conveniently but inaccurately called the full court has any greater power ... than a division of the court consisting of three members only' supports B.
- Correction: add `why_wrong` for A, B, C, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q020 · Effect of a declaration of incompatibility (HRA 1998 ss.3-4)
- Status: **needs correction**. Session FLK1-S2; context Legal Systems (Constitutional and Administrative Law and EU Law); answer B; difficulty easy; tags human rights act 1998, declaration of incompatibility, parliamentary sovereignty.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1998/42/section/4
- Quote: "(6)A declaration under this section (“a declaration of incompatibility”)— (a)does not affect the validity, continuing operation or enforcement of the provision in respect of which it is given; and (b)is not binding on the parties to the proceedings in which it is made."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- HRA s.10(2) checked separately: 'If a Minister of the Crown considers that there are compelling reasons'.
- Correction: add `why_wrong` for A, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q021 · Acting against a former client whose confidential information you hold (SRA Code paras 6.3-6.5)
- Status: **needs correction**. Session FLK1-S1; context Dispute Resolution (debt claim); answer E; difficulty medium; tags confidentiality, former clients, sra code of conduct.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.sra.org.uk/solicitors/standards-regulations/code-conduct-solicitors/
- Quote: "unless: (a) effective measures have been taken which result in there being no real risk of disclosure of the confidential information; or (b) the current or former client whose information you or your business or employer holds has given informed consent, given or evidenced in writing"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Key rule 37 words.
- Correction: add `why_wrong` for A, B, C, D. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q022 · Failure to complete and the notice to complete (SCS 5th ed, condition 6.8)
- Status: **needs correction**. Session FLK2-S2; context Property Practice; answer C; difficulty medium; tags completion, notice to complete, standard conditions of sale.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.lawsociety.org.uk/-/media/files/topics/property/specimen-standard-conditions-of-sale-residential-property-2018.pdf
- Quote: "The parties are to complete the contract within ten working days of giving a notice to complete, excluding the day on which the notice is given. For this purpose, time is of the essence of the contract."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Key rule is 40 words. SCS specimen PDF (Fifth Edition, 2018 Revision) supports 6.8.1 to 6.8.3 and 1.3.2.
- Correction: add `why_wrong` for A, B, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q023 · Revocation of a will by marriage and the expectation of marriage exception (Wills Act 1837 s.18)
- Status: **needs correction**. Session FLK2-S1; context Wills and the Administration of Estates; answer E; difficulty medium; tags revocation, marriage, wills act 1837.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Will4and1Vict/7/26/section/18
- Quote: "Where it appears from a will that at the time it was made the testator was expecting to be married to a particular person and that he intended that the will should not be revoked by the marriage, the will shall not be revoked by his marriage to that person."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Key rule 39 words.
- Correction: add `why_wrong` for A, B, C, D. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q024 · Client account must not be used as a banking facility (SRA Accounts Rules, rule 3.3)
- Status: **needs correction**. Session FLK2-S2; context Property Practice (only once the proposed scenario correction is made; currently a business sale); answer A; difficulty easy; tags client account, banking facility, sra accounts rules.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.sra.org.uk/solicitors/standards-regulations/accounts-rules/
- Quote: "You must not use a client account to provide banking facilities to clients or third parties. Payments into, and transfers or withdrawals from a client account must be in respect of the delivery by you of regulated services."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- The context is a sale of a business (BLP), not Wills or Property as the brief requires for Solicitors Accounts. The proposed minimal change makes it a property sale. Nothing else in the scenario depends on the change; 'suppliers' invoices for a new business' still reads naturally.
- Correction: add `why_wrong` for B, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.
- Correction: `scenario`, see 'Substantive corrections' above.

### q025 · Overreaching on payment to two trustees and a beneficiary in actual occupation (LPA 1925 ss.2 and 27; City of London BS v Flegg)
- Status: **needs correction**. Session FLK2-S1; context Land Law; answer D; difficulty hard; tags overreaching, co-ownership, actual occupation.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/uk/cases/UKHL/1987/6.html
- Quote: "the interests of the respondents cannot at one and the same time be overreached and overridden and at the same time be overriding interests."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Explanation is exactly 200 words, at the ceiling. Flegg on BAILII also supports the 'equity of redemption' point. Note that 'registered proprietors ... in Reading' implies registered land, so LRA 2002 Sch 3 para 2 is the current home of the actual-occupation point, as the why_wrong says.
- Correction: add `why_wrong` for A, B, C, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q026 · Certainty of intention and precatory words
- Status: **needs correction**. Session FLK2-S1; context Trusts; answer B; difficulty medium; tags three certainties, certainty of intention, express trusts.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/ew/cases/EWCA/Civ/1976/2.html
- Quote: ""The words" ... "must be so used that on the whole they ought to be construed as imperative ... No particular form of expression is necessary for the creation of a trust, if on the whole it can be gathered that a trust was intended.""
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Accuracy: in Paul v Constance, the 'clear evidence' formulation is counsel's principle, which Scarman LJ adopted ('I think that the evidence does have to go as far as that'). Source scope: Paul v Constance supports the general test (imperative words, no particular form) but is not a precatory-words case. The application to 'in the hope and confidence' is orthodox (Re Adams and the Kensington Vestry). If a primary source for that is wanted, it would need to be fetched; no URL is proposed here.
- Correction: add `why_wrong` for A, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.
- Correction: `explanation`, see 'Substantive corrections' above.

### q027 · Oblique intention and the virtual certainty direction (R v Woollin)
- Status: **needs correction**. Session FLK2-S2; context Criminal Liability; answer A; difficulty medium; tags intention, mens rea, homicide.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://publications.parliament.uk/pa/ld199798/ldjudgmt/jd980722/wool.htm
- Quote: "By using the phrase "substantial risk" the judge blurred the line between intention and recklessness, and hence between murder and manslaughter. The misdirection enlarged the scope of the mental element required for murder. It was a material misdirection."
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- Woollin opinion (publications.parliament.uk) fetched via the Parliament archive. It supports A, B, C (Hyam 'highly probable' as part of the disarray), D (Moloney/Hancock) and E (CA's limitation rejected).
- Correction: add `why_wrong` for B, C, D, E. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q028 · Adverse inferences from silence and access to legal advice (CJPOA 1994 s.34(2A))
- Status: **needs correction**. Session FLK2-S2; context Criminal Law and Practice; answer E; difficulty medium; tags silence, adverse inferences, legal advice.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1994/33/section/34
- Quote: "Where the accused was at an authorised place of detention at the time of the failure, subsections (1) and (2) above do not apply if he had not been allowed an opportunity to consult a solicitor prior to being questioned"
- No why_wrong object; the reasons for the four wrong letters sit only as 'X is wrong' lines inside explanation (all four wrong letters are covered there). generate.py hides those lines automatically once why_wrong exists, so explanation need not change.
- s.34(2A) checked. Unapplied changes on the page are to CJPOA ss.25 and 51 only. ABH (s.47 OAPA) is either-way, so the superintendent's s.58 delay in the facts is consistent.
- Correction: add `why_wrong` for A, B, C, D. Full text is in audit.json; it copies the explanation's 'X is wrong' lines.
- Correction: `last_reviewed` null to `2026-10-16`.

### q029 · Substantial property transactions with a director: members' approval (CA 2006 ss.190-191)
- Status: **needs correction**. Session FLK1-S1; context Business Law and Practice; answer D; difficulty medium; tags directors, substantial property transactions, members' resolutions, non-cash assets.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/2006/46/section/190
- Quote: "(b)the company acquires or is to acquire a substantial non-cash asset (directly or indirectly) from such a director [s.190(1)]; [s.191(2), separately fetched:] An asset is a substantial asset ... if its value— (a)exceeds 10% of the company's asset value and is more than £5,000"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Key rule is 43 words. The verified source (s.190) does not contain the thresholds. s.191 was fetched separately and supports them (https://www.legislation.gov.uk/ukpga/2006/46/section/191). Consider citing it as a second source if the schema allows.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q030 · Claimant fails to beat a defendant's Part 36 offer: costs consequences (CPR 36.17(1)(a) and (3))
- Status: **ready**. Session FLK1-S1; context Dispute Resolution; answer A; difficulty medium; tags part 36, offers to settle, costs.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part36
- Quote: "“more advantageous” means better in money terms by any amount, however small ... the court must, unless it considers it unjust to do so, order that the defendant is entitled to— (a) costs (including any recoverable pre-action costs) from the date on wh[ich the relevant period expired]"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- CPR 36.17(3) is now 'Subject to paragraphs (7) and (8)'; no effect on the answer. Claim value is £180,000, so the fixed recoverable costs regime does not complicate it.

### q031 · Excluding liability for negligence in a business contract (Unfair Contract Terms Act 1977 s.2)
- Status: **ready**. Session FLK1-S2; context Contract Law; answer C; difficulty medium; tags exclusion clauses, unfair contract terms, negligence, reasonableness.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1977/50/section/2
- Quote: "(1)A person cannot by reference to any contract term ... exclude or restrict his liability for death or personal injury resulting from negligence. (2)In the case of other loss or damage, a person cannot so exclude or restrict his liability for negligence except in so far as the term"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- UCTA s.2: no outstanding effects.

### q032 · Occupiers' duty to trespassers and no recovery for property damage (Occupiers' Liability Act 1984 s.1(3), (4) and (8))
- Status: **ready**. Session FLK1-S2; context Tort; answer E; difficulty medium; tags occupiers' liability, trespassers, property damage.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1984/3/section/1
- Quote: "(8)Where a person owes a duty by virtue of this section, he does not, by reason of any breach of the duty, incur any liability in respect of any loss of or damage to property."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- OLA 1984: no outstanding effects.

### q033 · Using Hansard to interpret a statute: the conditions in Pepper v Hart [1993] AC 593
- Status: **ready**. Session FLK1-S2; context Legal Systems (Legal System of England and Wales); answer B; difficulty medium; tags statutory interpretation, hansard, pepper v hart, parliamentary material.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.bailii.org/uk/cases/UKHL/1992/3.html
- Quote: "reference to Parliamentary material should be permitted as an aid to the construction of legislation which is ambiguous or obscure ... I cannot foresee that any statement other than the statement of the Minister or other promoter of the Bill is likely to meet these criteria."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Pepper v Hart on BAILII supports all three conditions and the 'Minister or other promoter' limit.

### q034 · Passing a Bill without the consent of the House of Lords (Parliament Act 1911 s.2, as amended by the Parliament Act 1949)
- Status: **needs correction**. Session FLK1-S2; context Legal Systems (Constitutional and Administrative Law and EU Law); answer A; difficulty medium; tags parliament acts, house of lords, legislative process, parliamentary sovereignty.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Geo5/1-2/13/section/2
- Quote: "Provided that this provision shall not take effect unless one year has elapsed between the date of the second reading in the first of those sessions of the Bill in the House of Commons and the date on which it passes the House of Commons in the second of these sessions."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Key rule is 42 words.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q035 · Oral undertakings and the time for performance (SRA Code of Conduct for Solicitors, para 1.3)
- Status: **needs correction**. Session FLK2-S2; context Property Practice (residential conveyancing); answer D; difficulty easy; tags undertakings, professional conduct, conveyancing.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.sra.org.uk/solicitors/standards-regulations/code-conduct-solicitors/
- Quote: "You perform all undertakings given by you, and do so within an agreed timescale or if no timescale has been agreed then within a reasonable amount of time. [Glossary:] undertaking means a statement, given orally or in writing, whether or not it includes the word "undertake""
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Paper/session: an undertaking given in a residential conveyancing context is an Ethics question in Property Practice (FLK2, session 2). As written it sits on FLK1. The route is number-locked.
- Correction: `flk`, see 'Substantive corrections' above.

### q036 · Landlord's section 25 notice: timing, termination date and grounds of opposition (LTA 1954 s.25)
- Status: **needs correction**. Session FLK2-S2; context Property Practice; answer E; difficulty medium; tags business tenancies, section 25 notice, security of tenure, landlord and tenant act 1954.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Eliz2/2-3/56/section/25
- Quote: "a notice under this section shall not have effect unless it is given not more than twelve nor less than six months before the date of the termination specified therein. ... shall not have effect unless it also specifies one or more of the grounds specified in section 30(1)"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Key rule is 43 words. The page lists unapplied changes only to LTA 1954 s.63. Date check: 2 Dec 2026 to 30 June 2027 is within 6 to 12 months.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q037 · Gift to a child who dies before the testator leaving issue (Wills Act 1837 s.33)
- Status: **ready**. Session FLK2-S1; context Wills and the Administration of Estates; answer B; difficulty easy; tags lapse, section 33, gifts to issue, predeceasing beneficiary.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Will4and1Vict/7/26/section/33
- Quote: "(a)a will contains a devise or bequest to a child or remoter descendant of the testator; and (b)the intended beneficiary dies before the testator, leaving issue; and (c)issue of the intended beneficiary are living at the testator’s death"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Key rule 36 words.

### q038 · Client account reconciliations every five weeks (SRA Accounts Rules, rule 8.3)
- Status: **needs correction**. Session FLK2-S1; context Wills and the Administration of Estates (only once the proposed scenario correction is made; currently no context); answer C; difficulty easy; tags reconciliation, client account, cofa, accounting records.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.sra.org.uk/solicitors/standards-regulations/accounts-rules/
- Quote: "You complete at least every five weeks, for all client accounts held or operated by you, a reconciliation of the bank or building society statement balance with the cash book balance and the client ledger total, a record of which must be signed off by the COFA or a manager"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- No Wills or Property context, which the brief requires for Solicitors Accounts. The proposed minimal change gives a Wills (estate administration) context; the point tested is unchanged.
- Correction: `scenario`, see 'Substantive corrections' above.

### q039 · Legal leases of seven years or less as overriding interests (LRA 2002 Sch 3 para 1)
- Status: **ready**. Session FLK2-S1; context Land Law; answer A; difficulty medium; tags overriding interests, short leases, registered land, schedule 3.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/2002/9/schedule/3
- Quote: "A leasehold estate in land granted for a term not exceeding seven years from the date of the grant, except for— (a)a lease the grant of which falls within section 4(1)(d), (e) or (f); (b)a lease the grant of which constitutes a registrable disposition."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- LRA Sch 3: no outstanding effects. s.27(2)(b)(i) checked separately ('for a term of more than seven years').

### q040 · Statutory power of advancement: up to the whole presumptive share (Trustee Act 1925 s.32)
- Status: **needs correction**. Session FLK2-S1; context Trusts; answer D; difficulty medium; tags power of advancement, presumptive share, contingent interest, trustee powers.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Geo5/15-16/19/section/32
- Quote: "the capital of the trust property or of any share thereof, whether absolutely or contingently on his attaining any specified age ... the presumptive or vested share or interest of that person in the trust property"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Key rule is 44 words. ITPA 2014 s.10(4) checked ('apply only in relation to trusts created or arising after the coming into force'). The 1 October 2014 commencement date is not stated on that page; it is the well-known commencement (SI 2014/2039).
- Correction: `key_rule`, see 'Substantive corrections' above.

### q041 · Burglary where the intent to steal is formed after entry (Theft Act 1968 s.9(1)(b))
- Status: **ready**. Session FLK2-S2; context Criminal Liability; answer B; difficulty easy; tags burglary, trespasser, theft, mens rea.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1968/60/section/9
- Quote: "(b)having entered any building or part of a building as a trespasser he steals or attempts to steal anything in the building"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- TA 1968 page lists unapplied ss.26A-26C (2026 c. 20) only, not s.9.

### q042 · Extending detention without charge from 24 to 36 hours (PACE 1984 ss.41 and 42)
- Status: **needs correction**. Session FLK2-S2; context Criminal Law and Practice; answer E; difficulty medium; tags police detention, detention time limits, superintendent authorisation, pace.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1984/60/section/42
- Quote: "Where a police officer of the rank of superintendent or above who is responsible for the police station at which a person is detained has reasonable grounds for believing that ... an offence for which he is under arrest is an indictable offence"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Key rule is 42 words. s.41(2)(d) checked separately: relevant time is arrival at the first police station. 9 November 2026 is a Monday, as stated.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q043 · Changing the nature of a partnership business needs every partner's consent (Partnership Act 1890 s.24(8))
- Status: **ready**. Session FLK1-S1; context Business Law and Practice; answer C; difficulty medium; tags partnership, partnership act 1890, decision making, unanimity.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/Vict/53-54/39/section/24
- Quote: "Any difference arising as to ordinary matters connected with the partnership business may be decided by a majority of the partners, but no change may be made in the nature of the partnership business without the consent of all existing partners."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- s.25 (expulsion), relied on for E, was fetched separately today: 'No majority of the partners can expel any partner unless a power to do so has been conferred by express agreement between the partners.'

### q044 · Summary judgment: no real prospect and no other compelling reason for a trial (CPR 24.3 and 24.4)
- Status: **needs correction**. Session FLK1-S1; context Dispute Resolution; answer E; difficulty medium; tags summary judgment, real prospect, case management.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.justice.gov.uk/courts/procedure-rules/civil/rules/part24
- Quote: "The court may give summary judgment against a claimant or defendant on the whole of a claim or on an issue if— (a) it considers that the party has no real prospect of succeeding on the claim, defence or issue; and (b) there is no other compelling reason"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Key rule is 54 words, well over the limit.
- Correction: `key_rule`, see 'Substantive corrections' above.

### q045 · Damages for negligent misrepresentation and the reverse burden of proof (Misrepresentation Act 1967 s.2(1))
- Status: **ready**. Session FLK1-S2; context Contract Law; answer A; difficulty medium; tags misrepresentation, damages, burden of proof, negligent misrepresentation.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1967/7/section/2
- Quote: "that person shall be so liable notwithstanding that the misrepresentation was not made fraudulently, unless he proves that he had reasonable ground to believe and did believe up to the time the contract was made the facts represented were true."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Unapplied change to s.2(4) (SI 2025/381) concerns the consumer-protection carve-out, not s.2(1). Key rule 38 words.

### q046 · Recoverable damage under the Consumer Protection Act 1987: the product itself is excluded (s.5)
- Status: **ready**. Session FLK1-S2; context Tort; answer B; difficulty medium; tags product liability, consumer protection act 1987, strict liability, recoverable damage.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1987/43/section/5
- Quote: "A person shall not be liable under section 2 above in respect of any defect in a product for the loss of or any damage to the product itself"
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- CPA s.5: no outstanding effects.

### q047 · Which activities are reserved legal activities? Probate activities v will-writing (Legal Services Act 2007 s.12 and Sch 2)
- Status: **ready**. Session FLK1-S1; context Legal Services; answer D; difficulty easy; tags reserved legal activities, probate activities, will writing, legal services act 2007.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/2007/29/schedule/2
- Quote: "“Probate activities” means preparing any probate papers for the purposes of the law of England and Wales ... “probate papers” means papers on which to found or oppose—(a)a grant of probate, or(b)a grant of letters of administration."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- LSA s.12 checked separately; Sch 2 para 5(3)(a) excludes wills.

### q048 · Hybrid public authorities and private acts under the Human Rights Act 1998 s.6(3)(b) and (5)
- Status: **ready**. Session FLK1-S2; context Legal Systems (Constitutional and Administrative Law and EU Law); answer C; difficulty medium; tags human rights act 1998, public authority, hybrid authority, section 6.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.legislation.gov.uk/ukpga/1998/42/section/6
- Quote: "(b)any person certain of whose functions are functions of a public nature ... (5)In relation to a particular act, a person is not a public authority by virtue only of subsection (3)(b) if the nature of the act is private."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Hybrid authority status of a private immigration detention contractor is orthodox but the source does not itself decide it. YL is cited for the framework (in YL the majority found the care home was not a public authority), so it is fine as cited.

### q049 · Taking will instructions from a relative: acting only on the client's own instructions (SRA Code para 3.1)
- Status: **ready**. Session FLK2-S1; context Wills and the Administration of Estates (will instructions); answer A; difficulty medium; tags client instructions, wills, vulnerable clients, client care.
- Single best answer and clear facts: yes. Jurisdiction is England and Wales, either implied by the statute or case or stated in the facts. No ambiguity found unless noted below.
- Source checked (2026-10-16): https://www.sra.org.uk/solicitors/standards-regulations/code-conduct-solicitors/
- Quote: "You only act for clients on instructions from the client, or from someone properly authorised to provide instructions on their behalf. If you have reason to suspect that the instructions do not represent your client's wishes, you do not act unless you have satisfied yourself that they do."
- Minor (no change proposed): explanation still repeats the 'X is wrong' lines as well as why_wrong. The site hides them (generate.py WRONG_LINE filter), but brief rule 4 says the explanation should not include them; strip only if the bank is being normalised.
- Key rule 37 words.

## Cross-bank checks
- **Duplication:** none. Related pairs test different points: q001, q015 and q029 (removing a director, declaring an interest, a substantial property transaction); q004 and q032 (visitor, trespasser); q020 and q048 (declaration of incompatibility, hybrid authority); q014, q028 and q042 (delay in legal advice, silence inference, extending detention); q008, q023 and q037 (s.15, s.18, s.33 Wills Act); q010, q024 and q038 (costs transfer, banking facility, reconciliation); q006 and q021 (conflict, confidentiality).
- **Outdated law:** none found as at 11 September 2026. Pending reform not in force, such as the Law Commission's wills and 1954 Act projects, does not affect any answer.
- **Style (not blocking):** explanations below the 80-word floor are q001 (70), q002 (64), q003 (54), q004 (77), q005 (66), q008 (79) and q009 (74). q025 is exactly at the 200-word ceiling. Key rules over about 35 words are trimmed only where they exceeded 40, plus q022 at 40.
- **Answer letters across the 49:** A 11, B 10, C 9, D 9, E 10.

## Applied in this PR (16 Oct 2026, awaiting approval)
All corrections above are applied to content/questions.json **except q001's why_wrong**. Adding it changes q001's content hash, and `scripts/test_site.py` (line ~187) assumes the first published question has never been modified, so PR checks would fail. That fixture belongs to the test suite (Codex); q001's why_wrong will follow once the fixture is adjusted. last_reviewed is set to 2026-10-16 only where the source was re-fetched and checked on that date.
