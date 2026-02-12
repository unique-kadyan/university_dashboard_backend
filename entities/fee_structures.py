from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    ForeignKey,
    Index,
    UniqueConstraint,
    func,
)
from configs.db_config import Base


class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    acedamic_year = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    tution_fee = Column(Numeric(10, 2), nullable=False)
    lab_fee = Column(Numeric(10, 2), nullable=False)
    library_fee = Column(Numeric(10, 2), nullable=False)
    sports_fee = Column(Numeric(10, 2), nullable=False)
    examination_fee = Column(Numeric(10, 2), nullable=False)
    hostel_fee = Column(Numeric(10, 2), nullable=True)
    other_fee = Column(Numeric(10, 2), nullable=True)
    total_fee = Column(Numeric(10, 2), nullable=False)
    due_date = Column(DateTime, nullable=False)
    late_fee_per_day = Column(Numeric(10, 2), default=0, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
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
