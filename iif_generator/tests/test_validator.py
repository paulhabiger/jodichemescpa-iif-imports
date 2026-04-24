import pytest
from decimal import Decimal
from datetime import date
from iif_generator import Transaction, Split
from iif_generator.validator import validate_transactions, ValidationError


def make_check(**overrides):
    defaults = dict(
        trns_type="CHECK",
        date=date(2024, 1, 15),
        account="Main Checking",
        name="Test Vendor",
        amount=Decimal("-100.00"),
        splits=[Split(account="Office Supplies", amount=Decimal("100.00"))],
    )
    defaults.update(overrides)
    return Transaction(**defaults)


def test_valid_transaction_does_not_raise(check_tx):
    validate_transactions([check_tx])  # no exception


def test_unbalanced_raises():
    t = make_check(splits=[Split(account="Office Supplies", amount=Decimal("99.00"))])
    with pytest.raises(ValidationError, match="sum to 0"):
        validate_transactions([t])


def test_wrong_sign_check_raises():
    t = make_check(amount=Decimal("100.00"))
    with pytest.raises(ValidationError, match="negative"):
        validate_transactions([t])


def test_wrong_sign_deposit_raises():
    t = Transaction(
        trns_type="DEPOSIT",
        date=date(2024, 1, 15),
        account="Main Checking",
        name="Customer",
        amount=Decimal("-500.00"),
        splits=[Split(account="Service Revenue", amount=Decimal("500.00"))],
    )
    with pytest.raises(ValidationError, match="positive"):
        validate_transactions([t])


def test_unsupported_trnstype_raises():
    t = make_check(trns_type="BILL")
    with pytest.raises(ValidationError, match="unsupported TRNSTYPE"):
        validate_transactions([t])


def test_empty_splits_raises():
    t = make_check(splits=[])
    with pytest.raises(ValidationError, match="split"):
        validate_transactions([t])


def test_no_file_written_on_failure(tmp_path):
    from iif_generator import generate_iif
    t = make_check(splits=[Split(account="Office Supplies", amount=Decimal("99.00"))])
    out = tmp_path / "out.iif"
    with pytest.raises(ValidationError):
        generate_iif([t], out, client_id="test")
    assert not out.exists()


def test_second_transaction_failure_caught():
    good = make_check()
    bad = make_check(trns_type="WIRE")  # unsupported
    with pytest.raises(ValidationError, match="unsupported TRNSTYPE"):
        validate_transactions([good, bad])
