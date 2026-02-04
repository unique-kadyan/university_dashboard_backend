from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from configs.db_config import Base


class fee_structure(Base):
    __tablename__ = "fee_structures"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    acedamic_year = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    tution_fee = Column(Decimal(10, 2), nullable=False)
    lab_fee = Column(Decimal(10, 2), nullable=False)
    library_fee = Column(Decimal(10, 2), nullable=False)
    sports_fee = Column(Decimal(10, 2), nullable=False)
    examination_fee = Column(Decimal(10, 2), nullable=False)
    hostel_fee = Column(Decimal(10, 2), nullable=True)
    other_fee = Column(Decimal(10, 2), nullable=True)
    total_fee = Column(Decimal(10, 2), nullable=False)
    due_date = Column(DateTime, nullable=False)
    late_fee_per_day = Column(Decimal(10, 2), default=0, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_fee_structures_program_id", "program_id"),
        Index("idx_fee_structures_student_id", "student_id"),
        Index("idx_fee_structures_acedamic_year", "acedamic_year"),
        Index("idx_fee_structures_semester", "semester"),
        UniqueConstraint(
            "program_id",
            "student_id",
            "acedamic_year",
            "semester",
            name="uix_fee_structure",
        ),
    )
