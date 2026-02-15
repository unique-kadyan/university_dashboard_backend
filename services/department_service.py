import math
from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from entities.departments import Department
from repositories.department_repository import DepartmentRepository
from schemas.department_schemas import (
    DepartmentCourseResponse,
    DepartmentCreateRequest,
    DepartmentFacultyResponse,
    DepartmentResponse,
    DepartmentStudentResponse,
    DepartmentUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse
from utils.safe_update import apply_update


class DepartmentService:
    def __init__(self, department_repository: DepartmentRepository = Depends()):
        self.department_repository = department_repository

    async def get_all_departments(
        self,
        page: int,
        page_size: int,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[DepartmentResponse]:
        departments_list, total = await self.department_repository.find_all_paginated(
            page=page,
            page_size=page_size,
            is_active=is_active,
            search=search,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedResponse(
            items=[DepartmentResponse.model_validate(d) for d in departments_list],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_department(
        self, data: DepartmentCreateRequest
    ) -> DepartmentResponse:
        existing_name = await self.department_repository.find_department_by_name(
            data.name
        )
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department name already exists",
            )

        existing_code = await self.department_repository.find_department_by_code(
            data.code
        )
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department code already exists",
            )

        if data.hod_id is not None:
            faculty = await self.department_repository.find_faculty_by_id(
                data.hod_id
            )
            if not faculty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="HOD faculty not found",
                )

        department = Department(
            name=data.name,
            code=data.code,
            description=data.description,
            hod_id=data.hod_id,
            phone=data.phone,
            email=data.email,
            building=data.building,
            floor=data.floor,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        department = await self.department_repository.create_department(department)
        return DepartmentResponse.model_validate(department)

    async def get_department_by_id(self, id: int) -> DepartmentResponse:
        department = await self.department_repository.find_department_by_id(id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )
        return DepartmentResponse.model_validate(department)

    async def update_department(
        self, id: int, data: DepartmentUpdateRequest
    ) -> DepartmentResponse:
        department = await self.department_repository.find_department_by_id(id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "name" in update_data and update_data["name"] != department.name:
            existing = await self.department_repository.find_department_by_name(
                update_data["name"]
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Department name already exists",
                )

        if "hod_id" in update_data and update_data["hod_id"] is not None:
            faculty = await self.department_repository.find_faculty_by_id(
                update_data["hod_id"]
            )
            if not faculty:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="HOD faculty not found",
                )

        apply_update(department, update_data)

        department = await self.department_repository.update_department(department)
        return DepartmentResponse.model_validate(department)

    async def delete_department(self, id: int) -> None:
        department = await self.department_repository.find_department_by_id(id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

        try:
            await self.department_repository.delete_department(department)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete department with existing faculty, students, programs, or courses",
            )

    async def get_department_faculty(
        self, id: int
    ) -> list[DepartmentFacultyResponse]:
        department = await self.department_repository.find_department_by_id(id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )
        rows = await self.department_repository.find_faculty_by_department_id(id)
        return [DepartmentFacultyResponse(**row) for row in rows]

    async def get_department_students(
        self, id: int
    ) -> list[DepartmentStudentResponse]:
        department = await self.department_repository.find_department_by_id(id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )
        rows = await self.department_repository.find_students_by_department_id(id)
        return [DepartmentStudentResponse(**row) for row in rows]

    async def get_department_courses(
        self, id: int
    ) -> list[DepartmentCourseResponse]:
        department = await self.department_repository.find_department_by_id(id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )
        rows = await self.department_repository.find_courses_by_department_id(id)
        return [DepartmentCourseResponse(**row) for row in rows]
