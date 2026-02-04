from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from configs.db_config import Base


class UserNotification(Base):
    __tablename__ = "user_notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=DateTime.now(), nullable=False
    )
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_user_notifications_user_id", "user_id"),
        Index("idx_user_notifications_is_read", "is_read"),
        UniqueConstraint("user_id", "notification_id", name="uix_user_notification"),
    )
