from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from enums.student_status import StudentStatus


# ── Enrollment Schemas ──────────────────────────────────────────────────────

class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    program_id: int
    enrollment_date: datetime
    status: str
    grade: Optional[str] = None
    grade_point: Optional[Decimal] = None
    credits_earned: Optional[int] = None
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EnrollmentCreateRequest(BaseModel):
    student_id: int
    program_id: int
    enrollment_date: datetime
    remarks: Optional[str] = None


class EnrollmentUpdateRequest(BaseModel):
    status: Optional[StudentStatus] = None
    grade: Optional[str] = None
    grade_point: Optional[Decimal] = None
    credits_earned: Optional[int] = None
    remarks: Optional[str] = None


class BulkEnrollmentItem(BaseModel):
    student_id: int
    program_id: int
    enrollment_date: datetime
    remarks: Optional[str] = None


class BulkEnrollmentRequest(BaseModel):
    enrollments: list[BulkEnrollmentItem]


class BulkEnrollmentResultItem(BaseModel):
    student_id: int
    program_id: int
    success: bool
    message: str
    enrollment_id: Optional[int] = None


class BulkEnrollmentResponse(BaseModel):
    total: int
    successful: int
    failed: int
    results: list[BulkEnrollmentResultItem]


class EligibilityResponse(BaseModel):
    student_id: int
    program_id: int
    is_eligible: bool
    reasons: list[str]
