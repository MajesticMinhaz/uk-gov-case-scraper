from .session import db as db_instance
from .models import Case

def update_case_by_id(case_id: int, **kwargs) -> Case:
    """
    Update a case by ID with provided field values.

    Args:
        case_id (int): The ID of the case to update
        **kwargs: Field names and values to update (e.g., reference="REF123", status="Approved")

    Returns:
        Case: The updated case object

    Raises:
        ValueError: If case with given ID is not found
    """
    with db_instance.session_scope() as session:
        case = session.query(Case).filter(Case.id == case_id).first()

        if not case:
            raise ValueError(f"Case with ID {case_id} not found")

        # Update fields
        for field, value in kwargs.items():
            if hasattr(case, field):
                setattr(case, field, value)

        session.commit()
        return case
