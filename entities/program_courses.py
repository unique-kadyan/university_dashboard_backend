from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)

from configs.db_config import Base


# NOTE: This file is NOT registered in __init__.py because course_offerings.py
# already maps ProgramCourse to the "program_courses" table with more complete columns.
# This file is kept for reference only. Do not import it alongside course_offerings.py.
class ProgramCourseLink(Base):
    __tablename__ = "program_course_links"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    semester = Column(Integer, nullable=False)
    is_mandatory = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_program_course_links_program_id", "program_id"),
        Index("idx_program_course_links_course_id", "course_id"),
        Index("idx_program_course_links_semester", "semester"),
        UniqueConstraint(
            "program_id", "course_id", "semester", name="uq_program_course_link_semester"
        ),
    )
