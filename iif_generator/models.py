from dataclasses import dataclass, field
from decimal import Decimal
from datetime import date

SUPPORTED_TYPES = {"CHECK", "DEPOSIT", "CREDIT CARD", "CCARD REFUND"}

# Expected sign on the TRNS amount line per TRNSTYPE (ref: iif_reference.md §3)
TRNS_SIGN = {
    "CHECK":        -1,
    "DEPOSIT":      +1,
    "CREDIT CARD":  -1,
    "CCARD REFUND": +1,
}


@dataclass
class Split:
    account: str
    amount: Decimal
    memo: str = ""
    name: str = ""


@dataclass
class Transaction:
    trns_type: str
    date: date
    account: str
    amount: Decimal
    name: str = ""
    splits: list["Split"] = field(default_factory=list)
    memo: str = ""
    doc_num: str = ""
