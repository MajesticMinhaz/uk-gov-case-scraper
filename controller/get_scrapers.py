from case import get_uk_gov_case_id

def get_scraper_function(category: str):
    mapping = {
        ("case-id",): get_uk_gov_case_id,
    }
    return mapping[(category,)]