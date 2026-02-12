from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from schemas.faculty_schemas import (
    FacultyCourseResponse,
    FacultyPhotoUploadResponse,
    FacultyRegisterRequest,
    FacultyRegisterResponse,
    FacultyResponse,
    FacultyScheduleResponse,
    FacultyStudentResponse,
    FacultyUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse
from services.faculty_service import FacultyService
from utils.auth_dependency import get_current_user

router = APIRouter(prefix="/api/v1/faculty", tags=["Faculty Management"])


@router.get(
    "/",
    response_model=PaginatedResponse[FacultyResponse],
    status_code=status.HTTP_200_OK,
)
async def get_faculty(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    faculty_status: Optional[str] = Query(
        None,
        description="Filter by status (active, inactive, suspended, retired, terminated)",
    ),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    employment_type: Optional[str] = Query(
        None,
        description="Filter by employment type (permanent, contract, visiting, parttime)",
    ),
    is_hod: Optional[bool] = Query(None, description="Filter by HOD status"),
    search: Optional[str] = Query(
        None, description="Search by employee ID or designation"
    ),
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    return await faculty_service.get_all_faculty(
        page=page,
        page_size=page_size,
        status=faculty_status,
        department_id=department_id,
        employment_type=employment_type,
        is_hod=is_hod,
        search=search,
    )


@router.post(
    "/",
    response_model=FacultyRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_faculty(
    faculty_data: FacultyRegisterRequest,
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can register faculty",
        )
    return await faculty_service.create_faculty(faculty_data)


@router.get("/{id}", response_model=FacultyResponse, status_code=status.HTTP_200_OK)
async def get_faculty_by_id(
    id: str,
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    return await faculty_service.get_faculty_by_id(id)


@router.put("/{id}", response_model=FacultyResponse, status_code=status.HTTP_200_OK)
async def update_faculty(
    id: str,
    faculty_data: FacultyUpdateRequest,
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update faculty",
        )
    return await faculty_service.update_faculty(id, faculty_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faculty(
    id: str,
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete faculty",
        )
    await faculty_service.delete_faculty(id)


@router.get(
    "/{id}/courses",
    response_model=list[FacultyCourseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_faculty_courses(
    id: str,
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    return await faculty_service.get_faculty_courses(id)


@router.get(
    "/{id}/schedule",
    response_model=list[FacultyScheduleResponse],
    status_code=status.HTTP_200_OK,
)
async def get_faculty_schedule(
    id: str,
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    return await faculty_service.get_faculty_schedule(id)


@router.get(
    "/{id}/students",
    response_model=list[FacultyStudentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_faculty_students(
    id: str,
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    return await faculty_service.get_faculty_students(id)


@router.post(
    "/{id}/upload-photo",
    response_model=FacultyPhotoUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_faculty_photo(
    id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(),
):
    if (
        current_user["role"] not in ["admin", "staff"]
        and str(current_user["user_id"]) != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload photo for this faculty",
        )
    return await faculty_service.upload_faculty_photo(id, file)
