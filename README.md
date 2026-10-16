# SQE Daily

Free, independent SQE1 practice: one original question per publishing day, five options, a worked answer and a primary-source link. Static HTML, CSS and vanilla JavaScript, hosted on GitHub Pages at https://sqedaily.co.uk.

## Run locally

Python 3.9+ (with Europe/London timezone data) is required. No Python packages or website runtime dependencies are needed.

```sh
python3 scripts/generate.py --package
python3 scripts/test_site.py
node scripts/test_dates.cjs
python3 -m http.server 8766 --directory _site
```

Open http://localhost:8766. Serve `_site`, not the repository root, to preview the exact deployed package. `--date YYYY-MM-DD` is available for generator testing; do not deploy a future-date preview.

## Add questions

Append valid objects to `content/questions.json`; keep all existing field names. Each question needs a unique id and integer number, ISO publish_date, subject, FLK1/FLK2, difficulty, title, scenario, stem, five A–E options, answer, explanation, key_rule, authority and verified HTTPS source URL. The subject must be one of the names in `SUBJECTS` in `scripts/generate.py`; anything else fails the build. Hark edits only `content/questions.json` and `content/pages.json`.

Optional question fields (leave a field out rather than guess):

- `why_wrong`: `{"A": "One-line reason.", ...}` with exactly the four wrong letters. Shown in place of the combined "X is wrong" lines.
- `tags`: 1–5 lowercase topic strings, reused consistently across questions.
- `last_reviewed`: ISO date the question was actually re-checked against its primary source. Shows "Checked against primary source on …". Never in the future.
- `last_modified`: ISO date the visible content genuinely changed after publication. A source check alone is not a modification.

Modification dates are also detected automatically: the route lock stores a hash of each published question's visible content (title, scenario, stem, options, answer, explanation, key rule, authority, source URL, `why_wrong`, subject, paper, difficulty). When a publishing build sees it change, it records that day as the modification date. The later of that date and `last_modified` drives sitemap `lastmod` and `dateModified`. Tags and `last_reviewed` never count as modifications.

### Page copy and approval

`content/pages.json` (optional) holds `sittings`, `pages` and `subjects`. Every entry has `approved: false` until the owner approves the copy in chat. Then record the approval with `python3 scripts/generate.py --approve pages.editorial-standards` (or `sittings.0`, `subjects.Contract`). This sets `approved: true` and an `approved_hash` of the exact approved text. Editing the entry afterwards withdraws its approval: the page is not published, and an edited sitting stops driving the countdown, until it is approved again. Pull-request checks fail on such stale approvals. Approved subject introductions render from PR 2, and their changes will then also record modification dates. Built pages in this release: `sqe1-exam-dates` and `editorial-standards`. Copy is plain text: blank lines separate paragraphs and links are `[text](https://...)`. No HTML, names or credentials. Approved sittings drive the homepage countdown; until one is approved the existing January 2027 dates remain.

### Permanent URLs

`content/routes.lock.json` is generator-owned; never edit it by hand. A question's URL is fixed the first time it is published, so editing a published title changes its title and heading but never its URL, share link, sitemap or RSS entry. The build fails if a lock entry would move an already-published page or a subject slug differs. Previews with `--date` never write the lock.

The home question is the newest question whose publish_date is no later than today's Europe/London date; ties use the highest number. If there is no question today, the latest past question remains available. Nothing future-dated is rendered or included in the deployed JSON, sitemap or RSS. The full authoring bank remains in the public GitHub repository, so scheduled questions are not confidential there.

`scripts/generate.py` rebuilds question pages at their locked `/q/<number>-<title-slug>/` URLs, the server-rendered homepage, the main and subject archives, About, Sponsor, Privacy, approved pages from `content/pages.json`, 404, sitemap and RSS. Generated pages should not be edited by hand. Home layout source is `scripts/templates/home.html`; shared styles and interactions are in `assets/`. The homepage HTML contains the latest question, its permanent link and recent questions; JavaScript still refreshes it at London midnight, keeps checking every 5 minutes until that day's question is live (scheduled publishing can run late), picks up corrections to the same question, and labels it Today's or Latest question.

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

`scripts/test_site.py` checks all deployed internal links/fragments, unique ids, one h1 per page, unique titles and descriptions, JSON-LD (Organization author, no Person), published-only data, RSS, sitemap coverage and lastmod rules, locked routes, the approval gate and that every generated file is packaged. It appends a future fixture in a temporary checkout, verifies exclusion and removes the whole fixture checkout automatically; it also tests the full 14-question bank at a simulated later date. `scripts/test_dates.cjs` checks selection and BST/GMT boundaries. HTML can be checked using `npx html-validate '_site/**/*.html'`; `.htmlvalidate.json` permits descriptive long question titles. The website itself needs neither Node nor npm.

Cloudflare DNS, HTTPS, email forwarding and Buttondown account settings are unchanged. The supplied legal questions have not received a new legal accuracy audit.
