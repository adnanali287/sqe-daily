const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const context = vm.createContext({ Intl, Date, document: {} });
vm.runInContext(fs.readFileSync('assets/app.js', 'utf8').split('// Buttondown requires')[0], context);
context.bank = [
  { id: 'past', number: 1, publish_date: '2026-10-13' },
  { id: 'today', number: 2, publish_date: '2026-10-14' },
  { id: 'future', number: 3, publish_date: '2099-12-31' }
];
assert.equal(vm.runInContext("selectQuestion(bank, '2026-10-13').id", context), 'past');
assert.equal(vm.runInContext("selectQuestion(bank, '2026-10-14').id", context), 'today');
assert.equal(vm.runInContext("selectQuestion(bank, '2026-12-01').id", context), 'today');
assert.equal(vm.runInContext("selectQuestion(bank, '2026-10-12')", context), undefined);
assert.equal(vm.runInContext("londonDay(new Date('2026-10-13T23:01:00Z'))", context), '2026-10-14');
assert.equal(vm.runInContext("londonDay(new Date('2026-10-25T23:01:00Z'))", context), '2026-10-25');
assert.equal(vm.runInContext("londonDay(new Date('2027-03-28T23:01:00Z'))", context), '2027-03-29');
// Homepage left open across London midnight: the next fetch picks the new question and relabels it.
context.daily = [
  { id: 'q1', number: 1, publish_date: '2026-10-25' },
  { id: 'q2', number: 2, publish_date: '2026-10-26' }
];
vm.runInContext("beforeDay = londonDay(new Date('2026-10-25T23:59:30Z')); afterDay = londonDay(new Date('2026-10-26T00:00:30Z'))", context);
assert.equal(vm.runInContext('selectQuestion(daily, beforeDay).id', context), 'q1');
assert.equal(vm.runInContext('headingLabel(selectQuestion(daily, beforeDay), beforeDay)', context), "Today's question");
assert.equal(vm.runInContext('selectQuestion(daily, afterDay).id', context), 'q2');
assert.equal(vm.runInContext('headingLabel(selectQuestion(daily, afterDay), afterDay)', context), "Today's question");
assert.equal(vm.runInContext("headingLabel(daily[1], '2026-10-27')", context), 'Latest question');
// Share and permanent links use the locked route, never a slug rebuilt from the title.
context.sample = { id: 'q1', number: 1, subject: 's', flk: 'FLK1', difficulty: 'easy', title: 'Edited title', scenario: 's', stem: 's', answer: 'A', explanation: 'Why.\n\nA is wrong: x.\nB is wrong: y.', key_rule: 'k', authority: 'a', verified_source_url: 'https://example.org', publish_date: '2026-10-25', options: { A: 'a', B: 'b', C: 'c', D: 'd', E: 'e' }, route: '/q/1-original-title/' };
assert.equal(vm.runInContext('validQuestion(sample)', context), true);
assert.equal(vm.runInContext('validQuestion({ ...sample, route: undefined })', context), false);
assert.deepEqual([...vm.runInContext('explanationLines(sample)', context)], ['Why.', 'A is wrong: x.', 'B is wrong: y.']);
context.sample.why_wrong = { B: 'Reason B.', A: 'Reason A.' };
assert.deepEqual([...vm.runInContext('explanationLines(sample)', context)], ['Why.', 'Why A is wrong: Reason A.', 'Why B is wrong: Reason B.']);
// Delayed publication: after midnight the page keeps checking every 5 minutes until today's question is live.
context.state = { activeDay: '2026-10-26', today: '2026-10-26', question: context.daily[0], now: 1_000_000, nextRetry: 1_000_000 + 300000 };
assert.equal(vm.runInContext("refreshDue({ ...state, activeDay: '2026-10-25' })", context), true, 'day change refreshes');
assert.equal(vm.runInContext('refreshDue(state)', context), false, 'retries are spaced out');
assert.equal(vm.runInContext('refreshDue({ ...state, now: state.nextRetry })', context), true, 'still waiting for today: retry is due');
assert.equal(vm.runInContext('refreshDue({ ...state, question: daily[1], now: state.nextRetry })', context), false, "today's question is shown: stop retrying");
assert.equal(vm.runInContext('RETRY_MS', context), 300000);
// Corrections under the same id are content changes; an identical copy is not.
delete context.sample.why_wrong;
assert.equal(vm.runInContext('sameContent(sample, JSON.parse(JSON.stringify(sample)))', context), true);
for (const change of ["{ explanation: 'Corrected.' }", "{ answer: 'B' }", "{ title: 'Corrected title' }", "{ options: { ...sample.options, C: 'fixed' } }", "{ why_wrong: { B: 'r', C: 'r', D: 'r', E: 'r' } }"]) {
  assert.equal(vm.runInContext(`sameContent(sample, { ...sample, ...${change} })`, context), false, change);
}
assert.equal(vm.runInContext("sameContent(sample, { ...sample, tags: ['x'], modified: '2026-10-26' })", context), true, 'non-displayed fields are ignored');
console.log('PASS: exact date, latest past, no future, BST/GMT boundaries, midnight relabel, delayed publication retry, same-id corrections, locked routes, why_wrong');
