from enum import Enum


class NotificationType(Enum):
    INFO = "info"
    WARNING = "warning"
    URGENT = "urgent"
    ANNOUNCEMENT = "announcement"
