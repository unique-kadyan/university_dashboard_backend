import json
import math
import os
import uuid
from typing import Optional

from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from entities.documents import Document
from enums.access_levels import AccessLevel
from enums.document_types import DocumentType
from repositories.document_repository import DocumentRepository
from schemas.student_schemas import DocumentResponse, PaginatedResponse

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",
    "text/csv",
}

ALLOWED_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".webp",
    ".doc", ".docx", ".xls", ".xlsx", ".txt", ".csv",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


class DocumentService:
    def __init__(self, repo: DocumentRepository = Depends()):
        self.repo = repo

    async def upload_document(
        self,
        file: UploadFile,
        title: str,
        document_type: str,
        user_id: int,
        description: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
        is_public: bool = False,
        access_level: Optional[str] = None,
        tags: Optional[str] = None,
    ) -> DocumentResponse:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File type is not allowed",
            )

        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File extension is not allowed",
            )

        contents = b""
        chunk_size = 1024 * 1024
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            contents += chunk
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File size must not exceed 10 MB",
                )
        unique_name = f"{user_id}_{uuid.uuid4().hex}{ext}"
        upload_dir = os.path.join("uploads", "documents")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_name)

        with open(file_path, "wb") as f:
            f.write(contents)

        parsed_tags = None
        if tags:
            try:
                parsed_tags = json.loads(tags)
            except json.JSONDecodeError:
                parsed_tags = [t.strip() for t in tags.split(",") if t.strip()]

        document = Document(
            user_id=user_id,
            title=title,
            description=description,
            document_type=DocumentType(document_type),
            file_path=file_path,
            file_name=file.filename or unique_name,
            file_size=len(contents),
            mime_type=file.content_type,
            uploaded_by=user_id,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            is_public=is_public,
            access_level=AccessLevel(access_level) if access_level else None,
            tags=parsed_tags,
        )
        document = await self.repo.create_document(document)
        return DocumentResponse.model_validate(document)

    async def list_documents(
        self,
        page: int,
        page_size: int,
        document_type: Optional[str] = None,
        user_id: Optional[int] = None,
        is_public: Optional[bool] = None,
    ) -> PaginatedResponse[DocumentResponse]:
        records, total = await self.repo.find_documents_paginated(
            page=page,
            page_size=page_size,
            document_type=document_type,
            user_id=user_id,
            is_public=is_public,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[DocumentResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    def _check_document_access(
        self, document, requesting_user_id: int, role: str
    ) -> None:
        if role in ["admin", "staff"]:
            return
        if document.is_public:
            return
        if document.user_id == requesting_user_id:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document",
        )

    async def get_document(
        self, id: int, requesting_user_id: int = 0, role: str = ""
    ) -> DocumentResponse:
        document = await self.repo.find_document_by_id(id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        self._check_document_access(document, requesting_user_id, role)
        return DocumentResponse.model_validate(document)

    async def delete_document(self, id: int) -> None:
        document = await self.repo.find_document_by_id(id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)

        await self.repo.delete_document(document)

    async def download_document(
        self, id: int, requesting_user_id: int = 0, role: str = ""
    ) -> FileResponse:
        document = await self.repo.find_document_by_id(id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )
        self._check_document_access(document, requesting_user_id, role)

        if not os.path.exists(document.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk",
            )

        return FileResponse(
            path=document.file_path,
            media_type=document.mime_type or "application/octet-stream",
            filename=document.file_name,
        )

    async def search_documents(
        self,
        query: str,
        page: int,
        page_size: int,
        document_type: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> PaginatedResponse[DocumentResponse]:
        records, total = await self.repo.search_documents(
            query_str=query,
            page=page,
            page_size=page_size,
            document_type=document_type,
            user_id=user_id,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[DocumentResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
