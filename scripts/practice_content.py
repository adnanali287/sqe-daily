"""Approval-controlled early library releases and fixed full-mock manifests."""
import hashlib
import json
import re
from datetime import date


def fingerprint(entry):
    return hashlib.sha256(json.dumps({k: v for k, v in entry.items() if k not in {'approved', 'approved_hash'}}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def question_hash(question):
    return hashlib.sha256(json.dumps({k: v for k, v in question.items() if k not in {'route', 'modified', 'available_from'}}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def approved(entry):
    return entry.get('approved') is True and entry.get('approved_hash') == fingerprint(entry)


def read(root):
    path = root / 'content/practice.json'
    data = json.loads(path.read_text()) if path.exists() else {'version': 1, 'releases': [], 'mocks': []}
    if data.get('version') != 1 or any(not isinstance(data.get(k), list) for k in ['releases', 'mocks']):
        raise ValueError('Invalid practice manifest')
    for kind in ['releases', 'mocks']:
        ids = [entry.get('id') for entry in data[kind]]
        if any(not isinstance(i, str) or not re.fullmatch(r'[a-z0-9-]+', i) for i in ids) or len(ids) != len(set(ids)):
            raise ValueError(f'Invalid or duplicate {kind} IDs')
        for entry in data[kind]:
            if entry.get('approved') and not approved(entry):
                raise ValueError(f'{kind}.{entry["id"]} changed after approval')
    return data


def library(bank, data, day):
    by_id = {q['id']: q for q in bank}
    release_dates = {}
    for entry in data['releases']:
        if entry['id'] not in by_id:
            raise ValueError(f'Unknown release question {entry["id"]}')
        date.fromisoformat(entry['available_from'])
        if approved(entry) and entry.get('question_hash') == question_hash(by_id[entry['id']]):
            release_dates[entry['id']] = entry['available_from']
    result = [{**q, 'available_from': min(filter(None, [q['publish_date'], release_dates.get(q['id'])]), default=None)} for q in bank]
    return sorted((q for q in result if q['available_from'] and q['available_from'] <= day), key=lambda q: (q['available_from'], q['number']))


def mocks(bank, available, data):
    by_id = {q['id']: q for q in bank}
    available_ids = {q['id'] for q in available}
    result = []
    for entry in data['mocks']:
        if not approved(entry):
            continue
        sessions = entry.get('sessions', [])
        if len(sessions) != 2 or any(not isinstance(s, list) or len(s) != 85 for s in sessions):
            raise ValueError('A full mock requires two sessions of 85 questions')
        ids = [i for s in sessions for i in s]
        if len(set(ids)) != 170 or any(i not in by_id for i in ids):
            raise ValueError('A full mock requires 170 distinct known questions')
        if entry.get('paper') not in ['FLK1', 'FLK2'] or any(by_id[i]['flk'] != entry['paper'] for i in ids):
            raise ValueError('Full mock question paper mismatch')
        ethics = {'Ethics & Professional Conduct'}
        groups = {
            'FLK1': [{'Business Law & Practice', 'Dispute Resolution', 'Legal Services'},
                     {'Contract', 'Tort', 'Legal System of England and Wales', 'Constitutional & Administrative Law'}],
            'FLK2': [{'Wills & Administration of Estates', 'Solicitors Accounts', 'Trusts', 'Land Law'},
                     {'Property Practice', 'Solicitors Accounts', 'Criminal Law', 'Criminal Practice'}],
        }
        if any(by_id[i]['subject'] not in groups[entry['paper']][n] | ethics for n, session in enumerate(sessions) for i in session):
            raise ValueError('Full mock session subject mismatch')
        for n, session in enumerate(sessions, 1):
            for identifier in session:
                q = by_id[identifier]
                if q.get('session') and q['session'] != f'{entry["paper"]}-S{n}':
                    raise ValueError('Full mock contextual session mismatch')
                if q['subject'] == 'Solicitors Accounts' and q.get('session'):
                    context = 'Wills & Administration of Estates' if n == 1 else 'Property Practice'
                    if q.get('context_subject') != context:
                        raise ValueError('Accounts question context mismatch')
        if any(not groups[entry['paper']][n] <= {by_id[i]['subject'] for i in session} for n, session in enumerate(sessions)):
            raise ValueError('Full mock session is missing required subject coverage')
        date.fromisoformat(entry['law_cutoff'])
        if not entry.get('title') or not entry.get('source_url', '').startswith('https://sqe.sra.org.uk/'):
            raise ValueError('Full mock title and official specification source required')
        if not set(ids) <= available_ids or any(entry.get('question_hashes', {}).get(i) != question_hash(by_id[i]) for i in ids):
            continue
        result.append({k: entry[k] for k in ['id', 'title', 'paper', 'law_cutoff', 'source_url', 'sessions']})
    return result


def approve(root, label, expect):
    if not expect or not re.fullmatch(r'[a-f0-9]{12,64}', expect):
        raise ValueError('Provide the fingerprint the owner approved with --expect')
    data = json.loads((root / 'content/practice.json').read_text())
    kind, identifier = label.split('.', 1)
    if kind not in ['releases', 'mocks']:
        raise ValueError('Expected releases.ID or mocks.ID')
    entry = next(e for e in data[kind] if e['id'] == identifier)
    digest = fingerprint(entry)
    if not digest.startswith(expect):
        raise ValueError('Practice entry differs from the approved fingerprint')
    entry.update(approved=True, approved_hash=digest)
    (root / 'content/practice.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
