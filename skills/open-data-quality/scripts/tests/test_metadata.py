"""Phase 5 — metadata validator tests."""

from open_data_quality.metadata_validator import MetadataValidator


def _base_meta(**kwargs) -> dict:
    """Minimal valid CKAN metadata dict."""
    meta = {
        "title": "Dataset di test",
        "notes": "Descrizione del dataset di test.",
        "organization": {"title": "Ente di test"},
        "license_id": "CC BY 4.0",
        "tags": [{"name": "a"}, {"name": "b"}, {"name": "c"}],
        "extras": [
            {"key": "issued",   "value": "2024-01-01"},
            {"key": "modified", "value": "2024-06-01"},
        ],
        "resources": [],
    }
    meta.update(kwargs)
    return meta


def _run(meta, portal_url="https://dati.gov.it/opendata"):
    return MetadataValidator(meta, portal_url=portal_url).run()


# ── issued/modified date format ───────────────────────────────────────────────

def test_iso_date_accepted():
    meta = _base_meta()
    report = _run(meta)
    codes = {f.code for f in report.findings}
    assert "issued_ok" in codes
    assert "invalid_issued" not in codes


def test_iso_datetime_accepted():
    """Full ISO datetime must NOT be flagged as invalid."""
    meta = _base_meta()
    meta["extras"] = [
        {"key": "issued",   "value": "2021-12-07T15:20:47.883135"},
        {"key": "modified", "value": "2022-03-10T09:27:04.895252"},
    ]
    report = _run(meta)
    codes = {f.code for f in report.findings}
    assert "invalid_issued" not in codes
    assert "invalid_modified" not in codes


def test_non_iso_date_flagged():
    meta = _base_meta()
    meta["extras"] = [
        {"key": "issued",   "value": "07/12/2021"},
        {"key": "modified", "value": "2024-06-01"},
    ]
    report = _run(meta)
    codes = {f.code for f in report.findings}
    assert "non_iso_issued" in codes


# ── description ───────────────────────────────────────────────────────────────

def test_short_description_not_flagged():
    """A short but present description must not trigger any major finding."""
    meta = _base_meta(notes="Breve.")
    report = _run(meta)
    codes = {f.code for f in report.findings}
    assert "short_description" not in codes
    assert "missing_description" not in codes


def test_missing_description_flagged():
    meta = _base_meta(notes="")
    report = _run(meta)
    codes = {f.code for f in report.findings}
    assert "missing_description" in codes


def test_description_equals_title_flagged():
    meta = _base_meta(title="Uguale", notes="Uguale")
    report = _run(meta)
    codes = {f.code for f in report.findings}
    assert "description_equals_title" in codes


# ── IT profile: holder (dct:rightsHolder) ────────────────────────────────────

def test_it_holder_present_ok():
    meta = _base_meta()
    meta["extras"].append({"key": "holder_name", "value": "Comune di Test"})
    report = _run(meta)
    codes = {f.code for f in report.findings}
    assert "missing_holder_name" not in codes


def test_it_holder_missing_flagged():
    meta = _base_meta()
    report = _run(meta)
    codes = {f.code for f in report.findings}
    assert "missing_holder_name" in codes


# ── UK profile: dcat_-prefixed date aliases ───────────────────────────────────

def test_uk_dcat_prefixed_dates_accepted():
    """UK CKAN uses dcat_issued/dcat_modified — must not be flagged as missing."""
    meta = _base_meta()
    meta["extras"] = [
        {"key": "dcat_issued",   "value": "2024-01-01"},
        {"key": "dcat_modified", "value": "2024-06-01"},
    ]
    report = MetadataValidator(meta, portal_url="https://data.gov.uk").run()
    codes = {f.code for f in report.findings}
    assert "missing_issued" not in codes
    assert "missing_modified" not in codes
