from sqlalchemy import Column, Date, DateTime, Integer, String, Boolean, ForeignKey, Index, func
from enums.gender import Gender
from enums.user_type import UserType
from configs.db_config import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(UserType, nullable=False)
    email = Column(String, unique=True, nullable=False)
    user_name = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(Gender, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    emergency_contact = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    country = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "user_name"),
        Index("idx_users_user_type", "user_type"),
        Index("idx_users_is_active", "is_active"),
    )
