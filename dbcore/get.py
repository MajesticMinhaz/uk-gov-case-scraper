from .session import db as db_instance
from .models import Case


def get_cases_with_none_reference(limit: int = 1000) -> list[Case]:
    """
    Retrieve cases that:
    - have reference field as None
    - ordered by ID ascending

    Args:
        limit (int): Maximum number of records to retrieve (default: 100)

    Returns:
        list[Case]: Cases with None reference, ordered by ID
    """
    with db_instance.session_scope() as session:
        return (
            session.query(Case)
            .filter(Case.reference.is_(None))
            .order_by(Case.id)
            .limit(limit)
            .all()
        )
