# Team Workflow

## Source of truth

- `dataset/` is input data and is not modified.
- `code/business_entity_resolution/src/` is the only production pipeline.
- `experiments/` contains temporary notebooks, profiling output, and validation results.
- `output/` contains the latest generated submission files.
- `Documentation_template.md` is updated after the final experiment.

## Required pipeline stages

1. Profile data without hard-coding countries.
2. Normalize names and addresses.
3. Generate candidates with blocking.
4. Create labeled training pairs from `train_ground_truth.tsv`.
5. Train or calibrate a pair matcher.
6. Tune thresholds using macro F0.5 on a held-out Source-1 validation split.
7. Generate test candidates and predictions.
8. Run `utils/validate_submission.py`.
9. Record the experiment configuration and score.

## Team rules

- Never overwrite another person's experiment output.
- Use Git branches or clearly named commits for changes.
- Do not use external business databases, APIs, geocoding, or web lookup.
- Keep the final command reproducible on CPU.
- Every test Source-1 record must receive one output row.
