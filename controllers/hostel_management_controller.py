from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.hostel_schemas import (
    AllocationCreateRequest,
    AllocationHistoryResponse,
    AllocationResponse,
    AllocationUpdateRequest,
    HostelCreateRequest,
    HostelResponse,
    HostelRoomCreateRequest,
    HostelRoomResponse,
    HostelRoomUpdateRequest,
    HostelUpdateRequest,
)
from schemas.student_schemas import PaginatedResponse
from services.hostel_service import (
    HostelAllocationService,
    HostelRoomService,
    HostelService,
)
from utils.auth_dependency import get_current_user

hostels_router = APIRouter(prefix="/api/v1/hostels", tags=["Hostel Management"])


@hostels_router.get(
    "",
    response_model=PaginatedResponse[HostelResponse],
    status_code=status.HTTP_200_OK,
)
async def list_hostels(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    hostel_type: Optional[str] = Query(None, description="Filter by hostel type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: dict = Depends(get_current_user),
    service: HostelService = Depends(),
):
    return await service.list_hostels(
        page=page,
        page_size=page_size,
        hostel_type=hostel_type,
        is_active=is_active,
    )


@hostels_router.post(
    "",
    response_model=HostelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_hostel(
    data: HostelCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: HostelService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can create hostels",
        )
    return await service.create_hostel(data)


@hostels_router.get(
    "/{id}",
    response_model=HostelResponse,
    status_code=status.HTTP_200_OK,
)
async def get_hostel(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: HostelService = Depends(),
):
    return await service.get_hostel(id)


@hostels_router.put(
    "/{id}",
    response_model=HostelResponse,
    status_code=status.HTTP_200_OK,
)
async def update_hostel(
    id: int,
    data: HostelUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: HostelService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update hostels",
        )
    return await service.update_hostel(id, data)


@hostels_router.get(
    "/{id}/rooms",
    response_model=list[HostelRoomResponse],
    status_code=status.HTTP_200_OK,
)
async def get_hostel_rooms(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: HostelService = Depends(),
):
    return await service.get_hostel_rooms(id)


hostel_rooms_router = APIRouter(
    prefix="/api/v1/hostel-rooms", tags=["Hostel Room Management"]
)


@hostel_rooms_router.get(
    "/available",
    response_model=list[HostelRoomResponse],
    status_code=status.HTTP_200_OK,
)
async def get_available_rooms(
    hostel_id: Optional[int] = Query(None, description="Filter by hostel"),
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    current_user: dict = Depends(get_current_user),
    service: HostelRoomService = Depends(),
):
    return await service.get_available_rooms(hostel_id=hostel_id, room_type=room_type)


@hostel_rooms_router.get(
    "",
    response_model=PaginatedResponse[HostelRoomResponse],
    status_code=status.HTTP_200_OK,
)
async def list_rooms(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    hostel_id: Optional[int] = Query(None, description="Filter by hostel"),
    room_type: Optional[str] = Query(None, description="Filter by room type"),
    room_status: Optional[str] = Query(None, description="Filter by status"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: dict = Depends(get_current_user),
    service: HostelRoomService = Depends(),
):
    return await service.list_rooms(
        page=page,
        page_size=page_size,
        hostel_id=hostel_id,
        room_type=room_type,
        room_status=room_status,
        is_active=is_active,
    )


@hostel_rooms_router.post(
    "",
    response_model=HostelRoomResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_room(
    data: HostelRoomCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: HostelRoomService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can add rooms",
        )
    return await service.add_room(data)


@hostel_rooms_router.get(
    "/{id}",
    response_model=HostelRoomResponse,
    status_code=status.HTTP_200_OK,
)
async def get_room(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: HostelRoomService = Depends(),
):
    return await service.get_room(id)


@hostel_rooms_router.put(
    "/{id}",
    response_model=HostelRoomResponse,
    status_code=status.HTTP_200_OK,
)
async def update_room(
    id: int,
    data: HostelRoomUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: HostelRoomService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update rooms",
        )
    return await service.update_room(id, data)


hostel_allocations_router = APIRouter(
    prefix="/api/v1/hostel-allocations", tags=["Hostel Allocation Management"]
)


@hostel_allocations_router.get(
    "/history/{student_id}",
    response_model=AllocationHistoryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_student_allocation_history(
    student_id: int,
    current_user: dict = Depends(get_current_user),
    service: HostelAllocationService = Depends(),
):
    return await service.get_student_history(student_id)


@hostel_allocations_router.get(
    "",
    response_model=PaginatedResponse[AllocationResponse],
    status_code=status.HTTP_200_OK,
)
async def list_allocations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    student_id: Optional[int] = Query(None, description="Filter by student"),
    hostel_id: Optional[int] = Query(None, description="Filter by hostel"),
    room_id: Optional[int] = Query(None, description="Filter by room"),
    allocation_status: Optional[str] = Query(None, description="Filter by status"),
    acedamic_year: Optional[str] = Query(None, description="Filter by academic year"),
    current_user: dict = Depends(get_current_user),
    service: HostelAllocationService = Depends(),
):
    return await service.list_allocations(
        page=page,
        page_size=page_size,
        student_id=student_id,
        hostel_id=hostel_id,
        room_id=room_id,
        allocation_status=allocation_status,
        acedamic_year=acedamic_year,
    )


@hostel_allocations_router.post(
    "",
    response_model=AllocationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def allocate_room(
    data: AllocationCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: HostelAllocationService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can allocate rooms",
        )
    return await service.allocate_room(data)


@hostel_allocations_router.put(
    "/{id}",
    response_model=AllocationResponse,
    status_code=status.HTTP_200_OK,
)
async def update_allocation(
    id: int,
    data: AllocationUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: HostelAllocationService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update allocations",
        )
    return await service.update_allocation(id, data)


@hostel_allocations_router.delete(
    "/{id}",
    response_model=AllocationResponse,
    status_code=status.HTTP_200_OK,
)
async def vacate_room(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: HostelAllocationService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can vacate rooms",
        )
    return await service.vacate_room(id)
