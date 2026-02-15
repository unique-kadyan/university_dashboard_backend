from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    notification_type: str
    target_audience: Optional[str] = None
    target_id: Optional[list] = None
    priority: str
    sent_by: int
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationCreateRequest(BaseModel):
    title: str
    message: str
    notification_type: str
    target_audience: Optional[str] = None
    target_id: Optional[List[int]] = None
    priority: str
    status: Optional[str] = "sent"
    scheduled_at: Optional[datetime] = None


class UserNotificationItem(BaseModel):
    id: int
    notification_id: int
    title: str
    message: str
    notification_type: str
    priority: str
    sent_by: int
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class UserNotificationListResponse(BaseModel):
    items: List[UserNotificationItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class UnreadCountResponse(BaseModel):
    user_id: int
    unread_count: int
