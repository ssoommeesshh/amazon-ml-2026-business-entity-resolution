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
