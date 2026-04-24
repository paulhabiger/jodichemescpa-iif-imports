from pathlib import Path
from decimal import Decimal
from datetime import date
import pytest
from iif_generator import generate_iif, Transaction, Split
from iif_generator.writer import TRNS_FIELDS, SPL_FIELDS

FIXTURES = Path(__file__).parent / "fixtures"


def parse_iif(path):
    """Parse IIF file into a list of (keyword, fields_dict) tuples.

    Normalizes line endings and handles missing trailing fields gracefully,
    so fixture files and generated output compare equal regardless of trailing tabs.
    """
    content = Path(path).read_bytes().decode("ascii", errors="replace")
    lines = content.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")

    headers = {}
    rows = []

    for line in lines:
        if not line.strip():
            continue
        cols = line.split("\t")
        keyword = cols[0]

        if keyword.startswith("!"):
            base = keyword[1:]
            headers[base] = cols[1:]
        elif keyword == "ENDTRNS":
            rows.append(("ENDTRNS", {}))
        else:
            field_names = headers.get(keyword, [])
            values = cols[1:]
            row_data = {
                name: (values[i] if i < len(values) else "")
                for i, name in enumerate(field_names)
            }
            rows.append((keyword, row_data))

    return rows


# --- Happy path: fixture comparison ---

def test_check_single(check_tx, tmp_path):
    out = generate_iif([check_tx], tmp_path / "out.iif", client_id="test")
    assert parse_iif(out) == parse_iif(FIXTURES / "check_single.iif")


def test_deposit_single(deposit_tx, tmp_path):
    out = generate_iif([deposit_tx], tmp_path / "out.iif", client_id="test")
    assert parse_iif(out) == parse_iif(FIXTURES / "deposit_single.iif")


def test_credit_card_single(credit_card_tx, tmp_path):
    out = generate_iif([credit_card_tx], tmp_path / "out.iif", client_id="test")
    assert parse_iif(out) == parse_iif(FIXTURES / "credit_card_single.iif")


def test_ccard_refund_single(ccard_refund_tx, tmp_path):
    out = generate_iif([ccard_refund_tx], tmp_path / "out.iif", client_id="test")
    assert parse_iif(out) == parse_iif(FIXTURES / "ccard_refund_single.iif")


def test_check_multi_split(check_multi_split_tx, tmp_path):
    out = generate_iif([check_multi_split_tx], tmp_path / "out.iif", client_id="test")
    assert parse_iif(out) == parse_iif(FIXTURES / "check_multi_split.iif")


def test_mixed_types_in_one_file(check_tx, deposit_tx, tmp_path):
    out = generate_iif([check_tx, deposit_tx], tmp_path / "out.iif", client_id="test")
    assert parse_iif(out) == parse_iif(FIXTURES / "mixed_types.iif")


# --- Structural tests ---

def test_headers_written_once(check_tx, deposit_tx, tmp_path):
    out = generate_iif([check_tx, deposit_tx], tmp_path / "out.iif", client_id="test")
    content = out.read_bytes().decode("ascii")
    assert content.count("!TRNS") == 1
    assert content.count("!SPL") == 1
    assert content.count("!ENDTRNS") == 1


def test_crlf_line_endings(check_tx, tmp_path):
    out = generate_iif([check_tx], tmp_path / "out.iif", client_id="test")
    raw = out.read_bytes()
    assert b"\r\n" in raw
    # No bare LF (every \n must be preceded by \r)
    import re
    assert not re.search(b"(?<!\r)\n", raw)


def test_tab_delimiter(check_tx, tmp_path):
    out = generate_iif([check_tx], tmp_path / "out.iif", client_id="test")
    content = out.read_bytes().decode("ascii")
    lines = content.replace("\r\n", "\n").strip().split("\n")
    for line in lines:
        keyword = line.split("\t")[0]
        if keyword == "TRNS":
            assert line.count("\t") == len(TRNS_FIELDS)
        elif keyword == "SPL":
            assert line.count("\t") == len(SPL_FIELDS)


def test_trnsid_splid_blank(check_tx, tmp_path):
    out = generate_iif([check_tx], tmp_path / "out.iif", client_id="test")
    rows = parse_iif(out)
    trns_rows = [r for kw, r in rows if kw == "TRNS"]
    spl_rows  = [r for kw, r in rows if kw == "SPL"]
    assert all(r["TRNSID"] == "" for r in trns_rows)
    assert all(r["SPLID"] == "" for r in spl_rows)


def test_output_path_returned(check_tx, tmp_path):
    out_path = tmp_path / "result.iif"
    result = generate_iif([check_tx], out_path, client_id="test")
    assert result == out_path
    assert result.exists()


# --- Edge cases ---

def test_empty_memo_and_name(tmp_path):
    t = Transaction(
        trns_type="CHECK",
        date=date(2024, 1, 15),
        account="Main Checking",
        amount=Decimal("-50.00"),
        splits=[Split(account="Office Supplies", amount=Decimal("50.00"))],
    )
    out = generate_iif([t], tmp_path / "out.iif", client_id="test")
    rows = parse_iif(out)
    trns = next(r for kw, r in rows if kw == "TRNS")
    assert trns["NAME"] == ""
    assert trns["MEMO"] == ""


def test_doc_num_written(tmp_path):
    t = Transaction(
        trns_type="CHECK",
        date=date(2024, 1, 15),
        account="Main Checking",
        name="Vendor",
        amount=Decimal("-50.00"),
        doc_num="1042",
        splits=[Split(account="Office Supplies", amount=Decimal("50.00"))],
    )
    out = generate_iif([t], tmp_path / "out.iif", client_id="test")
    rows = parse_iif(out)
    trns = next(r for kw, r in rows if kw == "TRNS")
    assert trns["DOCNUM"] == "1042"


def test_sanitized_semicolon_in_memo(tmp_path):
    t = Transaction(
        trns_type="CHECK",
        date=date(2024, 1, 15),
        account="Main Checking",
        name="Vendor",
        amount=Decimal("-50.00"),
        memo="Office supplies; Jan 2024",
        splits=[Split(account="Office Supplies", amount=Decimal("50.00"))],
    )
    out = generate_iif([t], tmp_path / "out.iif", client_id="test")
    rows = parse_iif(out)
    trns = next(r for kw, r in rows if kw == "TRNS")
    assert ";" not in trns["MEMO"]


def test_trnstype_on_every_spl_line(check_multi_split_tx, tmp_path):
    out = generate_iif([check_multi_split_tx], tmp_path / "out.iif", client_id="test")
    rows = parse_iif(out)
    spl_rows = [r for kw, r in rows if kw == "SPL"]
    assert len(spl_rows) == 3
    assert all(r["TRNSTYPE"] == "CHECK" for r in spl_rows)


def test_endtrns_present(check_tx, tmp_path):
    out = generate_iif([check_tx], tmp_path / "out.iif", client_id="test")
    content = out.read_bytes().decode("ascii")
    assert "ENDTRNS" in content
    # Data ENDTRNS (no !) should appear once per transaction
    rows = parse_iif(out)
    endtrns_count = sum(1 for kw, _ in rows if kw == "ENDTRNS")
    assert endtrns_count == 1
