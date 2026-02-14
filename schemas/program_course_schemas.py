from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict
from enums.course_status import CourseStatus
from enums.course_type import CourseType
from enums.degree_type import DegreeType
from enums.levels import Levels


class ProgramResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    degree_type: str
    department_id: int
    duration_years: int
    total_semesters: int
    total_credits: int
    eligibity_criteria: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProgramCreateRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    degree_type: DegreeType
    department_id: int
    duration_years: int
    total_semesters: int
    total_credits: int
    eligibity_criteria: Optional[str] = None


class ProgramUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    degree_type: Optional[DegreeType] = None
    department_id: Optional[int] = None
    duration_years: Optional[int] = None
    total_semesters: Optional[int] = None
    total_credits: Optional[int] = None
    eligibity_criteria: Optional[str] = None
    is_active: Optional[bool] = None


class ProgramCourseItem(BaseModel):
    course_id: int
    course_name: str
    course_code: str
    credits: int
    semester: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class CourseResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None
    credits: int
    department_id: int
    course_type: str
    level: str
    max_students: Optional[int] = None
    prerequisites: Optional[list[int]] = None
    syllabus: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CourseCreateRequest(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    credits: int
    department_id: int
    course_type: CourseType
    level: Levels
    max_students: Optional[int] = None
    prerequisites: Optional[list[int]] = None
    syllabus: Optional[str] = None


class CourseUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    department_id: Optional[int] = None
    course_type: Optional[CourseType] = None
    level: Optional[Levels] = None
    max_students: Optional[int] = None
    prerequisites: Optional[list[int]] = None
    syllabus: Optional[str] = None
    is_active: Optional[bool] = None


class CoursePrerequisiteResponse(BaseModel):
    id: int
    name: str
    code: str
    credits: int

    model_config = ConfigDict(from_attributes=True)


class CourseOfferingResponse(BaseModel):
    id: int
    program_id: int
    course_id: int
    faculty_id: Optional[list[int]] = None
    semester: int
    acedemic_year: str
    section: Optional[str] = None
    max_capacity: Optional[int] = None
    enrolled_students: Optional[int] = None
    room_number: Optional[str] = None
    schedule: Optional[Any] = None
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CourseOfferingCreateRequest(BaseModel):
    program_id: int
    course_id: int
    faculty_id: Optional[list[int]] = None
    semester: int
    acedemic_year: str
    section: Optional[str] = None
    max_capacity: Optional[int] = None
    room_number: Optional[str] = None
    schedule: Optional[Any] = None
    status: CourseStatus
    start_date: datetime
    end_date: datetime


class CourseOfferingUpdateRequest(BaseModel):
    faculty_id: Optional[list[int]] = None
    semester: Optional[int] = None
    section: Optional[str] = None
    max_capacity: Optional[int] = None
    room_number: Optional[str] = None
    schedule: Optional[Any] = None
    status: Optional[CourseStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
