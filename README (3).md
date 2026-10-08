# PAL Prospecting Agent — 0.2.0 draft

Classification: agent wrapper + reusable research skill + Python runtime + tool-adapter contracts. Scope: one bounded signal-to-business-email research job with scored local outputs. No outreach or CRM mutations.

## Run the synthetic demo
From this extracted package directory, run:

```sh
python -m runtime.prospect --project demo --brief "Find SaaS RevOps prospects" --out demo-output
python -m unittest discover -s tests -v
```

The demo needs no third-party packages or network, uses a fictional company/person and does not verify addresses. Its synthetic DNS status is not a real lookup. Do not interpret the demo output as live leads.

## Run with a real harness
1. Register agent.yaml and manifest-entry.yaml in the actual harness loader; no universal loader is assumed.
2. Create a trusted harness adapter using ADAPTER-CONTRACT.md. Bind PAL/extraction to the model and search/fetch to permitted real tools with schemas and timeouts. This adapter is required for live natural-language research.
3. If native DNS is unavailable, install requirements in an isolated environment. DDGS is optional, third-party, and only enabled after a permission review; it is not an official DuckDuckGo API. The declared dependency ranges require an integration test and lockfile before production deployment.
4. Set the adapter's module name with --adapter. Enable --allow-ddg only if approved. Runtime imports an installed trusted module; it does not install anything.
5. Provide current free verifier quota, actual provider/tool binding and exact-action approval callbacks. Never place secrets in files; use ENV:HUNTER_API_KEY or the harness secret store. Live provider integration is harness-owned, not a fabricated API client.
6. Run with --suppression pointing to a local JSON object with domains[] and emails[]. Missing suppression source is explicitly reported. Contact-level opt-outs require mapping to the approved email/domain suppression source before this runtime is used.
7. Inspect generated reports, scores, provenance and blockers. Local checker-candidates.txt and checker-handoff.json enable the user to submit to the CAPTCHA-protected free checker manually. Exporting does not authorize upload.
8. Complete live acceptance tests before approving deployment. Do not claim the unit suite validates real source permissions, API availability, account quota or authenticated gateway integration.

```sh
python -m runtime.prospect --adapter your_trusted_harness_adapter --project PROJECT_ID --brief "Your targeting brief" --suppression suppression.json --out lead-output
```

## Added provider
Emails Checker free bulk page: up to 5,000 addresses, no signup, CAPTCHA, syntax/MX only, XLSX output. It explicitly says these checks do not establish inbox existence. The registered platform advertises full checks, API access and 100 signup credits; those marketing claims were not independently tested. No automatic public-form submission or invented API exists here.

## Requirements discipline
Stated: add Emails Checker; Python execution; PAL; automated web search; structured scoring; protected prospecting workflow.
Inferred, reversible: local exports; business-email-only; free-only; bounded limits; trusted harness owns model and permission gateways.
Optional: approved DDGS fallback, actual mailbox-verifier integration, scheduled runs, CRM handoff. Scheduling and CRM writes are not implemented.
Open: actual harness binding, approved fallback rights, verifier account/API and quota, suppression source, retention, production lockfile. No external-action approval is requested or consumed during package generation.

## Evidence and distinctions
PAL sequence comes from pal-website-agent.soul.md, not the provisional Extract/Enhance/Execute mapping in the prior draft. This is a correction. The website skill provisions sites; this package researches prospects in an existing harness.

Reviewed 2026-10-07:
- https://emails-checker.net/bulk-email-checker — free-check scope, CAPTCHA, batch size and registered-platform distinction.
- https://github.com/deedy5/ddgs — third-party Python search adapter and duckduckgo backend.
- https://hunter.io/api-documentation — detailed verifier statuses; accept_all differs from valid; provider result is not consent.
- https://www.rfc-editor.org/rfc/rfc7505.html — null MX and implicit routing.
- https://www.linkedin.com/help/linkedin/answer/a1341387/prohibited-software-and-extensions?lang=en — prohibited automation boundary.

## Validation limits
The delivered runtime is complete for orchestration with trusted adapters and includes an offline runnable demo. It is not a fully configured standalone live agent, and no live leads, external uploads, API calls or DNS checks were executed while building this package. Semantic evidence checks, durable checkpoint/resume, broad international email syntax, contact-ID suppression and source-specific rights belong to additional deployment work; ambiguous names are not guessed.

## Change log
0.2.0: Added corrected PAL stages, protection protocol, Python runtime, weighted scoring, safe DDGS hook, exact-action verifier callbacks, manual Emails Checker handoff and tests.
