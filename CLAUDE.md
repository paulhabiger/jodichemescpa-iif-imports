# ClearBooks — IIF Transaction Categorization

## Project Overview
A Python script that automates transaction categorization for QuickBooks Desktop using IIF files. Part of the larger ClearBooks suite of CPA firm automation tools.

## The Workflow
1. Bank CSV downloaded from the bank
2. CSV + client chart of accounts fed to Claude API
3. Claude categorizes each transaction
4. Script outputs a formatted IIF file
5. Human reviews categorizations
6. Import into QuickBooks Desktop via File → Utilities → Import → IIF Files

## Developer Context
- AAS computer programming, BSAS systems administration — dated but fundamentals are solid
- Currently learning AI-assisted development
- Using Claude Code in Cursor, Gemini for code review
- Spec-driven development approach
- Familiar with Claude API from other projects

## Environment
- QuickBooks Desktop Accountant 2024 on remote server
- Python on local machine
- Claude API for categorization

## IIF Format Rules
- Tab-separated ASCII text
- Account and vendor names must EXACTLY match QuickBooks chart of accounts including capitalization and spacing
- Import requires single-user mode in QuickBooks
- Always backup company file before importing
- Failed imports generate an error IIF file for review

## Code Rules
- Never hardcode client data, API keys, or real financial data
- No real bank CSVs or QuickBooks files committed to the repo
- Chart of accounts loaded per client from config, not hardcoded
- Review step is mandatory before any IIF file is imported — nothing touches QuickBooks without human approval
- Build as if this will serve multiple clients from day one
- Keep modules clean and separated — this is part of a larger platform eventually

## Conversation Rules
- Plan before building, always
- Short answers — I almost always have a follow up
- Never run ahead of what was asked
- No placating, no apologies, no sign-offs
- Push back when something is wrong
- Best practices and learning opportunities welcome when relevant
