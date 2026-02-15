import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status

from entities.class_schedules import ClassSchedule
from repositories.timetable_repository import TimetableRepository
from schemas.student_schemas import PaginatedResponse
from utils.safe_update import apply_update
from schemas.timetable_schemas import (
    ClassScheduleResponse,
    FacultyTimetableResponse,
    RoomTimetableResponse,
    StudentTimetableResponse,
    TimetableGenerateRequest,
    TimetableGenerateResponse,
    TimetableItem,
    TimetableUpdateRequest,
)


class TimetableService:
    def __init__(self, repo: TimetableRepository = Depends()):
        self.repo = repo

    async def list_timetables(
        self,
        page: int,
        page_size: int,
        course_offering_id: Optional[int] = None,
        slot_id: Optional[int] = None,
        room_no: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse[ClassScheduleResponse]:
        records, total = await self.repo.find_class_schedules_paginated(
            page=page,
            page_size=page_size,
            course_offering_id=course_offering_id,
            slot_id=slot_id,
            room_no=room_no,
            is_active=is_active,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[ClassScheduleResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def generate_timetable(
        self, data: TimetableGenerateRequest
    ) -> TimetableGenerateResponse:
        if not data.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one timetable item is required",
            )

        for item in data.items:
            offering = await self.repo.find_course_offering_by_id(
                item.course_offering_id
            )
            if not offering:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Course offering {item.course_offering_id} not found",
                )

            slot = await self.repo.find_slot_by_id(item.slot_id)
            if not slot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Timetable slot {item.slot_id} not found",
                )

            conflict = await self.repo.find_conflict(item.slot_id, item.room_no)
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Room '{item.room_no}' is already booked for slot {item.slot_id}",
                )

        schedules = [
            ClassSchedule(
                course_offering_id=item.course_offering_id,
                slot_id=item.slot_id,
                room_no=item.room_no,
                is_active=True,
            )
            for item in data.items
        ]
        created = await self.repo.create_class_schedules_bulk(schedules)
        return TimetableGenerateResponse(
            created=[ClassScheduleResponse.model_validate(s) for s in created],
            total=len(created),
        )

    async def update_timetable(
        self, id: int, data: TimetableUpdateRequest
    ) -> ClassScheduleResponse:
        schedule = await self.repo.find_class_schedule_by_id(id)
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Class schedule not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "course_offering_id" in update_data:
            offering = await self.repo.find_course_offering_by_id(
                update_data["course_offering_id"]
            )
            if not offering:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course offering not found",
                )

        if "slot_id" in update_data:
            slot = await self.repo.find_slot_by_id(update_data["slot_id"])
            if not slot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Timetable slot not found",
                )

        new_slot_id = update_data.get("slot_id", schedule.slot_id)
        new_room_no = update_data.get("room_no", schedule.room_no)
        if new_slot_id != schedule.slot_id or new_room_no != schedule.room_no:
            conflict = await self.repo.find_conflict(new_slot_id, new_room_no)
            if conflict and conflict.id != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Room '{new_room_no}' is already booked for slot {new_slot_id}",
                )

        apply_update(schedule, update_data)

        schedule = await self.repo.update_class_schedule(schedule)
        return ClassScheduleResponse.model_validate(schedule)

    async def get_student_timetable(self, student_id: int) -> StudentTimetableResponse:
        student = await self.repo.find_student_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        rows = await self.repo.get_student_timetable(student_id)
        schedules = [TimetableItem(**row) for row in rows]
        return StudentTimetableResponse(
            student_id=student_id,
            schedules=schedules,
            total=len(schedules),
        )

    async def get_faculty_timetable(self, faculty_id: int) -> FacultyTimetableResponse:
        rows = await self.repo.get_faculty_timetable(faculty_id)
        schedules = [TimetableItem(**row) for row in rows]
        return FacultyTimetableResponse(
            faculty_id=str(faculty_id),
            schedules=schedules,
            total=len(schedules),
        )

    async def get_room_timetable(self, room_no: str) -> RoomTimetableResponse:
        rows = await self.repo.get_room_timetable(room_no)
        schedules = [TimetableItem(**row) for row in rows]
        return RoomTimetableResponse(
            room_no=room_no,
            schedules=schedules,
            total=len(schedules),
        )
