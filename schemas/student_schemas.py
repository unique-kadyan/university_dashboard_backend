from datetime import date, datetime
from decimal import Decimal
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel


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
