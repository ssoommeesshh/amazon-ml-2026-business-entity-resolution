# Business Entity Resolution Pipeline

This folder contains the reproducible code required for the Amazon ML Challenge submission.

## Structure

```text
business_entity_resolution/
  src/business_entity_resolution/
    __init__.py
    io.py          # TSV readers and submission writers
    cli.py         # pipeline entry point
  requirements.txt
```

The source data is not copied into this folder and must remain outside Git. The pipeline accepts paths to the existing `dataset/train`, `dataset/test`, and `output` directories.

## Setup

From the repository root on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:PYTHONPATH = (Resolve-Path .\code\business_entity_resolution\src)
```

## Current smoke run

```powershell
python -m business_entity_resolution.cli `
  --train-dir dataset/train `
  --test-dir dataset/test `
  --output-dir output `
  --mode profile
```

The next implementation stages are profiling, normalization, blocking, pair scoring, threshold validation, and final output generation. The final command must create both `matching_results.tsv` and `candidate_pairs.tsv`.

## Candidate smoke test

Use the project virtual environment and a bounded sample before scanning the full files:

```powershell
$env:PYTHONPATH = (Resolve-Path .\code\business_entity_resolution\src)
.\.venv\Scripts\python.exe -m business_entity_resolution.cli `
  --train-dir dataset/train `
  --test-dir dataset/test `
  --output-dir output\sample_train `
  --mode candidates `
  --source-set train `
  --sample-rows 1000 `
  --max-candidates 50 `
  --max-token-frequency 500
```

This reads at most 1,000 rows from each of the three training files and writes a local candidate file. Sample output is ignored by Git. Exact blocking is intentionally conservative, so a low non-empty candidate count is expected at this stage.

For a recall smoke test against the full target files while keeping Source 1 small, use `--source1-sample-rows 1000` without `--target-sample-rows`. The `--max-token-frequency` option excludes overly common tokens from blocking.

## End-to-end smoke test

Generate candidates and baseline matches together:

```powershell
$env:PYTHONPATH = (Resolve-Path .\code\business_entity_resolution\src)
.\.venv\Scripts\python.exe -m business_entity_resolution.cli `
  --train-dir dataset/train `
  --test-dir dataset/test `
  --output-dir output\sample_match_train_100 `
  --mode match `
  --source-set train `
  --source1-sample-rows 100 `
  --max-candidates 500 `
  --max-token-frequency 500 `
  --threshold 0.80
```

This creates both `candidate_pairs.tsv` and `matching_results.tsv`. It is a development smoke test; threshold tuning and a memory-bounded full-test runner are still required before submission.
