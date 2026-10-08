# QA Report: prospector-core v0.4.0 (2026-10-07)

**Verdict: PASS.** Official `jev-qa` CLI run (from `~/jev-backend-qa-main`): 0 candidate findings, exit PASS.
Reports: `qa/jev-qa-report/` (md + html + json).

What that PASS covers: `bin/backend_checks.py` ran its 10 checks over the full tree and found nothing. Only the
**secret scan** really applies to this Python skill; the other 9 checks target JS/Supabase/Stripe code
(routes, RLS, webhooks) and had nothing to inspect. Jev was **not called**, because with 0 findings there is
nothing to adjudicate (no `AI_GATEWAY_API_KEY` is set either). The defects D1–D7 below were found by the
domain eval suite, not the scanner. All were fixed and re-verified by a clean re-run (re-verify the fix,
not the claim). Their severities and p(risk) values are my calibrated estimates using the skill's
thresholds, not Jev scores.

## Scope
- Build: `prospector-core/` (SKILL.md, scripts/verify_list.py, scripts/web_search.py, references/, evals/)
- QA type: pre-launch, full tree
- Question under test: **can anything fabricated reach the SURE list, and do real, proven rows reach it?**

## What was verified
| Area | Method | Result |
|---|---|---|
| Recall: proven rows reach SURE | 9 ground-truth cases (team page, mailto, obfuscated, accented name, "Last, First", supplied+published, corroborated pattern + verifier, flast pattern ranking, supplied + news page) | 9/9 |
| Precision: hallucinations blocked | 15 attack cases (fabricated person, fabricated company, wrong supplied email, someone else's address, same-first-name neighbour, lookalike domain, address without name, role inbox, third-party page, prompt injection, LinkedIn-only person, MX-only guess, catch-all, name only in local part, verifier "valid" for a fake person) | 15/15 |
| Gates | 17 cases (approval list, quota cap, stop at first valid, invalid, provider error, null MX, implicit MX, DNS unknown, webmail, suppression, duplicates, multiple addresses, no domain, single-token name, syntax, signal check, supplied role inbox) | 17/17 |
| Invariants on every case | INV-1 SURE email literally on its evidence page or approved+valid · INV-2 MX present · INV-3 verifier never called for unapproved addresses · INV-4 non-SURE rows never carry `email` · INV-5 verified rows have a fetched person page | 0 violations |
| Eval strength | Mutation test: 6 deliberate breakages of the judge | 6/6 caught |
| Live smoke | Real DNS (gmail.com MX, example.com null MX, nonexistent nxdomain); fetch guards (LinkedIn, 127.0.0.1, 169.254.169.254 metadata, file://); real public page fetch | pass |
| CSV safety | Formula-leading cells neutralised | pass |
| Secrets | Scan for hardcoded keys/tokens | none; verifier key read from `HUNTER_API_KEY` env only |

## Defects found and fixed (builder fix → QA re-run)
| # | Defect | Severity (0–10) | p(risk) | Class | Status |
|---|---|---|---|---|---|
| D1 | **False SURE:** an address was attributed to the wrong person when a neighbour shared the first name (`alex@` → Alex Rivera instead of Alex Smith) | 9 | 0.85 | BLOCK | Fixed: full-name sequence required, rival-name ambiguity guard. H6 passes. |
| D2 | Non-SURE rows kept a value in `email` in all_results.json (could be read downstream as verified) | 6 | 0.60 | WARN | Fixed: only SURE rows carry `email`. INV-4 clean. |
| D3 | Crawler stopped when the homepage failed, so team/about pages were never read (silent recall loss) | 6 | 0.70 | WARN | Fixed. Recall went from 1/9 to 9/9. |
| D4 | Crawler discarded every sub-page (marked "seen" before its own duplicate check) | 6 | 0.90 | WARN | Fixed; verified live on python.org. |
| D5 | robots.txt redirect treated as "disallow", so whole sites (e.g. python.org) were skipped | 5 | 0.80 | WARN | Fixed; live check passes. |
| D6 | Blocked fetches labelled `robots_disallow` instead of `blocked_host` / `non_public_address` (outcome safe, label wrong) | 2 | 0.30 | minor | Fixed. |
| D7 | Eval gap: allowing role mailboxes went undetected | 4 | 0.50 | WARN (eval) | Added G17; mutant now caught. |

## Not verified (still the user's move)
- **Hunter verifier against the real API:** the adapter follows Hunter's documented endpoint, but no key was used and no live call was made. Do a 1-address live test with your key before relying on it.
- **Real-world recall rate.** The fixtures prove the logic. How many SURE rows you get on real lists depends on how many companies publish emails or how much verifier quota you approve. Expect most guess-only rows to land in REVIEW until the verifier is approved.
- **Claude.ai sandbox networking.** The script needs outbound DNS/HTTPS. If code execution has no network egress, the report shows a DNS blocker and returns zero SURE rows (by design).
- Known limits: two different people with the same full name at one company cannot be told apart. Hyphenated or compound surnames are matched conservatively, so expect more REVIEW and no false SURE.

## Re-run
```bash
python3 evals/run_evals.py --live
```
