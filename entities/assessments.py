from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
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
from enums.assessment_type import AssessmentType


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(
        Integer, ForeignKey("course_offerings.id"), nullable=False
    )
    name = Column(String, nullable=False)
    assessment_type = Column(Enum(AssessmentType), nullable=False)
    description = Column(String, nullable=True)
    max_marks = Column(Decimal(10, 2), nullable=False)
    weightage = Column(Decimal(6, 2), nullable=False)
    date = Column(Date, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __tableargs__ = (
        Index("idx_course_offering_id", "course_offering_id"),
        Index("idx_assessment_type", "assessment_type"),
        UniqueConstraint(
            "course_offering_id", "assessment_type", name="uix_course_assessment_name"
        ),
    )
