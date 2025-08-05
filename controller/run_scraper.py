from selenium_webdriver import get_selenium_chrome_driver
from .get_scrapers import get_scraper_function
from dbcore import get_config, create_case
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

    else:
        # Category not recognized, no operation
        pass