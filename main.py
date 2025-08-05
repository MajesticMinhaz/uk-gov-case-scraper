import argparse
from controller import run_scraper


def main():
    parser = argparse.ArgumentParser(description="Case Scraper Tool")

    parser.add_argument(
        "category",
        choices=["case-id", "case-details"],
        help="Category to perform"
    )

    # Parse full args
    args = parser.parse_args()

    # Run scraper with parsed arguments
    run_scraper(args.category)


if __name__ == "__main__":
    main()