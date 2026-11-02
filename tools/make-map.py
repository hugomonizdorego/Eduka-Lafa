#!/usr/bin/env python3
"""Build Lafa's offline map of Timor-Leste (lafa/assets/timor/map/).

Source (downloaded once into build/geo/): geoBoundaries gbOpen TLS ADM2
(WHO / OCHA ROAP, CC BY 3.0 IGO) — the 65 administrative posts.
https://github.com/wmgeolab/geoBoundaries (release data, "_simplified").

Each post belongs to its municipality by the official list (POSTS below), and
a municipality's shape is the union of its posts, so posts and municipalities
always agree (Dom Aleixo and western Díli belong to Díli, Zumalai to Cova Lima).
Ataúro is its own municipality since 1 January 2022. Needs shapely
(pip install shapely) for the union.

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

# Administrative posts of each municipality (65 posts; Ataúro became a municipality in 2022).
POSTS = {
    "Aileu": ["Aileu Vila", "Laulara", "Liquidoe", "Remexio"],
    "Ainaro": ["Ainaro", "Hatu-Builico", "Hatu-Udo", "Maubisse"],
    "Atauro": ["Atauro"],
    "Baucau": ["Baguia", "Baucau", "Laga", "Quelicai", "Vemasse", "Venilale"],
    "Bobonaro": ["Atabae", "Balibo", "Bobonaro", "Cailaco", "Lolotoe", "Maliana"],
    "Cova Lima": ["Fatululic", "Fatumean", "Forohem", "Maukatar", "Suai", "Tilomar", "Zumalai"],
    "Dili": ["Cristo Rei", "Dom Aleixo", "Metinaro", "Nain Feto", "Vera Cruz"],
    "Ermera": ["Atsabe", "Ermera", "Hatolia", "Letefoho", "Railaco"],
    "Lautém": ["Iliomar", "Lautém", "Lospalos", "Luro", "Tutuala"],
    "Liquiçá": ["Bazartete", "Liquiçá", "Maubara"],
    "Manatuto": ["Barique/Natarbora", "Laclo", "Laclubar", "Laleia", "Manatuto", "Soibada"],
    "Manufahi": ["Alas", "Fatuberliu", "Same", "Turiscai"],
    "Oecusse": ["Nitibe", "Oesilo", "Pante Macassar", "Passabe"],
    "Viqueque": ["Lacluta", "Ossu", "Uato-Lari", "Uatucarbau", "Viqueque"],
}
OWNER = {post: mun for mun, posts in POSTS.items() for post in posts}

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
    from shapely.geometry import shape, mapping
    from shapely.ops import unary_union
    adm2 = fetch("ADM2", "_simplified.geojson"); meta2 = fetch("ADM2", "-metaData.json")
    parts = {name: [] for name in POSTS}; posts = []
    for feature in adm2["features"]:
        name = feature["properties"]["shapeName"]
        if name not in OWNER: sys.exit(f"make-map: post {name!r} is not in POSTS")
        parts[OWNER[name]].append(shape(feature["geometry"]).buffer(0))
        rings = clean(polygons(feature["geometry"]), 0.003, 0.02)
        if rings: posts.append({"name": name, "municipality": IDS[OWNER[name]], "centroid": centroid(rings), "polygons": rings})
    missing = set(OWNER) - {p["name"] for p in posts}
    if missing: sys.exit(f"make-map: posts without a shape: {sorted(missing)}")
    municipalities = []
    for name in sorted(parts):
        # Union of the posts; a tiny buffer closes slivers between neighbouring posts.
        union = unary_union(parts[name]).buffer(0.0004).buffer(-0.0004)
        rings = clean(polygons(mapping(union)), 0.0025)
        area = sum(abs(ring_area(p[0])) - sum(abs(ring_area(h)) for h in p[1:]) for p in rings)
        municipalities.append({"name": name, "id": IDS[name], "centroid": centroid(rings), "area_km2_approx": round(area), "posts": sorted(POSTS[name]), "polygons": rings})
    xs = [pt[0] for m in municipalities for p in m["polygons"] for pt in p[0]]; ys = [pt[1] for m in municipalities for p in m["polygons"] for pt in p[0]]
    OUT.mkdir(parents=True, exist_ok=True)
    common = {"bbox": [min(xs), min(ys), max(xs), max(ys)]}
    (OUT / "municipalities.json").write_text(json.dumps({**common, "source": "geoBoundaries gbOpen TLS ADM2 (" + meta2["boundarySource"] + "), posts joined by municipality",
        "licence": meta2["boundaryLicense"], "note": "Municipalities = union of their administrative posts (official list); Ataúro is a municipality since 2022. Simplified for Lafa.",
        "municipalities": municipalities}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "posts.json").write_text(json.dumps({**common, "source": "geoBoundaries gbOpen TLS ADM2 (" + meta2["boundarySource"] + ")",
        "licence": meta2["boundaryLicense"], "posts": posts}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (OUT / "SOURCES.md").write_text(f"""# Map data

* `posts.json` — the 65 administrative posts, derived from geoBoundaries gbOpen TLS ADM2, source: {meta2['boundarySource']},
  licence: {meta2['boundaryLicense']} (https://data.humdata.org/dataset/timor-leste-administrative-boundaries-levels-0-3).
* `municipalities.json` — the 14 municipalities, each the union of its posts (official list of posts per
  municipality in tools/make-map.py), same source and licence. Ataúro is shown as the municipality created in 2022.
  Post boundaries may predate the administrative changes of 2022.
* geoBoundaries: Runfola, D. et al. (2020) geoBoundaries: A global database of political administrative
  boundaries. PLoS ONE 15(4): e0231866. https://www.geoboundaries.org

Simplified with tools/make-map.py; coordinates are WGS84 longitude/latitude.
""", encoding="utf-8")
    for m in municipalities: print(f"{m['name']:10} {m['area_km2_approx']:6} km²  {sum(len(p[0]) for p in m['polygons'])} points  {m['centroid']}")
    print(len(posts), "posts;", (OUT / "municipalities.json").stat().st_size, "+", (OUT / "posts.json").stat().st_size, "bytes")

if __name__ == "__main__":
    sys.exit(main())
