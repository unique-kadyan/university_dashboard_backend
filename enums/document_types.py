from enum import Enum


class DocumentType(Enum):
    CERTIFICATE = "certificate"
    TRANSCRIPT = "transcript"
    ID_CARD = "id_card"
    REPORT = "report"
    OTHER = "other"
