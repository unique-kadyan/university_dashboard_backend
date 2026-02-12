from sqlalchemy import Column, DateTime, Enum, Integer, func

from configs.db_config import Base
from enums.slot_types import SlotType


class TimetableSlot(Base):
    __tablename__ = "timetable_slots"

    id = Column(Integer, primary_key=True, index=True)
    slot_type = Column(Enum(SlotType), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)
