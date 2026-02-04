from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from configs.db_config import Base


class ProgramCourse(Base):
    __tablename__ = "program_courses"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_program_courses_program_id", "program_id"),
        Index("idx_program_courses_course_id", "course_id"),
        Index("idx_program_courses_semester", "semester"),
        UniqueConstraint(
            "program_id", "course_id", "semester", name="uq_program_course_semester"
        ),
    )
