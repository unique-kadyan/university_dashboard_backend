from sqlalchemy import Column, Date, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal

from configs.db_config import Base


class AttendanceSummary(Base):
    __tablename__ = "attendance_summary"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, nullable=False)
    total_classes = Column(Integer, nullable=False)
    attended_classes = Column(Integer, nullable=False)
    attendance_percentage = Column(Decimal(5, 3), nullable=False)
    month: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __tableargs__ = (
        UniqueConstraint("enrollment_id", "month", name="uix_enrollment_month"),
    )
