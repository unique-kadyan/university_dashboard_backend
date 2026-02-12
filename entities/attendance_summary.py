from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from configs.db_config import Base


class AttendanceSummary(Base):
    __tablename__ = "attendance_summary"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    total_classes = Column(Integer, nullable=False)
    attended_classes = Column(Integer, nullable=False)
    attendance_percentage = Column(Numeric(5, 3), nullable=False)
    month = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("enrollment_id", "month", name="uix_enrollment_month"),
    )
