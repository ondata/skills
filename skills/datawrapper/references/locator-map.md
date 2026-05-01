# Datawrapper — Creating a Locator Map

A locator map shows WHERE something is located or happened. Chart type: `locator-map`.
Unlike choropleth maps, locator maps use markers (points, areas, lines) placed on
a basemap — they don't color regions by a data value.

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

Add markers after the base map is configured.

### Point markers
```bash
curl -s -X POST "https://api.datawrapper.de/v3/charts/<ID>/markers" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "point",
    "coordinates": [12.492, 41.890],
    "title": "Rome",
    "visible": true
  }'
```

### Area markers
```bash
curl -s -X POST "https://api.datawrapper.de/v3/charts/<ID>/markers" \
  -H "Authorization: Bearer $DATAWRAPPER_API" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "area",
    "coordinates": [[lon1,lat1],[lon2,lat2],[lon3,lat3],[lon1,lat1]],
    "title": "Area label",
    "fill": "#e74c3c",
    "opacity": 0.4
  }'
```

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
