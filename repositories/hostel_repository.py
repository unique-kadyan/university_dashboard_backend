from typing import Optional

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.hostel_allocations import HostelAllocation
from entities.hostel_rooms import HostelRoom
from entities.hostels import Hostel
from entities.students import Student
from enums.hostel_allocation_status import HostelAllocationStatus
from enums.hostel_room_status import HostelRoomStatus


class HostelRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_hostels_paginated(
        self,
        page: int,
        page_size: int,
        hostel_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[Hostel], int]:
        query = select(Hostel)
        count_query = select(func.count(Hostel.id))

        if hostel_type is not None:
            query = query.where(Hostel.hostel_type == hostel_type)
            count_query = count_query.where(Hostel.hostel_type == hostel_type)
        if is_active is not None:
            query = query.where(Hostel.is_active == is_active)
            count_query = count_query.where(Hostel.is_active == is_active)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Hostel.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_hostel_by_id(self, id: int) -> Optional[Hostel]:
        result = await self.db.execute(select(Hostel).where(Hostel.id == id))
        return result.scalars().first()

    async def find_hostel_by_name(self, name: str) -> Optional[Hostel]:
        result = await self.db.execute(select(Hostel).where(Hostel.name == name))
        return result.scalars().first()

    async def create_hostel(self, hostel: Hostel) -> Hostel:
        self.db.add(hostel)
        await self.db.commit()
        await self.db.refresh(hostel)
        return hostel

    async def update_hostel(self, hostel: Hostel) -> Hostel:
        await self.db.commit()
        await self.db.refresh(hostel)
        return hostel

    async def find_rooms_paginated(
        self,
        page: int,
        page_size: int,
        hostel_id: Optional[int] = None,
        room_type: Optional[str] = None,
        room_status: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[HostelRoom], int]:
        query = select(HostelRoom)
        count_query = select(func.count(HostelRoom.id))

        if hostel_id is not None:
            query = query.where(HostelRoom.hostel_id == hostel_id)
            count_query = count_query.where(HostelRoom.hostel_id == hostel_id)
        if room_type is not None:
            query = query.where(HostelRoom.room_type == room_type)
            count_query = count_query.where(HostelRoom.room_type == room_type)
        if room_status is not None:
            query = query.where(HostelRoom.status == room_status)
            count_query = count_query.where(HostelRoom.status == room_status)
        if is_active is not None:
            query = query.where(HostelRoom.is_active == is_active)
            count_query = count_query.where(HostelRoom.is_active == is_active)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(HostelRoom.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_room_by_id(self, id: int) -> Optional[HostelRoom]:
        result = await self.db.execute(
            select(HostelRoom).where(HostelRoom.id == id)
        )
        return result.scalars().first()

    async def create_room(self, room: HostelRoom) -> HostelRoom:
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def update_room(self, room: HostelRoom) -> HostelRoom:
        await self.db.commit()
        await self.db.refresh(room)
        return room

    async def find_rooms_by_hostel_id(self, hostel_id: int) -> list[HostelRoom]:
        result = await self.db.execute(
            select(HostelRoom)
            .where(HostelRoom.hostel_id == hostel_id)
            .order_by(HostelRoom.room_number.asc())
        )
        return result.scalars().all()

    async def find_available_rooms(
        self,
        hostel_id: Optional[int] = None,
        room_type: Optional[str] = None,
    ) -> list[HostelRoom]:
        query = select(HostelRoom).where(
            HostelRoom.is_active == True,
            HostelRoom.occupied_beds < HostelRoom.capacity,
            HostelRoom.status == HostelRoomStatus.AVAILABLE,
        )
        if hostel_id is not None:
            query = query.where(HostelRoom.hostel_id == hostel_id)
        if room_type is not None:
            query = query.where(HostelRoom.room_type == room_type)
        query = query.order_by(HostelRoom.room_number.asc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_allocations_paginated(
        self,
        page: int,
        page_size: int,
        student_id: Optional[int] = None,
        hostel_id: Optional[int] = None,
        room_id: Optional[int] = None,
        allocation_status: Optional[str] = None,
        acedamic_year: Optional[str] = None,
    ) -> tuple[list[HostelAllocation], int]:
        query = select(HostelAllocation)
        count_query = select(func.count(HostelAllocation.id))

        if student_id is not None:
            query = query.where(HostelAllocation.student_id == student_id)
            count_query = count_query.where(
                HostelAllocation.student_id == student_id
            )
        if hostel_id is not None:
            query = query.where(HostelAllocation.hostel_id == hostel_id)
            count_query = count_query.where(
                HostelAllocation.hostel_id == hostel_id
            )
        if room_id is not None:
            query = query.where(HostelAllocation.room_id == room_id)
            count_query = count_query.where(HostelAllocation.room_id == room_id)
        if allocation_status is not None:
            query = query.where(HostelAllocation.status == allocation_status)
            count_query = count_query.where(
                HostelAllocation.status == allocation_status
            )
        if acedamic_year is not None:
            query = query.where(HostelAllocation.acedamic_year == acedamic_year)
            count_query = count_query.where(
                HostelAllocation.acedamic_year == acedamic_year
            )

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = (
            query.offset(offset)
            .limit(page_size)
            .order_by(HostelAllocation.id.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_allocation_by_id(
        self, id: int
    ) -> Optional[HostelAllocation]:
        result = await self.db.execute(
            select(HostelAllocation).where(HostelAllocation.id == id)
        )
        return result.scalars().first()

    async def find_active_allocation_for_student(
        self, student_id: int
    ) -> Optional[HostelAllocation]:
        result = await self.db.execute(
            select(HostelAllocation).where(
                HostelAllocation.student_id == student_id,
                HostelAllocation.status == HostelAllocationStatus.ACTIVE,
            )
        )
        return result.scalars().first()

    async def create_allocation(
        self, allocation: HostelAllocation
    ) -> HostelAllocation:
        self.db.add(allocation)
        await self.db.commit()
        await self.db.refresh(allocation)
        return allocation

    async def update_allocation(
        self, allocation: HostelAllocation
    ) -> HostelAllocation:
        await self.db.commit()
        await self.db.refresh(allocation)
        return allocation

    async def find_allocations_by_student_id(
        self, student_id: int
    ) -> list[HostelAllocation]:
        result = await self.db.execute(
            select(HostelAllocation)
            .where(HostelAllocation.student_id == student_id)
            .order_by(HostelAllocation.allocation_date.desc())
        )
        return result.scalars().all()

    async def find_student_by_id(self, student_id: int) -> Optional[Student]:
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalars().first()
