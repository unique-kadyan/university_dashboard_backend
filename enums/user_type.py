from enum import Enum


class UserType(str, Enum):
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"
    PARENT = "parent"
