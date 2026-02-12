from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.attendance_schemas import (
    AttendanceCreateRequest,
    AttendanceDefaulterResponse,
    AttendanceReportResponse,
    AttendanceResponse,
    AttendanceSummaryResponse,
    AttendanceUpdateRequest,
    BulkAttendanceRequest,
    BulkAttendanceResponse,
)
from schemas.student_schemas import PaginatedResponse
from services.attendance_service import AttendanceService
from utils.auth_dependency import get_current_user

router = APIRouter(prefix="/api/v1/attendance", tags=["Attendance Management"])


@router.get(
    "/summary",
    response_model=list[AttendanceSummaryResponse],
    status_code=status.HTTP_200_OK,
)
async def get_attendance_summary(
    enrollment_id: Optional[int] = Query(None, description="Filter by enrollment"),
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(),
):
    return await attendance_service.get_summary(
        enrollment_id=enrollment_id, month=month
    )


@router.get(
    "/reports",
    response_model=AttendanceReportResponse,
    status_code=status.HTTP_200_OK,
)
async def get_attendance_reports(
    enrollment_id: Optional[int] = Query(None, description="Filter by enrollment"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    current_user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(),
):
    return await attendance_service.get_reports(
        enrollment_id=enrollment_id,
        student_id=student_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get(
    "/defaulters",
    response_model=AttendanceDefaulterResponse,
    status_code=status.HTTP_200_OK,
)
async def get_attendance_defaulters(
    threshold: float = Query(75.0, description="Attendance percentage threshold"),
    current_user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(),
):
    return await attendance_service.get_defaulters(threshold=threshold)


@router.get(
    "/",
    response_model=PaginatedResponse[AttendanceResponse],
    status_code=status.HTTP_200_OK,
)
async def get_attendance_records(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    enrollment_id: Optional[int] = Query(None, description="Filter by enrollment"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    attendance_status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Start date"),
    date_to: Optional[datetime] = Query(None, description="End date"),
    current_user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(),
):
    return await attendance_service.get_attendance_records(
        page=page,
        page_size=page_size,
        enrollment_id=enrollment_id,
        student_id=student_id,
        attendance_status=attendance_status,
        date_from=date_from,
        date_to=date_to,
    )


@router.post(
    "/",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def mark_attendance(
    attendance_data: AttendanceCreateRequest,
    current_user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(),
):
    if current_user["role"] not in ["admin", "staff", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, staff, and faculty can mark attendance",
        )
    return await attendance_service.mark_attendance(
        attendance_data, marked_by=current_user["id"]
    )


@router.post(
    "/bulk",
    response_model=BulkAttendanceResponse,
    status_code=status.HTTP_200_OK,
)
async def bulk_mark_attendance(
    bulk_data: BulkAttendanceRequest,
    current_user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(),
):
    if current_user["role"] not in ["admin", "staff", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, staff, and faculty can mark attendance",
        )
    return await attendance_service.bulk_mark_attendance(
        bulk_data, marked_by=current_user["id"]
    )


@router.put(
    "/{id}",
    response_model=AttendanceResponse,
    status_code=status.HTTP_200_OK,
)
async def update_attendance(
    id: int,
    attendance_data: AttendanceUpdateRequest,
    current_user: dict = Depends(get_current_user),
    attendance_service: AttendanceService = Depends(),
):
    if current_user["role"] not in ["admin", "staff", "faculty"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin, staff, and faculty can update attendance",
        )
    return await attendance_service.update_attendance(id, attendance_data)
