from typing import Optional, Tuple, List
from fastapi import Depends
from sqlalchemy import select, func, literal, type_coerce, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db_config import get_db
from entities.faculty import Faculty
from entities.user import User
from entities.departments import Department
from entities.course_offerings import ProgramCourse as CourseOffering
from entities.courses import Course
from entities.class_schedules import ClassSchedule
from entities.timetable_slots import TimetableSlot
from entities.students import Student


class FacultyRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def find_user_by_username(self, user_name: str) -> User | None:
        result = await self.db.execute(select(User).where(User.user_name == user_name))
        return result.scalar_one_or_none()

    async def find_faculty_by_employee_id(self, employee_id: str) -> Faculty | None:
        result = await self.db.execute(
            select(Faculty).where(Faculty.employee_id == employee_id)
        )
        return result.scalar_one_or_none()

    async def find_department_by_code(self, code: str) -> Department | None:
        result = await self.db.execute(
            select(Department).where(Department.code == code)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def create_faculty(self, faculty: Faculty) -> Faculty:
        self.db.add(faculty)
        await self.db.commit()
        await self.db.refresh(faculty)
        return faculty

    async def find_faculty_by_id(self, faculty_id: str) -> Faculty | None:
        result = await self.db.execute(select(Faculty).where(Faculty.id == faculty_id))
        return result.scalar_one_or_none()

    async def update_faculty(self, faculty: Faculty) -> Faculty:
        await self.db.commit()
        await self.db.refresh(faculty)
        return faculty

    async def delete_faculty(self, faculty: Faculty) -> None:
        await self.db.delete(faculty)
        await self.db.commit()

    async def find_user_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def delete_user(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()

    async def find_courses_by_faculty_id(self, faculty_id: str) -> list:
        query = (
            select(
                Course.id.label("course_id"),
                Course.name.label("course_name"),
                Course.code.label("course_code"),
                Course.credits,
                CourseOffering.program_id,
                CourseOffering.semester,
                CourseOffering.acedemic_year.label("academic_year"),
                CourseOffering.section,
                CourseOffering.status,
            )
            .join(Course, CourseOffering.course_id == Course.id)
            .where(
                CourseOffering.faculty_id.any(type_coerce(literal(faculty_id), Integer))
            )
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_schedule_by_faculty_id(self, faculty_id: str) -> list:
        query = (
            select(
                Course.name.label("course_name"),
                Course.code.label("course_code"),
                TimetableSlot.day_of_week,
                TimetableSlot.start_time,
                TimetableSlot.end_time,
                ClassSchedule.room_no,
                CourseOffering.section,
            )
            .join(CourseOffering, ClassSchedule.course_offering_id == CourseOffering.id)
            .join(Course, CourseOffering.course_id == Course.id)
            .join(TimetableSlot, ClassSchedule.slot_id == TimetableSlot.id)
            .where(
                CourseOffering.faculty_id.any(type_coerce(literal(faculty_id), Integer))
            )
            .where(ClassSchedule.is_active == True)
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_students_by_faculty_id(self, faculty_id: str) -> list:
        offering_subquery = (
            select(CourseOffering.program_id)
            .where(
                CourseOffering.faculty_id.any(type_coerce(literal(faculty_id), Integer))
            )
            .distinct()
            .subquery()
        )
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
            .where(Student.program_id.in_(select(offering_subquery.c.program_id)))
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def update_user_profile_picture(self, user: User, file_path: str) -> User:
        user.profile_picture = file_path
        await self.db.merge(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def find_all_paginated(
        self,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        department_id: Optional[int] = None,
        employment_type: Optional[str] = None,
        is_hod: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Faculty], int]:
        query = select(Faculty)
        count_query = select(func.count()).select_from(Faculty)

        if status:
            query = query.where(Faculty.status == status)
            count_query = count_query.where(Faculty.status == status)

        if department_id:
            query = query.where(Faculty.department_id == department_id)
            count_query = count_query.where(Faculty.department_id == department_id)

        if employment_type:
            query = query.where(Faculty.employment_type == employment_type)
            count_query = count_query.where(Faculty.employment_type == employment_type)

        if is_hod is not None:
            query = query.where(Faculty.is_hod == is_hod)
            count_query = count_query.where(Faculty.is_hod == is_hod)

        if search:
            search_filter = Faculty.employee_id.ilike(
                f"%{search}%"
            ) | Faculty.designation.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Faculty.id).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        faculty_list = list(result.scalars().all())

        return faculty_list, total
