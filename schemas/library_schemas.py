from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    publisher: Optional[str] = None
    year_of_publication: Optional[int] = None
    edition: Optional[str] = None
    category: Optional[str] = None
    department_id: Optional[int] = None
    language: Optional[str] = None
    pages: Optional[int] = None
    price: Optional[Decimal] = None
    copies_total: int
    copies_available: int
    rack_no: Optional[str] = None
    shelf_no: Optional[str] = None
    is_referenced: bool
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BookCreateRequest(BaseModel):
    title: str
    author: str
    isbn: str
    publisher: Optional[str] = None
    year_of_publication: Optional[int] = None
    edition: Optional[str] = None
    category: Optional[str] = None
    department_id: Optional[int] = None
    language: Optional[str] = None
    pages: Optional[int] = None
    price: Optional[Decimal] = None
    copies_total: int = 1
    rack_no: Optional[str] = None
    shelf_no: Optional[str] = None
    is_referenced: bool = False
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class BookUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    year_of_publication: Optional[int] = None
    edition: Optional[str] = None
    category: Optional[str] = None
    department_id: Optional[int] = None
    language: Optional[str] = None
    pages: Optional[int] = None
    price: Optional[Decimal] = None
    copies_total: Optional[int] = None
    rack_no: Optional[str] = None
    shelf_no: Optional[str] = None
    is_referenced: Optional[bool] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None


class BookSearchResult(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    category: Optional[str] = None
    copies_available: int
    rack_no: Optional[str] = None
    shelf_no: Optional[str] = None


class BookIssueResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    fine_amount: Optional[Decimal] = None
    status: str
    issued_by: int
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class BookIssueRequest(BaseModel):
    book_id: int
    user_id: int
    due_date: datetime
    remarks: Optional[str] = None


class BookReturnRequest(BaseModel):
    issue_id: int
    remarks: Optional[str] = None


class BookRenewRequest(BaseModel):
    issue_id: int
    new_due_date: datetime


class PayFineRequest(BaseModel):
    issue_id: int
    amount: Decimal


class PayFineResponse(BaseModel):
    issue_id: int
    fine_before: Decimal
    amount_paid: Decimal
    fine_remaining: Decimal
    message: str


class OverdueBookItem(BaseModel):
    issue_id: int
    book_id: int
    book_title: str
    user_id: int
    issue_date: datetime
    due_date: datetime
    days_overdue: int
    fine_amount: Optional[Decimal] = None


class OverdueBookResponse(BaseModel):
    records: list[OverdueBookItem]
    total: int
