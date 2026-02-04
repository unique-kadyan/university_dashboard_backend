from enum import Enum
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from configs.db_config import Base
from enums.slot_types import SlotType


class TimetableSlot(Base):
    __tablename__ = "timetable_slots"

    id = Column(Integer, primary_key=True, index=True)
    slot_type = Column(Enum(SlotType), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)
