from enum import Enum


class ResultStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    PROMOTED = "promoted"
    DETAINED = "detained"
