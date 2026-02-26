"""CLI integration tests (odq-csv)."""

import json
from pathlib import Path
from typer.testing import CliRunner
from open_data_quality.cli_csv import app

runner = CliRunner()


def test_ok_exit_code_zero(fx, tmp_path):
    result = runner.invoke(app, [str(fx("ok.csv")), "--quiet"])
    assert result.exit_code == 0


def test_major_exit_code_one(fx, tmp_path):
    result = runner.invoke(app, [str(fx("non_iso_date.csv")), "--quiet"])
    assert result.exit_code == 1


def test_blocker_exit_code_two(fx, tmp_path):
    result = runner.invoke(app, [str(fx("empty.csv")), "--quiet"])
    assert result.exit_code == 2


def test_output_json(fx, tmp_path):
    out = tmp_path / "report.json"
    runner.invoke(app, [str(fx("ok.csv")), "--output-json", str(out), "--quiet"])
    assert out.exists()
    data = json.loads(out.read_text())
    assert "score" in data
    assert "findings" in data


def test_output_json_has_no_blockers(fx, tmp_path):
    out = tmp_path / "report.json"
    runner.invoke(app, [str(fx("ok.csv")), "--output-json", str(out), "--quiet"])
    data = json.loads(out.read_text())
    blockers = [f for f in data["findings"] if f["severity"] == "blocker"]
    assert blockers == []


def test_auto_md_written(fx, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, [str(fx("ok.csv")), "--quiet"])
    md_files = list((tmp_path / "open-data-quality").glob("*.md"))
    assert len(md_files) == 1
