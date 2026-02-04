from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from configs.db_config import Base


class Grades(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    marks_obtained = Column(Decimal(6, 2), nullable=False)
    remarks = Column(String, nullable=True)
    graded_by = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    graded_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __tableargs__ = (
        Index("idx_grades_enrollment_id", "enrollment_id"),
        Index("idx_grades_assessment_id", "assessment_id"),
        UniqueConstraint(
            "enrollment_id", "assessment_id", name="uix_enrollment_assessment"
        ),
    )
