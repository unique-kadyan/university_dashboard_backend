from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from enums.employment_type import EmploymentType
from enums.faculty_status import Status
from enums.gender import Gender


class FacultyResponse(BaseModel):
    id: str
    user_id: int
    employee_id: str
    department_id: int
    designation: str
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    date_of_joining: Optional[datetime] = None
    employment_type: str
    experience_years: Optional[int] = None
    is_hod: bool
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FacultyUpdateRequest(BaseModel):
    designation: Optional[str] = None
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    date_of_joining: Optional[datetime] = None
    employment_type: Optional[EmploymentType] = None
    experience_years: Optional[int] = None
    department_id: Optional[int] = None
    is_hod: Optional[bool] = None
    status: Optional[Status] = None


class FacultyRegisterRequest(BaseModel):
    email: EmailStr
    user_name: str
    password: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    faculty_id: str
    employee_id: str
    department_code: str
    designation: str
    specialization: Optional[str] = None
    qualification: Optional[str] = None
    date_of_joining: Optional[datetime] = None
    employment_type: EmploymentType
    experience_years: Optional[int] = None
    is_hod: bool = False
    status: Status = Status.ACTIVE


class FacultyRegisterResponse(BaseModel):
    user_id: int
    email: str
    user_name: str
    first_name: str
    last_name: str

    id: str
    employee_id: str
    department_id: int
    designation: str
    employment_type: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class FacultyCourseResponse(BaseModel):
    course_id: int
    course_name: str
    course_code: str
    credits: int
    program_id: int
    semester: int
    academic_year: str
    section: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class FacultyScheduleResponse(BaseModel):
    course_name: str
    course_code: str
    day_of_week: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    room_no: str
    section: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FacultyStudentResponse(BaseModel):
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


class FacultyPhotoUploadResponse(BaseModel):
    faculty_id: str
    user_id: int
    profile_picture: str
