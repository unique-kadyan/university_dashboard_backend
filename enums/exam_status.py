from enum import Enum


class ExamStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
