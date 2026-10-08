# Installation and integration

Classification: skill plus optional tool adapters. Scope: one bounded signal-to-business-email research run. An existing PAL agent invokes it; it is not a newly provisioned persistent agent.

1. Copy this directory into the harness's configured skills location. Register manifest-entry.yaml using the project's actual loader. No universal installer is assumed.
2. Bind the logical tools to real runtime tools and their schemas. Do not enable a named capability merely because it appears in SKILL.md. This package includes procedure and contracts, not live provider adapters.
3. Supply the approved PAL protocol. The supplied project excerpt supports brief parsing and reversible defaults, but does not define a complete canonical prospecting PAL protocol. The fallback mapping is explicitly provisional.
4. Bind search(query, limit) to results [{url,title,snippet,retrieved_at}]; fetch(url) to permitted text; dns(domain) to MX/A/AAAA results and DNS error codes; verify(email) to provider/raw_status/status/checked_at. Configure deadline, counters, throttling, bounded retries, and free-quota enforcement in the harness.
5. If desired, implement an approved full-search DuckDuckGo adapter. Do not use Instant Answer as a full search endpoint. No scraping adapter or installation is bundled.
6. Configure the verifier with a secret-store reference, e.g. ENV:HUNTER_API_KEY. Verify current quota and terms; do not put the key in files or logs. Bind VERIFY_DISCLOSURE to exact provider payload confirmation. If the harness mandates confirmation per external write, confirm each call; a general campaign approval is not a substitute.
7. Run the skill against a synthetic fixture first. Execute `python scripts/validate_output.py templates/leads.json` as a structural smoke test, then run every tests/cases.yaml scenario through the harness with mocked search/DNS/verifier tools. Verify deny paths produce zero external calls. The validator is a structural guard, not proof that sources, permissions, suppression, deadlines, or approvals are true; check those in runtime audit logs.
8. Export local JSON and CSV only. A separate outreach or CRM skill owns any subsequent externally approved action.

## CSV contract
One row per candidate: lead_id, company, domain, signal, signal_event_date, contact_name, title, profile_url, email, provenance, ownership, dns_status, verification_status, provider, checked_at, disposition, blockers, source_ids. Contacts without an email retain a row with blank email fields. Neutralize cells beginning with =, +, -, or @ when opening in spreadsheets.

## Intent discipline
- Stated: harness web search with DuckDuckGo backup; PAL intent extraction; signal creation/search; company/contact discovery including LinkedIn; published email pattern research then guesses; MX checks; free verification.
- Inferred and reversible: professional business contacts; bounded local artifacts; 10-company default; current role evidence; separate candidate and verifier states.
- Optional: authorized paid search providers, scheduling, enrichment, CRM synchronization, outreach. Not enabled.
- Open decisions: actual harness, approved PAL protocol, approved full-search backup, free verifier account/quota, source rights, suppression source, retention policy.
- Approval requests: none needed to install by copying locally yourself; adapter installation/deployment and any external verification submission require approval at execution. This package performs neither.

## Relationship to existing work
Distinct from pal-website-agent.SKILL.md: that skill builds a website and agent runtime. This skill operates inside an already configured runtime and returns prospect research. The archived one-must-act.skill was not readable as usable text in project exploration; no definitive duplication claim is made about it.

## Evidence notes
Sources reviewed 2026-10-07:
- DuckDuckGo Instant Answer documentation states it is not a full search results API: https://www.postman.com/api-evangelist/duckduckgo/documentation/i9r819s/duckduckgo-instant-answer-api
- Hunter offers a free verification/API path, but official pages show different allowance and credit models. Read account quota rather than hardcoding a count: https://hunter.io/email-verifier and https://hunter.io/api/email-verifier
- Hunter authentication and verification rate/credit guidance: https://help.hunter.io/en/articles/1970956-hunter-api
- DNS null MX and implicit A/AAAA fallback: https://www.rfc-editor.org/rfc/rfc7505.html
- LinkedIn prohibits unauthorized scraping and automated activity: https://www.linkedin.com/help/linkedin/answer/a1341387/prohibited-software-and-extensions?lang=en

No live prospecting, DNS checks, provider verification, installs, or external writes were executed during skill creation.

## Change log
0.1.0: Draft procedure, manifest, templates, structural validator, and scenario tests.
