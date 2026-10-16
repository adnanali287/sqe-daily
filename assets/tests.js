'use strict';
(() => {
  const C = window.SQETests;
  const $ = id => document.getElementById(id);
  const KEY = 'sqedaily-practice-v1';
  let bank = [], papers = [], attempt = null, saved = null, missedOnly = false, externalChange = false;
  let lastWarning = '';
  const node = (tag, text, className) => {
    const el = document.createElement(tag);
    if (text !== undefined) el.textContent = text;
    if (className) el.className = className;
    return el;
  };
  const button = (text, action, className = 'test-secondary') => {
    const el = node('button', text, className); el.type = 'button'; el.addEventListener('click', action); return el;
  };
  const kind = () => document.querySelector('input[name="kind"]:checked').value;
  const timed = () => document.querySelector('input[name="timing"]:checked').value === 'timed';
  const announce = text => { $('test-announcement').textContent = text; };
  function notice(text) { $('storage-note').textContent = text; $('storage-note').hidden = false; }
  function persist() {
    try {
      if (attempt) localStorage.setItem(KEY, JSON.stringify(attempt));
      else localStorage.removeItem(KEY);
    } catch { notice('Your browser could not save this attempt. Keep this tab open to finish.'); }
  }
  function screen(id) {
    document.body.classList.toggle('taking-test', id !== 'test-setup');
    for (const name of ['test-setup', 'test-running', 'test-break', 'test-results']) $(name).hidden = name !== id;
  }
  function formatTime(ms) {
    const seconds = Math.max(0, Math.ceil(ms / 1000));
    const h = Math.floor(seconds / 3600), m = Math.floor(seconds % 3600 / 60), s = seconds % 60;
    return `${h ? `${h}:` : ''}${h ? String(m).padStart(2, '0') : m}:${String(s).padStart(2, '0')}`;
  }
  function setup() {
    screen('test-setup');
    $('bank-count').textContent = bank.length;
    $('resume-panel').hidden = !saved;
    $('resume-heading').textContent = saved?.status === 'results' ? 'Previous result' : 'Unfinished test';
    $('resume-test').textContent = saved?.status === 'results' ? 'View results' : 'Resume test';
    if (saved) $('resume-summary').textContent = `${saved.title} · ${saved.status === 'results' ? 'Completed' : saved.status === 'break' ? 'Between sessions' : `${C.results(saved).answered} answered`}${saved.timed && saved.status !== 'results' ? '. The timer continues while you are away.' : ''}`;
    configure();
  }
  function configure(resetSubjects = false) {
    const paper = $('test-paper').value;
    const oldSubject = resetSubjects ? '' : $('test-subject').value;
    const subjects = [...new Set(C.pool(bank, paper).map(q => q.subject))].sort();
    $('test-subject').replaceChildren(new Option('All subjects', ''), ...subjects.map(s => new Option(s, s)));
    $('test-subject').value = subjects.includes(oldSubject) ? oldSubject : '';
    const full = kind() === 'full';
    $('subject-field').hidden = full; $('count-field').hidden = full; $('mock-field').hidden = !full;
    const oldMock = $('test-mock').value;
    const choices = papers.filter(p => p.paper === paper);
    $('test-mock').replaceChildren(...choices.map(p => new Option(p.title, p.id)));
    if (choices.some(p => p.id === oldMock)) $('test-mock').value = oldMock;
    $('test-mock').disabled = !choices.length;
    const count = Number($('test-count').value);
    const size = C.pool(bank, paper, $('test-subject').value).length;
    $('pool-status').textContent = full ? choices.length ? `${choices.length} approved full ${paper} ${choices.length === 1 ? 'paper' : 'papers'}` : `No approved full ${paper} mock is available yet.` : `${size} questions available${size < count ? ` · ${count} needed for this test` : ''}`;
    $('duration-note').textContent = full ? timed() ? '170 questions · 2 sessions of 153 minutes · 60-minute break' : '170 questions · 2 sessions · untimed practice' : timed() ? `${count} questions · ${count * 1.8} minutes. The timer continues if you leave.` : `${count} questions · untimed practice`;
    if (full && choices.length) $('duration-note').textContent += ` · Law cutoff: ${choices.find(p => p.id === $('test-mock').value)?.law_cutoff || choices[0].law_cutoff}`;
    if (full && choices.length) {
      const source = node('a', 'SRA assessment format');
      source.href = choices.find(p => p.id === $('test-mock').value)?.source_url || choices[0].source_url;
      source.target = '_blank'; source.rel = 'noopener noreferrer';
      $('duration-note').append(document.createTextNode(' · '), source);
    }
    $('start-test').disabled = Boolean(saved && saved.status !== 'results') || (full ? !choices.length : size < count);
  }
  function grid(target, ids, go) {
    const offset = attempt.session === 1 ? 85 : 0;
    target.replaceChildren(...ids.map((id, index) => {
      const answered = Boolean(attempt.answers[id]), flagged = Boolean(attempt.flags[id]);
      const b = button(String(offset + index + 1), () => go(index), '');
      b.dataset.answered = String(answered); b.dataset.flagged = String(flagged);
      b.setAttribute('aria-label', `Question ${offset + index + 1}, ${answered ? 'answered' : 'unanswered'}${flagged ? ', flagged' : ''}`);
      if (index === attempt.index) b.setAttribute('aria-current', 'true');
      return b;
    }));
  }
  function go(index) {
    if (!active()) return;
    attempt.index = index; persist(); renderQuestion(); focusQuestion();
  }
  function focusQuestion() { $('test-question-position').setAttribute('tabindex', '-1'); $('test-question-position').focus(); }
  function active() {
    if (externalChange || !attempt) return false;
    const status = attempt.status;
    C.reconcile(attempt);
    if (status !== attempt.status) { persist(); render(); }
    return attempt.status === 'active';
  }
  function renderQuestion() {
    const ids = C.currentIds(attempt), id = ids[attempt.index];
    const q = attempt.questions.find(q => q.id === id);
    const answered = ids.filter(id => attempt.answers[id]).length;
    const n = attempt.index + 1 + (attempt.session === 1 ? 85 : 0);
    $('attempt-label').textContent = attempt.mode === 'full' ? `${attempt.paper} · SESSION ${attempt.session + 1} OF 2${!attempt.timed ? ' · UNTIMED' : ''}` : `${attempt.paper} · MINI TEST${!attempt.timed ? ' · UNTIMED' : ''}`;
    $('attempt-heading').textContent = attempt.title;
    $('test-progress').max = ids.length; $('test-progress').value = answered;
    $('answered-count').textContent = `${answered} of ${ids.length} answered`;
    grid($('question-grid'), ids, go);
    $('test-question-position').textContent = `QUESTION ${String(n).padStart(2, '0')} / ${attempt.questions.length}`;
    $('flag-question').checked = Boolean(attempt.flags[id]);
    $('test-scenario').textContent = q.scenario; $('test-stem').textContent = q.stem;
    $('test-choices').replaceChildren();
    for (const letter of ['A', 'B', 'C', 'D', 'E']) {
      const label = node('label', undefined, 'test-choice');
      const input = document.createElement('input'); input.type = 'radio'; input.name = 'test-answer'; input.value = letter;
      input.checked = attempt.answers[id] === letter;
      input.addEventListener('change', () => {
        if (!active()) return;
        C.answer(attempt, id, letter); persist();
        $('test-progress').value = ids.filter(id => attempt.answers[id]).length;
        $('answered-count').textContent = `${$('test-progress').value} of ${ids.length} answered`;
        grid($('question-grid'), ids, go);
      });
      label.append(input, node('span', letter, 'test-letter'), node('span', q.options[letter]));
      $('test-choices').append(label);
    }
    $('previous-question').disabled = attempt.index === 0;
    $('next-question').textContent = attempt.index === ids.length - 1 ? 'Review & submit' : 'Next →';
    updateClock();
  }
  function render() {
    if (!attempt) { setup(); return; }
    if (attempt.status === 'active') { screen('test-running'); renderQuestion(); }
    else if (attempt.status === 'break') {
      screen('test-break');
      $('break-note').textContent = attempt.timed ? 'Session 2 begins automatically when the break ends. Its timer continues if this tab is closed.' : 'Untimed practice: continue when you are ready.';
      $('begin-session').hidden = attempt.timed;
      updateClock();
    } else renderResults();
  }
  function renderResults() {
    screen('test-results');
    const score = C.results(attempt);
    $('results-heading').textContent = attempt.title;
    $('test-score').textContent = `${Math.round(score.correct / score.total * 100)}%`;
    $('score-detail').textContent = `${score.correct} correct out of ${score.total} · ${score.unanswered} unanswered`;
    $('subject-results').replaceChildren(...Object.entries(score.subjects).sort(([a], [b]) => a.localeCompare(b)).map(([subject, s]) => {
      const row = node('div', undefined, 'subject-result'); row.append(node('span', subject), node('strong', `${s.correct} / ${s.total}`)); return row;
    }));
    $('review-missed').textContent = missedOnly ? 'Review all questions' : 'Review missed questions';
    $('answer-review').replaceChildren();
    const selected = attempt.questions.filter(q => !missedOnly || attempt.answers[q.id] !== q.answer);
    if (!selected.length) $('answer-review').append(node('p', 'No missed questions.'));
    for (const q of selected) {
      const index = attempt.questions.indexOf(q) + 1;
      const details = document.createElement('details');
      const summary = node('summary', `Question ${index} · ${q.subject}`);
      const choice = attempt.answers[q.id];
      summary.append(node('span', `${choice === q.answer ? 'Correct' : choice ? 'Incorrect' : 'Unanswered'} · Your answer: ${choice || '—'} · Correct answer: ${q.answer}`));
      details.append(summary, node('p', q.scenario), node('p', q.stem));
      const options = document.createElement('ol'); options.type = 'A';
      for (const letter of ['A', 'B', 'C', 'D', 'E']) options.append(node('li', q.options[letter]));
      details.append(options, node('p', q.key_rule, 'review-rule'));
      const lines = q.explanation.split(/\n+/).filter(line => !q.why_wrong || !/^[A-E] is wrong\b/.test(line));
      if (q.why_wrong) lines.push(...Object.entries(q.why_wrong).sort(([a], [b]) => a.localeCompare(b)).map(([key, why]) => `Why ${key} is wrong: ${why}`));
      details.append(...lines.filter(Boolean).map(p => node('p', p)));
      const source = node('a', q.authority); source.href = q.verified_source_url; source.target = '_blank'; source.rel = 'noopener noreferrer';
      const report = node('a', 'Report an error'); report.href = `mailto:hello@sqedaily.co.uk?subject=${encodeURIComponent(`Question ${q.number}`)}`;
      const links = node('p'); links.append(source, document.createTextNode(' · '), report);
      details.append(links); $('answer-review').append(details);
    }
  }
  function review() {
    if (!active()) return;
    const ids = C.currentIds(attempt);
    const missing = ids.filter(id => !attempt.answers[id]).length;
    const flagged = ids.filter(id => attempt.flags[id]).length;
    $('submit-heading').textContent = attempt.mode === 'full' ? `Submit session ${attempt.session + 1}?` : 'Submit this test?';
    $('submit-summary').textContent = `${missing} unanswered · ${flagged} flagged${attempt.mode === 'full' && attempt.session === 0 ? '. Session 1 will be locked; explanations follow session 2.' : ''}`;
    grid($('submission-grid'), ids, index => { $('submit-dialog').close(); go(index); });
    $('submit-dialog').showModal();
    $('cancel-submit').focus();
  }
  function updateClock() {
    if (!attempt) return;
    if (attempt.status === 'break') { $('break-clock').textContent = attempt.timed ? formatTime(attempt.breakUntil - Date.now()) : 'Session 2'; return; }
    $('clock-label').textContent = attempt.timed ? 'Time remaining' : 'Timing';
    $('test-clock').textContent = attempt.timed ? formatTime(attempt.deadline - Date.now()) : 'Untimed';
    if (attempt.timed) {
      const seconds = Math.ceil((attempt.deadline - Date.now()) / 1000);
      const warning = seconds <= 60 ? 'One minute remaining.' : seconds <= 300 ? 'Five minutes remaining.' : '';
      if (warning && warning !== lastWarning) { lastWarning = warning; announce(warning); }
    }
  }
  function tick() {
    if (!attempt || externalChange || attempt.status === 'results') return;
    const before = `${attempt.status}:${attempt.session}`;
    C.reconcile(attempt);
    if (`${attempt.status}:${attempt.session}` !== before) {
      $('submit-dialog').close(); persist(); render();
      announce(attempt.status === 'results' ? 'Time is up. Your test has been submitted.' : attempt.status === 'break' ? 'Session 1 ended. Your break has started.' : 'Session 2 has started.');
    } else updateClock();
  }
  $('test-form').addEventListener('change', e => configure(e.target.id === 'test-paper'));
  $('test-form').addEventListener('submit', e => {
    e.preventDefault();
    if (externalChange || (saved && saved.status !== 'results')) return;
    try {
      const selectedMock = kind() === 'full' ? papers.find(p => p.id === $('test-mock').value) : null;
      if (kind() === 'full' && !selectedMock) throw Error('This full mock is not ready.');
      attempt = C.create({ bank, paper: $('test-paper').value, subject: kind() === 'full' ? '' : $('test-subject').value,
        count: Number($('test-count').value), timed: timed(), mock: selectedMock });
      saved = null; missedOnly = false; lastWarning = ''; persist(); render(); focusQuestion();
    } catch (error) { notice(error.message); }
  });
  $('previous-question').addEventListener('click', () => go(Math.max(0, attempt.index - 1)));
  $('next-question').addEventListener('click', () => attempt.index === C.currentIds(attempt).length - 1 ? review() : go(attempt.index + 1));
  $('flag-question').addEventListener('change', () => {
    if (!active()) return;
    attempt.flags[C.currentIds(attempt)[attempt.index]] = $('flag-question').checked; persist(); grid($('question-grid'), C.currentIds(attempt), go);
  });
  $('review-test').addEventListener('click', review);
  $('review-top').addEventListener('click', review);
  $('cancel-submit').addEventListener('click', () => $('submit-dialog').close());
  $('confirm-submit').addEventListener('click', () => {
    $('submit-dialog').close(); if (!active()) return;
    C.finish(attempt); persist(); render();
    $(attempt.status === 'results' ? 'results-heading' : 'test-break').querySelector?.('h2')?.focus();
    if (attempt.status === 'results') $('results-heading').focus();
  });
  $('save-exit').addEventListener('click', () => {
    tick(); persist(); saved = attempt; attempt = null; setup(); notice('Saved on this device. Timed tests keep running while you are away.'); $('resume-test').focus();
  });
  $('resume-test').addEventListener('click', () => {
    attempt = C.reconcile(saved); saved = null; persist(); render(); if (attempt.status === 'active') focusQuestion();
  });
  $('discard-test').addEventListener('click', () => { attempt = null; saved = null; persist(); setup(); });
  $('begin-session').addEventListener('click', () => { C.advance(attempt); persist(); render(); focusQuestion(); });
  $('new-test').addEventListener('click', () => { attempt = null; saved = null; persist(); setup(); $('setup-heading').setAttribute('tabindex', '-1'); $('setup-heading').focus(); });
  $('review-missed').addEventListener('click', () => { missedOnly = !missedOnly; renderResults(); });
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') tick(); });
  window.addEventListener('storage', e => {
    if (e.key !== KEY) return;
    externalChange = true; $('test-form').hidden = true; screen('test-setup'); $('resume-panel').hidden = true;
    notice('This attempt changed in another tab. Reload this page to use the latest saved version.');
    $('storage-note').append(button('Reload', () => location.reload()));
  });
  async function load() {
    try {
      const responses = await Promise.all([fetch('/content/questions.json', { cache: 'no-cache' }), fetch('/content/practice-tests.json', { cache: 'no-cache' })]);
      if (responses.some(r => !r.ok)) throw Error('Question data could not load.');
      const [questions, manifest] = await Promise.all(responses.map(r => r.json()));
      if (!Array.isArray(questions) || !questions.every(C.validQuestion) || new Set(questions.map(q => q.id)).size !== questions.length || manifest.version !== 1 || !Array.isArray(manifest.mocks)) throw Error('Question data could not be verified.');
      bank = questions; papers = manifest.mocks;
      try {
        const raw = localStorage.getItem(KEY);
        if (raw) {
          saved = C.restore(raw, bank);
          if (!saved) notice('The saved attempt no longer matches the current question bank. Please start a new test.');
        }
      } catch { notice('Saved attempts are unavailable in this browser. Keep this tab open to finish.'); }
      $('test-loading').hidden = true; $('test-app').setAttribute('aria-busy', 'false'); setup();
    } catch {
      $('test-loading').hidden = true; $('test-app').setAttribute('aria-busy', 'false');
      $('test-error').hidden = false; $('test-error').textContent = 'Practice questions could not load. Please try again.';
      $('test-error').append(button('Try again', () => { $('test-error').hidden = true; $('test-loading').hidden = false; load(); }));
    }
  }
  setInterval(tick, 1000);
  load();
})();
