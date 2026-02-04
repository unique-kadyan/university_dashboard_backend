from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from enums.employment_type import EmploymentType
from datetime import datetime
from enums.faculty_status import Status
from configs.db_config import Base


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    designation = Column(String, nullable=False)
    specialization = Column(String, nullable=True)
    qualification = Column(String, nullable=True)
    date_of_joining: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=True
    )
    employment_type = Column(EmploymentType, nullable=False)
    experience_years = Column(Integer, nullable=True)
    is_hod = Column(Boolean, default=False)
    status = Column(Status, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=True
    )
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_faculty_user_id", "user_id"),
        Index("idx_faculty_employee_id", "employee_id"),
        Index("idx_faculty_department_id", "department_id"),
        Index("idx_faculty_status", "status"),
    )
