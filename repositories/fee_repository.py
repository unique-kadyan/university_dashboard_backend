from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.admin_staff import AdminStaff
from entities.fee_payments import FeePayment
from entities.fee_structures import FeeStructure
from entities.students import Student
from entities.user import User


class FeeRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_fee_structures_paginated(
        self,
        page: int,
        page_size: int,
        program_id: Optional[int] = None,
        student_id: Optional[int] = None,
        acedamic_year: Optional[str] = None,
        semester: Optional[int] = None,
    ) -> tuple[list[FeeStructure], int]:
        query = select(FeeStructure)
        count_query = select(func.count(FeeStructure.id))

        if program_id is not None:
            query = query.where(FeeStructure.program_id == program_id)
            count_query = count_query.where(FeeStructure.program_id == program_id)
        if student_id is not None:
            query = query.where(FeeStructure.student_id == student_id)
            count_query = count_query.where(FeeStructure.student_id == student_id)
        if acedamic_year is not None:
            query = query.where(FeeStructure.acedamic_year == acedamic_year)
            count_query = count_query.where(FeeStructure.acedamic_year == acedamic_year)
        if semester is not None:
            query = query.where(FeeStructure.semester == semester)
            count_query = count_query.where(FeeStructure.semester == semester)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(FeeStructure.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_fee_structure_by_id(self, id: int) -> Optional[FeeStructure]:
        result = await self.db.execute(
            select(FeeStructure).where(FeeStructure.id == id)
        )
        return result.scalars().first()

    async def create_fee_structure(self, fee_structure: FeeStructure) -> FeeStructure:
        self.db.add(fee_structure)
        await self.db.commit()
        await self.db.refresh(fee_structure)
        return fee_structure

    async def update_fee_structure(self, fee_structure: FeeStructure) -> FeeStructure:
        await self.db.commit()
        await self.db.refresh(fee_structure)
        return fee_structure

    async def find_payments_paginated(
        self,
        page: int,
        page_size: int,
        student_id: Optional[int] = None,
        fee_structure_id: Optional[int] = None,
        payment_status: Optional[str] = None,
    ) -> tuple[list[FeePayment], int]:
        query = select(FeePayment)
        count_query = select(func.count(FeePayment.id))

        if student_id is not None:
            query = query.where(FeePayment.student_id == student_id)
            count_query = count_query.where(FeePayment.student_id == student_id)
        if fee_structure_id is not None:
            query = query.where(FeePayment.fee_structure_id == fee_structure_id)
            count_query = count_query.where(
                FeePayment.fee_structure_id == fee_structure_id
            )
        if payment_status is not None:
            query = query.where(FeePayment.payment_status == payment_status)
            count_query = count_query.where(FeePayment.payment_status == payment_status)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(FeePayment.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_payment_by_id(self, id: int) -> Optional[FeePayment]:
        result = await self.db.execute(select(FeePayment).where(FeePayment.id == id))
        return result.scalars().first()

    async def create_payment(self, payment: FeePayment) -> FeePayment:
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def update_payment(self, payment: FeePayment) -> FeePayment:
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def find_student_by_id(self, student_id: int) -> Optional[Student]:
        result = await self.db.execute(select(Student).where(Student.id == student_id))
        return result.scalars().first()

    async def find_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def find_admin_staff_by_user_id(self, user_id: int) -> Optional[AdminStaff]:
        result = await self.db.execute(
            select(AdminStaff).where(AdminStaff.user_id == user_id)
        )
        return result.scalars().first()

    async def get_pending_payments(
        self,
        student_id: Optional[int] = None,
    ) -> list[dict]:
        paid_subq = (
            select(
                FeePayment.fee_structure_id,
                func.coalesce(func.sum(FeePayment.amount_paid), 0).label("total_paid"),
            )
            .where(FeePayment.payment_status == "completed")
            .group_by(FeePayment.fee_structure_id)
            .subquery()
        )

        query = (
            select(
                FeeStructure.student_id,
                FeeStructure.id.label("fee_structure_id"),
                FeeStructure.acedamic_year,
                FeeStructure.semester,
                FeeStructure.total_fee,
                func.coalesce(paid_subq.c.total_paid, 0).label("total_paid"),
                FeeStructure.due_date,
            )
            .outerjoin(paid_subq, FeeStructure.id == paid_subq.c.fee_structure_id)
            .where(FeeStructure.total_fee > func.coalesce(paid_subq.c.total_paid, 0))
        )

        if student_id is not None:
            query = query.where(FeeStructure.student_id == student_id)

        query = query.order_by(FeeStructure.due_date.asc())
        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_fee_defaulters(self) -> list[dict]:
        paid_subq = (
            select(
                FeePayment.fee_structure_id,
                func.coalesce(func.sum(FeePayment.amount_paid), 0).label("total_paid"),
            )
            .where(FeePayment.payment_status == "completed")
            .group_by(FeePayment.fee_structure_id)
            .subquery()
        )

        now = datetime.now(timezone.utc)

        query = (
            select(
                FeeStructure.student_id,
                FeeStructure.id.label("fee_structure_id"),
                FeeStructure.acedamic_year,
                FeeStructure.semester,
                FeeStructure.total_fee,
                func.coalesce(paid_subq.c.total_paid, 0).label("total_paid"),
                FeeStructure.due_date,
            )
            .outerjoin(paid_subq, FeeStructure.id == paid_subq.c.fee_structure_id)
            .where(
                and_(
                    FeeStructure.total_fee > func.coalesce(paid_subq.c.total_paid, 0),
                    FeeStructure.due_date < now,
                )
            )
            .order_by(FeeStructure.due_date.asc())
        )

        result = await self.db.execute(query)
        return result.mappings().all()

    async def get_student_name(self, student_id: int) -> str:
        result = await self.db.execute(
            select(User.first_name, User.last_name)
            .join(Student, Student.user_id == User.id)
            .where(Student.id == student_id)
        )
        row = result.first()
        if row:
            return f"{row.first_name} {row.last_name}"
        return "Unknown"

    async def find_max_receipt_number(self) -> Optional[str]:
        result = await self.db.execute(
            select(FeePayment.reciept_number).order_by(FeePayment.id.desc()).limit(1)
        )
        return result.scalars().first()
