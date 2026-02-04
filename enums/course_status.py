from enum import Enum


class CourseStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
