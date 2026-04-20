import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Populate accessibility attributes from public datasets.")
    parser.add_argument("--config", required=False, help="Optional ETL config path.")
    return parser.parse_args()


def main():
    parse_args()
    raise SystemExit("etl_accessibility.py is scaffolded in foundation setup only. Implement this in the accessibility-etl workstream.")


if __name__ == "__main__":
    sys.exit(main())
