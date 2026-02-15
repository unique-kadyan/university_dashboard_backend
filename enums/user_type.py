from enum import Enum


class UserType(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"
