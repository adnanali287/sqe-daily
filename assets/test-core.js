(function (root) {
  'use strict';
  const VERSION = 1;
  const LETTERS = ['A', 'B', 'C', 'D', 'E'];
  const SESSION_MS = 153 * 60000;
  const BREAK_MS = 60 * 60000;
  const signature = questions => JSON.stringify(questions.map(q => [q.id, q.flk, q.subject, q.session, q.context_subject, q.title, q.scenario, q.stem, q.options, q.answer, q.explanation, q.why_wrong, q.key_rule, q.authority, q.verified_source_url]));
  function validQuestion(q) {
    return q && typeof q.id === 'string' && ['FLK1', 'FLK2'].includes(q.flk) && LETTERS.includes(q.answer)
      && ['scenario', 'stem', 'explanation', 'key_rule', 'subject', 'authority'].every(k => typeof q[k] === 'string' && q[k])
      && LETTERS.every(k => typeof q.options?.[k] === 'string' && q.options[k]) && /^https:\/\//.test(q.verified_source_url);
  }
  function pool(bank, paper, subject = '') {
    return bank.filter(q => {
      if (!validQuestion(q) || (paper === 'ETHICS' ? q.subject !== 'Ethics & Professional Conduct' : q.flk !== paper)) return false;
      if (!subject) return true;
      if (subject.startsWith('@session-')) return q.session === `${paper}-S${subject.slice(-1)}`;
      if (subject === '@legal-systems') return ['Legal System of England and Wales', 'Constitutional & Administrative Law'].includes(q.subject);
      return q.subject === subject;
    });
  }
  const group = q => ['Legal System of England and Wales', 'Constitutional & Administrative Law'].includes(q.subject) ? 'Legal Systems' : q.subject;
  const weights = {'Business Law & Practice':28, 'Dispute Resolution':28, 'Legal Services':22, Contract:28, Tort:27, 'Legal Systems':24,
    'Wills & Administration of Estates':22, 'Solicitors Accounts':8, Trusts:26, 'Land Law':26, 'Property Practice':22, 'Criminal Law':26, 'Criminal Practice':26, 'Ethics & Professional Conduct':14};
  function sample(available, count, random, recent) {
    const sessionMix = new Set(available.map(q=>q.session)).size === 1 && available[0]?.session;
    const weight = key => key === 'Ethics & Professional Conduct'
      ? sessionMix ? sessionMix === 'FLK1-S2' ? 6 : 7 : available[0]?.flk === 'FLK1' ? 13 : 14
      : key === 'Solicitors Accounts' && sessionMix ? 4 : weights[key] || 1;
    const buckets = new Map();
    for (const q of shuffle(available, random)) { const key = group(q); if (!buckets.has(key)) buckets.set(key, []); buckets.get(key).push(q); }
    // Allocate subject quotas first; recency and difficulty rank within each quota.
    const keys = [...buckets.keys()], quota = Object.fromEntries(keys.map(k => [k, count === 20 ? 1 : 0]));
    const totalWeight = keys.reduce((n,k) => n + weight(k), 0);
    while (Object.values(quota).reduce((a,b)=>a+b,0) < count) {
      const eligible = keys.filter(k => quota[k] < buckets.get(k).length);
      eligible.sort((a,b)=>(count*weight(b)/totalWeight-quota[b])-(count*weight(a)/totalWeight-quota[a]));
      quota[eligible[0]]++;
    }
    const selected = [], usedDifficulty = {easy:0,medium:0,hard:0}, target = {easy:count*.25,medium:count*.55,hard:count*.2};
    const recency = q => { const i = recent.indexOf(q.id); return i < 0 ? -1 : i; };
    for (const key of shuffle(keys, random)) {
      const candidates = buckets.get(key);
      for (let i=0; i<quota[key]; i++) {
        candidates.sort((a,b)=>recency(a)-recency(b) || ((target[b.difficulty]||0)-(usedDifficulty[b.difficulty]||0))-((target[a.difficulty]||0)-(usedDifficulty[a.difficulty]||0)));
        const q = candidates.shift(); selected.push(q); usedDifficulty[q.difficulty] = (usedDifficulty[q.difficulty]||0)+1;
      }
    }
    const letters = new Map(LETTERS.map(letter=>[letter,shuffle(selected.filter(q=>q.answer===letter),random)]));
    const ordered = [];
    while (ordered.length < count) {
      const last = ordered.at(-1)?.answer;
      const blocked = ordered.length >= 3 && ordered.slice(-3).every(q=>q.answer===last) ? last : null;
      const remaining = shuffle(LETTERS.filter(letter=>letters.get(letter).length),random);
      const eligible = remaining.filter(letter=>letter !== blocked);
      const choices = eligible.length ? eligible : remaining;
      choices.sort((a,b)=>letters.get(b).length-letters.get(a).length);
      ordered.push(letters.get(choices[0]).pop());
    }
    return ordered;
  }
  function shuffle(items, random = Math.random) {
    const copy = [...items];
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }
  function create({ bank, paper, subject = '', count = 10, timed = true, mock = null, now = Date.now(), random = Math.random, recent = [] }) {
    if (!['FLK1', 'FLK2', 'ETHICS'].includes(paper) || (mock && paper === 'ETHICS')) throw Error('Choose FLK1 or FLK2.');
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
      sessions = [sample(available, count, random, recent).map(q => q.id)];
    }
    const questions = sessions.flat().map(id => byId.get(id));
    const poolName = subject.startsWith('@session-') ? `Session ${subject.slice(-1)}` : subject === '@legal-systems' ? 'Legal Systems' : subject;
    return { version: VERSION, title: mock?.title || `${paper === 'ETHICS' ? 'Ethics · both papers' : paper}${poolName ? ` · ${poolName}` : ''} mini test`,
      lawCutoff: mock?.law_cutoff || null, mockId: mock?.id || null, mode: mock ? 'full' : 'mini', paper, timed, sessions, questions,
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
  function restore(raw, bank, now = Date.now(), mocks = null) {
    try {
      const state = JSON.parse(raw);
      if (state.version !== VERSION || !['mini', 'full'].includes(state.mode) || !['active', 'break', 'results'].includes(state.status)
        || typeof state.timed !== 'boolean' || !Array.isArray(state.sessions) || !Array.isArray(state.questions)
        || !state.answers || Array.isArray(state.answers) || !state.flags || Array.isArray(state.flags) || !Number.isInteger(state.session) || !Number.isInteger(state.index)) return null;
      if (state.sessions.length !== (state.mode === 'full' ? 2 : 1) || state.sessions.some(s => !Array.isArray(s) || (state.mode === 'full' ? s.length !== 85 : ![10, 20].includes(s.length)))) return null;
      const ids = state.sessions.flat();
      if (state.mode === 'full' && mocks !== null) {
        const manifest = mocks.find(m=>m.id === state.mockId && m.paper === state.paper && m.law_cutoff === state.lawCutoff);
        if (!manifest || manifest.sessions.some((session,n)=>session.length !== state.sessions[n].length || session.some(id=>!state.sessions[n].includes(id)))) return null;
      }
      const map = new Map(bank.filter(validQuestion).map(q => [q.id, q]));
      if (new Set(ids).size !== ids.length || ids.some(id => !map.has(id) || (state.paper === 'ETHICS' ? map.get(id).subject !== 'Ethics & Professional Conduct' : map.get(id).flk !== state.paper))) return null;
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
