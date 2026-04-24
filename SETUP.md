# Work Laptop Setup — ClearBooks IIF Generator

Fresh Windows machine, no dev environment. Follow in order.

---

## 1. Install Git

Download: https://git-scm.com/download/win

Run the installer. All defaults are fine.

Verify:
```
git --version
```

---

## 2. Install Python

Download Python 3.11 or newer: https://www.python.org/downloads/windows/

**Important during install:** Check **"Add Python to PATH"** before clicking Install Now.

Verify:
```
python --version
```

---

## 3. Install VS Code

Download: https://code.visualstudio.com/

Run the installer. During install, check:
- "Add to PATH"
- "Register Code as an editor for supported file types"

After install, open VS Code and install the Python extension:
- `Ctrl+Shift+X` → search **Python** → install the one by Microsoft

---

## 4. Clone the Repo

Open a terminal (Windows Terminal, PowerShell, or CMD) and run:

```
git clone https://github.com/paulhabiger/jodichemescpa-iif-imports.git
cd jodichemescpa-iif-imports
```

---

## 5. Create a Virtual Environment

```
python -m venv .venv
```

Activate it:
```
.venv\Scripts\activate
```

Your prompt will change to show `(.venv)`. You'll need to activate it each time you open a new terminal in this project.

---

## 6. Install Dependencies

With the venv active:
```
pip install -e ".[dev]"
```

This installs the `iif_generator` module in editable mode plus pytest.

---

## 7. Verify Everything Works

```
python -m pytest iif_generator/tests/ -v
```

Should show 32 passed.

---

## 8. Open in VS Code

```
code .
```

VS Code will prompt you to select a Python interpreter — choose the one inside `.venv`.

---

## 9. Generate a Test IIF File

```
python generate_sample.py
```

Output file: `output/sample.iif`

This file has 5 transactions (2 checks, 1 deposit, 1 credit card charge, 1 credit card refund) using fake account and vendor names.

---

## 10. Import into QuickBooks Desktop

Before importing:
1. Back up the company file
2. Switch to single-user mode

Import steps:
1. **File → Utilities → Import → IIF Files**
2. Select `output/sample.iif`
3. When prompted, click **"Import it for me. I'll fix it later"** — not the "Import IIF" button
4. Check the register for the imported transactions

The fake account/vendor names in `sample.iif` won't match your chart of accounts, so QB will either error or silently create new accounts. That's expected for this test — the goal is to confirm the file structure imports without crashing.

For a real test against your actual chart of accounts, update `generate_sample.py` with account and vendor names that match exactly (including capitalization).

---

## Ongoing Use

Each time you open a new terminal in this project, activate the venv first:
```
.venv\Scripts\activate
```

To pull updates from GitHub:
```
git pull
```
