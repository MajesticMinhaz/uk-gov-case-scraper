from .session import db as db_instance
from .models import Case


def get_cases_with_none_reference(limit: int = 1000, offset: int = None) -> list[Case]:
    """
    Retrieve cases that:
    - have reference field as None
    - ordered by ID ascending

    Args:
        limit (int): Maximum number of records to retrieve (default: 1000)
        offset (int, optional): Number of records to skip from the beginning.
                               If None, no records are skipped.

    Returns:
        list[Case]: Cases with None reference, ordered by ID
    """
    with db_instance.session_scope() as session:
        query = (
            session.query(Case)
            .filter(Case.reference.is_(None))
            .order_by(Case.id)
        )

        # Apply offset if provided
        if offset is not None:
            query = query.offset(offset)

        return query.limit(limit).all()


def get_cases_with_pdf_url(limit: int = 100) -> list[Case]:
    """
    Retrieve cases that:
    - have pdf_url field as not null
    - have pdf_downloaded field as False
    - ordered by ID ascending

    Args:
        limit (int): Maximum number of records to retrieve (default: 100)

    Returns:
        list[Case]: Cases with non-null pdf_url and pdf_downloaded=False, ordered by ID
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Case)
            .filter(Case.pdf_url.isnot(None))
            .filter(Case.pdf_downloaded == False)
            .order_by(Case.id)
            .limit(limit)
            .all()
        )


def get_all_cases(limit: int = None) -> list[Case]:
    """
    Retrieve all cases from the table ordered by ID ascending.

    Args:
        limit (int, optional): Maximum number of records to retrieve.
                              If None, retrieves all records.

    Returns:
        list[Case]: All cases ordered by ID ascending
    """
    with db_instance.session_scope() as session:
        query = session.query(Case).order_by(Case.id)

        if limit is not None:
            query = query.limit(limit)

        return query.all()
