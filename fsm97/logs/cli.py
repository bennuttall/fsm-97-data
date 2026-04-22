import argparse
from pathlib import Path

from . import is_processed, process_log_file


def run(input_dir: Path, csv_dir: Path, pattern: str):
    gz_files = sorted(input_dir.rglob(pattern)) if input_dir.is_dir() else [input_dir]
    for f in gz_files:
        if not is_processed(f, csv_dir):
            print(f"Processing {f}")
            n = process_log_file(f, csv_dir)
            print(f"  {n:,} rows -> {csv_dir / (f.name + '.csv')}")


def main():
    parser = argparse.ArgumentParser(description="Process Apache log gz files into CSV")
    parser.add_argument("input", type=Path, help="Directory of .gz log files (or a single file)")
    parser.add_argument("--csv-dir", type=Path, default=Path("logs/csv"), help="Output CSV directory (default: logs/csv)")
    parser.add_argument("--pattern", default="*.gz", help="Glob pattern for log files (default: *.gz)")
    args = parser.parse_args()

    run(args.input, args.csv_dir, args.pattern)
