from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FeeStructureResponse(BaseModel):
    id: int
    program_id: int
    student_id: int
    acedamic_year: str
    semester: int
    tution_fee: Decimal
    lab_fee: Decimal
    library_fee: Decimal
    sports_fee: Decimal
    examination_fee: Decimal
    hostel_fee: Optional[Decimal] = None
    other_fee: Optional[Decimal] = None
    total_fee: Decimal
    due_date: datetime
    late_fee_per_day: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeeStructureCreateRequest(BaseModel):
    program_id: int
    student_id: int
    acedamic_year: str
    semester: int
    tution_fee: Decimal
    lab_fee: Decimal
    library_fee: Decimal
    sports_fee: Decimal
    examination_fee: Decimal
    hostel_fee: Optional[Decimal] = None
    other_fee: Optional[Decimal] = None
    total_fee: Decimal
    due_date: datetime
    late_fee_per_day: Optional[Decimal] = None


class FeeStructureUpdateRequest(BaseModel):
    tution_fee: Optional[Decimal] = None
    lab_fee: Optional[Decimal] = None
    library_fee: Optional[Decimal] = None
    sports_fee: Optional[Decimal] = None
    examination_fee: Optional[Decimal] = None
    hostel_fee: Optional[Decimal] = None
    other_fee: Optional[Decimal] = None
    total_fee: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    late_fee_per_day: Optional[Decimal] = None


class FeePaymentDetailResponse(BaseModel):
    id: int
    student_id: int
    fee_structure_id: int
    amount_paid: Decimal
    payment_date: date
    payment_mode: str
    transaction_id: str
    reciept_number: str
    late_fee: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    payment_status: str
    remarks: Optional[str] = None
    processed_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeePaymentCreateRequest(BaseModel):
    student_id: int
    fee_structure_id: int
    amount_paid: Decimal
    payment_date: date
    payment_mode: str
    transaction_id: str
    late_fee: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    remarks: Optional[str] = None


class ReceiptFeeBreakdown(BaseModel):
    tution_fee: Decimal
    lab_fee: Decimal
    library_fee: Decimal
    sports_fee: Decimal
    examination_fee: Decimal
    hostel_fee: Optional[Decimal] = None
    other_fee: Optional[Decimal] = None
    total_fee: Decimal


class ReceiptResponse(BaseModel):
    reciept_number: str
    student_id: int
    student_name: str
    acedamic_year: str
    semester: int
    fee_breakdown: ReceiptFeeBreakdown
    amount_paid: Decimal
    late_fee: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    payment_date: date
    payment_mode: str
    transaction_id: str
    payment_status: str


class PendingPaymentItem(BaseModel):
    student_id: int
    fee_structure_id: int
    acedamic_year: str
    semester: int
    total_fee: Decimal
    total_paid: Decimal
    balance: Decimal
    due_date: datetime
    is_overdue: bool


class PendingPaymentResponse(BaseModel):
    records: list[PendingPaymentItem]
    total: int


class FeeDefaulterItem(BaseModel):
    student_id: int
    fee_structure_id: int
    acedamic_year: str
    semester: int
    total_fee: Decimal
    total_paid: Decimal
    balance: Decimal
    due_date: datetime
    days_overdue: int


class FeeDefaulterResponse(BaseModel):
    defaulters: list[FeeDefaulterItem]
    total: int


class RefundRequest(BaseModel):
    payment_id: int
    reason: str


class RefundResponse(BaseModel):
    payment_id: int
    reciept_number: str
    amount_refunded: Decimal
    status: str
    message: str
