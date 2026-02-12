from typing import Optional, Tuple, List
from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db_config import get_db
from entities.programs import Program
from entities.courses import Course
from entities.course_offerings import ProgramCourse as CourseOffering
from entities.departments import Department


class ProgramCourseRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_program_by_id(self, program_id: int) -> Program | None:
        result = await self.db.execute(select(Program).where(Program.id == program_id))
        return result.scalar_one_or_none()

    async def find_program_by_name(self, name: str) -> Program | None:
        result = await self.db.execute(select(Program).where(Program.name == name))
        return result.scalar_one_or_none()

    async def find_program_by_code(self, code: str) -> Program | None:
        result = await self.db.execute(select(Program).where(Program.code == code))
        return result.scalar_one_or_none()

    async def create_program(self, program: Program) -> Program:
        self.db.add(program)
        await self.db.commit()
        await self.db.refresh(program)
        return program

    async def update_program(self, program: Program) -> Program:
        await self.db.commit()
        await self.db.refresh(program)
        return program

    async def delete_program(self, program: Program) -> None:
        await self.db.delete(program)
        await self.db.commit()

    async def find_programs_paginated(
        self,
        page: int,
        page_size: int,
        department_id: Optional[int] = None,
        degree_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Program], int]:
        query = select(Program)
        count_query = select(func.count()).select_from(Program)

        if department_id:
            query = query.where(Program.department_id == department_id)
            count_query = count_query.where(Program.department_id == department_id)

        if degree_type:
            query = query.where(Program.degree_type == degree_type)
            count_query = count_query.where(Program.degree_type == degree_type)

        if is_active is not None:
            query = query.where(Program.is_active == is_active)
            count_query = count_query.where(Program.is_active == is_active)

        if search:
            search_filter = Program.name.ilike(f"%{search}%") | Program.code.ilike(
                f"%{search}%"
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Program.id).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        programs = list(result.scalars().all())
        return programs, total

    async def find_program_courses(self, program_id: int) -> list:
        query = (
            select(
                Course.id.label("course_id"),
                Course.name.label("course_name"),
                Course.code.label("course_code"),
                Course.credits,
                CourseOffering.semester,
                CourseOffering.status,
            )
            .join(Course, CourseOffering.course_id == Course.id)
            .where(CourseOffering.program_id == program_id)
            .order_by(CourseOffering.semester, Course.name)
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_course_by_id(self, course_id: int) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.id == course_id))
        return result.scalar_one_or_none()

    async def find_course_by_name(self, name: str) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.name == name))
        return result.scalar_one_or_none()

    async def find_course_by_code(self, code: str) -> Course | None:
        result = await self.db.execute(select(Course).where(Course.code == code))
        return result.scalar_one_or_none()

    async def create_course(self, course: Course) -> Course:
        self.db.add(course)
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def update_course(self, course: Course) -> Course:
        await self.db.commit()
        await self.db.refresh(course)
        return course

    async def delete_course(self, course: Course) -> None:
        await self.db.delete(course)
        await self.db.commit()

    async def find_courses_paginated(
        self,
        page: int,
        page_size: int,
        department_id: Optional[int] = None,
        course_type: Optional[str] = None,
        level: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Course], int]:
        query = select(Course)
        count_query = select(func.count()).select_from(Course)

        if department_id:
            query = query.where(Course.department_id == department_id)
            count_query = count_query.where(Course.department_id == department_id)

        if course_type:
            query = query.where(Course.course_type == course_type)
            count_query = count_query.where(Course.course_type == course_type)

        if level:
            query = query.where(Course.level == level)
            count_query = count_query.where(Course.level == level)

        if is_active is not None:
            query = query.where(Course.is_active == is_active)
            count_query = count_query.where(Course.is_active == is_active)

        if search:
            search_filter = Course.name.ilike(f"%{search}%") | Course.code.ilike(
                f"%{search}%"
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Course.id).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        courses = list(result.scalars().all())
        return courses, total

    async def find_courses_by_ids(self, course_ids: list[int]) -> list:
        query = (
            select(
                Course.id,
                Course.name,
                Course.code,
                Course.credits,
            )
            .where(Course.id.in_(course_ids))
            .order_by(Course.id)
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_offering_by_id(self, offering_id: int) -> CourseOffering | None:
        result = await self.db.execute(
            select(CourseOffering).where(CourseOffering.id == offering_id)
        )
        return result.scalar_one_or_none()

    async def create_offering(self, offering: CourseOffering) -> CourseOffering:
        self.db.add(offering)
        await self.db.commit()
        await self.db.refresh(offering)
        return offering

    async def update_offering(self, offering: CourseOffering) -> CourseOffering:
        await self.db.commit()
        await self.db.refresh(offering)
        return offering

    async def delete_offering(self, offering: CourseOffering) -> None:
        await self.db.delete(offering)
        await self.db.commit()

    async def find_offerings_paginated(
        self,
        page: int,
        page_size: int,
        program_id: Optional[int] = None,
        course_id: Optional[int] = None,
        semester: Optional[int] = None,
        acedemic_year: Optional[str] = None,
        offering_status: Optional[str] = None,
    ) -> Tuple[List[CourseOffering], int]:
        query = select(CourseOffering)
        count_query = select(func.count()).select_from(CourseOffering)

        if program_id:
            query = query.where(CourseOffering.program_id == program_id)
            count_query = count_query.where(CourseOffering.program_id == program_id)

        if course_id:
            query = query.where(CourseOffering.course_id == course_id)
            count_query = count_query.where(CourseOffering.course_id == course_id)

        if semester:
            query = query.where(CourseOffering.semester == semester)
            count_query = count_query.where(CourseOffering.semester == semester)

        if acedemic_year:
            query = query.where(CourseOffering.acedemic_year == acedemic_year)
            count_query = count_query.where(
                CourseOffering.acedemic_year == acedemic_year
            )

        if offering_status:
            query = query.where(CourseOffering.status == offering_status)
            count_query = count_query.where(CourseOffering.status == offering_status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(CourseOffering.id).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        offerings = list(result.scalars().all())
        return offerings, total

    async def find_department_by_id(self, department_id: int) -> Department | None:
        result = await self.db.execute(
            select(Department).where(Department.id == department_id)
        )
        return result.scalar_one_or_none()
