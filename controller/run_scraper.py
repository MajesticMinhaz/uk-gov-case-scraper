import random
import time
from selenium_webdriver import get_selenium_chrome_driver
from .get_scrapers import get_scraper_function
from dbcore import get_config, create_case, get_cases_with_none_reference, update_case_by_id
from library import generate_monthly_dates

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

    else:
        # Category not recognized, no operation
        pass