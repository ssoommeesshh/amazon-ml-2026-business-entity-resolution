"""Command-line entry point placeholder for the reproducible pipeline."""

import argparse
import json

from .profile import profile_directory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run business entity resolution.")
    parser.add_argument("--train-dir", required=True)
    parser.add_argument("--test-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument(
        "--mode",
        choices=["profile", "predict"],
        default="profile",
        help="Use profile while building the pipeline; predict will be implemented next.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.mode == "predict":
        raise NotImplementedError("Blocking and matching are the next implementation step.")
    reports = profile_directory(args.train_dir) + profile_directory(args.test_dir)
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
