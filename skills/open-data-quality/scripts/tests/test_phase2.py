"""Phase 2 — column structure tests."""

from open_data_quality.csv_validator import CsvValidator


def test_wide_format_years(fx):
    report = CsvValidator(fx("wide_years.csv")).run()
    codes = {f.code for f in report.findings}
    assert "wide_format_years" in codes


def test_wide_format_months(fx):
    report = CsvValidator(fx("wide_months.csv")).run()
    codes = {f.code for f in report.findings}
    assert "wide_format_months" in codes


def test_aggregate_rows(fx):
    report = CsvValidator(fx("aggregate_rows.csv")).run()
    codes = {f.code for f in report.findings}
    assert "aggregate_rows" in codes


def test_duplicate_columns(fx):
    report = CsvValidator(fx("duplicate_cols.csv")).run()
    codes = {f.code for f in report.findings}
    assert "duplicate_columns" in codes


def test_ok_no_wide_format(fx):
    report = CsvValidator(fx("ok.csv")).run()
    codes = {f.code for f in report.findings}
    assert "no_wide_format" in codes
    assert "wide_format_years" not in codes
    assert "wide_format_months" not in codes
