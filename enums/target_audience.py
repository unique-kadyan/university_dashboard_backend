from enum import Enum


class TargetAudience(Enum):
    ALL = "all"
    STUDENTS = "students"
    FACULTY = "faculty"
    STAFF = "staff"
    SPECIFIC = "specific"
