from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Enum,
    Integer,
    String,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal

from configs.db_config import Base
from enums.payment_mode import PaymentMode
from enums.payment_status import PaymentStatus


class FeePayment(Base):
    __tablename__ = "fee_payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    fee_structure_id = Column(Integer, ForeignKey("fee_structures.id"), nullable=False)
    amount_paid = Column(Decimal(10, 2), nullable=False)
    payment_date: Mapped[Date] = mapped_column(Date, nullable=False)
    payment_mode = Column(Enum(PaymentMode), nullable=False)
    transaction_id = Column(String, unique=True, nullable=False)
    reciept_number = Column(String, unique=True, nullable=False)
    late_fee = Column(Decimal(10, 2), default=0, nullable=True)
    discount = Column(Decimal(10, 2), default=0, nullable=True)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    remarks = Column(String, nullable=True)
    processed_by = Column(Integer, ForeignKey("admin_staff.id"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=True
    )
    updated_at = Column(DateTime, nullable=True)

    __tableargs__ = (
        Index("idx_fee_payments_student_id", "student_id"),
        Index("idx_fee_payments_fee_structure_id", "fee_structure_id"),
        Index("idx_fee_payments_payment_status", "payment_status"),
        Index("idx_fee_payments_payment_date", "payment_date"),
    )
