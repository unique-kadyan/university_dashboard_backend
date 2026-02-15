from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Integer,
    String,
    ForeignKey,
    Index,
    func,
)

from configs.db_config import Base
from enums.access_levels import AccessLevel
from enums.document_types import DocumentType


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    document_type = Column(Enum(DocumentType), nullable=False)
    file_path = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    related_entity_type = Column(String, nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    access_level = Column(Enum(AccessLevel), nullable=True)
    tags = Column(JSON, nullable=True)
    uploaded_at = Column(DateTime, default=func.now(), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_documents_uploaded_by", "uploaded_by"),
        Index("idx_documents_uploaded_at", "uploaded_at"),
        Index("idx_documents_document_type", "document_type"),
        Index("idx_related_entity", "related_entity_type", "related_entity_id"),
    )
