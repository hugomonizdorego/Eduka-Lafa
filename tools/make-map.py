#!/usr/bin/env python3
"""Build Lafa's offline map of Timor-Leste (lafa/assets/timor/map/).

Sources (downloaded once into build/geo/):
* municipalities: geoBoundaries gbOpen TLS ADM1 (OpenStreetMap contributors,
  Open Database License 1.0) — 13 units; the island of Ataúro is split from
  Díli because it became a municipality on 1 January 2022;
* administrative posts: geoBoundaries gbOpen TLS ADM2 (WHO / OCHA ROAP,
  CC BY 3.0 IGO) — 65 posts.
https://github.com/wmgeolab/geoBoundaries (release data, "_simplified").

The geometry is simplified further (Douglas–Peucker) for a small file and
stored as [lon, lat] rings with four decimals. Output:
  municipalities.json  — 14 shapes with centroid and approximate area
  posts.json           — administrative posts with their municipality
  SOURCES.md           — attribution and licences

    python3 tools/make-map.py
"""
import json
import math
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "build" / "geo"
OUT = ROOT / "lafa" / "assets" / "timor" / "map"
BASE = "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/main/releaseData/gbOpen/TLS/{lvl}/geoBoundaries-TLS-{lvl}{suffix}"
IDS = {"Aileu": "mun.aileu", "Ainaro": "mun.ainaro", "Atauro": "mun.atauro", "Baucau": "mun.baucau", "Bobonaro": "mun.bobonaro",
       "Cova Lima": "mun.covalima", "Dili": "mun.dili", "Ermera": "mun.ermera", "Lautém": "mun.lautem", "Liquiçá": "mun.liquica",
       "Manatuto": "mun.manatuto", "Manufahi": "mun.manufahi", "Oecusse": "mun.oecusse", "Viqueque": "mun.viqueque"}

def fetch(lvl, suffix):
    target = CACHE / f"geoBoundaries-TLS-{lvl}{suffix}"
    if not target.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(BASE.format(lvl=lvl, suffix=suffix), timeout=60) as r: target.write_bytes(r.read())
    return json.loads(target.read_text(encoding="utf-8"))

def polygons(geometry):
    if geometry["type"] == "Polygon": return [geometry["coordinates"]]
    if geometry["type"] == "MultiPolygon": return geometry["coordinates"]
    return []

def perpendicular(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == dy == 0: return math.hypot(x - x1, y - y1)
    t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - x1 - t * dx, y - y1 - t * dy)

def simplify(points, tolerance):
    if len(points) < 4: return points
    keep = [False] * len(points); keep[0] = keep[-1] = True; stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop(); best, index = 0.0, None
        for i in range(a + 1, b):
            d = perpendicular(points[i], points[a], points[b])
            if d > best: best, index = d, i
        if index is not None and best > tolerance:
            keep[index] = True; stack += [(a, index), (index, b)]
    return [p for p, k in zip(points, keep) if k]

def ring_area(ring):
    """Signed area in km² (equirectangular approximation, fine at this size)."""
    lat0 = math.radians(sum(p[1] for p in ring) / len(ring)); kx = 111.320 * math.cos(lat0); ky = 110.574
    s = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]): s += (x1 * kx) * (y2 * ky) - (x2 * kx) * (y1 * ky)
    return s / 2

def centroid(polys):
    best = max(polys, key=lambda poly: abs(ring_area(poly[0])))[0]
    a = cx = cy = 0.0
    for (x1, y1), (x2, y2) in zip(best, best[1:] + best[:1]):
        f = x1 * y2 - x2 * y1; a += f; cx += (x1 + x2) * f; cy += (y1 + y2) * f
    if a == 0: return best[0]
    return [round(cx / (3 * a), 4), round(cy / (3 * a), 4)]

def inside(point, ring):
    x, y = point; result = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: result = not result
    return result

def clean(polys, tolerance, min_km2=0.05):
    out = []
    for poly in polys:
        rings = []
        for ring in poly:
            pts = simplify([tuple(p[:2]) for p in ring], tolerance)
            if len(pts) >= 4 and abs(ring_area(pts)) >= min_km2: rings.append([[round(x, 4), round(y, 4)] for x, y in pts])
        if rings: out.append(rings)
    return out

def main():
    adm1 = fetch("ADM1", "_simplified.geojson"); adm2 = fetch("ADM2", "_simplified.geojson")
    meta1 = fetch("ADM1", "-metaData.json"); meta2 = fetch("ADM2", "-metaData.json")
    shapes = {}
    for feature in adm1["features"]:
        name = feature["properties"]["shapeName"]; polys = polygons(feature["geometry"])
        if name == "Dili":
            # Ataúro island (north of Díli, lat > -8.4) is its own municipality since 2022.
            island = [p for p in polys if sum(pt[1] for pt in p[0]) / len(p[0]) > -8.40]
            shapes["Atauro"] = island; polys = [p for p in polys if p not in island]
        shapes[name] = polys
    municipalities = []
    for name, polys in sorted(shapes.items()):
        rings = clean(polys, 0.0025)
        area = sum(abs(ring_area(p[0])) - sum(abs(ring_area(h)) for h in p[1:]) for p in rings)
        municipalities.append({"name": name, "id": IDS[name], "centroid": centroid(rings), "area_km2_approx": round(area), "polygons": rings})
    posts = []
    for feature in adm2["features"]:
        name = feature["properties"]["shapeName"]; rings = clean(polygons(feature["geometry"]), 0.003, 0.02)
        if not rings: continue
        c = centroid(rings)
        owner = next((m["name"] for m in municipalities if any(inside(c, p[0]) for p in m["polygons"])), None)
        if owner is None:   # centroid in the sea or a lake: nearest municipality centroid
            owner = min(municipalities, key=lambda m: math.hypot(m["centroid"][0] - c[0], m["centroid"][1] - c[1]))["name"]
        if name == "Atauro": owner = "Atauro"
        posts.append({"name": name, "municipality": IDS[owner], "centroid": c, "polygons": rings})
    xs = [pt[0] for m in municipalities for p in m["polygons"] for pt in p[0]]; ys = [pt[1] for m in municipalities for p in m["polygons"] for pt in p[0]]
    OUT.mkdir(parents=True, exist_ok=True)
    common = {"bbox": [min(xs), min(ys), max(xs), max(ys)]}
    (OUT / "municipalities.json").write_text(json.dumps({**common, "source": "geoBoundaries gbOpen TLS ADM1 (" + meta1["boundarySource"] + ")",
        "licence": meta1["boundaryLicense"], "note": "Ataúro split from Díli (municipality since 2022). Simplified for Lafa.",
        "municipalities": municipalities}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "posts.json").write_text(json.dumps({**common, "source": "geoBoundaries gbOpen TLS ADM2 (" + meta2["boundarySource"] + ")",
        "licence": meta2["boundaryLicense"], "posts": posts}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "SOURCES.md").write_text(f"""# Map data

* `municipalities.json` — derived from geoBoundaries gbOpen TLS ADM1, source: {meta1['boundarySource']},
  licence: {meta1['boundaryLicense']} (© OpenStreetMap contributors, https://www.openstreetmap.org/copyright).
  The derived database is shared under the same licence (ODbL 1.0). Ataúro was split from Díli to show the
  municipality created in 2022.
* `posts.json` — derived from geoBoundaries gbOpen TLS ADM2, source: {meta2['boundarySource']},
  licence: {meta2['boundaryLicense']} (https://data.humdata.org/dataset/timor-leste-administrative-boundaries-levels-0-3).
  Post boundaries may predate the 2022 changes.
* geoBoundaries: Runfola, D. et al. (2020) geoBoundaries: A global database of political administrative
  boundaries. PLoS ONE 15(4): e0231866. https://www.geoboundaries.org

Simplified with tools/make-map.py; coordinates are WGS84 longitude/latitude.
""", encoding="utf-8")
    for m in municipalities: print(f"{m['name']:10} {m['area_km2_approx']:6} km²  {sum(len(p[0]) for p in m['polygons'])} points  {m['centroid']}")
    print(len(posts), "posts;", (OUT / "municipalities.json").stat().st_size, "+", (OUT / "posts.json").stat().st_size, "bytes")

if __name__ == "__main__":
    sys.exit(main())
