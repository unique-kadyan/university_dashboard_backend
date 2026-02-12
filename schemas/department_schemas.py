from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    hod_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DepartmentCreateRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    hod_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None


class DepartmentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    hod_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    is_active: Optional[bool] = None


class DepartmentFacultyResponse(BaseModel):
    id: str
    employee_id: str
    user_id: int
    first_name: str
    last_name: str
    designation: str
    is_hod: bool
    status: str

    model_config = ConfigDict(from_attributes=True)


class DepartmentStudentResponse(BaseModel):
    student_id: int
    user_id: int
    student_code: str
    first_name: str
    last_name: str
    program_id: int
    semester: int
    batch_year: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class DepartmentCourseResponse(BaseModel):
    id: int
    name: str
    code: str
    credits: int
    course_type: str
    level: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
