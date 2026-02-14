#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${OPENALEX_API_KEY:-}" ]]; then
  echo "ERROR: OPENALEX_API_KEY is not set." >&2
  exit 1
fi

entity="works"
per_page="25"
raw="false"
jq_expr=""

declare -a params

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --entity <name>        OpenAlex entity endpoint (default: works)
  --search <expr>        search parameter
  --filter <expr>        filter parameter
  --sort <expr>          sort parameter
  --select <fields>      select parameter
  --per-page <n>         per-page (1..200), default 25
  --page <n>             basic pagination page
  --cursor <value>       cursor pagination value (use '*' to start)
  --group-by <field>     group_by parameter
  --sample <n>           sample parameter
  --seed <n>             seed parameter
  --jq <expr>            jq expression for output processing
  --raw                  print raw JSON (skip pretty jq)
  -h, --help             show this help
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --entity) entity="$2"; shift 2 ;;
    --search) params+=(--data-urlencode "search=$2"); shift 2 ;;
    --filter) params+=(--data-urlencode "filter=$2"); shift 2 ;;
    --sort) params+=(--data-urlencode "sort=$2"); shift 2 ;;
    --select) params+=(--data-urlencode "select=$2"); shift 2 ;;
    --per-page) per_page="$2"; shift 2 ;;
    --page) params+=(--data-urlencode "page=$2"); shift 2 ;;
    --cursor) params+=(--data-urlencode "cursor=$2"); shift 2 ;;
    --group-by) params+=(--data-urlencode "group_by=$2"); shift 2 ;;
    --sample) params+=(--data-urlencode "sample=$2"); shift 2 ;;
    --seed) params+=(--data-urlencode "seed=$2"); shift 2 ;;
    --jq) jq_expr="$2"; shift 2 ;;
    --raw) raw="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

params+=(--data-urlencode "per-page=$per_page")
params+=(--data-urlencode "api_key=$OPENALEX_API_KEY")

url="https://api.openalex.org/${entity}"

if [[ "$raw" == "true" ]]; then
  curl -sS --get "$url" "${params[@]}"
  exit 0
fi

if [[ -n "$jq_expr" ]]; then
  curl -sS --get "$url" "${params[@]}" | jq "$jq_expr"
else
  curl -sS --get "$url" "${params[@]}" | jq .
fi
