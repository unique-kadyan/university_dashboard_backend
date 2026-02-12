from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


# ── Assessment Schemas ─────────────────────────────────────────────


class AssessmentResponse(BaseModel):
    id: int
    course_offering_id: int
    name: str
    assessment_type: str
    description: Optional[str] = None
    max_marks: Decimal
    weightage: Decimal
    date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentCreateRequest(BaseModel):
    course_offering_id: int
    name: str
    assessment_type: str
    description: Optional[str] = None
    max_marks: Decimal
    weightage: Decimal
    date: date


class AssessmentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    max_marks: Optional[Decimal] = None
    weightage: Optional[Decimal] = None
    date: Optional[date] = None


# ── Grade Schemas ──────────────────────────────────────────────────


class GradeDetailResponse(BaseModel):
    id: int
    enrollment_id: int
    course_id: int
    assessment_id: int
    marks_obtained: Decimal
    remarks: Optional[str] = None
    graded_by: str
    graded_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class GradeCreateRequest(BaseModel):
    enrollment_id: int
    course_id: int
    assessment_id: int
    marks_obtained: Decimal
    remarks: Optional[str] = None


class GradeUpdateRequest(BaseModel):
    marks_obtained: Optional[Decimal] = None
    remarks: Optional[str] = None


# ── Bulk Grade Schemas ─────────────────────────────────────────────


class BulkGradeItem(BaseModel):
    enrollment_id: int
    marks_obtained: Decimal
    remarks: Optional[str] = None


class BulkGradeRequest(BaseModel):
    assessment_id: int
    course_id: int
    items: list[BulkGradeItem]


class BulkGradeResultItem(BaseModel):
    enrollment_id: int
    success: bool
    message: str


class BulkGradeResponse(BaseModel):
    total: int
    successful: int
    failed: int
    results: list[BulkGradeResultItem]


# ── SGPA / CGPA Schemas ───────────────────────────────────────────


class CourseGradeItem(BaseModel):
    course_id: int
    course_name: str
    course_code: str
    credits: int
    weighted_percentage: float
    grade_point: float
    grade_letter: str


class SGPAResponse(BaseModel):
    student_id: int
    semester: int
    courses: list[CourseGradeItem]
    total_credits: int
    sgpa: float


class SemesterGPAItem(BaseModel):
    semester: int
    gpa: float
    credits: int


class CGPAResponse(BaseModel):
    student_id: int
    semesters: list[SemesterGPAItem]
    total_credits: int
    cgpa: float


# ── Publish Results Schemas ────────────────────────────────────────


class PublishResultsRequest(BaseModel):
    semester: int
    academic_year: str
    student_ids: Optional[list[int]] = None


class PublishResultItem(BaseModel):
    student_id: int
    success: bool
    message: str
    gpa: Optional[float] = None


class PublishResultsResponse(BaseModel):
    total: int
    published: int
    failed: int
    results: list[PublishResultItem]
