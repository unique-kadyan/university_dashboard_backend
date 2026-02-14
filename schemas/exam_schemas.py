from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ExamScheduleResponse(BaseModel):
    id: int
    exam_name: str
    exam_type: str
    course_id: int
    academic_year: str
    semester: int
    start_time: datetime
    end_time: datetime
    result_declaration_date: Optional[datetime] = None
    location: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ExamScheduleCreateRequest(BaseModel):
    exam_name: str
    exam_type: str
    course_id: int
    academic_year: str
    semester: int
    start_time: datetime
    end_time: datetime
    result_declaration_date: Optional[datetime] = None
    location: Optional[str] = None
    status: str


class ExamScheduleUpdateRequest(BaseModel):
    exam_name: Optional[str] = None
    exam_type: Optional[str] = None
    course_id: Optional[int] = None
    academic_year: Optional[str] = None
    semester: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result_declaration_date: Optional[datetime] = None
    location: Optional[str] = None
    status: Optional[str] = None


class ExamTimetableResponse(BaseModel):
    id: int
    exam_schedule_id: int
    course_offering_id: int
    exam_date: datetime
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    venue: str
    max_marks: Decimal
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ExamTimetableCreateRequest(BaseModel):
    exam_schedule_id: int
    course_offering_id: int
    exam_date: datetime
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    venue: str
    max_marks: Decimal


class ExamTimetableUpdateRequest(BaseModel):
    exam_schedule_id: Optional[int] = None
    course_offering_id: Optional[int] = None
    exam_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    venue: Optional[str] = None
    max_marks: Optional[Decimal] = None


class StudentExamScheduleItem(BaseModel):
    exam_schedule_id: int
    exam_name: str
    exam_type: str
    course_id: int
    course_offering_id: int
    exam_date: datetime
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    venue: str
    max_marks: Decimal
    status: str


class StudentExamScheduleResponse(BaseModel):
    student_id: int
    exams: List[StudentExamScheduleItem]
    total: int


class ExamTimetableExportItem(BaseModel):
    exam_name: str
    exam_type: str
    course_id: int
    course_offering_id: int
    academic_year: str
    semester: int
    exam_date: datetime
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    venue: str
    max_marks: Decimal
    status: str


class ExamTimetableExportResponse(BaseModel):
    records: List[ExamTimetableExportItem]
    total: int
