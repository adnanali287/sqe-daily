# Measurement baseline

Recorded 16 October 2026. Only measurements actually taken are recorded here; nothing is estimated.

## Lighthouse (measured)

- **How it was run:** Lighthouse 12 (mobile emulation, default throttling) in headless Chromium, against local builds served from `_site`.
- **Why local:** the live site (sqedaily.co.uk) and the PageSpeed Insights API could not be reached from the build environment. The proxy refused the connection, and the API returned HTTP 429.
- **What that means:** these scores describe the generated pages, not live field data.

| Page (build) | Performance | Accessibility | Best practices | SEO | LCP | CLS | TBT |
|---|---|---|---|---|---|---|---|
| Home, before PR #1 (`06235f5`) | 95 | 100 | 100 | 100 | n/r | n/r | n/r |
| Question page, before PR #1 | 100 | 98 | 100 | 100 | n/r | n/r | n/r |
| Home, this PR (current content) | 99 | 100 | 100 | 100 | 1.8 s | 0 | 70 ms |
| Question page, this PR | 100 | 100 | 100 | 100 | 1.7 s | 0 | 0 ms |
| Archive, this PR | 100 | 100 | 100 | 100 | 1.5 s | 0 | 0 ms |
| `/sqe1-practice-questions/` (approved preview) | 100 | 100 | 100 | 100 | 1.5 s | 0 | 0 ms |
| `/flk1/` (approved preview) | 100 | 100 | 100 | 100 | 1.5 s | 0 | 0 ms |
| `/sqe1-exam-dates/` (approved preview) | 100 | 100 | 100 | 100 | 1.5 s | 0 | 0 ms |
| Guide: single best answer (approved preview) | 100 | 100 | 100 | 100 | 1.5 s | 0 | 0 ms |
| Subject page with introduction: Contract (approved preview) | 100 | 100 | 100 | 100 | 1.5 s | 0 | 0 ms |
| Question page with related questions (approved preview) | 100 | 100 | 100 | 100 | 1.7 s | 0 | 0 ms |

"n/r" means the metric was not recorded for that run.

Local scores vary by a point or two between runs.

## Search Console: verified update, 16 October 2026

The earlier access limitation below is historical. Codex accessed the verified
`sqedaily.co.uk` Domain property through the owner's signed-in browser:

- Submitted `https://sqedaily.co.uk/sitemap.xml`. Google reported **Success**,
  last read 16 October 2026, with **21 discovered pages** and zero videos.
- Search results, **Web**, selected **3 months**: zero clicks, zero impressions,
  CTR displayed as 0%. The chart currently covers 13-14 October 2026 only.
  Average position displays 0, but with no impressions it is not a meaningful
  ranking measurement. The Queries table has no data.
- Page indexing: **Processing data, please check again in a day or so**.
  Indexed/excluded counts and exclusion reasons are not available yet.
- The overview reports no experience data yet. No field Core Web Vitals scores
  are claimed.
- Stored homepage URL Inspection: **URL is not on Google**, **URL is unknown
  to Google**, no recorded last crawl. This is the stored index result, not a
  failure of the live HTTP request or evidence that the sitemap submission failed.

Discovered pages are not necessarily indexed. Recheck Page indexing and URL
Inspection after Google processes the submission. No search ranking or traffic
improvement is claimed from these early figures.

## Search Console: earlier handover instructions

No Search Console data could be read: there is no Search Console connector or account access in this environment. **Nothing below has been filled in, and nothing should be assumed.**

Owner, please export these from the `sqedaily.co.uk` Domain property:

1. **Performance → Search results**, last 3 months, all search types:
   - Total clicks, total impressions, average CTR and average position.
   - The **Queries** table and the **Pages** table (Export → CSV).
2. **Indexing → Pages**: the counts of indexed and not indexed pages, and the reasons listed under "Why pages aren't indexed".
3. **Sitemaps**: the status and discovered-URL count for `https://sqedaily.co.uk/sitemap.xml` (submit it first if it isn't listed).
4. **Core Web Vitals** (mobile and desktop): the status. It may say "not enough data" for a new site, and that is a valid baseline.

Paste the figures, or attach the CSVs, in chat and they will be recorded here with the export date.

## Live PageSpeed (owner action, optional)

Run https://pagespeed.web.dev/ on `https://sqedaily.co.uk/` and on one question URL. Record the mobile scores and the "Discover what your real users are experiencing" field data, if any.

## Newsletter (separate indicator)

Buttondown subscriber totals are tracked separately from search. Aggregate signups are **not** attributed to organic search, because there is no analytics to connect them. Record the total confirmed subscribers from the Buttondown dashboard on the same date as each Search Console export.

## Analytics

Cloudflare Web Analytics stays off until the public beacon token is supplied (`assets/config.js`). No other analytics are used.

## Tracking cadence

Record one entry per month (see backlog item 2.5), using the same exports, so the figures are comparable.
