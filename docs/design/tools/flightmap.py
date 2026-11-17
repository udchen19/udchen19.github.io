"""Flight map for the About page (UD, 2026-11-16).

python flightmap.py <repo> <ne_110m_land.shp> <ne_10m_airports.shp>

Reads data/flights.yaml (airports and year only) and Natural Earth (public domain):
  assets/textures/map-land.png  land as a 1-bit dot screen, coloured by CSS mask (served fingerprinted)
  data/flight_map.json          projected airports and great-circle routes, rendered as inline SVG
Projection: equirectangular, cropped to the travelled area. No shapefile library is installed, so
the .shp/.dbf readers below cover only what these two files use (polygons, points, text fields).
"""
import sys, json, math, struct, pathlib, subprocess, tempfile
import numpy as np
import yaml
from PIL import Image, ImageDraw

repo = pathlib.Path(sys.argv[1]); land_shp = pathlib.Path(sys.argv[2]); air_shp = pathlib.Path(sys.argv[3])

# --------------------------------------------------------------- shapefile readers
def shp_records(path):
    b = path.read_bytes(); i = 100
    while i < len(b):
        _, length = struct.unpack(">ii", b[i:i + 8]); i += 8
        rec = b[i:i + length * 2]; i += length * 2
        t = struct.unpack("<i", rec[:4])[0]
        if t == 1:
            yield ("point", struct.unpack("<2d", rec[4:20]))
        elif t == 5:
            nparts, npts = struct.unpack("<2i", rec[36:44])
            parts = list(struct.unpack(f"<{nparts}i", rec[44:44 + 4 * nparts])) + [npts]
            o = 44 + 4 * nparts
            pts = [struct.unpack("<2d", rec[o + 16 * k:o + 16 * k + 16]) for k in range(npts)]
            yield ("poly", [pts[parts[k]:parts[k + 1]] for k in range(nparts)])

def dbf_rows(path):
    b = path.read_bytes()
    n, hlen, rlen = struct.unpack("<IHH", b[4:12])
    fields, o = [], 32
    while b[o] != 0x0D:
        name = b[o:o + 11].split(b"\0")[0].decode(); flen = b[o + 16]; fields.append((name, flen)); o += 32
    for r in range(n):
        rec = b[hlen + r * rlen + 1: hlen + (r + 1) * rlen]; row, p = {}, 0
        for name, flen in fields:
            row[name] = rec[p:p + flen].decode("utf-8", "replace").strip(); p += flen
        yield row

# --------------------------------------------------------------- data
legs = yaml.safe_load((repo / "data/flights.yaml").read_text())["legs"]
codes = sorted({c for l in legs for c in l[1:3]})
pos, names, icao = {}, {}, {}
for (kind, xy), row in zip(shp_records(air_shp), dbf_rows(air_shp.with_suffix(".dbf"))):
    code = row.get("iata_code") or row.get("IATA_CODE")
    if code in codes and kind == "point":
        pos[code] = xy                                   # (lon, lat)
        names[code] = row.get("name", "")
        icao[code] = row.get("gps_code", "")
# Not in Natural Earth's airport file; coordinates from Wikidata (P625), looked up by IATA code on
# 2026-11-16: Q1147000 Dubrovnik Ruđer Bošković Airport, Q702019 Taipei Songshan Airport; ICAO codes
# from the same items (P239).
EXTRA = {"DBV": ((18.268333333, 42.561388888), "Dubrovnik Ruđer Bošković", "LDDU"),
         "TSA": ((121.551666666, 25.069444444), "Taipei Songshan", "RCSS")}
for c, (xy, nm, ic) in EXTRA.items():
    if c not in pos: pos[c], names[c], icao[c] = xy, nm, ic
missing = [c for c in codes if c not in pos]
print("airports found", len(pos), "of", len(codes), "missing:", missing or "none")
if missing:
    sys.exit("stop: airports missing from Natural Earth; ask UD before filling them in")

# Country or region of each airport, for its flag in the airport list (static/flags, from flag-icons):
# the first letters of the ICAO code name it (ICAO Doc 7910 nationality letters), only those needed here.
ICAO_CC = {"RC": "tw", "RJ": "jp", "VH": "hk", "ZS": "cn", "VT": "th", "EG": "gb", "ED": "de", "LI": "it",
           "LE": "es", "LS": "ch", "LD": "hr", "HE": "eg", "OM": "ae", "OT": "qa", "MM": "mx", "K": "us"}
# English names, spoken once with each flag in the airport list (Astra, round 7).
COUNTRY = {"tw": "Taiwan", "jp": "Japan", "hk": "Hong Kong", "cn": "China", "th": "Thailand", "gb": "United Kingdom",
           "de": "Germany", "it": "Italy", "es": "Spain", "ch": "Switzerland", "hr": "Croatia", "eg": "Egypt",
           "ae": "United Arab Emirates", "qa": "Qatar", "mx": "Mexico", "us": "United States"}
def cc_of(ic):
    for n in (2, 1):
        if ic[:n] in ICAO_CC: return ICAO_CC[ic[:n]]

# --------------------------------------------------------------- projection
# The whole world, cut in the open Atlantic so that no continent is split (UD, 2026-11-16). The edge is
# the middle of the widest run of whole degrees of longitude, between 70°W and 10°W, with no land in the
# map's latitudes (Natural Earth land, rasterised at one degree).
LAT0, LAT1 = -2.0, 64.0                                  # travelled latitudes, with a margin
grid = Image.new("L", (360, int(LAT1 - LAT0)), 0); g = ImageDraw.Draw(grid)
for kind, rings in shp_records(land_shp):
    for ring in rings:
        g.polygon([(lo + 180, LAT1 - la) for lo, la in ring], fill=1, outline=1)
wet = (np.asarray(grid) == 0).all(axis=0)                # columns with no land, index 0 = 180°W
best, run = (0, 0), 0
for lon in range(-70, -9):
    run = run + 1 if wet[lon + 180] else 0
    if run > best[0]: best = (run, lon)
if best[0] < 3:
    sys.exit("stop: no open ocean in the Atlantic band; ask UD where to cut the map")
LON0 = best[1] - (best[0] - 1) / 2; LON1 = LON0 + 360
W = 1400; H = round(W * (LAT1 - LAT0) / (LON1 - LON0) / math.cos(math.radians(32)))   # equal-area-ish at mid latitude
def proj(lon, lat):
    return ((lon - LON0) / (LON1 - LON0) * W, (LAT1 - lat) / (LAT1 - LAT0) * H)
def proj_pt(lon, lat):                                   # a single point: its copy inside the span
    return proj(LON0 + (lon - LON0) % 360, lat)
print(f"edge {LON0:.1f} (open ocean {best[0]} deg wide), {W} x {H}, Taipei at {proj_pt(*pos['TPE'])[0] / W:.1%}")

def great_circle(a, b, n=48):
    (lo1, la1), (lo2, la2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    p1 = np.array([math.cos(la1) * math.cos(lo1), math.cos(la1) * math.sin(lo1), math.sin(la1)])
    p2 = np.array([math.cos(la2) * math.cos(lo2), math.cos(la2) * math.sin(lo2), math.sin(la2)])
    w = math.acos(max(-1, min(1, float(p1 @ p2))))
    if w < 1e-6: return [a, b]
    pts = []
    for t in np.linspace(0, 1, n):
        v = (math.sin((1 - t) * w) * p1 + math.sin(t * w) * p2) / math.sin(w)
        pts.append((math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(v[2]))))
    return pts

# --------------------------------------------------------------- land as dots
S = 2                                                    # mask at 2x
img = Image.new("L", (W * S, H * S), 255); d = ImageDraw.Draw(img)
for kind, rings in shp_records(land_shp):
    for ring in rings:
        for shift in (-360, 0, 360):                     # the span runs past 180; draw each shifted copy
            if max(lo for lo, _ in ring) + shift < LON0 or min(lo for lo, _ in ring) + shift > LON1: continue
            d.polygon([tuple(c * S for c in proj(lo + shift, la)) for lo, la in ring], fill=0)
with tempfile.TemporaryDirectory() as t:
    t = pathlib.Path(t)
    land = np.asarray(img) < 128
    Image.fromarray(np.where(land, 200, 255).astype(np.uint8), "L").save(t / "l.png")   # ~22% coverage
    subprocess.run(["magick", str(t / "l.png"), "-ordered-dither", "h6x6a", str(t / "d.png")], check=True)
    dots = np.asarray(Image.open(t / "d.png").convert("L")) < 128
pal = Image.fromarray(dots.astype(np.uint8), "P"); pal.putpalette([0, 0, 0, 255, 255, 255] + [0] * 762)
land_png = repo / "assets/textures/map-land.png"
pal.save(land_png, optimize=True, transparency=0)
print("map-land.png", (W * S, H * S), land_png.stat().st_size // 1024, "KB")

# --------------------------------------------------------------- routes and places
# The map marks places, not routes: every route prints faint; the places in flights.yaml print strong.
routes, seen = [], {}
for leg in legs:
    year, a, b = leg[:3]
    key = tuple(sorted((a, b)))
    if key in seen:
        routes[seen[key]]["years"].add(year); continue
    # Unwrap the longitudes so the curve is continuous, then draw it once per 360° shift that touches
    # the map; the SVG clips what falls outside (London to Chicago leaves by both edges).
    gc = great_circle(pos[a], pos[b]); lons = [gc[0][0]]
    for lo, _ in gc[1:]:
        lo += 360 * round((lons[-1] - lo) / 360); lons.append(lo)
    pieces = []
    for shift in (-360, 0, 360):
        ls = [lo + shift for lo in lons]
        if max(ls) < LON0 or min(ls) > LON1: continue
        pieces.append("M" + " L".join(f"{proj(lo, la)[0]:.1f},{proj(lo, la)[1]:.1f}" for lo, (_, la) in zip(ls, gc)))
    seen[key] = len(routes)
    routes.append({"d": " ".join(pieces), "years": {year}, "a": a, "b": b})
for r in routes:
    r["years"] = sorted(r["years"])
count = {}
for leg in legs:
    for c in leg[1:3]: count[c] = count.get(c, 0) + 1
no_cc = [c for c in codes if not cc_of(icao.get(c, ""))]
if no_cc:
    sys.exit(f"stop: no country for {no_cc}; add its ICAO letters to ICAO_CC")
airports = [{"code": c, "name": names[c], "cc": cc_of(icao[c]), "country": COUNTRY[cc_of(icao[c])], "x": round(proj_pt(*pos[c])[0], 1), "y": round(proj_pt(*pos[c])[1], 1), "n": count[c]} for c in codes]
places = []
for pl in yaml.safe_load((repo / "data/flights.yaml").read_text()).get("places", []):
    dots = [[round(v, 1) for v in proj_pt(*pos[c])] for c in pl["airports"]]   # the name sits by the first
    places.append({"name": pl["name"], "note": pl["note"], "airports": pl["airports"], "label": pl.get("label", "ne"),
                   "x": dots[0][0], "y": dots[0][1], "dots": dots})
(repo / "data/flight_map.json").write_text(json.dumps({"w": W, "h": H, "routes": routes, "airports": airports, "places": places}, ensure_ascii=False))
print("routes", len(routes), "airports", len(airports), "places", len(places))
