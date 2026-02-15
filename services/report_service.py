from decimal import Decimal
from typing import Optional

from fastapi import Depends

from repositories.report_repository import ReportRepository
from schemas.report_schemas import (
    AttendanceReport,
    DashboardStats,
    DepartmentStats,
    DepartmentStudentCount,
    DepartmentWiseReport,
    ExamResultsReport,
    FeeCollectionReport,
    FeeTrendItem,
    HostelOccupancyReport,
    HostelWiseOccupancy,
    LibraryStatsReport,
    SemesterGpa,
    StudentPerformanceReport,
    TrendItem,
    TrendsAnalysis,
)


class ReportService:
    def __init__(self, repo: ReportRepository = Depends()):
        self.repo = repo

    async def get_student_performance(
        self,
        department_id: Optional[int] = None,
        program_id: Optional[int] = None,
        academic_year: Optional[str] = None,
    ) -> StudentPerformanceReport:
        total = await self.repo.get_student_count()
        avg_cgpa = await self.repo.get_avg_cgpa(department_id, program_id)
        status_rows = await self.repo.get_student_status_breakdown(
            department_id, program_id
        )
        dept_rows = await self.repo.get_department_student_counts()
        sem_rows = await self.repo.get_semester_wise_gpa(academic_year)

        return StudentPerformanceReport(
            total_students=total,
            avg_cgpa=round(avg_cgpa, 3) if avg_cgpa else None,
            status_breakdown={row["status"]: row["count"] for row in status_rows},
            department_wise=[DepartmentStudentCount(**row) for row in dept_rows],
            semester_wise_gpa=[
                SemesterGpa(
                    semester=row["semester"],
                    avg_gpa=round(row["avg_gpa"], 2),
                    student_count=row["student_count"],
                )
                for row in sem_rows
            ],
        )

    async def get_attendance_report(
        self,
        department_id: Optional[int] = None,
        course_offering_id: Optional[int] = None,
    ) -> AttendanceReport:
        rows = await self.repo.get_attendance_status_counts(
            department_id, course_offering_id
        )
        counts = {row["status"]: row["count"] for row in rows}
        total = sum(counts.values())
        present = counts.get("present", 0) + counts.get("PRESENT", 0)
        absent = counts.get("absent", 0) + counts.get("ABSENT", 0)
        late = counts.get("late", 0) + counts.get("LATE", 0)
        excused = counts.get("excused", 0) + counts.get("EXCUSED", 0)

        pct = None
        if total > 0:
            pct = round(Decimal(present) / Decimal(total) * 100, 2)

        return AttendanceReport(
            total_records=total,
            present_count=present,
            absent_count=absent,
            late_count=late,
            excused_count=excused,
            attendance_percentage=pct,
        )

    async def get_fee_collection_report(
        self,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
        department_id: Optional[int] = None,
    ) -> FeeCollectionReport:
        stats = await self.repo.get_fee_collection_stats(
            academic_year, semester, department_id
        )
        return FeeCollectionReport(**stats)

    async def get_exam_results_report(
        self,
        academic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> ExamResultsReport:
        stats = await self.repo.get_exam_results_stats(academic_year, semester)
        sem_rows = await self.repo.get_semester_wise_gpa(academic_year)

        return ExamResultsReport(
            total_results=stats["total_results"],
            avg_gpa=round(stats["avg_gpa"], 2) if stats["avg_gpa"] else None,
            status_breakdown=stats["status_breakdown"],
            semester_wise=[
                SemesterGpa(
                    semester=row["semester"],
                    avg_gpa=round(row["avg_gpa"], 2),
                    student_count=row["student_count"],
                )
                for row in sem_rows
            ],
        )

    async def get_library_stats(self) -> LibraryStatsReport:
        stats = await self.repo.get_library_stats()
        return LibraryStatsReport(**stats)

    async def get_hostel_occupancy(self) -> HostelOccupancyReport:
        stats = await self.repo.get_hostel_occupancy_stats()

        total_cap = stats["total_capacity"]
        total_occ = stats["total_occupied"]
        pct = Decimal(0)
        if total_cap > 0:
            pct = round(Decimal(total_occ) / Decimal(total_cap) * 100, 2)

        return HostelOccupancyReport(
            total_hostels=stats["total_hostels"],
            total_rooms=stats["total_rooms"],
            total_capacity=total_cap,
            total_occupied=total_occ,
            occupancy_percentage=pct,
            hostel_wise=[
                HostelWiseOccupancy(
                    hostel_id=h["hostel_id"],
                    hostel_name=h["hostel_name"],
                    total_capacity=h["total_capacity"],
                    occupied=h["occupied"],
                    occupancy_percentage=(
                        round(
                            Decimal(h["occupied"]) / Decimal(h["total_capacity"]) * 100,
                            2,
                        )
                        if h["total_capacity"] > 0
                        else Decimal(0)
                    ),
                )
                for h in stats["hostels"]
            ],
            room_type_breakdown=stats["room_type_breakdown"],
        )

    async def get_department_wise_report(self) -> DepartmentWiseReport:
        rows = await self.repo.get_department_wise_stats()
        return DepartmentWiseReport(
            departments=[DepartmentStats(**row) for row in rows]
        )

    async def get_dashboard(self) -> DashboardStats:
        stats = await self.repo.get_dashboard_counts()
        return DashboardStats(**stats)

    async def get_trends(self, months: int = 12) -> TrendsAnalysis:
        enrollment = await self.repo.get_enrollment_trends(months)
        fees = await self.repo.get_fee_collection_trends(months)
        attendance = await self.repo.get_attendance_trends(months)

        return TrendsAnalysis(
            enrollment_trends=[TrendItem(**row) for row in enrollment],
            fee_collection_trends=[FeeTrendItem(**row) for row in fees],
            attendance_trends=[TrendItem(**row) for row in attendance],
        )
