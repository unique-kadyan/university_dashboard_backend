from enum import Enum


class StudentStatus(str, Enum):
    ENROLLED = "enrolled"
    DROPPED = "dropped"
    COMPLETED = "completed"
    FAILED = "failed"
