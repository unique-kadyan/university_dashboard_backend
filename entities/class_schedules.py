from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from configs.db_config import Base


class ClassSchedule(Base):
    __tablename__ = "class_schedules"

    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(
        Integer, ForeignKey("course_offering.id"), nullable=False
    )
    slot_id = Column(Integer, ForeignKey("timetable_slots.id"), nullable=False)
    room_no = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_class_schedules_course_id", "course_offering_id"),
        Index("idx_class_schedules_slot_id", "slot_id"),
        Index("idx_class_schedules_room_no", "room_no"),
        Index("idx_class_schedules_is_active", "is_active"),
    )
