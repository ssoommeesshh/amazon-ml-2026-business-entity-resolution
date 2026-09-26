"""Command-line entry point placeholder for the reproducible pipeline."""

import argparse
import json

from .duckdb_candidates import generate_exact_candidates
from .pipeline import score_candidate_file
from .profile import profile_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run business entity resolution.")
    parser.add_argument("--train-dir", required=True)
    parser.add_argument("--test-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--mode",
        choices=["profile", "candidates", "match", "predict"],
        default="profile",
        help="Profile data or generate baseline candidates; predict comes later.",
    )
    parser.add_argument("--source-set", choices=["train", "test"], default="test")
    parser.add_argument("--sample-rows", type=int, default=None)
    parser.add_argument("--source1-sample-rows", type=int, default=None)
    parser.add_argument("--target-sample-rows", type=int, default=None)
    parser.add_argument("--max-candidates", type=int, default=500)
    parser.add_argument("--max-token-frequency", type=int, default=5000)
    parser.add_argument("--threshold", type=float, default=0.80)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.mode == "predict":
        raise NotImplementedError("Blocking and matching are the next implementation step.")
    if args.mode in {"candidates", "match"}:
        source_dir = args.train_dir if args.source_set == "train" else args.test_dir
        prefix = "train" if args.source_set == "train" else "test"
        candidate_path = f"{args.output_dir}/candidate_pairs.tsv"
        count = generate_exact_candidates(
            source1_path=f"{source_dir}/{prefix}_source1.tsv",
            source2_path=f"{source_dir}/{prefix}_source2.tsv",
            source3_path=f"{source_dir}/{prefix}_source3.tsv",
            output_path=candidate_path,
            max_candidates=args.max_candidates,
            sample_rows=args.sample_rows,
            source1_sample_rows=args.source1_sample_rows,
            target_sample_rows=args.target_sample_rows,
            max_token_frequency=args.max_token_frequency,
        )
        print(f"Wrote {count} candidate rows to {candidate_path}")
        if args.mode == "match":
            matching_path = f"{args.output_dir}/matching_results.tsv"
            score_candidate_file(
                f"{source_dir}/{prefix}_source1.tsv",
                f"{source_dir}/{prefix}_source2.tsv",
                f"{source_dir}/{prefix}_source3.tsv",
                candidate_path,
                matching_path,
                threshold=args.threshold,
            )
            print(f"Wrote matching results to {matching_path}")
        return
    reports = profile_directory(args.train_dir) + profile_directory(args.test_dir)
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
