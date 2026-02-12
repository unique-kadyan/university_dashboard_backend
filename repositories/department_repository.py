from typing import Optional, Tuple, List
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db_config import get_db
from entities.departments import Department
from entities.faculty import Faculty
from entities.students import Student
from entities.courses import Course
from entities.user import User


class DepartmentRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_department_by_id(self, department_id: int) -> Department | None:
        result = await self.db.execute(
            select(Department).where(Department.id == department_id)
        )
        return result.scalar_one_or_none()

    async def find_department_by_code(self, code: str) -> Department | None:
        result = await self.db.execute(
            select(Department).where(Department.code == code)
        )
        return result.scalar_one_or_none()

    async def find_department_by_name(self, name: str) -> Department | None:
        result = await self.db.execute(
            select(Department).where(Department.name == name)
        )
        return result.scalar_one_or_none()

    async def create_department(self, department: Department) -> Department:
        self.db.add(department)
        await self.db.commit()
        await self.db.refresh(department)
        return department

    async def update_department(self, department: Department) -> Department:
        await self.db.commit()
        await self.db.refresh(department)
        return department

    async def delete_department(self, department: Department) -> None:
        await self.db.delete(department)
        await self.db.commit()

    async def find_all_paginated(
        self,
        page: int,
        page_size: int,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Department], int]:
        query = select(Department)
        count_query = select(func.count()).select_from(Department)

        if is_active is not None:
            query = query.where(Department.is_active == is_active)
            count_query = count_query.where(Department.is_active == is_active)

        if search:
            search_filter = Department.name.ilike(
                f"%{search}%"
            ) | Department.code.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Department.id).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        departments = list(result.scalars().all())

        return departments, total

    async def find_faculty_by_department_id(self, department_id: int) -> list:
        query = (
            select(
                Faculty.id,
                Faculty.employee_id,
                Faculty.user_id,
                User.first_name,
                User.last_name,
                Faculty.designation,
                Faculty.is_hod,
                Faculty.status,
            )
            .join(User, Faculty.user_id == User.id)
            .where(Faculty.department_id == department_id)
            .order_by(Faculty.id)
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_students_by_department_id(self, department_id: int) -> list:
        query = (
            select(
                Student.id.label("student_id"),
                Student.user_id,
                Student.Student_id.label("student_code"),
                User.first_name,
                User.last_name,
                Student.program_id,
                Student.semester,
                Student.batch_year,
                Student.status,
            )
            .join(User, Student.user_id == User.id)
            .where(Student.department_id == department_id)
            .order_by(Student.id)
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_courses_by_department_id(self, department_id: int) -> list:
        query = (
            select(
                Course.id,
                Course.name,
                Course.code,
                Course.credits,
                Course.course_type,
                Course.level,
                Course.is_active,
            )
            .where(Course.department_id == department_id)
            .order_by(Course.id)
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_faculty_by_id(self, faculty_id: str) -> Faculty | None:
        result = await self.db.execute(select(Faculty).where(Faculty.id == faculty_id))
        return result.scalar_one_or_none()
