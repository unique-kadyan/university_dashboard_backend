from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from fastapi import Depends
from sqlalchemy import cast, func, select, String, extract
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.attendance import Attendance
from entities.book_issues import BookIssue
from entities.courses import Course
from entities.departments import Department
from entities.enrollments import Enrollment
from entities.faculty import Faculty
from entities.fee_payments import FeePayment
from entities.fee_structures import FeeStructure
from entities.hostel_rooms import HostelRoom
from entities.hostels import Hostel
from entities.library_books import LibraryBook
from entities.programs import Program
from entities.semester_results import SemesterResults
from entities.students import Student


class ReportRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_student_count(self) -> int:
        result = await self.db.execute(select(func.count(Student.id)))
        return result.scalar() or 0

    async def get_student_status_breakdown(
        self,
        department_id: Optional[int] = None,
        program_id: Optional[int] = None,
    ) -> list[dict]:
        query = select(
            cast(Student.status, String).label("status"),
            func.count(Student.id).label("count"),
        ).group_by(Student.status)

        if department_id is not None:
            query = query.where(Student.department_id == department_id)
        if program_id is not None:
            query = query.where(Student.program_id == program_id)

        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_avg_cgpa(
        self,
        department_id: Optional[int] = None,
        program_id: Optional[int] = None,
    ) -> Optional[Decimal]:
        query = select(func.avg(Student.cgpa)).where(Student.cgpa.isnot(None))

        if department_id is not None:
            query = query.where(Student.department_id == department_id)
        if program_id is not None:
            query = query.where(Student.program_id == program_id)

        result = await self.db.execute(query)
        return result.scalar()

    async def get_department_student_counts(self) -> list[dict]:
        query = (
            select(
                Department.id.label("department_id"),
                Department.name.label("department_name"),
                func.count(Student.id).label("student_count"),
            )
            .outerjoin(Student, Student.department_id == Department.id)
            .group_by(Department.id, Department.name)
            .order_by(Department.name)
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_semester_wise_gpa(
        self,
        academic_year: Optional[str] = None,
    ) -> list[dict]:
        query = (
            select(
                SemesterResults.semester,
                func.avg(SemesterResults.gpa).label("avg_gpa"),
                func.count(SemesterResults.id).label("student_count"),
            )
            .group_by(SemesterResults.semester)
            .order_by(SemesterResults.semester)
        )

        if academic_year is not None:
            query = query.where(SemesterResults.acedamic_year == academic_year)

        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_attendance_status_counts(
        self,
        department_id: Optional[int] = None,
        course_offering_id: Optional[int] = None,
    ) -> list[dict]:
        query = select(
            cast(Attendance.status, String).label("status"),
            func.count(Attendance.id).label("count"),
        ).group_by(Attendance.status)

        if department_id is not None:
            query = query.join(Student, Attendance.student_id == Student.id).where(
                Student.department_id == department_id
            )
        if course_offering_id is not None:
            query = query.where(Attendance.course_offering_id == course_offering_id)

        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_fee_collection_stats(
        self,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        department_id: Optional[int] = None,
    ) -> dict:
        base_filter = []
        if academic_year is not None:
            base_filter.append(FeeStructure.acedamic_year == academic_year)
        if semester is not None:
            base_filter.append(FeeStructure.semester == semester)
        if department_id is not None:
            base_filter.append(
                FeePayment.student_id.in_(
                    select(Student.id).where(Student.department_id == department_id)
                )
            )

        collected_query = select(
            func.coalesce(func.sum(FeePayment.amount_paid), 0)
        ).join(FeeStructure, FeePayment.fee_structure_id == FeeStructure.id)
        for f in base_filter:
            collected_query = collected_query.where(f)
        collected_query = collected_query.where(
            FeePayment.payment_status == "completed"
        )

        pending_query = select(func.coalesce(func.sum(FeePayment.amount_paid), 0)).join(
            FeeStructure, FeePayment.fee_structure_id == FeeStructure.id
        )
        for f in base_filter:
            pending_query = pending_query.where(f)
        pending_query = pending_query.where(FeePayment.payment_status == "pending")

        late_fee_query = select(func.coalesce(func.sum(FeePayment.late_fee), 0))
        discount_query = select(func.coalesce(func.sum(FeePayment.discount), 0))

        collected = (await self.db.execute(collected_query)).scalar() or Decimal(0)
        pending = (await self.db.execute(pending_query)).scalar() or Decimal(0)
        late_fees = (await self.db.execute(late_fee_query)).scalar() or Decimal(0)
        discounts = (await self.db.execute(discount_query)).scalar() or Decimal(0)

        status_query = select(
            cast(FeePayment.payment_status, String).label("status"),
            func.count(FeePayment.id).label("count"),
        ).group_by(FeePayment.payment_status)
        status_result = await self.db.execute(status_query)
        status_breakdown = {
            row["status"]: row["count"] for row in status_result.mappings().all()
        }

        mode_query = select(
            cast(FeePayment.payment_mode, String).label("mode"),
            func.coalesce(func.sum(FeePayment.amount_paid), 0).label("amount"),
        ).group_by(FeePayment.payment_mode)
        mode_result = await self.db.execute(mode_query)
        mode_breakdown = {
            row["mode"]: row["amount"] for row in mode_result.mappings().all()
        }

        return {
            "total_collected": collected,
            "total_pending": pending,
            "total_late_fees": late_fees,
            "total_discounts": discounts,
            "payment_status_breakdown": status_breakdown,
            "payment_mode_breakdown": mode_breakdown,
        }

    async def get_exam_results_stats(
        self,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> dict:
        query = select(
            cast(SemesterResults.status, String).label("status"),
            func.count(SemesterResults.id).label("count"),
        ).group_by(SemesterResults.status)

        if academic_year is not None:
            query = query.where(SemesterResults.acedamic_year == academic_year)
        if semester is not None:
            query = query.where(SemesterResults.semester == semester)

        result = await self.db.execute(query)
        status_breakdown = {
            row["status"]: row["count"] for row in result.mappings().all()
        }

        avg_query = select(func.avg(SemesterResults.gpa))
        if academic_year is not None:
            avg_query = avg_query.where(SemesterResults.acedamic_year == academic_year)
        if semester is not None:
            avg_query = avg_query.where(SemesterResults.semester == semester)
        avg_gpa = (await self.db.execute(avg_query)).scalar()

        total = sum(status_breakdown.values())

        return {
            "total_results": total,
            "avg_gpa": avg_gpa,
            "status_breakdown": status_breakdown,
        }

    async def get_library_stats(self) -> dict:
        books_query = select(
            func.count(LibraryBook.id).label("total_books"),
            func.coalesce(func.sum(LibraryBook.copies_total), 0).label("total_copies"),
            func.coalesce(func.sum(LibraryBook.copies_available), 0).label(
                "available_copies"
            ),
        )
        books = (await self.db.execute(books_query)).mappings().first()

        issued_query = select(func.count(BookIssue.id)).where(
            BookIssue.status == "issued"
        )
        issued = (await self.db.execute(issued_query)).scalar() or 0

        overdue_query = select(func.count(BookIssue.id)).where(
            BookIssue.status == "overdue"
        )
        overdue = (await self.db.execute(overdue_query)).scalar() or 0

        lost_query = select(func.count(BookIssue.id)).where(BookIssue.status == "lost")
        lost = (await self.db.execute(lost_query)).scalar() or 0

        fines_query = select(func.coalesce(func.sum(BookIssue.fine_amount), 0))
        fines = (await self.db.execute(fines_query)).scalar() or Decimal(0)

        return {
            "total_books": books["total_books"],
            "total_copies": books["total_copies"],
            "available_copies": books["available_copies"],
            "currently_issued": issued,
            "overdue_count": overdue,
            "lost_count": lost,
            "total_fines": fines,
        }

    async def get_hostel_occupancy_stats(self) -> dict:
        hostel_query = select(
            Hostel.id.label("hostel_id"),
            Hostel.name.label("hostel_name"),
            Hostel.total_capacity,
            Hostel.occupied_capacity.label("occupied"),
        ).where(Hostel.is_active == True)
        hostels = (await self.db.execute(hostel_query)).mappings().all()

        room_count = (
            await self.db.execute(
                select(func.count(HostelRoom.id)).where(HostelRoom.is_active == True)
            )
        ).scalar() or 0

        room_type_query = (
            select(
                cast(HostelRoom.room_type, String).label("room_type"),
                func.count(HostelRoom.id).label("count"),
            )
            .where(HostelRoom.is_active == True)
            .group_by(HostelRoom.room_type)
        )
        room_types = (await self.db.execute(room_type_query)).mappings().all()

        total_capacity = sum(h["total_capacity"] for h in hostels)
        total_occupied = sum(h["occupied"] for h in hostels)

        return {
            "total_hostels": len(hostels),
            "total_rooms": room_count,
            "total_capacity": total_capacity,
            "total_occupied": total_occupied,
            "hostels": hostels,
            "room_type_breakdown": {r["room_type"]: r["count"] for r in room_types},
        }

    async def get_department_wise_stats(self) -> list[dict]:
        query = (
            select(
                Department.id.label("department_id"),
                Department.name.label("department_name"),
            )
            .where(Department.is_active == True)
            .order_by(Department.name)
        )
        departments = (await self.db.execute(query)).mappings().all()

        results = []
        for dept in departments:
            dept_id = dept["department_id"]

            student_count = (
                await self.db.execute(
                    select(func.count(Student.id)).where(
                        Student.department_id == dept_id
                    )
                )
            ).scalar() or 0

            faculty_count = (
                await self.db.execute(
                    select(func.count(Faculty.id)).where(
                        Faculty.department_id == dept_id
                    )
                )
            ).scalar() or 0

            course_count = (
                await self.db.execute(
                    select(func.count(Course.id)).where(Course.department_id == dept_id)
                )
            ).scalar() or 0

            program_count = (
                await self.db.execute(
                    select(func.count(Program.id)).where(
                        Program.department_id == dept_id
                    )
                )
            ).scalar() or 0

            results.append(
                {
                    "department_id": dept_id,
                    "department_name": dept["department_name"],
                    "student_count": student_count,
                    "faculty_count": faculty_count,
                    "course_count": course_count,
                    "program_count": program_count,
                }
            )

        return results

    async def get_dashboard_counts(self) -> dict:
        students = (await self.db.execute(select(func.count(Student.id)))).scalar() or 0
        faculty = (await self.db.execute(select(func.count(Faculty.id)))).scalar() or 0
        departments = (
            await self.db.execute(
                select(func.count(Department.id)).where(Department.is_active == True)
            )
        ).scalar() or 0
        programs = (
            await self.db.execute(
                select(func.count(Program.id)).where(Program.is_active == True)
            )
        ).scalar() or 0
        courses = (
            await self.db.execute(
                select(func.count(Course.id)).where(Course.is_active == True)
            )
        ).scalar() or 0
        enrollments = (
            await self.db.execute(
                select(func.count(Enrollment.id)).where(Enrollment.status == "enrolled")
            )
        ).scalar() or 0
        fee_collected = (
            await self.db.execute(
                select(func.coalesce(func.sum(FeePayment.amount_paid), 0)).where(
                    FeePayment.payment_status == "completed"
                )
            )
        ).scalar() or Decimal(0)
        books = (
            await self.db.execute(select(func.count(LibraryBook.id)))
        ).scalar() or 0

        hostel_cap = (
            await self.db.execute(
                select(func.coalesce(func.sum(Hostel.total_capacity), 0)).where(
                    Hostel.is_active == True
                )
            )
        ).scalar() or 0
        hostel_occ = (
            await self.db.execute(
                select(func.coalesce(func.sum(Hostel.occupied_capacity), 0)).where(
                    Hostel.is_active == True
                )
            )
        ).scalar() or 0
        hostel_pct = Decimal(0)
        if hostel_cap > 0:
            hostel_pct = round(Decimal(hostel_occ) / Decimal(hostel_cap) * 100, 2)

        return {
            "total_students": students,
            "total_faculty": faculty,
            "total_departments": departments,
            "total_programs": programs,
            "total_courses": courses,
            "active_enrollments": enrollments,
            "fee_collected_total": fee_collected,
            "library_books_total": books,
            "hostel_occupancy_pct": hostel_pct,
        }

    async def get_enrollment_trends(self, months: int = 12) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)
        query = (
            select(
                func.to_char(Enrollment.enrollment_date, "YYYY-MM").label("period"),
                func.count(Enrollment.id).label("count"),
            )
            .where(Enrollment.enrollment_date >= cutoff)
            .group_by(func.to_char(Enrollment.enrollment_date, "YYYY-MM"))
            .order_by(func.to_char(Enrollment.enrollment_date, "YYYY-MM"))
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_fee_collection_trends(self, months: int = 12) -> list[dict]:
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=months * 30)
        query = (
            select(
                func.to_char(FeePayment.payment_date, "YYYY-MM").label("period"),
                func.coalesce(func.sum(FeePayment.amount_paid), 0).label("amount"),
            )
            .where(
                FeePayment.payment_date >= cutoff,
                FeePayment.payment_status == "completed",
            )
            .group_by(func.to_char(FeePayment.payment_date, "YYYY-MM"))
            .order_by(func.to_char(FeePayment.payment_date, "YYYY-MM"))
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_attendance_trends(self, months: int = 12) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=months * 30)
        query = (
            select(
                func.to_char(Attendance.date, "YYYY-MM").label("period"),
                func.count(Attendance.id).label("count"),
            )
            .where(Attendance.date >= cutoff)
            .group_by(func.to_char(Attendance.date, "YYYY-MM"))
            .order_by(func.to_char(Attendance.date, "YYYY-MM"))
        )
        result = await self.db.execute(query)
        return result.mappings().all()
