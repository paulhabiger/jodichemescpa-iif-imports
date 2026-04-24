from pathlib import Path
from .models import Transaction
from .validator import validate_transactions
from .sanitizer import sanitize_text

TRNS_FIELDS = ["TRNSID", "TRNSTYPE", "DATE", "ACCNT", "NAME", "AMOUNT", "DOCNUM", "MEMO"]
SPL_FIELDS  = ["SPLID",  "TRNSTYPE", "DATE", "ACCNT", "NAME", "AMOUNT",           "MEMO"]


def generate_iif(
    transactions: list[Transaction],
    output_path: Path | str,
    client_id: str,
) -> Path:
    """Generate a QuickBooks IIF file from structured transaction data.

    Validates all transactions before writing. Raises ValidationError on any
    violation — no partial file is written on failure.

    client_id is reserved for future per-client config; unused in v1.
    """
    validate_transactions(transactions)
    output_path = Path(output_path)

    lines = _build_lines(transactions)

    # newline="" disables Python's line-ending translation so we control CRLF explicitly.
    with open(output_path, "w", newline="", encoding="ascii", errors="replace") as f:
        for line in lines:
            f.write(line + "\r\n")

    return output_path


def _build_lines(transactions: list[Transaction]) -> list[str]:
    # Headers written once — re-declaring between transactions is a common error (ref gotcha #8).
    lines = [
        "!TRNS\t" + "\t".join(TRNS_FIELDS),
        "!SPL\t"  + "\t".join(SPL_FIELDS),
        "!ENDTRNS",
    ]
    for t in transactions:
        lines.extend(_format_transaction(t))
    return lines


def _format_transaction(t: Transaction) -> list[str]:
    date_str = t.date.strftime("%m/%d/%Y")
    lines = [
        "\t".join([
            "TRNS",
            "",  # TRNSID — present but blank (ref gotcha #10)
            t.trns_type,
            date_str,
            sanitize_text(t.account),
            sanitize_text(t.name),
            _fmt_amount(t.amount),
            sanitize_text(t.doc_num),
            sanitize_text(t.memo),
        ])
    ]
    for s in t.splits:
        lines.append("\t".join([
            "SPL",
            "",  # SPLID — present but blank (ref gotcha #10)
            t.trns_type,
            date_str,
            sanitize_text(s.account),
            sanitize_text(s.name),
            _fmt_amount(s.amount),
            sanitize_text(s.memo),
        ]))
    lines.append("ENDTRNS")
    return lines


def _fmt_amount(amount) -> str:
    return f"{amount:.2f}"
