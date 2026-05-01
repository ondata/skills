# Datawrapper — Creating a Chart

## Step sequence

### 1. Create
```bash
CHART_ID=$(curl -s -X POST "https://api.datawrapper.de/v3/charts" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{"title": "My chart", "type": "d3-lines"}' \
  | jq -r '.id')
echo "Chart ID: $CHART_ID"
```

### 2. Upload CSV data
```bash
curl -s -X PUT "https://api.datawrapper.de/v3/charts/$CHART_ID/data" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: text/csv" \
  --data-binary @data.csv
```

### 3. Configure metadata
```bash
curl -s -X PATCH "https://api.datawrapper.de/v3/charts/$CHART_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{ "metadata": { ... } }' \
  | jq -r '.id // .'
```

### 4. Publish
```bash
curl -s -X POST "https://api.datawrapper.de/v3/charts/$CHART_ID/publish" \
  -H "Authorization: Bearer $DATAWRAPPER_API" > /dev/null
```

### 5. Export PNG

**Wait at least 6 seconds after publish before exporting** — CDN takes a moment to update.
Omit `height` so Datawrapper uses the natural chart height (avoids blank space on short charts).

```bash
sleep 6

curl -s "https://api.datawrapper.de/v3/charts/$CHART_ID/export/png?unit=px&width=1200&scale=2" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  --output chart.png
```

Always read the exported PNG visually to verify it looks correct.

---

## Chart types

| Visualization | `type` |
|---|---|
| Stacked bar | `d3-bars-stacked` |
| Grouped bar | `d3-bars` |
| Line | `d3-lines` |
| Scatter | `d3-scatter-plot` |
| Pie/donut | `d3-pies` |
| Table | `tables` |

---

## CSV format

- First row = column headers
- First column = categories/labels (x-axis or row labels)
- Additional columns = series values
- Separator: comma `,` or semicolon `;`

Example for a grouped bar:
```
Country,2022,2023,2024
Italy,23.1,24.5,25.0
Germany,18.2,19.0,19.8
France,20.5,21.1,22.3
```

---

## Metadata: custom colors per series
```json
{
  "metadata": {
    "visualize": {
      "custom-colors": {
        "Italy": "#c0392b",
        "Germany": "#2980b9",
        "France": "#27ae60"
      }
    }
  }
}
```
Keys must match series names exactly (case-sensitive). For stacked bar charts,
keys are the **column header names** in the CSV (not the row labels in the first column).

---

## Units of measure — always set them

**Always** configure number formatting when values have a unit. Datawrapper applies
these to bar labels, axis ticks, and tooltips.

```json
{
  "metadata": {
    "describe": {
      "number-append": " %",
      "number-prepend": "",
      "number-format": "0.0"
    }
  }
}
```

| Property | Use | Example value |
|---|---|---|
| `number-append` | suffix after value | `" %"`, `" €"`, `" km"` |
| `number-prepend` | prefix before value | `"$"`, `"€ "` |
| `number-format` | decimal/thousands format | `"0.0"`, `"0,0"`, `"0.00"` |
| `number-divisor` | divide values before display | `1000` → show millions as thousands |

**Rules**:
- Percentages → `"number-append": " %"` (with a space before `%`)
- Monetary → use `number-prepend` or `number-append` depending on locale
- Large numbers → set `number-divisor` + explain the unit in the intro text
- When in doubt, add the unit: an ambiguous axis label is always wrong

---

## Scatter plot — point labels

To show labels on each point, set `axes.labels` to the CSV column containing the label text.
This is an **axes** property, not a visualize property.

```bash
curl -s -X PATCH "https://api.datawrapper.de/v3/charts/$CHART_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "axes": {
        "x": "GDP per capita",
        "y": "Life expectancy",
        "size": "Population",
        "color": "Continent",
        "labels": "Country"
      }
    }
  }'
```

Only `x`, `y`, and `labels` are required. Omit `size` and `color` if not needed.

---

## Metadata: visual options
```json
{
  "metadata": {
    "visualize": {
      "thick": true,
      "y-grid": true,
      "label-colors": true,
      "sort-by": "last"
    }
  }
}
```

---

## Readability limits

| Chart type | Limit | Reason |
|---|---|---|
| Bar / grouped bar | Max ~10 bars | More becomes unreadable |
| Stacked bar | Max ~8 categories | Small segments lose labels |
| Pie / donut | Max ~6 slices | Group the rest as "Other" |

Always inspect values before building stacked bar or pie charts: **exclude negative values**,
which distort the stack and make segments impossible to read.

---

## Discover property names

The most reliable way to find visualization property names is to configure the
chart in the Datawrapper UI, then read back the metadata:
```bash
curl -s "https://api.datawrapper.de/v3/charts/$CHART_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  | jq '.metadata.visualize'
```
