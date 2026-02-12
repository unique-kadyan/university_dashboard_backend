import math
from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from entities.programs import Program
from entities.courses import Course
from entities.course_offerings import ProgramCourse as CourseOffering
from repositories.program_course_repository import ProgramCourseRepository
from schemas.program_course_schemas import (
    CourseCreateRequest,
    CourseOfferingCreateRequest,
    CourseOfferingResponse,
    CourseOfferingUpdateRequest,
    CoursePrerequisiteResponse,
    CourseResponse,
    CourseUpdateRequest,
    ProgramCourseItem,
    ProgramCreateRequest,
    ProgramResponse,
    ProgramUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse


class ProgramService:
    def __init__(self, repo: ProgramCourseRepository = Depends()):
        self.repo = repo

    async def get_all_programs(
        self,
        page: int,
        page_size: int,
        department_id: Optional[int] = None,
        degree_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[ProgramResponse]:
        programs, total = await self.repo.find_programs_paginated(
            page=page,
            page_size=page_size,
            department_id=department_id,
            degree_type=degree_type,
            is_active=is_active,
            search=search,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[ProgramResponse.model_validate(p) for p in programs],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_program(self, data: ProgramCreateRequest) -> ProgramResponse:
        existing_name = await self.repo.find_program_by_name(data.name)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Program name already exists",
            )

        existing_code = await self.repo.find_program_by_code(data.code)
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Program code already exists",
            )

        department = await self.repo.find_department_by_id(data.department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

        program = Program(
            name=data.name,
            code=data.code,
            description=data.description,
            degree_type=data.degree_type,
            department_id=data.department_id,
            duration_years=data.duration_years,
            total_semesters=data.total_semesters,
            total_credits=data.total_credits,
            eligibity_criteria=data.eligibity_criteria,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        program = await self.repo.create_program(program)
        return ProgramResponse.model_validate(program)

    async def get_program_by_id(self, id: int) -> ProgramResponse:
        program = await self.repo.find_program_by_id(id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found",
            )
        return ProgramResponse.model_validate(program)

    async def update_program(
        self, id: int, data: ProgramUpdateRequest
    ) -> ProgramResponse:
        program = await self.repo.find_program_by_id(id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "name" in update_data and update_data["name"] != program.name:
            existing = await self.repo.find_program_by_name(update_data["name"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Program name already exists",
                )

        if "department_id" in update_data:
            department = await self.repo.find_department_by_id(
                update_data["department_id"]
            )
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found",
                )

        for field, value in update_data.items():
            setattr(program, field, value)
        program.updated_at = datetime.now(timezone.utc)

        program = await self.repo.update_program(program)
        return ProgramResponse.model_validate(program)

    async def delete_program(self, id: int) -> None:
        program = await self.repo.find_program_by_id(id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found",
            )
        try:
            await self.repo.delete_program(program)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete program with existing enrollments or course offerings",
            )

    async def get_program_courses(self, id: int) -> list[ProgramCourseItem]:
        program = await self.repo.find_program_by_id(id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found",
            )
        rows = await self.repo.find_program_courses(id)
        return [ProgramCourseItem(**row) for row in rows]


class CourseService:
    def __init__(self, repo: ProgramCourseRepository = Depends()):
        self.repo = repo

    async def get_all_courses(
        self,
        page: int,
        page_size: int,
        department_id: Optional[int] = None,
        course_type: Optional[str] = None,
        level: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[CourseResponse]:
        courses, total = await self.repo.find_courses_paginated(
            page=page,
            page_size=page_size,
            department_id=department_id,
            course_type=course_type,
            level=level,
            is_active=is_active,
            search=search,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[CourseResponse.model_validate(c) for c in courses],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_course(self, data: CourseCreateRequest) -> CourseResponse:
        existing_name = await self.repo.find_course_by_name(data.name)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course name already exists",
            )

        existing_code = await self.repo.find_course_by_code(data.code)
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Course code already exists",
            )

        department = await self.repo.find_department_by_id(data.department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found",
            )

        if data.prerequisites:
            for prereq_id in data.prerequisites:
                prereq = await self.repo.find_course_by_id(prereq_id)
                if not prereq:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Prerequisite course with ID {prereq_id} not found",
                    )

        course = Course(
            name=data.name,
            code=data.code,
            description=data.description,
            credits=data.credits,
            department_id=data.department_id,
            course_type=data.course_type,
            level=data.level,
            max_students=data.max_students,
            prerequisites=data.prerequisites,
            syllabus=data.syllabus,
            is_active=True,
        )
        course = await self.repo.create_course(course)
        return CourseResponse.model_validate(course)

    async def get_course_by_id(self, id: int) -> CourseResponse:
        course = await self.repo.find_course_by_id(id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        return CourseResponse.model_validate(course)

    async def update_course(self, id: int, data: CourseUpdateRequest) -> CourseResponse:
        course = await self.repo.find_course_by_id(id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "name" in update_data and update_data["name"] != course.name:
            existing = await self.repo.find_course_by_name(update_data["name"])
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Course name already exists",
                )

        if "department_id" in update_data:
            department = await self.repo.find_department_by_id(
                update_data["department_id"]
            )
            if not department:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Department not found",
                )

        for field, value in update_data.items():
            setattr(course, field, value)
        course.updated_at = datetime.now(timezone.utc)

        course = await self.repo.update_course(course)
        return CourseResponse.model_validate(course)

    async def delete_course(self, id: int) -> None:
        course = await self.repo.find_course_by_id(id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        try:
            await self.repo.delete_course(course)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete course with existing offerings or grades",
            )

    async def get_course_prerequisites(
        self, id: int
    ) -> list[CoursePrerequisiteResponse]:
        course = await self.repo.find_course_by_id(id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        if not course.prerequisites:
            return []

        rows = await self.repo.find_courses_by_ids(course.prerequisites)
        return [CoursePrerequisiteResponse(**row) for row in rows]


class CourseOfferingService:
    def __init__(self, repo: ProgramCourseRepository = Depends()):
        self.repo = repo

    async def get_all_offerings(
        self,
        page: int,
        page_size: int,
        program_id: Optional[int] = None,
        course_id: Optional[int] = None,
        semester: Optional[int] = None,
        acedemic_year: Optional[str] = None,
        offering_status: Optional[str] = None,
    ) -> PaginatedResponse[CourseOfferingResponse]:
        offerings, total = await self.repo.find_offerings_paginated(
            page=page,
            page_size=page_size,
            program_id=program_id,
            course_id=course_id,
            semester=semester,
            acedemic_year=acedemic_year,
            offering_status=offering_status,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[CourseOfferingResponse.model_validate(o) for o in offerings],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_offering(
        self, data: CourseOfferingCreateRequest
    ) -> CourseOfferingResponse:
        program = await self.repo.find_program_by_id(data.program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found",
            )

        course = await self.repo.find_course_by_id(data.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        offering = CourseOffering(
            program_id=data.program_id,
            course_id=data.course_id,
            faculty_id=data.faculty_id,
            semester=data.semester,
            acedemic_year=data.acedemic_year,
            section=data.section,
            max_capacity=data.max_capacity,
            enrolled_students=0,
            room_number=data.room_number,
            schedule=data.schedule,
            status=data.status,
            start_date=data.start_date,
            end_date=data.end_date,
            created_at=datetime.now(timezone.utc),
        )
        offering = await self.repo.create_offering(offering)
        return CourseOfferingResponse.model_validate(offering)

    async def get_offering_by_id(self, id: int) -> CourseOfferingResponse:
        offering = await self.repo.find_offering_by_id(id)
        if not offering:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course offering not found",
            )
        return CourseOfferingResponse.model_validate(offering)

    async def update_offering(
        self, id: int, data: CourseOfferingUpdateRequest
    ) -> CourseOfferingResponse:
        offering = await self.repo.find_offering_by_id(id)
        if not offering:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course offering not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        for field, value in update_data.items():
            setattr(offering, field, value)
        offering.updated_at = datetime.now(timezone.utc)

        offering = await self.repo.update_offering(offering)
        return CourseOfferingResponse.model_validate(offering)

    async def delete_offering(self, id: int) -> None:
        offering = await self.repo.find_offering_by_id(id)
        if not offering:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course offering not found",
            )
        try:
            await self.repo.delete_offering(offering)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete offering with existing schedules or attendance records",
            )
