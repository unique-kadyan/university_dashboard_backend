from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.admin_staff import AdminStaff
from entities.book_issues import BookIssue
from entities.library_books import LibraryBook
from entities.user import User
from enums.library_book_status import LibraryBookStatus


class LibraryRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_books_paginated(
        self,
        page: int,
        page_size: int,
        category: Optional[str] = None,
        department_id: Optional[int] = None,
        is_referenced: Optional[bool] = None,
    ) -> tuple[list[LibraryBook], int]:
        query = select(LibraryBook)
        count_query = select(func.count(LibraryBook.id))

        if category is not None:
            query = query.where(LibraryBook.category == category)
            count_query = count_query.where(LibraryBook.category == category)
        if department_id is not None:
            query = query.where(LibraryBook.department_id == department_id)
            count_query = count_query.where(
                LibraryBook.department_id == department_id
            )
        if is_referenced is not None:
            query = query.where(LibraryBook.is_referenced == is_referenced)
            count_query = count_query.where(
                LibraryBook.is_referenced == is_referenced
            )

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(LibraryBook.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_book_by_id(self, id: int) -> Optional[LibraryBook]:
        result = await self.db.execute(
            select(LibraryBook).where(LibraryBook.id == id)
        )
        return result.scalars().first()

    async def find_book_by_isbn(self, isbn: str) -> Optional[LibraryBook]:
        result = await self.db.execute(
            select(LibraryBook).where(LibraryBook.isbn == isbn)
        )
        return result.scalars().first()

    async def create_book(self, book: LibraryBook) -> LibraryBook:
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def update_book(self, book: LibraryBook) -> LibraryBook:
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete_book(self, book: LibraryBook) -> None:
        await self.db.delete(book)
        await self.db.commit()

    async def search_books(self, query: str, limit: int = 20) -> list[LibraryBook]:
        search = f"%{query}%"
        stmt = (
            select(LibraryBook)
            .where(
                or_(
                    LibraryBook.title.ilike(search),
                    LibraryBook.author.ilike(search),
                    LibraryBook.isbn.ilike(search),
                    LibraryBook.category.ilike(search),
                    LibraryBook.publisher.ilike(search),
                )
            )
            .limit(limit)
            .order_by(LibraryBook.title.asc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_issue_by_id(self, id: int) -> Optional[BookIssue]:
        result = await self.db.execute(
            select(BookIssue).where(BookIssue.id == id)
        )
        return result.scalars().first()

    async def find_active_issue(
        self, book_id: int, user_id: int
    ) -> Optional[BookIssue]:
        result = await self.db.execute(
            select(BookIssue).where(
                and_(
                    BookIssue.book_id == book_id,
                    BookIssue.user_id == user_id,
                    BookIssue.status == LibraryBookStatus.ISSUED,
                )
            )
        )
        return result.scalars().first()

    async def create_issue(self, issue: BookIssue) -> BookIssue:
        self.db.add(issue)
        await self.db.commit()
        await self.db.refresh(issue)
        return issue

    async def update_issue(self, issue: BookIssue) -> BookIssue:
        await self.db.commit()
        await self.db.refresh(issue)
        return issue

    async def find_issued_books(
        self,
        user_id: Optional[int] = None,
        book_id: Optional[int] = None,
    ) -> list[BookIssue]:
        query = select(BookIssue).where(
            BookIssue.status == LibraryBookStatus.ISSUED
        )
        if user_id is not None:
            query = query.where(BookIssue.user_id == user_id)
        if book_id is not None:
            query = query.where(BookIssue.book_id == book_id)
        query = query.order_by(BookIssue.due_date.asc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def find_overdue_books(self) -> list[dict]:
        now = datetime.now(timezone.utc)
        query = (
            select(
                BookIssue.id.label("issue_id"),
                BookIssue.book_id,
                LibraryBook.title.label("book_title"),
                BookIssue.user_id,
                BookIssue.issue_date,
                BookIssue.due_date,
                BookIssue.fine_amount,
            )
            .join(LibraryBook, BookIssue.book_id == LibraryBook.id)
            .where(
                and_(
                    BookIssue.status == LibraryBookStatus.ISSUED,
                    BookIssue.due_date < now,
                )
            )
            .order_by(BookIssue.due_date.asc())
        )
        result = await self.db.execute(query)
        return result.mappings().all()

    async def find_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def find_admin_staff_by_user_id(
        self, user_id: int
    ) -> Optional[AdminStaff]:
        result = await self.db.execute(
            select(AdminStaff).where(AdminStaff.user_id == user_id)
        )
        return result.scalars().first()
