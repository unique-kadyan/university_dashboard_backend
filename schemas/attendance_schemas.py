from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enums.attendance_status import AttendanceStatus


# ── Attendance Schemas ──────────────────────────────────────────────────────

class AttendanceResponse(BaseModel):
    id: int
    enrollment_id: int
    student_id: int
    date: datetime
    status: str
    marked_by: str
    remarks: Optional[str] = None
    marked_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AttendanceCreateRequest(BaseModel):
    enrollment_id: int
    student_id: int
    date: datetime
    status: AttendanceStatus
    remarks: Optional[str] = None


class AttendanceUpdateRequest(BaseModel):
    status: Optional[AttendanceStatus] = None
    remarks: Optional[str] = None


# ── Bulk Attendance ─────────────────────────────────────────────────────────

class BulkAttendanceItem(BaseModel):
    enrollment_id: int
    student_id: int
    status: AttendanceStatus
    remarks: Optional[str] = None


class BulkAttendanceRequest(BaseModel):
    date: datetime
    items: list[BulkAttendanceItem]


class BulkAttendanceResultItem(BaseModel):
    enrollment_id: int
    student_id: int
    success: bool
    message: str


class BulkAttendanceResponse(BaseModel):
    total: int
    successful: int
    failed: int
    results: list[BulkAttendanceResultItem]


# ── Summary ─────────────────────────────────────────────────────────────────

class AttendanceSummaryResponse(BaseModel):
    id: int
    enrollment_id: int
    total_classes: int
    attended_classes: int
    attendance_percentage: Decimal
    month: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ── Reports ─────────────────────────────────────────────────────────────────

class AttendanceReportItem(BaseModel):
    enrollment_id: int
    student_id: int
    total_classes: int
    present: int
    absent: int
    late: int
    excused: int
    attendance_percentage: float


class AttendanceReportResponse(BaseModel):
    records: list[AttendanceReportItem]
    total: int


# ── Defaulters ──────────────────────────────────────────────────────────────

class AttendanceDefaulterItem(BaseModel):
    enrollment_id: int
    student_id: int
    total_classes: int
    attended_classes: int
    attendance_percentage: float


class AttendanceDefaulterResponse(BaseModel):
    threshold: float
    defaulters: list[AttendanceDefaulterItem]
    total: int
