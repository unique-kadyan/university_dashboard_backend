from enums import Enum


class EmploymentType(str, Enum):
    PERMANENT = "permanent"
    CONTRACT = "contract"
    VISITING = "visiting"
    PARTTIME = "parttime"
