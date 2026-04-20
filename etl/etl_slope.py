import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Populate avg_slope_percent from DEM data.")
    parser.add_argument("--dem", required=False, help="Path to the DEM GeoTIFF.")
    return parser.parse_args()


def main():
    parse_args()
    raise SystemExit("etl_slope.py is scaffolded in foundation setup only. Implement this in the accessibility-etl workstream.")


if __name__ == "__main__":
    sys.exit(main())
