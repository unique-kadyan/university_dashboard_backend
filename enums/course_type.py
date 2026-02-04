from enum import Enum


class CourseType(str, Enum):
    CORE = "core"
    ELECTIVE = "elective"
    MANDATORY = "mandatory"
    OPTIONAL = "optional"
