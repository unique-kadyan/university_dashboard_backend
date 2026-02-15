from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ClassScheduleResponse(BaseModel):
    id: int
    course_offering_id: int
    slot_id: int
    room_no: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TimetableGenerateItem(BaseModel):
    course_offering_id: int
    slot_id: int
    room_no: str


class TimetableGenerateRequest(BaseModel):
    items: List[TimetableGenerateItem]


class TimetableGenerateResponse(BaseModel):
    created: List[ClassScheduleResponse]
    total: int


class TimetableUpdateRequest(BaseModel):
    course_offering_id: Optional[int] = None
    slot_id: Optional[int] = None
    room_no: Optional[str] = None
    is_active: Optional[bool] = None


class TimetableItem(BaseModel):
    course_offering_id: int
    course_name: str
    course_code: str
    slot_type: str
    day_of_week: int
    start_time: datetime
    end_time: datetime
    room_no: str


class StudentTimetableResponse(BaseModel):
    student_id: int
    schedules: List[TimetableItem]
    total: int


class FacultyTimetableResponse(BaseModel):
    faculty_id: str
    schedules: List[TimetableItem]
    total: int


class RoomTimetableResponse(BaseModel):
    room_no: str
    schedules: List[TimetableItem]
    total: int
