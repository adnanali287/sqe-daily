"""Generate SQE Daily's static pages using only Python's standard library."""
import argparse
import hashlib
import html
import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://sqedaily.co.uk'
NAV = '<nav aria-label="Main navigation">' + ''.join(f'<a href="{url}">{name}</a>' for name, url in [('Today', '/'), ('Archive', '/archive/'), ('About', '/about/'), ('Sponsor', '/sponsor/'), ('Privacy', '/privacy/')]) + '</nav>'
esc = lambda value: html.escape(str(value), quote=True)

def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')

def route(q):
    return f'/q/{q["number"]}-{slug(q["title"])}/'

def published(bank, day):
    return sorted((q for q in bank if q['publish_date'] <= day), key=lambda q: (q['publish_date'], q['number']))

def write(path, content):
    target = ROOT / path.lstrip('/')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.suffix == '.html':
        for name in ['app.js', 'site.js', 'config.js', 'styles.css']:
            version = hashlib.sha256((ROOT / 'assets' / name).read_bytes()).hexdigest()[:12]
            content = re.sub(r'((?:src|href)="/assets/' + re.escape(name) + r')(?:\?[^" ]*)?"', rf'\1?v={version}"', content)
    target.write_text('\n'.join(line.rstrip() for line in content.splitlines()) + '\n', encoding='utf-8')

def generate(day, package=False):
    bank = json.loads((ROOT / 'content/questions.json').read_text())
    ids, numbers, paths = set(), set(), set()
    for q in bank:
        for field in ['id', 'number', 'publish_date', 'subject', 'flk', 'difficulty', 'title', 'scenario', 'stem', 'options', 'answer', 'explanation', 'key_rule', 'authority', 'verified_source_url']:
            if field not in q:
                raise ValueError(f'Missing {field}: {q.get("id")}')
        datetime.strptime(q['publish_date'], '%Y-%m-%d')
        if q['id'] in ids or q['number'] in numbers or route(q) in paths:
            raise ValueError('Duplicate question id, number or route')
        if q['flk'] not in ['FLK1', 'FLK2'] or q['answer'] not in 'ABCDE' or set(q['options']) != set('ABCDE') or not q['verified_source_url'].startswith('https://'):
            raise ValueError(f'Invalid question: {q["id"]}')
        ids.add(q['id']); numbers.add(q['number']); paths.add(route(q))
    questions = published(bank, day)
    template = (ROOT / 'scripts/templates/home.html').read_text()
    template = template.replace('class="countdown" aria-label=', 'class="countdown" role="group" aria-label=')
    template = template.replace('id="result-heading" tabindex="-1"></h3>', 'id="result-heading" tabindex="-1">Worked answer</h3>')
    newsletter = template.split('    <section class="email-band"')[1].split('    <section class="how-band')[0]
    newsletter = '    <section class="email-band"' + newsletter
    footer = '<footer class="wrap"><a class="footer-brand" href="/">SQE Daily.</a>' + NAV.replace('Main navigation', 'Footer navigation') + '<p>Independent. Not affiliated with the SRA or any training provider.<br>For revision only. Not legal advice.</p><a href="mailto:hello@sqedaily.co.uk">Say hello</a></footer>'
    header = '<a class="skip-link" href="#main">Skip to content</a><header class="masthead wrap"><a class="brand" href="/" aria-label="SQE Daily home"><img src="/assets/mark.svg" width="52" height="52" alt=""><span class="brand-name">SQE Daily<span class="brand-dot">.</span></span></a>' + NAV + '</header>'
    extras = '''<!-- Google Search Console: insert verification meta tag here. -->
<link rel="alternate" type="application/rss+xml" title="SQE Daily" href="https://sqedaily.co.uk/feed.xml">
<link rel="preload" href="/assets/dm-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/newsreader.woff2" as="font" type="font/woff2" crossorigin>
<script src="/assets/config.js" defer></script><script src="/assets/site.js" defer></script>'''

    def page(path, title, description, body, schema=None):
        structured = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c') + '</script>' if schema else ''
        description = re.sub('<[^>]+>', '', description)
        write(path + 'index.html', f'''<!DOCTYPE html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#142f2b"><title>{esc(title)} | SQE Daily</title><meta name="description" content="{esc(description)}"><link rel="canonical" href="{BASE}{path}"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} | SQE Daily"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{BASE}{path}"><meta property="og:image" content="{BASE}/assets/social.png"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/styles.css">{extras}{structured}</head><body>{header}<main id="main">{body}</main>{footer}</body></html>''')

    # Rebuild only generator-owned directories, removing stale scheduled pages.
    for directory in ['q', 'archive']:
        if (ROOT / directory).exists():
            shutil.rmtree(ROOT / directory)
        (ROOT / directory).mkdir()
    practice = template.split('    <section class="practice-band"')[1].split('    <section class="email-band"')[0]
    practice = '    <section class="practice-band"' + practice
    practice = re.sub(r'<div id="load-state".*?</noscript>', '', practice, flags=re.S)
    practice = practice.replace('id="practice-content" hidden', 'id="practice-content"')
    practice = practice.replace("Today's question", 'Daily practice')
    practice = practice.replace('id="question"', 'id="question" data-static-question')
    question_urls = []
    for i, q in enumerate(questions):
        body = practice
        body = body.replace('<h2 id="practice-heading">Daily practice</h2>', f'<h1 id="practice-heading">{esc(q["title"])}</h1>')
        values = {**q, 'question-number': str(q['number']).zfill(2), 'difficulty': q['difficulty'].capitalize()}
        for key in ['scenario', 'stem', 'subject', 'flk', 'difficulty', 'question-number']:
            body = body.replace(f'id="{key}"></', f'id="{key}">{esc(values[key])}</')
        body = body.replace('<time id="today"></time>', f'<time datetime="{q["publish_date"]}">{q["publish_date"]}</time>')
        options = ''.join(f'<button type="button" class="option" data-letter="{letter}" aria-label="{letter}. {esc(text)}"><span class="option-letter" aria-hidden="true">{letter}</span><span class="option-text">{esc(text)}</span><span class="option-symbol" aria-hidden="true"></span></button>' for letter, text in q['options'].items())
        body = body.replace('aria-labelledby="stem"></div>', f'aria-labelledby="stem">{options}</div>')
        body = body.replace('id="correct-answer" class="correct-answer"></p>', f'id="correct-answer" class="correct-answer">Correct answer {q["answer"]}: {esc(q["options"][q["answer"]])}</p>')
        body = body.replace('id="key-rule"></p>', f'id="key-rule">{esc(q["key_rule"])}</p>')
        body = body.replace('id="question-title"></h4>', f'id="question-title">{esc(q["title"])}</h4>')
        explanation = ''.join(f'<p>{esc(p)}</p>' for p in q['explanation'].split('\n\n'))
        body = body.replace('id="explanation" class="explanation"></div>', f'id="explanation" class="explanation">{explanation}</div>')
        body = body.replace('id="authority-link" target=', f'id="authority-link" href="{esc(q["verified_source_url"])}" target=').replace('rel="noopener noreferrer"></a>', f'rel="noopener noreferrer">{esc(q["authority"])}</a>')
        body += '<nav class="wrap question-navigation" aria-label="Question navigation">'
        if i > 0:
            body += f'<a href="{route(questions[i-1])}">← Previous question</a>'
        body += f'<a href="/archive/{slug(q["subject"])}/">{esc(q["subject"])} archive</a>'
        if i + 1 < len(questions):
            body += f'<a href="{route(questions[i+1])}">Next question →</a>'
        body += '</nav><noscript><style>#result[hidden]{display:block!important}</style><p class="wrap">The worked answer is below the options.</p></noscript>'
        payload = json.dumps(q, ensure_ascii=False).replace('<', '\\u003c')
        body += f'<script type="application/json" id="question-data">{payload}</script><script src="/assets/app.js?v=archive-1" defer></script>' + newsletter
        schema = {'@context': 'https://schema.org', '@type': 'Quiz', 'name': q['title'], 'url': BASE + route(q), 'datePublished': q['publish_date'], 'educationalLevel': 'SQE1', 'hasPart': {'@type': 'Question', 'name': q['stem'], 'text': q['scenario'], 'suggestedAnswer': [{'@type': 'Answer', 'text': f'{k}. {v}'} for k, v in q['options'].items()], 'acceptedAnswer': {'@type': 'Answer', 'text': q['options'][q['answer']], 'answerExplanation': q['explanation']}}}
        page(route(q), q['title'], f'Free {q["flk"]} practice: {q["subject"]}. {q["stem"]}', body, schema)
        question_urls.append(route(q))

    subjects = sorted({q['subject'] for q in questions})
    def archive(subject=None):
        selected = [q for q in reversed(questions) if subject is None or q['subject'] == subject]
        title = subject or 'Question archive'
        filters = '<div class="archive-filters" role="group" aria-label="Filter questions" hidden><label>Subject<select id="subject-filter"><option value="">All subjects</option>' + ''.join(f'<option>{esc(s)}</option>' for s in subjects) + '</select></label><label>Paper<select id="flk-filter"><option value="">FLK1 and FLK2</option><option>FLK1</option><option>FLK2</option></select></label></div>'
        links = '<nav class="subject-index" aria-label="Subject archives">' + ''.join(f'<a href="/archive/{slug(s)}/">{esc(s)}</a>' for s in subjects) + '</nav>'
        items = ''.join(f'<li data-subject="{esc(q["subject"])}" data-flk="{q["flk"]}"><div class="archive-meta"><time datetime="{q["publish_date"]}">{q["publish_date"]}</time><span>{esc(q["subject"])} · {q["flk"]}</span><span>No. {q["number"]:02}</span></div><h2><a href="{route(q)}">{esc(q["title"])}</a></h2><p>{esc(q["stem"])}</p></li>' for q in selected)
        return f'<section class="reading wrap"><p class="eyebrow">THE DAILY PRACTICE</p><h1>{esc(title)}</h1><p class="lead">One question. One rule to remember. Browse the published practice.</p>{filters}{links}<ol class="archive-list">{items}</ol><p id="archive-empty" hidden>No questions match these filters.</p></section>' + newsletter
    page('/archive/', 'Question archive', 'Browse published SQE1 questions, worked answers and primary legal sources by subject and paper.', archive())
    for subject in subjects:
        page('/archive/' + slug(subject) + '/', subject + ' questions', f'Free SQE1 practice questions in {subject}, with worked answers and primary sources.', archive(subject))
    copy = {
        'about': ('About SQE Daily', [('A little practice. Every day.', 'SQE Daily is a free site and newsletter for aspiring solicitors preparing for SQE1. One original Single Best Answer question, five options, a worked answer and the legal source. A few minutes of practice, wherever your day takes you.'), ('Written for revision. Checked at the source.', 'Each question is written for SQE Daily and checked against primary sources: legislation and case law. The worked answer explains the correct option, the alternatives and the key rule. Follow the authority link to read the source for yourself.'), ('Independent by design.', 'SQE Daily is provider-neutral, sells no course, and is not affiliated with the SRA or any training provider. It is a revision resource, not legal advice or a substitute for comprehensive exam preparation.'), ('Say hello.', 'Questions, corrections or feedback? Email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a>.')]),
        'sponsor': ('Sponsor SQE Daily', [('Support a daily habit.', 'SQE Daily reaches SQE1 candidates: law students, career changers and paralegals building a daily revision habit, often on their phones between other commitments.'), ('One considered placement.', 'One sponsor slot per daily email and one on the site. Sponsorship keeps the daily question free. SQE Daily remains independent and provider-neutral.'), ('Start a conversation.', 'Media kit on request. Email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a> to discuss a placement. No course is sold by SQE Daily.')]),
        'privacy': ('Privacy', [('Newsletter subscriptions.', 'When you subscribe, your email address is sent to Buttondown, which stores subscriber emails and handles confirmation, delivery and unsubscribe requests. Confirm your address to activate your subscription. Unsubscribe using the link in an email. Read <a href="https://buttondown.com/legal/privacy">Buttondown’s privacy policy</a>.'), ('Website analytics.', 'Cloudflare Web Analytics is configured but disabled until a site token is added. When enabled, it collects cookie-free website usage and performance measurements. We do not add advertising trackers. Read <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare’s privacy policy</a>.'), ('Hosting and links.', 'GitHub Pages hosts this site. Hosting providers may process technical request information to serve and protect their services. Legal-source links take you to external websites, which have their own privacy policies.'), ('Contact and your information.', 'For privacy questions, access or deletion requests, email <a href="mailto:hello@sqedaily.co.uk">hello@sqedaily.co.uk</a>. SQE Daily does not sell your subscriber email address or share it with sponsors.')])}
    for name, (title, sections) in copy.items():
        body = '<section class="reading wrap"><p class="eyebrow">SQE DAILY</p><h1>' + title + '</h1>' + ''.join(f'<section class="reading-section"><h2>{heading}</h2><p>{text}</p></section>' for heading, text in sections) + '</section>'
        page('/' + name + '/', title, sections[0][1], body + (newsletter if name != 'privacy' else ''))
    page('/not-found/', 'Page not found', 'Find today’s free SQE1 question or browse the archive.', '<section class="reading wrap"><p class="eyebrow">404</p><h1>This page has moved on.</h1><p class="lead">There is still a good question waiting.</p><p><a href="/">Today’s question</a> · <a href="/archive/">Browse the archive</a></p></section>')
    shutil.move(ROOT / 'not-found/index.html', ROOT / '404.html'); (ROOT / 'not-found').rmdir()
    home = template.replace('<footer class="wrap">' + template.split('<footer class="wrap">')[1].split('</footer>')[0] + '</footer>', footer)
    home = home.replace('<p class="masthead-note">Independent practice.<br>A daily habit.</p>', NAV)
    home = home.replace('</head>', extras + '</head>').replace('assets/app.js?v=buttondown-2', '/assets/app.js?v=archive-1')
    home = home.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
    if questions:
        current = questions[-1]
        home = home.replace('id="stem"></h3>', f'id="stem">{esc(current["stem"])}</h3>')
        home = home.replace('id="question-title"></h4>', f'id="question-title">{esc(current["title"])}</h4>')
        home = home.replace('id="authority-link" target=', f'id="authority-link" href="{esc(current["verified_source_url"])}" target=')
    else:
        home = home.replace('id="stem"></h3>', 'id="stem">Daily practice</h3>').replace('id="question-title"></h4>', 'id="question-title">Explanation</h4>').replace('id="authority-link" target=', 'id="authority-link" href="/archive/" target=')
    write('index.html', home)
    urls = ['/', '/archive/', '/about/', '/sponsor/', '/privacy/'] + ['/archive/' + slug(s) + '/' for s in subjects] + question_urls
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for url in urls:
        item = ET.SubElement(sitemap, 'url'); ET.SubElement(item, 'loc').text = BASE + url
    write('sitemap.xml', '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(sitemap, encoding='unicode'))
    rss = ET.Element('rss', version='2.0'); channel = ET.SubElement(rss, 'channel')
    for tag, value in [('title', 'SQE Daily'), ('link', BASE), ('description', 'One free SQE1 practice question every day, with a worked answer and the legal source.'), ('language', 'en-gb')]:
        ET.SubElement(channel, tag).text = value
    for q in reversed(questions):
        item = ET.SubElement(channel, 'item')
        for tag, value in [('title', q['title']), ('link', BASE + route(q)), ('guid', BASE + route(q)), ('description', q['scenario'] + '\n\n' + q['stem']), ('pubDate', datetime.fromisoformat(q['publish_date']).strftime('%a, %d %b %Y 00:00:00 +0000'))]:
            ET.SubElement(item, tag).text = value
    write('feed.xml', '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding='unicode'))
    write('robots.txt', f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n')
    if package:
        public = ROOT / '_site'
        if public.exists(): shutil.rmtree(public)
        public.mkdir()
        for name in ['index.html', '404.html', 'CNAME', '.nojekyll', 'robots.txt', 'sitemap.xml', 'feed.xml', 'assets', 'q', 'archive', 'about', 'sponsor', 'privacy']:
            source = ROOT / name
            if source.is_dir(): shutil.copytree(source, public / name)
            else: shutil.copy2(source, public / name)
        (public / 'content').mkdir()
        (public / 'content/questions.json').write_text(json.dumps(questions, ensure_ascii=False, indent=2) + '\n')
    print(f'Generated {len(questions)} published questions for {day}.')
    return questions

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=datetime.now(ZoneInfo('Europe/London')).date().isoformat())
    parser.add_argument('--package', action='store_true')
    args = parser.parse_args()
    datetime.strptime(args.date, '%Y-%m-%d')
    generate(args.date, args.package)
