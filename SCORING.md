# Structured Lead Scoring

This is a designed review-priority rubric, not a statistically calibrated buying probability.

| Component | Points | Condition |
|---|---:|---|
| ICP fit | 25 | Confirmed match with sourced company evidence |
| Signal relevance | 20 | Observed event explicitly relevant to the offer |
| Freshness | 15 or 8 | 0–30 days: 15; older but inside configured window: 8; unknown, future, or stale: 0 |
| Contact role fit | 20 | Current employer/role and target-role relevance are evidenced |
| Source quality | 10 or 5 | Observed primary evidence: 10; observed secondary evidence: 5 |
| Email evidence | 10 or 4 | Exact verifier status valid: 10; published but not valid: 4; inferred only: 0 |

Total: 0–100. Tier A: 85–100; B: 70–84; C: below 70. Tiers rank review effort; they do not approve outreach.

Hard gates: confirmed domain, sourced ICP match, observed relevant signal, date inside window, confirmed current relevant contact, and no suppression match. Snippet-only company/role claims are downgraded before scoring. ready_for_review additionally requires score >=70 and exact-address valid verification. Unknown, catch-all, DNS-only, role mailbox, disposable, webmail, and unverified candidates remain needs_review regardless of score.

Example: ICP 25 + relevant signal 20 + fresh 15 + owner role 20 + primary evidence 10 + guessed email 0 = 90, Tier A, needs_review. A valid exact-address result adds 10 but ownership remains inferred if the address was guessed.
