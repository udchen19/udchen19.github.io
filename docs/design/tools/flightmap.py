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
        names[code] = row.get("name", "").replace("'", "’")     # "Int’l", typeset like the rest of the site
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
# Order for the map's drawing (UD, 2026-11-16): each route inks in at the flight that first took it, each
# airport appears at the first flight that touched it (on arrival, "arr" 1, or departure), each place at
# its first airport's turn; later flights on a route are kept, with their direction, to redraw it.
# Legs are listed in the order flown.
first = {}
flights = []        # every flight after the first on its route: route, order, flown the other way
routes, seen = [], {}
for li, leg in enumerate(legs):
    year, a, b = leg[:3]
    first.setdefault(a, (li, 0)); first.setdefault(b, (li, 1))
    key = tuple(sorted((a, b)))
    if key in seen:
        r = routes[seen[key]]; r["years"].add(year)
        flights.append({"r": seen[key], "i": li, "rev": int((a, b) != (r["a"], r["b"]))}); continue
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
    routes.append({"d": " ".join(pieces), "years": {year}, "a": a, "b": b, "o": li})
for r in routes:
    r["years"] = sorted(r["years"])
    # The same route drawn the other way, for return flights: each piece's points in reverse.
    r["dr"] = " ".join("M" + " L".join(reversed(p.strip().split(" L"))) for p in r["d"].split("M") if p.strip())
count = {}
for leg in legs:
    for c in leg[1:3]: count[c] = count.get(c, 0) + 1
no_cc = [c for c in codes if not cc_of(icao.get(c, ""))]
if no_cc:
    sys.exit(f"stop: no country for {no_cc}; add its ICAO letters to ICAO_CC")
transfer = set(yaml.safe_load((repo / "data/flights.yaml").read_text()).get("transfer", []))   # stops only passed through (UD)
airports = [{"code": c, "name": names[c], "cc": cc_of(icao[c]), "country": COUNTRY[cc_of(icao[c])], "x": round(proj_pt(*pos[c])[0], 1), "y": round(proj_pt(*pos[c])[1], 1), "n": count[c], "o": first[c][0], "arr": first[c][1], "via": int(c in transfer)} for c in codes]
places = []
for pl in yaml.safe_load((repo / "data/flights.yaml").read_text()).get("places", []):
    dots = [[round(v, 1) for v in proj_pt(*pos[c])] for c in pl["airports"]]   # the name sits by the first
    places.append({"name": pl["name"], "note": pl["note"], "airports": pl["airports"], "label": pl.get("label", "ne"),
                   "x": dots[0][0], "y": dots[0][1], "dots": dots, "o": min(first[c] for c in pl["airports"])[0], "arr": min(first[c] for c in pl["airports"])[1]})
# Timing for the drawing (UD, 2026-11-16), in seconds from the start. Each flight, strictly in turn:
#   1+2  at the departure, if new: its dot and its entry in the airport list; if it is one of the four places
#        and not yet shown, its dot and name on the map, then its entry in the key types out;
#   3    the route draws (or, flown before, flashes);
#   4+5  at the arrival, the same as 1+2.
# Only 1 with 2, and 4 with 5, run together. Flights are drawn one after another,
# each starting when the one before has landed, at one steady speed: a line's time follows its length on the
# map (at least MIN), scaled so the whole run of flights takes RUN. When a flight first reaches one of the
# places, its dot and name appear (LABEL) and its entry in the key below types out before the next line starts;
# a flight reaching any new airport waits for that airport to appear in the list below (LIST). Written into the data so the page
# needs no arithmetic of its own.
RUN, MIN, BEAT, LABEL, CPS, LIST = 13.0, 0.12, 0.2, 0.7, 60.0, 0.45   # CPS: key typing speed; LIST: an airport appearing in the list;
# BEAT: a pause after every step, so each comes to rest before the next (UD); NEW: the longer pause after a new
# airport or place; BRISK, QUICK: a familiar flight's share of the time, and its pause (UD, after Astra round 11)
NEW, BRISK, QUICK = 0.6, 0.4, 0.05
def plen(d):
    """Length, in map units, of a route's first drawn piece."""
    pts = [tuple(map(float, p.split(","))) for p in d.split("M")[1].strip().split(" L")]
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
route_of = {tuple(sorted((r["a"], r["b"]))): k for k, r in enumerate(routes)}
lens = [plen(routes[route_of[tuple(sorted(leg[1:3]))]]["d"]) for leg in legs]
speed = sum(lens) / (RUN - MIN * len(legs) * 0.5)          # map units per second
durs = [round(max(MIN, L / speed), 3) for L in lens]
# A flight on a route already drawn flashes it: drawn again at the same speed, then fading back. Its slot
# includes the fade (the draw is the first FLASH of it), so nothing starts until the flash is over.
FLASH = 0.65
again = {f["i"] for f in flights}
REPEAT = 0.6   # a flash over a route already drawn runs at this share of a first drawing's time (UD: repeats faster)
slots = [round(d * REPEAT / FLASH, 3) if li in again else d for li, d in enumerate(durs)]
place_of = {c: k for k, pl in enumerate(places) for c in pl["airports"]}
shown, t, at, leg_t = set(), 0.0, {}, []
def reach(code, when):
    """An airport first touched at `when`; returns when the next line may start (after a place's name)."""
    if code in at: return when
    at[code] = when                            # a new airport: its entry in the list appears before the next flight
    k = place_of.get(code)
    if k is None or k in shown: return when + LIST + NEW
    shown.add(k); pl = places[k]
    # The dot and name on the map (LABEL), then the place's entry in the key types out, name and note,
    # before the next flight (UD, 2026-11-16).
    pl["t"] = round(when, 3); pl["kt"] = round(when + LABEL, 3)
    pl["kd"] = round((len(pl["name"]) + len(pl["note"])) / CPS, 3)
    return max(when + LIST, when + LABEL + pl["kd"]) + NEW
# Events (UD, 2026-11-17): each belongs to the flight that arrived for it. After that arrival (its airport and
# place shown), its line in "What took me there" types out before the next flight starts.
events = yaml.safe_load((repo / "data/flights.yaml").read_text()).get("events", [])
ev_at = {}
for e in events:
    li = next((i for i, l in enumerate(legs) if l[0] == e["year"] and l[3] == e["month"] and l[2] == e["airport"]), None)
    if li is None: sys.exit(f"stop: no flight to {e['airport']} in {e['month']}/{e['year']} for {e['name']}")
    ev_at.setdefault(li, []).append(e)
for li, leg in enumerate(legs):
    # Familiar: a route already drawn between two airports already shown. Nothing new appears, so it runs brisk;
    # anything new keeps its full time and is followed by a longer pause (UD, after Astra round 11).
    familiar = li in again and leg[1] in at and leg[2] in at
    t = reach(leg[1], t)                        # a departure from a new place: its name first
    leg_t.append(round(t, 3))
    if familiar: slots[li] = round(slots[li] * BRISK, 3)
    t = reach(leg[2], t + slots[li] + (QUICK if familiar else BEAT))   # rest; then a new airport / place
    for e in ev_at.get(li, []):
        e["t"] = round(t, 3); e["kd"] = round(len(f"{e['year']} {e['name']} {e.get('city', '')}") / CPS, 3)
        t = e["t"] + e["kd"] + NEW
# The running date: the month and year of the flight being drawn, from its start (only when it changes).
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
dates = []
for li, leg in enumerate(legs):
    label = f"{MON[leg[3] - 1]} {leg[0]}"
    if not dates or dates[-1][1] != label: dates.append([leg_t[li], label])
for r in routes: r["t"], r["dur"] = leg_t[r["o"]], durs[r["o"]]
for f in flights: f["t"], f["dur"] = leg_t[f["i"]], slots[f["i"]]
for ap in airports: ap["t"] = round(at[ap["code"]], 3)
print(f"drawing takes {t:.1f} s")
(repo / "data/flight_map.json").write_text(json.dumps({"w": W, "h": H, "legs": len(legs), "label": LABEL, "list": LIST, "dates": dates, "end": round(t, 3), "routes": routes, "flights": flights, "airports": airports, "places": places, "events": events}, ensure_ascii=False))
print("routes", len(routes), "airports", len(airports), "places", len(places))
