from enum import Enum


class NotificationStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"
