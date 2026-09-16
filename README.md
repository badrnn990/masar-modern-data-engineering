# Masar Mini-Lakehouse — SDA-DSC-214

**Student:** Badr Al-Otaibi  
**GitHub:** `badrnn990`  
**Programme:** Modern Data Engineering for AI Systems  
**Institution:** SDAIA Academy  
**Dataset:** `MASAR_SMALL_V1` (synthetic training data only)

## Project idea

This repository implements the cumulative Masar Mini-Lakehouse project across Labs 01–08. The pipeline preserves raw arrivals in Bronze, creates typed and deduplicated Silver data, applies reliable Delta operations and quality controls, and publishes reconciled Gold outputs for BI reporting and point-in-time-safe AI features.

## Architecture

```text
Synthetic source feeds
        |
        v
   Bronze / Delta
        |
        v
 Silver / typed + conformed + deduplicated
        |
        +--------------------+
        |                    |
        v                    v
 Gold / BI             Gold / AI features
        ^                    ^
        |                    |
 Quality gate <---- Streaming / recovery
```

### Required controls

- Bronze is append-only and retains source/ingestion metadata.
- Silver normalizes timestamps and labels, validates driver relationships, and applies a documented business key and deterministic deduplication rule.
- Delta operations retain auditable transaction history and reject unsafe writes.
- Streaming uses Kafka/Structured Streaming with persistent checkpoints and restart evidence.
- Great Expectations is used as the promotion quality gate; invalid candidates are quarantined with reasons.
- Gold outputs have explicit grains and are reconciled for trip/fare totals and point-in-time feature safety.

## Repository evidence

- `day01/STUDENT.ipynb` through `day05/STUDENT.ipynb` — executed learner notebooks with retained outputs.
- `LAB01_NOTES.md` through `LAB08_NOTES.md` — lab-specific observations and evidence references.
- `BENCHMARKS.md` — measured Spark benchmark evidence.
- `DECISIONS.md` — architecture and reliability decisions.
- `GOVERNANCE.md` — ownership, access, lineage, retention and data classification.
- `reports/` — machine-produced native execution reports, including Bronze, benchmark, streaming, quality, recovery and serving evidence.
- `docs/VERIFICATION.md` and `docs/verification.json` — cumulative execution provenance.

## Environment

The supplied course route targets Python 3.11, Java 17, Spark 3.5.8, Delta 3.3.3, Kafka 4.0.2, Great Expectations 1.7.0 and dbt-spark 1.9.1. The repository contains the pinned course requirements and execution workflow.

## Execution order

1. Create/use the `develop` branch.
2. Install the course requirements from the repository.
3. Execute `day01/STUDENT.ipynb`.
4. Continue in order through `day05/STUDENT.ipynb`.
5. Retain notebook outputs and generated reports.
6. Run the repository checks with `python scripts/check_repository.py --release`.

The repository also contains a native GitHub Actions route under `.github/workflows/student-course.yml`. It is configured to execute the complete learner route on `develop` and publish generated notebook/evidence files back to that branch.

## Limitations

This is a synthetic training project, not a production-scale benchmark. Timing results are machine-dependent. Colab hosting and distributed production-scale workloads are not claimed unless separately evidenced in the repository.

## Programme credit

Developed as part of **Modern Data Engineering for AI Systems (SDA-DSC-214)** at **SDAIA Academy**.  
#SDAIAAcademy
