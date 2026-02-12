from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from configs.db_config import Base
from enums.assessment_type import AssessmentType


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(
        Integer, ForeignKey("program_courses.id"), nullable=False
    )
    name = Column(String, nullable=False)
    assessment_type = Column(Enum(AssessmentType), nullable=False)
    description = Column(String, nullable=True)
    max_marks = Column(Numeric(10, 2), nullable=False)
    weightage = Column(Numeric(6, 2), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_course_offering_id", "course_offering_id"),
        Index("idx_assessment_type", "assessment_type"),
        UniqueConstraint(
            "course_offering_id", "assessment_type", name="uix_course_assessment_name"
        ),
    )
