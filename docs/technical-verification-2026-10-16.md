# Technical verification, 16 October 2026

Reviewed current main at `0334e2a`, following the content and editorial merges
`fa42623` and `616e44c`. No editorial copy, questions, approval hashes, design,
newsletter settings or DNS was changed in this technical pass.

## Answer-marker report

The reported extra tick on option E was not reproduced on the live homepage or
the permanent question page. For question 04, choosing A marks only A correct;
choosing E marks A correct and E incorrect. The separate result-heading icon is
outside the options container and is not an additional answer marker.

All four published question pages passed Space-key activation checks at actual
390px and 1440px viewport widths, with exactly one correct marker and no horizontal
overflow. An early keyboard attempt before page load finished did not activate an
answer; checks were repeated after the load event. No keyboard behaviour change
is claimed or made.

Added `scripts/test_answers.cjs` to PR and publishing checks. It exercises the
actual production renderer and answer handler with a small DOM fixture: all 245
choices across 49 questions, correct/incorrect symbols and classes, accessible
labels, result state, repeat-answer guard, render resets and a same-ID answer
correction from E to A. This is unit coverage, not a replacement for browser tests.

## Live technical SEO crawl

- All 21 sitemap URLs returned HTTP 200, had exactly one h1, a non-empty meta
  description, and one self-referencing canonical URL.
- No sitemap page had a noindex meta tag or X-Robots-Tag header.
- Internal page links from those pages resolve to URLs represented in the sitemap.
- `robots.txt` allows crawling and names the correct HTTPS sitemap.
- Deployed question JSON contains only the four published questions. The first
  and last future-question routes were checked and returned HTTP 404.
- Future questions remain visible in the public GitHub authoring repository;
  website exclusion is not repository privacy.

## Local checks

- `python3 scripts/generate.py --package`
- `STRICT_APPROVALS=1 python3 scripts/test_site.py`
- `node scripts/test_dates.cjs`
- `node scripts/test_answers.cjs`
- `npx --yes html-validate@11.16.2 '_site/**/*.html'`

All passed. Site checks include the full 49-question bank at its last scheduled
date, approval invalidation/re-approval, permanent URLs and future exclusion.

## Search and remaining limits

See `docs/measurement-baseline.md` for the actual Search Console observations.
The sitemap was submitted successfully; Google indexing is a separate process.
No real signup or subscriber email was triggered. No new legal-content audit,
outreach, analytics installation, DNS changes, history rewrite or automation was
performed. Hark retains responsibility for content and newsletter operations.
