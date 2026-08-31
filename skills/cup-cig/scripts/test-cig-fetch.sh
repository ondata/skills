#!/usr/bin/env bash
# Offline contract test for cig-fetch.sh: drives it with a fake agent-browser,
# so it needs no network and no real ANAC session.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
FETCHER="$ROOT/cig-fetch.sh"
WORK="$(mktemp -d)"
trap 'rm -rf -- "$WORK"' EXIT

FAKE_BROWSER="$WORK/fake-agent-browser"
FAKE_STATE="$WORK/current-cig"
FAKE_LOG="$WORK/browser.log"
OUTPUT="$WORK/output"
LIST="$WORK/cigs.txt"

cat > "$FAKE_BROWSER" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$1" >> "$FAKE_LOG"
case "$1" in
  fill)
    printf '%s' "$3" > "$FAKE_STATE"
    ;;
  download)
    cig="$(cat "$FAKE_STATE")"
    if [[ "${FAKE_BAD_JSON:-0}" == 1 ]]; then
      printf '{"bando":{"CIG":"WRONGCIG00"}}' > "$3"
    else
      printf '{"bando":{"CIG":"%s"}}' "$cig" > "$3"
    fi
    ;;
esac
EOF
chmod +x "$FAKE_BROWSER"

cat > "$LIST" <<'EOF'
# CIG list
a0059785cc

B52CE8B8F4
A0059785CC
EOF
STDOUT_JSON="$WORK/stdout.json"


run_fetcher() {
  FAKE_STATE="$FAKE_STATE" FAKE_LOG="$FAKE_LOG" CIG_FETCH_AGENT_BROWSER="$FAKE_BROWSER" "$FETCHER" "$@"
}

run_fetcher --output-dir "$OUTPUT" --file "$LIST" B52CE8B8F4
jq -e '.bando.CIG == "A0059785CC"' "$OUTPUT/A0059785CC.json" >/dev/null
jq -e '.bando.CIG == "B52CE8B8F4"' "$OUTPUT/B52CE8B8F4.json" >/dev/null

printf '{"bando":{"CIG":"A0059785CC"},"kept":true}' > "$OUTPUT/A0059785CC.json"
run_fetcher --output-dir "$OUTPUT" A0059785CC
jq -e '.kept == true' "$OUTPUT/A0059785CC.json" >/dev/null

run_fetcher --force --output-dir "$OUTPUT" A0059785CC
jq -e 'has("kept") | not' "$OUTPUT/A0059785CC.json" >/dev/null

run_fetcher --stdout A0059785CC > "$STDOUT_JSON"
jq -e '.bando.CIG == "A0059785CC"' "$STDOUT_JSON" >/dev/null
if run_fetcher --stdout A0059785CC B52CE8B8F4 >/dev/null 2>&1; then
  printf -- '--stdout accepted more than one CIG\n' >&2
  exit 1
fi
if run_fetcher --stdout --output-dir "$OUTPUT" A0059785CC >/dev/null 2>&1; then
  printf -- '--stdout accepted --output-dir\n' >&2
  exit 1
fi

if FAKE_BAD_JSON=1 run_fetcher --output-dir "$OUTPUT" Z893433C4B; then
  printf 'expected a validation error for JSON with the wrong CIG\n' >&2
  exit 1
fi
[[ ! -e "$OUTPUT/Z893433C4B.json" ]]

printf 'OK: CLI contracts verified\n'
