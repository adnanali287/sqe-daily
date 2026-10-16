# SQE Daily

Free, independent SQE1 practice: one original question per publishing day, five options, a worked answer and a primary-source link. Static HTML, CSS and vanilla JavaScript, hosted on GitHub Pages at https://sqedaily.co.uk.

## Run locally

Python 3.9+ (with Europe/London timezone data) is required. No Python packages or website runtime dependencies are needed.

```sh
python3 scripts/generate.py --package
python3 scripts/test_site.py
node scripts/test_dates.cjs
node scripts/test_answers.cjs
python3 scripts/test_practice.py
node scripts/test_test_core.cjs
python3 -m http.server 8766 --directory _site
```

Open http://localhost:8766. Serve `_site`, not the repository root, to preview the exact deployed package. `--date YYYY-MM-DD` is available for generator testing; do not deploy a future-date preview.

## Practice library and tests

`/tests/` provides 10- or 20-question mini tests from the available library, filtered by paper and optionally subject, with timed and untimed modes. Full papers require an approved 170-question composition: two locked 85-question sessions, 153 minutes per timed session and a 60-minute break. Scores, flags, answers and timing stay in local storage on the visitor's device; there are no accounts or result submissions. A timed attempt continues while the tab is closed.

Library availability is separate from the daily feature date. Exact-content approvals in `content/practice.json` can release a question early without changing its daily question or newsletter schedule. New library-only questions may use `publish_date: null`; they require a release approval and are never selected as the daily question. Existing question dates and locked URLs must not be changed. Unapproved, stale or incomplete mock compositions are not offered. The checked-in practice configuration intentionally contains no early releases or approved mocks.

See [the content contract](docs/practice-content-contract.md) for the release and mock schema and fingerprinted approval commands. Hark supplies and reviews content; owner approval is required before recording releases or mock approvals. Do not copy temporary QA approvals or synthetic mock fixtures into production. Draft content and private authoring metadata are excluded from the deployment package.

## Add questions

Append valid objects to `content/questions.json`; keep all existing field names. Each question needs a unique id and integer number, ISO publish_date, subject, FLK1/FLK2, difficulty, title, scenario, stem, five A–E options, answer, explanation, key_rule, authority and verified HTTPS source URL. The subject must be one of the names in `SUBJECTS` in `scripts/generate.py`; anything else fails the build. Hark's workflow is unchanged: Hark maintains `content/questions.json` and pushes. Page copy lives separately in `content/pages.json` (see below), so question work and page work never touch the same file.

Optional question fields (leave a field out rather than guess):

- `why_wrong`: `{"A": "One-line reason.", ...}` with exactly the four wrong letters. Shown in place of the combined "X is wrong" lines.
- `tags`: 1–5 lowercase topic strings, reused consistently across questions.
- `last_reviewed`: ISO date the question was actually re-checked against its primary source. Shows "Checked against primary source on …". Never in the future.
- `last_modified`: ISO date the visible content genuinely changed after publication. A source check alone is not a modification.

Modification dates are also detected automatically: the route lock stores a hash of each published question's visible content (title, scenario, stem, options, answer, explanation, key rule, authority, source URL, `why_wrong`, subject, paper, difficulty). When a publishing build sees it change, it records that day as the modification date. The later of that date and `last_modified` drives sitemap `lastmod` and `dateModified`. Tags and `last_reviewed` never count as modifications.

### Page copy and approval

`content/pages.json` holds all editorial copy:
- `sittings`: SRA exam dates, which drive the homepage countdown and `/sqe1-exam-dates/`;
- `pages`: `sqe1-practice-questions`, `flk1`, `flk2`, `sqe1-exam-dates` and `editorial-standards`;
- `guides`: any slug, published at `/guides/<slug>/` with a `/guides/` index;
- `subjects`: introductions for subject archives, keyed by the exact subject name.

**Format.** Copy is plain text: blank lines separate paragraphs. Links are `[text](https://…)`, `[text](/path/)` or `[text](mailto:…)`. A link to an internal page that isn't live renders as plain text, so partial approval never breaks links. No HTML, names or credentials. Exam facts come from the SRA's own pages, and legal statements come from primary sources.

**Approval.**
- Every entry starts as `approved: false` and is not published.
- `python3 scripts/approval_batch.py` writes `docs/editorial-approval-batch.md`: every unapproved entry exactly as it will publish, with a fingerprint.
- After the owner approves in chat, record it with `python3 scripts/generate.py --approve <entry> --expect <fingerprint>`, for example `pages.flk1`, `guides.sqe1-revision-timetable`, `sittings.0` or `subjects.Contract`. This refuses if the text changed since the batch was shown. The owner never edits JSON.
- Any later edit withdraws approval until the entry is approved again:
  - the page, guide or introduction is not published;
  - an edited sitting stops driving the countdown;
  - the build prints a warning, and pull-request checks fail.

**What approval publishes.**
- Approved subject introductions add the introduction, a "Rules to remember" section built from the published questions' `key_rule`, and a fuller title, at the same `/archive/<subject>/` URL.
- Approved pages and guides record the day they were first published and the day their copy last changed. These dates feed sitemap `lastmod` and structured data.

**Related questions.** Each question page lists up to three other published questions: shared `tags` first, then the same subject, then the same paper. Adding `tags` to questions improves the matches.

**Maintenance documents.** See `docs/`: the approval batch, the 90-day content and outreach backlog, the outreach drafts (never sent automatically) and the measurement baseline.

### Permanent URLs

`content/routes.lock.json` is generator-owned; never edit it by hand. A question's URL is fixed the first time it is published, so editing a published title changes its title and heading but never its URL, share link, sitemap or RSS entry. The build fails if a lock entry would move an already-published page or a subject slug differs. Previews with `--date` never write the lock.

The home question is the newest question whose publish_date is no later than today's Europe/London date; ties use the highest number. If there is no question today, the latest past question remains available. Nothing future-dated is rendered or included in the deployed JSON, sitemap or RSS. The full authoring bank remains in the public GitHub repository, so scheduled questions are not confidential there.

`scripts/generate.py` rebuilds question pages at their locked `/q/<number>-<title-slug>/` URLs, the server-rendered homepage, the main and subject archives, About, Sponsor, Privacy, approved pages, guides and subject introductions from `content/pages.json`, 404, sitemap and RSS. Generated pages should not be edited by hand. Home layout source is `scripts/templates/home.html`; shared styles and interactions are in `assets/`. The homepage HTML contains the latest question, its permanent link and recent questions; JavaScript still refreshes it at London midnight, keeps checking every 5 minutes until that day's question is live (scheduled publishing can run late), picks up corrections to the same question, and labels it Today's or Latest question.

## Publishing

GitHub Pages uses **GitHub Actions**, not branch-source publishing, to deploy plain static files from `_site`. Root `CNAME` and `.nojekyll` remain intact. The workflow runs on relevant main-branch pushes, manual dispatch, and at 00:05 London time: 23:05 UTC during BST or 00:05 UTC during GMT. Two UTC schedules plus an offset guard select the appropriate run. GitHub may delay scheduled jobs; this is not an exact-time service. GitHub may disable schedules after 60 days of inactivity on public repositories; weekly question commits prevent that.

Pull requests run `.github/workflows/checks.yml`: the same build, tests (with strict approval checks) and HTML validation, with read-only permissions and no deployment. The publish workflow runs on changes under `content/`, generates, tests, commits every path listed by `python scripts/generate.py --owned` (including new pages and the route lock), then deploys its own artifact. This avoids relying on bot commits to trigger another workflow. Concurrency serialises deployments. No API keys or paid services are required. Future authoring data and internal drafts/screenshots are excluded from the deployment package.

## Newsletter

All signup forms retain native POST to `https://buttondown.com/api/emails/embed-subscribe/sqedaily`, field `email`, hidden `embed=1`. Do not use a public API key or fake success handler. Buttondown handles validation/CAPTCHA/server errors and double opt-in. Saved redirects:

- After signup: `https://sqedaily.co.uk/?subscription=pending#daily-email`
- After confirmation: `https://sqedaily.co.uk/?subscription=confirmed#daily-email`

The site shows the relevant confirmation message, strips personal redirect parameters, and scrolls after the question loads. Forms do not schedule or send daily newsletter campaigns. Custom automatic confirmation/welcome copy is not active on the Free plan; existing unsent Buttondown drafts remain unchanged.

## Analytics and Search Console

Set the **public beacon token** in `assets/config.js` under `cloudflareAnalyticsToken`. Empty means no analytics script or requests. Do not paste a Cloudflare API key. Only the cookie-free Cloudflare Web Analytics beacon is supported; no other trackers or cookie banner were added. After enabling analytics, update the Privacy wording that currently says it is disabled.

Google Search Console is verified as a Domain property by DNS TXT record, so no meta tag is needed. Submit https://sqedaily.co.uk/sitemap.xml there by hand. Bing Webmaster Tools can import the site from Search Console; only if that fails to verify, set `BING_VERIFICATION` in `scripts/generate.py`. Sitemap `lastmod` appears only where a publication date or `last_modified` backs it. Structured data names the Organization "SQE Daily" as author and publisher; never add a Person.

## Fonts and checks

The three existing OFL fonts are Latin-subset WOFF2 files, with regular DM Sans and Newsreader preloaded. Original fonts and OFL licence files are retained. To reconvert, install `fonttools[woff]` in a temporary environment and use `pyftsubset` with `--flavor=woff2 --unicodes=U+0000-00FF,U+0100-024F,U+2000-206F,U+2190-21FF --layout-features='*'`.

`scripts/test_site.py` checks all deployed internal links/fragments, unique ids, one h1 per page, unique titles and descriptions, JSON-LD (Organization author, no Person), published-only data, RSS, sitemap coverage and lastmod rules, locked routes, the approval gate and that every generated file is packaged. It appends a future fixture in a temporary checkout, verifies exclusion and removes the whole fixture checkout automatically; it also tests the full current question bank at a simulated later date. `scripts/test_dates.cjs` checks selection and BST/GMT boundaries. `scripts/test_answers.cjs` exercises every A-E choice for every question using the production renderer and answer handler, checking markers, accessible labels, result state, repeat submissions and resets after corrections. It uses a DOM fixture, not a browser; responsive and keyboard checks still need a real browser. HTML can be checked using `npx html-validate '_site/**/*.html'`; `.htmlvalidate.json` permits descriptive long question titles. The website itself needs neither Node nor npm.

Cloudflare DNS, HTTPS, email forwarding and Buttondown account settings are unchanged. The supplied legal questions have not received a new legal accuracy audit.
