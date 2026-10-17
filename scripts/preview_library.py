"""Build an isolated approval preview; never approve real content or publish."""
import argparse
import json
import shutil
from pathlib import Path
from unittest.mock import patch
import generate as g
import practice_content as p


def build_preview(destination):
    destination = Path(destination).resolve()
    if destination == g.ROOT or g.ROOT in destination.parents:
        raise ValueError('Preview destination must be outside the repository')
    destination.mkdir(parents=True, exist_ok=True)
    for name in ['scripts', 'content', 'assets']:
        shutil.copytree(g.ROOT / name, destination / name, dirs_exist_ok=True)
    for name in ['CNAME', '.nojekyll']:
        shutil.copy2(g.ROOT / name, destination / name)
    data = json.loads((destination / 'content/practice.json').read_text())
    for entry in data['releases']:
        entry['available_from'] = g.london_today()
    for entry in data['releases'] + data['mocks']:
        entry.update(approved=True, approved_hash=p.fingerprint(entry))
    (destination / 'content/practice.json').write_text(json.dumps(data))
    pages = json.loads((destination / 'content/pages.json').read_text())
    for name, proposal in json.loads((destination / 'content/library-editorial-proposals.json').read_text()).items():
        proposal.update(approved=True, approved_hash=g.content_hash(proposal, g.APPROVAL_FIELDS))
        pages['pages'][name] = proposal
    (destination / 'content/pages.json').write_text(json.dumps(pages))
    with patch.object(g, 'ROOT', destination):
        g.generate(g.london_today(), True, False)
    print('LOCAL REVIEW PREVIEW ONLY. Synthetic approvals exist only in:', destination)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination')
    build_preview(parser.parse_args().destination)
