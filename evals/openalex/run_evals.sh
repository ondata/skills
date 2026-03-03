#!/usr/bin/env bash
# Run openalex eval prompts through Claude and save outputs for human review.
#
# Usage:
#   ./run_evals.sh                   run all prompts
#   ./run_evals.sh --id test-09      run one prompt
#   ./run_evals.sh --skip-false      skip should_trigger=false prompts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE=$(date +%Y-%m-%d)
OUT_DIR="$SCRIPT_DIR/runs/$DATE"
FILTER_ID=""
SKIP_FALSE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --id)          FILTER_ID="$2"; shift 2 ;;
    --skip-false)  SKIP_FALSE=true; shift ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

mkdir -p "$OUT_DIR"
echo "openalex eval run — $DATE"
echo "outputs → $OUT_DIR"
echo ""

EVAL_SCRIPT_DIR="$SCRIPT_DIR" \
EVAL_OUT_DIR="$OUT_DIR" \
EVAL_FILTER_ID="$FILTER_ID" \
EVAL_SKIP_FALSE="$SKIP_FALSE" \
python3 << 'PYEOF'
import csv, os, subprocess
from pathlib import Path

script_dir = Path(os.environ["EVAL_SCRIPT_DIR"])
out_dir    = Path(os.environ["EVAL_OUT_DIR"])
filter_id  = os.environ["EVAL_FILTER_ID"]
skip_false = os.environ["EVAL_SKIP_FALSE"] == "true"

# Automated pattern checks: (test_ids, description, detector_fn)
# These are heuristic — always review the raw output file.
AUTO_CHECKS = [
    (
        {"test-09", "test-27"},
        "relevance_score without search=",
        lambda body: "relevance_score" in body and "search=" not in body,
    ),
    (
        {"test-10", "test-11", "test-24"},
        "title.search outside filter=",
        lambda body: "title.search" in body and "filter=" not in body,
    ),
    (
        {"test-22"},
        "multi-line curl (backslash continuation)",
        lambda body: any(
            line.rstrip().endswith("\\") and "curl" in line
            for line in body.split("\n")
        ),
    ),
    (
        None,  # applies to all
        "API key printed",
        lambda body: "echo" in body and "openalex_api_key" in body.lower(),
    ),
]

warnings = {}

with open(script_dir / "prompts.csv") as f:
    for row in csv.DictReader(f):
        tid     = row["id"]
        trigger = row["should_trigger"] == "true"
        prompt  = row["prompt"]

        if filter_id and tid != filter_id:
            continue
        if skip_false and not trigger:
            continue

        label = "trigger   " if trigger else "no-trigger"
        print(f"[{tid}] {label}  {prompt[:72]}")

        result = subprocess.run(
            ["claude", "-p", prompt, "--allowedTools", "Bash"],
            capture_output=True, text=True,
        )

        out_text = (
            f"PROMPT: {prompt}\n"
            f"SHOULD_TRIGGER: {row['should_trigger']}\n"
            f"{'=' * 72}\n\n"
            f"{result.stdout}"
        )
        if result.stderr:
            out_text += f"\n--- stderr ---\n{result.stderr}"

        (out_dir / f"{tid}.txt").write_text(out_text)

        # Run auto-checks
        body = result.stdout.lower()
        tid_warnings = []
        for ids, desc, check in AUTO_CHECKS:
            if ids is None or tid in ids:
                if check(body):
                    tid_warnings.append(desc)

        if tid_warnings:
            warnings[tid] = tid_warnings
            for w in tid_warnings:
                print(f"  ⚠  {w}")
        else:
            print(f"  ✓  {tid}.txt")
        print()

# Summary
total = sum(1 for _ in (out_dir).glob("test-*.txt"))
print("=" * 72)
print(f"Saved {total} output(s) → {out_dir}")
if warnings:
    print(f"\nAuto-check warnings ({len(warnings)} test(s)):")
    for tid, ws in warnings.items():
        for w in ws:
            print(f"  [{tid}] {w}")
else:
    print("No auto-check warnings.")
print("\nNext: review outputs, tick checks.md, save results/YYYY-MM-DD.json")
PYEOF
