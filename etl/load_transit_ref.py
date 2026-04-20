import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Load low-floor bus and subway elevator reference data.")
    parser.add_argument("--source", required=False, help="Optional source manifest path.")
    return parser.parse_args()


def main():
    parse_args()
    raise SystemExit("load_transit_ref.py is scaffolded in foundation setup only. Implement this in the transit-reference-data workstream.")


if __name__ == "__main__":
    sys.exit(main())
