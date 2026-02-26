"""Phase 3 — data content tests."""

from open_data_quality.csv_validator import CsvValidator


def test_comma_decimal(fx):
    report = CsvValidator(fx("comma_decimal.csv")).run()
    codes = {f.code for f in report.findings}
    assert "comma_decimal" in codes


def test_non_iso_date(fx):
    report = CsvValidator(fx("non_iso_date.csv")).run()
    codes = {f.code for f in report.findings}
    assert "non_iso_date" in codes


def test_placeholder_values(fx):
    report = CsvValidator(fx("placeholder.csv")).run()
    codes = {f.code for f in report.findings}
    assert "placeholder_values" in codes


def test_fuzzy_duplicates(fx):
    report = CsvValidator(fx("fuzzy_duplicates.csv")).run()
    codes = {f.code for f in report.findings}
    assert "fuzzy_category_values" in codes


def test_datetime_col_no_fuzzy_false_positive(fx):
    """Timestamp columns stored as VARCHAR must not trigger fuzzy duplicate check."""
    report = CsvValidator(fx("datetime_col.csv")).run()
    codes = {f.code for f in report.findings}
    assert "fuzzy_category_values" not in codes


def test_ok_no_content_issues(fx):
    report = CsvValidator(fx("ok.csv")).run()
    codes = {f.code for f in report.findings}
    assert "comma_decimal" not in codes
    assert "non_iso_date" not in codes
    assert "placeholder_values" not in codes
    assert "fuzzy_category_values" not in codes
