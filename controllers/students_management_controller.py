from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from schemas.student_schemas import PaginatedResponse, StudentResponse
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
    student_status: Optional[str] = Query(None, description="Filter by status (active, inactive, pending, suspended, graduated, dropped, transferred)"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    program_id: Optional[int] = Query(None, description="Filter by program ID"),
    batch_year: Optional[int] = Query(None, description="Filter by batch year"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    category: Optional[str] = Query(None, description="Filter by category (general, obc, sc, st, ews, other)"),
    search: Optional[str] = Query(None, description="Search by student ID or admission number"),
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
