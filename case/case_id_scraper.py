from urllib.parse import urlparse, parse_qs
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from library import generate_monthly_dates



monthly_dates = generate_monthly_dates(from_date="01/01/2015", to_date="01/12/2022")


def select_dropdown_option(driver, dropdown_id, child_id, option_index, wait_time=10):
    """
    Select an option from a custom dropdown by index.

    Args:
        driver: WebDriver instance
        dropdown_id (str): ID of the dropdown trigger element
        child_id (str): ID of the dropdown options container
        option_index (int): Index of the option to select (0-based)
        wait_time (int): Maximum wait time in seconds (default: 10)

    Returns:
        bool: True if selection was successful, False otherwise
    """
    try:
        wait = WebDriverWait(driver, wait_time)

        # Click to open dropdown
        dropdown = wait.until(ec.element_to_be_clickable((By.ID, dropdown_id)))
        dropdown.click()

        # Wait for options to be visible and select by index
        dropdown_options = wait.until(
            ec.visibility_of_all_elements_located((By.XPATH, f"//div[@id='{child_id}']//li"))
        )

        # Check if the index is valid
        if option_index >= len(dropdown_options):
            raise IndexError(f"Option index {option_index} is out of range. Available options: {len(dropdown_options)}")

        dropdown_options[option_index].click()
        return True

    except Exception as e:
        print(f"Error selecting dropdown option: {e}")
        return False


def set_date_field(driver, input_id, date_value, checkbox_id=None, check_checkbox=False, wait_time=10):
    """
    Set date in input field and optionally handle associated checkbox.

    Args:
        driver: WebDriver instance
        input_id (str): ID of the date input field
        date_value (str): Date value to enter (format: dd/mm/yyyy)
        checkbox_id (str, optional): ID of the checkbox to handle
        check_checkbox (bool): Whether to check (True) or uncheck (False) the checkbox
        wait_time (int): Maximum wait time in seconds (default: 10)

    Returns:
        bool: True if operation was successful, False otherwise
    """
    try:
        wait = WebDriverWait(driver, wait_time)

        # Wait for and clear the input field
        date_input = wait.until(ec.element_to_be_clickable((By.ID, input_id)))
        date_input.clear()

        # Enter the date value
        date_input.send_keys(date_value)

        # Handle checkbox if provided
        if checkbox_id:
            # Wait for checkbox to exist
            wait.until(ec.presence_of_element_located((By.ID, checkbox_id)))

            # Force check/uncheck with JS
            state_js = 'true' if check_checkbox else 'false'
            driver.execute_script(f'''
                var cb = document.getElementById("{checkbox_id}");
                if (cb) {{
                    cb.checked = {state_js};
                    cb.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            ''')

        return True

    except Exception as e:
        print(f"Error setting date field: {e}")
        return False


def extract_case_ids(driver: WebDriver, wait_time: int = 10) -> set[int]:
    """
    Waits for case result links to load and extracts unique CaseID values from <a> tags
    whose IDs start with 'cphMainContent_grdCaseResults_lnkViewCase_'.

    Each matching <a> tag contains a 'href' attribute with a 'CaseID' query parameter.
    This function parses the CaseID values and returns them as a set of integers.

    Args:
        driver (WebDriver): Selenium WebDriver instance.
        wait_time (int): Maximum time in seconds to wait for the elements to be present.

    Returns:
        set[int]: A set of unique CaseID integers.
    """
    case_ids = set()

    # Wait until at least one matching link is present in the DOM
    wait = WebDriverWait(driver, wait_time)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '[id^="cphMainContent_grdCaseResults_lnkViewCase_"]')))

    # Find all matching <a> elements
    links = driver.find_elements(By.CSS_SELECTOR, '[id^="cphMainContent_grdCaseResults_lnkViewCase_"]')

    for link in links:
        href = link.get_attribute("href")
        if href:
            parsed_url = urlparse(href)
            query_params = parse_qs(parsed_url.query)
            case_id_list = query_params.get("CaseID")
            if case_id_list and case_id_list[0].isdigit():
                case_ids.add(int(case_id_list[0]))

    return case_ids

def get_uk_gov_case_id(
        chromedriver: WebDriver,
        base_page_url: str = "https://acp.planninginspectorate.gov.uk/CaseSearch.aspx",
        start_date: str = "01/01/2015"
) -> set[int]:

    chromedriver.get(url=base_page_url)

    # Chromedriver wait for 10 seconds
    wait = WebDriverWait(chromedriver, 10)


    wait.until(ec.presence_of_element_located((By.ID, "cphMainContent_dSearchContent")))

    # Case Type
    select_dropdown_option(
        driver=chromedriver,
        dropdown_id="cphMainContent_cboAppealType_msdd",
        child_id="cphMainContent_cboAppealType_child",
        option_index=1
    )

    # Procedure Type
    select_dropdown_option(
        driver=chromedriver,
        dropdown_id="cphMainContent_cboProcedureType_msdd",
        child_id="cphMainContent_cboProcedureType_child",
        option_index=2
    )

    # Status
    select_dropdown_option(
        driver=chromedriver,
        dropdown_id="cphMainContent_cboStatus_msdd",
        child_id="cphMainContent_cboStatus_child",
        option_index=1
    )

    # Set Start date field
    set_date_field(
        driver=chromedriver,
        input_id="cphMainContent_pdsStart_txtDateSearch",
        date_value=start_date,
        checkbox_id="cphMainContent_pdsStart_chk30days",
        check_checkbox=True
    )

    search_btn = wait.until(ec.element_to_be_clickable((By.ID, "cphMainContent_cmdSearch")))
    search_btn.click()

    case_ids = extract_case_ids(driver=chromedriver)

    return case_ids
