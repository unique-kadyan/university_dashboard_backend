import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status

from entities.notifications import Notification
from entities.user_notifications import UserNotification
from enums.notification_status import NotificationStatus
from enums.notification_type import NotificationType
from enums.priority_levels import PriorityLevel
from enums.target_audience import TargetAudience
from repositories.notification_repository import NotificationRepository
from schemas.notification_schemas import (
    NotificationCreateRequest,
    NotificationResponse,
    UnreadCountResponse,
    UserNotificationItem,
    UserNotificationListResponse,
)
from schemas.student_schemas import PaginatedResponse

TARGET_AUDIENCE_TO_USER_TYPE = {
    "students": "student",
    "faculty": "teacher",
    "staff": "admin",
}


class NotificationService:
    def __init__(self, repo: NotificationRepository = Depends()):
        self.repo = repo

    async def send_notification(
        self, data: NotificationCreateRequest, sender_id: int
    ) -> NotificationResponse:
        notification = Notification(
            title=data.title,
            message=data.message,
            notification_type=NotificationType(data.notification_type),
            target_audience=(
                TargetAudience(data.target_audience) if data.target_audience else None
            ),
            target_id=data.target_id,
            priority=PriorityLevel(data.priority),
            sent_by=sender_id,
            scheduled_at=data.scheduled_at,
            sent_at=datetime.now(timezone.utc),
            status=(
                NotificationStatus(data.status)
                if data.status
                else NotificationStatus.SENT
            ),
        )
        notification = await self.repo.create_notification(notification)

        user_ids = await self._resolve_target_users(
            data.target_audience, data.target_id
        )
        if user_ids:
            user_notifications = [
                UserNotification(
                    user_id=uid,
                    notification_id=notification.id,
                )
                for uid in user_ids
            ]
            await self.repo.create_user_notifications_bulk(user_notifications)

        return NotificationResponse.model_validate(notification)

    async def _resolve_target_users(
        self, target_audience: Optional[str], target_id: Optional[list]
    ) -> list[int]:
        if not target_audience:
            return []

        audience = target_audience.lower()
        if audience == "all":
            return await self.repo.find_active_user_ids_by_type()
        elif audience == "specific":
            return target_id or []
        elif audience in TARGET_AUDIENCE_TO_USER_TYPE:
            user_type = TARGET_AUDIENCE_TO_USER_TYPE[audience]
            return await self.repo.find_active_user_ids_by_type(user_type)
        return []

    async def list_notifications(
        self,
        page: int,
        page_size: int,
        notification_type: Optional[str] = None,
        priority: Optional[str] = None,
        status_filter: Optional[str] = None,
        target_audience: Optional[str] = None,
    ) -> PaginatedResponse[NotificationResponse]:
        records, total = await self.repo.find_notifications_paginated(
            page=page,
            page_size=page_size,
            notification_type=notification_type,
            priority=priority,
            status=status_filter,
            target_audience=target_audience,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return PaginatedResponse(
            items=[NotificationResponse.model_validate(r) for r in records],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_notification(self, id: int) -> NotificationResponse:
        notification = await self.repo.find_notification_by_id(id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        return NotificationResponse.model_validate(notification)

    async def mark_as_read(self, notification_id: int, user_id: int) -> dict:
        user_notification = await self.repo.find_user_notification(
            user_id, notification_id
        )
        if not user_notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found for this user",
            )

        user_notification.is_read = True
        user_notification.read_at = datetime.now(timezone.utc)
        user_notification.updated_at = datetime.now(timezone.utc)
        await self.repo.update_user_notification(user_notification)
        return {"message": "Notification marked as read"}

    async def delete_notification(self, id: int) -> None:
        notification = await self.repo.find_notification_by_id(id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        await self.repo.delete_notification(notification)

    async def get_unread_count(self, user_id: int) -> UnreadCountResponse:
        count = await self.repo.get_unread_count(user_id)
        return UnreadCountResponse(user_id=user_id, unread_count=count)

    async def get_user_notifications(
        self,
        user_id: int,
        page: int,
        page_size: int,
        is_read: Optional[bool] = None,
    ) -> UserNotificationListResponse:
        rows, total = await self.repo.get_user_notifications_paginated(
            user_id=user_id,
            page=page,
            page_size=page_size,
            is_read=is_read,
        )
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        items = [UserNotificationItem(**row) for row in rows]
        return UserNotificationListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
