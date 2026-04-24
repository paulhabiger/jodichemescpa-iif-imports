# IIF File Reference — QuickBooks Desktop

Reference sheet for building automated IIF generation. Sourced from Intuit's official docs, Big Red Consulting (the de facto IIF experts), and verified community examples. Focused on what's needed to import bank transactions — checks, deposits, credit card charges — via categorization.

---

## 1. Format Fundamentals

- **File extension:** `.iif`
- **Encoding:** ASCII text (extended/international characters get mangled — stick to ASCII)
- **Delimiter:** Tab character (`\t`) between fields
- **Line endings:** CRLF (`\r\n`) — Windows-style
- **MIME type:** `application/qbooks` or `text/iif`

### Structural pattern

```
!HEADER_DEFINITION <tab> FIELD1 <tab> FIELD2 <tab> ...    <-- definition row (starts with !)
DATA_ROW            <tab> value1 <tab> value2 <tab> ...   <-- data row (same keyword, no !)
```

- Rows starting with `!` are **header/definition rows** — they tell QuickBooks what fields appear in what order.
- Rows without `!` are **data rows** — they must match the field order defined above.
- The first column of every row is a **keyword** (e.g., `TRNS`, `SPL`, `ENDTRNS`, `ACCNT`, `CUST`, `VEND`).

---

## 2. Transaction Block Structure

For any transaction import, three header rows must appear before data:

```
!TRNS     TRNSTYPE  DATE  ACCNT  NAME  AMOUNT  DOCNUM  MEMO  CLEAR
!SPL      TRNSTYPE  DATE  ACCNT  NAME  AMOUNT  DOCNUM  MEMO  CLEAR
!ENDTRNS
```

Then each transaction follows this pattern:

```
TRNS      <transaction header row — the "top" of the transaction>
SPL       <one or more split/distribution lines>
SPL       <...>
ENDTRNS
```

- **`TRNS`** — the transaction's "main" line. Contains the bank/credit-card account and the total amount.
- **`SPL`** — each distribution/category line. One SPL per expense account hit.
- **`ENDTRNS`** — terminator. Required. Missing ENDTRNS is one of the most common import failures.

---

## 3. The Sign Convention (critical)

**Every transaction must sum to zero.** TRNS amount + sum of SPL amounts = 0.

This follows standard double-entry accounting: debits and credits must balance.

| Transaction type | TRNS amount sign | SPL amount sign |
|---|---|---|
| `CHECK` (money leaving a bank account) | Negative | Positive |
| `DEPOSIT` (money entering a bank account) | Positive | Negative |
| `CREDIT CARD` (credit card charge) | Negative | Positive |
| `CCARD REFUND` (credit card refund/credit) | Positive | Negative |
| `BILL` (vendor bill, A/P) | Negative | Positive |
| `INVOICE` (customer invoice, A/R) | Positive | Negative |

**Mental model:** on the `TRNS` line, positive means "the first account (bank/AR) went up." On `SPL` lines, the sign is always the opposite.

Example — a $70 check split between Fuel and Auto Repair:

```
TRNS   CHECK  3/3/2024  Main Checking  ArchCo Gas        -70
SPL    CHECK  3/3/2024  Fuel           ArchCo Gas         10
SPL    CHECK  3/3/2024  Auto Repair                       60
ENDTRNS
```

-70 + 10 + 60 = 0. ✅

---

## 4. TRNSTYPE Values (what matters for bank-feed automation)

These are the types you'll actually hit when categorizing downloaded bank transactions:

| TRNSTYPE | Use for |
|---|---|
| `CHECK` | Any debit from a bank account (checks, debit card, ACH, wire out) |
| `DEPOSIT` | Any credit into a bank account |
| `CREDIT CARD` | Credit card charge (purchase on the card) |
| `CCARD REFUND` | Credit card refund/return |
| `TRANSFER` | Money between two owned accounts |
| `GENERAL JOURNAL` | Adjusting entries — probably not in the first build |

**Watch out:** the IIF Import Kit docs list `BILLCCARD` for credit card charges. That's wrong for current versions — use `CREDIT CARD` with a space. The kit is years out of date.

Types you likely *won't* need for the categorization workflow (but good to know exist):
`BILL`, `BILL REFUND`, `INVOICE`, `CASH SALE`, `CASH REFUND`, `PAYMENT`, `ESTIMATE`, `PURCHASE ORDER`, `STATEMENT CHARGE`, `SALES TAX PAYMENT`, `ITEM RECEIPT`.

---

## 5. Field Reference — TRNS and SPL Rows

### Required (minimum viable transaction)

| Field | Notes |
|---|---|
| `TRNSTYPE` | Must match on TRNS and every SPL line of the same transaction |
| `DATE` | Format must match the Windows regional settings on the machine running QB. Safest bet: `MM/DD/YYYY`. Must be exactly 10 chars if using that format. |
| `ACCNT` | Account name. **Must exactly match** the chart of accounts including capitalization, spaces, and `:` for sub-accounts (e.g., `Automobile:Fuel`). |
| `AMOUNT` | Decimal. Signs per section 3. |
| `NAME` | Vendor/customer/employee name. Required for most transaction types. Use `<none>` or blank where permitted. |

### Commonly used optional fields

| Field | Notes |
|---|---|
| `DOCNUM` | Check number, reference number. **Capped at 12 chars by the new importer** (a bug — workaround in section 8). |
| `MEMO` | Free text. Newlines get flattened in the new importer. |
| `CLEAR` | Reconciled status: `Y`, `N`, or blank. Ignored by new importer anyway. |
| `CLASS` | Class tracking (if enabled). Colon-delimited for sub-classes. |
| `TRNSID` | Unique transaction ID. Leave blank on import — QB assigns it. Including an empty `TRNSID` column is recommended to avoid intermittent issues. |
| `SPLID` | Same as TRNSID but for split lines. Leave blank. |
| `TOPRINT` | `Y`/`N` — whether to mark for printing. |
| `PAID` | `Y`/`N`. |

### SPL-only fields (for item-based transactions — invoices, bills with items)

`QNTY`, `PRICE`, `INVITEM`, `TAXABLE`, `EXTRA`. Not needed for pure account-based categorization of bank transactions.

---

## 6. List-Type Rows (for context — you probably won't generate these)

Each list type has its own `!KEYWORD` header:

| Keyword | List |
|---|---|
| `!ACCNT` | Chart of accounts |
| `!CUST` | Customers |
| `!VEND` | Vendors |
| `!EMP` | Employees |
| `!CLASS` | Classes |
| `!INVITEM` | Items |
| `!OTHERNAME` | Other names |
| `!HDR` | File header (QB adds on export) |

For the ClearBooks categorization workflow: **don't import lists via IIF.** Pull the chart of accounts *out* of QB as reference data for the AI, then generate transactions only. Account/vendor names must pre-exist in QB — if they don't match exactly, QB silently creates them as new bank accounts (yes, really).

---

## 7. The 2019+ Import Bug Pit (critical for QB 2024)

In QB 2019 Intuit introduced a "new and improved" IIF importer. It's widely regarded as broken. Since you're on QB 2024, this applies directly.

**The punchline:** when importing, QuickBooks shows two options:

1. **"Import IIF"** button — the new, buggy code. Slower (10–20×), stricter, with data-mangling bugs.
2. **"Import it for me. I'll fix it later"** link — the old, stable code used for 20+ years. **This is what you want, despite the scary label.**

The second option works reliably and does *not* require fixing anything later. It requires single-user mode.

### Known bugs in the new importer (that the old one doesn't have)

- Semicolons `;` in text fields truncate the line at the semicolon.
- Extended ASCII / international characters render as `?` (e.g., `René` → `Ren?`).
- Newlines inside memo fields get flattened.
- `DOCNUM` capped at 12 chars (QB itself allows more).
- Reconciled status silently ignored — all imports come in as uncleared.
- Won't import $0 invoices even if detail lines are non-zero.
- Assigns check numbers to checks that intentionally have none (debit charges, EFTs).

**Design implication:** build the script to target the old importer path. Assume single-user mode. Document "use Import Without Review" as part of the operator procedure.

---

## 8. Gotchas Worth Pinning to the Wall

1. **Exact name matching is silent-failure territory.** Misspell an account? QB creates a new bank account with that name. Always validate against the client's chart of accounts *before* writing the IIF.
2. **No linking.** IIF can't link invoices to payments, bills to bill payments, or estimates to invoices. Bill payment checks come in as regular checks against A/P.
3. **Single-user mode required** for the recommended import path.
4. **Back up before every import.** Non-negotiable. IIF imports can't be fully undone.
5. **No semicolons** in any text field (new importer). Strip or replace them in memos.
6. **ASCII only.** Strip or transliterate extended characters before writing.
7. **Dates:** `MM/DD/YYYY`, exactly 10 chars, matching the QB machine's regional settings.
8. **Header lines only need to appear once per file.** Don't re-declare `!TRNS` between each transaction — that's actually a common error.
9. **Column order in data rows must match the `!` header exactly.** If the header says `TRNS TRNSTYPE DATE ACCNT NAME AMOUNT`, every data row has to follow that order.
10. **`TRNSID` — include the column, leave values blank.** Omitting the column entirely causes intermittent failures per community reports.
11. **If it can't be entered via the QB UI, it can't be imported via IIF.** IIF is a thin wrapper over the data-entry forms.

---

## 9. Minimal Working Example — Bank Transaction Categorization

A CSV with two bank transactions categorized:

```
!TRNS<TAB>TRNSID<TAB>TRNSTYPE<TAB>DATE<TAB>ACCNT<TAB>NAME<TAB>AMOUNT<TAB>DOCNUM<TAB>MEMO
!SPL<TAB>SPLID<TAB>TRNSTYPE<TAB>DATE<TAB>ACCNT<TAB>NAME<TAB>AMOUNT<TAB>MEMO
!ENDTRNS
TRNS<TAB><TAB>CHECK<TAB>04/15/2024<TAB>Main Checking<TAB>Shell Oil<TAB>-45.20<TAB>DEBIT<TAB>Fuel purchase
SPL<TAB><TAB>CHECK<TAB>04/15/2024<TAB>Automobile:Fuel<TAB>Shell Oil<TAB>45.20<TAB>
ENDTRNS
TRNS<TAB><TAB>DEPOSIT<TAB>04/16/2024<TAB>Main Checking<TAB>Acme Corp<TAB>2500.00<TAB><TAB>Customer payment
SPL<TAB><TAB>DEPOSIT<TAB>04/16/2024<TAB>Accounts Receivable<TAB>Acme Corp<TAB>-2500.00<TAB>
ENDTRNS
```

(`<TAB>` = literal tab character. `<TAB><TAB>` between columns = one empty field, e.g. blank `TRNSID`.)

---

## 10. Authoritative Sources

- **Intuit official:** [IIF Overview: import kit, sample files, and headers](https://quickbooks.intuit.com/learn-support/en-us/help-article/list-management/iif-overview-import-kit-sample-files-headers/L5CZIpJne_US_en_US) — the only first-party reference. Intuit's IIF Import Kit ZIP (linked from that page) contains sample `.iif` files for every transaction type. **Download this.** It's the closest thing to a spec that exists.
- **Intuit official:** [Improved IIF Import in QuickBooks 2019 and later](https://quickbooks.intuit.com/learn-support/en-us/help-article/import-export-data-files/improved-iif-import-quickbooks-2019-later/L1K3ZQDX9_US_en_US) — covers the error-review flow.
- **Big Red Consulting:** [QuickBooks 2019+ IIF Import Issues](https://bigredconsulting.com/quickbooks-2019-iif-import/) — essential reading. Documents every bug in the new importer and the workaround.
- Intuit does not offer technical support for IIF creation or imports. This is officially "programming" territory. Expect to rely on the kit, BRC, and trial-and-error.

---

---

## 11. Import Kit Examples — QB 2007+ (Relevant Types Only)

Kit is in `docs/IIF_Import_Kit/`. Only the QB 2007 & Enterprise 7.0 and later folder applies. Raw examples below, stripped of fields not needed for bank transaction categorization (CLASS, TOPRINT, ADDR5, QNTY, REIMBEXP, VEND list declarations).

**No CREDIT CARD example exists in the kit.** The kit predates the TRNSTYPE rename. Use `CREDIT CARD` (with space) per section 4; sign convention matches CHECK.

---

### CHECK (Write Check)

Kit file: `Write Check/2007 Check (Write Check) Item & Expense.iif`

Raw (tab-separated, extra fields omitted):
```
!TRNS	TRNSID	TRNSTYPE	DATE	ACCNT	NAME	AMOUNT	DOCNUM	MEMO
!SPL	SPLID	TRNSTYPE	DATE	ACCNT	NAME	AMOUNT	DOCNUM	MEMO
!ENDTRNS
TRNS		CHECK	7/16/1998	Checking	Vendor	-110		
SPL		CHECK	7/16/1998	Expense Account		100		Expense memo
SPL		CHECK	7/16/1998	Expense Account		10		
ENDTRNS
```

Notes:
- Kit example had TRNSID populated (140, 141, 142) — leave blank per gotcha #10
- Kit example included CLASS, TOPRINT, ADDR5, QNTY, REIMBEXP — not needed for expense categorization
- Kit example pre-declared a `!VEND` list — don't do this; vendors must already exist in QB

---

### DEPOSIT

Kit file: `Deposit/2007 Deposit (Income).iif`

Raw (tab-separated):
```
!TRNS	TRNSID	TRNSTYPE	DATE	ACCNT	NAME	CLASS	AMOUNT	DOCNUM	CLEAR
!SPL	SPLID	TRNSTYPE	DATE	ACCNT	NAME	CLASS	AMOUNT	DOCNUM	CLEAR
!ENDTRNS
TRNS	15	DEPOSIT	7/16/1998	Checking		50		N
SPL	16	DEPOSIT	7/16/1998	Income Account	Customer	Class Name	-50	236	N
ENDTRNS
```

Clean version (fields we actually use):
```
!TRNS	TRNSID	TRNSTYPE	DATE	ACCNT	NAME	AMOUNT	DOCNUM	MEMO
!SPL	SPLID	TRNSTYPE	DATE	ACCNT	NAME	AMOUNT	DOCNUM	MEMO
!ENDTRNS
TRNS		DEPOSIT	7/16/1998	Checking	Customer	50		
SPL		DEPOSIT	7/16/1998	Income Account	Customer	-50	236	
ENDTRNS
```

Notes:
- Kit omits MEMO from headers — include it; it's useful and the old importer handles it fine
- CLASS omitted — not needed for v1

---

### TRANSFER

Kit file: `Transfer (Bank Transfer)/2007 Transfer.iif`

Raw (tab-separated) — kit example is already clean:
```
!TRNS	TRNSID	TRNSTYPE	DATE	ACCNT	NAME	AMOUNT	DOCNUM	MEMO	CLEAR
!SPL	SPLID	TRNSTYPE	DATE	ACCNT	NAME	AMOUNT	DOCNUM	MEMO	CLEAR
!ENDTRNS
TRNS		TRANSFER	7/1/98	Checking		-500	123	Funds Transfer	N
SPL		TRANSFER	7/1/98	Savings		500			N
ENDTRNS
```

Notes:
- TRNSID is blank in this example — consistent with gotcha #10
- NAME is blank on both lines — transfers are between owned accounts, no vendor/customer
- CLEAR column present but ignored by old importer; can omit in our output

---

### GENERAL JOURNAL

Kit file: `Journal Entry/2007 General Journal Entry.iif`

Raw (tab-separated):
```
!TRNS	TRNSID	TRNSTYPE	DATE	ACCNT	CLASS	AMOUNT	DOCNUM	MEMO
!SPL	SPLID	TRNSTYPE	DATE	ACCNT	CLASS	AMOUNT	DOCNUM	MEMO
!ENDTRNS
TRNS		GENERAL JOURNAL	7/1/1998	Checking		650		
SPL		GENERAL JOURNAL	7/1/1998	Expense Account		-650		
ENDTRNS
```

Notes:
- No NAME field in the kit's journal header — journal entries don't require a vendor/customer
- CLASS present but not needed for v1
- Not in scope for initial build; included here for completeness

---

## Recommended Next Step

Full kit is at `docs/IIF_Import_Kit/`. The QB 2007 & Enterprise 7.0 and later folder is the authoritative version. Section 11 above captures everything relevant — the raw kit files are there if deeper verification is needed.
