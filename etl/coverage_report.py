import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Report ETL coverage for road_segments attributes.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    return parser.parse_args()


def main():
    parse_args()
    raise SystemExit("coverage_report.py is scaffolded in foundation setup only. Implement this in the accessibility-etl workstream.")


if __name__ == "__main__":
    sys.exit(main())
