const assert = require('node:assert/strict');
const C = require('../assets/test-core.js');
const batch = new Set(require('../drafts/library-2027-01/composition.json').items.map(e=>e.id));
const bank = [...require('../content/questions.json'),...require('../content/library.json')].filter(q=>batch.has(q.id));
const cases = [['FLK1','',181],['FLK2','',187],['FLK1','@session-1',91],['FLK1','@session-2',90],['FLK2','@session-1',93],['FLK2','@session-2',94],['FLK1','@legal-systems',26],['ETHICS','',30],['FLK2','Solicitors Accounts',10]];
for (const [paper,subject,expected] of cases) {
  const available = C.pool(bank,paper,subject);
  assert.equal(available.length,expected,`${paper} ${subject}`);
  for (const count of [10,20]) {
    if (available.length<count) { assert.throws(()=>C.create({bank,paper,subject,count})); continue; }
    const state=C.create({bank,paper,subject,count,random:()=>0.314,timed:false});
    assert.equal(state.questions.length,count); assert.equal(new Set(state.sessions.flat()).size,count);
    assert.ok(state.questions.every(q=>available.some(a=>a.id===q.id)));
    assert.ok(C.restore(JSON.stringify(state),bank));
  }
}
const first=C.create({bank,paper:'FLK1',count:20,random:()=>0.42});
const next=C.create({bank,paper:'FLK1',count:20,random:()=>0.42,recent:first.sessions.flat()});
assert.equal(next.sessions.flat().filter(id=>first.sessions.flat().includes(id)).length,0,'prefer unseen questions where every pool has room');
for (const subject of ['Contract','Tort','Business Law & Practice','Dispute Resolution','Legal Services','Ethics & Professional Conduct']) assert.ok(first.questions.some(q=>q.subject===subject));
assert.ok(first.questions.some(q=>['Constitutional & Administrative Law','Legal System of England and Wales'].includes(q.subject)));
const manifest=require('../content/practice.json').mocks[0];
const full=C.create({bank,paper:'FLK1',mock:manifest});
assert.ok(C.restore(JSON.stringify(full),bank,Date.now(),[manifest]));
assert.equal(C.restore(JSON.stringify(full),bank,Date.now(),[]),null,'withdrawn mock cannot resume');
const swapped=JSON.parse(JSON.stringify(manifest));
[swapped.sessions[0][0],swapped.sessions[1][0]]=[swapped.sessions[1][0],swapped.sessions[0][0]];
assert.equal(C.restore(JSON.stringify(full),bank,Date.now(),[swapped]),null,'changed session membership cannot resume');
const letterFixture=Array.from({length:10},(_,i)=>({...bank[0],id:`letter-fixture-${i}`,answer:i<8?'A':'B'}));
const letterAttempt=C.create({bank:letterFixture,paper:'FLK1',count:10,random:()=>0});
assert.ok(!letterAttempt.questions.some((q,i,a)=>i>=3 && a.slice(i-3,i+1).every(x=>x.answer===q.answer)),'avoid four identical letters when the selected pool permits');
console.log('PASS: all paper/session/combined/ethics pools, insufficient pools, balanced coverage, recent-history preference and withdrawn mocks');
