import math
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from entities.fee_payments import FeePayment
from entities.fee_structures import FeeStructure
from enums.payment_status import PaymentStatus
from repositories.fee_repository import FeeRepository
from schemas.fee_schemas import (
    FeeDefaulterItem,
    FeeDefaulterResponse,
    FeePaymentCreateRequest,
    FeePaymentDetailResponse,
    FeeStructureCreateRequest,
    FeeStructureResponse,
    FeeStructureUpdateRequest,
    PendingPaymentItem,
    PendingPaymentResponse,
    ReceiptFeeBreakdown,
    ReceiptResponse,
    RefundRequest,
    RefundResponse,
)
from schemas.student_schemas import PaginatedResponse
from utils.safe_update import apply_update


class FeeStructureService:
    def __init__(self, repo: FeeRepository = Depends()):
        self.repo = repo

    async def list_fee_structures(
        self,
        page: int,
        page_size: int,
        program_id: Optional[int] = None,
        student_id: Optional[int] = None,
        acedamic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> PaginatedResponse[FeeStructureResponse]:
        records, total = await self.repo.find_fee_structures_paginated(
            page=page,
            page_size=page_size,
            program_id=program_id,
            student_id=student_id,
            acedamic_year=acedamic_year,
            semester=semester,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[FeeStructureResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_fee_structure(
        self, data: FeeStructureCreateRequest
    ) -> FeeStructureResponse:
        student = await self.repo.find_student_by_id(data.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        fee_structure = FeeStructure(
            program_id=data.program_id,
            student_id=data.student_id,
            acedamic_year=data.acedamic_year,
            semester=data.semester,
            tution_fee=data.tution_fee,
            lab_fee=data.lab_fee,
            library_fee=data.library_fee,
            sports_fee=data.sports_fee,
            examination_fee=data.examination_fee,
            hostel_fee=data.hostel_fee,
            other_fee=data.other_fee,
            total_fee=data.total_fee,
            due_date=data.due_date,
            late_fee_per_day=data.late_fee_per_day,
        )
        try:
            fee_structure = await self.repo.create_fee_structure(fee_structure)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Fee structure already exists for this program, student, year, and semester",
            )
        return FeeStructureResponse.model_validate(fee_structure)

    async def get_fee_structure(self, id: int) -> FeeStructureResponse:
        fee_structure = await self.repo.find_fee_structure_by_id(id)
        if not fee_structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found",
            )
        return FeeStructureResponse.model_validate(fee_structure)

    async def update_fee_structure(
        self, id: int, data: FeeStructureUpdateRequest
    ) -> FeeStructureResponse:
        fee_structure = await self.repo.find_fee_structure_by_id(id)
        if not fee_structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        apply_update(fee_structure, update_data)

        fee_structure = await self.repo.update_fee_structure(fee_structure)
        return FeeStructureResponse.model_validate(fee_structure)


class FeePaymentService:
    def __init__(self, repo: FeeRepository = Depends()):
        self.repo = repo

    def _generate_receipt_number(self) -> str:
        return f"RCP-{uuid.uuid4().hex[:10].upper()}"

    async def list_payments(
        self,
        page: int,
        page_size: int,
        student_id: Optional[int] = None,
        fee_structure_id: Optional[int] = None,
        payment_status: Optional[str] = None,
    ) -> PaginatedResponse[FeePaymentDetailResponse]:
        records, total = await self.repo.find_payments_paginated(
            page=page,
            page_size=page_size,
            student_id=student_id,
            fee_structure_id=fee_structure_id,
            payment_status=payment_status,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[FeePaymentDetailResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def record_payment(
        self, data: FeePaymentCreateRequest, processed_by_user_id: int
    ) -> FeePaymentDetailResponse:
        fee_structure = await self.repo.find_fee_structure_by_id(data.fee_structure_id)
        if not fee_structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found",
            )

        student = await self.repo.find_student_by_id(data.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        admin_staff = await self.repo.find_admin_staff_by_user_id(processed_by_user_id)
        if not admin_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin staff can process payments",
            )

        reciept_number = self._generate_receipt_number()

        payment = FeePayment(
            student_id=data.student_id,
            fee_structure_id=data.fee_structure_id,
            amount_paid=data.amount_paid,
            payment_date=data.payment_date,
            payment_mode=data.payment_mode,
            transaction_id=data.transaction_id,
            reciept_number=reciept_number,
            late_fee=data.late_fee,
            discount=data.discount,
            payment_status=PaymentStatus.COMPLETED,
            remarks=data.remarks,
            processed_by=admin_staff.id,
        )
        try:
            payment = await self.repo.create_payment(payment)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate transaction ID or receipt number",
            )
        return FeePaymentDetailResponse.model_validate(payment)

    async def get_payment(self, id: int) -> FeePaymentDetailResponse:
        payment = await self.repo.find_payment_by_id(id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        return FeePaymentDetailResponse.model_validate(payment)

    async def generate_receipt(self, payment_id: int) -> ReceiptResponse:
        payment = await self.repo.find_payment_by_id(payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        fee_structure = await self.repo.find_fee_structure_by_id(
            payment.fee_structure_id
        )
        if not fee_structure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fee structure not found",
            )

        student_name = await self.repo.get_student_name(payment.student_id)

        return ReceiptResponse(
            reciept_number=payment.reciept_number,
            student_id=payment.student_id,
            student_name=student_name,
            acedamic_year=fee_structure.acedamic_year,
            semester=fee_structure.semester,
            fee_breakdown=ReceiptFeeBreakdown(
                tution_fee=fee_structure.tution_fee,
                lab_fee=fee_structure.lab_fee,
                library_fee=fee_structure.library_fee,
                sports_fee=fee_structure.sports_fee,
                examination_fee=fee_structure.examination_fee,
                hostel_fee=fee_structure.hostel_fee,
                other_fee=fee_structure.other_fee,
                total_fee=fee_structure.total_fee,
            ),
            amount_paid=payment.amount_paid,
            late_fee=payment.late_fee,
            discount=payment.discount,
            payment_date=payment.payment_date,
            payment_mode=payment.payment_mode,
            transaction_id=payment.transaction_id,
            payment_status=payment.payment_status,
        )

    async def get_pending_payments(
        self, student_id: Optional[int] = None
    ) -> PendingPaymentResponse:
        rows = await self.repo.get_pending_payments(student_id=student_id)
        now = datetime.now(timezone.utc)
        records = []
        for row in rows:
            total_fee = Decimal(str(row["total_fee"]))
            total_paid = Decimal(str(row["total_paid"]))
            balance = total_fee - total_paid
            due_date = row["due_date"]
            is_overdue = due_date < now if due_date else False

            records.append(
                PendingPaymentItem(
                    student_id=row["student_id"],
                    fee_structure_id=row["fee_structure_id"],
                    acedamic_year=row["acedamic_year"],
                    semester=row["semester"],
                    total_fee=total_fee,
                    total_paid=total_paid,
                    balance=balance,
                    due_date=due_date,
                    is_overdue=is_overdue,
                )
            )
        return PendingPaymentResponse(records=records, total=len(records))

    async def get_fee_defaulters(self) -> FeeDefaulterResponse:
        rows = await self.repo.get_fee_defaulters()
        now = datetime.now(timezone.utc)
        defaulters = []
        for row in rows:
            total_fee = Decimal(str(row["total_fee"]))
            total_paid = Decimal(str(row["total_paid"]))
            balance = total_fee - total_paid
            due_date = row["due_date"]
            days_overdue = (now - due_date).days if due_date else 0

            defaulters.append(
                FeeDefaulterItem(
                    student_id=row["student_id"],
                    fee_structure_id=row["fee_structure_id"],
                    acedamic_year=row["acedamic_year"],
                    semester=row["semester"],
                    total_fee=total_fee,
                    total_paid=total_paid,
                    balance=balance,
                    due_date=due_date,
                    days_overdue=max(days_overdue, 0),
                )
            )
        return FeeDefaulterResponse(defaulters=defaulters, total=len(defaulters))

    async def process_refund(
        self, data: RefundRequest, processed_by_user_id: int
    ) -> RefundResponse:
        payment = await self.repo.find_payment_by_id(data.payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        if str(payment.payment_status) not in [
            PaymentStatus.COMPLETED.value,
            "PaymentStatus.COMPLETED",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only completed payments can be refunded",
            )

        admin_staff = await self.repo.find_admin_staff_by_user_id(processed_by_user_id)
        if not admin_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin staff can process refunds",
            )

        payment.payment_status = PaymentStatus.REFUNDED
        payment.remarks = f"{payment.remarks or ''} | Refund: {data.reason}".strip(" |")
        payment.updated_at = datetime.now(timezone.utc)
        await self.repo.update_payment(payment)

        return RefundResponse(
            payment_id=payment.id,
            reciept_number=payment.reciept_number,
            amount_refunded=payment.amount_paid,
            status="refunded",
            message="Payment refunded successfully",
        )
