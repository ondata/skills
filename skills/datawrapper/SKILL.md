---
name: datawrapper
description: >
  Create charts, choropleth maps, and locator maps via the Datawrapper API.
  Use this skill whenever the user wants to publish a visualization on Datawrapper,
  create an interactive chart or map from data, generate a PNG/embed from Datawrapper,
  or use the Datawrapper REST API. Triggers on: "create a map with datawrapper",
  "publish a chart on datawrapper", "choropleth map", "locator map datawrapper",
  "export PNG from datawrapper", and any request involving creating or configuring
  Datawrapper charts/maps programmatically. Also triggers for Italian variants:
  "mappa coropletica datawrapper", "crea grafico datawrapper", "mappa datawrapper".
---

# Datawrapper API — Skill

Create and publish Datawrapper charts and maps via REST API.

**Auth**: `Authorization: Bearer $DATAWRAPPER_API` (env var — never print the value).
**Base URL**: `https://api.datawrapper.de/v3`

---

## ⚠️ Step 0 — Verify API key before anything else

```bash
curl -s -o /dev/null -w "%{http_code}" \
  "https://api.datawrapper.de/v3/me" \
  -H "Authorization: Bearer $DATAWRAPPER_API"
```

- `200` → key is valid, proceed.
- `401` or `000` → key is missing or invalid. Stop and tell the user:
  > "`DATAWRAPPER_API` is not set or invalid.
  > Set it with `export DATAWRAPPER_API=<token>` (Linux/macOS) or
  > `$env:DATAWRAPPER_API='<token>'` (PowerShell)."

Do NOT proceed past a non-200 — all subsequent calls will fail silently.

---

## Chart types

| Visualization | `type` value |
|---|---|
| Stacked bar | `d3-bars-stacked` |
| Grouped bar | `d3-bars` |
| Line | `d3-lines` |
| Scatter | `d3-scatter-plot` |
| Pie/donut | `d3-pies` |
| Choropleth map | `d3-maps-choropleth` |
| Locator map | `locator-map` |

---

## Quick reference by task

- **Chart** (line, bar, scatter…) → read [references/chart.md](references/chart.md)
- **Choropleth map** (color regions by value) → read [references/choropleth-map.md](references/choropleth-map.md)
- **Locator map** (show where something happened) → read [references/locator-map.md](references/locator-map.md)

Always read the relevant reference file before starting — each file contains the
exact step sequence, mandatory properties, and known pitfalls.

---

## Common steps (all types)

### 1. Create the visualization
```bash
CHART_ID=$(curl -s -X POST "https://api.datawrapper.de/v3/charts" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{"title": "My title", "type": "<type>"}' \
  | jq -r '.id')
echo "Chart ID: $CHART_ID"
```

Always capture the `id` — needed for all subsequent calls. Print it immediately.

### 2. Upload data (CSV)
```bash
curl -s -X PUT "https://api.datawrapper.de/v3/charts/$CHART_ID/data" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: text/csv" \
  --data-binary @/path/to/data.csv
```

### 3. Configure metadata (PATCH)
```bash
curl -s -X PATCH "https://api.datawrapper.de/v3/charts/$CHART_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{ "metadata": { ... } }' \
  | jq -r '.id // .'
```

PATCH does a **deep merge** — each call merges into existing metadata.
Old keys persist. To fully replace a nested object, include ALL its keys in a
single PATCH call, or create a fresh chart.

### 4. Publish
```bash
curl -s -X POST "https://api.datawrapper.de/v3/charts/$CHART_ID/publish" \
  -H "Authorization: Bearer $DATAWRAPPER_API" > /dev/null
```

### 5. Export PNG

**Always wait at least 6 seconds after publish before exporting.** Datawrapper's CDN
takes a moment to update — exporting immediately returns the previous render.
Use `scale=2` to export at double resolution. Omit `height` so Datawrapper uses
the natural chart height — avoids large blank areas on short charts.

```bash
sleep 6

curl -s "https://api.datawrapper.de/v3/charts/$CHART_ID/export/png?unit=px&width=1200&scale=2" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  --output output.png
```

Always read the exported PNG visually to verify it looks correct before reporting success.

### 6. Offer to delete the chart

After verifying the PNG, ask the user:

> "The PNG has been saved locally. Do you want to delete the chart from Datawrapper?"

If yes:

```bash
curl -s -X DELETE "https://api.datawrapper.de/v3/charts/$CHART_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API"
```

If no, remind the user the chart is available at:
`https://app.datawrapper.de/chart/<CHART_ID>/visualize`

---

## Add descriptive metadata (recommended for all types)

Always include units of measure (`number-append`/`number-prepend`) when values have a unit —
percentages, euros, kilometres, etc. An axis without a unit label is always wrong.

```json
{
  "metadata": {
    "describe": {
      "source-name": "Data source name",
      "source-url": "https://source-url.com",
      "intro": "Chart or map description",
      "byline": "Author or organization",
      "number-append": " %",
      "number-format": "0.0"
    },
    "annotate": {
      "notes": "Methodology notes, caveats"
    }
  }
}
```

See [references/chart.md](references/chart.md) for the full units-of-measure reference.

---

## Inspect what Datawrapper stored
```bash
curl -s "https://api.datawrapper.de/v3/charts/$CHART_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  | jq '.metadata'
```

Use this to debug when the output doesn't look right — verify what properties
Datawrapper actually stored vs. what you intended to send.

---

## Delete a chart
```bash
curl -s -X DELETE "https://api.datawrapper.de/v3/charts/$CHART_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API"
```

Useful when iterating: delete a broken chart and start fresh to avoid deep-merge
conflicts from previous PATCH calls.

---

## Manual fallback (browser editor)
If something doesn't render correctly via API, the user can inspect and fix it at
`https://app.datawrapper.de/chart/<ID>/visualize`.
After manual edits, read back the config via GET to make it reproducible via API.
