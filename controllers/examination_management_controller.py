from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.exam_schemas import (
    ExamScheduleCreateRequest,
    ExamScheduleResponse,
    ExamScheduleUpdateRequest,
    ExamTimetableCreateRequest,
    ExamTimetableExportResponse,
    ExamTimetableResponse,
    ExamTimetableUpdateRequest,
    StudentExamScheduleResponse,
)
from schemas.student_schemas import PaginatedResponse
from services.exam_service import ExamScheduleService, ExamTimetableService
from utils.auth_dependency import get_current_user

exam_schedules_router = APIRouter(
    prefix="/api/v1/exams", tags=["Exam Schedules"]
)


@exam_schedules_router.get(
    "/",
    response_model=PaginatedResponse[ExamScheduleResponse],
    status_code=status.HTTP_200_OK,
)
async def list_exam_schedules(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    course_id: Optional[int] = Query(None, description="Filter by course"),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    status_filter: Optional[str] = Query(
        None, alias="status", description="Filter by status"
    ),
    exam_type: Optional[str] = Query(None, description="Filter by exam type"),
    current_user: dict = Depends(get_current_user),
    service: ExamScheduleService = Depends(),
):
    return await service.list_exam_schedules(
        page=page,
        page_size=page_size,
        course_id=course_id,
        academic_year=academic_year,
        semester=semester,
        status_filter=status_filter,
        exam_type=exam_type,
    )


@exam_schedules_router.post(
    "/",
    response_model=ExamScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_exam_schedule(
    data: ExamScheduleCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: ExamScheduleService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create exam schedules",
        )
    return await service.create_exam_schedule(data)


@exam_schedules_router.get(
    "/{id}",
    response_model=ExamScheduleResponse,
    status_code=status.HTTP_200_OK,
)
async def get_exam_schedule(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: ExamScheduleService = Depends(),
):
    return await service.get_exam_schedule(id)


@exam_schedules_router.put(
    "/{id}",
    response_model=ExamScheduleResponse,
    status_code=status.HTTP_200_OK,
)
async def update_exam_schedule(
    id: int,
    data: ExamScheduleUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: ExamScheduleService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update exam schedules",
        )
    return await service.update_exam_schedule(id, data)


@exam_schedules_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_exam_schedule(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: ExamScheduleService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete exam schedules",
        )
    await service.delete_exam_schedule(id)


exam_timetable_router = APIRouter(
    prefix="/api/v1/exam-timetable", tags=["Exam Timetable"]
)


@exam_timetable_router.get(
    "/export",
    response_model=ExamTimetableExportResponse,
    status_code=status.HTTP_200_OK,
)
async def export_timetable(
    exam_schedule_id: Optional[int] = Query(
        None, description="Filter by exam schedule"
    ),
    academic_year: Optional[str] = Query(None, description="Filter by academic year"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    current_user: dict = Depends(get_current_user),
    service: ExamTimetableService = Depends(),
):
    return await service.export_timetable(
        exam_schedule_id=exam_schedule_id,
        academic_year=academic_year,
        semester=semester,
    )


@exam_timetable_router.get(
    "/student/{student_id}",
    response_model=StudentExamScheduleResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_exam_schedule(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    service: ExamTimetableService = Depends(),
):
    return await service.get_student_exam_schedule(student_id)


@exam_timetable_router.get(
    "/",
    response_model=PaginatedResponse[ExamTimetableResponse],
    status_code=status.HTTP_200_OK,
)
async def list_exam_timetables(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    exam_schedule_id: Optional[int] = Query(
        None, description="Filter by exam schedule"
    ),
    course_offering_id: Optional[int] = Query(
        None, description="Filter by course offering"
    ),
    current_user: dict = Depends(get_current_user),
    service: ExamTimetableService = Depends(),
):
    return await service.list_exam_timetables(
        page=page,
        page_size=page_size,
        exam_schedule_id=exam_schedule_id,
        course_offering_id=course_offering_id,
    )


@exam_timetable_router.post(
    "/",
    response_model=ExamTimetableResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_exam_timetable(
    data: ExamTimetableCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: ExamTimetableService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create exam timetable entries",
        )
    return await service.create_exam_timetable(data)


@exam_timetable_router.put(
    "/{id}",
    response_model=ExamTimetableResponse,
    status_code=status.HTTP_200_OK,
)
async def update_exam_timetable(
    id: int,
    data: ExamTimetableUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: ExamTimetableService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update exam timetable entries",
        )
    return await service.update_exam_timetable(id, data)
