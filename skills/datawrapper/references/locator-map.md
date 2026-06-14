# Datawrapper — Creating a Locator Map

A locator map shows WHERE something is located or happened. Chart type: `locator-map`.
Unlike choropleth maps, locator maps use markers (points, areas, lines, arrows) placed on
a basemap — they don't color regions by a data value.

---

## ⚠️ How markers are stored (read first)

Markers are NOT a separate REST resource. There is **no `/markers` endpoint**
(`GET`/`POST /v3/charts/<ID>/markers` both return 404). All markers — points,
areas, and arrows — live in the chart **data**, written as a single JSON object:

```json
{ "markers": [ { ...marker1... }, { ...marker2... } ] }
```

Write them with `PUT /v3/charts/<ID>/data` (Content-Type `application/json`).
Each PUT **replaces** the whole marker set — to add a marker, include all the
existing ones too. `"metadata": {"data": {"json": true}}` must be set on the chart.

---

## Step sequence

### 1. Create
```bash
curl -s -X POST "https://api.datawrapper.de/v3/charts" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{"title": "My locator map", "type": "locator-map"}'
# → save the returned "id"
```

### 2. Configure map view and style
```bash
curl -s -X PATCH "https://api.datawrapper.de/v3/charts/<ID>" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "data": { "json": true },
      "visualize": {
        "view": {
          "center": [12.492, 41.890],
          "zoom": 6,
          "height": 100
        },
        "style": "dw-light"
      }
    }
  }'
```

Note: `"data": {"json": true}` is required for locator maps.

### View properties

| Property | Description | Example |
|---|---|---|
| `center` | `[longitude, latitude]` — map center | `[12.492, 41.890]` (Rome) |
| `zoom` | 0–15 (0 = world, 10 = city, 15 = street) | `6` |
| `height` | Aspect ratio % (100 = square, 50 = wide landscape) | `75` |
| `bearing` | Rotation in degrees (0 = north up) | `0` |
| `fit` | Bounding box guaranteed to be visible on all screen sizes | see below |

**fit** — use when the map must always show a specific area regardless of embed size:
```json
"fit": {
  "top":    [longitude, latitude],
  "right":  [longitude, latitude],
  "bottom": [longitude, latitude],
  "left":   [longitude, latitude]
}
```

### Map styles

| Style | Description |
|---|---|
| `dw-light` | Light, clean (good default) |
| `dw-earth` | Terrain-like, natural colors |
| `dw-white` | Minimalist white |
| `dw-dark` | Dark background |
| `dw-white-invert` | High-contrast white |

### Layer visibility control
```json
"visibility": {
  "boundary_country": true,
  "boundary_state": true,
  "building": false,
  "green": true,
  "roads": true,
  "water": true,
  "urban": true,
  "building3d": false
}
```

---

## Adding markers

Build the full `{"markers":[...]}` object and PUT it to `/data`:

```bash
curl -s -X PUT "https://api.datawrapper.de/v3/charts/<ID>/data" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  --data-binary @markers.json
```

`markers.json` contains every marker on the map (one PUT = full replace).

### Point markers
```json
{
  "id": "p1",
  "type": "point",
  "title": "Rome",
  "coordinates": [12.49, 41.89],
  "markerColor": "#c0392b",
  "scale": 1.1,
  "visibility": { "enabled": true },
  "text": { "color": "#333333", "fontSize": 14, "enabled": true },
  "icon": {
    "id": "circle",
    "path": "M1000 350a500 500 0 0 0-500-500 500 500 0 0 0-500 500 500 500 0 0 0 500 500 500 500 0 0 0 500-500z",
    "horiz-adv-x": 1000, "scale": 1.1, "height": 700, "width": 1000
  }
}
```

The `icon` block is required to get a visible symbol; `circle` is the safe default.

### Area markers
The on/off toggles `fill`/`stroke` are top-level booleans; the colors live in a
top-level `properties` object using GeoJSON-style keys. The geometry goes in
`feature` (Polygon or MultiPolygon).
```json
{
  "id": "ar1",
  "type": "area",
  "title": "Zone",
  "fill": true,
  "stroke": true,
  "properties": {
    "fill": "#e74c3c",
    "fill-opacity": 0.35,
    "stroke": "#c0392b",
    "stroke-width": 1,
    "stroke-opacity": 1
  },
  "feature": {
    "type": "Feature",
    "properties": {},
    "geometry": {
      "type": "Polygon",
      "coordinates": [[[11.0,42.0],[13.0,42.0],[13.0,43.5],[11.0,43.5],[11.0,42.0]]]
    }
  }
}
```

### Arrow markers
Arrows show movement/connection between two points (`tail` → `tip`). Two styles:
`"line"` (constant width) and `"flow"` (variable width, for volume).

```json
{
  "id": "arrowA",
  "type": "arrow",
  "title": "Rome to Milan",
  "color": "#c30711",
  "opacity": 1,
  "gradient": false,
  "arrowType": "line",
  "head": "triangle",
  "lineWeight": "style0",
  "flowWeight": 0,
  "taper": { "direction": "tail", "headStrength": 0, "tailStrength": 0 },
  "curve": { "angle": 0, "offset": 0.5 },
  "coordinates": { "tip": [9.19, 45.46], "tail": [12.49, 41.89] },
  "bidirectional": false,
  "visibility": { "enabled": true },
  "tooltip": { "enabled": false, "text": "" }
}
```

Arrow fields:

| Field | Values | Notes |
|---|---|---|
| `coordinates.tail` / `coordinates.tip` | `[lon, lat]` | tail = start, tip = end (where the head points) |
| `arrowType` | `"line"` \| `"flow"` | `flow` = variable-width band (volume) |
| `head` | `"triangle"` \| `"lines"` | arrowhead style |
| `bidirectional` | `true` \| `false` | `true` = heads on both ends |
| `curve.angle` | degrees | `0` = straight; sign = bulge side. **Counterintuitive** — see note below |
| `curve.offset` | `0`–`1` | moves the arc apex along the arrow (`0.5` = middle) |
| `lineWeight` | `"style0"` / `"style1"` / `"style2"` | thickness preset for `line` arrows |
| `flowWeight` | number (e.g. `1`–`100`) | band thickness for `flow` arrows |
| `gradient` | `true` \| `false` | fade the color along the arrow |
| `taper` | `{direction, headStrength, tailStrength}` | shape of a `flow` band |
| `color` / `opacity` | hex / `0`–`1` | |

All arrow fields are writable via the API and render in the published map.
Optional: `data.tipLabel` / `data.tailLabel` to label the endpoints,
`groupId` to group markers.

#### Curving an arrow (important)

`curve.angle` is **not** "how much to curve" — its behaviour is counterintuitive
and depends on the arrow's length:

- `0` = straight (always safe).
- Values **close to 0** (e.g. `5`, `-8`) produce a HUGE, looping arc, especially
  on long arrows — not a gentle bend.
- Natural, gentle curves use **larger** magnitudes, and the longer the arrow the
  larger the angle needed. Rough heuristic: `|angle| ≈ chord_length_km / 2.5`.
  Observed good values: short hop (~90 km) → `40`; cross-region (~230 km) → `~120`.
- The **sign** flips which side the arc bulges. `curve.offset` (0–1) slides the
  apex along the arrow.

Because the mapping is non-linear, the reliable way to set a curve is to draw/adjust
it once in the editor (`https://app.datawrapper.de/chart/<ID>/visualize`, step
"Add markers"), then `GET /v3/charts/<ID>/data` and copy the resulting
`curve.angle`/`curve.offset` back into your script.

---

## Publish and export
```bash
# Publish
curl -s -X POST "https://api.datawrapper.de/v3/charts/<ID>/publish" \
  -H "Authorization: Bearer $DATAWRAPPER_API" > /dev/null

# Wait for CDN to update — do NOT skip this
sleep 6

# Export PNG
curl -s "https://api.datawrapper.de/v3/charts/<ID>/export/png?unit=px&width=1200&height=800&scale=1" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  --output locator_map.png
```

Always read the exported PNG to verify markers and map extent look correct.

---

## Common patterns

**Single event location**: set `center` + `zoom` to the area, add one point marker.

**Region or conflict zone**: add an area marker with a low-opacity fill color,
use `fit` bounds so the area is always in view on all screen sizes.

**Multiple cities comparison**: add multiple point markers, choose `zoom` level
that shows all of them, or use `fit` to define the bounding box.

**Flows / movement** (migration, trade, routes): add `arrow` markers, one per
origin→destination pair. Use `arrowType: "flow"` + `flowWeight` to encode volume.
```
