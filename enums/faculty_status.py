from enums import Enum


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    RETIRED = "retired"
    TERMINATED = "terminated"
