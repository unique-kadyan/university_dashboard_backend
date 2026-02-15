from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY as Array
from configs.db_config import Base
from enums.course_type import CourseType
from enums.levels import Levels


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    credits = Column(Integer, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    course_type = Column(Enum(CourseType), nullable=False)
    level = Column(Enum(Levels), nullable=False)
    max_students = Column(Integer, nullable=True)
    prerequisites = Column(Array(Integer), nullable=True)
    syllabus = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_courses_name", "name"),
        Index("idx_courses_code", "code"),
        Index("idx_courses_department_id", "department_id"),
        Index("idx_courses_course_type", "course_type"),
    )
