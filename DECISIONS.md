# DECISIONS

- Preserve Bronze as append-only source history.
- Use deterministic business-key deduplication and precedence for late/replayed data.
- Require native stage evidence before downstream promotion.
- Keep streaming checkpoints persistent and separate by query.
- Quarantine failed quality candidates and block unsafe promotion.
- Reconcile Gold outputs by business content, not volatile timestamps.
- Use only synthetic `MASAR_SMALL_V1`.

Execution evidence: https://github.com/badrnn990/masar-modern-data-engineering/actions/runs/35097801713
