import pandas as pd
from datetime import datetime
from typing import Optional
from dbcore import get_all_cases


def export_cases_to_excel(
        output_path: str = None,
        limit: Optional[int] = None
) -> str or None:
    """
    Export all cases from the database to an Excel file.

    Args:
        output_path (str): Path where the Excel file will be saved.
                          If None, generates filename with timestamp.
        limit (Optional[int]): Maximum number of records to export.
                              If None, exports all records.

    Returns:
        str: Path of the created Excel file
    """

    # Generate default filename if not provided
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"cases_export_{timestamp}.xlsx"

    # Get all cases using the dedicated function
    cases = get_all_cases(limit=limit)

    if not cases:
        print("No cases found to export.")
        return None

    # Convert to list of dictionaries
    cases_data = []
    for case in cases:
        case_dict = {
            'ID': case.id,
            'Reference': case.reference,
            'Site Address': case.site_address,
            'Case Type': case.type,
            'Local Planning Authority': case.local_planning_authority,
            'Case Officer': case.officer,
            'Status': case.status,
            'Decision Date': case.decision_date,
            'PDF URL': case.pdf_url,
            'PDF Name': case.pdf_name,
            'PDF Downloaded': 'Yes' if case.pdf_downloaded else 'No',
        }

        cases_data.append(case_dict)

    # Create DataFrame
    df = pd.DataFrame(cases_data)

    # Export to Excel with formatting
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Cases', index=False)

        # Get the workbook and worksheet for formatting
        workbook = writer.book
        worksheet = writer.sheets['Cases']

        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter

            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception as e:
                    print(e)

            # Set column width with some padding
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width

    print(f"Successfully exported {len(cases)} cases to: {output_path}")
    return output_path
