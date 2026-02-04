from sqlalchemy import Column, DateTime, Enum, Enum, Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from decimal import Decimal
from configs.db_config import Base
from enums.library_book_status import LibraryBookStatus


class BookIssue(Base):
    __tablename__ = "book_issues"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    issue_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    return_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    fine_amount = Column(Decimal(6, 2), default=0, nullable=True)
    status = Column(Enum(LibraryBookStatus), nullable=False)
    issued_by = Column(Integer, ForeignKey("admin_staff.id"), nullable=False)
    remarks = Column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=True
    )
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_book_issues_book_id", "book_id"),
        Index("idx_book_issues_user_id", "user_id"),
        Index("idx_book_issues_issue_date", "issue_date"),
        Index("idx_issue_due_date", "due_date"),
        Index("idx_book_issues_status", "status"),
    )
