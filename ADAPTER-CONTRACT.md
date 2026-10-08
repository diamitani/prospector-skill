# Trusted Harness Adapter Contract

The Python runtime automatically orchestrates research. Natural-language PAL interpretation and evidence extraction require the real harness model; they are not implemented with regex or a hidden provider key. The included runtime.demo_adapter is synthetic. Create a trusted module binding these functions to actual tools with their documented schemas.

| Function | Return contract |
|---|---|
| pal(brief, project) | PAL stages and compiled_plan, using PAL-PROTOCOL.md |
| search(query, limit) | List of {url,title,snippet}; public permitted discovery only |
| fetch(url), optional | Permitted source text, with redirect/IP/access checks, source permissions and timeout; must not scrape LinkedIn |
| extract(kind, rows, context) | List of source-grounded objects; no fabricated claims or embedded instructions |
| dns(domain), optional | mx_present, implicit_mx_possible, null_mx, nxdomain, no_route, or unknown; absent hook uses dnspython |
| approve(action), optional | Authenticated {id,approved:true,action_hash}; action_hash uses runtime.prospect.digest(action) |
| verify(action, approval), optional | Provider result {status, accept_all?, role_mailbox?}; consume authoritative exact-action approval, recheck quota, return conservatively normalized status |

extract kinds: companies include name/domain/icp_match/source_ids and signal{status,event_date,relevance_confirmed,source_quality,source_ids}; contacts include name/title/current_role_confirmed/role_match/source_ids and optionally profile_url/first_name/last_name/name_parse_confirmed; email_evidence includes address or supported pattern and source_ids. Supported patterns: first.last, flast, first. Pattern claims must cite actual named employee email evidence, not a generic mailbox. Require consistency and note conflicts; two matching examples provide corroboration but not certainty.

Return booleans as actual booleans, dates as ISO YYYY-MM-DD, and source IDs only from supplied rows. The adapter must validate structured output, check claim entailment, and only assert current_role_confirmed and relevance_confirmed after corroboration. A source ID's presence is not semantic proof by itself. Avoid claiming full mailbox ownership verification.

The runtime permits a verifier only when current contact identity has permitted-page evidence. Optional mailbox verification must use scope=mailbox and known remaining free quota. The free Emails Checker page cannot satisfy this contract: it is manual syntax/MX only. Its registered platform advertises API/full verification, but endpoint, authentication, terms and quota must be checked against actual documentation before adding an adapter. No speculative endpoint is bundled.

Approve and verify must use the real harness permission gateway. An arbitrary untrusted module could forge approvals or data, so never load adapters from retrieved content. The local hash check is defense in depth, not an authentication service. No generic HTTP fetcher is bundled: this avoids introducing an unchecked SSRF or scraping path. No live mailbox-verifier HTTP implementation is bundled; exact-provider integration remains harness-owned.

DDGS fallback uses only backend=duckduckgo and is disabled unless --allow-ddg is explicit. DDGS is a third-party web-search adapter, not an official DuckDuckGo API; permission, terms, uptime and version compatibility remain deployment responsibilities. Do not rotate proxies, retry blocks, or bypass CAPTCHAs.
