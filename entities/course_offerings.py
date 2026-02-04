from sqlalchemy import Column, DateTime, Enum, Integer, JSON, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY as Array

from configs.db_config import Base
from enums.course_status import CourseStatus

class ProgramCourse(Base):
    __tablename__ = "program_courses"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    faculty_id = Column(Array(Integer), ForeignKey("faculty.id"), nullable=True)
    semester = Column(Integer, nullable=False)
    acedemic_year = Column(String, nullable=False)
    section = Column(String, nullable=True)
    max_capacity = Column(Integer, nullable=True)
    enrolled_students = Column(Integer, nullable=True)
    room_number = Column(String, nullable=True)
    schedule = Column(JSON, nullable=True)
    status = Column(Enum(CourseStatus), nullable=False)
    start_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_program_courses_program_id", "program_id"),
        Index("idx_program_courses_course_id", "course_id"),
        Index("idx_program_courses_faculty_id", "faculty_id"),
        Index("idx_program_courses_acedemic_year", "acedemic_year"),
        Index("idx_program_courses_semester", "semester"),
    )