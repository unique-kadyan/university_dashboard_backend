from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String, func
from configs.db_config import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    hod_id = Column(String, ForeignKey("faculty.id"), nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    building = Column(String, nullable=True)
    floor = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_departments_name", "name"),
        Index("idx_departments_code", "code"),
        Index("idx_departments_is_active", "is_active"),
    )
