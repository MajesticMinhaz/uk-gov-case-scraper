from datetime import datetime


def generate_monthly_dates(from_date, to_date):
    """
    Generate a list of all months between two dates (inclusive).

    Args:
        from_date (str): Start date in "dd/mm/yyyy" format (e.g., "01/01/2015")
        to_date (str): End date in "dd/mm/yyyy" format (e.g., "01/12/2022")

    Returns:
        list: List of month dates in "dd/mm/yyyy" format
    """

    # Parse dates
    start = datetime.strptime(from_date, "%d/%m/%Y")
    end = datetime.strptime(to_date, "%d/%m/%Y")

    months = []
    current_year = start.year
    current_month = start.month

    while (current_year < end.year) or (current_year == end.year and current_month <= end.month):
        # Create date string for first day of current month
        date_str = f"01/{current_month:02d}/{current_year}"
        months.append(date_str)

        # Move to next month
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    return months
