from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Index, func
from configs.db_config import Base
from enums.staff_role import AdminStaffRole
from enums.status import Status


class AdminStaff(Base):
    __tablename__ = "admin_staff"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), unique=True, nullable=False)
    employee_id = Column(String, unique=True, nullable=False)
    role = Column(AdminStaffRole, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    designation = Column(String, nullable=False)
    date_of_joining = Column(DateTime, nullable=False)
    status = Column(Status, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=True)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_admin_staff_user_id", "user_id"),
        Index("idx_admin_staff_employee_id", "employee_id"),
        Index("idx_admin_staff_role", "role"),
        Index("idx_admin_staff_department_id", "department_id"),
        Index("idx_admin_staff_status", "status"),
    )
