def sanitize_text(value: str) -> str:
    """Strip non-ASCII, semicolons, and newlines from IIF text fields.

    Non-ASCII and semicolons cause silent data corruption in QB's IIF importer.
    Sanitization is silent — callers receive clean output without raising.
    """
    value = value.encode("ascii", errors="ignore").decode("ascii")
    value = value.replace(";", "")
    value = value.replace("\n", " ").replace("\r", " ")
    return value
