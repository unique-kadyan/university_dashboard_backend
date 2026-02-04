from enums import Enum


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"
    DROPPED = "dropped"
    TRANSFERRED = "transferred"
