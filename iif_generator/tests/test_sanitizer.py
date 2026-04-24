from iif_generator.sanitizer import sanitize_text


def test_semicolon_stripped():
    assert sanitize_text("memo; with semicolon") == "memo with semicolon"


def test_multiple_semicolons_stripped():
    assert sanitize_text("a;b;c") == "abc"


def test_non_ascii_stripped():
    assert sanitize_text("René") == "Ren"


def test_newline_replaced_with_space():
    assert sanitize_text("line one\nline two") == "line one line two"


def test_carriage_return_replaced_with_space():
    assert sanitize_text("line one\rline two") == "line one line two"


def test_clean_string_unchanged():
    assert sanitize_text("Normal memo text") == "Normal memo text"


def test_empty_string():
    assert sanitize_text("") == ""


def test_combined_issues():
    result = sanitize_text("René; line\none")
    assert result == "Ren line one"
