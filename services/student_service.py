import math
from typing import Optional
from fastapi import Depends
from repositories.student_repository import StudentRepository
from schemas.student_schemas import PaginatedResponse, StudentResponse


class StudentService:
    def __init__(self, student_repository: StudentRepository = Depends()):
        self.student_repository = student_repository

    async def get_all_students(
        self,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        department_id: Optional[int] = None,
        program_id: Optional[int] = None,
        batch_year: Optional[int] = None,
        semester: Optional[int] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[StudentResponse]:
        students, total = await self.student_repository.find_all_paginated(
            page=page,
            page_size=page_size,
            status=status,
            department_id=department_id,
            program_id=program_id,
            batch_year=batch_year,
            semester=semester,
            category=category,
            search=search,
        )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return PaginatedResponse(
            items=[StudentResponse.model_validate(s) for s in students],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
