from sqlalchemy import Column, DateTime, Integer, Numeric, String, Date, ForeignKey, Index, func
from enums.category import Category
from enums.status import Status
from configs.db_config import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    Student_id = Column(String, unique=True, nullable=False)
    admisson_number = Column(String, unique=True, nullable=False)
    admission_date = Column(Date, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id", ondelete="RESTRICT"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False)
    batch_year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    section = Column(String, nullable=True)
    blood_group = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    religion = Column(String, nullable=True)
    category = Column(Category, nullable=True)
    parent_id = Column(Integer, ForeignKey("parents.id", ondelete="SET NULL"), nullable=True)
    guardian_id = Column(Integer, nullable=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id", ondelete="SET NULL"), nullable=True)
    status = Column(Status, nullable=False)
    cgpa = Column(Numeric(10, 3), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_students_user_id", "user_id"),
        Index("idx_students_student_id", "Student_id"),
        Index("idx_program_id", "program_id"),
        Index("idx_department_id", "department_id"),
        Index("idx_status", "status"),
        Index("idx_batch_year", "batch_year"),
    )
