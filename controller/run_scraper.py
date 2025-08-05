from selenium_webdriver import get_selenium_chrome_driver
from .get_scrapers import get_scraper_function
from dbcore import get_config
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

        monthly_dates = generate_monthly_dates(from_date="01/01/2015", to_date="01/02/2015")

        print(f"Scraping: {category}")
        scraper_func = get_scraper_function(category)

        for monthly_date in monthly_dates:

            data = scraper_func(chromedriver=chromedriver, start_date=monthly_date)
            print(data)
            #
            # # Create events in DB from scraped data
            # for event in data.get("events", []):
            #     if event.get("url") in existing_urls:
            #         print(f"✅ Skipping existing event: {event.get('url')}")
            #         continue
            #
            #     _event = create_event(
            #         event_url=event.get("url"),
            #         website_name=data.get("website_name"),
            #         image_url=event.get("image_url")
            #     )
            #     if _event:
            #         print(f"Event Created, Event ID: {_event.id}")

    else:
        # Category not recognized, no operation
        pass