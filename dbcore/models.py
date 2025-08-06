from dbcore.session import Base
from sqlalchemy import (
    Column, String, Integer, DateTime, func, Boolean, Text
)

# -------------------------------------------------------------------
# Case model - represents a scraped or created case entry
# -------------------------------------------------------------------
class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True)

    reference = Column(String, nullable=True, default=None)
    site_address = Column(Text, nullable=True, default=None)
    type = Column(String, nullable=True, default=None)
    local_planning_authority = Column(String, nullable=True, default=None)
    officer = Column(String, nullable=True, default=None)
    status = Column(String, nullable=True, default=None)
    decision_date = Column(String, nullable=True, default=None)
    pdf_url = Column(Text, nullable=True, default=None)
    pdf_name = Column(Text, nullable=True, default=None)
    pdf_downloaded = Column(Boolean, nullable=False, default=False)


    updated_at = Column(DateTime, onupdate=func.now())
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"Case(id={self.id}, view_case=ViewCase.aspx?CaseID={self.id})"
