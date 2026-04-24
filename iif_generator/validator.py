from decimal import Decimal
from .models import Transaction, SUPPORTED_TYPES, TRNS_SIGN


class ValidationError(Exception):
    pass


def validate_transactions(transactions: list[Transaction]) -> None:
    for i, t in enumerate(transactions):
        _validate(t, i)


def _validate(t: Transaction, index: int) -> None:
    label = f"Transaction {index}"

    if t.trns_type not in SUPPORTED_TYPES:
        raise ValidationError(
            f"{label}: unsupported TRNSTYPE {t.trns_type!r}. "
            f"Supported: {sorted(SUPPORTED_TYPES)}"
        )

    if not t.splits:
        raise ValidationError(f"{label}: must have at least one split line.")

    expected_sign = TRNS_SIGN[t.trns_type]
    if expected_sign == -1 and t.amount >= 0:
        raise ValidationError(
            f"{label}: {t.trns_type!r} TRNS amount must be negative, got {t.amount}."
        )
    if expected_sign == +1 and t.amount <= 0:
        raise ValidationError(
            f"{label}: {t.trns_type!r} TRNS amount must be positive, got {t.amount}."
        )

    total = t.amount + sum(s.amount for s in t.splits)
    if total != Decimal("0"):
        raise ValidationError(
            f"{label}: TRNS + splits must sum to 0, got {total}."
        )
