import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status

from entities.exam_schedules import ExamSchedule
from entities.exam_timetables import ExamTimetable
from enums.exam_status import ExamStatus
from enums.exam_types import ExamType
from repositories.exam_repository import ExamRepository
from schemas.exam_schemas import (
    ExamScheduleCreateRequest,
    ExamScheduleResponse,
    ExamScheduleUpdateRequest,
    ExamTimetableCreateRequest,
    ExamTimetableExportItem,
    ExamTimetableExportResponse,
    ExamTimetableResponse,
    ExamTimetableUpdateRequest,
    StudentExamScheduleItem,
    StudentExamScheduleResponse,
)
from schemas.student_schemas import PaginatedResponse
from utils.safe_update import apply_update


class ExamScheduleService:
    def __init__(self, repo: ExamRepository = Depends()):
        self.repo = repo

    async def list_exam_schedules(
        self,
        page: int,
        page_size: int,
        course_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        status_filter: Optional[str] = None,
        exam_type: Optional[str] = None,
    ) -> PaginatedResponse[ExamScheduleResponse]:
        records, total = await self.repo.find_exam_schedules_paginated(
            page=page,
            page_size=page_size,
            course_id=course_id,
            academic_year=academic_year,
            semester=semester,
            status=status_filter,
            exam_type=exam_type,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[ExamScheduleResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_exam_schedule(
        self, data: ExamScheduleCreateRequest
    ) -> ExamScheduleResponse:
        course = await self.repo.find_course_by_id(data.course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        if data.start_time >= data.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before end time",
            )

        exam_schedule = ExamSchedule(
            exam_name=data.exam_name,
            exam_type=ExamType(data.exam_type),
            course_id=data.course_id,
            academic_year=data.academic_year,
            semester=data.semester,
            start_time=data.start_time,
            end_time=data.end_time,
            result_declaration_date=data.result_declaration_date,
            location=data.location,
            status=ExamStatus(data.status),
        )
        exam_schedule = await self.repo.create_exam_schedule(exam_schedule)
        return ExamScheduleResponse.model_validate(exam_schedule)

    async def get_exam_schedule(self, id: int) -> ExamScheduleResponse:
        exam_schedule = await self.repo.find_exam_schedule_by_id(id)
        if not exam_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam schedule not found",
            )
        return ExamScheduleResponse.model_validate(exam_schedule)

    async def update_exam_schedule(
        self, id: int, data: ExamScheduleUpdateRequest
    ) -> ExamScheduleResponse:
        exam_schedule = await self.repo.find_exam_schedule_by_id(id)
        if not exam_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam schedule not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "course_id" in update_data:
            course = await self.repo.find_course_by_id(update_data["course_id"])
            if not course:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Course not found",
                )

        if "exam_type" in update_data:
            update_data["exam_type"] = ExamType(update_data["exam_type"])
        if "status" in update_data:
            update_data["status"] = ExamStatus(update_data["status"])

        apply_update(exam_schedule, update_data)

        exam_schedule = await self.repo.update_exam_schedule(exam_schedule)
        return ExamScheduleResponse.model_validate(exam_schedule)

    async def delete_exam_schedule(self, id: int) -> None:
        exam_schedule = await self.repo.find_exam_schedule_by_id(id)
        if not exam_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam schedule not found",
            )
        await self.repo.delete_exam_schedule(exam_schedule)


class ExamTimetableService:
    def __init__(self, repo: ExamRepository = Depends()):
        self.repo = repo

    async def list_exam_timetables(
        self,
        page: int,
        page_size: int,
        exam_schedule_id: Optional[int] = None,
        course_offering_id: Optional[int] = None,
    ) -> PaginatedResponse[ExamTimetableResponse]:
        records, total = await self.repo.find_exam_timetables_paginated(
            page=page,
            page_size=page_size,
            exam_schedule_id=exam_schedule_id,
            course_offering_id=course_offering_id,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[ExamTimetableResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_exam_timetable(
        self, data: ExamTimetableCreateRequest
    ) -> ExamTimetableResponse:
        exam_schedule = await self.repo.find_exam_schedule_by_id(
            data.exam_schedule_id
        )
        if not exam_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam schedule not found",
            )

        offering = await self.repo.find_course_offering_by_id(
            data.course_offering_id
        )
        if not offering:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course offering not found",
            )

        if data.start_time >= data.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before end time",
            )

        timetable = ExamTimetable(
            exam_schedule_id=data.exam_schedule_id,
            course_offering_id=data.course_offering_id,
            exam_date=data.exam_date,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_minutes=data.duration_minutes,
            venue=data.venue,
            max_marks=data.max_marks,
        )
        timetable = await self.repo.create_exam_timetable(timetable)
        return ExamTimetableResponse.model_validate(timetable)

    async def update_exam_timetable(
        self, id: int, data: ExamTimetableUpdateRequest
    ) -> ExamTimetableResponse:
        timetable = await self.repo.find_exam_timetable_by_id(id)
        if not timetable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam timetable entry not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "exam_schedule_id" in update_data:
            exam_schedule = await self.repo.find_exam_schedule_by_id(
                update_data["exam_schedule_id"]
            )
            if not exam_schedule:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Exam schedule not found",
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

        apply_update(timetable, update_data)

        timetable = await self.repo.update_exam_timetable(timetable)
        return ExamTimetableResponse.model_validate(timetable)

    async def get_student_exam_schedule(
        self, student_id: int
    ) -> StudentExamScheduleResponse:
        student = await self.repo.find_student_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        rows = await self.repo.get_student_exam_timetable(student_id)
        exams = [StudentExamScheduleItem(**row) for row in rows]
        return StudentExamScheduleResponse(
            student_id=student_id,
            exams=exams,
            total=len(exams),
        )

    async def export_timetable(
        self,
        exam_schedule_id: Optional[int] = None,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> ExamTimetableExportResponse:
        rows = await self.repo.get_all_timetable_with_schedule(
            exam_schedule_id=exam_schedule_id,
            academic_year=academic_year,
            semester=semester,
        )
        records = [ExamTimetableExportItem(**row) for row in rows]
        return ExamTimetableExportResponse(
            records=records,
            total=len(records),
        )
