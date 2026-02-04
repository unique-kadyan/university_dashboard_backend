from decimal import Decimal
from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from configs.db_config import Base
from enums.result_status import ResultStatus


class SemesterResults(Base):
    __tablename__ = "semester_results"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(
        Integer, ForeignKey("enrollments.id"), unique=True, nullable=False
    )
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    acedamic_year = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    gpa = Column(Decimal(3, 2), nullable=False)
    cgpa = Column(Decimal(3, 2), nullable=False)
    total_credits_attempted = Column(Integer)
    total_credits_earned = Column(Integer)
    status = Column(Enum(ResultStatus), nullable=False)
    remarks = Column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_semester_results_enrollment_id", "enrollment_id"),
        Index("idx_semester_results_semester", "semester"),
    )
