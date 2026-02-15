from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.student_schemas import PaginatedResponse
from schemas.timetable_schemas import (
    ClassScheduleResponse,
    FacultyTimetableResponse,
    RoomTimetableResponse,
    StudentTimetableResponse,
    TimetableGenerateRequest,
    TimetableGenerateResponse,
    TimetableUpdateRequest,
)
from services.timetable_service import TimetableService
from utils.auth_dependency import get_current_user

timetable_router = APIRouter(prefix="/api/v1/timetable", tags=["Timetable Management"])


@timetable_router.post(
    "/generate",
    response_model=TimetableGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_timetable(
    data: TimetableGenerateRequest,
    current_user: dict = Depends(get_current_user),
    service: TimetableService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can generate timetables",
        )
    return await service.generate_timetable(data)


@timetable_router.get(
    "/student/{student_id}",
    response_model=StudentTimetableResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_timetable(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    service: TimetableService = Depends(),
):
    return await service.get_student_timetable(student_id)


@timetable_router.get(
    "/faculty/{faculty_id}",
    response_model=FacultyTimetableResponse,
    status_code=status.HTTP_200_OK,
)
async def get_faculty_timetable(
    faculty_id: int,
    current_user: dict = Depends(get_current_user),
    service: TimetableService = Depends(),
):
    return await service.get_faculty_timetable(faculty_id)


@timetable_router.get(
    "/room/{room_number}",
    response_model=RoomTimetableResponse,
    status_code=status.HTTP_200_OK,
)
async def get_room_timetable(
    room_number: str,
    current_user: dict = Depends(get_current_user),
    service: TimetableService = Depends(),
):
    return await service.get_room_timetable(room_number)


@timetable_router.get(
    "/",
    response_model=PaginatedResponse[ClassScheduleResponse],
    status_code=status.HTTP_200_OK,
)
async def list_timetables(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    course_offering_id: Optional[int] = Query(
        None, description="Filter by course offering"
    ),
    slot_id: Optional[int] = Query(None, description="Filter by slot"),
    room_no: Optional[str] = Query(None, description="Filter by room number"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: dict = Depends(get_current_user),
    service: TimetableService = Depends(),
):
    return await service.list_timetables(
        page=page,
        page_size=page_size,
        course_offering_id=course_offering_id,
        slot_id=slot_id,
        room_no=room_no,
        is_active=is_active,
    )


@timetable_router.put(
    "/{id}",
    response_model=ClassScheduleResponse,
    status_code=status.HTTP_200_OK,
)
async def update_timetable(
    id: int,
    data: TimetableUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: TimetableService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update timetables",
        )
    return await service.update_timetable(id, data)
