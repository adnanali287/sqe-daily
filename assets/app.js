'use strict';
const $ = id => document.getElementById(id);
const DAY = 86400000;
let activeQuestion;
let activeDay;
let answered = false;

// A UK calendar day is stable across time zones and daylight-saving changes.
function londonDay(date = new Date()) {
  const parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/London', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(date);
  const part = type => parts.find(p => p.type === type).value;
  return `${part('year')}-${part('month')}-${part('day')}`;
}
function dayIndex(date) { return Math.floor(Date.parse(`${date}T00:00:00Z`) / DAY); }
function updateDates() {
  const today = londonDay();
  if (!$('today') || !$('days')) return today;
  const questionDate = activeQuestion?.publish_date || today;
  $('today').dateTime = questionDate;
  $('today').textContent = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${questionDate}T00:00:00Z`));
  const days = Math.max(0, dayIndex('2027-01-11') - dayIndex(today));
  $('days').textContent = days;
  $('days-label').textContent = days === 1 ? 'day to go' : days === 0 ? 'days to go' : 'days to go';
  return today;
}
function selectQuestion(questions, today) {
  return questions.filter(q => q.publish_date <= today).sort((a, b) => b.publish_date.localeCompare(a.publish_date) || b.number - a.number)[0];
}
function questionPath(q) {
  return `/q/${q.number}-${q.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}/`;
}
function validQuestion(q) {
  return q && ['id', 'subject', 'flk', 'difficulty', 'title', 'scenario', 'stem', 'answer', 'explanation', 'key_rule', 'authority', 'verified_source_url', 'publish_date'].every(k => typeof q[k] === 'string' && q[k].trim()) && Number.isInteger(q.number) && /^[A-E]$/.test(q.answer) && ['A', 'B', 'C', 'D', 'E'].every(k => typeof q.options?.[k] === 'string') && /^https:\/\//.test(q.verified_source_url) && Number.isFinite(dayIndex(q.publish_date));
}
function renderQuestion(q) {
  activeQuestion = q;
  $('practice-heading').textContent = q.publish_date === londonDay() ? "Today's question" : 'Latest question';
  updateDates();
  answered = false;
  $('result').hidden = true;
  $('share-question')?.remove();
  $('share-status')?.remove();
  $('answer-hint').hidden = false;
  $('question-number').textContent = String(q.number).padStart(2, '0');
  ['subject', 'flk', 'scenario', 'stem'].forEach(k => $(k).textContent = q[k]);
  $('difficulty').textContent = q.difficulty[0].toUpperCase() + q.difficulty.slice(1);
  $('options').replaceChildren();
  Object.entries(q.options).sort(([a], [b]) => a.localeCompare(b)).forEach(([letter, option]) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'option';
    button.dataset.letter = letter;
    button.setAttribute('aria-label', `${letter}. ${option}`);
    ['option-letter', 'option-text', 'option-symbol'].forEach((className, index) => {
      const span = document.createElement('span');
      span.className = className;
      span.textContent = index === 0 ? letter : index === 1 ? option : '';
      if (index !== 1) span.setAttribute('aria-hidden', 'true');
      button.append(span);
    });
    button.addEventListener('click', () => answerQuestion(letter));
    $('options').append(button);
  });
}
function answerQuestion(letter) {
  if (answered) return;
  answered = true;
  const q = activeQuestion;
  const correct = letter === q.answer;
  [...$('options').children].forEach(button => {
    const key = button.dataset.letter;
    button.disabled = true;
    if (key === q.answer) {
      button.classList.add('correct');
      button.querySelector('.option-symbol').textContent = '✓';
      button.setAttribute('aria-label', `${key}. ${q.options[key]}. Correct answer${correct ? ', your answer' : ''}.`);
    } else if (key === letter) {
      button.classList.add('incorrect');
      button.querySelector('.option-symbol').textContent = '×';
      button.setAttribute('aria-label', `${key}. ${q.options[key]}. Your answer, incorrect.`);
    }
  });
  $('result-heading').textContent = correct ? 'Correct. Nicely done.' : `Not quite. The answer is ${q.answer}.`;
  $('result-symbol').textContent = correct ? '✓' : '×';
  $('correct-answer').textContent = `Correct answer ${q.answer}: ${q.options[q.answer]}`;
  $('key-rule').textContent = q.key_rule;
  $('question-title').textContent = q.title;
  $('explanation').replaceChildren();
  q.explanation.split(/\n+/).forEach(text => {
    const p = document.createElement('p');
    p.textContent = text;
    $('explanation').append(p);
  });
  $('authority-link').textContent = `${q.authority} ↗`;
  $('authority-link').href = q.verified_source_url;
  if (!$('share-question')) {
    const share = document.createElement('button');
    share.id = 'share-question';
    share.type = 'button';
    share.className = 'share-button';
    share.textContent = 'Share';
    share.setAttribute('aria-label', 'Share this question without revealing the answer');
    const status = document.createElement('p');
    status.id = 'share-status';
    status.setAttribute('role', 'status');
    share.addEventListener('click', async () => {
      const url = `https://sqedaily.co.uk${questionPath(q)}`;
      const text = correct ? "I got this SQE Daily question right. Can you?" : 'Can you answer this SQE Daily question?';
      try {
        if (navigator.share) await navigator.share({ title: 'SQE Daily', text, url });
        else { await navigator.clipboard.writeText(`${text} ${url}`); status.textContent = 'Link copied.'; }
      } catch (error) {
        if (error.name === 'AbortError') return;
        status.replaceChildren(document.createTextNode('Copy this link: '));
        const link = document.createElement('a'); link.href = url; link.textContent = url; status.append(link);
      }
    });
    $('result').append(share, status);
  }
  $('answer-hint').hidden = true;
  $('result').hidden = false;
  $('result-heading').focus({ preventScroll: true });
  $('result').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
}
async function loadQuestion() {
  $('load-state').replaceChildren(document.createTextNode('Getting today\'s question ready…'));
  $('load-state').hidden = false;
  $('practice-content').hidden = true;
  try {
    const response = await fetch('/content/questions.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error('Question data unavailable');
    const questions = await response.json();
    if (!Array.isArray(questions) || !questions.length || !questions.every(validQuestion)) throw new Error('Invalid question data');
    activeDay = updateDates();
    const question = selectQuestion(questions, activeDay);
    if (!question) throw new Error('No published questions');
    renderQuestion(question);
    $('load-state').hidden = true;
    $('practice-content').hidden = false;
  } catch {
    $('load-state').textContent = 'Today\'s question couldn\'t load. Please try again in a moment.';
    const retry = document.createElement('button');
    retry.type = 'button';
    retry.textContent = 'Try again';
    retry.addEventListener('click', loadQuestion);
    $('load-state').append(retry);
  }
}
// Buttondown requires a native form POST so validation and CAPTCHA can work.
// Its saved redirects return here only after signup or opt-in confirmation.
const subscriptionState = new URLSearchParams(location.search).get('subscription');
if (subscriptionState === 'pending' || subscriptionState === 'confirmed') {
  $('email-status').hidden = false;
  $('email-status').textContent = subscriptionState === 'pending'
    ? 'Check your inbox to confirm your subscription.'
    : 'Your subscription is confirmed. Thanks for joining SQE Daily.';
  // Buttondown may append the address to its redirect. Keep it out of the URL.
  history.replaceState(null, '', `${location.pathname}#daily-email`);
}
updateDates();
const staticData = $('question-data');
const ready = staticData ? Promise.resolve().then(() => {
  const question = JSON.parse(staticData.textContent);
  if (question.publish_date > londonDay()) {
    $('practice-content').hidden = true;
    return;
  }
  activeQuestion = question;
  [...$('options').children].forEach(button => button.addEventListener('click', () => answerQuestion(button.dataset.letter)));
}) : loadQuestion();
ready.then(() => {
  if (subscriptionState === 'pending' || subscriptionState === 'confirmed') {
    $('daily-email').scrollIntoView({ behavior: 'instant' });
  }
});
if (!staticData) setInterval(() => { if (updateDates() !== activeDay) loadQuestion(); }, 60000);
