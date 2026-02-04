from decimal import Decimal
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column
from datetime import Date, datetime

from configs.db_config import Base


class Parent(Base):

    __tablename__ = "parents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    father_name = Column(String, nullable=False)
    mother_name = Column(String, nullable=False)
    father_occupation = Column(String, nullable=True)
    mother_occupation = Column(String, nullable=True)
    father_contact = Column(String, nullable=True)
    mother_contact = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(Integer, nullable=True)
    annual_income = Column(Decimal, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(default=DateTime.now(), nullable=True)
    updated_at = Column(Date, nullable=True)

    __table_args__ = (
        Index("idx_parents_user_id", "user_id"),
        Index("idx_parents_father_name", "father_name"),
        Index("idx_parents_mother_name", "mother_name"),
    )
