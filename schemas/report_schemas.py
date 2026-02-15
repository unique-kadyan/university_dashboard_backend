from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import BaseModel


class DepartmentStudentCount(BaseModel):
    department_id: int
    department_name: str
    student_count: int


class SemesterGpa(BaseModel):
    semester: int
    avg_gpa: Decimal
    student_count: int


class StudentPerformanceReport(BaseModel):
    total_students: int
    avg_cgpa: Optional[Decimal] = None
    status_breakdown: Dict[str, int]
    department_wise: List[DepartmentStudentCount]
    semester_wise_gpa: List[SemesterGpa]


class AttendanceReport(BaseModel):
    total_records: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_percentage: Optional[Decimal] = None


class FeeCollectionReport(BaseModel):
    total_collected: Decimal
    total_pending: Decimal
    total_late_fees: Decimal
    total_discounts: Decimal
    payment_status_breakdown: Dict[str, int]
    payment_mode_breakdown: Dict[str, Decimal]


class ExamResultsReport(BaseModel):
    total_results: int
    avg_gpa: Optional[Decimal] = None
    status_breakdown: Dict[str, int]
    semester_wise: List[SemesterGpa]


class LibraryStatsReport(BaseModel):
    total_books: int
    total_copies: int
    available_copies: int
    currently_issued: int
    overdue_count: int
    lost_count: int
    total_fines: Decimal


class HostelWiseOccupancy(BaseModel):
    hostel_id: int
    hostel_name: str
    total_capacity: int
    occupied: int
    occupancy_percentage: Decimal


class HostelOccupancyReport(BaseModel):
    total_hostels: int
    total_rooms: int
    total_capacity: int
    total_occupied: int
    occupancy_percentage: Decimal
    hostel_wise: List[HostelWiseOccupancy]
    room_type_breakdown: Dict[str, int]


class DepartmentStats(BaseModel):
    department_id: int
    department_name: str
    student_count: int
    faculty_count: int
    course_count: int
    program_count: int


class DepartmentWiseReport(BaseModel):
    departments: List[DepartmentStats]


class DashboardStats(BaseModel):
    total_students: int
    total_faculty: int
    total_departments: int
    total_programs: int
    total_courses: int
    active_enrollments: int
    fee_collected_total: Decimal
    library_books_total: int
    hostel_occupancy_pct: Decimal


class TrendItem(BaseModel):
    period: str
    count: int


class FeeTrendItem(BaseModel):
    period: str
    amount: Decimal


class TrendsAnalysis(BaseModel):
    enrollment_trends: List[TrendItem]
    fee_collection_trends: List[FeeTrendItem]
    attendance_trends: List[TrendItem]
