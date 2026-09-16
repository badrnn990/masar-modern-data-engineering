# Masar Mini-Lakehouse — Badr Al-Otaibi

**GitHub:** `badrnn990`  
**Programme:** Modern Data Engineering for AI Systems (SDA-DSC-214)  
**Institution:** SDAIA Academy  
**Dataset:** `MASAR_SMALL_V1` — synthetic training data only

## Project idea

This repository implements one cumulative Mini-Lakehouse across Labs 01–08. Raw synthetic feeds are preserved in Bronze, conformed into a typed and deduplicated Silver trip table, protected by Delta reliability and Great Expectations quality controls, and served as Gold outputs for BI reporting and point-in-time-safe AI features.

## Architecture

```text
Synthetic source feeds
        |
        v
 Bronze / append-only Delta
        |
        v
 Silver / typed + conformed + deduplicated
        |
        +-------------------------+
        |                         |
        v                         v
 Quality gate + quarantine   Streaming / recovery
        |                         |
        +------------+------------+
                     v
                 Gold layer
                  /      \
                 v        v
             BI outputs  AI features
```

### Layer guarantees

- **Bronze:** append-only source history with source and ingestion metadata.
- **Silver:** normalized timestamps and labels, validated driver relationships, documented business-key deduplication and deterministic precedence.
- **Reliability:** Delta transaction history, schema enforcement and negative-write evidence.
- **Streaming:** Kafka / Structured Streaming route with persistent query checkpoints and restart/replay evidence.
- **Quality:** Great Expectations promotion gate; invalid candidates are quarantined and unsafe promotion is blocked.
- **Gold:** explicit BI/AI grains with reconciliation and point-in-time feature checks.

## Verified results

The committed native reports contain the following observed results from the synthetic fixture:

| Evidence | Observed result |
|---|---:|
| Benchmark source population | 72 trips |
| Benchmark fare total | SAR 1,794.60 |
| Trusted quality population | 75 rows |
| Mixed quality candidate | 82 rows; GX failed as intended |
| BI fact grain | 75 trips |
| BI trip reconciliation | 75 = 75 |
| BI total fare | SAR 1,880.60 |
| Dammam | 25 trips / SAR 670.40 |
| Jeddah | 25 trips / SAR 625.20 |
| Riyadh | 25 trips / SAR 585.00 |
| AI feature rows | 3 |
| AI label rows | 3 |

The serving report records `gold_fact_totals_match=true`, `group_grains_reconcile=true`, valid foreign keys, aligned feature/label keys and a 75-row BI fact table. AI labels remain explicitly `UNOBSERVED_NOT_ZERO`; unavailable future outcomes are not fabricated.

## Failure and recovery evidence

The project records negative tests as evidence rather than only successful runs. The quality report shows the trusted 75-row candidate passed Great Expectations, the deliberately mixed 82-row candidate failed, and the failed candidate was not promoted. Quarantine was written as Delta and read back successfully.

Day 5 recovery evidence records `injected_failure_observed=true`, `previous_release_preserved=true`, and `content_equal=true` after rebuilding the same logical input. This demonstrates that a failed run does not replace the prior trusted release and that reconciliation is based on business content rather than volatile run identifiers.

## Benchmark evidence

The local Spark comparison used the same 72-row population and returned the same aggregate result for CSV and Delta. Four measured samples per variant were recorded after one warm-up. Median observed times were approximately **0.055 s for CSV** and **0.340 s for Delta** on this tiny local fixture. These measurements do **not** establish that CSV is generally faster or that Delta should provide a speed-up; startup, metadata, local storage and tiny-data effects dominate this exercise.

## Repository evidence

- `day01/STUDENT.ipynb` through `day05/STUDENT.ipynb` — executed notebooks with retained outputs.
- `LAB01_NOTES.md` through `LAB08_NOTES.md` — observations, decisions and evidence references.
- `BENCHMARKS.md` — cost assumptions and measured Spark evidence.
- `DECISIONS.md` — architecture, reliability, deduplication, quality and serving decisions.
- `GOVERNANCE.md` — lineage, ownership, intended access, retention and synthetic-data classification.
- `reports/` — machine-generated Bronze, benchmark, transaction, streaming, quality, recovery and serving evidence.
- `docs/VERIFICATION.md` and `docs/verification.json` — cumulative execution provenance.

## Environment

Verified course execution targets Python 3.11, Java 17, Spark 3.5.8, Delta 3.3.3, Kafka 4.0.2, Great Expectations 1.7.0 and dbt-spark 1.9.1. Pinned requirements and the execution workflow are committed in this repository.

## How to run

From a clean clone of this fork, switch to `develop`, install the pinned requirements, and execute the five learner notebooks in dependency order: `day01/STUDENT.ipynb` → `day02/STUDENT.ipynb` → `day03/STUDENT.ipynb` → `day04/STUDENT.ipynb` → `day05/STUDENT.ipynb`. Do not regenerate an unrelated dataset between days; each day consumes evidence from the previous day. Retain notebook outputs and generated reports.

Repository source/navigation checks can be run with:

```bash
python scripts/check_repository.py
python -m unittest discover -s tests -v
```

The native learner execution route is defined in `.github/workflows/student-course.yml` and the source checks in `.github/workflows/learner-checks.yml`.

## Key decisions

See [`DECISIONS.md`](DECISIONS.md). The most important choices are preserving Bronze history, deterministic Silver deduplication, separate persistent streaming checkpoints, blocking promotion on failed quality checks, and reconciling Gold by business content rather than execution timestamps.

## Limitations

This is a small synthetic training project, not a production deployment or production-scale benchmark. Local timing measurements cannot establish distributed performance or cloud cost. The Day 5 recovery test was performed within the recorded execution environment and is not evidence of an independent production disaster-recovery system. The project does not claim model training/accuracy, Power BI connector execution, public deployment, permissions enforcement or legal-compliance certification.

## Credits

This project was developed as part of **Modern Data Engineering for AI Systems (SDA-DSC-214)** at **SDAIA Academy** — [SDAIAAcademy](https://github.com/SDAIAAcademy).  
Course materials by **Meaad Al-Marri**; attribution for reused course material is preserved.

#SDAIAAcademy
