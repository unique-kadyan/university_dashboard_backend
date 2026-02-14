from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.fee_schemas import (
    FeeDefaulterResponse,
    FeePaymentCreateRequest,
    FeePaymentDetailResponse,
    FeeStructureCreateRequest,
    FeeStructureResponse,
    FeeStructureUpdateRequest,
    PendingPaymentResponse,
    ReceiptResponse,
    RefundRequest,
    RefundResponse,
)
from schemas.student_schemas import PaginatedResponse
from services.fee_service import FeePaymentService, FeeStructureService
from utils.auth_dependency import get_current_user

fee_structures_router = APIRouter(
    prefix="/api/v1/fee-structures", tags=["Fee Structures"]
)


@fee_structures_router.get(
    "/",
    response_model=PaginatedResponse[FeeStructureResponse],
    status_code=status.HTTP_200_OK,
)
async def list_fee_structures(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    program_id: Optional[int] = Query(None, description="Filter by program"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    acedamic_year: Optional[str] = Query(None, description="Filter by academic year"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    current_user: dict = Depends(get_current_user),
    service: FeeStructureService = Depends(),
):
    return await service.list_fee_structures(
        page=page,
        page_size=page_size,
        program_id=program_id,
        student_id=student_id,
        acedamic_year=acedamic_year,
        semester=semester,
    )


@fee_structures_router.post(
    "/",
    response_model=FeeStructureResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_fee_structure(
    data: FeeStructureCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: FeeStructureService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create fee structures",
        )
    return await service.create_fee_structure(data)


@fee_structures_router.get(
    "/{id}",
    response_model=FeeStructureResponse,
    status_code=status.HTTP_200_OK,
)
async def get_fee_structure(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: FeeStructureService = Depends(),
):
    return await service.get_fee_structure(id)


@fee_structures_router.put(
    "/{id}",
    response_model=FeeStructureResponse,
    status_code=status.HTTP_200_OK,
)
async def update_fee_structure(
    id: int,
    data: FeeStructureUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: FeeStructureService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update fee structures",
        )
    return await service.update_fee_structure(id, data)


fee_payments_router = APIRouter(prefix="/api/v1/fee-payments", tags=["Fee Payments"])


@fee_payments_router.get(
    "/pending",
    response_model=PendingPaymentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_pending_payments(
    student_id: Optional[int] = Query(None, description="Filter by student"),
    current_user: dict = Depends(get_current_user),
    service: FeePaymentService = Depends(),
):
    return await service.get_pending_payments(student_id=student_id)


@fee_payments_router.get(
    "/defaulters",
    response_model=FeeDefaulterResponse,
    status_code=status.HTTP_200_OK,
)
async def get_fee_defaulters(
    current_user: dict = Depends(get_current_user),
    service: FeePaymentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can view fee defaulters",
        )
    return await service.get_fee_defaulters()


@fee_payments_router.get(
    "/",
    response_model=PaginatedResponse[FeePaymentDetailResponse],
    status_code=status.HTTP_200_OK,
)
async def list_payments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    fee_structure_id: Optional[int] = Query(
        None, description="Filter by fee structure"
    ),
    payment_status: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user),
    service: FeePaymentService = Depends(),
):
    return await service.list_payments(
        page=page,
        page_size=page_size,
        student_id=student_id,
        fee_structure_id=fee_structure_id,
        payment_status=payment_status,
    )


@fee_payments_router.post(
    "/",
    response_model=FeePaymentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_payment(
    data: FeePaymentCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: FeePaymentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can record payments",
        )
    return await service.record_payment(
        data, processed_by_user_id=int(current_user["id"])
    )


@fee_payments_router.post(
    "/refund",
    response_model=RefundResponse,
    status_code=status.HTTP_200_OK,
)
async def process_refund(
    data: RefundRequest,
    current_user: dict = Depends(get_current_user),
    service: FeePaymentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can process refunds",
        )
    return await service.process_refund(
        data, processed_by_user_id=int(current_user["id"])
    )


@fee_payments_router.get(
    "/{id}",
    response_model=FeePaymentDetailResponse,
    status_code=status.HTTP_200_OK,
)
async def get_payment(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: FeePaymentService = Depends(),
):
    return await service.get_payment(id)


@fee_payments_router.get(
    "/{id}/receipt",
    response_model=ReceiptResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_receipt(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: FeePaymentService = Depends(),
):
    return await service.generate_receipt(id)
