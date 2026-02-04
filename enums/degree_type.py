from enum import Enum


class DegreeType(str, Enum):
    BACHELORS = "bachelors"
    MASTERS = "masters"
    PHD = "phd"
    DIPLOMA = "diploma"
    CERTIFICATE = "certificate"
