from case import get_uk_gov_case_id, get_uk_gov_case_details_by_id

def get_scraper_function(category: str):
    mapping = {
        ("case-id",): get_uk_gov_case_id,
        ("case-details",): get_uk_gov_case_details_by_id
    }
    return mapping[(category,)]