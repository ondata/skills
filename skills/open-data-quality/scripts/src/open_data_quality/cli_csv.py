"""
odq-csv — validate a local CSV file (phases 0–4).

Usage examples:
  uvx --from open-data-quality odq-csv data.csv
  uvx --from open-data-quality odq-csv data.csv --show-ok
  uvx --from open-data-quality odq-csv data.csv --output-json report.json
  uvx --from open-data-quality odq-csv data.csv --output-md  report.md
  uvx --from open-data-quality odq-csv data.csv --sample-rows 100000
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from .csv_validator import CsvValidator
from .reporter import render_markdown, render_terminal

def _to_snake(name: str) -> str:
    """Convert a filename stem to snake_case for the auto report filename."""
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    return name or "report"


app = typer.Typer(
    name="odq-csv",
    help="Open data quality validator for CSV files (phases 0–4).",
    add_completion=False,
)


@app.command()
def main(
    csv_file: Annotated[Path, typer.Argument(help="Path to the CSV file to validate")],
    show_ok: Annotated[bool, typer.Option("--show-ok", help="Also print passed checks")] = False,
    output_json: Annotated[Optional[Path], typer.Option("--output-json", help="Write JSON report to file")] = None,
    output_md: Annotated[Optional[Path], typer.Option("--output-md", help="Write Markdown report to file")] = None,
    sample_rows: Annotated[int, typer.Option("--sample-rows", help="Max rows to sample for content checks")] = 50_000,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Suppress terminal output (useful with --output-*)")] = False,
) -> None:
    console = Console(stderr=False)

    if not quiet:
        console.print(f"[dim]Validating:[/dim] {csv_file}")

    validator = CsvValidator(csv_path=csv_file, sample_rows=sample_rows)
    report = validator.run()

    if not quiet:
        render_terminal(report, console=console, show_ok=show_ok)

    if output_json:
        output_json.write_text(report.to_json(), encoding="utf-8")
        if not quiet:
            console.print(f"[dim]JSON report written to:[/dim] {output_json}")

    # Auto-write markdown report to ./open-data-quality/<name>.md
    auto_md_dir = Path.cwd() / "open-data-quality"
    auto_md_dir.mkdir(exist_ok=True)
    auto_md_path = auto_md_dir / f"{_to_snake(csv_file.stem)}.md"
    auto_md_path.write_text(render_markdown(report, show_ok=show_ok), encoding="utf-8")
    if not quiet:
        console.print(f"[dim]Report:[/dim] {auto_md_path}")

    if output_md:
        output_md.write_text(render_markdown(report, show_ok=show_ok), encoding="utf-8")
        if not quiet:
            console.print(f"[dim]Markdown report written to:[/dim] {output_md}")

    # Exit codes:
    #   0 = no blockers and no major issues
    #   1 = major issues (usable with caution)
    #   2 = blocker (unusable)
    if report.has_blockers:
        raise typer.Exit(code=2)
    elif report.majors:
        raise typer.Exit(code=1)
    else:
        raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
