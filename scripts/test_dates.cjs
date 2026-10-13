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
console.log('PASS: exact date, latest past, no future, BST/GMT calendar boundaries');
