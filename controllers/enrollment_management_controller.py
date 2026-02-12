from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.enrollment_schemas import (
    BulkEnrollmentRequest,
    BulkEnrollmentResponse,
    EligibilityResponse,
    EnrollmentCreateRequest,
    EnrollmentResponse,
    EnrollmentUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse
from services.enrollment_service import EnrollmentService
from utils.auth_dependency import get_current_user

router = APIRouter(prefix="/api/v1/enrollments", tags=["Enrollment Management"])


@router.get(
    "/verify-eligibility",
    response_model=EligibilityResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_eligibility(
    student_id: int = Query(..., description="Student ID"),
    program_id: int = Query(..., description="Program ID"),
    current_user: dict = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(),
):
    return await enrollment_service.verify_eligibility(student_id, program_id)


@router.get(
    "/",
    response_model=PaginatedResponse[EnrollmentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_enrollments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    program_id: Optional[int] = Query(None, description="Filter by program"),
    enrollment_status: Optional[str] = Query(None, description="Filter by status"),
    current_user: dict = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(),
):
    return await enrollment_service.get_all_enrollments(
        page=page,
        page_size=page_size,
        student_id=student_id,
        program_id=program_id,
        enrollment_status=enrollment_status,
    )


@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_enrollment(
    enrollment_data: EnrollmentCreateRequest,
    current_user: dict = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create enrollments",
        )
    return await enrollment_service.create_enrollment(enrollment_data)


@router.post(
    "/bulk",
    response_model=BulkEnrollmentResponse,
    status_code=status.HTTP_200_OK,
)
async def bulk_enroll(
    bulk_data: BulkEnrollmentRequest,
    current_user: dict = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can perform bulk enrollments",
        )
    return await enrollment_service.bulk_enroll(bulk_data)


@router.get(
    "/{id}",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_enrollment_by_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(),
):
    return await enrollment_service.get_enrollment_by_id(id)


@router.put(
    "/{id}",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_enrollment(
    id: int,
    enrollment_data: EnrollmentUpdateRequest,
    current_user: dict = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update enrollments",
        )
    return await enrollment_service.update_enrollment(id, enrollment_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    id: int,
    current_user: dict = Depends(get_current_user),
    enrollment_service: EnrollmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can drop enrollments",
        )
    await enrollment_service.delete_enrollment(id)
