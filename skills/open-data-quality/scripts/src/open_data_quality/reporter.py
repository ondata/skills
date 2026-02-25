"""
Render a QualityReport to the terminal (Rich) or as plain Markdown.
"""

from __future__ import annotations

from datetime import date

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import QualityReport, Severity

_SEV_STYLE = {
    Severity.BLOCKER: "bold red",
    Severity.MAJOR:   "bold yellow",
    Severity.MINOR:   "cyan",
    Severity.OK:      "green",
}

_SEV_LABEL = {
    Severity.BLOCKER: "⛔ BLOCKER",
    Severity.MAJOR:   "⚠️  MAJOR",
    Severity.MINOR:   "ℹ️  MINOR",
    Severity.OK:      "✅ OK",
}


def render_terminal(report: QualityReport, console: Console | None = None, show_ok: bool = False) -> None:
    """Print a rich-formatted report to the terminal."""
    con = console or Console()

    # ── header ──────────────────────────────────────────────────────────
    score_colour = "red" if report.score_pct < 50 else ("yellow" if report.score_pct < 75 else "green")
    header = (
        f"[bold]Open Data Quality Report[/bold]\n"
        f"Source:   {report.source}\n"
        f"Profile:  {report.profile}\n"
        f"Date:     {date.today().isoformat()}\n"
        f"Score:    [{score_colour}]{report.score_pct}/100[/{score_colour}] "
        f"({report.total_score}/{report.max_score} pts)"
    )
    con.print(Panel(header, expand=False, border_style="bold blue"))

    # ── findings grouped by severity ────────────────────────────────────
    for sev in (Severity.BLOCKER, Severity.MAJOR, Severity.MINOR):
        findings = [f for f in report.findings if f.severity == sev]
        if not findings:
            continue
        label = _SEV_LABEL[sev]
        style = _SEV_STYLE[sev]
        con.print(f"\n[{style}]{label} ({len(findings)})[/{style}]")
        for f in findings:
            con.print(f"  [{style}]•[/{style}] [{style}][{f.phase}][/{style}] {f.message}")
            if f.detail:
                con.print(f"    [dim]Detail:[/dim] {f.detail}")
            if f.fix:
                con.print(f"    [dim]Fix:[/dim] [italic]{f.fix}[/italic]")

    # ── OK findings (optional) ──────────────────────────────────────────
    if show_ok:
        ok_findings = [f for f in report.findings if f.severity == Severity.OK]
        if ok_findings:
            con.print("\n[green]✅ Passed checks[/green]")
            for f in ok_findings:
                con.print(f"  [green]•[/green] [{f.phase}] {f.message}")

    # ── score table ──────────────────────────────────────────────────────
    if report.dimensions:
        con.print()
        tbl = Table(title="Score breakdown", box=box.SIMPLE_HEAVY, show_header=True)
        tbl.add_column("Dimension", style="bold")
        tbl.add_column("Score", justify="right")
        tbl.add_column("Max",   justify="right")
        tbl.add_column("Notes")
        for dim in report.dimensions:
            colour = "red" if dim.score < dim.max_score * 0.5 else (
                "yellow" if dim.score < dim.max_score else "green"
            )
            tbl.add_row(
                dim.name,
                f"[{colour}]{dim.score}[/{colour}]",
                str(dim.max_score),
                "; ".join(dim.notes) if dim.notes else "",
            )
        con.print(tbl)

    # ── summary verdict ──────────────────────────────────────────────────
    if report.has_blockers:
        verdict = "[bold red]⛔ UNUSABLE — blocker issues must be resolved first.[/bold red]"
    elif report.majors:
        verdict = f"[bold yellow]⚠️  USABLE WITH CAUTION — {len(report.majors)} major issue(s) to fix.[/bold yellow]"
    else:
        verdict = "[bold green]✅ GOOD — minor or no issues detected.[/bold green]"
    con.print(f"\n{verdict}\n")


def render_markdown(report: QualityReport, show_ok: bool = False) -> str:
    """Return the report as a Markdown string (for --output-md or piping)."""
    lines: list[str] = []
    score_label = f"{report.score_pct}/100 ({report.total_score}/{report.max_score} pts)"

    lines += [
        "# Open Data Quality Report",
        f"",
        f"| | |",
        f"|---|---|",
        f"| **Source** | {report.source} |",
        f"| **DCAT-AP profile** | {report.profile} |",
        f"| **Validated** | {date.today().isoformat()} |",
        f"| **Score** | {score_label} |",
        "",
    ]

    for sev, emoji in ((Severity.BLOCKER, "⛔"), (Severity.MAJOR, "⚠️"), (Severity.MINOR, "ℹ️")):
        findings = [f for f in report.findings if f.severity == sev]
        if not findings:
            continue
        lines.append(f"## {emoji} {sev.value.title()} issues ({len(findings)})")
        lines.append("")
        for f in findings:
            lines.append(f"**[{f.phase}]** {f.message}")
            if f.detail:
                lines.append(f"- *Detail:* `{f.detail}`")
            if f.fix:
                lines.append(f"- *Fix:* `{f.fix}`")
            lines.append("")

    if show_ok:
        ok = [f for f in report.findings if f.severity == Severity.OK]
        if ok:
            lines.append("## ✅ Passed checks")
            lines.append("")
            for f in ok:
                lines.append(f"- [{f.phase}] {f.message}")
            lines.append("")

    if report.dimensions:
        lines += [
            "## Score breakdown",
            "",
            "| Dimension | Score | Max |",
            "|-----------|------:|----:|",
        ]
        for dim in report.dimensions:
            lines.append(f"| {dim.name} | {dim.score} | {dim.max_score} |")
        lines.append("")

    if report.has_blockers:
        lines.append("> ⛔ **UNUSABLE** — blocker issues must be resolved first.")
    elif report.majors:
        lines.append(f"> ⚠️ **USABLE WITH CAUTION** — {len(report.majors)} major issue(s) to fix.")
    else:
        lines.append("> ✅ **GOOD** — minor or no issues detected.")

    return "\n".join(lines)
