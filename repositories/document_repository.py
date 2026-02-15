from typing import Optional

from fastapi import Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.documents import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_documents_paginated(
        self,
        page: int,
        page_size: int,
        document_type: Optional[str] = None,
        user_id: Optional[int] = None,
        is_public: Optional[bool] = None,
    ) -> tuple[list[Document], int]:
        query = select(Document)
        count_query = select(func.count(Document.id))

        if document_type is not None:
            query = query.where(Document.document_type == document_type)
            count_query = count_query.where(Document.document_type == document_type)
        if user_id is not None:
            query = query.where(Document.user_id == user_id)
            count_query = count_query.where(Document.user_id == user_id)
        if is_public is not None:
            query = query.where(Document.is_public == is_public)
            count_query = count_query.where(Document.is_public == is_public)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Document.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_document_by_id(self, id: int) -> Optional[Document]:
        result = await self.db.execute(select(Document).where(Document.id == id))
        return result.scalars().first()

    async def create_document(self, document: Document) -> Document:
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete_document(self, document: Document) -> None:
        await self.db.delete(document)
        await self.db.commit()

    async def search_documents(
        self,
        query_str: str,
        page: int,
        page_size: int,
        document_type: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> tuple[list[Document], int]:
        search_filter = or_(
            Document.title.ilike(f"%{query_str}%"),
            Document.description.ilike(f"%{query_str}%"),
            Document.file_name.ilike(f"%{query_str}%"),
        )

        query = select(Document).where(search_filter)
        count_query = select(func.count(Document.id)).where(search_filter)

        if document_type is not None:
            query = query.where(Document.document_type == document_type)
            count_query = count_query.where(Document.document_type == document_type)
        if user_id is not None:
            query = query.where(Document.user_id == user_id)
            count_query = count_query.where(Document.user_id == user_id)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Document.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total
