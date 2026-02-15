from typing import Optional

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from configs.db_config import get_db
from entities.notifications import Notification
from entities.user import User
from entities.user_notifications import UserNotification


class NotificationRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def find_notifications_paginated(
        self,
        page: int,
        page_size: int,
        notification_type: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        target_audience: Optional[str] = None,
    ) -> tuple[list[Notification], int]:
        query = select(Notification)
        count_query = select(func.count(Notification.id))

        if notification_type is not None:
            query = query.where(Notification.notification_type == notification_type)
            count_query = count_query.where(
                Notification.notification_type == notification_type
            )
        if priority is not None:
            query = query.where(Notification.priority == priority)
            count_query = count_query.where(Notification.priority == priority)
        if status is not None:
            query = query.where(Notification.status == status)
            count_query = count_query.where(Notification.status == status)
        if target_audience is not None:
            query = query.where(Notification.target_audience == target_audience)
            count_query = count_query.where(
                Notification.target_audience == target_audience
            )

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Notification.id.desc())
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def find_notification_by_id(self, id: int) -> Optional[Notification]:
        result = await self.db.execute(
            select(Notification).where(Notification.id == id)
        )
        return result.scalars().first()

    async def create_notification(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def update_notification(self, notification: Notification) -> Notification:
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def delete_notification(self, notification: Notification) -> None:
        await self.db.delete(notification)
        await self.db.commit()

    async def create_user_notifications_bulk(
        self, user_notifications: list[UserNotification]
    ) -> None:
        self.db.add_all(user_notifications)
        await self.db.commit()

    async def find_user_notification(
        self, user_id: int, notification_id: int
    ) -> Optional[UserNotification]:
        result = await self.db.execute(
            select(UserNotification).where(
                UserNotification.user_id == user_id,
                UserNotification.notification_id == notification_id,
            )
        )
        return result.scalars().first()

    async def update_user_notification(
        self, user_notification: UserNotification
    ) -> UserNotification:
        await self.db.commit()
        await self.db.refresh(user_notification)
        return user_notification

    async def get_user_notifications_paginated(
        self,
        user_id: int,
        page: int,
        page_size: int,
        is_read: Optional[bool] = None,
    ) -> tuple[list[dict], int]:
        query = (
            select(
                UserNotification.id,
                UserNotification.notification_id,
                Notification.title,
                Notification.message,
                Notification.notification_type,
                Notification.priority,
                Notification.sent_by,
                UserNotification.is_read,
                UserNotification.read_at,
                UserNotification.created_at,
            )
            .join(Notification, UserNotification.notification_id == Notification.id)
            .where(UserNotification.user_id == user_id)
        )

        count_query = select(func.count(UserNotification.id)).where(
            UserNotification.user_id == user_id
        )

        if is_read is not None:
            query = query.where(UserNotification.is_read == is_read)
            count_query = count_query.where(UserNotification.is_read == is_read)

        total = (await self.db.execute(count_query)).scalar() or 0
        offset = (page - 1) * page_size
        query = (
            query.offset(offset)
            .limit(page_size)
            .order_by(UserNotification.created_at.desc())
        )
        result = await self.db.execute(query)
        return result.mappings().all(), total

    async def get_unread_count(self, user_id: int) -> int:
        result = await self.db.execute(
            select(func.count(UserNotification.id)).where(
                UserNotification.user_id == user_id,
                UserNotification.is_read == False,
            )
        )
        return result.scalar() or 0

    async def find_active_user_ids_by_type(
        self, user_type: Optional[str] = None
    ) -> list[int]:
        query = select(User.id).where(User.is_active == True)
        if user_type is not None:
            query = query.where(User.user_type == user_type)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]
