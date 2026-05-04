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

## Range annotations — vertical colored bands (line charts)

Use `range-annotations` to highlight time periods as colored vertical bands.

**Critical fields** — all required, wrong values silently break rendering:

| Field | Value |
|---|---|
| `type` | `"x"` (vertical band on x-axis) |
| `display` | `"range"` |
| `opacity` | integer **0–100** (NOT 0–1) |
| `position.x0` / `position.x1` | date string `"YYYY/MM/DD HH:mm"` (slashes, not dashes) |
| `position.y0` / `position.y1` | y-axis extent, e.g. `"0"` and `"15"` for full height |
| `strokeWidth` | `0` to hide border |

```json
{
  "metadata": {
    "visualize": {
      "range-annotations": [
        {
          "id": "band-1",
          "type": "x",
          "display": "range",
          "color": "#2980b9",
          "opacity": 12,
          "position": {
            "x0": "2014/02/01 00:00",
            "x1": "2016/12/01 00:00",
            "y0": "0",
            "y1": "15"
          },
          "strokeType": "solid",
          "strokeWidth": 0
        }
      ]
    }
  }
}
```

**Common mistakes that break rendering silently:**
- Using `"x0"/"x1"` at top level instead of inside `position` → ignored
- Using dashes in dates (`"2014-02-01"`) instead of slashes (`"2014/02/01 00:00"`) → ignored
- Using `opacity: 0.12` (float) instead of `opacity: 12` (integer 0-100) → too transparent or ignored
- Omitting `"type": "x"` or `"display": "range"` → not rendered

**Readability rule: colored bands without labels are unreadable.**
Always pair every range annotation with a matching `text-annotation` that names the period.
Place the label at a fixed low y value (e.g. `"0.6"`) centered in the band, italic, no connector, color matching the band:

```json
{
  "id": "lbl-period",
  "text": "Period name",
  "align": "bc",
  "size": 11,
  "italic": true,
  "bg": false,
  "color": "#1a5276",
  "dx": 0,
  "dy": 0,
  "position": { "x": "2015-07-01", "y": "0.6" },
  "connectorLine": { "enabled": false },
  "showMobile": true,
  "showDesktop": true
}
```

`x` = midpoint of the band; `y` = value safely below all data (check the actual data minimum first).

---

## Text annotations with arrows (line charts)

Point to a specific data value with a callout box and arrow.

```json
{
  "metadata": {
    "visualize": {
      "text-annotations": [
        {
          "id": "ann-1",
          "text": "Label with <b>bold</b>",
          "align": "tl",
          "size": 13,
          "color": "#494949",
          "bg": true,
          "bold": false,
          "italic": false,
          "underline": false,
          "dx": 8,
          "dy": -30,
          "position": {
            "x": "2014-11-01",
            "y": "13.29"
          },
          "connectorLine": {
            "enabled": true,
            "arrowHead": "triangle",
            "type": "straight",
            "stroke": 1,
            "inheritColor": false,
            "targetPadding": 6
          },
          "showMobile": true,
          "showDesktop": true
        }
      ]
    }
  }
}
```

- `position.x`: ISO date string matching the data (`"YYYY-MM-DD"`)
- `position.y`: string of the data value at that point
- `dx`/`dy`: pixel offset of the text box from the arrow tip
- `align`: text anchor — `"tl"` top-left, `"br"` bottom-right, `"tr"` top-right, `"bl"` bottom-left
- `bg`: `true` adds a white background behind the text

---

## Text annotations on bar charts (d3-bars)

Bar charts use a **completely different `position` format** — row-based, not coordinate-based.
Using `position.x = "CategoryName"` or `position.y = "value"` silently fails.

```json
{
  "id": "ann-bar",
  "text": "My annotation",
  "align": "tl",
  "size": 13,
  "color": "#494949",
  "bg": true,
  "dx": -5,
  "dy": -30,
  "position": {
    "x": "-1.3600",
    "yAxis": "y",
    "rowIndex": 4,
    "rowOffset": -2
  },
  "connectorLine": {
    "enabled": true,
    "arrowHead": "lines",
    "type": "straight",
    "stroke": 1,
    "inheritColor": false,
    "targetPadding": 4
  },
  "showMobile": true,
  "showDesktop": true
}
```

- `position.x`: the data value of the bar as a string (e.g. `"-1.3600"`) — determines horizontal position of arrow tip
- `position.rowIndex`: 0-based index of the bar **from the top** of the chart
- `position.rowOffset`: small integer offset in pixels (usually `-2`)
- `position.yAxis`: always `"y"`
- `arrowHead`: `"lines"` (two-line arrow) or `"triangle"` — both work on bar charts

**To find `rowIndex`**: count bars from top, starting at 0. If bars are in CSV order, row 0 = first CSV row.

---

## Colored title words

The `title` field supports inline HTML `<span>` for partial coloring:

```json
{
  "title": "Unemployment at <span style=\"color:#c0392b\">historic lows</span>"
}
```

---

## Readability: always spell out abbreviations

Any abbreviation used in labels, axes, or annotations must be spelled out **at least once** in the chart — in the intro or in the notes. A chart with unexplained abbreviations is not self-contained.

- Wrong: axis label `pp/anno`, notes say nothing → reader doesn't know what `pp` means
- Right: intro says *"in punti percentuali (pp)"* or notes say *"pp = punti percentuali"*

Apply this to any unit shorthand: `pp`, `Mm³`, `k`, `M`, `idx`, etc.

---

## Discover property names

The most reliable way to find visualization property names is to configure the
chart in the Datawrapper UI, then read back the metadata:
```bash
curl -s "https://api.datawrapper.de/v3/charts/$CHART_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  | jq '.metadata.visualize'
```
