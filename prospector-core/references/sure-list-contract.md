# SURE list contract

## Statuses
| Status | Meaning |
|---|---|
| SURE | Domain has MX, and the address is either published next to the person's name on the company site, or verifier-`valid` with the person confirmed on a fetched page. |
| REVIEW | Not proven either way. `best_candidate_UNVERIFIED` + `candidate_basis` show the best lead. |
| REJECT | Proven unusable for a named-person list. |

## Proof types (SURE only)
| proof | ownership | Evidence stored |
|---|---|---|
| published_on_company_site | source_asserted | page URL, excerpt, retrieval time, page SHA-256 |
| published_on_third_party_page | source_asserted | same; only with `--evidence-policy any` |
| mailbox_verified | list_supplied or pattern_inferred | provider, raw status, check time, page that confirmed the person |

## Reason codes
| Code | Status | Meaning / next step |
|---|---|---|
| syntax_invalid | REJECT | Address is malformed. |
| webmail_domain / disposable_domain | REJECT | Personal or throwaway mailbox; not a business contact. |
| role_mailbox | REJECT | info@, sales@ … is not a person. |
| suppressed | REJECT | On the user's suppression list. |
| dns_null_mx / dns_nxdomain / dns_no_route | REJECT | Domain cannot receive mail or does not exist. |
| verifier_invalid | REJECT | Verifier says the supplied mailbox does not exist. |
| verifier_webmail / verifier_disposable | REJECT | Verifier classified the address as webmail or disposable. |
| duplicate_of_row_N | REJECT | Same address already on the SURE list. |
| no_company_domain | REVIEW | Add the company website. |
| no_email_and_name_unparsed / no_valid_guess_for_name | REVIEW | Need a first and last name to guess. |
| multiple_published_addresses | REVIEW | Site shows more than one address for this name. |
| supplied_email_differs_from_published | REVIEW | The site shows a different address (see best candidate). |
| email_domain_differs_from_company_domain | REVIEW | Possible subsidiary or a wrong email. |
| dns_unknown | REVIEW | DNS lookup failed or timed out; re-run. |
| no_mx_record_implicit_only | REVIEW | No MX; mail may route via an A record. |
| not_verified_no_verifier | REVIEW | Guess or supplied address; no verifier configured. |
| awaiting_verification_approval | REVIEW | Approve `verification_requests.txt` and re-run. |
| catch_all_domain | REVIEW | Domain accepts every address, so the mailbox cannot be proven. |
| all_guesses_invalid | REVIEW | Every guess was rejected by the verifier. |
| mailbox_valid_but_person_unconfirmed | REVIEW | Mailbox exists, but no fetched page shows this person. Add a source URL. |
| verifier_unknown / verifier_provider_error / verifier_quota_exhausted | REVIEW | Provider could not decide or is out of quota. |

## DNS states
mx_present · implicit_mx_possible · null_mx (`MX 0 .`, RFC 7505) · nxdomain · no_route · unknown.
