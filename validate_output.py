import json, sys
from datetime import datetime

def validate(data):
    errors = []
    sources = {s['id']: s for s in data.get('sources', [])}
    for sid, s in sources.items():
        if not all(s.get(k) for k in ('url', 'excerpt', 'retrieved_at')):
            errors.append(f'{sid}: incomplete source')
    ids = set()
    for lead in data.get('leads', []):
        lid = lead.get('id')
        if not lid or lid in ids:
            errors.append(f'{lid}: missing or duplicate lead id')
        ids.add(lid)
        for part in ('company', 'signal', 'contact'):
            for sid in lead.get(part, {}).get('source_ids', []):
                if sid not in sources:
                    errors.append(f'{lid}: unresolved source {sid}')
        seen = set()
        for e in lead.get('emails', []):
            address = e.get('address', '').lower()
            if address.count('@') != 1 or address in seen:
                errors.append(f'{lid}: malformed or duplicate email')
            seen.add(address)
            if e.get('provenance') not in ('published', 'pattern-derived', 'guessed'):
                errors.append(f'{lid}: email provenance missing')
            for sid in e.get('source_ids', []):
                if sid not in sources:
                    errors.append(f'{lid}: unresolved email source')
            v = e.get('verification', {})
            if v.get('status') not in ('valid', 'invalid', 'accept_all', 'unknown', 'not_checked', 'quota_exhausted', 'approval_required', 'provider_error', 'role_mailbox', 'disposable', 'webmail'):
                errors.append(f'{lid}: invalid verification status')
            if v.get('status') in ('valid', 'invalid', 'accept_all'):
                if not all(v.get(k) for k in ('provider', 'checked_at', 'approval_id', 'raw_status')):
                    errors.append(f'{lid}: missing verification evidence or approval')
            if e.get('provenance') == 'guessed' and e.get('ownership') != 'inferred':
                errors.append(f'{lid}: guessed email ownership overstated')
        if lead.get('disposition') == 'ready_for_review':
            if not lead.get('company', {}).get('icp_match') or not lead.get('company', {}).get('source_ids'):
                errors.append(f'{lid}: missing company qualification')
            if lead.get('signal', {}).get('status') != 'observed' or not lead.get('signal', {}).get('source_ids'):
                errors.append(f'{lid}: signal not evidenced')
            if not lead.get('contact', {}).get('current_role_confirmed') or not lead.get('contact', {}).get('source_ids'):
                errors.append(f'{lid}: role not evidenced')
            if not any(e.get('verification', {}).get('status') == 'valid' and e.get('dns', {}).get('status') in ('mx_present', 'implicit_mx_possible') for e in lead.get('emails', [])):
                errors.append(f'{lid}: no valid routed candidate')
    return errors

if __name__ == '__main__':
    errors = validate(json.load(open(sys.argv[1], encoding='utf-8')))
    for error in errors:
        print(error)
    sys.exit(bool(errors))
