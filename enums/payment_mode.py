from enum import Enum


class PaymentMode(Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"
    CHEQUE = "cheque"
    ONLINE = "online"
