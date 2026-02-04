from enum import Enum


class LibraryBookStatus(Enum):
    ISSUED = "issued"
    RETURNED = "returned"
    OVERDUE = "overdue"
    LOST = "lost"
