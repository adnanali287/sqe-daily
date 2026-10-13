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

Append valid objects to `content/questions.json`; keep all existing field names. Each question needs a unique id and integer number, ISO publish_date, subject, FLK1/FLK2, difficulty, title, scenario, stem, five A–E options, answer, explanation, key_rule, authority and verified HTTPS source URL. No other file needs editing. Hark can continue committing only this file.

The home question is the newest question whose publish_date is no later than today's Europe/London date; ties use the highest number. If there is no question today, the latest past question remains available. Nothing future-dated is rendered or included in the deployed JSON, sitemap or RSS. The full authoring bank remains in the public GitHub repository, so scheduled questions are not confidential there.

`scripts/generate.py` rebuilds question URLs `/q/<number>-<title-slug>/`, the main and subject archives, About, Sponsor, Privacy, 404, sitemap and RSS. Generated pages should not be edited by hand. Home layout source is `scripts/templates/home.html`; shared styles and interactions are in `assets/`. Changing a published title changes its URL, so keep published titles stable.

## Publishing

GitHub Pages uses **GitHub Actions**, not branch-source publishing, to deploy plain static files from `_site`. Root `CNAME` and `.nojekyll` remain intact. The workflow runs on relevant main-branch pushes, manual dispatch, and at 00:05 London time: 23:05 UTC during BST or 00:05 UTC during GMT. Two UTC schedules plus an offset guard select the appropriate run. GitHub may delay scheduled jobs; this is not an exact-time service. GitHub may disable schedules after 60 days of inactivity on public repositories; weekly question commits prevent that.

The workflow generates, tests, commits generated pages, then deploys its own artifact. This avoids relying on bot commits to trigger another workflow. Concurrency serialises deployments. No API keys or paid services are required. Future authoring data and internal drafts/screenshots are excluded from the deployment package.

## Newsletter

All signup forms retain native POST to `https://buttondown.com/api/emails/embed-subscribe/sqedaily`, field `email`, hidden `embed=1`. Do not use a public API key or fake success handler. Buttondown handles validation/CAPTCHA/server errors and double opt-in. Saved redirects:

- After signup: `https://sqedaily.co.uk/?subscription=pending#daily-email`
- After confirmation: `https://sqedaily.co.uk/?subscription=confirmed#daily-email`

The site shows the relevant confirmation message, strips personal redirect parameters, and scrolls after the question loads. Forms do not schedule or send daily newsletter campaigns. Custom automatic confirmation/welcome copy is not active on the Free plan; existing unsent Buttondown drafts remain unchanged.

## Analytics and Search Console

Set the **public beacon token** in `assets/config.js` under `cloudflareAnalyticsToken`. Empty means no analytics script or requests. Do not paste a Cloudflare API key. Only the cookie-free Cloudflare Web Analytics beacon is supported; no other trackers or cookie banner were added. After enabling analytics, update the Privacy wording that currently says it is disabled.

Insert the Google Search Console verification meta tag at the marked head location in `scripts/generate.py` (shared pages) and regenerate. Submit https://sqedaily.co.uk/sitemap.xml to Search Console. Verification is intentionally not configured yet.

## Fonts and checks

The three existing OFL fonts are Latin-subset WOFF2 files, with regular DM Sans and Newsreader preloaded. Original fonts and OFL licence files are retained. To reconvert, install `fonttools[woff]` in a temporary environment and use `pyftsubset` with `--flavor=woff2 --unicodes=U+0000-00FF,U+0100-024F,U+2000-206F,U+2190-21FF --layout-features='*'`.

`scripts/test_site.py` checks all deployed internal links/fragments, unique ids, h1s, published-only data, RSS and sitemap coverage. It appends a future fixture in a temporary checkout, verifies exclusion and removes the whole fixture checkout automatically; it also tests the full 14-question bank at a simulated later date. `scripts/test_dates.cjs` checks selection and BST/GMT boundaries. HTML can be checked using `npx html-validate '_site/**/*.html'`; `.htmlvalidate.json` permits descriptive long question titles. The website itself needs neither Node nor npm.

Cloudflare DNS, HTTPS, email forwarding and Buttondown account settings are unchanged. The supplied legal questions have not received a new legal accuracy audit.
