const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

// Runs the whole of assets/app.js as the homepage does: embedded question first,
// then quiet refreshes from /content/latest.json, with a fake clock, DOM and network.
class Element {
  constructor(id = '') {
    this.id = id;
    this.children = [];
    this.dataset = {};
    this.attributes = {};
    this.listeners = {};
    this.textContent = '';
    this.className = '';
    this.hidden = false;
    this.disabled = false;
    this.classList = { add: name => { this.className += ` ${name}`; } };
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener(type, fn) { (this.listeners[type] ||= []).push(fn); }
  click() { (this.listeners.click || []).forEach(fn => fn()); }
  remove() { if (this.id) delete this.owner?.[this.id]; }
  focus() {}
  scrollIntoView() {}
  querySelector(selector) {
    return this.children.find(child => child.className.split(' ').includes(selector.slice(1)));
  }
}

const bank = JSON.parse(fs.readFileSync('content/questions.json', 'utf8')).filter(q => q.publish_date).slice(0, 2);
const withRoute = q => ({ ...q, route: `/q/${q.number}-fixture/`, available_from: q.publish_date });
const [current, next] = bank.map(withRoute);
// London midnight at the start of `next`'s feature day, plus or minus a few minutes.
const midnight = Date.parse(`${next.publish_date}T00:00:00+01:00`);
const MINUTE = 60000;

function serverOptions(q) {
  const options = new Element('options');
  for (const letter of ['A', 'B', 'C', 'D', 'E']) {
    const button = new Element();
    button.className = 'option';
    button.dataset.letter = letter;
    ['option-letter', 'option-text', 'option-symbol'].forEach((className, index) => {
      const span = new Element();
      span.className = className;
      span.textContent = index === 0 ? letter : index === 1 ? q.options[letter] : '';
      button.append(span);
    });
    options.append(button);
  }
  return options;
}

async function settle() {
  for (let i = 0; i < 10; i++) await new Promise(resolve => setImmediate(resolve));
}

// responses: an array consumed in order; each is a function returning a fetch result or throwing.
async function boot({ now, embedded = current, responses }) {
  const clock = { now };
  const nodes = {};
  const element = id => {
    if (!(id in nodes)) { nodes[id] = new Element(id); nodes[id].owner = nodes; }
    return nodes[id];
  };
  if (embedded) {
    nodes['home-question-data'] = new Element('home-question-data');
    nodes['home-question-data'].textContent = JSON.stringify(embedded);
    nodes.options = serverOptions(embedded);
    nodes.result = new Element('result');
    nodes.result.hidden = true;
  }
  const requests = [];
  const intervals = [];
  const documentListeners = {};
  class FakeDate extends Date {
    constructor(...args) { if (args.length) super(...args); else super(clock.now); }
    static now() { return clock.now; }
  }
  const context = vm.createContext({
    Intl, JSON, Object, Array, Promise, Error, Number, String, Boolean, encodeURIComponent, URLSearchParams,
    Date: FakeDate,
    location: { search: '', pathname: '/' },
    history: { replaceState() {} },
    matchMedia: () => ({ matches: true }),
    navigator: {},
    setInterval: fn => { intervals.push(fn); return intervals.length; },
    fetch: async (url, options) => {
      requests.push({ url, options });
      const next = responses.shift();
      assert.ok(next, `unexpected extra fetch of ${url}`);
      return next();
    },
    document: {
      getElementById: id => (id === 'question-data' || (id === 'home-question-data' && !embedded)) ? null
        : ['share-question', 'share-status'].includes(id) ? nodes[id] || null : element(id),
      createElement: () => new Element(),
      createTextNode: text => { const node = new Element(); node.textContent = text; return node; },
      querySelector: () => null,
      addEventListener: (type, fn) => { documentListeners[type] = fn; },
      visibilityState: 'visible',
    },
  });
  vm.runInContext(fs.readFileSync('assets/app.js', 'utf8'), context);
  await settle();
  return {
    // Reading a node the page never touched gives a fresh element, as an untouched DOM node would be.
    nodes: new Proxy(nodes, { get: (target, id) => element(id) }), requests, clock, context,
    tick: async () => { intervals.forEach(fn => fn()); await settle(); },
    returnToTab: async () => { documentListeners.visibilitychange(); await settle(); },
    shown: () => vm.runInContext('activeQuestion?.id', context),
    heading: () => nodes['practice-heading'].textContent,
  };
}

const ok = body => () => ({ ok: true, json: async () => JSON.parse(JSON.stringify(body)) });
const status = code => () => ({ ok: false, status: code, json: async () => ({}) });
const malformed = () => () => ({ ok: true, json: async () => JSON.parse('{"truncated": [') });
const offline = () => () => { throw new TypeError('Failed to fetch'); };
const clickAnswer = (nodes, letter) => nodes.options.children.find(b => b.dataset.letter === letter).click();
const dayBefore = midnight - 10 * MINUTE;

(async () => {
  // 1. The homepage refreshes from the compact endpoint, never the full bank.
  let page = await boot({ now: dayBefore, responses: [ok([current, next])] });
  assert.equal(page.requests.length, 1);
  assert.equal(page.requests[0].url, '/content/latest.json');
  assert.equal(page.requests[0].options.cache, 'no-cache');
  assert.equal(page.shown(), current.id);
  assert.equal(page.heading(), "Today's question");
  assert.equal(page.nodes['load-state'].hidden, true);
  assert.equal(page.nodes['practice-content'].hidden, false);

  // 2. A released next daily in the file is never shown before its London date.
  assert.notEqual(page.shown(), next.id, 'future daily must stay hidden before its date');
  page.clock.now = dayBefore + 5 * MINUTE;
  await page.tick();
  assert.equal(page.requests.length, 1, 'no refetch before midnight while today is shown');

  // 3. At London midnight the open tab moves to the next daily from the same file shape.
  page = await boot({ now: dayBefore, responses: [ok([current, next]), ok([current, next])] });
  page.clock.now = midnight + MINUTE;
  await page.tick();
  assert.equal(page.requests.length, 2);
  assert.equal(page.shown(), next.id);
  assert.equal(page.heading(), "Today's question");

  // 4. Delayed publication: the file still lacks today's question, so keep it and retry every 5 minutes.
  page = await boot({ now: dayBefore, responses: [ok([current]), ok([current]), ok([current, next])] });
  page.clock.now = midnight + MINUTE;
  await page.tick();
  assert.equal(page.shown(), current.id);
  assert.equal(page.heading(), 'Latest question');
  page.clock.now = midnight + 3 * MINUTE;
  await page.tick();
  assert.equal(page.requests.length, 2, 'retries are spaced five minutes apart');
  page.clock.now = midnight + 6 * MINUTE;
  await page.tick();
  assert.equal(page.requests.length, 3);
  assert.equal(page.shown(), next.id, 'late publish is picked up without a reload');
  assert.equal(page.heading(), "Today's question");
  page.clock.now = midnight + 20 * MINUTE;
  await page.tick();
  assert.equal(page.requests.length, 3, 'stops retrying once today is live');

  // 5. Returning to the tab checks straight away, even inside the retry window.
  page = await boot({ now: dayBefore, responses: [ok([current]), ok([current]), ok([current, next])] });
  page.clock.now = midnight + MINUTE;
  await page.tick();
  page.clock.now = midnight + 2 * MINUTE;
  await page.returnToTab();
  assert.equal(page.requests.length, 3);
  assert.equal(page.shown(), next.id);

  // 6. Failed, malformed, offline and invalid responses keep the embedded question quietly.
  const invalid = [
    ['HTTP 404', status(404)], ['HTTP 500', status(500)], ['malformed JSON', malformed()], ['offline', offline()],
    ['empty array', ok([])], ['not an array', ok({ questions: [current] })],
    ['missing route', ok([{ ...current, route: undefined }])], ['bad answer letter', ok([{ ...current, answer: 'F' }])],
    ['non-https source', ok([{ ...current, verified_source_url: 'http://example.org' }])],
    ['only a future daily', ok([next])],
  ];
  for (const [label, response] of invalid) {
    page = await boot({ now: dayBefore, responses: [response] });
    assert.equal(page.shown(), current.id, label);
    assert.equal(page.nodes['practice-content'].hidden, false, label);
    assert.notEqual(page.nodes['load-state'].textContent, "Today's question couldn't load. Please try again in a moment.", `${label} must stay quiet`);
    clickAnswer(page.nodes, current.answer);
    assert.equal(page.nodes.result.hidden, false, `${label}: the embedded question still answers`);
  }

  // 7. A failure during the midnight retry keeps the visible question and tries again later.
  page = await boot({ now: dayBefore, responses: [ok([current]), status(503), ok([current, next])] });
  page.clock.now = midnight + MINUTE;
  await page.tick();
  assert.equal(page.shown(), current.id);
  page.clock.now = midnight + 7 * MINUTE;
  await page.tick();
  assert.equal(page.shown(), next.id);

  // 8. Same-ID correction on load: a cached homepage picks up the corrected copy from latest.json.
  const corrected = { ...current, stem: 'Corrected stem?', explanation: 'Corrected explanation.', key_rule: 'Corrected rule.' };
  page = await boot({ now: dayBefore, responses: [ok([corrected])] });
  assert.equal(page.shown(), current.id);
  assert.equal(page.nodes.stem.textContent, 'Corrected stem?');
  assert.equal(page.nodes.result.hidden, true, 'nothing answered yet');

  // 9. Same-ID correction during a retry: the visitor's answer is replayed onto the corrected copy.
  const wrong = ['A', 'B', 'C', 'D', 'E'].find(letter => letter !== current.answer);
  page = await boot({ now: midnight + MINUTE, responses: [ok([current]), ok([corrected])] });
  assert.equal(page.heading(), 'Latest question');
  clickAnswer(page.nodes, wrong);
  await page.tick();
  assert.equal(page.requests.length, 2);
  assert.equal(page.shown(), current.id);
  assert.equal(page.nodes['key-rule'].textContent, 'Corrected rule.');
  assert.equal(page.nodes.explanation.children[0].textContent, 'Corrected explanation.');
  assert.equal(page.nodes.result.hidden, false, 'answer replayed after correction');
  assert.match(page.nodes.options.children.find(b => b.dataset.letter === wrong).className, /incorrect/);
  assert.match(page.nodes.options.children.find(b => b.dataset.letter === current.answer).className, / correct/);

  // A corrected answer letter moves the markers onto the visitor's replayed choice.
  page = await boot({ now: midnight + MINUTE, responses: [ok([current]), ok([{ ...current, answer: wrong }])] });
  clickAnswer(page.nodes, wrong);
  await page.tick();
  assert.equal(page.nodes['result-heading'].textContent, 'Correct. Nicely done.');
  // Changes to non-displayed fields re-render nothing.
  page = await boot({ now: midnight + MINUTE, responses: [ok([current]), ok([{ ...current, tags: ['changed'], modified: next.publish_date }])] });
  const before = page.nodes.options.children;
  await page.tick();
  assert.equal(page.requests.length, 2);
  assert.equal(page.nodes.options.children, before, 'non-displayed changes do not re-render');

  // 10. Without an embedded question, a failed load shows the retry message and button.
  page = await boot({ now: dayBefore, embedded: null, responses: [status(500), ok([current])] });
  assert.equal(page.nodes['load-state'].textContent, "Today's question couldn't load. Please try again in a moment.");
  const retry = page.nodes['load-state'].children.at(-1);
  assert.equal(retry.textContent, 'Try again');
  retry.click();
  await settle();
  assert.equal(page.shown(), current.id);
  assert.equal(page.nodes['practice-content'].hidden, false);

  console.log('PASS: homepage fetch flow from latest.json: next daily hidden until its date, midnight switch, delayed publish retry, tab return, failed/malformed/invalid responses, same-ID corrections and no-embed retry');
})().catch(error => { console.error(error); process.exit(1); });
