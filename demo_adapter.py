from datetime import date

def pal(brief, project):
    return {'protocol':'Parse → Ambiguity Scan → Latent Intent → Expand → Compile','mode':'synthetic_demo','parse':{'brief':brief},'ambiguity_scan':{'defaults':['demo only']},'latent_intent':{'inferred':['professional prospect research']},'expand':{'signals':['hiring']},'approval_sensitive_open_decisions':[], 'compiled_plan':{'roles':['RevOps'],'signals':[{'id':'hiring','queries':['demo hiring']}],'signal_age_days':90,'spend_usd':0,'verification':{'enabled':False}}}

def search(query, limit):
    return [{'url':'https://example.com/demo','title':'Synthetic company evidence','snippet':'Synthetic company hiring RevOps, with Alex Rivera as owner.'}]

def fetch(url):
    return 'Synthetic evidence. Fictional Example Co hires RevOps. Alex Rivera, Head of RevOps. No real company or person is asserted.'

def extract(kind, rows, context):
    ids=[rows[0]['id']]
    if kind=='companies':
        return [{'name':'Fictional Example Co','domain':'example.com','icp_match':True,'source_ids':ids,'signal':{'status':'observed','event_date':date.today().isoformat(),'relevance_confirmed':True,'source_quality':'primary','source_ids':ids}}]
    if kind=='contacts':
        return [{'name':'Alex Rivera','first_name':'Alex','last_name':'Rivera','name_parse_confirmed':True,'title':'Head of RevOps','current_role_confirmed':True,'role_match':True,'source_ids':ids}]
    return []

def dns(domain):
    return 'mx_present'
