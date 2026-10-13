# SQE Daily

A fast, mobile-first landing page with one free SQE1 question per day, instant answer feedback, the complete worked explanation and a linked primary source. Plain HTML, CSS and JavaScript. No build step, dependencies, trackers or accounts.

## Run locally

From this folder:

```sh
python3 -m http.server 8765
```

Open http://localhost:8765. Use a local HTTP server rather than opening index.html directly, because the question data is loaded with fetch.

## Publish with GitHub Pages

Put the contents of this folder at your repository root on the main branch. In GitHub, open Settings > Pages, choose Deploy from a branch, select main and / (root), then Save. The empty .nojekyll file is included. CNAME sets the custom domain to sqedaily.co.uk.

The repository is https://github.com/adnanali287/sqe-daily. The custom domain is https://sqedaily.co.uk/. The original GitHub Pages address is https://adnanali287.github.io/sqe-daily/.

All asset and data paths work at the custom domain root and under a GitHub Pages repository subpath. The sharing tags and canonical URL point to sqedaily.co.uk. assets/social.png is the social sharing image; assets/social.svg is its editable source.

Cloudflare manages DNS. The apex uses GitHub Pages' four A records (185.199.108.153 through 185.199.111.153); www is a CNAME to adnanali287.github.io. Use DNS-only records so GitHub can validate the domain and provision its HTTPS certificate.

## Question rotation

content/questions.json contains the supplied 14 questions, unchanged. The page uses the Europe/London calendar date and rotates the list in number order, anchored to q001's publish_date (13 October 2026). q014 is followed by q001. An open tab refreshes the question after midnight. The countdown targets 11 January 2027 and never goes negative. Update the sitting dates for a later exam cycle.

## Email preview

The form POSTs JSON with an email field to ./api/subscribe, a placeholder endpoint. GitHub Pages cannot handle that POST, so the preview shows a friendly confirmation that explicitly says the visitor has not been subscribed. It stores no addresses. Replace the form action and the submit handler in assets/app.js with your Buttondown integration, and show a real subscription confirmation only after a successful response. No API keys belong in this static site.

## Design and review

DESIGN_PLAN.md records the direction, tokens, critique and two screenshot refinement loops. screenshots/ contains final full-page captures at 1440px and 390px, before and after answering. The original SVG brand mark and favicon are in assets/. Newsreader and DM Sans are self-hosted; their SIL Open Font License files are included.

The questions and legal explanations are supplied content, not a new legal accuracy audit. Review the bank as law and exam requirements change.

Browser verification passed for all 14 questions, with correct and incorrect answers at 1440px, 390px and 320px; keyboard activation, date rotation and midnight rollover, countdown, failed-load retry, email validation and placeholder POST, reduced motion, and no horizontal overflow. Two visual review loops were completed before final capture.
