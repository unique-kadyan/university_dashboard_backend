from typing import Optional, Tuple, List
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db_config import get_db
from entities.students import Student


class StudentRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_all_paginated(
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
    ) -> Tuple[List[Student], int]:
        query = select(Student)
        count_query = select(func.count()).select_from(Student)

        # Apply filters
        if status:
            query = query.where(Student.status == status)
            count_query = count_query.where(Student.status == status)

        if department_id:
            query = query.where(Student.department_id == department_id)
            count_query = count_query.where(Student.department_id == department_id)

        if program_id:
            query = query.where(Student.program_id == program_id)
            count_query = count_query.where(Student.program_id == program_id)

        if batch_year:
            query = query.where(Student.batch_year == batch_year)
            count_query = count_query.where(Student.batch_year == batch_year)

        if semester:
            query = query.where(Student.semester == semester)
            count_query = count_query.where(Student.semester == semester)

        if category:
            query = query.where(Student.category == category)
            count_query = count_query.where(Student.category == category)

        if search:
            search_filter = (
                Student.Student_id.ilike(f"%{search}%")
                | Student.admisson_number.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order_by(Student.id).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        students = list(result.scalars().all())

        return students, total
