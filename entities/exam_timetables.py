from sqlalchemy import Column, DateTime, Integer, Numeric, String, ForeignKey, Index, func
from configs.db_config import Base


class ExamTimetable(Base):
    __tablename__ = "exam_timetables"

    id = Column(Integer, primary_key=True, index=True)
    exam_schedule_id = Column(Integer, ForeignKey("exam_schedules.id"), nullable=False)
    course_offering_id = Column(
        Integer, ForeignKey("program_courses.id"), nullable=False
    )
    exam_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    venue = Column(String, nullable=False)
    max_marks = Column(Numeric(6, 2), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_exam_timetables_exam_schedule_id", "exam_schedule_id"),
        Index("idx_exam_timetables_course_offering_id", "course_offering_id"),
        Index("idx_exam_timetables_exam_date", "exam_date"),
    )
