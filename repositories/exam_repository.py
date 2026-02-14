from typing import Optional

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.course_offerings import ProgramCourse
from entities.courses import Course
from entities.enrollments import Enrollment
from entities.exam_schedules import ExamSchedule
from entities.exam_timetables import ExamTimetable
from entities.students import Student


class ExamRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db


    async def find_exam_schedules_paginated(
        self,
        page: int,
        page_size: int,
        course_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        status: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> tuple[list[ExamSchedule], int]:
        query = select(ExamSchedule)
        count_query = select(func.count(ExamSchedule.id))

        if course_id is not None:
            query = query.where(ExamSchedule.course_id == course_id)
            count_query = count_query.where(ExamSchedule.course_id == course_id)
        if academic_year is not None:
            query = query.where(ExamSchedule.academic_year == academic_year)
            count_query = count_query.where(
                ExamSchedule.academic_year == academic_year
            )
        if semester is not None:
            query = query.where(ExamSchedule.semester == semester)
            count_query = count_query.where(ExamSchedule.semester == semester)
        if status is not None:
            query = query.where(ExamSchedule.status == status)
            count_query = count_query.where(ExamSchedule.status == status)
        if exam_type is not None:
            query = query.where(ExamSchedule.exam_type == exam_type)
            count_query = count_query.where(ExamSchedule.exam_type == exam_type)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(ExamSchedule.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_exam_schedule_by_id(self, id: int) -> Optional[ExamSchedule]:
        result = await self.db.execute(
            select(ExamSchedule).where(ExamSchedule.id == id)
        )
        return result.scalars().first()

    async def create_exam_schedule(
        self, exam_schedule: ExamSchedule
    ) -> ExamSchedule:
        self.db.add(exam_schedule)
        await self.db.commit()
        await self.db.refresh(exam_schedule)
        return exam_schedule

    async def update_exam_schedule(
        self, exam_schedule: ExamSchedule
    ) -> ExamSchedule:
        await self.db.commit()
        await self.db.refresh(exam_schedule)
        return exam_schedule

    async def delete_exam_schedule(self, exam_schedule: ExamSchedule) -> None:
        await self.db.delete(exam_schedule)
        await self.db.commit()


    async def find_exam_timetables_paginated(
        self,
        page: int,
        page_size: int,
        exam_schedule_id: Optional[int] = None,
        course_offering_id: Optional[int] = None,
    ) -> tuple[list[ExamTimetable], int]:
        query = select(ExamTimetable)
        count_query = select(func.count(ExamTimetable.id))

        if exam_schedule_id is not None:
            query = query.where(
                ExamTimetable.exam_schedule_id == exam_schedule_id
            )
            count_query = count_query.where(
                ExamTimetable.exam_schedule_id == exam_schedule_id
            )
        if course_offering_id is not None:
            query = query.where(
                ExamTimetable.course_offering_id == course_offering_id
            )
            count_query = count_query.where(
                ExamTimetable.course_offering_id == course_offering_id
            )

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = (
            query.offset(offset)
            .limit(page_size)
            .order_by(ExamTimetable.exam_date.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_exam_timetable_by_id(self, id: int) -> Optional[ExamTimetable]:
        result = await self.db.execute(
            select(ExamTimetable).where(ExamTimetable.id == id)
        )
        return result.scalars().first()

    async def create_exam_timetable(
        self, timetable: ExamTimetable
    ) -> ExamTimetable:
        self.db.add(timetable)
        await self.db.commit()
        await self.db.refresh(timetable)
        return timetable

    async def update_exam_timetable(
        self, timetable: ExamTimetable
    ) -> ExamTimetable:
        await self.db.commit()
        await self.db.refresh(timetable)
        return timetable


    async def find_course_by_id(self, course_id: int) -> Optional[Course]:
        result = await self.db.execute(
            select(Course).where(Course.id == course_id)
        )
        return result.scalars().first()

    async def find_course_offering_by_id(
        self, offering_id: int
    ) -> Optional[ProgramCourse]:
        result = await self.db.execute(
            select(ProgramCourse).where(ProgramCourse.id == offering_id)
        )
        return result.scalars().first()

    async def find_student_by_id(self, student_id: int) -> Optional[Student]:
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalars().first()

    async def get_student_exam_timetable(
        self, student_id: int
    ) -> list[dict]:
        """Get exam timetable entries for a student based on their program enrollments."""
        query = (
            select(
                ExamSchedule.id.label("exam_schedule_id"),
                ExamSchedule.exam_name,
                ExamSchedule.exam_type,
                ExamSchedule.course_id,
                ExamTimetable.course_offering_id,
                ExamTimetable.exam_date,
                ExamTimetable.start_time,
                ExamTimetable.end_time,
                ExamTimetable.duration_minutes,
                ExamTimetable.venue,
                ExamTimetable.max_marks,
                ExamSchedule.status,
            )
            .join(ExamSchedule, ExamTimetable.exam_schedule_id == ExamSchedule.id)
            .join(
                ProgramCourse,
                ExamTimetable.course_offering_id == ProgramCourse.id,
            )
            .join(
                Enrollment,
                Enrollment.program_id == ProgramCourse.program_id,
            )
            .where(Enrollment.student_id == student_id)
            .order_by(ExamTimetable.exam_date.asc())
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_all_timetable_with_schedule(
        self,
        exam_schedule_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> list[dict]:
        """Get combined timetable + schedule data for export."""
        query = (
            select(
                ExamSchedule.exam_name,
                ExamSchedule.exam_type,
                ExamSchedule.course_id,
                ExamTimetable.course_offering_id,
                ExamSchedule.academic_year,
                ExamSchedule.semester,
                ExamTimetable.exam_date,
                ExamTimetable.start_time,
                ExamTimetable.end_time,
                ExamTimetable.duration_minutes,
                ExamTimetable.venue,
                ExamTimetable.max_marks,
                ExamSchedule.status,
            )
            .join(ExamSchedule, ExamTimetable.exam_schedule_id == ExamSchedule.id)
        )

        if exam_schedule_id is not None:
            query = query.where(ExamTimetable.exam_schedule_id == exam_schedule_id)
        if academic_year is not None:
            query = query.where(ExamSchedule.academic_year == academic_year)
        if semester is not None:
            query = query.where(ExamSchedule.semester == semester)

        query = query.order_by(ExamTimetable.exam_date.asc())
        result = await self.db.execute(query)
        return result.mappings().all()
