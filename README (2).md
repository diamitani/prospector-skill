# Prospector Skill 0.3.0

This is a specification and integration-contract update, not a replacement Python runtime. No new Maps/Places adapter or CRM connector code is claimed as implemented. The previous Python runtime requires modifications before it can execute the new local-business route, ICP-only scoring, and CRM write flow.

## Install and integrate
1. Replace the previous skill instructions with SKILL.md and update the manifest. Keep the stable skill ID to avoid duplicate routing.
2. Bind actual Places/web search and CRM tools after discovering schemas and source permissions. Use the current Places API, not invented endpoints. Default spend is zero; approved paid calls require a cost decision and a guarded adapter.
3. Update the Python orchestration to branch on discovery_route and targeting_mode. Apply scoring.yaml; this differs from the previous signal-only scoring function.
4. Add named-person/general-inbox/business-phone distinctions and Places IDs to the lead schema.
5. Add resolved CRM read/dedup/preview/exact-approval/write/receipt handling at the harness gateway. crm-preview.template.json is conceptual; actual arguments must match the discovered connector schema.
6. Run tests.md in a synthetic harness. Perform separate live acceptance tests for source permissions, quota and authoritative approvals before marking approved.

## Intent discipline
Stated: subscription-free contact research, signal-or-ICP input, PAL, web company discovery, title-based LinkedIn search, local-business Maps/Places discovery, email-pattern guesses, domain checks, verifier, spreadsheet or CRM.
Inferred and reversible: business contacts only, spreadsheet default, zero budget, bounded runs, source evidence, independent identity verification.
Optional: authorized Places API and CRM integration; no runtime implementation is included in this update.
Open: actual CRM/account/object schema, approved Places access/budget, free verifier account, suppression source and artifact retention.
Approval requests: none consumed while generating this package. Each external verifier disclosure, cost-incurring Places action and CRM mutation remains separately gated at execution.

## Evidence notes
Google Places documentation lists establishment details including website and phone, not guaranteed owner email discovery. Website/phone fields can affect pricing. Sources reviewed 2026-10-07:
- https://developers.google.com/maps/documentation/places/web-service/place-details
- https://developers.google.com/maps/documentation/places/web-service/data-fields

PAL sequence and existing verifier distinction carry forward from version 0.2.0. This update corrects the requested wording 'MX to see if working inbox': MX checks routing, while specific mailbox validity remains a separate verifier result. No live prospecting or CRM mutations were performed.
