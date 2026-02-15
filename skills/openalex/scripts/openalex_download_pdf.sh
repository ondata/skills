#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${OPENALEX_API_KEY:-}" ]]; then
  echo "ERROR: OPENALEX_API_KEY is not set." >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is not installed." >&2
  exit 1
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $(basename "$0") <WORK_ID_or_URL> [output_dir]" >&2
  exit 1
fi

work_input="$1"
outdir="${2:-.}"
mkdir -p "$outdir"

work_id="$work_input"
work_id="${work_id##*/}" # normalize URL to bare id

meta=$(curl -sS "https://api.openalex.org/works/${work_id}?api_key=${OPENALEX_API_KEY}")

pdf_url=$(echo "$meta" | jq -r '
  .content_urls.pdf
  // .best_oa_location.pdf_url
  // .primary_location.pdf_url
  // ([.locations[]?.pdf_url] | map(select(. != null)) | first)
  // empty
')

if [[ -z "$pdf_url" ]]; then
  title=$(echo "$meta" | jq -r '.display_name // "(unknown title)"')
  echo "No PDF URL available in OpenAlex metadata for ${work_id}: ${title}" >&2
  exit 2
fi

if [[ "$pdf_url" == *"content.openalex.org"* ]]; then
  if [[ "$pdf_url" == *"?"* ]]; then
    pdf_url="${pdf_url}&api_key=${OPENALEX_API_KEY}"
  else
    pdf_url="${pdf_url}?api_key=${OPENALEX_API_KEY}"
  fi
fi

outfile="${outdir}/${work_id}.pdf"
curl -fL -sS "$pdf_url" -o "$outfile"

echo "$outfile"
