#!/usr/bin/env python3
"""
Script to validate and apply safe fixes to n8n workflow JSON files under
3.opena4_telegram/workflows.

Usage:
  - Dry run (default): python3 scripts/fix_workflows.py
  - Apply changes:      python3 scripts/fix_workflows.py --apply

Backups are written to .bak/ with a timestamped filename before modification.
"""

import json
import glob
import os
import shutil
import argparse
from datetime import datetime, timezone

WORKFLOW_GLOB = '3.opena4_telegram/workflows/*.json'
BACKUP_DIR = '3.opena4_telegram/workflows/.bak'


def safe_fix_workflow(obj):
    """Return (new_obj, changes_list)"""
    changed = False
    changes = []

    # Top-level defaults
    if 'active' not in obj:
        obj['active'] = False
        changes.append("added top-level 'active': false")
        changed = True

    if 'createdAt' not in obj:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        obj['createdAt'] = now
        obj['updatedAt'] = now
        changes.append(f"added timestamps createdAt/updatedAt: {now}")
        changed = True
    # Add default versionId required by newer n8n versions
    if 'versionId' not in obj:
        obj['versionId'] = 1
        changes.append("added top-level 'versionId' = 1")
        changed = True

    # Nodes
    nodes = obj.get('nodes', [])
    for i, n in enumerate(nodes):
        nid = n.get('id') or f'index_{i}'
        if 'parameters' not in n:
            n['parameters'] = {}
            changes.append(f"node {nid}: added empty 'parameters'")
            changed = True

        # Normalize undefined or null-like values inside parameters
        params = n.get('parameters', {})
        for k, v in list(params.items()):
            if v is None or (isinstance(v, str) and v.strip().lower() == 'undefined'):
                params[k] = ''
                changes.append(f"node {nid}: parameter '{k}' had undefined/null, set to empty string")
                changed = True

        # Ensure common node fields exist
        if 'typeVersion' not in n:
            n['typeVersion'] = 1
            changes.append(f"node {nid}: set 'typeVersion' = 1")
            changed = True

        if 'position' not in n:
            n['position'] = [0, 0]
            changes.append(f"node {nid}: added default position [0,0]")
            changed = True

        # Webhook node specific
        if n.get('type') == 'n8n-nodes-base.webhook':
            p = n['parameters']
            if 'path' not in p or not isinstance(p.get('path'), str) or not p.get('path').strip():
                default_path = n.get('name', 'webhook').lower().replace(' ', '-')
                p['path'] = default_path
                changes.append(f"node {nid}: webhook path missing, set to '{default_path}'")
                changed = True
            if 'httpMethod' not in p:
                p['httpMethod'] = 'POST'
                changes.append(f"node {nid}: webhook httpMethod missing, set to 'POST'")
                changed = True

        # httpRequest node specific
        if n.get('type') == 'n8n-nodes-base.httpRequest':
            p = n['parameters']
            if 'url' not in p or not isinstance(p.get('url'), str) or not p.get('url').strip():
                p['url'] = 'http://127.0.0.1/'
                changes.append(f"node {nid}: httpRequest URL missing, set to 'http://127.0.0.1/'")
                changed = True
            if 'method' not in p:
                p['method'] = 'GET'
                changes.append(f"node {nid}: httpRequest method missing, set to 'GET'")
                changed = True
            if 'jsonParameters' not in p:
                p['jsonParameters'] = False
                changes.append(f"node {nid}: set 'jsonParameters' = False")
                changed = True

        # ensure name and id present
        if 'name' not in n or not n.get('name'):
            guess = n.get('type', 'node')
            n['name'] = guess
            changes.append(f"node {nid}: missing name, set to '{guess}'")
            changed = True
        if 'id' not in n or not n.get('id'):
            # create an id from name and index
            new_id = f"{n['name']}_{i}"
            n['id'] = new_id
            changes.append(f"node missing id, set id = '{new_id}'")
            changed = True

    # Connections check: ensure keys exist as node id or name
    node_names = {n['name'] for n in nodes if 'name' in n}
    node_ids = {n['id'] for n in nodes if 'id' in n}
    conns = obj.get('connections', {})
    for k in list(conns.keys()):
        if k not in node_names and k not in node_ids:
            # try to map by id->name or name->id equivalence not possible; create an alias mapping
            # we'll try to find a node with id starting with k or name starting with k
            matched = None
            for n in nodes:
                if n.get('id') == k or n.get('name') == k:
                    matched = k
                    break
            if not matched:
                # leave as-is but record
                changes.append(f"connections key '{k}' does not match any node id/name")

    return obj, changes


def main(apply=False):
    files = sorted(glob.glob(WORKFLOW_GLOB))
    report = {}
    if not files:
        print('No workflow files found')
        return 1

    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)

    for f in files:
        data = json.load(open(f, 'r', encoding='utf-8'))
        new, changes = safe_fix_workflow(data)
        if changes:
            report[f] = changes
            if apply:
                # backup
                base = os.path.basename(f)
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
                backup_name = os.path.join(BACKUP_DIR, f + '.' + stamp + '.bak')
                # ensure parent dir exists
                os.makedirs(os.path.dirname(backup_name), exist_ok=True)
                shutil.copyfile(f, backup_name)
                with open(f, 'w', encoding='utf-8') as fh:
                    json.dump(new, fh, indent=2, ensure_ascii=False)
                print(f"Applied {len(changes)} change(s) to {f}; backup: {backup_name}")
            else:
                print(f"Would apply {len(changes)} change(s) to {f}:")
                for c in changes:
                    print('  - ' + c)
        else:
            print(f"No changes needed for {f}")

    if not apply:
        print('\nDry-run complete. Run with --apply to write changes and create backups.')
    else:
        print('\nApply complete. Review backups in .bak/')

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Write changes to files')
    args = parser.parse_args()
    exit(main(apply=args.apply))
