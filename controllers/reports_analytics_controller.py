from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.report_schemas import (
    AttendanceReport,
    DashboardStats,
    DepartmentWiseReport,
    ExamResultsReport,
    FeeCollectionReport,
    HostelOccupancyReport,
    LibraryStatsReport,
    StudentPerformanceReport,
    TrendsAnalysis,
)
from services.report_service import ReportService
from utils.auth_dependency import get_current_user

reports_router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])
analytics_router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@reports_router.get(
    "/student-performance",
    response_model=StudentPerformanceReport,
    status_code=status.HTTP_200_OK,
)
async def student_performance_report(
    department_id: Optional[int] = Query(None, description="Filter by department"),
    program_id: Optional[int] = Query(None, description="Filter by program"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access reports",
        )
    return await service.get_student_performance(
        department_id=department_id,
        program_id=program_id,
        academic_year=academic_year,
    )


@reports_router.get(
    "/attendance",
    response_model=AttendanceReport,
    status_code=status.HTTP_200_OK,
)
async def attendance_report(
    department_id: Optional[int] = Query(None, description="Filter by department"),
    course_offering_id: Optional[int] = Query(
        None, description="Filter by course offering"
    ),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access reports",
        )
    return await service.get_attendance_report(
        department_id=department_id,
        course_offering_id=course_offering_id,
    )


@reports_router.get(
    "/fee-collection",
    response_model=FeeCollectionReport,
    status_code=status.HTTP_200_OK,
)
async def fee_collection_report(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access reports",
        )
    return await service.get_fee_collection_report(
        academic_year=academic_year,
        semester=semester,
        department_id=department_id,
    )


@reports_router.get(
    "/exam-results",
    response_model=ExamResultsReport,
    status_code=status.HTTP_200_OK,
)
async def exam_results_report(
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access reports",
        )
    return await service.get_exam_results_report(
        academic_year=academic_year,
        semester=semester,
    )


@reports_router.get(
    "/library-stats",
    response_model=LibraryStatsReport,
    status_code=status.HTTP_200_OK,
)
async def library_stats_report(
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access reports",
        )
    return await service.get_library_stats()


@reports_router.get(
    "/hostel-occupancy",
    response_model=HostelOccupancyReport,
    status_code=status.HTTP_200_OK,
)
async def hostel_occupancy_report(
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access reports",
        )
    return await service.get_hostel_occupancy()


@reports_router.get(
    "/department-wise",
    response_model=DepartmentWiseReport,
    status_code=status.HTTP_200_OK,
)
async def department_wise_report(
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access reports",
        )
    return await service.get_department_wise_report()


@analytics_router.get(
    "/dashboard",
    response_model=DashboardStats,
    status_code=status.HTTP_200_OK,
)
async def dashboard_stats(
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access analytics",
        )
    return await service.get_dashboard()


@analytics_router.get(
    "/trends",
    response_model=TrendsAnalysis,
    status_code=status.HTTP_200_OK,
)
async def trends_analysis(
    months: int = Query(12, ge=1, le=60, description="Number of months to analyze"),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can access analytics",
        )
    return await service.get_trends(months)
