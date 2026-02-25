"""
odq-ckan — validate a CKAN dataset (metadata + resources + optional CSV content).

Usage examples:
  # Metadata + accessibility only (no file download)
  uvx --from open-data-quality odq-ckan https://dati.gov.it/opendata DATASET-ID-OR-SLUG

  # Also download and validate the first CSV resource
  uvx --from open-data-quality odq-ckan https://dati.gov.it/opendata DATASET-ID --download

  # Output
  uvx --from open-data-quality odq-ckan https://portal.example.org DATASET-ID \\
      --download --output-json report.json --output-md report.md

  # Skip accessibility checks (faster, offline)
  uvx --from open-data-quality odq-ckan https://portal.example.org DATASET-ID --no-check-urls
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Annotated, Optional

import httpx
import typer
from rich.console import Console

from .metadata_validator import AccessibilityChecker, ConsistencyChecker, MetadataValidator
from .csv_validator import CsvValidator
from .models import QualityReport
from .reporter import render_markdown, render_terminal

app = typer.Typer(
    name="odq-ckan",
    help="Open data quality validator for CKAN portal datasets (phases 5–6 + optional CSV).",
    add_completion=False,
)


def _fetch_ckan_metadata(portal_url: str, dataset_id: str, console: Console) -> dict:
    """Call CKAN package_show API and return the result dict."""
    base = portal_url.rstrip("/")
    url = f"{base}/api/3/action/package_show?id={dataset_id}"
    console.print(f"[dim]Fetching metadata:[/dim] {url}")
    try:
        resp = httpx.get(url, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPStatusError as e:
        console.print(f"[bold red]HTTP error fetching metadata:[/bold red] {e}")
        raise typer.Exit(code=3)
    except Exception as e:
        console.print(f"[bold red]Error fetching metadata:[/bold red] {e}")
        raise typer.Exit(code=3)

    if not data.get("success"):
        msg = data.get("error", {}).get("message", "unknown error")
        console.print(f"[bold red]CKAN API error:[/bold red] {msg}")
        raise typer.Exit(code=3)

    return data["result"]


def _pick_csv_resource(metadata: dict) -> dict | None:
    """Return the first CSV resource, or None."""
    for res in metadata.get("resources") or []:
        fmt = (res.get("format") or res.get("distribution_format") or "").upper()
        mime = (res.get("mimetype") or "").lower()
        url = res.get("url") or ""
        if fmt == "CSV" or "csv" in mime or url.lower().endswith(".csv"):
            return res
    return None


def _download_csv(url: str, console: Console, timeout: float = 60.0) -> Path | None:
    """Download a resource to a temp file. Returns path or None on failure."""
    console.print(f"[dim]Downloading:[/dim] {url}")
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=timeout) as resp:
            resp.raise_for_status()
            suffix = ".csv"
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            for chunk in resp.iter_bytes(chunk_size=65536):
                tmp.write(chunk)
            tmp.close()
            size_mb = Path(tmp.name).stat().st_size / 1_048_576
            console.print(f"[dim]Downloaded:[/dim] {size_mb:.1f} MB → {tmp.name}")
            return Path(tmp.name)
    except Exception as e:
        console.print(f"[bold yellow]Warning:[/bold yellow] Could not download resource: {e}")
        return None


@app.command()
def main(
    portal_url: Annotated[str, typer.Argument(help="Base URL of the CKAN portal (e.g. https://dati.gov.it/opendata)")],
    dataset_id: Annotated[str, typer.Argument(help="Dataset ID or slug (e.g. some-dataset-slug)")],
    download: Annotated[bool, typer.Option("--download", help="Download and validate the first CSV resource")] = False,
    check_urls: Annotated[bool, typer.Option("--check-urls/--no-check-urls", help="Check resource URL accessibility")] = True,
    show_ok: Annotated[bool, typer.Option("--show-ok", help="Also print passed checks")] = False,
    output_json: Annotated[Optional[Path], typer.Option("--output-json")] = None,
    output_md: Annotated[Optional[Path], typer.Option("--output-md")] = None,
    sample_rows: Annotated[int, typer.Option("--sample-rows", help="Max rows for CSV content checks")] = 50_000,
    quiet: Annotated[bool, typer.Option("--quiet", "-q")] = False,
) -> None:
    console = Console()

    # ── 1. Fetch CKAN metadata ──────────────────────────────────────────
    metadata = _fetch_ckan_metadata(portal_url, dataset_id, console)
    source_label = f"{portal_url}/dataset/{dataset_id}"

    report = QualityReport(source=source_label)
    report.metadata = metadata

    # ── 2. Accessibility check (HTTP HEAD on each resource URL) ─────────
    if check_urls:
        if not quiet:
            console.print("[dim]Checking resource URLs...[/dim]")
        checker = AccessibilityChecker(metadata, report)
        checker.run()
    else:
        console.print("[dim]URL checks skipped (--no-check-urls)[/dim]")

    # ── 3. Metadata / DCAT-AP compliance ────────────────────────────────
    if not quiet:
        console.print("[dim]Validating metadata...[/dim]")
    MetadataValidator(metadata, portal_url=portal_url, report=report).run()

    # ── 4. Optional: download + full CSV validation ──────────────────────
    csv_path: Path | None = None
    if download:
        csv_res = _pick_csv_resource(metadata)
        if csv_res:
            csv_url = csv_res.get("url") or ""
            csv_path = _download_csv(csv_url, console)
            if csv_path:
                if not quiet:
                    console.print("[dim]Running CSV validation...[/dim]")
                csv_report = CsvValidator(csv_path, sample_rows=sample_rows).run()
                # Merge CSV findings into main report
                report.findings.extend(csv_report.findings)
                report.dimensions.extend(csv_report.dimensions)
                # Phase 6: consistency cross-check
                ConsistencyChecker(metadata, csv_path, report).run()
                # Clean up temp file
                try:
                    csv_path.unlink()
                except Exception:
                    pass
        else:
            console.print("[yellow]No CSV resource found — skipping file validation[/yellow]")
    else:
        # Still add CSV score dimensions as N/A
        from .models import ScoreDimension
        for name, pts in [("File format compliance", 15), ("Data structure quality", 20), ("Data content quality", 25)]:
            report.dimensions.append(ScoreDimension(name, pts, pts, notes=["Not checked — use --download"]))

    # ── 5. Render report ─────────────────────────────────────────────────
    if not quiet:
        render_terminal(report, console=console, show_ok=show_ok)

    if output_json:
        output_json.write_text(report.to_json(), encoding="utf-8")
        if not quiet:
            console.print(f"[dim]JSON written to:[/dim] {output_json}")

    if output_md:
        output_md.write_text(render_markdown(report, show_ok=show_ok), encoding="utf-8")
        if not quiet:
            console.print(f"[dim]Markdown written to:[/dim] {output_md}")

    # Exit codes
    if report.has_blockers:
        raise typer.Exit(code=2)
    elif report.majors:
        raise typer.Exit(code=1)
    else:
        raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
