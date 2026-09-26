"""Command-line entry point placeholder for the reproducible pipeline."""

import argparse
import json

from .duckdb_candidates import generate_exact_candidates
from .profile import profile_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run business entity resolution.")
    parser.add_argument("--train-dir", required=True)
    parser.add_argument("--test-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--mode",
        choices=["profile", "candidates", "predict"],
        default="profile",
        help="Profile data or generate baseline candidates; predict comes later.",
    )
    parser.add_argument("--source-set", choices=["train", "test"], default="test")
    parser.add_argument("--sample-rows", type=int, default=None)
    parser.add_argument("--max-candidates", type=int, default=500)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.mode == "predict":
        raise NotImplementedError("Blocking and matching are the next implementation step.")
    if args.mode == "candidates":
        source_dir = args.train_dir if args.source_set == "train" else args.test_dir
        count = generate_exact_candidates(
            source1_path=f"{source_dir}/{'train' if args.source_set == 'train' else 'test'}_source1.tsv",
            source2_path=f"{source_dir}/{'train' if args.source_set == 'train' else 'test'}_source2.tsv",
            source3_path=f"{source_dir}/{'train' if args.source_set == 'train' else 'test'}_source3.tsv",
            output_path=f"{args.output_dir}/candidate_pairs.tsv",
            max_candidates=args.max_candidates,
            sample_rows=args.sample_rows,
        )
        print(f"Wrote {count} candidate rows to {args.output_dir}/candidate_pairs.tsv")
        return
    reports = profile_directory(args.train_dir) + profile_directory(args.test_dir)
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
