# BENCHMARKS

Machine-produced Day 1 benchmark evidence; timing values are retained exactly as generated and are not general performance guarantees.

```json
{
  "cache_condition": "no explicit Spark cache; repeated local reads; OS/JVM/metadata caches not controlled",
  "checks": {
    "equal_source_populations": true,
    "positive_measured_samples": true,
    "query_plans_saved": true,
    "query_results_match_oracle": true
  },
  "dataset_manifest_sha256": "20a7e45bed2980b9394c10e8532da3b9f40f614366bb2df26a88610253e768e3",
  "engine_executed": true,
  "execution_order": [
    [
      "csv",
      "delta_v0"
    ],
    [
      "delta_v0",
      "csv"
    ],
    [
      "csv",
      "delta_v0"
    ],
    [
      "delta_v0",
      "csv"
    ]
  ],
  "expected_and_observed_aggregate": {
    "fare_total": "1794.60",
    "nonnull_fares": 72,
    "rows": 72
  },
  "limitations": [
    "Tiny synthetic fixture",
    "Local CPU and storage only",
    "No guaranteed ranking or speed-up",
    "Not cloud pricing or distributed scalability evidence"
  ],
  "measurements": {
    "csv": {
      "max_s": 0.05648625499999582,
      "median_s": 0.05477325900000096,
      "min_s": 0.04883856499999695,
      "samples_s": [
        0.05648625499999582,
        0.05333355800000561,
        0.04883856499999695,
        0.056212959999996315
      ]
    },
    "delta_v0": {
      "max_s": 0.4388751199999916,
      "median_s": 0.3395562095000031,
      "min_s": 0.31515601499999946,
      "samples_s": [
        0.35342432999999573,
        0.32568808900001045,
        0.31515601499999946,
        0.4388751199999916
      ]
    }
  },
  "payload_hashes": {
    "csv": "7257378390b1239dd31bb94fb9f8277f0bba15044b797f639cd31a094dd966ba",
    "delta_v0": "7257378390b1239dd31bb94fb9f8277f0bba15044b797f639cd31a094dd966ba"
  },
  "plans": {
    "csv": "reports/plans/csv.txt",
    "delta_v0": "reports/plans/delta_v0.txt"
  },
  "population_rows": 72,
  "repetitions_per_variant": 4,
  "scope": "DAY01_SPARK_LOCAL_BENCHMARK",
  "snapshot_version": 0,
  "spark_version": "3.5.8",
  "timing_scope": "query construction, planning, Spark action and collect; excludes session startup and ingestion",
  "warmups_per_variant": 1
}
```
