from typing import Optional, Tuple, List
from fastapi import Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db_config import get_db
from entities.enrollments import Enrollment
from entities.students import Student
from entities.programs import Program
from enums.student_status import StudentStatus


class EnrollmentRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_enrollment_by_id(self, enrollment_id: int) -> Enrollment | None:
        result = await self.db.execute(
            select(Enrollment).where(Enrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def find_existing_enrollment(
        self, student_id: int, program_id: int
    ) -> Enrollment | None:
        result = await self.db.execute(
            select(Enrollment).where(
                and_(
                    Enrollment.student_id == student_id,
                    Enrollment.program_id == program_id,
                    Enrollment.status == StudentStatus.ENROLLED,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_enrollment(self, enrollment: Enrollment) -> Enrollment:
        self.db.add(enrollment)
        await self.db.commit()
        await self.db.refresh(enrollment)
        return enrollment

    async def update_enrollment(self, enrollment: Enrollment) -> Enrollment:
        await self.db.commit()
        await self.db.refresh(enrollment)
        return enrollment

    async def delete_enrollment(self, enrollment: Enrollment) -> None:
        await self.db.delete(enrollment)
        await self.db.commit()

    async def find_enrollments_paginated(
        self,
        page: int,
        page_size: int,
        student_id: Optional[int] = None,
        program_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Tuple[List[Enrollment], int]:
        query = select(Enrollment)
        count_query = select(func.count()).select_from(Enrollment)

        if student_id:
            query = query.where(Enrollment.student_id == student_id)
            count_query = count_query.where(Enrollment.student_id == student_id)

        if program_id:
            query = query.where(Enrollment.program_id == program_id)
            count_query = count_query.where(Enrollment.program_id == program_id)

        if status:
            query = query.where(Enrollment.status == status)
            count_query = count_query.where(Enrollment.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Enrollment.id).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        enrollments = list(result.scalars().all())
        return enrollments, total

    async def find_student_by_id(self, student_id: int) -> Student | None:
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        return result.scalar_one_or_none()

    async def find_program_by_id(self, program_id: int) -> Program | None:
        result = await self.db.execute(select(Program).where(Program.id == program_id))
        return result.scalar_one_or_none()
