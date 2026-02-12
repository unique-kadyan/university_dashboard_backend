from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from schemas.department_schemas import (
    DepartmentCourseResponse,
    DepartmentCreateRequest,
    DepartmentFacultyResponse,
    DepartmentResponse,
    DepartmentStudentResponse,
    DepartmentUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse
from services.department_service import DepartmentService
from utils.auth_dependency import get_current_user

router = APIRouter(prefix="/api/v1/departments", tags=["Department Management"])


@router.get(
    "/",
    response_model=PaginatedResponse[DepartmentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_departments(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends(),
):
    return await department_service.get_all_departments(
        page=page,
        page_size=page_size,
        is_active=is_active,
        search=search,
    )


@router.post(
    "/",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_department(
    department_data: DepartmentCreateRequest,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create departments",
        )
    return await department_service.create_department(department_data)


@router.get(
    "/{id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_department_by_id(
    id: int,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends(),
):
    return await department_service.get_department_by_id(id)


@router.put(
    "/{id}",
    response_model=DepartmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_department(
    id: int,
    department_data: DepartmentUpdateRequest,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update departments",
        )
    return await department_service.update_department(id, department_data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    id: int,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete departments",
        )
    await department_service.delete_department(id)


@router.get(
    "/{id}/faculty",
    response_model=list[DepartmentFacultyResponse],
    status_code=status.HTTP_200_OK,
)
async def get_department_faculty(
    id: int,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends(),
):
    return await department_service.get_department_faculty(id)


@router.get(
    "/{id}/students",
    response_model=list[DepartmentStudentResponse],
    status_code=status.HTTP_200_OK,
)
async def get_department_students(
    id: int,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends(),
):
    return await department_service.get_department_students(id)


@router.get(
    "/{id}/courses",
    response_model=list[DepartmentCourseResponse],
    status_code=status.HTTP_200_OK,
)
async def get_department_courses(
    id: int,
    current_user: dict = Depends(get_current_user),
    department_service: DepartmentService = Depends(),
):
    return await department_service.get_department_courses(id)
