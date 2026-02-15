from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Index, func
from configs.db_config import Base
from enums.degree_type import DegreeType


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    degree_type = Column(DegreeType, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    duration_years = Column(Integer, nullable=False)
    total_semesters = Column(Integer, nullable=False)
    total_credits = Column(Integer, nullable=False)
    eligibity_criteria = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_programs_name", "name"),
        Index("idx_programs_code", "code"),
        Index("idx_programs_department_id", "department_id"),
    )
