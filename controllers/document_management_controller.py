from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse

from schemas.student_schemas import DocumentResponse, PaginatedResponse
from services.document_service import DocumentService
from utils.auth_dependency import get_current_user

document_router = APIRouter(prefix="/api/v1/documents", tags=["Document Management"])


@document_router.get(
    "/search",
    response_model=PaginatedResponse[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def search_documents(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(),
):
    return await service.search_documents(
        query=q,
        page=page,
        page_size=page_size,
        document_type=document_type,
        user_id=user_id,
    )


@document_router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(...),
    description: Optional[str] = Form(None),
    related_entity_type: Optional[str] = Form(None),
    related_entity_id: Optional[int] = Form(None),
    is_public: bool = Form(False),
    access_level: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can upload documents",
        )
    return await service.upload_document(
        file=file,
        title=title,
        document_type=document_type,
        user_id=current_user["id"],
        description=description,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        is_public=is_public,
        access_level=access_level,
        tags=tags,
    )


@document_router.get(
    "/",
    response_model=PaginatedResponse[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    document_type: Optional[str] = Query(
        None,
        description="Filter by type (certificate, transcript, id_card, report, other)",
    ),
    user_id: Optional[int] = Query(None, description="Filter by user"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(),
):
    return await service.list_documents(
        page=page,
        page_size=page_size,
        document_type=document_type,
        user_id=user_id,
        is_public=is_public,
    )


@document_router.get(
    "/{id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(),
):
    return await service.get_document(
        id, requesting_user_id=int(current_user["id"]), role=current_user["role"]
    )


@document_router.get(
    "/{id}/download",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
)
async def download_document(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(),
):
    return await service.download_document(
        id, requesting_user_id=int(current_user["id"]), role=current_user["role"]
    )


@document_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: DocumentService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete documents",
        )
    await service.delete_document(id)
