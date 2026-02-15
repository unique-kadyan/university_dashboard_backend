from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)

from configs.db_config import Base
from enums.hostel_room_status import HostelRoomStatus
from enums.hostel_room_types import HostelRoomType


class HostelRoom(Base):
    __tablename__ = "hostel_rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, nullable=False)
    room_type = Column(Enum(HostelRoomType), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id", ondelete="CASCADE"), nullable=False)
    floor = Column(Integer, nullable=True)
    capacity = Column(Integer, nullable=False)
    occupied_beds = Column(Integer, default=0, nullable=False)
    room_fee = Column(Numeric(10, 2), nullable=False)
    aminities = Column(JSON, nullable=True)
    status = Column(Enum(HostelRoomStatus), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_hostel_rooms_room_number", "room_number"),
        Index("idx_hostel_rooms_hostel_id", "hostel_id"),
        Index("idx_hostel_rooms_is_active", "is_active"),
        Index("idx_hostel_rooms_status", "status"),
        UniqueConstraint("hostel_id", "room_number", name="uix_hostel_room_number"),
    )
