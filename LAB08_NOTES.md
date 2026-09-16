# LAB08_NOTES — Serve AI and BI

## What I did

I served BI and AI outputs from the same trusted Day 5 lineage. The BI path publishes trip facts/dimensions and Gold aggregates. The AI path publishes point-in-time-aware zone/hour features and keeps unavailable future labels explicitly unobserved.

## Output grains

- `bi.fact_trips`: one row per trusted trip; observed 75 rows.
- `gold.driver_daily`: driver/day aggregate; observed 18 rows.
- `gold.zone_hourly_demand`: zone/hour demand output; observed 75 rows.
- `ai.zone_hourly_features`: feature rows at the documented zone/hour serving grain; observed 3 rows in the release export.
- `ai.zone_hourly_labels`: aligned label keys; observed 3 rows, with unavailable outcomes represented as `UNOBSERVED_NOT_ZERO` rather than fabricated zeros.

## BI reconciliation

| Zone | Trip count | Fare total (SAR) |
|---|---:|---:|
| Dammam | 25 | 670.40 |
| Jeddah | 25 | 625.20 |
| Riyadh | 25 | 585.00 |
| **Total** | **75** | **1,880.60** |

The serving report records `gold_fact_totals_match=true`, `group_grains_reconcile=true`, `fact_grain_75=true`, and `foreign_keys_valid=true`. Therefore the trusted trip population and BI outputs reconcile on both business grain and totals.

## Point-in-time correctness

The feature inputs recorded by the native report are `zone_key`, `completed_trips_24h`, `avg_duration_seconds_24h`, and `history_available`. The release records `feature_availability_checked=true` and `feature_label_keys_aligned=true`. Information that is not available at the prediction time is not fabricated into the feature set or labels.

## What I observed

All serving schema/key checks in the native report passed, including BI dimensions/fact, Gold aggregates and AI feature/label outputs. Events are aggregated before the serving join, avoiding multiplication of trip facts by raw event rows.

## Limitations

This evidence demonstrates generated serving outputs and reconciliation. It does not claim model training/accuracy, Power BI connector execution, public deployment, or full course approval.

## Evidence

Primary evidence: `reports/serving/day05_serving_latest.json`  
Dataset: `MASAR_SMALL_V1` (synthetic)
