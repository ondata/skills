"""Phase 0 — blocker detection tests."""

import pytest
from open_data_quality.csv_validator import CsvValidator


def test_file_not_found(tmp_path):
    report = CsvValidator(tmp_path / "missing.csv").run()
    codes = {f.code for f in report.findings}
    assert "file_not_found" in codes
    assert report.has_blockers


def test_empty_file(fx):
    report = CsvValidator(fx("empty.csv")).run()
    codes = {f.code for f in report.findings}
    assert "file_empty" in codes
    assert report.has_blockers


def test_json_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_text('{"key": "value"}', encoding="utf-8")
    report = CsvValidator(f).run()
    codes = {f.code for f in report.findings}
    assert "file_wrong_type" in codes
    assert report.has_blockers


def test_binary_file(tmp_path):
    f = tmp_path / "data.csv"
    f.write_bytes(b"\x00\x01\x02\x03" * 100)
    report = CsvValidator(f).run()
    assert report.has_blockers


def test_ok_file_no_blockers(fx):
    report = CsvValidator(fx("ok.csv")).run()
    assert not report.has_blockers
