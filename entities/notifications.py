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
from enums.notification_status import NotificationStatus
from enums.notification_type import NotificationType
from enums.priority_levels import PriorityLevel
from enums.target_audience import TargetAudience


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    target_audience = Column(Enum(TargetAudience), nullable=True)
    target_id = Column(JSON, nullable=True)
    priority = Column(Enum(PriorityLevel), nullable=False)
    sent_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    status = Column(Enum(NotificationStatus), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_notifications_user_id", "sent_by"),
        Index("idx_notifications_status", "status"),
        Index("idx_notifications_notification_type", "notification_type"),
    )
