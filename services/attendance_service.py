import math
from datetime import datetime, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from entities.attendance import Attendance
from repositories.attendance_repository import AttendanceRepository
from schemas.attendance_schemas import (
    AttendanceCreateRequest,
    AttendanceDefaulterItem,
    AttendanceDefaulterResponse,
    AttendanceReportItem,
    AttendanceReportResponse,
    AttendanceResponse,
    AttendanceSummaryResponse,
    AttendanceUpdateRequest,
    BulkAttendanceRequest,
    BulkAttendanceResponse,
    BulkAttendanceResultItem,
)
from schemas.student_schemas import PaginatedResponse


class AttendanceService:
    def __init__(self, repo: AttendanceRepository = Depends()):
        self.repo = repo

    async def mark_attendance(
        self, data: AttendanceCreateRequest, marked_by: str
    ) -> AttendanceResponse:
        enrollment = await self.repo.find_enrollment_by_id(data.enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )

        existing = await self.repo.find_existing_attendance(
            data.enrollment_id, data.date
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attendance already marked for this enrollment on this date",
            )

        attendance = Attendance(
            enrollment_id=data.enrollment_id,
            student_id=data.student_id,
            date=data.date,
            status=data.status,
            marked_by=marked_by,
            remarks=data.remarks,
            marked_at=datetime.now(timezone.utc),
        )
        attendance = await self.repo.create_attendance(attendance)
        return AttendanceResponse.model_validate(attendance)

    async def get_attendance_records(
        self,
        page: int,
        page_size: int,
        enrollment_id: Optional[int] = None,
        student_id: Optional[int] = None,
        attendance_status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> PaginatedResponse[AttendanceResponse]:
        records, total = await self.repo.find_attendance_paginated(
            page=page,
            page_size=page_size,
            enrollment_id=enrollment_id,
            student_id=student_id,
            status=attendance_status,
            date_from=date_from,
            date_to=date_to,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[AttendanceResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def update_attendance(
        self, id: int, data: AttendanceUpdateRequest
    ) -> AttendanceResponse:
        attendance = await self.repo.find_attendance_by_id(id)
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        for field, value in update_data.items():
            setattr(attendance, field, value)
        attendance.updated_at = datetime.now(timezone.utc)

        attendance = await self.repo.update_attendance(attendance)
        return AttendanceResponse.model_validate(attendance)

    async def bulk_mark_attendance(
        self, data: BulkAttendanceRequest, marked_by: str
    ) -> BulkAttendanceResponse:
        results: list[BulkAttendanceResultItem] = []
        successful = 0
        failed = 0

        for item in data.items:
            enrollment = await self.repo.find_enrollment_by_id(item.enrollment_id)
            if not enrollment:
                results.append(
                    BulkAttendanceResultItem(
                        enrollment_id=item.enrollment_id,
                        student_id=item.student_id,
                        success=False,
                        message="Enrollment not found",
                    )
                )
                failed += 1
                continue

            existing = await self.repo.find_existing_attendance(
                item.enrollment_id, data.date
            )
            if existing:
                results.append(
                    BulkAttendanceResultItem(
                        enrollment_id=item.enrollment_id,
                        student_id=item.student_id,
                        success=False,
                        message="Attendance already marked for this date",
                    )
                )
                failed += 1
                continue

            attendance = Attendance(
                enrollment_id=item.enrollment_id,
                student_id=item.student_id,
                date=data.date,
                status=item.status,
                marked_by=marked_by,
                remarks=item.remarks,
                marked_at=datetime.now(timezone.utc),
            )
            await self.repo.create_attendance(attendance)
            results.append(
                BulkAttendanceResultItem(
                    enrollment_id=item.enrollment_id,
                    student_id=item.student_id,
                    success=True,
                    message="Attendance marked successfully",
                )
            )
            successful += 1

        return BulkAttendanceResponse(
            total=len(data.items),
            successful=successful,
            failed=failed,
            results=results,
        )

    async def get_summary(
        self,
        enrollment_id: Optional[int] = None,
        month: Optional[str] = None,
    ) -> list[AttendanceSummaryResponse]:
        summaries = await self.repo.find_summaries(
            enrollment_id=enrollment_id, month=month
        )
        return [AttendanceSummaryResponse.model_validate(s) for s in summaries]

    async def get_reports(
        self,
        enrollment_id: Optional[int] = None,
        student_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> AttendanceReportResponse:
        rows = await self.repo.get_attendance_report(
            enrollment_id=enrollment_id,
            student_id=student_id,
            date_from=date_from,
            date_to=date_to,
        )
        records = []
        for row in rows:
            total = row["total_classes"]
            present = row["present"] or 0
            late = row["late"] or 0
            attended = present + late
            percentage = (attended / total * 100) if total > 0 else 0.0
            records.append(
                AttendanceReportItem(
                    enrollment_id=row["enrollment_id"],
                    student_id=row["student_id"],
                    total_classes=total,
                    present=present,
                    absent=row["absent"] or 0,
                    late=late,
                    excused=row["excused"] or 0,
                    attendance_percentage=round(percentage, 2),
                )
            )
        return AttendanceReportResponse(records=records, total=len(records))

    async def get_defaulters(
        self, threshold: float = 75.0
    ) -> AttendanceDefaulterResponse:
        rows = await self.repo.get_defaulters(threshold)
        defaulters = []
        for row in rows:
            total = row["total_classes"]
            attended = row["attended_classes"] or 0
            percentage = (attended / total * 100) if total > 0 else 0.0
            defaulters.append(
                AttendanceDefaulterItem(
                    enrollment_id=row["enrollment_id"],
                    student_id=row["student_id"],
                    total_classes=total,
                    attended_classes=attended,
                    attendance_percentage=round(percentage, 2),
                )
            )
        return AttendanceDefaulterResponse(
            threshold=threshold,
            defaulters=defaulters,
            total=len(defaulters),
        )
