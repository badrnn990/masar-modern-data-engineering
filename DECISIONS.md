# DECISIONS

This record explains the choices made in the cumulative Masar Mini-Lakehouse and the evidence used to verify them.

## 1. Preserve Bronze as append-only history

**Choice:** Keep raw arrivals and replayed deliveries in Bronze instead of overwriting prior data.  
**Why:** Bronze is the auditable archive from which later layers can be rebuilt. Source and ingestion metadata distinguish deliveries from business records.  
**Rejected:** Replacing Bronze with the latest clean snapshot, because that would hide replay history and break the cumulative project chain.

## 2. Deterministic Silver deduplication

**Choice:** Conform types, timestamps and labels first, validate driver relationships, then deduplicate using the documented business key and deterministic precedence.  
**Why:** Replays and late deliveries must produce one stable trusted business representation. A rerun of the same logical input must not create extra business trips.  
**Rejected:** `dropDuplicates` without a stated key/precedence because its surviving record would not express a reproducible business rule.

## 3. Delta safety before convenience

**Choice:** Use real Delta transaction history and schema enforcement and retain negative-write evidence. Corrections are applied idempotently and logical contents are compared after repeated application.  
**Why:** A trusted table must reject incompatible writes and preserve auditable versions.  
**Rejected:** Silently coercing or dropping invalid records at the trusted-table write boundary.

## 4. Persistent checkpoint per streaming query

**Choice:** Each Structured Streaming query has its own persistent checkpoint.  
**Why:** Query progress is state belonging to that query. Separate checkpoints make stop/restart and replay behaviour auditable and avoid state collisions.  
**Rejected:** Sharing or deleting checkpoints merely to make a replay appear clean.

## 5. Quality gate blocks promotion

**Choice:** Run Great Expectations at the promotion boundary. Invalid candidate records are quarantined with reasons and a failed candidate is not promoted.  
**Evidence:** The trusted candidate contains 75 rows and passes GX. The deliberately mixed candidate contains 82 rows and fails GX; `failed_candidate_not_promoted=true`, while quarantine Delta readback succeeds.  
**Why:** Bad data should fail visibly and remain diagnosable rather than silently entering a trusted output.  
**Rejected:** Logging quality errors while continuing publication.

## 6. Fixed scenario time for freshness observations

**Choice:** Evaluate scenario freshness against the supplied fixed scenario time rather than wall-clock execution time.  
**Evidence:** The quality report records delivery age 240 s against a 300 s limit and source-event age 33,540 s against a 43,200 s limit; both pass.  
**Why:** The synthetic scenario must remain reproducible whenever the project is rerun.

## 7. Failure must preserve the previous release

**Choice:** Downstream publication is blocked when an injected failure occurs, leaving the previous trusted release intact. Recovery is rerun from the same logical inputs.  
**Evidence:** Day 5 records `injected_failure_observed=true`, `previous_release_preserved=true`, `content_equal=true`, and a new run identity after recovery.  
**Why:** Reliability means a failed attempt cannot replace trusted data.

## 8. Reconcile business content, not volatile metadata

**Choice:** Compare row/business totals and deterministic content rather than run IDs or ingestion timestamps.  
**Why:** A correct rerun may have a different execution identity while representing exactly the same business state.

## 9. Explicit BI and AI grains

**Choice:** Serve both consumers from the same trusted lineage. BI uses a 75-row trip fact plus dimensions and grouped Gold outputs. AI features are produced at the documented zone/hour grain with availability checks.  
**Evidence:** The serving report records 75 BI fact rows, valid foreign keys, `gold_fact_totals_match=true`, `group_grains_reconcile=true`, three AI feature rows and three label rows.

## 10. Point-in-time safety over fabricated labels

**Choice:** Only information available at the feature cut-off is used for AI features. Unobserved future labels remain explicitly `UNOBSERVED_NOT_ZERO`.  
**Why:** Treating an unavailable future outcome as zero would introduce false information and invalidate the feature/label semantics.  
**Rejected:** Filling unobserved labels with zero for convenience.

## 11. Honest benchmark interpretation

**Choice:** Report measured local timings without claiming a general speed advantage.  
**Evidence:** For the same 72-row population and SAR 1,794.60 aggregate, observed median times were about 0.055 s for CSV and 0.340 s for Delta.  
**Why:** This tiny synthetic local workload is useful for demonstrating equal-result scans and query plans, not for production performance conclusions.

## 12. Synthetic data and bounded claims

Only `MASAR_SMALL_V1` synthetic training data is used. The repository does not claim production-scale performance, model accuracy, Power BI connector execution, public deployment, permissions enforcement or legal-compliance certification unless separately evidenced.

## Evidence index

- `reports/bronze.json`
- `reports/benchmark.json`
- `reports/day03_transactions.json`
- `reports/streaming/day04_stream_latest.json`
- `reports/quality/day04_quality_latest.json`
- `reports/recovery/day05_recovery.json`
- `reports/serving/day05_serving_latest.json`
- `docs/VERIFICATION.md`
