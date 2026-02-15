from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from schemas.notification_schemas import (
    NotificationCreateRequest,
    NotificationResponse,
    UnreadCountResponse,
    UserNotificationListResponse,
)
from schemas.student_schemas import PaginatedResponse
from services.notification_service import NotificationService
from utils.auth_dependency import get_current_user

notification_router = APIRouter(
    prefix="/api/v1/notifications", tags=["Notification Management"]
)


@notification_router.get(
    "/unread",
    response_model=UnreadCountResponse,
    status_code=status.HTTP_200_OK,
)
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(),
):
    return await service.get_unread_count(current_user["id"])


@notification_router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_notification(
    data: NotificationCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can send notifications",
        )
    return await service.send_notification(data, current_user["id"])


@notification_router.get(
    "/",
    response_model=PaginatedResponse[NotificationResponse],
    status_code=status.HTTP_200_OK,
)
async def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    notification_type: Optional[str] = Query(
        None, description="Filter by type (info, warning, urgent, announcement)"
    ),
    priority: Optional[str] = Query(
        None, description="Filter by priority (low, medium, high)"
    ),
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by status (draft, scheduled, sent, failed)",
    ),
    target_audience: Optional[str] = Query(
        None, description="Filter by audience (all, students, faculty, staff, specific)"
    ),
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(),
):
    return await service.list_notifications(
        page=page,
        page_size=page_size,
        notification_type=notification_type,
        priority=priority,
        status_filter=status_filter,
        target_audience=target_audience,
    )


@notification_router.get(
    "/{id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_notification(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(),
):
    return await service.get_notification(id)


@notification_router.put(
    "/{id}/read",
    status_code=status.HTTP_200_OK,
)
async def mark_as_read(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(),
):
    return await service.mark_as_read(id, current_user["id"])


@notification_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_notification(
    id: int,
    current_user: dict = Depends(get_current_user),
    service: NotificationService = Depends(),
):
    if current_user["role"] not in ["admin", "staff"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and staff can delete notifications",
        )
    await service.delete_notification(id)
