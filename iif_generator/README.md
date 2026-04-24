# iif_generator

Generates QuickBooks Desktop IIF import files from structured Python transaction data. Part of the ClearBooks automation suite.

## Usage

```python
from decimal import Decimal
from datetime import date
from iif_generator import generate_iif, Transaction, Split

transactions = [
    Transaction(
        trns_type="CHECK",
        date=date(2024, 1, 15),
        account="Main Checking",       # must exactly match QB account name
        name="Shell Oil",              # must exactly match QB vendor name
        amount=Decimal("-45.20"),
        memo="Fuel purchase",
        splits=[
            Split(account="Automobile:Fuel", name="Shell Oil", amount=Decimal("45.20")),
        ],
    ),
]

output_path = generate_iif(transactions, "output/january.iif", client_id="client_abc")
```

`generate_iif` validates all transactions before writing. On any failure it raises `ValidationError` and writes no file.

## Supported transaction types

| TRNSTYPE | Use for |
|---|---|
| `CHECK` | Bank debits — checks, debit card, ACH out, wire out |
| `DEPOSIT` | Bank credits |
| `CREDIT CARD` | Credit card charges |
| `CCARD REFUND` | Credit card refunds |

## Sign convention

Every transaction must sum to zero: TRNS amount + sum of split amounts = 0.

| Type | TRNS amount | Split amounts |
|---|---|---|
| CHECK | Negative | Positive |
| DEPOSIT | Positive | Negative |
| CREDIT CARD | Negative | Positive |
| CCARD REFUND | Positive | Negative |

## Importing into QuickBooks Desktop

Use **File → Utilities → Import → IIF Files**, then choose **"Import it for me. I'll fix it later"** (the old stable importer). Do not use the "Import IIF" button. Requires single-user mode. Always back up the company file first.

## Running tests

```bash
pip install -e ".[dev]"
pytest iif_generator/tests/ -v
```
