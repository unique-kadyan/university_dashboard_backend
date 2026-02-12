from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey, Index, func

from configs.db_config import Base
from enums.exam_status import ExamStatus
from enums.exam_types import ExamType


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    id = Column(Integer, primary_key=True, index=True)
    exam_name = Column(String, nullable=False)
    exam_type = Column(Enum(ExamType), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    academic_year = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    result_declaration_date = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    status = Column(Enum(ExamStatus), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_exam_schedules_course_id", "course_id"),
        Index("idx_exam_schedules_status", "status"),
        Index("idx_exam_schedules_academic_year", "academic_year"),
    )
