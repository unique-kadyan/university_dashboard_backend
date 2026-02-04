from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from configs.db_config import Base
from enums.hostel_allocation_status import HostelAllocationStatus


class HostelAllocation(Base):
    __tablename__ = "hostel_allocations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("hostel_rooms.id"), nullable=False)
    allocation_date: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    release_date = Column(DateTime, nullable=True)
    acedamic_year = Column(String, nullable=False)
    status = Column(Enum(HostelAllocationStatus), nullable=False)
    remarks = Column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(default=DateTime.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_hostel_allocations_student_id", "student_id"),
        Index("idx_hostel_allocations_hostel_id", "hostel_id"),
        Index("idx_hostel_allocations_room_id", "room_id"),
        Index("idx_hostel_allocations_status", "status"),
    )
