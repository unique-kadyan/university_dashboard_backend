from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from schemas.student_schemas import (
    PaginatedResponse,
    PhotoUploadResponse,
    StudentAttendanceResponse,
    StudentDocumentsResponse,
    StudentEnrollmentResponse,
    StudentFeesResponse,
    StudentGradesResponse,
    StudentRegisterRequest,
    StudentRegisterResponse,
    StudentResponse,
    StudentSearchResult,
)
from services.student_service import StudentService
from utils.auth_dependency import get_current_user

router = APIRouter(prefix="/api/v1/students", tags=["Students Management"])


@router.get(
    "/",
    response_model=PaginatedResponse[StudentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_students(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    student_status: Optional[str] = Query(
        None,
        description="Filter by status (active, inactive, pending, suspended, graduated, dropped, transferred)",
    ),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    program_id: Optional[int] = Query(None, description="Filter by program ID"),
    batch_year: Optional[int] = Query(None, description="Filter by batch year"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    category: Optional[str] = Query(
        None, description="Filter by category (general, obc, sc, st, ews, other)"
    ),
    search: Optional[str] = Query(
        None, description="Search by student ID or admission number"
    ),
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    return await student_service.get_all_students(
        page=page,
        page_size=page_size,
        status=student_status,
        department_id=department_id,
        program_id=program_id,
        batch_year=batch_year,
        semester=semester,
        category=category,
        search=search,
    )


@router.post(
    "/", response_model=StudentRegisterResponse, status_code=status.HTTP_201_CREATED
)
async def create_student(
    student_data: StudentRegisterRequest,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    return await student_service.create_student(student_data)


@router.get(
    "/search",
    response_model=List[StudentSearchResult],
    status_code=status.HTTP_200_OK,
)
async def search_students(
    q: str = Query(..., min_length=1, description="Search by name, email, student ID, or admission number"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return"),
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    return await student_service.search_students(q, limit)


@router.get("/export")
async def export_students(
    format: str = Query("csv", description="Export format: csv or xlsx"),
    student_status: Optional[str] = Query(None, description="Filter by status"),
    batch_year: Optional[int] = Query(None, description="Filter by batch year"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    program_id: Optional[int] = Query(None, description="Filter by program ID"),
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can export student data",
        )
    if format not in ("csv", "xlsx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Use 'csv' or 'xlsx'",
        )
    return await student_service.export_students(
        format=format,
        student_status=student_status,
        batch_year=batch_year,
        department_id=department_id,
        program_id=program_id,
    )


@router.get("/{id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def get_student_by_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["student", "admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's details",
        )
    return await student_service.get_student_by_id(id)


@router.put("/{id}", response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def update_student(
    id: int,
    student_data: StudentRegisterRequest,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this student's details",
        )
    return await student_service.update_student(id, student_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    id: int,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this student's details",
        )
    await student_service.delete_student(id)


@router.get(
    "/{id}/profile", response_model=StudentResponse, status_code=status.HTTP_200_OK
)
async def get_student_profile(
    id: int,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["student", "admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's profile",
        )
    return await student_service.get_student_by_id(id)


@router.get(
    "/{id}/enrollments",
    response_model=StudentEnrollmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_enrollments(
    id: int,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["student", "admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's enrollments",
        )
    return await student_service.get_student_enrollments(id)


@router.get(
    "/{id}/attendance",
    response_model=StudentAttendanceResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_attendance(
    id: int,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["student", "admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's enrollments",
        )
    return await student_service.get_student_attendance(id)

@router.get(
    "/{id}/grades",
    response_model=StudentGradesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_grades(
    id: int,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["student", "admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's grades",
        )
    return await student_service.get_student_grades(id)

@router.get(
    "/{id}/fees",
    response_model=StudentFeesResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_fees(
    id: int,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["student", "admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's grades",
        )
    return await student_service.get_student_fees(id)

@router.get(
    "/{id}/documents",
    response_model=StudentDocumentsResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_documents(
    id: int,
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["student", "admin", "faculty", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this student's documents",
        )
    return await student_service.get_student_documents(id)

@router.post(
    "/{id}/upload-photo",
    response_model=PhotoUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_student_photo(
    id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    student_service: StudentService = Depends(),
):
    if (
        current_user["role"] not in ["admin", "staff"]
        and current_user["user_id"] != id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload photo for this student",
        )
    return await student_service.upload_student_photo(id, file)
