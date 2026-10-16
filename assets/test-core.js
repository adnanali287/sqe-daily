(function (root) {
  'use strict';
  const VERSION = 1;
  const LETTERS = ['A', 'B', 'C', 'D', 'E'];
  const SESSION_MS = 153 * 60000;
  const BREAK_MS = 60 * 60000;
  const signature = questions => JSON.stringify(questions.map(q => [q.id, q.scenario, q.stem, q.options, q.answer, q.explanation, q.why_wrong, q.key_rule, q.verified_source_url]));
  function validQuestion(q) {
    return q && typeof q.id === 'string' && ['FLK1', 'FLK2'].includes(q.flk) && LETTERS.includes(q.answer)
      && ['scenario', 'stem', 'explanation', 'key_rule', 'subject', 'authority'].every(k => typeof q[k] === 'string' && q[k])
      && LETTERS.every(k => typeof q.options?.[k] === 'string' && q.options[k]) && /^https:\/\//.test(q.verified_source_url);
  }
  function pool(bank, paper, subject = '') {
    return bank.filter(q => validQuestion(q) && q.flk === paper && (!subject || q.subject === subject));
  }
  function shuffle(items, random = Math.random) {
    const copy = [...items];
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }
  function create({ bank, paper, subject = '', count = 10, timed = true, mock = null, now = Date.now(), random = Math.random }) {
    if (!['FLK1', 'FLK2'].includes(paper)) throw Error('Choose FLK1 or FLK2.');
    const available = pool(bank, paper, subject);
    const byId = new Map(available.map(q => [q.id, q]));
    let sessions;
    if (mock) {
      if (mock.paper !== paper || mock.sessions?.length !== 2 || mock.sessions.some(s => !Array.isArray(s) || s.length !== 85)) throw Error('This full mock is not ready.');
      const ids = mock.sessions.flat();
      if (new Set(ids).size !== 170 || ids.some(id => !byId.has(id))) throw Error('This full mock is not ready.');
      sessions = mock.sessions.map(s => shuffle(s, random));
    } else {
      if (![10, 20].includes(count) || available.length < count || byId.size !== available.length) throw Error('There are not enough distinct questions for this test.');
      sessions = [shuffle(available, random).slice(0, count).map(q => q.id)];
    }
    const questions = sessions.flat().map(id => byId.get(id));
    return { version: VERSION, title: mock?.title || `${paper}${subject ? ` · ${subject}` : ''} mini test`,
      lawCutoff: mock?.law_cutoff || null, mode: mock ? 'full' : 'mini', paper, timed, sessions, questions,
      signature: signature(questions), session: 0, index: 0, answers: {}, flags: {}, status: 'active',
      startedAt: now, finishedAt: null, deadline: timed ? now + (mock ? SESSION_MS : count * 108000) : null, breakUntil: null };
  }
  function currentIds(state) { return state.sessions[state.session]; }
  function answer(state, id, letter) {
    if (state.status !== 'active' || !currentIds(state).includes(id) || !LETTERS.includes(letter)) return;
    state.answers[id] = letter;
  }
  function finish(state, now = Date.now()) {
    if (state.status !== 'active') return state;
    if (state.mode === 'full' && state.session === 0) {
      state.status = 'break';
      state.breakUntil = now + BREAK_MS;
    } else {
      state.status = 'results';
      state.finishedAt = now;
    }
    state.deadline = null;
    return state;
  }
  function advance(state, now = Date.now()) {
    if (state.status !== 'break' || (state.timed && now < state.breakUntil)) return false;
    state.session = 1; state.index = 0; state.status = 'active';
    state.deadline = state.timed ? state.breakUntil + SESSION_MS : null;
    state.breakUntil = null;
    return true;
  }
  // Deadlines are absolute, including break/session 2, so closing a tab cannot pause a timed mock.
  function reconcile(state, now = Date.now()) {
    for (let i = 0; i < 3; i++) {
      if (state.status === 'active' && state.timed && now >= state.deadline) finish(state, state.deadline);
      else if (state.status === 'break' && state.timed && now >= state.breakUntil) advance(state, now);
      else break;
    }
    return state;
  }
  function results(state) {
    const subjects = {};
    let correct = 0, answered = 0;
    for (const q of state.questions) {
      const row = subjects[q.subject] ||= { total: 0, correct: 0, answered: 0 };
      row.total++;
      if (state.answers[q.id]) { row.answered++; answered++; }
      if (state.answers[q.id] === q.answer) { row.correct++; correct++; }
    }
    return { total: state.questions.length, correct, answered, unanswered: state.questions.length - answered, subjects };
  }
  function restore(raw, bank, now = Date.now()) {
    try {
      const state = JSON.parse(raw);
      if (state.version !== VERSION || !['mini', 'full'].includes(state.mode) || !['active', 'break', 'results'].includes(state.status)
        || typeof state.timed !== 'boolean' || !Array.isArray(state.sessions) || !Array.isArray(state.questions)
        || !state.answers || Array.isArray(state.answers) || !state.flags || Array.isArray(state.flags) || !Number.isInteger(state.session) || !Number.isInteger(state.index)) return null;
      if (state.sessions.length !== (state.mode === 'full' ? 2 : 1) || state.sessions.some(s => !Array.isArray(s) || (state.mode === 'full' ? s.length !== 85 : ![10, 20].includes(s.length)))) return null;
      const ids = state.sessions.flat();
      const map = new Map(bank.filter(validQuestion).map(q => [q.id, q]));
      if (new Set(ids).size !== ids.length || ids.some(id => !map.has(id) || map.get(id).flk !== state.paper)) return null;
      const questions = ids.map(id => map.get(id));
      if (state.signature !== signature(questions) || signature(state.questions) !== state.signature) return null;
      if (state.session < 0 || state.session >= state.sessions.length || state.index < 0 || state.index >= currentIds(state).length) return null;
      if (Object.entries(state.answers).some(([id, letter]) => !ids.includes(id) || !LETTERS.includes(letter))) return null;
      if (Object.entries(state.flags).some(([id, flag]) => !ids.includes(id) || typeof flag !== 'boolean')) return null;
      if (state.timed && ((state.status === 'active' && !Number.isFinite(state.deadline)) || (state.status === 'break' && !Number.isFinite(state.breakUntil)))) return null;
      state.questions = questions;
      return reconcile(state, now);
    } catch { return null; }
  }
  const api = { VERSION, SESSION_MS, BREAK_MS, signature, validQuestion, pool, create, answer, currentIds, finish, advance, reconcile, results, restore };
  if (typeof module !== 'undefined') module.exports = api;
  else root.SQETests = api;
})(typeof window === 'undefined' ? this : window);
