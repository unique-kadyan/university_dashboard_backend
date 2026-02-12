from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Integer,
    Numeric,
    String,
    ForeignKey,
    Index,
    func,
)
from configs.db_config import Base
from enums.payment_mode import PaymentMode
from enums.payment_status import PaymentStatus


class FeePayment(Base):
    __tablename__ = "fee_payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    fee_structure_id = Column(Integer, ForeignKey("fee_structures.id"), nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_mode = Column(Enum(PaymentMode), nullable=False)
    transaction_id = Column(String, unique=True, nullable=False)
    reciept_number = Column(String, unique=True, nullable=False)
    late_fee = Column(Numeric(10, 2), default=0, nullable=True)
    discount = Column(Numeric(10, 2), default=0, nullable=True)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    remarks = Column(String, nullable=True)
    processed_by = Column(Integer, ForeignKey("admin_staff.id"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_fee_payments_student_id", "student_id"),
        Index("idx_fee_payments_fee_structure_id", "fee_structure_id"),
        Index("idx_fee_payments_payment_status", "payment_status"),
        Index("idx_fee_payments_payment_date", "payment_date"),
    )
