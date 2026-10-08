# Prospector Core: breakdown (One Must Act + POP, condensed)

**100 (goal):** A user uploads a prospect list, or gives a signal/ICP brief, and in one run gets a SURE list in
which every row is backed by proof the system checked itself. Zero fabricated people, companies or emails on it,
measured by the eval suite (precision 15/15 attack cases, 0 invariant violations) rather than by the model's say-so.
**Threshold T:** 0 false SURE rows. Recall may be low on sites that publish nothing; those rows land in REVIEW with a reason.

**1 (what must be whole first):** `scripts/verify_list.py`, a deterministic judge. Claude discovers, the script decides.
W = 1: recall 9/9, precision 15/15, gates 17/17, mutation 6/6, live DNS/fetch guards pass.

**2–99 (multipliers, added only now that the 1 is whole):**
| Multiplier | Adds | Status |
|---|---|---|
| Harness web search / DuckDuckGo (`web_search.py`) | company + people discovery | Built (discovery only, re-checked by the judge) |
| Mailbox verifier (Hunter) | turns guesses into SURE | Built, approval-gated; **not live-tested** |
| Google Maps/Places | local-business owners | Deferred: needs an actual tool and cost approval |
| CRM write (HubSpot etc.) | delivery | Deferred: separate approved step; CSV/XLSX today |

**0 (where we started):** v0.1–v0.3 specs + an orphan `prospect.py` whose `runtime.*` modules were missing, so nothing ran end to end.

**NPAO order:** N: judge + evals (done) → A: live 1-address Hunter test (next) → P: first real list run →
O: Places + CRM adapters.

**First action today:** upload `prospector-core.zip`, then run it on a 10–20 row real list.
