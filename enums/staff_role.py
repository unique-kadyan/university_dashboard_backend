from enum import Enum


class AdminStaffRole(Enum):
    SUPER_ADMIN = "super_admin"
    REGISTRAR = "registrar"
    ACCOUNTANT = "accountant"
    LIBRARIAN = "librarian"
    WARDEN = "warden"
    STAFF = "staff"
