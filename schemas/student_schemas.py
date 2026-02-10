from datetime import date, datetime
from decimal import Decimal
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, EmailStr
from enums.gender import Gender
from enums.category import Category
from enums.status import Status


class StudentResponse(BaseModel):
    id: int
    user_id: int
    Student_id: str
    admisson_number: str
    admission_date: date
    program_id: int
    department_id: int
    batch_year: int
    semester: int
    section: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: Optional[str] = None
    religion: Optional[str] = None
    category: Optional[str] = None
    parent_id: Optional[int] = None
    guardian_id: Optional[int] = None
    hostel_id: Optional[int] = None
    status: str
    cgpa: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[date] = None

    class Config:
        from_attributes = True


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    
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

    class Config:
        from_attributes = True


class StudentEnrollmentResponse(BaseModel):
    student_id: int
    user_id: int
    enrollments: List[EnrollmentResponse]


class AttendanceResponse(BaseModel):
    id: int
    enrollment_id: int
    student_id: int
    date: datetime
    status: str
    marked_by: int
    remarks: Optional[str] = None
    marked_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentAttendanceResponse(BaseModel):
    student_id: int
    user_id: int
    attendance: List[AttendanceResponse]


class GradeResponse(BaseModel):
    id: int
    enrollment_id: int
    course_id: int
    assessment_id: int
    marks_obtained: Decimal
    remarks: Optional[str] = None
    graded_by: int
    graded_at: datetime

    class Config:
        from_attributes = True


class StudentGradesResponse(BaseModel):
    student_id: int
    user_id: int
    grades: List[GradeResponse]


class FeePaymentResponse(BaseModel):
    id: int
    student_id: int
    fee_structure_id: int
    amount_paid: Decimal
    payment_date: date
    payment_mode: str
    transaction_id: str
    reciept_number: str
    late_fee: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    payment_status: str
    remarks: Optional[str] = None
    processed_by: int

    class Config:
        from_attributes = True


class StudentFeesResponse(BaseModel):
    student_id: int
    user_id: int
    fees: List[FeePaymentResponse]


class DocumentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    document_type: str
    file_path: str
    file_name: str
    file_size: int
    mime_type: Optional[str] = None
    uploaded_by: int
    is_public: bool
    access_level: Optional[str] = None
    tags: Optional[list] = None
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StudentDocumentsResponse(BaseModel):
    student_id: int
    user_id: int
    documents: List[DocumentResponse]


class StudentRegisterRequest(BaseModel):
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

    Student_id: str
    admisson_number: str
    admission_date: date
    program_code: str
    department_code: str
    batch_year: int
    semester: int
    section: Optional[str] = None
    blood_group: Optional[str] = None
    nationality: Optional[str] = None
    religion: Optional[str] = None
    category: Optional[Category] = None
    status: Status = Status.ACTIVE


class StudentRegisterResponse(BaseModel):
    user_id: int
    email: str
    user_name: str
    first_name: str
    last_name: str

    id: int
    Student_id: str
    admisson_number: str
    admission_date: date
    program_id: int
    department_id: int
    batch_year: int
    semester: int
    status: str

    class Config:
        from_attributes = True
