from typing import Dict, Optional
from urllib.parse import urlencode
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class UKGovernmentCaseScraperError(Exception):
    """Custom exception for UK Government case scraping errors."""
    pass


def get_uk_gov_case_details_by_id(
        case_id: int,
        webdriver_instance: WebDriver,
        base_page_url: str = "https://acp.planninginspectorate.gov.uk/ViewCase.aspx",
        timeout: int = 10
) -> Dict[str, Optional[str]]:
    """
    Scrape case details from the UK Planning Inspectorate website.

    Args:
        case_id: The unique identifier for the planning case
        webdriver_instance: Selenium WebDriver instance (preferably Chrome)
        base_page_url: The base URL for the case viewing page
        timeout: Maximum time to wait for page elements (in seconds)

    Returns:
        Dictionary containing case details with the following keys:
        - ref: Case reference number
        - site_address: Site address for the planning application
        - case_type: Type of planning case
        - lpa_name: Local Planning Authority name
        - case_officer: Assigned case officer
        - status: Current case status
        - decision_date: Date of decision (if available)
        - pdf_url: URL to decision document PDF (if available)
        - pdf_name: Name of the decision document (if available)

    Raises:
        UKGovernmentCaseScraperError: If case details cannot be retrieved
        ValueError: If case_id is invalid
    """
    if not isinstance(case_id, int) or case_id <= 0:
        raise ValueError(f"case_id must be a positive integer, got: {case_id}")

    try:
        # Construct the full URL with case ID parameter
        full_url = f"{base_page_url}?{urlencode({'CaseID': case_id})}"
        print(f"Navigating to case details page for case ID: {case_id}")

        webdriver_instance.get(full_url)

        # Initialize explicit wait
        wait = WebDriverWait(webdriver_instance, timeout)

        # Wait for main content to load
        try:
            wait.until(ec.presence_of_element_located((By.ID, "divMainContent")))
        except TimeoutException:
            raise UKGovernmentCaseScraperError(
                f"Timeout waiting for page to load for case ID: {case_id}"
            )

        # Extract case details with error handling for each field
        case_details = dict()

        # Extract case reference
        case_details["reference"] = _safe_extract_text(
            webdriver_instance,
            "cphMainContent_LabelCaseReference",
            transform=lambda x: x.replace("Reference: ", "").strip()
        )

        # Extract site address from title attribute
        case_details["site_address"] = _safe_extract_attribute(
            webdriver_instance,
            "cphMainContent_labSiteAddress",
            "title"
        )

        # Extract other text fields
        case_details["type"] = _safe_extract_text(
            webdriver_instance, "cphMainContent_labCaseTypeName"
        )

        case_details["local_planning_authority"] = _safe_extract_text(
            webdriver_instance, "cphMainContent_labLPAName"
        )

        case_details["officer"] = _safe_extract_text(
            webdriver_instance, "cphMainContent_labCaseOfficer"
        )

        case_details["status"] = _safe_extract_text(
            webdriver_instance, "cphMainContent_labStatus"
        )

        case_details["decision_date"] = _safe_extract_text(
            webdriver_instance, "cphMainContent_labDecisionDate"
        )

        # Extract PDF link details
        pdf_url, pdf_name = _extract_pdf_details(webdriver_instance)
        case_details["pdf_url"] = pdf_url
        case_details["pdf_name"] = pdf_name

        print(f"Successfully extracted case details for ID: {case_id}")
        return case_details

    except WebDriverException as e:
        raise UKGovernmentCaseScraperError(
            f"WebDriver error while scraping case {case_id}: {str(e)}"
        ) from e
    except Exception as e:
        raise UKGovernmentCaseScraperError(
            f"Unexpected error while scraping case {case_id}: {str(e)}"
        ) from e


def _safe_extract_text(
        driver: WebDriver,
        element_id: str,
        transform: Optional[callable] = None
) -> Optional[str]:
    """
    Safely extract text from an element by ID.

    Args:
        driver: WebDriver instance
        element_id: ID of the element to extract text from
        transform: Optional function to transform the extracted text

    Returns:
        Extracted and optionally transformed text, or None if element not found
    """
    try:
        element = driver.find_element(By.ID, element_id)
        text = element.text.strip()

        if transform and callable(transform):
            text = transform(text)

        return text if text else None

    except NoSuchElementException:
        print(f"Warning: Element with ID '{element_id}' not found")
        return None


def _safe_extract_attribute(
        driver: WebDriver,
        element_id: str,
        attribute_name: str
) -> Optional[str]:
    """
    Safely extract an attribute value from an element by ID.

    Args:
        driver: WebDriver instance
        element_id: ID of the element
        attribute_name: Name of the attribute to extract

    Returns:
        Attribute value or None if element/attribute not found
    """
    try:
        element = driver.find_element(By.ID, element_id)
        attribute_value = element.get_attribute(attribute_name)
        return attribute_value.strip() if attribute_value else None

    except NoSuchElementException:
        print(f"Warning: Element with ID '{element_id}' not found")
        return None


def _extract_pdf_details(driver: WebDriver) -> tuple[Optional[str], Optional[str]]:
    """
    Extract PDF URL and name from the decision link element.

    Args:
        driver: WebDriver instance

    Returns:
        Tuple of (pdf_url, pdf_name) or (None, None) if not found
    """
    try:
        pdf_container = driver.find_element(By.ID, "cphMainContent_labDecisionLink")
        links = pdf_container.find_elements(By.TAG_NAME, "a")

        if links:
            first_link = links[0]
            pdf_url = first_link.get_attribute("href")
            pdf_name = first_link.text.strip()

            return (
                pdf_url.strip() if pdf_url else None,
                pdf_name if pdf_name else None
            )

    except NoSuchElementException:
        print("Warning: PDF decision link element not found")

    return None, None
