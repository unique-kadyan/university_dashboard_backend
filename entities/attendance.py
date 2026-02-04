from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from configs.db_config import Base
from enums.attendance_status import AttendanceStatus


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(
        Integer, ForeignKey("enrollments.id"), unique=True, nullable=False
    )
    student_id = Column(Integer, nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    status = Column(Enum(AttendanceStatus), nullable=False)
    marked_by = Column(Integer, ForeignKey("faculty.id"), nullable=False)
    remarks = Column(String, nullable=True)
    marked_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __tableargs__ = (
        Index("idx_attendance_enrollment_id", "enrollment_id"),
        Index("idx_attendance_date", "date"),
        Index("idx_attendance_status", "status"),
        UniqueConstraint("enrollment_id", "date", name="uix_enrollment_date"),
    )
