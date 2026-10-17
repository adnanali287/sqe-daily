'use strict';
const $ = id => document.getElementById(id);
const DAY = 86400000;
const RETRY_MS = 5 * 60000;
let activeQuestion;
let activeDay;
let answered = false;
let chosenLetter = null;
let nextRetry = 0;

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
  const questionDate = ($('question-data') ? activeQuestion?.available_from : activeQuestion?.publish_date) || today;
  $('today').dateTime = questionDate;
  $('today').textContent = new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${questionDate}T00:00:00Z`));
  const sitting = document.querySelector?.('.countdown')?.dataset.flk1 || '2027-01-11';
  const days = Math.max(0, dayIndex(sitting) - dayIndex(today));
  $('days').textContent = days;
  $('days-label').textContent = days === 1 ? 'day to go' : days === 0 ? 'days to go' : 'days to go';
  return today;
}
function selectQuestion(questions, today) {
  return questions.filter(q => typeof q.publish_date === 'string' && q.publish_date <= today).sort((a, b) => b.publish_date.localeCompare(a.publish_date) || b.number - a.number)[0];
}
function headingLabel(q, today) {
  if (q.library_number) return 'Library question';
  return q.publish_date === today ? "Today's question" : 'Latest question';
}
// Mirrors the generator: optional one-line reasons replace the combined "X is wrong" lines.
function explanationLines(q) {
  const lines = q.explanation.split(/\n+/);
  if (!q.why_wrong) return lines;
  return lines.filter(line => !/^[A-E] is wrong\b/.test(line)).concat(Object.keys(q.why_wrong).sort().map(key => `Why ${key} is wrong: ${q.why_wrong[key]}`));
}
// Displayed fields only: a correction published under the same id must still reach an open page.
const CONTENT_FIELDS = ['id', 'number', 'title', 'subject', 'flk', 'difficulty', 'scenario', 'stem', 'answer', 'explanation', 'key_rule', 'authority', 'verified_source_url', 'last_reviewed', 'route'];
function contentKey(q) {
  return JSON.stringify([CONTENT_FIELDS.map(k => q[k] ?? null), ['A', 'B', 'C', 'D', 'E'].map(k => q.options?.[k] ?? null), Object.keys(q.why_wrong || {}).sort().map(k => [k, q.why_wrong[k]])]);
}
function sameContent(a, b) {
  return Boolean(a && b) && contentKey(a) === contentKey(b);
}
// After midnight, keep checking until today's question is live: scheduled publishing can run late.
function refreshDue({ activeDay, today, question, now, nextRetry }) {
  return today !== activeDay || Boolean(question && question.publish_date < today && now >= nextRetry);
}
function longDate(date) {
  return new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${date}T00:00:00Z`));
}
function validQuestion(q) {
  return q && ['id', 'subject', 'flk', 'difficulty', 'title', 'scenario', 'stem', 'answer', 'explanation', 'key_rule', 'authority', 'verified_source_url'].every(k => typeof q[k] === 'string' && q[k].trim()) && Number.isInteger(q.number) && /^[A-E]$/.test(q.answer) && ['A', 'B', 'C', 'D', 'E'].every(k => typeof q.options?.[k] === 'string') && /^https:\/\//.test(q.verified_source_url) && /^\/q\/[a-z0-9-]+\/$/.test(q.route) && (q.publish_date === null ? typeof q.available_from === 'string' && Number.isFinite(dayIndex(q.available_from)) : typeof q.publish_date === 'string' && Number.isFinite(dayIndex(q.publish_date)));
}
function renderQuestion(q) {
  activeQuestion = q;
  $('practice-heading').textContent = headingLabel(q, londonDay());
  updateDates();
  $('question').dataset.questionId = q.id;
  if ($('permalink')) $('permalink').href = q.route;
  if ($('report-link')) $('report-link').href = `mailto:hello@sqedaily.co.uk?subject=${encodeURIComponent(`Question ${q.id}`)}`;
  if ($('checked-note')) {
    $('checked-note').hidden = !q.last_reviewed;
    $('checked-note').textContent = q.last_reviewed ? `Checked against ${q.library_number ? 'source' : 'primary source'} on ${longDate(q.last_reviewed)}` : '';
  }
  answered = false;
  $('result').hidden = true;
  $('share-question')?.remove();
  $('share-status')?.remove();
  $('answer-hint').hidden = false;
  $('question-number').textContent = q.library_number ? `L${String(q.library_number).padStart(3, '0')}` : String(q.number).padStart(2, '0');
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
function answerQuestion(letter, { quiet = false } = {}) {
  if (answered) return;
  answered = true;
  chosenLetter = letter;
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
  explanationLines(q).forEach(text => {
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
      const url = `https://sqedaily.co.uk${q.route}`;
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
  if (quiet) return;
  $('result-heading').focus({ preventScroll: true });
  $('result').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
}
function adoptQuestion(q) {
  activeQuestion = q;
  answered = false;
  activeDay = updateDates();
  $('practice-heading').textContent = headingLabel(q, activeDay);
  [...$('options').children].forEach(button => button.addEventListener('click', () => answerQuestion(button.dataset.letter)));
}
// The homepage arrives with the latest question already in its HTML. Fetching
// still runs so a cached page, or one left open past midnight, moves on quietly.
async function loadQuestion(quiet = Boolean(activeQuestion)) {
  if (!quiet) {
    $('load-state').replaceChildren(document.createTextNode('Getting today\'s question ready…'));
    $('load-state').hidden = false;
    $('practice-content').hidden = true;
  }
  try {
    const response = await fetch('/content/questions.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error('Question data unavailable');
    const questions = await response.json();
    if (!Array.isArray(questions) || !questions.length || !questions.every(validQuestion)) throw new Error('Invalid question data');
    activeDay = updateDates();
    const question = selectQuestion(questions, activeDay);
    if (!question) throw new Error('No published questions');
    if (!sameContent(question, activeQuestion)) {
      // Keep a visitor's answer when the same question is corrected; a new question starts fresh.
      const replay = answered && question.id === activeQuestion?.id ? chosenLetter : null;
      renderQuestion(question);
      if (replay) answerQuestion(replay, { quiet: true });
    } else {
      $('practice-heading').textContent = headingLabel(question, activeDay);
    }
    $('load-state').hidden = true;
    $('practice-content').hidden = false;
  } catch {
    if (quiet) return;
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
const homeData = $('home-question-data');
const ready = staticData ? Promise.resolve().then(() => {
  const question = JSON.parse(staticData.textContent);
  if ((question.available_from || question.publish_date) > londonDay()) {
    $('practice-content').hidden = true;
    return;
  }
  activeQuestion = question;
  [...$('options').children].forEach(button => button.addEventListener('click', () => answerQuestion(button.dataset.letter)));
}) : homeData ? Promise.resolve().then(() => {
  adoptQuestion(JSON.parse(homeData.textContent));
  return loadQuestion(true);
}) : loadQuestion();
ready.then(() => {
  if (subscriptionState === 'pending' || subscriptionState === 'confirmed') {
    $('daily-email').scrollIntoView({ behavior: 'instant' });
  }
});
function tick() {
  const now = Date.now();
  if (!refreshDue({ activeDay, today: updateDates(), question: activeQuestion, now, nextRetry })) return;
  nextRetry = now + RETRY_MS;
  loadQuestion();
}
if (!staticData) {
  setInterval(tick, 60000);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') { nextRetry = 0; tick(); }
  });
}
