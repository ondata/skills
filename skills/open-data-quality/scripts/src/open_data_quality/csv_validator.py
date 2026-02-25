"""
CSV validator — Phases 0–4.

All heavy lifting done via DuckDB in-process; no shell subprocesses.

Key design note: DuckDB renames headers that start with digits (e.g. '2020' → 'column1').
We always read raw headers directly from the file for structural checks (phases 1–2),
and use DuckDB column names only for SQL queries on content (phases 3–4).
"""

from __future__ import annotations

import csv as csvmod
import io
import re
from pathlib import Path
import chardet
import duckdb

from .models import QualityReport, ScoreDimension, Severity

# ── multilingual constants ────────────────────────────────────────────────────

PLACEHOLDER_VALUES = frozenset({
    # universal
    "n/a", "na", "null", "none", "-", "--", "/", "?", "",
    # English
    "not available", "not applicable", "unknown", "missing",
    # Italian
    "n.d.", "nd", "assente", "non disponibile",
    # French
    "n.r.", "nr", "inconnu", "non disponible",
    # German
    "k.a.", "ka", "unbekannt", "nicht verfügbar",
    # Spanish / Portuguese
    "n.a.", "desconocido", "no disponible", "não disponível", "indisponível",
    # Dutch
    "onbekend", "niet beschikbaar",
})

AGGREGATE_KEYWORDS = re.compile(
    r"\b(totale?|subtotale?|grand total|total général|gesamt|insgesamt"
    r"|suma total?|somma|subtotal|average|media|mittelwert|gemiddelde)\b",
    re.IGNORECASE,
)

MONTH_NAMES = re.compile(
    r"^(jan|feb|m[aä]r|apr|ma[yi]|jun|jul|aug|sep|o[ck]t|nov|de[cz]"
    r"|gen|fev|avr|mai|jui|aou|ago|set|ott|ene|abr|dic)",
    re.IGNORECASE,
)

YEAR_COLUMN = re.compile(r"^(19|20)\d{2}$")

FOOTNOTE_PAT = re.compile(r"\(\d+\)|\(\*\)|\d+\s*\*")

# codes columns heuristic
CODE_COL_PAT = re.compile(
    r"(code|cod_|_code|_cod|nuts|lau|iso_|zip|postal|istat|ags|insee"
    r"|gemeente|municipality|commune|gemeinde|municipio)",
    re.IGNORECASE,
)


# ── file-level helpers ────────────────────────────────────────────────────────

def _detect_encoding(path: Path) -> tuple[str, float]:
    with open(path, "rb") as f:
        raw = f.read(65536)
    result = chardet.detect(raw)
    return (result.get("encoding") or "unknown").lower(), result.get("confidence", 0.0)


def _has_bom(path: Path) -> bool:
    with open(path, "rb") as f:
        return f.read(3) == b"\xef\xbb\xbf"


def _has_crlf(path: Path) -> bool:
    with open(path, "rb") as f:
        return b"\r\n" in f.read(16384)


def _read_raw_headers(path: Path, separator: str = ",") -> list[str]:
    """Read column names directly from the first line of the file (no DuckDB rename)."""
    try:
        with open(path, "rb") as f:
            # Skip BOM if present
            start = f.read(3)
            if start != b"\xef\xbb\xbf":
                f.seek(0)
            first_line = f.readline().decode("utf-8", errors="replace").rstrip("\r\n")
        reader = csvmod.reader(io.StringIO(first_line), delimiter=separator)
        return next(reader, [])
    except Exception:
        return []


def _tail_lines(path: Path, n: int = 10) -> list[str]:
    try:
        lines = path.read_text(errors="replace").splitlines()
        return lines[-n:]
    except Exception:
        return []


def _head_lines(path: Path, n: int = 200) -> list[str]:
    try:
        lines = []
        with open(path, errors="replace") as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                lines.append(line.rstrip("\r\n"))
        return lines
    except Exception:
        return []


# ── main validator ────────────────────────────────────────────────────────────

class CsvValidator:
    """Runs phases 0–4 on a single CSV file. Returns a QualityReport."""

    P0 = "phase0_blockers"
    P1 = "phase1_structure"
    P2 = "phase2_columns"
    P3 = "phase3_content"
    P4 = "phase4_codes"

    def __init__(self, csv_path: Path, sample_rows: int = 50_000):
        self.path = Path(csv_path)
        self.sample_rows = sample_rows
        self.report = QualityReport(source=str(csv_path))
        self._con: duckdb.DuckDBPyConnection | None = None
        self._duckdb_columns: list[dict] = []   # DuckDB-renamed column names + types
        self._raw_headers: list[str] = []       # original headers from file
        self._row_count: int = 0
        self._separator: str = ","

    def run(self) -> QualityReport:
        self._phase0_blockers()
        if self.report.has_blockers:
            self.report.dimensions.append(ScoreDimension("File format compliance", 15, 0))
            self.report.dimensions.append(ScoreDimension("Data structure quality", 20, 0))
            self.report.dimensions.append(ScoreDimension("Data content quality", 25, 0))
            return self.report
        self._con = duckdb.connect()
        try:
            self._phase1_structure()
            self._phase2_columns()
            self._phase3_content()
            self._phase4_codes()
        finally:
            self._con.close()
        self._compute_scores()
        return self.report

    # ── Phase 0: blockers ────────────────────────────────────────────────

    def _phase0_blockers(self) -> None:
        r, p = self.report, self.P0

        if not self.path.exists():
            r.blocker(p, "file_not_found", f"File not found: {self.path}"); return
        if self.path.stat().st_size == 0:
            r.blocker(p, "file_empty", "File is empty (0 bytes)"); return

        with open(self.path, "rb") as f:
            chunk = f.read(8192)
        if b"\x00" in chunk:
            r.blocker(p, "file_binary", "File appears binary (null bytes) — not a CSV"); return

        try:
            con = duckdb.connect()
            row = con.execute(
                f"SELECT COUNT(*) FROM read_csv_auto('{self.path}', sample_size=1000)"
            ).fetchone()
            rows = row[0] if row else 0
            cols_info = con.execute(
                f"DESCRIBE SELECT * FROM read_csv_auto('{self.path}', sample_size=1)"
            ).fetchall()
            cols = len(cols_info)
            con.close()
        except Exception as e:
            r.blocker(p, "csv_unparseable", f"DuckDB cannot parse file: {e}",
                      fix="Check separator, quoting, and encoding"); return

        if rows == 0:
            r.blocker(p, "no_data_rows", "No data rows (header only or empty)"); return
        if cols <= 1:
            r.blocker(p, "trivial_structure", f"Only {cols} column(s) — check separator",
                      fix="Verify that the correct separator is used"); return

        r.ok(p, "parseable", f"Parsed OK: {rows:,} rows × {cols} columns")
        self._row_count = rows

    # ── Phase 1: file structure ──────────────────────────────────────────

    def _phase1_structure(self) -> None:
        r, p = self.report, self.P1

        # Encoding
        enc, conf = _detect_encoding(self.path)
        is_utf8 = enc in ("utf-8", "utf-8-sig", "ascii", "us-ascii")
        if is_utf8:
            r.ok(p, "encoding_utf8", f"Encoding: {enc} ({conf:.0%} confidence)")
        else:
            r.major(p, "encoding_not_utf8",
                    f"Encoding detected as {enc!r} ({conf:.0%} confidence) — expected UTF-8",
                    fix=f"iconv -f {enc} -t UTF-8 input.csv > output.csv")

        # BOM
        if _has_bom(self.path):
            r.major(p, "bom_present", "UTF-8 BOM present — causes parse errors in many tools",
                    fix="sed '1s/^\\xef\\xbb\\xbf//' input.csv > output.csv")
        else:
            r.ok(p, "no_bom", "No BOM")

        # Line endings
        if _has_crlf(self.path):
            r.minor(p, "crlf_endings", "Windows CRLF line endings — prefer LF",
                    fix="dos2unix input.csv")
        else:
            r.ok(p, "lf_endings", "LF line endings (Unix-style)")

        # Separator detection via DuckDB sniff_csv
        try:
            cur = self._con.execute(f"SELECT * FROM sniff_csv('{self.path}')")
            col_idx = {d[0]: i for i, d in enumerate(cur.description)}
            row = cur.fetchone()
            if row:
                self._separator = str(row[col_idx.get("Delimiter", 0)] or ",")
                if not row[col_idx.get("HasHeader", 0)]:
                    r.major(p, "no_header", "No header row detected",
                            fix="Add a descriptive header row as the first line")
        except Exception:
            self._separator = ","

        # DuckDB schema (renamed columns)
        schema = self._con.execute(
            f"DESCRIBE SELECT * FROM read_csv_auto('{self.path}')"
        ).fetchall()
        self._duckdb_columns = [{"name": row[0], "type": row[1]} for row in schema]

        # Raw headers from file (preserves original names, including digit-only like '2020')
        self._raw_headers = _read_raw_headers(self.path, self._separator)

        ncols = len(self._raw_headers) or len(self._duckdb_columns)
        r.ok(p, "separator", f"Separator: {self._separator!r}")
        r.ok(p, "dimensions", f"{self._row_count:,} rows × {ncols} columns")

    # ── Phase 2: columns & structure ─────────────────────────────────────

    def _phase2_columns(self) -> None:
        r, p = self.report, self.P2

        # Use raw headers for structural/naming checks
        names = self._raw_headers or [c["name"] for c in self._duckdb_columns]

        # Duplicate column names
        seen: dict[str, int] = {}
        for n in names:
            seen[n] = seen.get(n, 0) + 1
        dupes = [n for n, c in seen.items() if c > 1]
        if dupes:
            r.major(p, "duplicate_columns", f"Duplicate column names: {dupes}",
                    fix="Rename duplicates before publishing")
        else:
            r.ok(p, "no_duplicate_columns", "No duplicate column names")

        # Problematic column names
        bad = []
        for name in names:
            if " " in name:
                bad.append(f"{name!r} (space)")
            elif re.search(r"[^a-zA-Z0-9_À-ÿ\-]", name):
                bad.append(f"{name!r} (special chars)")
            elif re.match(r"^\d", name):
                bad.append(f"{name!r} (starts with digit)")
        if bad:
            r.minor(p, "bad_column_names",
                    f"{len(bad)} column(s) with non-SQL-friendly names",
                    detail=", ".join(bad[:5]) + ("…" if len(bad) > 5 else ""),
                    fix="Rename to snake_case: lowercase, no spaces, no special chars")
        else:
            r.ok(p, "column_names_ok", "All column names are SQL-friendly")

        # Wide format detection (uses RAW headers — DuckDB renames '2020' → 'column1')
        year_cols  = [n for n in names if YEAR_COLUMN.match(n)]
        month_cols = [n for n in names if MONTH_NAMES.match(n)]
        if len(year_cols) >= 3:
            r.major(p, "wide_format_years",
                    f"Wide format: {len(year_cols)} year columns ({year_cols[:4]}...)",
                    fix="UNPIVOT into (entity, year, value): DuckDB UNPIVOT or mlr reshape")
            # sniff_csv misreads year-as-header as no_header — suppress false positive
            r.suppress("no_header")
        elif len(month_cols) >= 3:
            r.major(p, "wide_format_months",
                    f"Wide format: {len(month_cols)} month columns ({month_cols[:4]}...)",
                    fix="UNPIVOT into (entity, month, value): DuckDB UNPIVOT or mlr reshape")
            r.suppress("no_header")
        else:
            r.ok(p, "no_wide_format", "No wide-format time-period columns")

        # Aggregate/total rows (last 10 lines)
        agg = [l for l in _tail_lines(self.path) if AGGREGATE_KEYWORDS.search(l)]
        if agg:
            r.major(p, "aggregate_rows",
                    f"{len(agg)} aggregate/total row(s) at end of file",
                    detail=agg[0][:100],
                    fix="Remove total rows; publish separate summary if needed")
        else:
            r.ok(p, "no_aggregate_rows", "No aggregate rows at end of file")

        # Footnote markers leaking from Excel (first 200 lines)
        fn = [l for l in _head_lines(self.path) if FOOTNOTE_PAT.search(l)]
        if fn:
            r.minor(p, "footnote_markers",
                    f"Footnote markers (*), (1) in {len(fn)} sampled line(s)",
                    detail=fn[0][:80],
                    fix="Remove markers; document notes in description or a separate column")

    # ── Phase 3: data types & content ────────────────────────────────────

    def _phase3_content(self) -> None:
        r, p = self.report, self.P3
        path = self.path
        sample = self.sample_rows

        # SUMMARIZE for null rates — pure DuckDB, no pandas
        try:
            cur = self._con.execute(
                f"SUMMARIZE SELECT * FROM read_csv_auto('{path}') LIMIT {sample}"
            )
            col_idx = {d[0]: i for i, d in enumerate(cur.description)}
            rows = cur.fetchall()
            r.ok(p, "summarize_ok", "DuckDB SUMMARIZE completed")
            self._check_null_rates(rows, col_idx, p)
        except Exception as e:
            r.minor(p, "summarize_failed", f"SUMMARIZE failed: {e}")

        # Verify the file can be loaded as all-varchar (needed for pattern checks)
        try:
            self._con.execute(
                f"SELECT COUNT(*) FROM read_csv_auto('{path}', all_varchar=true) LIMIT 1"
            ).fetchone()
        except Exception:
            r.minor(p, "varchar_load_failed", "Could not load data for content checks")
            return

        # ── Comma decimal separator ──────────────────────────────────────
        try:
            comma_rows = self._con.execute(f"""
                SELECT col, COUNT(*) AS hits, MIN(val) AS example
                FROM (UNPIVOT (
                    SELECT * FROM read_csv_auto('{path}', all_varchar=true) LIMIT {sample}
                ) ON COLUMNS(*) INTO NAME col VALUE val)
                WHERE regexp_matches(val, '^\\d+,\\d+$')
                GROUP BY col HAVING COUNT(*) >= 3
            """).fetchall()
        except Exception:
            comma_rows = []
        if comma_rows:
            r.major(p, "comma_decimal",
                    f"Comma decimal separator in {len(comma_rows)} column(s): {[row[0] for row in comma_rows]}",
                    detail="; ".join(f"{row[0]}: e.g. {row[2]!r}" for row in comma_rows[:3]),
                    fix="mlr --csv put 'for(k,v in $*){{if(v=~\"^[0-9]+,[0-9]+$\"){{$[k]=sub(v,\",\",\".\")}}}}' data.csv")
        else:
            r.ok(p, "no_comma_decimal", "No comma decimal separator detected")

        # ── Non-ISO date format ──────────────────────────────────────────
        try:
            date_rows = self._con.execute(f"""
                SELECT col, COUNT(*) AS hits, MIN(val) AS example
                FROM (UNPIVOT (
                    SELECT * FROM read_csv_auto('{path}', all_varchar=true) LIMIT {min(sample, 500)}
                ) ON COLUMNS(*) INTO NAME col VALUE val)
                WHERE regexp_matches(val, '^\\d{{1,2}}[/.]\\d{{1,2}}[/.]\\d{{4}}$')
                GROUP BY col HAVING COUNT(*) >= 2
            """).fetchall()
        except Exception:
            date_rows = []
        if date_rows:
            r.major(p, "non_iso_date",
                    f"Non-ISO date format in {len(date_rows)} column(s): {[row[0] for row in date_rows]}",
                    detail="; ".join(f"{row[0]}: e.g. {row[2]!r}" for row in date_rows[:3]),
                    fix="duckdb: strptime(col,'%d/%m/%Y')::DATE")
        else:
            r.ok(p, "iso_dates", "No non-ISO date formats detected")

        # ── Units in numeric cells ───────────────────────────────────────
        try:
            unit_rows = self._con.execute(f"""
                SELECT col, COUNT(*) AS hits, MIN(val) AS example
                FROM (UNPIVOT (
                    SELECT * FROM read_csv_auto('{path}', all_varchar=true) LIMIT {min(sample, 500)}
                ) ON COLUMNS(*) INTO NAME col VALUE val)
                WHERE regexp_matches(val, '^\\d+[.,]?\\d*\\s*(kg|km|EUR|%|ha|MW|GWh|tCO2|tn)\\s*$', 'i')
                GROUP BY col HAVING COUNT(*) >= 2
            """).fetchall()
        except Exception:
            unit_rows = []
        if unit_rows:
            r.major(p, "units_in_cells",
                    f"Units embedded in values in {len(unit_rows)} column(s)",
                    detail="; ".join(f"{row[0]}: {row[2]!r}" for row in unit_rows[:3]),
                    fix="Split into numeric value column + separate unit column")
        else:
            r.ok(p, "no_units_in_cells", "No units embedded in cell values")

        # ── Placeholder values ───────────────────────────────────────────
        ph_list = ", ".join(f"'{v}'" for v in PLACEHOLDER_VALUES)
        try:
            ph_rows = self._con.execute(f"""
                SELECT col, COUNT(*) AS n
                FROM (UNPIVOT (
                    SELECT * FROM read_csv_auto('{path}', all_varchar=true) LIMIT {sample}
                ) ON COLUMNS(*) INTO NAME col VALUE val)
                WHERE lower(trim(val)) IN ({ph_list})
                GROUP BY col HAVING COUNT(*) > 0
                ORDER BY n DESC LIMIT 10
            """).fetchall()
        except Exception:
            ph_rows = []
        if ph_rows:
            r.major(p, "placeholder_values",
                    f"Placeholder values (n/a, n.d., -, …) in {len(ph_rows)} column(s)",
                    detail=", ".join(f"{row[0]}({row[1]})" for row in ph_rows[:5]),
                    fix="Replace with proper NULL/empty; document missing-data policy")
        else:
            r.ok(p, "no_placeholder_values", "No placeholder values detected")

        # ── VARCHAR columns that look numeric (thousands separator) ───────
        varchar_typed = {c["name"] for c in self._duckdb_columns if c["type"] in ("VARCHAR", "TEXT")}
        if varchar_typed:
            col_filter = " OR ".join(f'col = {c!r}' for c in varchar_typed)
            try:
                num_rows = self._con.execute(f"""
                    SELECT col, COUNT(*) AS hits
                    FROM (UNPIVOT (
                        SELECT * FROM read_csv_auto('{path}', all_varchar=true) LIMIT 200
                    ) ON COLUMNS(*) INTO NAME col VALUE val)
                    WHERE ({col_filter})
                      AND regexp_matches(val, '^\\d{{1,3}}([.,]\\d{{3}})+$')
                    GROUP BY col HAVING COUNT(*) >= 5
                """).fetchall()
            except Exception:
                num_rows = []
            if num_rows:
                r.major(p, "numeric_as_varchar",
                        f"{len(num_rows)} column(s) are VARCHAR but contain numbers with thousands separator",
                        detail=", ".join(row[0] for row in num_rows[:5]),
                        fix="Remove thousands separator then cast to DOUBLE/BIGINT")

    def _check_null_rates(self, rows: list, col_idx: dict, phase: str) -> None:
        if not rows or "null_percentage" not in col_idx:
            return
        ci_name = col_idx["column_name"]
        ci_null = col_idx["null_percentage"]
        high = [(row[ci_name], row[ci_null]) for row in rows if (row[ci_null] or 0) > 5]
        if high:
            detail = ", ".join(f"{name}({pct:.1f}%)" for name, pct in high)
            self.report.major(phase, "high_null_rate",
                    f"{len(high)} column(s) with >5% null values",
                    detail=detail,
                    fix="Document missing-data policy; consider imputation or flagging")

    # ── Phase 4: administrative codes ────────────────────────────────────

    def _phase4_codes(self) -> None:
        r, p = self.report, self.P4

        # Use raw headers for name detection
        all_names = self._raw_headers or [c["name"] for c in self._duckdb_columns]
        code_cols = [n for n in all_names if CODE_COL_PAT.search(n)]

        if not code_cols:
            r.ok(p, "no_code_columns", "No administrative code columns detected")
            return

        # Load only those columns (use DuckDB names for the query, raw names for display)
        # Map raw→duckdb names via position
        raw_to_duck = {}
        duck_names = [c["name"] for c in self._duckdb_columns]
        for i, rn in enumerate(self._raw_headers):
            if i < len(duck_names):
                raw_to_duck[rn] = duck_names[i]

        issues: list[str] = []
        for raw_col in code_cols[:10]:
            duck_col = raw_to_duck.get(raw_col, raw_col)
            try:
                values = [
                    str(row[0])
                    for row in self._con.execute(
                        f"SELECT \"{duck_col}\"::VARCHAR FROM read_csv_auto('{self.path}', all_varchar=true) "
                        f"WHERE \"{duck_col}\" IS NOT NULL LIMIT 5000"
                    ).fetchall()
                    if row[0] is not None
                ]
            except Exception:
                continue

            col_lower = raw_col.lower()

            # NUTS check
            if "nuts" in col_lower:
                bad = [v for v in values if not re.match(r"^[A-Z]{2}[0-9A-Z]{1,3}$", v)]
                if bad:
                    issues.append(f"{raw_col}: {len(bad)} values don't match NUTS (e.g. {bad[0]!r})")

            # ISTAT municipality (IT): must be 6 digits
            if re.search(r"(istat|comune|municipal)", col_lower):
                short = [v for v in values if re.match(r"^\d{1,5}$", v)]
                bad = [v for v in values if not re.match(r"^\d{6}$", v)]
                if short:
                    issues.append(f"{raw_col}: {len(short)} values look like ISTAT missing leading zeros (e.g. {short[0]!r})")
                elif bad:
                    issues.append(f"{raw_col}: {len(bad)} values not 6-digit ISTAT (e.g. {bad[0]!r})")

            # ISO 3166-1 alpha-2 country
            if re.search(r"(country_code|iso_country|nation)", col_lower):
                bad = [v for v in values if not re.match(r"^[A-Z]{2}$", v)]
                if bad:
                    issues.append(f"{raw_col}: {len(bad)} values not 2-letter ISO country code (e.g. {bad[0]!r})")

        if issues:
            r.major(p, "invalid_reference_codes",
                    f"Potential issues in {len(issues)} code column(s)",
                    detail="; ".join(issues[:3]),
                    fix="Validate against reference tables; use LPAD() to restore leading zeros")
        else:
            r.ok(p, "reference_codes_ok", f"Reference code columns look well-formed: {code_cols[:5]}")

    # ── scoring ───────────────────────────────────────────────────────────

    def _compute_scores(self) -> None:
        r = self.report
        codes = {f.code for f in r.findings if f.severity != Severity.OK}

        # File format (15 pts)
        fmt = 15
        if "encoding_not_utf8" in codes: fmt -= 10
        if "bom_present"        in codes: fmt -= 5
        if "crlf_endings"       in codes: fmt -= 3
        if "no_header"          in codes: fmt -= 3
        r.dimensions.append(ScoreDimension("File format compliance", 15, max(0, fmt)))

        # Data structure (20 pts)
        struct = 20
        if "wide_format_years"   in codes: struct -= 5
        if "wide_format_months"  in codes: struct -= 5
        if "duplicate_columns"   in codes: struct -= 5
        if "aggregate_rows"      in codes: struct -= 5
        if "bad_column_names"    in codes: struct -= 3
        if "footnote_markers"    in codes: struct -= 2
        r.dimensions.append(ScoreDimension("Data structure quality", 20, max(0, struct)))

        # Data content (25 pts)
        content = 25
        if "comma_decimal"         in codes: content -= 5
        if "non_iso_date"          in codes: content -= 5
        if "high_null_rate"        in codes: content -= 5
        if "units_in_cells"        in codes: content -= 3
        if "placeholder_values"    in codes: content -= 3
        if "invalid_reference_codes" in codes: content -= 4
        if "numeric_as_varchar"    in codes: content -= 2
        r.dimensions.append(ScoreDimension("Data content quality", 25, max(0, content)))
