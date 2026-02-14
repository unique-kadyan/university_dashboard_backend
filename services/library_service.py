import math
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from entities.book_issues import BookIssue
from entities.library_books import LibraryBook
from enums.library_book_status import LibraryBookStatus
from repositories.library_repository import LibraryRepository
from schemas.library_schemas import (
    BookCreateRequest,
    BookIssueRequest,
    BookIssueResponse,
    BookRenewRequest,
    BookResponse,
    BookReturnRequest,
    BookSearchResult,
    BookUpdateRequest,
    OverdueBookItem,
    OverdueBookResponse,
    PayFineRequest,
    PayFineResponse,
)
from schemas.student_schemas import PaginatedResponse

FINE_PER_DAY = Decimal("5.00")


class LibraryBookService:
    def __init__(self, repo: LibraryRepository = Depends()):
        self.repo = repo

    async def list_books(
        self,
        page: int,
        page_size: int,
        category: Optional[str] = None,
        department_id: Optional[int] = None,
        is_referenced: Optional[bool] = None,
    ) -> PaginatedResponse[BookResponse]:
        records, total = await self.repo.find_books_paginated(
            page=page,
            page_size=page_size,
            category=category,
            department_id=department_id,
            is_referenced=is_referenced,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[BookResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def add_book(self, data: BookCreateRequest) -> BookResponse:
        existing = await self.repo.find_book_by_isbn(data.isbn)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Book with ISBN '{data.isbn}' already exists",
            )

        book = LibraryBook(
            title=data.title,
            author=data.author,
            isbn=data.isbn,
            publisher=data.publisher,
            year_of_publication=data.year_of_publication,
            edition=data.edition,
            category=data.category,
            department_id=data.department_id,
            language=data.language,
            pages=data.pages,
            price=data.price,
            copies_total=data.copies_total,
            copies_available=data.copies_total,
            rack_no=data.rack_no,
            shelf_no=data.shelf_no,
            is_referenced=data.is_referenced,
            description=data.description,
            cover_image_url=data.cover_image_url,
        )
        book = await self.repo.create_book(book)
        return BookResponse.model_validate(book)

    async def get_book(self, id: int) -> BookResponse:
        book = await self.repo.find_book_by_id(id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found",
            )
        return BookResponse.model_validate(book)

    async def update_book(
        self, id: int, data: BookUpdateRequest
    ) -> BookResponse:
        book = await self.repo.find_book_by_id(id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        if "copies_total" in update_data:
            issued = book.copies_total - book.copies_available
            new_total = update_data["copies_total"]
            if new_total < issued:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot set total copies below currently issued count ({issued})",
                )
            book.copies_available = new_total - issued

        for field, value in update_data.items():
            setattr(book, field, value)
        book.updated_at = datetime.now(timezone.utc)

        book = await self.repo.update_book(book)
        return BookResponse.model_validate(book)

    async def delete_book(self, id: int) -> None:
        book = await self.repo.find_book_by_id(id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found",
            )
        if book.copies_available < book.copies_total:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete book with active issues",
            )
        try:
            await self.repo.delete_book(book)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete book with existing issue records",
            )

    async def search_books(
        self, q: str, limit: int = 20
    ) -> list[BookSearchResult]:
        books = await self.repo.search_books(q, limit)
        return [
            BookSearchResult(
                id=b.id,
                title=b.title,
                author=b.author,
                isbn=b.isbn,
                category=b.category,
                copies_available=b.copies_available,
                rack_no=b.rack_no,
                shelf_no=b.shelf_no,
            )
            for b in books
        ]


class LibraryCirculationService:
    def __init__(self, repo: LibraryRepository = Depends()):
        self.repo = repo

    async def _get_admin_staff_id(self, user_id: int) -> int:
        admin_staff = await self.repo.find_admin_staff_by_user_id(user_id)
        if not admin_staff:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admin staff can perform this operation",
            )
        return admin_staff.id

    async def issue_book(
        self, data: BookIssueRequest, issued_by_user_id: int
    ) -> BookIssueResponse:
        book = await self.repo.find_book_by_id(data.book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found",
            )

        if book.is_referenced:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reference books cannot be issued",
            )

        if book.copies_available <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No copies available for issue",
            )

        user = await self.repo.find_user_by_id(data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        existing = await self.repo.find_active_issue(data.book_id, data.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has this book issued",
            )

        staff_id = await self._get_admin_staff_id(issued_by_user_id)

        issue = BookIssue(
            book_id=data.book_id,
            user_id=data.user_id,
            issue_date=datetime.now(timezone.utc),
            due_date=data.due_date,
            status=LibraryBookStatus.ISSUED,
            issued_by=staff_id,
            remarks=data.remarks,
        )
        issue = await self.repo.create_issue(issue)

        book.copies_available -= 1
        book.updated_at = datetime.now(timezone.utc)
        await self.repo.update_book(book)

        return BookIssueResponse.model_validate(issue)

    async def return_book(
        self, data: BookReturnRequest
    ) -> BookIssueResponse:
        issue = await self.repo.find_issue_by_id(data.issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue record not found",
            )

        if str(issue.status) not in [
            LibraryBookStatus.ISSUED.value,
            "LibraryBookStatus.ISSUED",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book is not currently issued",
            )

        now = datetime.now(timezone.utc)
        issue.return_date = now
        issue.status = LibraryBookStatus.RETURNED

        if issue.due_date and now > issue.due_date:
            days_overdue = (now - issue.due_date).days
            issue.fine_amount = FINE_PER_DAY * days_overdue

        if data.remarks:
            issue.remarks = (
                f"{issue.remarks or ''} | {data.remarks}".strip(" |")
            )
        issue.updated_at = now
        await self.repo.update_issue(issue)

        book = await self.repo.find_book_by_id(issue.book_id)
        if book:
            book.copies_available += 1
            book.updated_at = now
            await self.repo.update_book(book)

        return BookIssueResponse.model_validate(issue)

    async def get_issued_books(
        self,
        user_id: Optional[int] = None,
        book_id: Optional[int] = None,
    ) -> list[BookIssueResponse]:
        issues = await self.repo.find_issued_books(
            user_id=user_id, book_id=book_id
        )
        return [BookIssueResponse.model_validate(i) for i in issues]

    async def get_overdue_books(self) -> OverdueBookResponse:
        rows = await self.repo.find_overdue_books()
        now = datetime.now(timezone.utc)
        records = []
        for row in rows:
            days_overdue = (now - row["due_date"]).days
            records.append(
                OverdueBookItem(
                    issue_id=row["issue_id"],
                    book_id=row["book_id"],
                    book_title=row["book_title"],
                    user_id=row["user_id"],
                    issue_date=row["issue_date"],
                    due_date=row["due_date"],
                    days_overdue=max(days_overdue, 0),
                    fine_amount=row["fine_amount"],
                )
            )
        return OverdueBookResponse(records=records, total=len(records))

    async def renew_book(
        self, data: BookRenewRequest
    ) -> BookIssueResponse:
        issue = await self.repo.find_issue_by_id(data.issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue record not found",
            )

        if str(issue.status) not in [
            LibraryBookStatus.ISSUED.value,
            "LibraryBookStatus.ISSUED",
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only issued books can be renewed",
            )

        if data.new_due_date <= issue.due_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New due date must be after the current due date",
            )

        issue.due_date = data.new_due_date
        issue.updated_at = datetime.now(timezone.utc)
        await self.repo.update_issue(issue)
        return BookIssueResponse.model_validate(issue)

    async def pay_fine(self, data: PayFineRequest) -> PayFineResponse:
        issue = await self.repo.find_issue_by_id(data.issue_id)
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Issue record not found",
            )

        current_fine = issue.fine_amount or Decimal("0")
        if current_fine <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No outstanding fine for this issue",
            )

        if data.amount > current_fine:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payment amount exceeds fine ({current_fine})",
            )

        remaining = current_fine - data.amount
        issue.fine_amount = remaining
        issue.updated_at = datetime.now(timezone.utc)
        await self.repo.update_issue(issue)

        return PayFineResponse(
            issue_id=issue.id,
            fine_before=current_fine,
            amount_paid=data.amount,
            fine_remaining=remaining,
            message="Fine paid successfully"
            if remaining == 0
            else f"Partial payment. Remaining fine: {remaining}",
        )
