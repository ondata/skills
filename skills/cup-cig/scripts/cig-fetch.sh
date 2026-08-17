#!/usr/bin/env bash
# Download canonical ANAC CIG JSON through the public browser flow.
set -euo pipefail

readonly DEFAULT_OUTPUT_DIR="."
readonly STEP_TIMEOUT="${CIG_FETCH_STEP_TIMEOUT:-8}"
readonly ATTEMPT_TIMEOUT="${CIG_FETCH_ATTEMPT_TIMEOUT:-20}"

OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
OUTPUT_DIR_SET=0
FORCE=0
STDOUT=0
BROWSER="${CIG_FETCH_AGENT_BROWSER:-agent-browser}"
JQ="${CIG_FETCH_JQ:-jq}"
SESSION="${CIG_FETCH_SESSION:-cig-fetch-$$}"
CURRENT_TEMP=""
TEMP_OUTPUT_DIR=""
FETCH_ERROR=""
ATTEMPT_DEADLINE=0

CIGS=()
declare -A SEEN=()

usage() {
  cat <<'EOF'
Usage: cig-fetch.sh [options] [CIG ...]

Download one canonical ANAC JSON per requested CIG.

Options:
  -f, --file FILE        Text file: one CIG per line; blank lines and # comments ignored.
  -o, --output-dir DIR   Directory for <CIG>.json (default: current directory).
      --stdout           Emit raw JSON on stdout for a single CIG; saves no permanent file.
      --force            Re-download even existing and valid JSON files.
  -h, --help             Show this help.

CIGs from arguments and from a file can be combined; duplicates are processed once.
The batch continues after a failure and exits 1 if at least one CIG failed.
EOF
}

die() {
  printf 'Error: %s\n' "$*" >&2
  exit 64
}

status() {
  if (( STDOUT )); then
    printf "$@" >&2
  else
    printf "$@"
  fi
}

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

add_cig() {
  local input cig
  input="$(trim "$1")"
  [[ -z "$input" || "$input" == \#* ]] && return
  cig="${input^^}"
  [[ "$cig" =~ ^[A-Z0-9]{10}$ ]] || die "invalid CIG: $input"
  [[ -n "${SEEN[$cig]:-}" ]] && return
  SEEN["$cig"]=1
  CIGS+=("$cig")
}

add_cigs_from_file() {
  local file="$1" line
  [[ -r "$file" ]] || die "list file not readable: $file"
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%$'\r'}"
    add_cig "$line"
  done < "$file"
}

browser() {
  local now remaining budget
  now="$(date +%s)"
  remaining=$((ATTEMPT_DEADLINE - now))
  if (( ATTEMPT_DEADLINE > 0 && remaining <= 0 )); then
    return 124
  fi
  budget="$STEP_TIMEOUT"
  if (( ATTEMPT_DEADLINE > 0 && remaining < budget )); then
    budget="$remaining"
  fi
  timeout "$budget" env AGENT_BROWSER_SESSION="$SESSION" "$BROWSER" "$@" >/dev/null
}

close_browser() {
  timeout "$STEP_TIMEOUT" env AGENT_BROWSER_SESSION="$SESSION" "$BROWSER" close >/dev/null 2>&1 || true
}

cleanup() {
  [[ -z "$CURRENT_TEMP" ]] || rm -f -- "$CURRENT_TEMP"
  [[ -z "$TEMP_OUTPUT_DIR" ]] || rm -rf -- "$TEMP_OUTPUT_DIR"
  close_browser
}

valid_json_for_cig() {
  "$JQ" -e --arg cig "$1" '.bando.CIG == $cig' "$2" >/dev/null 2>&1
}

step() {
  local description="$1"
  shift
  if ! browser "$@"; then
    FETCH_ERROR="$description"
    return 1
  fi
}

fetch_once() {
  local cig="$1" destination="$2" attempt="$3"
  local url="https://dettaglio-cig.anticorruzione.it/cig/${cig}"
  CURRENT_TEMP="${destination}.part.${SESSION}.${attempt}"
  rm -f -- "$CURRENT_TEMP"
  ATTEMPT_DEADLINE=$(( $(date +%s) + ATTEMPT_TIMEOUT ))


  step "opening the page" open "$url" || return 1
  step "waiting for the CIG field" wait 'input[type=text]' || return 1
  step "filling the CIG field" fill 'input[type=text]' "$cig" || return 1
  step "waiting for the anti-spam control" wait '#mosparo-box .mosparo__checkbox' || return 1
  step "activating the anti-spam control" click '#mosparo-box .mosparo__checkbox' || return 1
  # Mosparo enables confirmation only after generating the token browser-side.
  step "waiting for anti-spam validation" wait 3000 || return 1
  step "confirming the anti-spam control" click '#mosparo-box' || return 1
  # Mosparo may submit the form on its own. If it does not, use the visible button.
  if ! browser wait --text 'Risultati della Ricerca'; then
    step "starting the search" click 'button.submit-button' || return 1
    step "waiting for the results" wait --text 'Risultati della Ricerca' || return 1
  fi

  step "waiting for the JSON export" wait 'button.export-json-btn' || return 1
  step "downloading the JSON export" download 'button.export-json-btn' "$CURRENT_TEMP" || return 1

  if ! valid_json_for_cig "$cig" "$CURRENT_TEMP"; then
    FETCH_ERROR="validating the downloaded JSON"
    return 1
  fi

  mv -f -- "$CURRENT_TEMP" "$destination"
  CURRENT_TEMP=""
}

while (($#)); do
  case "$1" in
    -f|--file)
      (($# >= 2)) || die "missing file after $1"
      add_cigs_from_file "$2"
      shift 2
      ;;
    -o|--output-dir)
      (($# >= 2)) || die "missing directory after $1"
      OUTPUT_DIR="$2"
      OUTPUT_DIR_SET=1
      shift 2
      ;;
    --stdout)
      STDOUT=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      while (($#)); do
        add_cig "$1"
        shift
      done
      ;;
    -*)
      die "unknown option: $1"
      ;;
    *)
      add_cig "$1"
      shift
      ;;
  esac
done

((${#CIGS[@]} > 0)) || die "specify at least one CIG or --file"
if (( STDOUT )); then
  ((${#CIGS[@]} == 1)) || die "--stdout requires exactly one CIG"
  (( ! OUTPUT_DIR_SET )) || die "--stdout is incompatible with --output-dir"
  TEMP_OUTPUT_DIR="$(mktemp -d)"
  OUTPUT_DIR="$TEMP_OUTPUT_DIR"
fi
command -v "$BROWSER" >/dev/null 2>&1 || die "command not found: $BROWSER"
command -v "$JQ" >/dev/null 2>&1 || die "command not found: $JQ"
[[ "$STEP_TIMEOUT" =~ ^[1-9][0-9]*$ ]] || die "CIG_FETCH_STEP_TIMEOUT must be a positive integer"
[[ "$ATTEMPT_TIMEOUT" =~ ^[1-9][0-9]*$ ]] || die "CIG_FETCH_ATTEMPT_TIMEOUT must be a positive integer"

mkdir -p -- "$OUTPUT_DIR"
trap cleanup EXIT

ok=0
skipped=0
failed=0

for cig in "${CIGS[@]}"; do
  output="${OUTPUT_DIR%/}/${cig}.json"

  if (( ! FORCE )) && valid_json_for_cig "$cig" "$output"; then
    printf 'SKIP %s %s\n' "$cig" "$output"
    skipped=$((skipped + 1))
    continue
  fi

  success=0
  for attempt in 1 2; do
    FETCH_ERROR=""
    if fetch_once "$cig" "$output" "$attempt"; then
      status 'OK %s %s\n' "$cig" "$output"
      ok=$((ok + 1))
      success=1
      break
    fi

    rm -f -- "$CURRENT_TEMP"
    CURRENT_TEMP=""
    if (( attempt < 2 )); then
      printf 'RETRY %s after failure: %s\n' "$cig" "$FETCH_ERROR" >&2
      close_browser
    fi
  done

  if (( ! success )); then
    printf 'ERROR %s: %s\n' "$cig" "$FETCH_ERROR" >&2
    failed=$((failed + 1))
  fi
done

status 'Summary: %d downloaded, %d skipped, %d failed.\n' "$ok" "$skipped" "$failed"
if (( STDOUT && failed == 0 )); then
  cat "${OUTPUT_DIR%/}/${CIGS[0]}.json"
fi
(( failed == 0 ))
