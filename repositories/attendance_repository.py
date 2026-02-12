from datetime import datetime
from typing import Optional, Tuple, List
from fastapi import Depends
from sqlalchemy import select, func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from configs.db_config import get_db
from entities.attendance import Attendance
from entities.attendance_summary import AttendanceSummary
from entities.enrollments import Enrollment
from enums.attendance_status import AttendanceStatus


class AttendanceRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_attendance_by_id(self, attendance_id: int) -> Attendance | None:
        result = await self.db.execute(
            select(Attendance).where(Attendance.id == attendance_id)
        )
        return result.scalar_one_or_none()

    async def find_existing_attendance(
        self, enrollment_id: int, date: datetime
    ) -> Attendance | None:
        result = await self.db.execute(
            select(Attendance).where(
                and_(
                    Attendance.enrollment_id == enrollment_id,
                    Attendance.date == date,
                )
            )
        )
        return result.scalar_one_or_none()

    async def find_enrollment_by_id(self, enrollment_id: int) -> Enrollment | None:
        result = await self.db.execute(
            select(Enrollment).where(Enrollment.id == enrollment_id)
        )
        return result.scalar_one_or_none()

    async def create_attendance(self, attendance: Attendance) -> Attendance:
        self.db.add(attendance)
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance

    async def update_attendance(self, attendance: Attendance) -> Attendance:
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance

    async def find_attendance_paginated(
        self,
        page: int,
        page_size: int,
        enrollment_id: Optional[int] = None,
        student_id: Optional[int] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Tuple[List[Attendance], int]:
        query = select(Attendance)
        count_query = select(func.count()).select_from(Attendance)

        if enrollment_id:
            query = query.where(Attendance.enrollment_id == enrollment_id)
            count_query = count_query.where(Attendance.enrollment_id == enrollment_id)

        if student_id:
            query = query.where(Attendance.student_id == student_id)
            count_query = count_query.where(Attendance.student_id == student_id)

        if status:
            query = query.where(Attendance.status == status)
            count_query = count_query.where(Attendance.status == status)

        if date_from:
            query = query.where(Attendance.date >= date_from)
            count_query = count_query.where(Attendance.date >= date_from)

        if date_to:
            query = query.where(Attendance.date <= date_to)
            count_query = count_query.where(Attendance.date <= date_to)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.order_by(Attendance.id.desc()).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        records = list(result.scalars().all())
        return records, total

    async def find_summaries(
        self,
        enrollment_id: Optional[int] = None,
        month: Optional[str] = None,
    ) -> List[AttendanceSummary]:
        query = select(AttendanceSummary)

        if enrollment_id:
            query = query.where(AttendanceSummary.enrollment_id == enrollment_id)

        if month:
            query = query.where(AttendanceSummary.month == month)

        query = query.order_by(AttendanceSummary.month.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_attendance_report(
        self,
        enrollment_id: Optional[int] = None,
        student_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> list:
        query = select(
            Attendance.enrollment_id,
            Attendance.student_id,
            func.count(Attendance.id).label("total_classes"),
            func.sum(
                case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)
            ).label("present"),
            func.sum(
                case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)
            ).label("absent"),
            func.sum(
                case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)
            ).label("late"),
            func.sum(
                case((Attendance.status == AttendanceStatus.EXCUSED, 1), else_=0)
            ).label("excused"),
        ).group_by(Attendance.enrollment_id, Attendance.student_id)

        if enrollment_id:
            query = query.where(Attendance.enrollment_id == enrollment_id)

        if student_id:
            query = query.where(Attendance.student_id == student_id)

        if date_from:
            query = query.where(Attendance.date >= date_from)

        if date_to:
            query = query.where(Attendance.date <= date_to)

        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_defaulters(self, threshold: float) -> list:
        subquery = (
            select(
                Attendance.enrollment_id,
                Attendance.student_id,
                func.count(Attendance.id).label("total_classes"),
                func.sum(
                    case(
                        (
                            Attendance.status.in_(
                                [AttendanceStatus.PRESENT, AttendanceStatus.LATE]
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("attended_classes"),
            )
            .group_by(Attendance.enrollment_id, Attendance.student_id)
            .subquery()
        )

        query = select(
            subquery.c.enrollment_id,
            subquery.c.student_id,
            subquery.c.total_classes,
            subquery.c.attended_classes,
        ).where(
            (subquery.c.attended_classes * 100.0 / subquery.c.total_classes) < threshold
        )

        result = await self.db.execute(query)
        return result.mappings().all()
