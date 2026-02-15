from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)

from configs.db_config import Base
from enums.hostel_types import HostelType


class Hostel(Base):
    __tablename__ = "hostels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    hostel_type = Column(Enum(HostelType), nullable=False)
    address = Column(String, nullable=True)
    total_rooms = Column(Integer, nullable=False)
    total_capacity = Column(Integer, nullable=False)
    occupied_capacity = Column(Integer, default=0, nullable=False)
    warden_id = Column(Integer, ForeignKey("admin_staff.id", ondelete="SET NULL"), nullable=True)
    aminities = Column(JSON, nullable=True)
    rules = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_hostels_name", "name"),
        Index("idx_hostel_type", "hostel_type"),
        Index("idx_hostels_is_active", "is_active"),
    )
