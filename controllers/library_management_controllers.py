from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.library_schemas import (
    BookCreateRequest,
    BookIssueRequest,
    BookIssueResponse,
    BookRenewRequest,
    BookResponse,
    BookReturnRequest,
    BookSearchResult,
    BookUpdateRequest,
    OverdueBookResponse,
    PayFineRequest,
    PayFineResponse,
)
from schemas.student_schemas import PaginatedResponse
from services.library_service import LibraryBookService, LibraryCirculationService
from utils.auth_dependency import get_current_user

library_router = APIRouter(prefix="/api/v1/library", tags=["Library Management"])


@library_router.get(
    "/books/search",
    response_model=list[BookSearchResult],
    status_code=status.HTTP_200_OK,
)
async def search_books(
    q: str = Query(..., description="Search term"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    current_user: dict = Depends(get_current_user),
    service: LibraryBookService = Depends(),
):
    return await service.search_books(q, limit)


@library_router.get(
    "/books",
    response_model=PaginatedResponse[BookResponse],
    status_code=status.HTTP_200_OK,
)
async def list_books(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    is_referenced: Optional[bool] = Query(None, description="Filter reference books"),
    current_user: dict = Depends(get_current_user),
    service: LibraryBookService = Depends(),
):
    return await service.list_books(
        page=page,
        page_size=page_size,
        category=category,
        department_id=department_id,
        is_referenced=is_referenced,
    )


@library_router.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_book(
    data: BookCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: LibraryBookService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can add books",
        )
    return await service.add_book(data)


@library_router.get(
    "/books/{id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
)
async def get_book(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: LibraryBookService = Depends(),
):
    return await service.get_book(id)


@library_router.put(
    "/books/{id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
)
async def update_book(
    id: int,
    data: BookUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: LibraryBookService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can update books",
        )
    return await service.update_book(id, data)


@library_router.delete(
    "/books/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: LibraryBookService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete books",
        )
    await service.delete_book(id)


@library_router.get(
    "/issued",
    response_model=list[BookIssueResponse],
    status_code=status.HTTP_200_OK,
)
async def get_issued_books(
    user_id: Optional[int] = Query(None, description="Filter by user"),
    book_id: Optional[int] = Query(None, description="Filter by book"),
    current_user: dict = Depends(get_current_user),
    service: LibraryCirculationService = Depends(),
):
    return await service.get_issued_books(user_id=user_id, book_id=book_id)


@library_router.get(
    "/overdue",
    response_model=OverdueBookResponse,
    status_code=status.HTTP_200_OK,
)
async def get_overdue_books(
    current_user: dict = Depends(get_current_user),
    service: LibraryCirculationService = Depends(),
):
    return await service.get_overdue_books()


@library_router.post(
    "/issue",
    response_model=BookIssueResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_book(
    data: BookIssueRequest,
    current_user: dict = Depends(get_current_user),
    service: LibraryCirculationService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can issue books",
        )
    return await service.issue_book(
        data, issued_by_user_id=int(current_user["id"])
    )


@library_router.put(
    "/return",
    response_model=BookIssueResponse,
    status_code=status.HTTP_200_OK,
)
async def return_book(
    data: BookReturnRequest,
    current_user: dict = Depends(get_current_user),
    service: LibraryCirculationService = Depends(),
):
    return await service.return_book(data)


@library_router.post(
    "/renew",
    response_model=BookIssueResponse,
    status_code=status.HTTP_200_OK,
)
async def renew_book(
    data: BookRenewRequest,
    current_user: dict = Depends(get_current_user),
    service: LibraryCirculationService = Depends(),
):
    return await service.renew_book(data)


@library_router.post(
    "/pay-fine",
    response_model=PayFineResponse,
    status_code=status.HTTP_200_OK,
)
async def pay_fine(
    data: PayFineRequest,
    current_user: dict = Depends(get_current_user),
    service: LibraryCirculationService = Depends(),
):
    return await service.pay_fine(data)
