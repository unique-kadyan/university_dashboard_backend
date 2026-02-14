from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from configs.db_config import Base


class Grades(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    course_offering_id = Column(
        Integer, ForeignKey("program_courses.id"), nullable=True
    )
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    marks_obtained = Column(Numeric(6, 2), nullable=False)
    remarks = Column(String, nullable=True)
    graded_by = Column(String, ForeignKey("faculty.id"), nullable=False)
    graded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_grades_enrollment_id", "enrollment_id"),
        Index("idx_grades_course_offering_id", "course_offering_id"),
        Index("idx_grades_assessment_id", "assessment_id"),
        UniqueConstraint(
            "enrollment_id", "assessment_id", name="uix_enrollment_assessment"
        ),
    )
