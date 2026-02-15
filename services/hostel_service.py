import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from entities.hostel_allocations import HostelAllocation
from entities.hostel_rooms import HostelRoom
from entities.hostels import Hostel
from enums.hostel_allocation_status import HostelAllocationStatus
from enums.hostel_room_status import HostelRoomStatus
from repositories.hostel_repository import HostelRepository
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
from utils.safe_update import apply_update


class HostelService:
    def __init__(self, repo: HostelRepository = Depends()):
        self.repo = repo

    async def list_hostels(
        self,
        page: int,
        page_size: int,
        hostel_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse[HostelResponse]:
        records, total = await self.repo.find_hostels_paginated(
            page=page,
            page_size=page_size,
            hostel_type=hostel_type,
            is_active=is_active,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[HostelResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_hostel(self, data: HostelCreateRequest) -> HostelResponse:
        existing = await self.repo.find_hostel_by_name(data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Hostel '{data.name}' already exists",
            )

        hostel = Hostel(
            name=data.name,
            hostel_type=data.hostel_type,
            address=data.address,
            total_rooms=data.total_rooms,
            total_capacity=data.total_capacity,
            occupied_capacity=0,
            warden_id=data.warden_id,
            aminities=data.aminities,
            rules=data.rules,
            is_active=True,
        )
        hostel = await self.repo.create_hostel(hostel)
        return HostelResponse.model_validate(hostel)

    async def get_hostel(self, id: int) -> HostelResponse:
        hostel = await self.repo.find_hostel_by_id(id)
        if not hostel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hostel not found",
            )
        return HostelResponse.model_validate(hostel)

    async def update_hostel(
        self, id: int, data: HostelUpdateRequest
    ) -> HostelResponse:
        hostel = await self.repo.find_hostel_by_id(id)
        if not hostel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hostel not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        apply_update(hostel, update_data)

        hostel = await self.repo.update_hostel(hostel)
        return HostelResponse.model_validate(hostel)

    async def get_hostel_rooms(self, hostel_id: int) -> list[HostelRoomResponse]:
        hostel = await self.repo.find_hostel_by_id(hostel_id)
        if not hostel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hostel not found",
            )
        rooms = await self.repo.find_rooms_by_hostel_id(hostel_id)
        return [HostelRoomResponse.model_validate(r) for r in rooms]


class HostelRoomService:
    def __init__(self, repo: HostelRepository = Depends()):
        self.repo = repo

    async def list_rooms(
        self,
        page: int,
        page_size: int,
        hostel_id: Optional[int] = None,
        room_type: Optional[str] = None,
        room_status: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> PaginatedResponse[HostelRoomResponse]:
        records, total = await self.repo.find_rooms_paginated(
            page=page,
            page_size=page_size,
            hostel_id=hostel_id,
            room_type=room_type,
            room_status=room_status,
            is_active=is_active,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[HostelRoomResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def add_room(self, data: HostelRoomCreateRequest) -> HostelRoomResponse:
        hostel = await self.repo.find_hostel_by_id(data.hostel_id)
        if not hostel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hostel not found",
            )

        room = HostelRoom(
            room_number=data.room_number,
            room_type=data.room_type,
            hostel_id=data.hostel_id,
            floor=data.floor,
            capacity=data.capacity,
            occupied_beds=0,
            room_fee=data.room_fee,
            aminities=data.aminities,
            status=data.status,
            is_active=True,
        )
        try:
            room = await self.repo.create_room(room)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Room '{data.room_number}' already exists in this hostel",
            )
        return HostelRoomResponse.model_validate(room)

    async def get_room(self, id: int) -> HostelRoomResponse:
        room = await self.repo.find_room_by_id(id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )
        return HostelRoomResponse.model_validate(room)

    async def update_room(
        self, id: int, data: HostelRoomUpdateRequest
    ) -> HostelRoomResponse:
        room = await self.repo.find_room_by_id(id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "capacity" in update_data and update_data["capacity"] < room.occupied_beds:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reduce capacity below occupied beds ({room.occupied_beds})",
            )

        apply_update(room, update_data)

        room = await self.repo.update_room(room)
        return HostelRoomResponse.model_validate(room)

    async def get_available_rooms(
        self,
        hostel_id: Optional[int] = None,
        room_type: Optional[str] = None,
    ) -> list[HostelRoomResponse]:
        rooms = await self.repo.find_available_rooms(
            hostel_id=hostel_id, room_type=room_type
        )
        return [HostelRoomResponse.model_validate(r) for r in rooms]


class HostelAllocationService:
    def __init__(self, repo: HostelRepository = Depends()):
        self.repo = repo

    async def list_allocations(
        self,
        page: int,
        page_size: int,
        student_id: Optional[int] = None,
        hostel_id: Optional[int] = None,
        room_id: Optional[int] = None,
        allocation_status: Optional[str] = None,
        acedamic_year: Optional[str] = None,
    ) -> PaginatedResponse[AllocationResponse]:
        records, total = await self.repo.find_allocations_paginated(
            page=page,
            page_size=page_size,
            student_id=student_id,
            hostel_id=hostel_id,
            room_id=room_id,
            allocation_status=allocation_status,
            acedamic_year=acedamic_year,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[AllocationResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def allocate_room(
        self, data: AllocationCreateRequest
    ) -> AllocationResponse:
        student = await self.repo.find_student_by_id(data.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )

        existing = await self.repo.find_active_allocation_for_student(
            data.student_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student already has an active room allocation",
            )

        hostel = await self.repo.find_hostel_by_id(data.hostel_id)
        if not hostel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hostel not found",
            )

        room = await self.repo.find_room_by_id(data.room_id)
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )

        if room.hostel_id != data.hostel_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room does not belong to the specified hostel",
            )

        if room.occupied_beds >= room.capacity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Room is at full capacity",
            )

        allocation = HostelAllocation(
            student_id=data.student_id,
            hostel_id=data.hostel_id,
            room_id=data.room_id,
            acedamic_year=data.acedamic_year,
            status=HostelAllocationStatus.ACTIVE,
            remarks=data.remarks,
        )
        allocation = await self.repo.create_allocation(allocation)

        now = datetime.now(timezone.utc)
        room.occupied_beds += 1
        if room.occupied_beds >= room.capacity:
            room.status = HostelRoomStatus.OCCUPIED
        room.updated_at = now
        await self.repo.update_room(room)

        hostel.occupied_capacity += 1
        hostel.updated_at = now
        await self.repo.update_hostel(hostel)

        return AllocationResponse.model_validate(allocation)

    async def update_allocation(
        self, id: int, data: AllocationUpdateRequest
    ) -> AllocationResponse:
        allocation = await self.repo.find_allocation_by_id(id)
        if not allocation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Allocation not found",
            )

        if str(allocation.status) not in [
            HostelAllocationStatus.ACTIVE.value,
            "HostelAllocationStatus.ACTIVE",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active allocations can be updated",
            )

        now = datetime.now(timezone.utc)

        if data.room_id is not None and data.room_id != allocation.room_id:
            new_room = await self.repo.find_room_by_id(data.room_id)
            if not new_room:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="New room not found",
                )
            if new_room.occupied_beds >= new_room.capacity:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="New room is at full capacity",
                )

            allocation.status = HostelAllocationStatus.TRANSFERRED
            allocation.release_date = now
            allocation.updated_at = now
            await self.repo.update_allocation(allocation)

            old_room = await self.repo.find_room_by_id(allocation.room_id)
            if old_room:
                old_room.occupied_beds = max(0, old_room.occupied_beds - 1)
                if old_room.occupied_beds < old_room.capacity:
                    old_room.status = HostelRoomStatus.AVAILABLE
                old_room.updated_at = now
                await self.repo.update_room(old_room)

            new_allocation = HostelAllocation(
                student_id=allocation.student_id,
                hostel_id=new_room.hostel_id,
                room_id=data.room_id,
                acedamic_year=allocation.acedamic_year,
                status=HostelAllocationStatus.ACTIVE,
                remarks=data.remarks or f"Transferred from room {old_room.room_number if old_room else allocation.room_id}",
            )
            new_allocation = await self.repo.create_allocation(new_allocation)

            new_room.occupied_beds += 1
            if new_room.occupied_beds >= new_room.capacity:
                new_room.status = HostelRoomStatus.OCCUPIED
            new_room.updated_at = now
            await self.repo.update_room(new_room)

            if new_room.hostel_id != allocation.hostel_id:
                old_hostel = await self.repo.find_hostel_by_id(allocation.hostel_id)
                if old_hostel:
                    old_hostel.occupied_capacity = max(
                        0, old_hostel.occupied_capacity - 1
                    )
                    old_hostel.updated_at = now
                    await self.repo.update_hostel(old_hostel)

                new_hostel = await self.repo.find_hostel_by_id(new_room.hostel_id)
                if new_hostel:
                    new_hostel.occupied_capacity += 1
                    new_hostel.updated_at = now
                    await self.repo.update_hostel(new_hostel)

            return AllocationResponse.model_validate(new_allocation)

        if data.remarks is not None:
            allocation.remarks = data.remarks
            allocation.updated_at = now
            await self.repo.update_allocation(allocation)

        return AllocationResponse.model_validate(allocation)

    async def get_student_history(
        self, student_id: int
    ) -> AllocationHistoryResponse:
        student = await self.repo.find_student_by_id(student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found",
            )
        allocations = await self.repo.find_allocations_by_student_id(student_id)
        return AllocationHistoryResponse(
            student_id=student_id,
            allocations=[AllocationResponse.model_validate(a) for a in allocations],
            total=len(allocations),
        )

    async def vacate_room(self, id: int) -> AllocationResponse:
        allocation = await self.repo.find_allocation_by_id(id)
        if not allocation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Allocation not found",
            )

        if str(allocation.status) not in [
            HostelAllocationStatus.ACTIVE.value,
            "HostelAllocationStatus.ACTIVE",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active allocations can be vacated",
            )

        now = datetime.now(timezone.utc)

        allocation.status = HostelAllocationStatus.VACATED
        allocation.release_date = now
        allocation.updated_at = now
        await self.repo.update_allocation(allocation)

        room = await self.repo.find_room_by_id(allocation.room_id)
        if room:
            room.occupied_beds = max(0, room.occupied_beds - 1)
            if room.occupied_beds < room.capacity:
                room.status = HostelRoomStatus.AVAILABLE
            room.updated_at = now
            await self.repo.update_room(room)

        hostel = await self.repo.find_hostel_by_id(allocation.hostel_id)
        if hostel:
            hostel.occupied_capacity = max(0, hostel.occupied_capacity - 1)
            hostel.updated_at = now
            await self.repo.update_hostel(hostel)

        return AllocationResponse.model_validate(allocation)
