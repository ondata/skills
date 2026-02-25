"""
Data models shared across all validators.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    BLOCKER = "blocker"
    MAJOR   = "major"
    MINOR   = "minor"
    OK      = "ok"


SEVERITY_EMOJI = {
    Severity.BLOCKER: "⛔",
    Severity.MAJOR:   "⚠️ ",
    Severity.MINOR:   "ℹ️ ",
    Severity.OK:      "✅",
}


@dataclass
class Finding:
    severity: Severity
    phase: str
    code: str          # machine-readable identifier, e.g. "encoding_not_utf8"
    message: str       # human-readable description
    detail: str = ""   # optional: column name, value sample, line number
    fix: str = ""      # optional: one-liner fix suggestion

    def to_dict(self) -> dict:
        return {
            "severity": self.severity.value,
            "phase": self.phase,
            "code": self.code,
            "message": self.message,
            "detail": self.detail,
            "fix": self.fix,
        }


@dataclass
class ScoreDimension:
    name: str
    max_score: int
    score: int
    notes: list[str] = field(default_factory=list)

    @property
    def deduction(self) -> int:
        return self.max_score - self.score


@dataclass
class QualityReport:
    source: str                      # filename or CKAN URL
    profile: str = "unknown"         # DCAT-AP profile detected
    mode: str = "standard"           # quick / standard / full
    findings: list[Finding] = field(default_factory=list)
    dimensions: list[ScoreDimension] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)  # raw CKAN metadata if available

    # ── derived properties ────────────────────────────────────────────────

    @property
    def blockers(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.BLOCKER]

    @property
    def majors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.MAJOR]

    @property
    def minors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == Severity.MINOR]

    @property
    def total_score(self) -> int:
        return sum(d.score for d in self.dimensions)

    @property
    def max_score(self) -> int:
        return sum(d.max_score for d in self.dimensions)

    @property
    def score_pct(self) -> int:
        if self.max_score == 0:
            return 0
        return round(self.total_score * 100 / self.max_score)

    @property
    def has_blockers(self) -> bool:
        return len(self.blockers) > 0

    # ── helpers ───────────────────────────────────────────────────────────

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def ok(self, phase: str, code: str, message: str) -> None:
        self.findings.append(Finding(Severity.OK, phase, code, message))

    def blocker(self, phase: str, code: str, message: str, detail: str = "", fix: str = "") -> None:
        self.findings.append(Finding(Severity.BLOCKER, phase, code, message, detail, fix))

    def major(self, phase: str, code: str, message: str, detail: str = "", fix: str = "") -> None:
        self.findings.append(Finding(Severity.MAJOR, phase, code, message, detail, fix))

    def minor(self, phase: str, code: str, message: str, detail: str = "", fix: str = "") -> None:
        self.findings.append(Finding(Severity.MINOR, phase, code, message, detail, fix))

    def suppress(self, code: str) -> None:
        """Remove all findings with the given code (used to cancel false positives)."""
        self.findings = [f for f in self.findings if f.code != code]

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "profile": self.profile,
            "mode": self.mode,
            "score": self.score_pct,
            "score_raw": f"{self.total_score}/{self.max_score}",
            "findings": [f.to_dict() for f in self.findings if f.severity != Severity.OK],
            "dimensions": [
                {
                    "name": d.name,
                    "score": d.score,
                    "max": d.max_score,
                    "notes": d.notes,
                }
                for d in self.dimensions
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
