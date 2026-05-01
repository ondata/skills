# Datawrapper — Creating a Choropleth Map

A choropleth map colors geographic regions (countries, NUTS regions, states…)
based on a numeric value. Chart type: `d3-maps-choropleth`.

---

## ⚠️ Critical rule: axes MUST be set first

Without `metadata.axes.keys` and `metadata.axes.values`, Datawrapper doesn't know
which CSV column is the geographic key and which is the value to color by.
Result: every region renders in the default color (solid dark/black). No error is shown.
This is the single most common mistake. Set axes before anything else.

---

## Step sequence

### 1. Create
```bash
curl -s -X POST "https://api.datawrapper.de/v3/charts" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{"title": "My choropleth", "type": "d3-maps-choropleth"}'
# → save the returned "id"
```

### 2. Upload CSV data
```bash
curl -s -X PUT "https://api.datawrapper.de/v3/charts/<ID>/data" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: text/csv" \
  --data-binary @data.csv
```

CSV must have at least two columns:
- **Key column**: geographic identifiers matching the basemap (e.g. `nuts_id`, `iso_code`)
- **Value column**: numeric values to color by

Example:
```
nuts_code,accidents_per_100k
ITC3,527.5
AT32,526.9
HR03,210.4
```

### 3. Find the correct basemap and key attribute

```bash
curl -s "https://api.datawrapper.de/plugin/basemaps" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  | jq -r '.data[] | "\(.id) — keys: \([.keys[].value] | join(", "))"'
```

**Note**: the response is `{"status": ..., "data": [...]}` — always use `.data[]`, never `.[]`.

Use `/plugin/basemaps` (NOT `/v3/basemaps`) — this is the authoritative endpoint.
The `value` field in each key entry is the `map-key-attr` to use.

To verify which codes are accepted by a specific basemap key:
```bash
curl -s "https://api.datawrapper.de/plugin/basemaps/europe-nuts2-2024/NUTS_ID" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  | jq -r '.data.values[:10]'
```

Common basemaps and their key attributes:
| Basemap | `map-key-attr` |
|---|---|
| `europe-nuts3-2024` | `NUTS_ID` |
| `europe-nuts2-2024` | `NUTS_ID` |
| `europe-nuts1-2024` | `NUTS_ID` |
| `europe-nuts3-2021` | `NUTS_ID` |
| `world` | `ISO_A3` or `ISO_A2` |
| `europe` | `ISO_A2` |
| `usa-states` | `FIPS` or `name` |

### 4. Configure — MINIMUM required PATCH (do this first)
```bash
curl -s -X PATCH "https://api.datawrapper.de/v3/charts/<ID>" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "axes": {
        "keys": "nuts_code",
        "values": "accidents_per_100k"
      },
      "visualize": {
        "basemap": "europe-nuts2-2024",
        "map-key-attr": "NUTS_ID"
      }
    }
  }'
```

- `axes.keys` = column name in the CSV containing geographic IDs
- `axes.values` = column name in the CSV containing numeric values
- `map-key-attr` = property name in the basemap TopoJSON (from step 3)

Set ONLY these 4 required properties first. Verify the map renders with color
variation before adding tooltip or other extras.

### 5. Publish and verify
```bash
curl -s -X POST "https://api.datawrapper.de/v3/charts/<ID>/publish" \
  -H "Authorization: Bearer $DATAWRAPPER_API"

sleep 6

curl -s "https://api.datawrapper.de/v3/charts/<ID>/export/png?unit=px&width=1400&height=1000&scale=1" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  --output map.png
```

Read the PNG image. If it shows clear color variation across regions → success.
If all regions are the same dark color → axes are not set correctly (see ⚠️ above).

### 6. Add extras (second PATCH, after verifying base works)

Tooltip — include `fields` to map template variables to CSV columns:
```json
{
  "metadata": {
    "visualize": {
      "tooltip": {
        "body": "{{ accidents_per_100k }} accidents per 100k inhabitants",
        "title": "{{ nuts_code }}",
        "fields": {
          "nuts_code": "nuts_code",
          "accidents_per_100k": "accidents_per_100k"
        }
      }
    }
  }
}
```

`fields` keys are template variable names; values are CSV column names. Required
when CSV column names contain hyphens or special characters (e.g. `literacy-rate`
becomes `{{ literacy_rate }}` with `"literacy_rate": "literacy-rate"` in `fields`).

Descriptive metadata:
```json
{
  "metadata": {
    "describe": {
      "source-name": "Source name",
      "source-url": "https://source-url",
      "intro": "Map description",
      "byline": "Author"
    },
    "annotate": {
      "notes": "Methodology note"
    }
  }
}
```

---

## Color palette for choropleth maps — correct format

**`colorscale.palette` must be an INTEGER (index), not a string name.**
String names like `"YlOrRd"` or `"Blues"` are silently ignored.

The integer indexes into the theme's `data.colors.gradients` array. To get the
available gradients for a theme, call:

```bash
curl -s "https://api.datawrapper.de/v3/themes/default-2018-v2" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  | jq '.data.colors.gradients'
```

Default theme `datawrapper` extends `default-2018-v2`, which has 9 gradients (0–8):

| index | description | first → last color |
|---|---|---|
| 0 | green→blue (default) | `#f0f9e8` → `#254b8c` |
| 1 | yellow→purple | `#fcfcbe` → `#2c1160` |
| 2 | yellow→dark blue | `#f0f723` → `#0d0787` |
| 3 | yellow→green (2-stop) | `#fefaca` → `#008b15` |
| 4 | light pink→purple | `#feebe2` → `#7a0177` |
| 5 | yellow→dark blue (YlGnBu) | `#ffffcc` → `#253494` |
| 6 | brown→teal (diverging) | `#8c510a` → `#01665e` |
| 7 | pink→green (diverging) | `#c51b7d` → `#4d9221` |
| 8 | red→blue (diverging) | `#b2182b` → `#2166ac` |

**To set palette 1 (yellow → purple):**

```bash
curl -s -X PATCH "https://api.datawrapper.de/v3/charts/<ID>" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "visualize": {
        "colorscale": {
          "palette": 1,
          "gradient": ["#fcfcbe","#fdc78d","#fb8d67","#e45563","#ac337b","#6b1f7b","#2c1160"],
          "colors": [
            {"color": "#fcfcbe", "position": 0},
            {"color": "#fdc78d", "position": 0.1667},
            {"color": "#fb8d67", "position": 0.3333},
            {"color": "#e45563", "position": 0.5},
            {"color": "#ac337b", "position": 0.6667},
            {"color": "#6b1f7b", "position": 0.8333},
            {"color": "#2c1160", "position": 1}
          ]
        }
      }
    }
  }'
```

Both `gradient` (array of hex strings) AND `colors` (array of `{color, position}` objects)
must be set together with `palette` for the change to render correctly.

---

## Debugging checklist

| Symptom | Likely cause | Fix |
|---|---|---|
| All regions same dark color | `axes.keys`/`axes.values` missing | Add axes in PATCH |
| Refine tab empty in browser editor | `axes` not set | Same fix |
| Most regions gray (no data) | Key mismatch: CSV codes ≠ basemap property | Check `map-key-attr` and verify with `/plugin/basemaps/<id>/<key>` |
| Some regions unmatched | Data has codes not in basemap (e.g. Serbia in EU basemap) | Normal — no fix needed |
| Colors don't change despite colorscale | `palette` set as string instead of integer | Set `palette` as integer index (0-8), set `gradient` array and `colors` array together |
| jq fails on basemaps response | Wrong path — response is `{"data": [...]}` | Use `.data[]` not `.[]` |

## Deep merge caveat

PATCH merges deeply. Old keys persist. To fully replace a nested object, include
ALL its keys in one PATCH, or start fresh with a new chart.

## Recommended step order (tested, working)

1. Create chart (POST)
2. Upload CSV data (PUT)
3. **First PATCH**: set ONLY `axes` + `basemap` + `map-key-attr`
4. Publish and export PNG — verify color variation appears before continuing
5. **Second PATCH**: add `tooltip` (with `fields`), `describe`, `annotate`
6. Publish again and export final PNG
