from .session import db, Database
from .models import Case
from sqlalchemy.exc import IntegrityError

def create_case(_id: int, **kwargs) -> Case | None:
    """
    Create and commit a new Case with manually assigned primary key,
    using the session_scope context manager.

    Returns None if the _id already exists or on integrity errors.
    """
    try:
        with db.session_scope() as session:
            existing = session.query(Case).filter_by(id=_id).first()
            if existing:
                print(f"Case with id={_id} already exists.")
                return None

            case = Case(id=_id, **kwargs)
            session.add(case)
            session.flush()  # push to DB but not commit yet
            return case
    except IntegrityError as e:
        print(f"IntegrityError when creating case with id={_id}: {e}")
        return None