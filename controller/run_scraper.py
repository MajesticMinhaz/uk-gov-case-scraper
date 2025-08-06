import random
import time
from pathlib import Path
from selenium_webdriver import get_selenium_chrome_driver
from .get_scrapers import get_scraper_function
from dbcore import get_config, create_case, get_cases_with_none_reference, update_case_by_id, get_cases_with_pdf_url
from library import generate_monthly_dates, download_pdf

env_config = get_config()


def run_scraper(category: str):
    """
    Run scraper based on category and target.

    Args:
        category (str): Scraper category ('case-id' or 'case-details')
    """

    if category == 'case-id':
        # Initialize Selenium Chrome driver once for all targets
        chromedriver = get_selenium_chrome_driver(
            headless=False,
            chromedriver_path=env_config.get("CHROMEDRIVER_PATH")
        )

        monthly_dates = generate_monthly_dates(from_date="01/01/2015", to_date="01/12/2022")

        print(f"Scraping: {category}")
        scraper_func = get_scraper_function(category)

        for monthly_date in monthly_dates:

            dataset = scraper_func(chromedriver=chromedriver, start_date=monthly_date)

            print(f"Checking > {monthly_date}")

            for data in dataset:
                create_case(_id=data)

    elif category == 'case-details':
        # Initialize Selenium Chrome driver once for all targets
        chromedriver = get_selenium_chrome_driver(
            headless=False,
            chromedriver_path=env_config.get("CHROMEDRIVER_PATH")
        )

        print(f"Scraping {category}")
        scraper_fuc = get_scraper_function(category)

        cases = get_cases_with_none_reference()

        for case in cases:
            dataset = scraper_fuc(
                webdriver_instance=chromedriver,
                case_id=case.id
            )

            # Wait for random second from 1 to 10
            time.sleep(random.randint(1, 10))

            update_case_by_id(
                case_id=case.id,
                reference=dataset.get("reference"),
                site_address=dataset.get("site_address"),
                type=dataset.get("type"),
                local_planning_authority=dataset.get("local_planning_authority"),
                officer=dataset.get("officer"),
                status=dataset.get("status"),
                decision_date=dataset.get("decision_date"),
                pdf_url=dataset.get("pdf_url"),
                pdf_name=dataset.get("pdf_name"),
            )

    elif category == 'download-pdf':

        print("Downloading PDF ...")

        cases = get_cases_with_pdf_url()

        for case in cases:

            # Split both pdf_url and pdf_name by "|" to handle multiple URLs and corresponding names
            pdf_urls = case.pdf_url.split("|") if case.pdf_url else []
            pdf_names = case.pdf_name.split("|") if case.pdf_name else []

            # Ensure we have the same number of URLs and names, or handle mismatches
            max_count = max(len(pdf_urls), len(pdf_names))

            for i in range(max_count):

                # Get URL and name, with fallback handling
                url = pdf_urls[i].strip() if i < len(pdf_urls) else None
                filename = pdf_names[i].strip() if i < len(pdf_names) else f"document_{i + 1}.pdf"

                if url:  # Only process non-empty URLs

                    print(f"Downloading PDF {i + 1}/{max_count} for case {case.id}: {filename}")

                    download_pdf(
                        url=url,
                        save_path=str(Path(env_config.get("CASE_PDF_PATH")) / str(case.id)),
                        filename=filename
                    )

            update_case_by_id(
                case_id=case.id,
                pdf_downloaded=True
            )
    else:
        # Category not recognized, no operation
        pass