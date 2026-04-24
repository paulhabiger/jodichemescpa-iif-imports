"""Quick smoke test — generates a sample IIF file for manual inspection / QB import."""
from decimal import Decimal
from datetime import date
from pathlib import Path
from iif_generator import generate_iif, Transaction, Split

transactions = [
    Transaction(
        trns_type="CHECK",
        date=date(2024, 4, 1),
        account="Main Checking",
        name="Shell Oil",
        amount=Decimal("-45.20"),
        memo="Fuel purchase",
        splits=[
            Split(account="Automobile:Fuel", name="Shell Oil", amount=Decimal("45.20")),
        ],
    ),
    Transaction(
        trns_type="CHECK",
        date=date(2024, 4, 3),
        account="Main Checking",
        name="Office Depot",
        amount=Decimal("-127.50"),
        doc_num="1042",
        splits=[
            Split(account="Office Supplies", name="Office Depot", amount=Decimal("80.00")),
            Split(account="Postage and Delivery", name="Office Depot", amount=Decimal("47.50")),
        ],
    ),
    Transaction(
        trns_type="DEPOSIT",
        date=date(2024, 4, 5),
        account="Main Checking",
        name="Acme Corp",
        amount=Decimal("2500.00"),
        memo="Invoice 1138 payment",
        splits=[
            Split(account="Accounts Receivable", name="Acme Corp", amount=Decimal("-2500.00")),
        ],
    ),
    Transaction(
        trns_type="CREDIT CARD",
        date=date(2024, 4, 8),
        account="Business Visa",
        name="Amazon",
        amount=Decimal("-63.99"),
        memo="Printer ink",
        splits=[
            Split(account="Office Supplies", name="Amazon", amount=Decimal("63.99")),
        ],
    ),
    Transaction(
        trns_type="CCARD REFUND",
        date=date(2024, 4, 10),
        account="Business Visa",
        name="Amazon",
        amount=Decimal("15.00"),
        memo="Partial return",
        splits=[
            Split(account="Office Supplies", name="Amazon", amount=Decimal("-15.00")),
        ],
    ),
]

out = Path("output/sample.iif")
out.parent.mkdir(exist_ok=True)
result = generate_iif(transactions, out, client_id="sample")
print(f"Written: {result}")
print()
print(result.read_text(encoding="ascii"))
