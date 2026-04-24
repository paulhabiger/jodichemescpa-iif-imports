import pytest
from decimal import Decimal
from datetime import date
from iif_generator import Transaction, Split


@pytest.fixture
def check_tx():
    return Transaction(
        trns_type="CHECK",
        date=date(2024, 1, 15),
        account="Main Checking",
        name="Test Vendor",
        amount=Decimal("-100.00"),
        splits=[
            Split(account="Office Supplies", name="Test Vendor", amount=Decimal("100.00")),
        ],
    )


@pytest.fixture
def deposit_tx():
    return Transaction(
        trns_type="DEPOSIT",
        date=date(2024, 1, 16),
        account="Main Checking",
        name="Test Customer",
        amount=Decimal("500.00"),
        splits=[
            Split(account="Service Revenue", name="Test Customer", amount=Decimal("-500.00")),
        ],
    )


@pytest.fixture
def credit_card_tx():
    return Transaction(
        trns_type="CREDIT CARD",
        date=date(2024, 1, 17),
        account="Business Visa",
        name="Office Depot",
        amount=Decimal("-75.50"),
        splits=[
            Split(account="Office Supplies", name="Office Depot", amount=Decimal("75.50")),
        ],
    )


@pytest.fixture
def ccard_refund_tx():
    return Transaction(
        trns_type="CCARD REFUND",
        date=date(2024, 1, 18),
        account="Business Visa",
        name="Amazon",
        amount=Decimal("25.00"),
        splits=[
            Split(account="Office Supplies", name="Amazon", amount=Decimal("-25.00")),
        ],
    )


@pytest.fixture
def check_multi_split_tx():
    return Transaction(
        trns_type="CHECK",
        date=date(2024, 1, 19),
        account="Main Checking",
        name="Gas Station",
        amount=Decimal("-70.00"),
        splits=[
            Split(account="Automobile:Fuel", name="Gas Station", amount=Decimal("10.00")),
            Split(account="Automobile:Repairs", amount=Decimal("30.00")),
            Split(account="Office Supplies", amount=Decimal("30.00")),
        ],
    )
