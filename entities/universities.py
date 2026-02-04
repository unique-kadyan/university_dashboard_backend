from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from configs.db_config import Base

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    established_year = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    website = Column(String, nullable=True)
    created_at : Mapped[DateTime] = mapped_column(default=DateTime.now(), nullable=False)
    updated_at = Column(Date, nullable=True)

    __table_args__ = (
        Index("idx_universities_name", "name"),
        Index("idx_universities_is_active", "is_active"),
        Index("idx_universities_code", "code")
    )