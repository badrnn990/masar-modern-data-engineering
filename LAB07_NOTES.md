# LAB07_NOTES — Integrate the Mini-Lakehouse

## What I did

I integrated the cumulative Bronze → Silver → Gold route in dependency order using the evidence produced by the earlier days rather than creating an unrelated replacement dataset. I also exercised the recovery path with a deliberate failure before a successful rebuild.

## What I observed

The Day 5 recovery report confirms all four required recovery properties:

- `injected_failure_observed=true` — the deliberate failure was actually reached.
- `previous_release_preserved=true` — the unsafe attempt did not replace the previous trusted release.
- `content_equal=true` — after recovery, the same logical input reconciled to the same business contents.
- `rebuild_has_new_identity=true` — execution identity changed while the business result remained stable.

The two recorded run IDs are different, which is expected. Correctness is therefore reconciled using deterministic business content, not volatile run IDs/timestamps.

## Decision

A downstream release must never be published merely because some upstream steps completed. Promotion occurs only after its dependencies and quality controls succeed. On failure, the prior trusted release remains the consumer-visible state.

## Recovery attempt

The recovery exercise intentionally injected a failure, observed it, verified preservation of the prior release, and reran the same logical input. The rebuilt release received a new execution identity but reconciled to equal business contents.

## Limitation

The recorded recovery test ran in the same Spark execution environment/session. It demonstrates the project's dependency and publication safety behaviour, but it is not evidence of an independent production disaster-recovery environment.

## Evidence

Primary evidence: `reports/recovery/day05_recovery.json`  
Related integration/serving evidence: `reports/serving/day05_serving_latest.json`  
Dataset: `MASAR_SMALL_V1` (synthetic)
