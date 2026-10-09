import argparse, csv, hashlib, importlib, json, re, time
from datetime import datetime, timezone, date
from pathlib import Path

CHECKER = 'https://emails-checker.net/bulk-email-checker'

def now():
    return datetime.now(timezone.utc).isoformat()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

def domain_clean(value):
    value = str(value or '').strip().lower().rstrip('.')
    if not re.fullmatch(r'[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\.[a-z]{2,63}', value):
        return None
    return value

def syntax(address):
    if not isinstance(address, str) or len(address) > 254 or address.count('@') != 1:
        return False
    local, domain = address.rsplit('@', 1)
    return bool(local and len(local) <= 64 and not local.startswith('.') and not local.endswith('.') and '..' not in local and re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+", local) and domain_clean(domain))

def candidates(contact, domain):
    result = []
    for item in contact.get('published_emails', []):
        address = item.get('address', '').lower()
        if syntax(address) and address.rsplit('@', 1)[1] == domain and item.get('source_ids'):
            result.append({'address': address, 'provenance': 'published', 'ownership': 'source_asserted', 'source_ids': item['source_ids']})
    first, last = contact.get('first_name', ''), contact.get('last_name', '')
    if contact.get('name_parse_confirmed') and re.fullmatch(r'[A-Za-z]+', first) and re.fullmatch(r'[A-Za-z]+', last):
        f, l = first.lower(), last.lower()
        supported = []
        for p in contact.get('patterns', []):
            if p.get('pattern') in ('first.last', 'flast', 'first') and p.get('source_ids'):
                supported.append(p)
        patterns = supported + [{'pattern': p, 'source_ids': []} for p in ('first.last', 'flast', 'first')]
        for p in patterns:
            local = {'first.last': f'{f}.{l}', 'flast': f[0]+l, 'first': f}[p['pattern']]
            result.append({'address': f'{local}@{domain}', 'provenance': 'pattern-derived' if p['source_ids'] else 'guessed', 'ownership': 'inferred', 'source_ids': p['source_ids']})
    unique = {}
    for e in result:
        unique.setdefault(e['address'], e)
    return list(unique.values())[:3]

def score(lead, today, window=90):
    company, signal, contact = lead['company'], lead['signal'], lead['contact']
    icp = 25 if company.get('icp_match') and company.get('source_ids') else 0
    observed = signal.get('status') == 'observed' and bool(signal.get('source_ids'))
    relevance = 20 if observed and signal.get('relevance_confirmed') else 0
    age = None
    try:
        age = (today - date.fromisoformat(signal['event_date'])).days
    except (ValueError, KeyError, TypeError):
        pass
    fresh = 15 if observed and age is not None and 0 <= age <= min(30, window) else 8 if observed and age is not None and 0 <= age <= window else 0
    role = 20 if contact.get('current_role_confirmed') and contact.get('role_match') and contact.get('source_ids') else 0
    primary = 10 if observed and signal.get('source_quality') == 'primary' else 5 if observed else 0
    exact = any(e['verification']['status'] == 'valid' for e in lead['emails'])
    published = any(e['provenance'] == 'published' for e in lead['emails'])
    email = 10 if exact else 4 if published else 0
    parts = {'icp_fit': icp, 'signal_relevance': relevance, 'freshness': fresh, 'role_fit': role, 'source_quality': primary, 'email_evidence': email}
    hard = bool(icp and relevance and fresh and role and company.get('domain') and not lead.get('suppressed'))
    total = sum(parts.values())
    ready = hard and exact and total >= 70
    return {'total': total, 'components': parts, 'qualified': hard, 'tier': 'A' if total >= 85 else 'B' if total >= 70 else 'C', 'disposition': 'ready_for_review' if ready else 'needs_review', 'not_probability': True}

class Engine:
    def __init__(self, adapter, allow_ddg=False):
        self.adapter = adapter
        self.allow_ddg = allow_ddg
        self.started = time.monotonic()
        self.queries = 0
        self.attempts = 0
        self.sources = {}
        self.audit = []
        self.blockers = []
        self.dns_cache = {}
        self.approvals_used = set()
        self.limits = {'search_queries': 60, 'verification_attempts': 20, 'wall_clock_minutes': 30, 'companies': 10, 'contacts_per_company': 2}

    def event(self, stage, **fields):
        self.audit.append({'at': now(), 'stage': stage, **fields})

    def check(self):
        if time.monotonic()-self.started >= self.limits['wall_clock_minutes']*60:
            raise RuntimeError('deadline_reached')

    def search(self, query):
        self.check()
        if self.queries >= self.limits['search_queries']:
            raise RuntimeError('search_budget_reached')
        self.queries += 1
        try:
            rows = self.adapter.search(query, 5)
        except Exception:
            if not self.allow_ddg:
                self.blockers.append('search_failed_or_missing')
                return []
            try:
                from ddgs import DDGS
                rows = [{'url': x['href'], 'title': x.get('title',''), 'snippet': x.get('body','')} for x in DDGS().text(query, backend='duckduckgo', max_results=5)]
            except Exception:
                self.blockers.append('duckduckgo_failed')
                return []
        found = []
        for row in rows:
            if not row.get('url') or not row.get('snippet'):
                continue
            sid = digest({'url':row['url'],'snippet':row['snippet']})[:16]
            record = {'id': sid, 'url': row['url'], 'title': row.get('title',''), 'excerpt': row['snippet'], 'retrieved_at': now(), 'source_type':'search_snippet'}
            self.sources[sid] = record
            found.append(record)
        self.event('search', query=query, count=len(found))
        return found

    def enrich(self, rows):
        if not hasattr(self.adapter, 'fetch'):
            return rows
        for row in rows:
            self.check()
            if 'linkedin.com' in row['url'].lower():
                continue
            try:
                text = self.adapter.fetch(row['url'])
                if isinstance(text,str) and text.strip():
                    row = dict(row, excerpt=text[:16000], source_type='permitted_page')
                    self.sources[row['id']] = row
            except Exception:
                self.blockers.append('page_unavailable')
        return [self.sources[r['id']] for r in rows]

    def extract(self, kind, rows, context):
        if not rows:
            return []
        self.check()
        items = self.adapter.extract(kind, rows, context)
        if not isinstance(items,list):
            raise ValueError('extract must return list')
        valid = []
        allowed = {r['id'] for r in rows}
        for item in items:
            refs = item.get('source_ids', [])
            if refs and set(refs).issubset(allowed):
                valid.append(item)
        return valid

    def dns(self, domain):
        if domain in self.dns_cache:
            return self.dns_cache[domain]
        self.check()
        try:
            if hasattr(self.adapter,'dns'):
                status = self.adapter.dns(domain)
            else:
                import dns.resolver
                try:
                    answer = dns.resolver.resolve(domain, 'MX', lifetime=5)
                    status = 'null_mx' if any(str(x.exchange) == '.' and x.preference == 0 for x in answer) else 'mx_present'
                except dns.resolver.NoAnswer:
                    status = 'no_route'
                    for typ in ('A','AAAA'):
                        try:
                            if dns.resolver.resolve(domain,typ,lifetime=5):
                                status = 'implicit_mx_possible'
                                break
                        except dns.resolver.NoAnswer:
                            continue
                except dns.resolver.NXDOMAIN:
                    status = 'nxdomain'
            if status not in ('mx_present','implicit_mx_possible','null_mx','nxdomain','no_route','unknown'):
                status = 'unknown'
        except Exception:
            status = 'unknown'
        self.dns_cache[domain] = {'status':status, 'checked_at':now()}
        return self.dns_cache[domain]

    def verify(self, email, plan):
        result = {'status':'not_checked','provider':None,'checked_at':None,'raw_status':None,'approval_id':None}
        v = plan.get('verification',{})
        if not v.get('enabled') or not hasattr(self.adapter,'verify'):
            return result
        if v.get('scope') != 'mailbox':
            return dict(result, status='not_checked', blocker='provider_not_mailbox_verifier')
        quota = min(self.limits['verification_attempts'], max(0,int(v.get('remaining_free_quota',0))))
        if self.attempts >= quota:
            return dict(result,status='quota_exhausted')
        action = {'gate':'VERIFY_DISCLOSURE','provider':v['provider'],'tool':v['tool'],'arguments':{'email':email},'cost_ceiling_usd':0}
        self.check()
        approval = self.adapter.approve(action) if hasattr(self.adapter,'approve') else None
        token = approval.get('id') if isinstance(approval,dict) else None
        if not token or token in self.approvals_used or approval.get('action_hash') != digest(action) or approval.get('approved') is not True:
            return dict(result,status='approval_required')
        self.approvals_used.add(token)
        self.attempts += 1
        self.event('verification', provider=v['provider'], action_hash=digest(action), approval_id=token)
        try:
            self.check()
            raw = self.adapter.verify(action, approval)
            status = raw.get('status','unknown')
            if status not in ('valid','invalid','accept_all','webmail','disposable','unknown'):
                status = 'unknown'
            if raw.get('accept_all'):
                status = 'accept_all'
            if raw.get('role_mailbox'):
                status = 'role_mailbox'
            return {'status':status,'provider':v['provider'],'checked_at':now(),'raw_status':str(raw.get('status','unknown')),'approval_id':token}
        except Exception:
            return dict(result,status='provider_error',provider=v['provider'],approval_id=token)

    def run(self, brief, project, suppression):
        # Semantic PAL execution is owned by the trusted harness adapter.
        pal = self.adapter.pal(brief, project)
        if pal.get('protocol') != 'Parse → Ambiguity Scan → Latent Intent → Expand → Compile':
            raise ValueError('PAL protocol mismatch')
        plan = pal['compiled_plan']
        if plan.get('spend_usd',0) != 0:
            raise ValueError('paid runs are out of scope')
        if pal.get('approval_sensitive_open_decisions'):
            return {'project_id':project,'pal':pal,'sources':[],'leads':[],'blockers':['clarification_required'],'audit':[]}
        for key, maximum in list(self.limits.items()):
            value = plan.get('limits',{}).get(key, maximum)
            if not isinstance(value,int) or isinstance(value,bool) or value < 1:
                raise ValueError('invalid limit')
            self.limits[key] = min(value,maximum)
        leads, seen = [], set()
        today = datetime.now(timezone.utc).date()
        try:
            companies = []
            for hypothesis in plan['signals']:
                for query in hypothesis['queries']:
                    rows = self.enrich(self.search(query))
                    companies.extend(self.extract('companies',rows,{'plan':plan,'hypothesis':hypothesis}))
            for item in companies:
                domain = domain_clean(item.get('domain'))
                if not domain or domain in seen or len(seen) >= self.limits['companies']:
                    continue
                seen.add(domain)
                if domain in suppression['domains']:
                    continue
                company = dict(item,domain=domain)
                name = company['name']
                rows=[]
                for role in plan['roles']:
                    rows += self.enrich(self.search(f'"{name}" "{role}" leadership'))
                    rows += self.search(f'site:linkedin.com/in "{name}" "{role}"')
                contacts = self.extract('contacts',rows,{'company':company,'plan':plan})
                contact_seen=set()
                for contact in contacts:
                    ident = contact.get('profile_url') or contact.get('name','').casefold()
                    if not ident or ident in contact_seen or len(contact_seen)>=self.limits['contacts_per_company']:
                        continue
                    contact_seen.add(ident)
                    emailrows=self.enrich(self.search(f'"{contact["name"]}" "{name}" email'))
                    research=self.extract('email_evidence',emailrows,{'contact':contact,'company':company})
                    contact['published_emails']=[{'address':r['address'],'source_ids':r['source_ids']} for r in research if r.get('address')]
                    contact['patterns']=[r for r in research if r.get('pattern')]
                    emails=[]
                    for email in candidates(contact,domain):
                        if email['address'] in suppression['emails']:
                            continue
                        if email['provenance'] != 'published':
                            proof=self.enrich(self.search('"'+email['address']+'"'))
                            exact=self.extract('email_evidence',proof,{'contact':contact,'company':company})
                            for r in exact:
                                if r.get('address','').lower()==email['address']:
                                    email.update(provenance='published',ownership='source_asserted',source_ids=r['source_ids'])
                        email['dns']=self.dns(domain)
                        email['verification']=self.verify(email['address'],plan) if email['dns']['status'] in ('mx_present','implicit_mx_possible') else {'status':'not_checked','provider':None,'checked_at':None,'raw_status':None,'approval_id':None}
                        emails.append(email)
                        if email['verification']['status']=='valid':
                            break
                    signal=company.get('signal',{})
                    # Only corroborated fetched-page claims qualify; snippets remain discovery evidence.
                    for claim in (company,signal,contact):
                        refs=claim.get('source_ids',[])
                        grounded=bool(refs) and all(s in self.sources for s in refs)
                        pages=grounded and any(self.sources[s]['source_type']=='permitted_page' for s in refs)
                        if not pages:
                            if claim is company: claim['icp_match']=False
                            if claim is signal: claim['status']='hypothesis'
                            if claim is contact: claim['current_role_confirmed']=False
                    lead={'id':digest({'domain':domain,'contact':ident})[:16],'company':company,'signal':signal,'contact':contact,'emails':emails,'suppressed':False}
                    lead['scoring']=score(lead,today,plan.get('signal_age_days',90))
                    lead['disposition']=lead['scoring']['disposition']
                    lead['blockers']=[] if lead['disposition']=='ready_for_review' else ['qualification_or_mailbox_evidence_incomplete']
                    leads.append(lead)
        except RuntimeError as exc:
            self.blockers.append(str(exc))
        except Exception:
            self.blockers.append('adapter_contract_or_processing_error')
        leads.sort(key=lambda x:(x['scoring']['qualified'],x['scoring']['total']),reverse=True)
        return {'project_id':project,'pal':pal,'sources':list(self.sources.values()),'leads':leads,'blockers':sorted(set(self.blockers)),'audit':self.audit,'metrics':{'queries':self.queries,'verification_attempts':self.attempts,'elapsed_seconds':round(time.monotonic()-self.started,2)}}

def export(data, folder):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    (folder/'leads.json').write_text(json.dumps(data,indent=2))
    (folder/'plan.json').write_text(json.dumps(data.get('pal',{}),indent=2))
    fields=['lead_id','company','contact','title','email','provenance','verification_status','score','tier','disposition']
    pending=[]
    with (folder/'leads.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for lead in data['leads']:
            for e in lead['emails'] or [{}]:
                row=dict(zip(fields,[lead['id'],lead['company']['name'],lead['contact']['name'],lead['contact'].get('title',''),e.get('address',''),e.get('provenance',''),e.get('verification',{}).get('status','not_checked'),lead['scoring']['total'],lead['scoring']['tier'],lead['disposition']]))
                writer.writerow({k:("'"+str(v) if str(v).startswith(('=','+','-','@')) else v) for k,v in row.items()})
                if e.get('address') and e.get('dns',{}).get('status') in ('mx_present','implicit_mx_possible'):
                    pending.append(e['address'])
    (folder/'checker-candidates.txt').write_text('\n'.join(sorted(set(pending))))
    (folder/'checker-handoff.json').write_text(json.dumps({'url':CHECKER,'mode':'manual_user_submission_only','captcha':'human_required','scope':'syntax_mx_only','upload_not_authorized_by_export':True,'max_addresses_per_run':5000,'candidate_count':len(set(pending))},indent=2))
    counts={s:sum(e['verification']['status']==s for l in data['leads'] for e in l['emails']) for s in ('valid','accept_all','not_checked','approval_required','quota_exhausted')}
    (folder/'run-report.md').write_text('# Prospecting run\n\n'+f"Leads: {len(data['leads'])}\n\nVerification counts: {counts}\n\nBlockers: {data['blockers']}\n\n"+'Scores prioritize review; they are not purchase probabilities. No outreach or checker upload was performed. Syntax/MX pre-check does not prove mailbox existence.\n')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--adapter',default='demo_adapter')
    p.add_argument('--brief',required=True)
    p.add_argument('--project',required=True)
    p.add_argument('--out',default='run-output')
    p.add_argument('--suppression')
    p.add_argument('--allow-ddg',action='store_true',help='Only enable after source-permission review; not an official DuckDuckGo API.')
    a=p.parse_args()
    try:
        adapter=importlib.import_module(a.adapter)
    except ModuleNotFoundError:
        adapter=importlib.import_module('demo_adapter')
    suppression=json.loads(Path(a.suppression).read_text()) if a.suppression else {'domains':[],'emails':[]}
    suppression={'domains':{str(x).lower() for x in suppression.get('domains',[])},'emails':{str(x).lower() for x in suppression.get('emails',[])}}
    data=Engine(adapter,a.allow_ddg).run(a.brief,a.project,suppression)
    if not a.suppression: data['blockers'].append('suppression_screening_incomplete')
    export(data,a.out)
    print(json.dumps({'leads':len(data['leads']),'blockers':data['blockers']}))

if __name__=='__main__':
    main()
