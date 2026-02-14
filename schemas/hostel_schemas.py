from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class HostelResponse(BaseModel):
    id: int
    name: str
    hostel_type: str
    address: Optional[str] = None
    total_rooms: int
    total_capacity: int
    occupied_capacity: int
    warden_id: Optional[int] = None
    aminities: Optional[list] = None
    rules: Optional[list] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HostelCreateRequest(BaseModel):
    name: str
    hostel_type: str
    address: Optional[str] = None
    total_rooms: int
    total_capacity: int
    warden_id: Optional[int] = None
    aminities: Optional[list] = None
    rules: Optional[list] = None


class HostelUpdateRequest(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    total_rooms: Optional[int] = None
    total_capacity: Optional[int] = None
    warden_id: Optional[int] = None
    aminities: Optional[list] = None
    rules: Optional[list] = None
    is_active: Optional[bool] = None


class HostelRoomResponse(BaseModel):
    id: int
    room_number: str
    room_type: str
    hostel_id: int
    floor: Optional[int] = None
    capacity: int
    occupied_beds: int
    room_fee: Decimal
    aminities: Optional[list] = None
    status: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HostelRoomCreateRequest(BaseModel):
    room_number: str
    room_type: str
    hostel_id: int
    floor: Optional[int] = None
    capacity: int
    room_fee: Decimal
    aminities: Optional[list] = None
    status: str = "available"


class HostelRoomUpdateRequest(BaseModel):
    room_type: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    room_fee: Optional[Decimal] = None
    aminities: Optional[list] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None


class AllocationResponse(BaseModel):
    id: int
    student_id: int
    hostel_id: int
    room_id: int
    allocation_date: datetime
    release_date: Optional[datetime] = None
    acedamic_year: str
    status: str
    remarks: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AllocationCreateRequest(BaseModel):
    student_id: int
    hostel_id: int
    room_id: int
    acedamic_year: str
    remarks: Optional[str] = None


class AllocationUpdateRequest(BaseModel):
    room_id: Optional[int] = None
    remarks: Optional[str] = None


class AllocationHistoryResponse(BaseModel):
    student_id: int
    allocations: list[AllocationResponse]
    total: int
