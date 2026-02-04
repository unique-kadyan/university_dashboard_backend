from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from configs.db_config import Base
from enums.student_status import StudentStatus


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    enrollment_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    status = Column(Enum(StudentStatus), nullable=False)
    grade = Column(String, nullable=True)
    grade_point = Column(Decimal(3, 2), nullable=True)
    credits_earned = Column(Integer, default=0, nullable=True)
    remarks = Column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __tableargs__ = (
        Index("idx_enrollments_student_id", "student_id"),
        Index("idx_enrollments_program_id", "program_id"),
        Index("idx_enrollments_status", "status"),
    )
