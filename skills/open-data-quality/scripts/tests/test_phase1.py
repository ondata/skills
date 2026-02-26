"""Phase 1 — file structure tests."""

from open_data_quality.csv_validator import CsvValidator


def test_bom_detected(fx):
    report = CsvValidator(fx("bom.csv")).run()
    codes = {f.code for f in report.findings}
    assert "bom_present" in codes


def test_ok_no_bom(fx):
    report = CsvValidator(fx("ok.csv")).run()
    codes = {f.code for f in report.findings}
    assert "no_bom" in codes
    assert "bom_present" not in codes


def test_ok_separator_detected(fx):
    report = CsvValidator(fx("ok.csv")).run()
    codes = {f.code for f in report.findings}
    assert "separator" in codes
