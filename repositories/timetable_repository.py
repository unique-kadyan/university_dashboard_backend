from typing import Optional

from fastapi import Depends
from sqlalchemy import func, select, any_
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.class_schedules import ClassSchedule
from entities.course_offerings import ProgramCourse
from entities.courses import Course
from entities.enrollments import Enrollment
from entities.students import Student
from entities.timetable_slots import TimetableSlot


class TimetableRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_class_schedules_paginated(
        self,
        page: int,
        page_size: int,
        course_offering_id: Optional[int] = None,
        slot_id: Optional[int] = None,
        room_no: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[ClassSchedule], int]:
        query = select(ClassSchedule)
        count_query = select(func.count(ClassSchedule.id))

        if course_offering_id is not None:
            query = query.where(ClassSchedule.course_offering_id == course_offering_id)
            count_query = count_query.where(
                ClassSchedule.course_offering_id == course_offering_id
            )
        if slot_id is not None:
            query = query.where(ClassSchedule.slot_id == slot_id)
            count_query = count_query.where(ClassSchedule.slot_id == slot_id)
        if room_no is not None:
            query = query.where(ClassSchedule.room_no == room_no)
            count_query = count_query.where(ClassSchedule.room_no == room_no)
        if is_active is not None:
            query = query.where(ClassSchedule.is_active == is_active)
            count_query = count_query.where(ClassSchedule.is_active == is_active)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(ClassSchedule.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_class_schedule_by_id(self, id: int) -> Optional[ClassSchedule]:
        result = await self.db.execute(
            select(ClassSchedule).where(ClassSchedule.id == id)
        )
        return result.scalars().first()

    async def create_class_schedule(self, schedule: ClassSchedule) -> ClassSchedule:
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def create_class_schedules_bulk(
        self, schedules: list[ClassSchedule]
    ) -> list[ClassSchedule]:
        self.db.add_all(schedules)
        await self.db.commit()
        for schedule in schedules:
            await self.db.refresh(schedule)
        return schedules

    async def update_class_schedule(self, schedule: ClassSchedule) -> ClassSchedule:
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def find_slot_by_id(self, slot_id: int) -> Optional[TimetableSlot]:
        result = await self.db.execute(
            select(TimetableSlot).where(TimetableSlot.id == slot_id)
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
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        return result.scalars().first()

    async def find_conflict(
        self, slot_id: int, room_no: str
    ) -> Optional[ClassSchedule]:
        result = await self.db.execute(
            select(ClassSchedule).where(
                ClassSchedule.slot_id == slot_id,
                ClassSchedule.room_no == room_no,
                ClassSchedule.is_active == True,
            )
        )
        return result.scalars().first()

    async def get_student_timetable(self, student_id: int) -> list[dict]:
        query = (
            select(
                ClassSchedule.course_offering_id,
                Course.name.label("course_name"),
                Course.code.label("course_code"),
                TimetableSlot.slot_type,
                TimetableSlot.day_of_week,
                TimetableSlot.start_time,
                TimetableSlot.end_time,
                ClassSchedule.room_no,
            )
            .join(TimetableSlot, ClassSchedule.slot_id == TimetableSlot.id)
            .join(ProgramCourse, ClassSchedule.course_offering_id == ProgramCourse.id)
            .join(Course, ProgramCourse.course_id == Course.id)
            .join(Enrollment, Enrollment.program_id == ProgramCourse.program_id)
            .where(
                Enrollment.student_id == student_id,
                ClassSchedule.is_active == True,
            )
            .order_by(TimetableSlot.day_of_week.asc(), TimetableSlot.start_time.asc())
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_faculty_timetable(self, faculty_id: int) -> list[dict]:
        query = (
            select(
                ClassSchedule.course_offering_id,
                Course.name.label("course_name"),
                Course.code.label("course_code"),
                TimetableSlot.slot_type,
                TimetableSlot.day_of_week,
                TimetableSlot.start_time,
                TimetableSlot.end_time,
                ClassSchedule.room_no,
            )
            .join(TimetableSlot, ClassSchedule.slot_id == TimetableSlot.id)
            .join(ProgramCourse, ClassSchedule.course_offering_id == ProgramCourse.id)
            .join(Course, ProgramCourse.course_id == Course.id)
            .where(
                faculty_id == any_(ProgramCourse.faculty_id),
                ClassSchedule.is_active == True,
            )
            .order_by(TimetableSlot.day_of_week.asc(), TimetableSlot.start_time.asc())
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_room_timetable(self, room_no: str) -> list[dict]:
        query = (
            select(
                ClassSchedule.course_offering_id,
                Course.name.label("course_name"),
                Course.code.label("course_code"),
                TimetableSlot.slot_type,
                TimetableSlot.day_of_week,
                TimetableSlot.start_time,
                TimetableSlot.end_time,
                ClassSchedule.room_no,
            )
            .join(TimetableSlot, ClassSchedule.slot_id == TimetableSlot.id)
            .join(ProgramCourse, ClassSchedule.course_offering_id == ProgramCourse.id)
            .join(Course, ProgramCourse.course_id == Course.id)
            .where(
                ClassSchedule.room_no == room_no,
                ClassSchedule.is_active == True,
            )
            .order_by(TimetableSlot.day_of_week.asc(), TimetableSlot.start_time.asc())
        )
        result = await self.db.execute(query)
        return result.mappings().all()
