# SQE Daily implementation handover

## Scope and hosting

Implemented the user's complete static-publishing brief, starting from an up-to-date main branch in adnanali287/sqe-daily. The approved paper/mint/ink/red visual language, self-hosted Newsreader and DM Sans, original mark and social image are retained. The site remains plain HTML/CSS/vanilla JS with no server, database, paid service or framework runtime.

GitHub Pages now publishes through `.github/workflows/publish.yml` rather than legacy branch-source builds. The repository remains main/root for source and generated pages; `_site` is the filtered deployment artifact. The root CNAME and .nojekyll are preserved. The custom domain, approved certificate and enforced HTTPS were verified. No Cloudflare DNS or email settings were changed.

## Implemented features

1. Per-question static pages at `/q/<number>-<title-slug>/`, with scenario, five keyboard-accessible options, correct/incorrect feedback, full explanation, key rule and authority link. Question content is in HTML before JS runs. Without JS, the worked answer is visible. Pages have unique title/description/canonical/OG metadata and Quiz/Question JSON-LD. Published-only previous/next links and subject archives are generated. All use the shared newsletter form.
2. `/archive/` newest first, subject archive pages, and optional accessible subject/paper select filters. Without JS the lists and subject links remain usable. Future-only subjects are not exposed.
3. Standard-library Python generator in `scripts/generate.py`. It reads the unchanged authoring bank, validates required fields/dates/identifiers, rebuilds generator-owned question/archive directories, and writes supporting pages, XML sitemap and RSS. Script/style URLs use content hashes to avoid stale browser caches.
4. Home selection now chooses an exact London publication date or latest past question, never a future question. Latest-past fallback is labelled Latest question and displays its actual publication date. Fetch revalidates the public JSON.
5. Workflow triggers on main pushes affecting questions/templates/assets/publishing configuration, manual dispatch, and two UTC cron candidates: 23:05 in BST or 00:05 in GMT. A London offset guard chooses the correct scheduled run. It generates, checks, commits output, then deploys its own artifact. Bot commits need not trigger a second workflow. GitHub may delay scheduled jobs and disable idle public-repository schedules after 60 days.
6. Deployment allowlist excludes internal source/scripts/drafts/screenshots. Its `content/questions.json` is generated from the authoring bank but contains only published questions. The complete bank remains the single source of truth in the public GitHub repository; future questions are not confidential in that repository.
7. Sitemap, robots.txt, RSS alternate links, shared OG image, styled/noindex 404 and a marked empty Search Console verification location in the shared head.
8. Cookie-free Cloudflare Analytics support via the single public-token value `cloudflareAnalyticsToken` in `assets/config.js`. Empty by default: no beacon script loads. No other analytics were added.
9. All three fonts converted to Latin-subset WOFF2, with Latin punctuation and arrows retained; originals and OFL licences retained. Regular DM Sans and Newsreader are preloaded. Font payload fell from 206,032 to 61,036 bytes, about 70% smaller.
10. Answer-only Share control: Web Share API when available, clipboard fallback otherwise, manual link if browser permissions prevent sharing/copying. Share content never includes the answer. Each question uses its permanent URL.
11. About, Sponsor and Privacy pages. Sponsor page describes one slot per daily email and site, audience and media kit on request, with no prices. Privacy describes Buttondown, optional cookie-free analytics, hosting, external links and contact. Consistent Today/Archive/About/Sponsor/Privacy header/footer links and independence/non-advice disclaimer.

## Newsletter preservation and live checks

The native Buttondown endpoint, email field, hidden embed=1 and double opt-in remain intact. No Buttondown API key was required or added. Existing redirects and account settings were not changed. A live submission from the new archive page using the user's existing Yahoo subscription returned to the site's confirmed-subscription message. This did not create or delete a disposable new subscriber. Previous custom email drafts and paid-plan limitations are unchanged. Daily newsletter sending is still not automated by this website build.

## Verification

- Generator and test suite passed locally and in the successful GitHub Actions deployment.
- All currently deployed HTML passed html-validate 11.16.2. Descriptive long question titles are intentionally allowed; validation rules otherwise remain enabled.
- Every internal deployed link/fragment, unique id, main heading, published data date, sitemap question URL and RSS XML checked automatically.
- Appended a clearly marked future question in a temporary checkout, verified it absent from all deployed HTML/JSON/XML, then automatically removed the temporary checkout. The real authoring bank was never changed.
- Simulated 1 November 2026 to exercise all 14 original questions: 33 generated HTML pages, including subject archives and previous/next links, passed structural/link tests.
- JavaScript tests cover exact date, latest past, no past question and BST/GMT boundaries; fixtures are independent of future additions to the real bank.
- Desktop 1440px and mobile 390px screenshots updated. Checked correct and incorrect answer states, keyboard activation, archive filtering and lack of horizontal overflow at those sizes.
- Verified each live sitemap page returned HTTPS 200, live JSON contained only q001 for 13 October 2026, and a missing URL returned HTTP 404 with the custom design.
- Invoked the Share control in the browser, but did not send a share to another person. Native sharing across actual phone platforms remains device-dependent.
- Requested a mobile Lighthouse audit through Google's PageSpeed API; it returned HTTP 429. No measured 95+ score is claimed. Real phone testing and a later Lighthouse run remain useful.

## Owner actions

Paste the public Cloudflare Web Analytics beacon token into `assets/config.js` when ready, and update Privacy wording from disabled to enabled. Do not paste a Cloudflare or Buttondown API key. Add a Search Console verification meta tag at the generator's shared-head comment, regenerate, then submit the sitemap. Hark only needs to append questions to `content/questions.json` and push; no other file requires editing. Keep published titles stable because they determine URLs. Review Privacy for the final operator details before launch. No legal accuracy audit of the question bank was performed.
