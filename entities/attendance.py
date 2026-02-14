from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from configs.db_config import Base
from enums.attendance_status import AttendanceStatus


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_offering_id = Column(
        Integer, ForeignKey("program_courses.id"), nullable=True
    )
    date = Column(DateTime, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    marked_by = Column(String, ForeignKey("faculty.id"), nullable=False)
    remarks = Column(String, nullable=True)
    marked_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_attendance_enrollment_id", "enrollment_id"),
        Index("idx_attendance_course_offering_id", "course_offering_id"),
        Index("idx_attendance_date", "date"),
        Index("idx_attendance_status", "status"),
        UniqueConstraint("enrollment_id", "date", name="uix_enrollment_date"),
    )
