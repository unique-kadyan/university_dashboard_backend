from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, ForeignKey, Index, func

from configs.db_config import Base


class LibraryBook(Base):
    __tablename__ = "library_books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    publisher = Column(String, nullable=True)
    year_of_publication = Column(Integer, nullable=True)
    edition = Column(String, nullable=True)
    category = Column(String, nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    language = Column(String, nullable=True)
    pages = Column(Integer, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    copies_total = Column(Integer, default=1, nullable=False)
    copies_available = Column(Integer, default=1, nullable=False)
    rack_no = Column(String, nullable=True)
    shelf_no = Column(String, nullable=True)
    is_referenced = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_library_books_title", "title"),
        Index("idx_library_books_author", "author"),
        Index("idx_library_books_isbn", "isbn"),
        Index("idx_category", "category"),
    )
