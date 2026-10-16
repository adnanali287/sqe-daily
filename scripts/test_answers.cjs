const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

// Exercise the production renderer and answer handler with a small DOM fixture.
class Element {
  constructor() {
    this.children = [];
    this.dataset = {};
    this.attributes = {};
    this.textContent = '';
    this.className = '';
    this.hidden = false;
    this.disabled = false;
    this.classList = { add: name => { this.className += ` ${name}`; } };
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener() {}
  remove() {}
  querySelector(selector) {
    return this.children.find(child => child.className.split(' ').includes(selector.slice(1)));
  }
}

const ids = ['practice-heading', 'question', 'result', 'answer-hint', 'question-number',
  'subject', 'flk', 'scenario', 'stem', 'difficulty', 'options', 'result-heading',
  'result-symbol', 'correct-answer', 'key-rule', 'question-title', 'explanation', 'authority-link'];
const nodes = Object.fromEntries(ids.map(id => [id, new Element()]));
// Keep the share control present so these tests never touch browser sharing APIs.
nodes['share-question'] = new Element();
const context = vm.createContext({
  Intl, Date,
  document: { getElementById: id => nodes[id] || null, createElement: () => new Element() }
});
vm.runInContext(fs.readFileSync('assets/app.js', 'utf8').split('// Buttondown requires')[0], context);
const bank = JSON.parse(fs.readFileSync('content/questions.json', 'utf8'));
const letters = ['A', 'B', 'C', 'D', 'E'];
let cases = 0;

for (const question of bank) {
  for (const choice of letters) {
    context.question = question;
    context.choice = choice;
    vm.runInContext('renderQuestion(question)', context);
    assert.equal(nodes.result.hidden, true);
    assert.equal(nodes['answer-hint'].hidden, false);
    assert.equal(nodes.options.children.length, 5);
    for (const button of nodes.options.children) {
      assert.equal(button.disabled, false);
      assert.equal(button.querySelector('.option-symbol').textContent, '');
      assert.equal(button.className, 'option', 'a new rendering clears previous markers');
    }
    vm.runInContext('answerQuestion(choice, { quiet: true })', context);
    const correctChoice = choice === question.answer;
    for (const button of nodes.options.children) {
      const key = button.dataset.letter;
      const state = key === question.answer ? 'correct' : key === choice ? 'incorrect' : '';
      assert.equal(button.className, `option${state ? ` ${state}` : ''}`, `${question.id}: ${choice} -> ${key}`);
      assert.equal(button.querySelector('.option-symbol').textContent,
        state === 'correct' ? '\u2713' : state === 'incorrect' ? '\u00d7' : '');
      assert.equal(button.disabled, true);
      const label = button.attributes['aria-label'];
      assert.equal(label.includes('Correct answer'), key === question.answer);
      assert.equal(label.includes('Your answer, incorrect'), key === choice && !correctChoice);
    }
    assert.equal(nodes['result-symbol'].textContent, correctChoice ? '\u2713' : '\u00d7');
    assert.equal(nodes.result.hidden, false);
    assert.equal(nodes['answer-hint'].hidden, true);
    const snapshot = JSON.stringify(nodes.options.children.map(b => b.attributes));
    vm.runInContext("answerQuestion(choice === 'A' ? 'E' : 'A', { quiet: true })", context);
    assert.equal(JSON.stringify(nodes.options.children.map(b => b.attributes)), snapshot, 'answers cannot be changed after submission');
    cases++;
  }
}

// A correction to the same ID can change the correct option; no old marker may survive.
context.question = { ...bank[0], answer: 'E' };
vm.runInContext("renderQuestion(question); answerQuestion('E', { quiet: true }); question = { ...question, answer: 'A' }; renderQuestion(question); answerQuestion('E', { quiet: true })", context);
assert.equal(nodes.options.children[0].querySelector('.option-symbol').textContent, '\u2713');
assert.equal(nodes.options.children[4].querySelector('.option-symbol').textContent, '\u00d7');
console.log(`PASS: ${cases} answer selections, all option markers and labels, result state, repeat-answer guard, render resets and same-ID answer correction`);
