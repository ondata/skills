#!/usr/bin/env bash
# Scarica il JSON completo di un CIG dal portale ANAC dettaglio-cig.
# Gist: https://gist.github.com/aborruso/183e93419b5d3528af69a6617e97a3f1
# Richiede: agent-browser (https://github.com/vercel-labs/agent-browser), jq
set -euo pipefail

if ! command -v agent-browser >/dev/null 2>&1; then
  echo "Errore: 'agent-browser' non installato." >&2
  echo "Info e installazione: https://github.com/vercel-labs/agent-browser" >&2
  exit 127
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Errore: 'jq' non installato." >&2
  exit 127
fi

if [ $# -lt 1 ]; then
  echo "Uso: $0 <CIG> [output-dir]" >&2
  exit 1
fi

CIG="$1"
OUTDIR="${2:-.}"
URL="https://dettaglio-cig.anticorruzione.it/cig/${CIG}"
OUT="${OUTDIR%/}/${CIG}.json"

mkdir -p "$OUTDIR"

# Sessione dedicata per non interferire con altre istanze agent-browser
export AGENT_BROWSER_SESSION="cig-fetch"

# Chiudi eventuali sessioni rimaste appese da run precedenti
agent-browser close >/dev/null 2>&1 || true
sleep 1

# Timeout globale: oltre HARD_TIMEOUT secondi si considera fallito
HARD_TIMEOUT="${CIG_FETCH_TIMEOUT:-15}"

run() {
  # Esegue un comando agent-browser con timeout per step; fallisce se scade.
  local step_timeout="$1"; shift
  if ! timeout "$step_timeout" "$@" >/dev/null 2>&1; then
    echo "Errore: step scaduto (${step_timeout}s): $*" >&2
    agent-browser close >/dev/null 2>&1 || true
    exit 4
  fi
}

# Avvia il timer complessivo come watchdog in background
(
  sleep "$HARD_TIMEOUT"
  kill -TERM $$ 2>/dev/null
) &
WATCHDOG=$!
trap 'kill $WATCHDOG 2>/dev/null || true; agent-browser close >/dev/null 2>&1 || true' EXIT
trap 'echo "Errore: timeout globale ${HARD_TIMEOUT}s superato" >&2; exit 5' TERM

run 8 agent-browser open "$URL"
run 6 agent-browser wait --text "I accept that the form entries"

run 4 agent-browser eval "(async () => {
  for (let i = 0; i < 20; i++) {
    const cb = document.querySelector('input[type=checkbox]');
    if (cb) { cb.click(); return 'clicked'; }
    await new Promise(r => setTimeout(r, 250));
  }
  return 'not-found';
})()"

run 3 agent-browser eval "(() => {
  const orig = URL.createObjectURL;
  URL.createObjectURL = function(blob) {
    if (blob instanceof Blob) blob.text().then(t => window.__capturedJSON = t);
    return orig.call(this, blob);
  };
  return 'hooked';
})()"

# Click "Cerca" via JS (il finder role-button si blocca su questa SPA)
run 3 agent-browser eval "(() => {
  const b = Array.from(document.querySelectorAll('button')).find(x => x.innerText.trim() === 'Cerca');
  if (!b) return 'no-cerca';
  b.click();
  return 'clicked';
})()"

run 8 agent-browser wait --text "Informazioni Gara"

# Click "Esporta in JSON" via JS (match parziale su "JSON")
run 3 agent-browser eval "(() => {
  const b = Array.from(document.querySelectorAll('button')).find(x => /JSON/i.test(x.innerText));
  if (!b) return 'no-json';
  b.click();
  return 'clicked';
})()"

# Attendi che il blob JSON venga catturato (entro il timeout residuo)
RAW='""'
for i in $(seq 1 10); do
  sleep 1
  RAW=$(agent-browser eval "window.__capturedJSON || ''" --json 2>/dev/null || echo '""')
  if [ "$(printf '%s' "$RAW" | wc -c)" -gt 20 ]; then
    break
  fi
done

kill $WATCHDOG 2>/dev/null || true
agent-browser close >/dev/null 2>&1 || true

if [ -z "${RAW:-}" ] || [ "$RAW" = '""' ]; then
  echo "Errore: JSON non catturato per $CIG" >&2
  exit 2
fi

printf '%s' "$RAW" | jq -r '.data.result' > "$OUT"

if ! jq -e . "$OUT" >/dev/null 2>&1; then
  echo "Errore: output non è JSON valido ($OUT)" >&2
  exit 3
fi

echo "OK: $OUT ($(wc -c <"$OUT") byte)"
