"""
CKAN / portal metadata validator — Phases 5–6.

Checks DCAT-AP compliance (baseline + national profiles).
Works on the Python dict returned by CKAN package_show.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any

import httpx

from .models import QualityReport, ScoreDimension

PHASE5 = "phase5_metadata"
PHASE6 = "phase6_consistency"

ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NON_ISO_DATE_RE = re.compile(r"^\d{1,2}[-/\.]\d{1,2}[-/\.]\d{4}$")

UNSTABLE_URL_RE = re.compile(
    r"bit\.ly|tinyurl|goo\.gl|t\.co|google\.com/spreadsheets"
    r"|dropbox\.com|drive\.google|onedrive\.live",
    re.IGNORECASE,
)

# National profile detection: portal URL → profile key
PORTAL_PROFILES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"dati\.gov\.it",           re.I), "DCAT-AP_IT"),
    (re.compile(r"govdata\.de",             re.I), "DCAT-AP_DE"),
    (re.compile(r"data\.gouv\.fr",          re.I), "DCAT-AP_FR"),
    (re.compile(r"data\.gov\.be",           re.I), "DCAT-AP_BE"),
    (re.compile(r"data\.overheid\.nl",      re.I), "DCAT-AP_DONL"),
    (re.compile(r"data\.gov\.uk",           re.I), "DCAT-AP_UK"),
    (re.compile(r"datos\.gob\.es",          re.I), "DCAT-AP_ES"),
    (re.compile(r"dados\.gov\.pt",          re.I), "DCAT-AP_PT"),
    (re.compile(r"opendata\.swiss",         re.I), "DCAT-AP_CH"),
    (re.compile(r"data\.gv\.at",            re.I), "DCAT-AP_AT"),
    (re.compile(r"data\.public\.lu",        re.I), "DCAT-AP_LU"),
]

# Profile-specific mandatory fields (beyond DCAT-AP baseline)
# key: extras key name in CKAN JSON, label: human readable
PROFILE_EXTRA_FIELDS: dict[str, list[tuple[str, str, str]]] = {
    # (extras_key, label, mandatory|recommended)
    "DCAT-AP_IT": [
        ("holder_name",    "Dataset holder (dcatapit:datasetHolder)", "mandatory"),
        ("identifier",     "Identifier (dct:identifier)",             "mandatory"),
        ("theme",          "Theme (dcat:theme)",                      "mandatory"),
    ],
    "DCAT-AP_DE": [
        ("identifier",     "Identifier (dct:identifier)",             "mandatory"),
    ],
    "DCAT-AP_BE": [
        ("identifier",     "Identifier (dct:identifier)",             "mandatory"),
    ],
    "DCAT-AP_DONL": [
        ("identifier",     "Identifier (dct:identifier)",             "mandatory"),
        ("geographical_geonames_url", "Spatial (dct:spatial)",        "mandatory"),
    ],
    "DCAT-AP_ES": [
        ("identifier",     "Identifier (dct:identifier)",             "mandatory"),
    ],
}


def _extras_value(metadata: dict, key: str) -> str:
    """Get value from CKAN extras list by key. Returns '' if missing or empty."""
    for item in metadata.get("extras", []):
        if item.get("key") == key:
            return (item.get("value") or "").strip()
    return ""


def detect_profile(metadata: dict, portal_url: str = "") -> str:
    """Heuristically detect DCAT-AP national profile."""
    # 1. Portal URL
    for pattern, profile in PORTAL_PROFILES:
        if pattern.search(portal_url):
            return profile
    # 2. Italian-specific: identifier follows istat_code:slug pattern
    identifier = _extras_value(metadata, "identifier")
    if re.match(r"^[a-z]_[a-z0-9]+:", identifier):
        return "DCAT-AP_IT"
    if _extras_value(metadata, "holder_name"):
        return "DCAT-AP_IT"
    # Fallback
    return "DCAT-AP_2x"


class MetadataValidator:
    """Validates CKAN package metadata for DCAT-AP compliance."""

    def __init__(self, metadata: dict, portal_url: str = "", report: QualityReport | None = None):
        self.meta = metadata
        self.portal_url = portal_url
        self.report = report or QualityReport(source=portal_url or metadata.get("name", "unknown"))
        self.profile = detect_profile(metadata, portal_url)
        self.report.profile = self.profile

    def run(self) -> QualityReport:
        self._phase5_metadata()
        return self.report

    # ── Phase 5 ──────────────────────────────────────────────────────────

    def _phase5_metadata(self) -> None:
        r = self.report
        p = PHASE5

        r.ok(p, "profile_detected", f"DCAT-AP profile detected: {self.profile}")

        score = 20  # start full, deduct

        # title
        title = (self.meta.get("title") or "").strip()
        if not title:
            r.major(p, "missing_title", "Title (dct:title) is missing",
                    fix="Add a clear, descriptive title")
            score -= 4
        elif len(title) < 10:
            r.minor(p, "short_title", f"Title is very short ({len(title)} chars): {title!r}",
                    fix="Expand the title to be more descriptive")
        else:
            r.ok(p, "title_ok", f"Title present: {title!r}")

        # description
        notes = (self.meta.get("notes") or "").strip()
        if not notes:
            r.major(p, "missing_description", "Description (dct:description) is missing",
                    fix="Add a description explaining the dataset content, coverage, and purpose")
            score -= 4
        elif len(notes) < 80:
            r.major(p, "short_description",
                    f"Description too short ({len(notes)} chars) — minimum 80 recommended",
                    fix="Expand: what data, time period, collection method, column meanings, caveats")
            score -= 2
        elif notes.strip() == title.strip():
            r.major(p, "description_equals_title",
                    "Description is identical to title — not a real description",
                    fix="Write a proper description explaining content, coverage, and purpose")
            score -= 3
        else:
            r.ok(p, "description_ok", f"Description present ({len(notes)} chars)")

        # publisher / organization
        org = self.meta.get("organization") or {}
        pub = org.get("title") or ""
        if not pub:
            r.major(p, "missing_publisher", "Publisher (dct:publisher) is missing",
                    fix="Assign the dataset to an organization in CKAN")
            score -= 4
        else:
            r.ok(p, "publisher_ok", f"Publisher: {pub!r}")

        # license
        lic = (self.meta.get("license_id") or self.meta.get("license_title") or "").strip()
        if not lic:
            r.major(p, "missing_license", "License (dct:license) is missing at dataset level",
                    fix="Add a license — CC BY 4.0 is common for EU open data")
            score -= 4
        else:
            r.ok(p, "license_ok", f"License: {lic!r}")

        # tags
        tags = self.meta.get("tags") or []
        if len(tags) < 3:
            r.minor(p, "few_tags",
                    f"Only {len(tags)} tag(s) — 3+ recommended for discoverability",
                    fix="Add relevant keywords describing topic, geography, and time period")
            score -= 1
        else:
            tag_names = [t.get("name", "") for t in tags]
            r.ok(p, "tags_ok", f"{len(tags)} tags: {', '.join(tag_names[:5])}")

        # dates
        for date_key in ("issued", "modified"):
            val = (self.meta.get(date_key) or _extras_value(self.meta, date_key)).strip()
            if not val:
                r.major(p, f"missing_{date_key}",
                        f"Date field '{date_key}' (dct:{date_key}) is missing or empty string",
                        fix=f"Set {date_key} to the actual date in ISO 8601 format: YYYY-MM-DD")
                score -= 2
            elif NON_ISO_DATE_RE.match(val):
                r.major(p, f"non_iso_{date_key}",
                        f"Field '{date_key}' is not ISO 8601: {val!r}",
                        fix=f"Convert to YYYY-MM-DD format")
                score -= 2
            elif not ISO_DATE_RE.match(val):
                r.minor(p, f"invalid_{date_key}",
                        f"Field '{date_key}' has unexpected format: {val!r}")
                score -= 1
            else:
                r.ok(p, f"{date_key}_ok", f"{date_key}: {val}")

        # update frequency
        freq = _extras_value(self.meta, "frequency") or _extras_value(self.meta, "accrualPeriodicity")
        if not freq:
            r.minor(p, "missing_frequency",
                    "Update frequency (dct:accrualPeriodicity) is missing",
                    fix="Set frequency: ANNUAL, MONTHLY, WEEKLY, DAILY, IRREGULAR, etc.")
        else:
            r.ok(p, "frequency_ok", f"Update frequency: {freq}")

        # temporal coverage
        tc = _extras_value(self.meta, "temporal_coverage")
        if not tc:
            r.minor(p, "missing_temporal_coverage",
                    "Temporal coverage (dct:temporal) is missing",
                    fix="Specify the time range covered by the dataset")

        # spatial coverage
        spatial = _extras_value(self.meta, "geographical_geonames_url") or \
                  _extras_value(self.meta, "spatial")
        if not spatial:
            r.minor(p, "missing_spatial",
                    "Spatial coverage (dct:spatial) is missing",
                    fix="Add a GeoNames URI or WKT bounding box")

        # language
        lang = _extras_value(self.meta, "language")
        if not lang:
            r.minor(p, "missing_language", "Language (dct:language) is missing",
                    fix="Add language code, e.g. 'ITA', 'ENG'")
        else:
            r.ok(p, "language_ok", f"Language: {lang}")

        # identifier
        identifier = _extras_value(self.meta, "identifier")
        if not identifier:
            r.minor(p, "missing_identifier", "Identifier (dct:identifier) is missing")
        else:
            r.ok(p, "identifier_ok", f"Identifier: {identifier!r}")

        # profile-specific extra fields
        extra_fields = PROFILE_EXTRA_FIELDS.get(self.profile, [])
        for extras_key, label, cardinality in extra_fields:
            val = _extras_value(self.meta, extras_key)
            if not val:
                if cardinality == "mandatory":
                    r.major(p, f"missing_{extras_key}",
                            f"[{self.profile}] Mandatory field missing: {label}",
                            fix=f"Add '{extras_key}' field to CKAN metadata")
                    score -= 3
                else:
                    r.minor(p, f"missing_{extras_key}",
                            f"[{self.profile}] Recommended field missing: {label}")

        # ── per-resource checks ───────────────────────────────────────────
        resources = self.meta.get("resources") or []
        for res in resources:
            res_name = res.get("name") or res.get("id") or "?"
            prefix = f"resource_{res.get('id', 'x')[:8]}"

            # format
            fmt = (res.get("format") or res.get("distribution_format") or "").strip()
            if not fmt:
                r.major(p, f"{prefix}_missing_format",
                        f"Resource '{res_name}': format (dct:format) is missing",
                        fix="Set format field: CSV, JSON, XML, etc.")
                score -= 1

            # MIME type
            mime = (res.get("mimetype") or "").strip()
            if not mime:
                r.minor(p, f"{prefix}_missing_mime",
                        f"Resource '{res_name}': MIME type (dcat:mediaType) is missing",
                        fix="Set mimetype: text/csv, application/json, etc.")

            # license on distribution
            res_lic = (res.get("license_id") or res.get("license") or "").strip()
            if not res_lic:
                r.major(p, f"{prefix}_missing_license",
                        f"Resource '{res_name}': license (dct:license) missing on distribution",
                        detail="DCAT-AP requires license on each distribution, not only at dataset level",
                        fix="Add license_id to the resource/distribution record")
                score -= 2

            # size
            size = res.get("size")
            try:
                size_int = int(size or 0)
            except (TypeError, ValueError):
                size_int = 0
            if size_int == 0:
                r.minor(p, f"{prefix}_size_zero",
                        f"Resource '{res_name}': size is 0 or missing",
                        fix="Update byteSize after upload; ensure harvester captures file size")

            # URL
            url = (res.get("url") or "").strip()
            if not url:
                r.major(p, f"{prefix}_missing_url",
                        f"Resource '{res_name}': URL is missing",
                        fix="Add the download URL for this resource")
            elif UNSTABLE_URL_RE.search(url):
                r.major(p, f"{prefix}_unstable_url",
                        f"Resource '{res_name}': unstable URL (cloud storage or short link)",
                        detail=url,
                        fix="Use permanent institutional hosting; avoid Google Sheets, Dropbox, bit.ly, etc.")
                score -= 2

        self.report.dimensions.append(
            ScoreDimension("Metadata completeness", 20, max(0, score))
        )


class AccessibilityChecker:
    """
    Checks whether all resource URLs are reachable.
    Run this BEFORE downloading files — quick HTTP HEAD checks only.
    """

    def __init__(self, metadata: dict, report: QualityReport, timeout: float = 15.0):
        self.meta = metadata
        self.report = report
        self.timeout = timeout

    def run(self) -> None:
        resources = self.meta.get("resources") or []
        if not resources:
            self.report.major(PHASE5, "no_resources",
                              "Dataset has no resources/distributions",
                              fix="Add at least one downloadable distribution")
            self.report.dimensions.append(ScoreDimension("Accessibility", 20, 0))
            return

        score = 20
        accessible = 0

        with httpx.Client(follow_redirects=True, timeout=self.timeout) as client:
            for res in resources:
                url = (res.get("url") or "").strip()
                name = res.get("name") or url[:60]
                prefix = f"access_{res.get('id', 'x')[:8]}"

                if not url:
                    continue

                if UNSTABLE_URL_RE.search(url):
                    # already flagged in metadata phase — just count as accessible if reachable
                    pass

                try:
                    resp = client.head(url, timeout=self.timeout)
                    # Some servers return 405 for HEAD but 200 for GET — try GET on 4xx/5xx
                    if resp.status_code >= 400:
                        resp = client.get(url, timeout=self.timeout)

                    if resp.status_code == 200:
                        accessible += 1
                        self.report.ok(PHASE5, f"{prefix}_accessible",
                                       f"Resource accessible: {name!r} (HTTP 200)")
                    else:
                        score -= 5
                        self.report.blocker(PHASE5, f"{prefix}_not_accessible",
                                            f"Resource not accessible: {name!r} (HTTP {resp.status_code})",
                                            detail=url,
                                            fix=f"Fix the URL or restore the file. HTTP {resp.status_code}.")
                except httpx.TimeoutException:
                    score -= 5
                    self.report.major(PHASE5, f"{prefix}_timeout",
                                      f"Resource timed out after {self.timeout}s: {name!r}",
                                      detail=url,
                                      fix="Check server availability; increase timeout or fix hosting")
                except Exception as e:
                    score -= 3
                    self.report.major(PHASE5, f"{prefix}_error",
                                      f"Resource check failed: {name!r}: {e}",
                                      detail=url)

        total = len([r for r in resources if r.get("url")])
        self.report.ok(PHASE5, "accessibility_summary",
                       f"Accessibility: {accessible}/{total} resources reachable")

        if accessible == 0 and total > 0:
            score = 0  # all inaccessible = blocker-level
        self.report.dimensions.append(ScoreDimension("Accessibility", 20, max(0, score)))


class ConsistencyChecker:
    """Phase 6: cross-validation between metadata and actual file content."""

    def __init__(self, metadata: dict, csv_path, report: QualityReport):
        self.meta = metadata
        self.csv_path = csv_path
        self.report = report

    def run(self) -> None:
        from charset_normalizer import from_bytes
        r = self.report
        p = PHASE6

        # Declared encoding vs actual
        declared_enc = (_extras_value(self.meta, "encoding") or "").lower().replace("-", "")
        if declared_enc and self.csv_path:
            from pathlib import Path
            with open(self.csv_path, "rb") as f:
                raw = f.read(65536)
            best = from_bytes(raw).best()
            actual = (best.encoding if best else "").lower().replace("-", "")
            if declared_enc and actual and declared_enc not in actual and actual not in declared_enc:
                r.major(p, "encoding_mismatch",
                        f"Declared encoding ({declared_enc!r}) ≠ actual ({actual!r})",
                        fix=f"Update metadata encoding field or re-encode the file to {declared_enc}")
            else:
                r.ok(p, "encoding_consistent", f"Encoding consistent: {actual!r}")

        # Temporal coverage vs update frequency consistency (heuristic)
        freq = _extras_value(self.meta, "frequency")
        modified = _extras_value(self.meta, "modified")
        if freq and modified and ISO_DATE_RE.match(modified):
            try:
                mod_date = datetime.strptime(modified, "%Y-%m-%d").date()
                today = date.today()
                delta_days = (today - mod_date).days
                freq_thresholds = {
                    "DAILY": 7, "WEEKLY": 30, "MONTHLY": 90,
                    "QUARTERLY": 180, "ANNUAL": 730, "BIENNIAL": 1460,
                }
                threshold = freq_thresholds.get(freq.upper())
                if threshold and delta_days > threshold:
                    r.minor(p, "stale_data",
                            f"Data may be stale: declared frequency {freq!r}, "
                            f"last modified {delta_days} days ago (>{threshold} days)",
                            fix="Update the dataset or revise the declared update frequency")
                else:
                    r.ok(p, "freshness_ok",
                         f"Freshness OK: {freq}, last modified {delta_days} days ago")
            except ValueError:
                pass
