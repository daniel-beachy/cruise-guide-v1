#!/usr/bin/env python3
"""Build the Koningsdam voyage guide: artifact page, standalone offline file, home-screen app bundle."""
import base64, json, math, os, sys
from datetime import datetime, timedelta, timezone
from html import escape as esc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from content_trip import TRIP, CALLS, LEG_NAMES, POIS, WEATHER, DAYS, SHIP_SPECS, SHIP_FACTS, DECKS, ELSEWHERE, HAL_FACTS, CABINS, SITE_URL
from content_vibes import VIBES, SD_EMBARK, SD_DISEMBARK, SKY_TARGETS, SKY_TIPS, SKY_APPS
from content_trivia import MORE as TRIVIA_MORE
from content_cards import CARDS
import sky as SKY
from content_ports import PORTS, ZOO, MEXICO
from content_play import WILDLIFE, QUIZ, PACKING, DOWNLOADS, GAMES
import build_svg as S

M = json.load(open(os.path.join(ROOT, "data", "build-maps.json")))
QUIZ = list(QUIZ) + list(TRIVIA_MORE)
PHOTO_CREDITS = {
    'gray': ('José Eugenio Gómez Rodríguez', 'CC BY 3.0', 'Ballena_gris_adulta_con_su_ballenato.jpg'),
    'humpback': ('Juan Cruzado Cortés', 'CC BY 4.0', 'Humpback_whale_breaching_off_Cabo_San_Lucas.jpg'),
    'blue': ('NOAA Photo Library', 'Public domain', 'Anim1754_-_Flickr_-_NOAA_Photo_Library.jpg'),
    'fin': ('Aqqa Rosing-Asvid, Visit Greenland', 'CC BY 2.0', 'Finhval_(1).jpg'),
    'common-dolphin': ('NOAA NMFS', 'Public domain', 'Common_dolphin_noaa.jpg'),
    'bottlenose': ('NASA', 'Public domain', 'Tursiops_truncatus_01-cropped.jpg'),
    'sea-lion': ('Jonathan Eisen', 'CC BY 4.0', 'California_Sea_Lion,_Monterey,_California,_United_States_imported_from_iNaturalist_photo_203598492.jpg'),
    'harbor-seal': ('Charles J. Sharp', 'CC BY-SA 4.0', 'Common_seal_(Phoca_vitulina)_2.jpg'),
    'pelican': ('Frank Schulenburg', 'CC BY-SA 4.0', 'Brown_pelican_in_flight_(Bodega_Bay).jpg'),
    'frigatebird': ('Andrew Turner', 'CC BY 2.0', 'Fregata_magnificens_-Galapagos,_Ecuador_-male-8_(1).jpg'),
    'booby': ('Benjamint444', 'GFDL 1.2', 'Blue-footed-booby.jpg'),
    'mobula': ('Nick Bonzey', 'CC BY-SA 2.0', 'Mobula_breach_2.jpg'),
    'turtle': ('Thierry Caro', 'CC BY-SA 3.0', 'Lepidochelys-olivacea-K%C3%A9lonia-1.JPG'),
    'garibaldi': ('Stan Shebs', 'CC BY-SA 3.0', 'Hypsypops_rubicundus_adult.jpg'),
}

def photo(key, alt):
    b64 = base64.b64encode(open(os.path.join(ROOT, 'photos', key + '.jpg'), 'rb').read()).decode()
    who, lic, f = PHOTO_CREDITS[key]
    return (f'<figure class="photo"><img src="data:image/jpeg;base64,{b64}" alt="{esc(alt)}" width="720" height="450" loading="lazy" decoding="async">'
            f'<figcaption>Photo: <a href="https://commons.wikimedia.org/wiki/File:{f}" target="_blank" rel="noopener">{esc(who)}</a> · {esc(lic)} · cropped</figcaption></figure>')

R = M["route"]
NM_TO_MI = 1.15078

# ------------------------------------------------------------ geometry helpers
def mercator_params():
    (x1, y1), (x2, y2) = R["pts"]["sd"], R["pts"]["pv"]
    l1, l2 = math.radians(-117.1735), math.radians(-105.2520)
    k = (x2 - x1) / (l2 - l1)
    tx = x1 - k * l1
    m1 = math.log(math.tan(math.pi / 4 + math.radians(32.7130) / 2))
    ty = y1 + k * m1
    return k, tx, ty
K, TX, TY = mercator_params()
def inv(x, y):
    lon = math.degrees((x - TX) / K)
    lat = math.degrees(2 * math.atan(math.exp((TY - y) / K)) - math.pi / 2)
    return round(lat, 2), round(lon, 2)

legs_out = {}
leg_times = {"sd_pv": ("2026-12-27T01:00:00Z", "2026-12-29T14:00:00Z"), "pv_mz": ("2026-12-29T23:00:00Z", "2026-12-30T15:00:00Z"),
             "mz_cb": ("2026-12-31T00:00:00Z", "2026-12-31T14:00:00Z"), "cb_sd": ("2026-12-31T21:00:00Z", "2027-01-02T15:00:00Z")}
zones = {"sd_pv": [[0, -8], [300, -7], [950, -6]], "pv_mz": [[0, -6], [30, -7]], "mz_cb": [[0, -7]], "cb_sd": [[0, -7], [455, -8]]}
px_per_nm = []
for leg, L in R["legs"].items():
    sm = [[s[0], s[1], s[2], *inv(s[0], s[1])] for s in L["samples"]]
    for a, b in zip(sm, sm[1:]):
        if b[2] > a[2]:
            px_per_nm.append(math.hypot(b[0] - a[0], b[1] - a[1]) / (b[2] - a[2]))
    legs_out[leg] = {"nm": L["nm"], "s": sm, "dep": leg_times[leg][0], "arr": leg_times[leg][1], "zones": zones[leg]}
PXNM = sum(px_per_nm) / len(px_per_nm)

def parse(t):
    return datetime.fromisoformat(t.replace("Z", "+00:00"))

poi_events = []
for leg, L in legs_out.items():
    for k, (name, text) in POIS.items():
        if k not in R["pts"]:
            continue
        x, y = R["pts"][k]
        best = min(L["s"], key=lambda s: (s[0] - x) ** 2 + (s[1] - y) ** 2)
        off_nm = math.hypot(best[0] - x, best[1] - y) / PXNM
        if off_nm <= 60 and 3 < best[2] < L["nm"] - 3:
            poi_events.append({"leg": leg, "along": best[2], "k": k, "name": name, "text": text, "off": round(off_nm)})
        elif k == "cb" and off_nm <= 60:
            poi_events.append({"leg": leg, "along": best[2], "k": k, "name": name, "text": text, "off": round(off_nm)})
tropic = R["tropic"]

def leg_time_at(leg, along):
    L = legs_out[leg]
    d0, d1 = parse(L["dep"]), parse(L["arr"])
    return d0 + (d1 - d0) * (along / L["nm"])

def zone_at(leg, along):
    z = -8
    for a, off in legs_out[leg]["zones"]:
        if along >= a:
            z = off
    return z

def local(dt, off):
    return (dt + timedelta(hours=off)).strftime("%a %b %d %I:%M %p").replace(" 0", " ")

print("== POI passing times (local where the ship is) ==")
for e in sorted(poi_events, key=lambda e: leg_time_at(e["leg"], e["along"])):
    t = leg_time_at(e["leg"], e["along"])
    print(f'{e["leg"]:6} {e["name"]:22} along {e["along"]:6.1f} nm  off {e["off"]:3} nm  {local(t, zone_at(e["leg"], e["along"]))} (UTC{zone_at(e["leg"], e["along"])})')
for leg, a in tropic.items():
    t = leg_time_at(leg, a)
    print(f"Tropic {leg}: {local(t, zone_at(leg, a))} (UTC{zone_at(leg, a)})")
total_nm = sum(L["nm"] for L in legs_out.values())
print("total nm", total_nm, "mi", round(total_nm * NM_TO_MI), "px/nm", round(PXNM, 3))

# ------------------------------------------------------------ HTML helpers
def icon(name):
    paths = {
        "trip": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5 13 13l-4.5 2.5L11 11z"/>',
        "ship": '<path d="M3 15h18l-2.5 4.5H5.5z"/><path d="M6 15V10h12v5"/><path d="M9 10V6.5h5V10"/>',
        "ports": '<circle cx="12" cy="5" r="2"/><path d="M12 7v13"/><path d="M8 11h8"/><path d="M4.5 13.5C5 17.5 8 20 12 20s7-2.5 7.5-6.5"/>',
        "play": '<rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r="1.1" fill="currentColor"/><circle cx="15" cy="15" r="1.1" fill="currentColor"/><circle cx="15" cy="9" r="1.1" fill="currentColor"/><circle cx="9" cy="15" r="1.1" fill="currentColor"/>',
        "pack": '<rect x="4" y="8" width="16" height="12" rx="2"/><path d="M9 8V5.5h6V8"/><path d="M4 13h16"/>',
    }
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>'

CHEV = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'

def h(s):
    return esc(s, quote=False)

def sec(eyebrow, title, body, intro=None, sid=None):
    i = f"<p>{h(intro)}</p>" if intro else ""
    idattr = f' id="{sid}"' if sid else ""
    return f'<section class="sec"{idattr}><header><span class="eyebrow">{h(eyebrow)}</span><h2>{h(title)}</h2>{i}</header>{body}</section>'

def facts_list(items, show=10, more_label="facts"):
    first = "".join(f"<li>{h(x)}</li>" for x in items[:show])
    rest = "".join(f"<li>{h(x)}</li>" for x in items[show:])
    out = f'<ol class="facts card">{first}</ol>'
    if rest:
        out = f'<div class="card"><ol class="facts">{first}</ol><details class="more"><summary>{len(items) - show} more {more_label}</summary><ol class="facts" start="{show + 1}" style="counter-reset:f {show}">{rest}</ol></details></div>'
    return out

def tl(items):
    return '<div class="timeline card">' + "".join(f'<details><summary><b>{h(y)}</b><span>{h(t)}</span></summary><p>{h(d)}</p></details>' for y, t, d in items) + "</div>"

def statgrid(stats):
    return '<div class="statgrid">' + "".join(f"<div><b>{h(v)}</b><span>{h(l)}</span>{f'<small>{h(n)}</small>' if n else ''}</div>" for v, l, n in stats) + "</div>"

def kv_list(cls, items):
    return f'<dl class="{cls}">' + "".join(f"<div><dt>{h(a)}</dt><dd>{h(b)}</dd></div>" for a, b in items) + "</dl>"

def hm(t):
    hh, mm = map(int, t.split(":"))
    return hh + mm / 60

def ampm(t):
    hh, mm = map(int, t.split(":"))
    suf = "am" if hh < 12 else "pm"
    hh = hh % 12 or 12
    return f"{hh}:{mm:02d} {suf}"

# ------------------------------------------------------------ planner
EFFORT = {"Chill": "var(--sea)", "Easy": "var(--c-pv)", "Moderate": "var(--c-cb)", "Active": "var(--accent)"}

def vibe_cards(pid):
    out = '<div class="vibes">'
    for v in VIBES[pid]:
        blocks = "".join(f"<div><dt>{h(w)}</dt><dd>{h(t)}<small>{h(d)}</small></dd></div>" for w, t, d in v["blocks"])
        bring = '<div class="bring"><span class="eyebrow">Bring</span>' + "".join(f"<span>{h(x)}</span>" for x in v["bring"]) + "</div>"
        also = f'<p class="note">{h(v["also"])}</p>' if v.get("also") else ""
        out += (f'<article class="card vibe" style="--ec:{EFFORT[v["effort"]]}"><header><h3>{h(v["name"])}</h3><span class="effort">{h(v["effort"])}</span></header>'
                f'<p class="pitch">{h(v["pitch"])}</p><dl class="steps">{blocks}</dl>{bring}{also}</article>')
    return out + "</div>"


def port_bar(port):
    p = port["plan"]
    o0, o1 = hm(p["open"]), hm(p["close"])
    span = o1 - o0
    hours = ""
    for hh in range(math.ceil(o0), int(o1) + 1):
        l = (hh - o0) / span * 100
        hours += f'<span style="left:{l:.2f}%">{hh % 12 or 12}{"a" if hh < 12 else "p"}</span>'
    c = (hm(p["back"]) - o0) / span * 100
    ab = (hm(p["aboard"]) - o0) / span * 100
    ashore = (hm(p["back"]) - o0) - (1.0 if port["id"] == "cb" else 0.5)
    date = next(d["date"] for d in DAYS if d.get("port") == port["id"])
    cd = f'<div class="countdown" data-date="{date}" data-utc="{p["utc"]}" data-aboard="{p["aboard"]}" data-open="{p["open"]}" data-close="{p["close"]}"><span>On board by {ampm(p["aboard"])}</span><b>--</b></div>'
    where = "pier" if port["id"] == "cb" else "gate"
    return (f'{cd}<div class="card portbar"><div class="track" data-open="{p["open"]}" data-close="{p["close"]}">'
            f'<div class="blk ashore" style="left:0;width:{c:.2f}%"><span>About {ashore:.0f} h ashore{" after tender lines" if port["id"] == "cb" else ""}</span></div>'
            f'<div class="blk margin" style="left:{c:.2f}%;width:{ab - c:.2f}%"></div>'
            f'<div class="cut" style="left:{ab:.2f}%"></div></div><div class="hours">{hours}</div>'
            f'<p class="small muted">Ship in port {ampm(p["open"])}–{ampm(p["close"])}. Plan to be back at the {where} by <b>{ampm(p["back"])}</b>; all aboard is about <b>{ampm(p["aboard"])}</b> (dashed line). Confirm in the daily program.</p></div>')


# ------------------------------------------------------------ views
def night_sky():
    rows = SKY.compute()
    W, L, R, T = 400, 62, 8, 26
    rh = 34
    H = T + rh * len(rows) + 30
    span = 16.0
    x = lambda hrs: L + (hrs - SKY.START_H) / span * (W - L - R)
    o = [f'<svg class="chart sky" viewBox="0 0 {W} {H}" role="img" aria-label="Each night from Dec 26 to Jan 1: the darkest stretch runs from the end of twilight until moonrise, growing from about 2 hours on Dec 26 to about 7 hours by Jan 1.">']
    for hh in range(16, 33, 2):
        xx = x(hh)
        o.append(f'<line class="gridl" x1="{xx:.1f}" y1="{T - 4}" x2="{xx:.1f}" y2="{H - 24}"/>')
        lab = f"{hh % 12 or 12}{'a' if hh % 24 < 12 else 'p'}"
        o.append(f'<text class="a" x="{xx:.1f}" y="{H - 12}" text-anchor="middle">{lab}</text>')
    for i, r in enumerate(rows):
        y = T + i * rh
        bh = 18
        o.append(f'<text x="{L - 8}" y="{y + 10}" text-anchor="end" font-weight="600">{r["md"]}</text><text class="a" x="{L - 8}" y="{y + 21}" text-anchor="end">{r["dow"].upper()}</text>')
        # day, twilight, night
        o.append(f'<rect class="s-day" x="{x(SKY.START_H):.1f}" y="{y}" width="{x(r["sunset"]) - x(SKY.START_H):.1f}" height="{bh}" rx="3"/>')
        o.append(f'<rect class="s-twi" x="{x(r["sunset"]):.1f}" y="{y}" width="{x(r["dusk"]) - x(r["sunset"]):.1f}" height="{bh}"/>')
        o.append(f'<rect class="s-night" x="{x(r["dusk"]):.1f}" y="{y}" width="{x(r["dawn"]) - x(r["dusk"]):.1f}" height="{bh}"/>')
        o.append(f'<rect class="s-twi" x="{x(r["dawn"]):.1f}" y="{y}" width="{x(r["sunrise"]) - x(r["dawn"]):.1f}" height="{bh}"/>')
        o.append(f'<rect class="s-day" x="{x(r["sunrise"]):.1f}" y="{y}" width="{x(32) - x(r["sunrise"]):.1f}" height="{bh}" rx="3"/>')
        # moonlit stretch
        m0 = max(r["moonrise"], r["sunset"])
        m1 = min(r["sunrise"], 32)
        if m0 < m1:
            o.append(f'<rect class="s-moon" x="{x(m0):.1f}" y="{y}" width="{x(m1) - x(m0):.1f}" height="{bh}"/>')
        # dark window outline + label
        if r["dark"] > 0.3:
            d1 = min(r["moonrise"], r["dawn"])
            o.append(f'<rect class="s-dark" x="{x(r["dusk"]):.1f}" y="{y - 1}" width="{x(d1) - x(r["dusk"]):.1f}" height="{bh + 2}" rx="3"/>')
            wpx = x(d1) - x(r["dusk"])
            lab = f'{r["dark"]:.1f} h dark' if wpx > 84 else f'{r["dark"]:.1f} h'
            o.append(f'<text class="v s-lab" x="{(x(r["dusk"]) + x(d1)) / 2 - (6 if wpx < 84 else 3):.1f}" y="{y + 12.5}" text-anchor="middle">{lab}</text>')
        # moon icon at moonrise
        mx = x(r["moonrise"])
        k = r["illum"] / 100.0
        o.append(f'<g transform="translate({mx:.1f},{y + bh / 2})"><circle r="6" class="s-moondisc"/><path d="M0,-6 A6,6 0 0 1 0,6 A{abs(6 * (1 - 2 * k)):.2f},6 0 0 {1 if k < .5 else 0} 0,-6 Z" class="s-moonshade"/></g>')
        right = mx + 168 > W - R
        o.append(f'<text class="a" x="{(mx - 9) if right else (mx + 9):.1f}" y="{y + bh + 9}" text-anchor="{"end" if right else "start"}">moonrise {SKY.clock(r["moonrise"])} · {r["illum"]}% lit</text>')
    o.append(f'<g transform="translate({L},10)" class="legend"><rect class="s-night" width="12" height="9" rx="2"/><text x="16" y="8">Dark sky</text><rect class="s-moon" x="72" width="12" height="9" rx="2"/><text x="88" y="8">Moon up</text><rect class="s-twi" x="142" width="12" height="9" rx="2"/><text x="158" y="8">Twilight</text><rect class="s-day" x="212" width="12" height="9" rx="2" style="stroke:var(--rule)"/><text x="228" y="8">Day</text></g>')
    o.append("</svg>")
    chart = f'<figure class="card"><div class="svgbox">{"".join(o)}</div><figcaption>Ship time at approximate positions along the route. "Dark" means after astronomical twilight and before moonrise: the best window for the Milky Way and faint stars. Last quarter moon is Dec 30.</figcaption></figure>'
    targets = '<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">What to look for</h3><dl class="dl">' + "".join(f"<div><dt>{h(n)} <span class=\"when\">{h(w)}</span></dt><dd>{h(d)}</dd></div>" for n, w, d in SKY_TARGETS) + "</dl></div>"
    tips = '<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">How to stargaze from the ship</h3><ul class="ticks">' + "".join(f"<li>{h(t)}</li>" for t in SKY_TIPS) + "</ul></div>"
    apps = '<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">Apps</h3>' + kv_list("dl", SKY_APPS) + "</div>"
    return chart + targets + f'<div class="grid2">{tips}{apps}</div>'


def view_trip():
    k = lambda v, l, n="": f"<div class=\"kpi\"><b>{v}</b><span>{l}</span>{f'<small>{n}</small>' if n else ''}</div>"
    hero = f'''<div class="hero"><span class="coords">32°43′N 117°10′W → 20°39′N 105°15′W → 23°12′N 106°25′W → 22°53′N 109°55′W → home</span>
<h1>Mexican Riviera Holiday</h1><p class="lede">Seven nights on ms Koningsdam: down the Baja coast, three Mexican ports, and New Year's Eve at sea.</p>
<div class="kpis">{k(f"{total_nm:,} nm", "total distance", f"≈ {round(total_nm * NM_TO_MI):,} statute miles")}{k("7", "nights", "Dec 26 – Jan 2")}{k("3", "time zones", "UTC−8, −7 and −6")}{k("2×", "Tropic of Cancer", "crossed Dec 28 and Dec 31")}</div></div>'''

    legs = '<div class="legs card"><div class="row h"><span>Leg</span><span>nm</span><span>hours</span><span>avg kn</span></div>'
    tot_h = 0
    for leg, (a, b, hrs) in LEG_NAMES.items():
        nm = legs_out[leg]["nm"]
        tot_h += hrs
        legs += f'<div class="row"><span>{h(a)} → {h(b)}</span><span class="data">{nm:,}</span><span class="data">{hrs}</span><span class="data">{nm / hrs:.1f}</span></div>'
    legs += f'<div class="row"><span>Total under way</span><span class="data">{total_nm:,}</span><span class="data">{tot_h}</span><span class="data">{total_nm / tot_h:.1f}</span></div></div>'
    route = f'''<div class="routewrap"><figure class="card"><div class="svgbox">{S.route_svg(M, poi_events)}</div>
<div class="jsonly" style="margin-top:12px"><div class="slider"><label class="eyebrow" for="voyage">Scrub through the voyage</label><input type="range" id="voyage" min="0" max="9480" step="10" value="0" aria-describedby="voyageOut"><div class="ticks-row"><span>Dec 26</span><span>Dec 28</span><span>Dec 30</span><span>Jan 1</span><span>Jan 2</span></div></div>
<div class="btnrow" style="margin:10px 0 12px"><button class="btn primary" id="vPlay" type="button">Play voyage</button><button class="btn" id="vNow" type="button">Jump to now</button></div>
<dl class="readout" id="voyageOut" aria-live="polite"><div><dt>Local time</dt><dd id="rTime">Sat Dec 26 · 5:00 pm</dd></div><div><dt>Status</dt><dd id="rStatus">Sailing from San Diego</dd></div><div><dt>Sailed</dt><dd id="rSailed">0 nm</dd></div><div><dt>Speed</dt><dd id="rSpeed">17.0 kn</dd></div><div class="wide"><dt>Nearby</dt><dd id="rNear">Point Loma and the lights of San Diego</dd></div></dl></div>
<figcaption>Track drawn from port coordinates and offshore waypoints; distances are measured along it. Holland America doesn't publish leg distances, so treat them as close estimates. Times on the slider assume a steady speed on each leg.</figcaption></figure>{legs}</div>'''

    days = '<div class="days">'
    for d in DAYS:
        port = d.get("port")
        pc = f' data-port="{port}" style="--pc:var(--c-{port})"' if port else ""
        items = "".join(f"<div><dt>{h(a)}</dt><dd>{h(b)}</dd></div>" for a, b in d["items"])
        sun = f'<span class="sun">Sunrise {d["sun"][0]} · sunset {d["sun"][1]}</span>' if d.get("sun") else ""
        link = f'<a href="#ports-{port}" class="small">Open the {h(PORTS[port]["name"])} page →</a>' if port else ""
        day, num = d["md"].split()
        days += f'''<details class="day" data-date="{d["date"]}"{pc}><summary><span class="date"><span>{d["dow"]}</span><b>{num}</b><span>{day}</span></span><span class="t"><small>{h(d["tag"])}</small><div>{h(d["title"])}</div></span>{CHEV}</summary>
<div class="body"><span class="sun">{h(d["zone"])}</span><dl class="items">{items}</dl>{sun}<p class="note">{h(d["note"])}</p>{link}</div></details>'''
    days += "</div>"

    weather = f'<figure class="card"><div class="svgbox">{S.weather_svg(WEATHER)}</div><figcaption>Climate averages for late December, not forecasts. The water warms about 19°F between San Diego and Puerto Vallarta, which is why a wetsuit matters at La Jolla but not in Mexico.</figcaption></figure>'

    tect = f'''<figure class="card"><div class="svgbox">{S.tect_svg(M)}</div>
<div class="jsonly" style="margin-top:12px"><div class="slider"><label class="eyebrow" for="tectR">Rewind time: <span id="tectOut">today</span></label><input type="range" id="tectR" min="0" max="60" step="1" value="0"><div class="ticks-row"><span>Today</span><span>2 Ma</span><span>4 Ma</span><span>6 Ma</span></div></div><div class="btnrow" style="margin-top:8px"><button class="btn" id="tectPlay" type="button">Play</button></div></div>
<figcaption>Baja rides the Pacific plate, sliding northwest past mainland Mexico at roughly 5 cm a year, about as fast as fingernails grow. Rewind about 6 million years (about 300 km) and the Sea of Cortez nearly closes. This is a simplified straight-line rewind; the real opening also stretched and rotated the crust.</figcaption></figure>'''

    return f'''<section class="view" id="trip" aria-label="Trip">{hero}
{sec("Route", "The voyage on a chart", route, "Southbound along Baja's Pacific coast, across the mouth of the Sea of Cortez to Banderas Bay, then north to Mazatlán, across to Cabo and home.")}
{sec("Day by day", "Eight days at a glance", days, "Tap a day for times. Today's card opens on its own during the trip.")}
{sec("Weather", "Air and water along the way", weather)}
{sec("Night sky", "Stargazing at sea", night_sky(), "Away from city lights the sky gets very dark. The moon was full on Dec 24, so each evening starts dark and the moon rises later every night.")}
{sec("Geology", "Why the Sea of Cortez exists", tect, "The water you cross on Dec 28 and Dec 31 is a young sea, opened by plate tectonics.")}
</section>'''


def cabin_deck(num):
    try:
        n = int(str(num).strip())
    except (TypeError, ValueError):
        return None
    return n // 1000 if 1000 <= n < 13000 else None


def cabins_card():
    rows = ""
    for c in CABINS:
        num = c.get("cabin")
        deck = cabin_deck(num)
        main = f'<b class="data">{h(str(num))}</b>' if num else f'<b class="tbd">{h(c.get("tbd", "Not added yet"))}</b>'
        meta = " · ".join(x for x in (c.get("type", ""), f"Deck {deck}" if deck else "", c.get("position", "")) if x)
        note = f'<small>{h(c["note"])}</small>' if c.get("note") else ""
        rows += f'<div><dt>{h(c["who"])}</dt><dd>{main}<span>{h(meta)}</span>{note}</dd></div>'
    return f'<div class="card"><dl class="cabins">{rows}</dl><p class="note">Cabin numbers start with the deck number (6123 is on deck 6). Tap that deck below to see what\'s nearby.</p></div>'


def view_ship():
    plate = '<dl class="plate">' + "".join(f"<div><dt>{h(a)}</dt><dd>{h(b)}</dd></div>" for a, b in SHIP_SPECS) + "</dl>"
    head = f'''<div class="hero"><span class="coords">IMO 9692557 · CALL SIGN PBGJ · PORT OF REGISTRY ROTTERDAM</span><h1>ms Koningsdam</h1><p class="lede">The first of Holland America's Pinnacle class, built in Venice in 2016 and christened by Queen Máxima.</p>{plate}</div>'''

    decklist = '<div class="decklist" id="deckList">'
    for d in DECKS:
        name = f'Deck {d["n"]}'
        sections = ""
        for sname, vs in d["venues"].items():
            sections += f'<div class="sect"><span>{h(sname) if sname else "·"}</span><span>{h(", ".join(vs))}</span></div>'
        tip = f'<p class="note">{h(d["tip"])}</p>' if d["tip"] else ""
        ours = [c for c in CABINS if cabin_deck(c.get("cabin")) == d["n"]]
        if ours:
            tip += '<p class="ourcab">' + " · ".join(f'Cabin {h(str(c["cabin"]))}: {h(c["who"])}' for c in ours) + "</p>"
        summary_v = ", ".join(v for vs in d["venues"].values() for v in vs)
        if len(summary_v) > 38:
            summary_v = summary_v[:36].rsplit(",", 1)[0] + "…"
        decklist += f'<details class="deck" id="deck{d["n"]}" data-deck="{d["n"]}"><summary><b>{name}</b><span>{h(d["name"] or "")}</span><em>{h(summary_v)}</em></summary><div class="body">{sections}{tip}</div></details>'
    decklist += "</div>"
    deck = f'''<figure class="card"><div class="svgbox">{S.deck_svg(DECKS)}</div><figcaption>Not to scale. Venue positions (fore, mid, aft) follow Holland America's deck pages. Also aboard: {h(", ".join(ELSEWHERE))}; check the deck plan in the Navigator app for exact spots.</figcaption></figure>{decklist}'''

    power = f'''<div class="card" style="display:grid;gap:12px"><div class="svgbox">{S.power_svg()}</div>
<div class="jsonly"><div class="speedbig"><b id="spdOut">18.0</b><span>knots</span></div><div class="slider"><label class="eyebrow" for="spd">Ship speed</label><input type="range" id="spd" min="0" max="22.2" step="0.1" value="18"><div class="ticks-row"><span>In port</span><span>11</span><span>18 service</span><span>22.2 max</span></div></div>
<div class="btnrow" style="margin-top:8px" id="spdPresets"><button class="pill" data-v="0" type="button">In port</button><button class="pill" data-v="11.5" type="button">PV → Mazatlán</button><button class="pill" data-v="17" type="button">Down Baja</button><button class="pill on" data-v="18" type="button">Service 18</button><button class="pill" data-v="22.2" type="button">Flat out</button></div></div>
<div class="gauges" id="gauges"><div><b id="gTotal">23.4 MW</b><span>electrical load</span></div><div><b id="gHp">31,400 hp</b><span>equivalent</span></div><div><b id="gEng">3 of 4</b><span>engines online</span></div><div><b id="gFuel">107 t</b><span>fuel per day</span></div><div><b id="gGph">1,190 gal</b><span>fuel per hour</span></div><div><b id="gGpm">57 gal</b><span>per statute mile</span></div><div><b id="gPmpg">46</b><span>passenger-miles per gallon</span></div><div><b id="gCo2">332 t</b><span>CO₂ per day</span></div><div><b id="gLeg">58 h</b><span>San Diego → Vallarta at this speed</span></div></div>
<p class="note">Estimates, not Holland America figures. The model assumes the pods reach their 28 MW at the 22.2-knot maximum, propulsion power rising with speed cubed, an 8.5 MW hotel load, about 190 g of fuel per kWh, generators kept under 85% load, and 2,650 guests.</p></div>'''

    size = f'<figure class="card"><div class="svgbox">{S.size_svg()}</div><div class="svgbox" style="margin-top:14px">{S.tonnage_svg()}</div><figcaption>Gross tonnage measures enclosed volume, not weight. Titanic\'s figure is in the older gross register tons, which are close but not identical.</figcaption></figure>'

    wifi = '<div class="card" style="display:grid;gap:10px"><h3>Phones at sea</h3><ul class="ticks small"><li>Keep phones in airplane mode at sea. The ship\'s maritime cell network roams at high rates, even for texts.</li><li>The Navigator app runs on the ship\'s network without a paid Wi-Fi plan: daily program, deck plans and your account.</li><li>GPS still works in airplane mode, so offline maps and Sky Guide know where you are.</li><li>In port, check whether your phone plan includes Mexico, or set up a Mexico eSIM before you go.</li></ul></div>'

    return f'''<section class="view" id="ship" aria-label="Ship">{head}
{sec("Our group", "Cabins", cabins_card())}
{sec("Deck explorer", "Twelve decks, bow to stern", deck, "Tap a deck on the profile, or open one below.")}
{sec("Power lab", "How a diesel-electric ship moves", power, "Four generators make electricity. Everything else, including the propellers, is an electrical load. Drag the speed and watch the plant respond.")}
{sec("Scale", "How big is 300 meters?", size)}
{sec("The ship", f"{len(SHIP_FACTS)} facts about Koningsdam", facts_list(SHIP_FACTS))}
{sec("The line", f"Holland America Line · {len(HAL_FACTS)} facts", facts_list(HAL_FACTS) + wifi)}
</section>'''


def port_page(pid):
    p = PORTS[pid]
    meta = "".join(f"<span>{h(x)}</span>" for x in (p["when"], p["mode"], p["zone"]))
    head = f'<div class="porthead"><span class="coords">{h(p["coords"])} · {h(p["state"]).upper()}</span><h2>{h(p["name"])}</h2><p>{h(p["tagline"])}</p><div class="meta">{meta}</div></div>'
    parts = [head]
    flags = ""
    if pid == "pv":
        flags = '<div class="flag"><b>Note</b><span>This cruise\'s Puerto Vallarta day is a Tuesday. The Marietas Hidden Beach is closed Mondays and Tuesdays, so choose a snorkel-only Marietas trip or Los Arcos instead.</span></div>'
    if pid == "mz":
        flags = '<div class="flag crit"><b>Level 4</b><span>Sinaloa carries a U.S. "Do not travel" advisory. The cruise exception covers the historic center and the Malecón only. The ideas below stay inside it.</span></div>'
    if pid == "cb":
        flags = '<div class="flag"><b>Tender day</b><span>Ship tours board the tenders first, and lines can run 45 minutes. Be at the pier 45–60 minutes before the last tender.</span></div>'
    if pid == "sd":
        parts.append(sec("Dec 26", "Embarkation day", '<div class="card"><ul class="ticks">' + "".join(f"<li>{h(x)}</li>" for x in SD_EMBARK) + "</ul></div>"))
        parts.append(sec("Jan 2", "Getting off the ship", '<div class="card"><ul class="ticks">' + "".join(f"<li>{h(x)}</li>" for x in SD_DISEMBARK) + "</ul></div>"))
        parts.append(sec("Jan 2", "Ways to spend the day", vibe_cards("sd"), "Nothing here is booked. Pick a vibe, mix them, or split up."))
    else:
        parts.append(sec("Port day", f"{p['name']}: pick a vibe", flags + port_bar(p) + vibe_cards(pid), "A few loose ways to spend the day. Mix them, split up, or swap in a ship excursion."))
    # map
    if pid == "pv":
        parts.append(sec("Map", "Banderas Bay", f'<figure class="card"><div class="svgbox">{S.pv_svg(M)}</div><figcaption>Coastline from OpenStreetMap-derived data, simplified. The terminal is 3 miles north of downtown; Boca de Tomatlán is 40–45 minutes south by road.</figcaption></figure>'))
    if pid == "mz":
        parts.append(sec("Map", "The old town and El Faro", f'<figure class="card"><div class="svgbox">{S.mz_svg()}</div><figcaption>Schematic. The shaded zone is an approximation of the advisory wording: the historic center from Avenida Gutiérrez Nájera to the ocean, and the Malecón north to Route 503.</figcaption></figure>'))
    if pid == "cb":
        parts.append(sec("Map", "Land's End", f'<figure class="card"><div class="svgbox">{S.cabo_svg()}</div><figcaption>Schematic. Lover\'s Beach and Divorce Beach share one strip of sand: calm bay on one side, Pacific surf on the other.</figcaption></figure>'))
    # stats + chart
    pops = [("San Diego", 1.39), ("Mazatlán", 0.50), ("Los Cabos", 0.35), ("Puerto Vallarta", 0.29)]
    hl = {"sd": "San Diego", "mz": "Mazatlán", "cb": "Los Cabos", "pv": "Puerto Vallarta"}[pid]
    chart = S.hbar_svg(pops, {hl}, "Population of each port city or municipality, 2020 census", lambda v: f"{v:.2f} M", note="City (San Diego) or municipality (Mexico), 2020 census")
    parts.append(sec("By the numbers", "At a glance", f'<div style="--pc:var(--c-{pid})">{statgrid(p["stats"])}</div><figure class="card"><div class="svgbox">{chart}</div></figure>'))
    parts.append(sec("Overview", "What it's known for", '<div class="card prose">' + "".join(f"<p>{h(x)}</p>" for x in p["overview"]) + '</div><div class="chips">' + "".join(f'<span class="chip">{h(x)}</span>' for x in p["known"]) + "</div>"))
    parts.append(sec("History", "From first peoples to now", f'<div style="--pc:var(--c-{pid})">{tl(p["history"])}</div>', "Tap an era to expand it."))
    parts.append(sec("Fun facts", f"{len(p['facts'])} things to know about {p['name']}", facts_list(p["facts"])))
    if pid == "sd":
        z = ZOO
        zoo_stats = '<div class="statgrid" style="--pc:var(--c-sd)">' + "".join(f"<div><b>{h(v)}</b><span>{h(l)}</span></div>" for v, l in z["stats"]) + "</div>"
        route = '<div class="card"><h3 style="font-size:1rem;margin-bottom:10px">Morning route</h3><dl class="zooroute">' + "".join(f"<div><dt>{ampm(t if len(t) == 5 else '0' + t)}</dt><i></i><dd><b>{h(n)}</b><small>{h(d)}</small></dd></div>" for t, n, d in z["route"]) + '</dl><p class="note">Stops in order, not a map. Grab the paper map at the gate or use the Zoo app for paths.</p></div>'
        pandas = '<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">The pandas</h3><ul class="ticks">' + "".join(f"<li>{h(x)}</li>" for x in z["pandas"]) + "</ul></div>"
        prac = '<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">Tickets, hours, parking</h3><ul class="ticks">' + "".join(f"<li>{h(x)}</li>" for x in z["practical"]) + "</ul></div>"
        parts.append(sec("Jan 2", "San Diego Zoo", zoo_stats + f'<div class="grid2">{route}<div style="display:grid;gap:12px">{pandas}{prac}</div></div>' + facts_list(z["facts"], more_label="Zoo facts") + f'<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">Safari Park instead?</h3><p>{h(z["safari"])}</p></div>', "If you go: it opens at 9 am. See the pandas first, while they're active."))
        parts.append(sec("More San Diego", "Other good stops on Jan 2", '<div class="card">' + kv_list("dl", z["more"]) + "</div>"))
    # practical
    prac = []
    if p.get("getting"):
        prac.append('<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">Getting ashore</h3><ul class="ticks">' + "".join(f"<li>{h(x)}</li>" for x in p["getting"]) + "</ul></div>")
    if p.get("snorkel"):
        prac.append('<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">Snorkeling & animals</h3><ul class="ticks">' + "".join(f"<li>{h(x)}</li>" for x in p["snorkel"]) + "</ul></div>")
    if p.get("safety"):
        prac.append('<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">Safety</h3><ul class="ticks">' + "".join(f"<li>{h(x)}</li>" for x in p["safety"]) + "</ul></div>")
    if p.get("nye"):
        prac.append(f'<div class="card"><h3 style="font-size:1rem;margin-bottom:6px">New Year\'s Eve in Cabo</h3><p>{h(p["nye"])}</p></div>')
    if prac:
        parts.append(sec("Practical", "Know before you go ashore", '<div class="grid2">' + "".join(prac) + "</div>"))
    if p.get("eat"):
        parts.append(sec("Eat & drink", "What to order", '<div class="grid2"><div class="card">' + kv_list("eats", p["eat"]) + '</div><div class="card"><h3 style="font-size:1rem;margin-bottom:4px">Handy here</h3>' + kv_list("phr", p["phrases"]) + '<a class="small" href="#ports-mx">Full phrasebook on the Mexico page →</a></div></div>'))
    return f'<article class="port" id="ports-{pid}" style="--pc:var(--c-{pid})">' + "".join(parts) + "</article>"


def mexico_page():
    x = MEXICO
    head = '<div class="porthead" style="--pc:var(--c-mx)"><span class="coords">ESTADOS UNIDOS MEXICANOS · 32 STATES</span><h2>Mexico briefing</h2><p>Country numbers, the three states you visit, money, manners, New Year\'s traditions and Spanish for the week.</p></div>'
    gdp = S.hbar_svg(x["gdp_share"], {"Jalisco", "Sinaloa", "Baja California Sur"}, "Share of Mexico's GDP by state, 2024", lambda v: f"{v:.2f}%", note="Preliminary 2024 figures, IIEG / INEGI. Your three states highlighted.", labw=136)
    pax = S.hbar_svg(x["cruise_pax"], {"Cabo San Lucas", "Puerto Vallarta", "Mazatlán"}, "Cruise passengers per year at Mexican Pacific ports", lambda v: f"{v:.2f} M", note="Years differ; Mazatlán's 2025 figure runs to Nov 4.", labw=136)
    adv = '<dl class="adv">' + "".join(f'<div><b>{h(a)}</b><em class="l{b[-1]}">{h(b)}</em><p>{h(c)}</p></div>' for a, b, c in x["advisory"]) + "</dl>"
    tips = kv_list("dl", x["tipping"])
    parts = [head,
             sec("Country", "Mexico by the numbers", f'<div style="--pc:var(--c-mx)">{statgrid(x["stats"])}</div><div class="card"><h3 style="font-size:1rem;margin-bottom:6px">What Mexico sells</h3><ul class="ticks">' + "".join(f"<li>{h(e)}</li>" for e in x["exports"]) + "</ul></div>"),
             sec("States", "Where your three states rank", f'<figure class="card"><div class="svgbox">{gdp}</div><figcaption>Jalisco is Mexico\'s fourth-largest state economy. Baja California Sur is one of the smallest but among the fastest-growing.</figcaption></figure><figure class="card"><div class="svgbox">{pax}</div><figcaption>Ensenada, which you pass on the first night, was Mexico\'s busiest Pacific cruise port in 2025.</figcaption></figure>'),
             sec("Safety", "U.S. travel advisory by state", f'<div class="card">{adv}</div><div class="card"><h3 style="font-size:1rem;margin-bottom:4px">Why the levels are what they are</h3>' + kv_list("dl", x["advisory_why"]) + '</div><div class="card"><h3 style="font-size:1rem;margin-bottom:6px">If something flares up while you\'re ashore</h3><ul class="ticks">' + "".join(f"<li>{h(t)}</li>" for t in x["flare"]) + '</ul></div><p class="note">Advisory as reissued May 29, 2026; figures from Sinaloa state data reported in September 2026. Recheck travel.state.gov the week before you sail.</p>'),
             sec("Manners & money", "Etiquette and tipping", '<div class="grid2"><div class="card"><ul class="ticks">' + "".join(f"<li>{h(e)}</li>" for e in x["etiquette"]) + f'</ul></div><div class="card"><h3 style="font-size:1rem;margin-bottom:4px">Tipping</h3>{tips}</div></div>'),
             sec("Traditions", "Late December in Mexico", '<div class="card">' + kv_list("dl", x["traditions"]) + "</div>"),
             sec("Phrasebook", "Spanish for the week", '<div class="card">' + kv_list("phr", x["phrases"]) + "</div>")]
    return '<article class="port" id="ports-mx" style="--pc:var(--c-mx)">' + "".join(parts) + "</article>"


def view_ports():
    order = [("sd", "San Diego"), ("pv", "Puerto Vallarta"), ("mz", "Mazatlán"), ("cb", "Cabo"), ("mx", "Mexico")]
    nav = '<nav class="portnav" aria-label="Ports"><div class="seg">' + "".join(f'<a class="pill" href="#ports-{k}" data-port="{k}" style="--dot:var(--c-{k})"><span class="dot"></span>{h(n)}</a>' for k, n in order) + "</div></nav>"
    pages = "".join(port_page(k) for k in ("sd", "pv", "mz", "cb")) + mexico_page()
    return f'<section class="view" id="ports" aria-label="Ports">{nav}{pages}</section>'


def view_play():
    order = ["Ship", "Line", "Route", "PV", "MZT", "CSL", "Mexico", "Spanish", "Food", "San Diego", "Animals", "Sky"]
    cats = sorted({q[0] for q in QUIZ}, key=lambda c: order.index(c))
    counts = {c: sum(1 for q in QUIZ if q[0] == c) for c in cats}
    quiz = f'''<div class="card quiz jsonly" id="quiz"><div class="seg" id="qCats"><button class="pill on" data-c="all" type="button">All</button>{"".join(f'<button class="pill" data-c="{h(c)}" type="button">{h(c)} <span class="n">{counts[c]}</span></button>' for c in cats)}</div>
<div class="meta"><span id="qProg">Question 1</span></div><p class="q" id="qText">…</p><div class="opts" id="qOpts"></div><p class="ex" id="qEx"></p>
<div class="btnrow"><button class="btn primary" id="qNext" type="button">Next question</button><button class="btn" id="qRestart" type="button">Shuffle</button></div></div>'''
    shuffle = '<div class="card factcard jsonly" id="factCard"><span class="eyebrow" id="fcSrc">Random fact</span><p class="f" id="fcText">…</p><div class="btnrow"><button class="btn primary" id="fcNext" type="button">Another fact</button></div></div>'
    critters = '<div class="critters">'
    for w in WILDLIFE:
        critters += f'''<article class="card critter" id="w-{w["id"]}">{photo(w["id"], w["name"])}<header><div><h3>{h(w["name"])}</h3><span class="sci">{h(w["sci"])}</span></div><label class="spot"><input type="checkbox" data-spot="{w["id"]}" id="spot-{w["id"]}"> Spotted</label></header>
<div class="tags"><span>{h(w["when"])}</span><span>{h(w["odds"])}</span></div><p><b>Where:</b> {h(w["where"])}</p><p><b>ID:</b> {h(w["id_tip"])}</p><p class="f">{h(w["fact"])}</p></article>'''
    critters += "</div>"
    wid = f'<figure class="card"><div class="svgbox">{S.whale_id_svg()}</div><figcaption>Blow shape and the back are your best clues at a distance. Gray whales are the likeliest off Baja on Dec 27 and Jan 1; humpbacks in Banderas Bay and off Land\'s End.</figcaption></figure>'
    cards = '<div class="games">'
    for g in CARDS:
        steps = "".join(f"<li>{h(x)}</li>" for x in g["play"])
        cards += (f'<details class="card game"><summary><span><b>{h(g["name"])}</b><small>{h(g["kind"])}</small></span><em>{h(g["players"])}</em></summary>'
                  f'<div class="body"><p class="goal">{h(g["goal"])}</p><dl class="dl"><div><dt>Setup</dt><dd>{h(g["setup"])}</dd></div>'
                  f'<div><dt>Play</dt><dd><ul class="ticks">{steps}</ul></dd></div><div><dt>Scoring</dt><dd>{h(g["score"])}</dd></div></dl>'
                  f'<p class="note">{h(g["tip"])} · About {h(g["time"])}.</p></div></details>')
    cards += "</div>"
    games = '<div class="card">' + kv_list("dl", GAMES) + '<p class="note" style="margin-top:8px">Ships usually stock games and puzzles near the Crow\'s Nest and Explorations Café, but the good ones go fast on sea days.</p></div>'
    return f'''<section class="view" id="play" aria-label="Play">
<div class="hero"><span class="coords">SEA DAYS · DEC 27 · DEC 28 · JAN 1</span><h1>Sea-day deck</h1><p class="lede">Trivia, a fact deck, a wildlife field guide and rules for card games, for whenever you have a quiet hour.</p></div>
{sec("Sea days", "Trivia", quiz, f"{len(QUIZ)} questions on the ship, the ports, Mexico, Spanish, wildlife and the night sky. Pick a category or shuffle them all.")}
{sec("Fact shuffle", "One fact at a time", shuffle, "Draws from all the ship, line, port and Zoo facts in this guide.")}
{sec("Field guide", "Which whale is that?", wid)}
{sec("Checklist", "Wildlife you might see", '<p class="small muted" id="spotCount" style="margin-top:-4px"></p>' + critters, "Tick what you spot. It saves on this phone.")}
{sec("Card games", "Rules for a standard deck", cards, "Tap a game for the rules. These are the common versions; agree on house rules before you start.")}
{sec("Games", "Small games that travel well", games)}
</section>'''


def view_pack():
    checks = '<div class="checks" id="packList">'
    for gi, (cat, items) in enumerate(PACKING):
        checks += f"<fieldset><legend>{h(cat)}</legend>" + "".join(f'<label for="pk{gi}-{ii}"><input type="checkbox" id="pk{gi}-{ii}" data-pack="{gi}-{ii}"><span>{h(it)}</span></label>' for ii, it in enumerate(items)) + "</fieldset>"
    checks += "</div>"
    prog = '<div class="card jsonly" style="display:grid;gap:8px"><div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px"><b id="packCount">0 of 0 packed</b><span class="small muted" id="countdown2"></span></div><div class="progress"><i id="packBar"></i></div><div class="btnrow"><button class="btn" id="packReset" type="button">Clear all ticks</button><button class="btn" id="packConfirm" type="button" hidden>Yes, clear them</button></div></div>'
    dls = '<div class="card">' + kv_list("dl", DOWNLOADS) + "</div>"
    how = f'''<div class="card" style="display:grid;gap:12px"><h3>Put it on your home screen</h3><ol class="how">
<li><span>On your iPhone, open <b>{SITE_URL}</b> in Safari while you have a connection.</span></li>
<li><span>Tap Share, then <b>Add to Home Screen</b>.</span></li>
<li><span>Open it once from the home screen. From then on it works in airplane mode at sea.</span></li>
<li><span>When the guide is updated, open it once with a connection and close it; the next launch shows the new version.</span></li></ol>
<p class="note">Packing ticks and wildlife sightings are saved on each phone separately. Android: open the link in Chrome and choose Install app or Add to Home screen.</p></div>'''
    colophon = '''<footer class="colophon"><span class="eyebrow">About this guide</span><p>Compiled October 2026 from Holland America, Fincantieri, the U.S. State Department, INEGI and IIEG, the San Diego Zoo Wildlife Alliance, the Congressional Research Service and port and tourism sources. Prices, hours and advisories change: recheck the week you sail. Distances, fuel and timing figures marked as estimates are calculations, not official numbers.</p><p>Coastlines from OpenStreetMap-derived data (© OpenStreetMap contributors, ODbL) and Natural Earth via geo-maps. Wildlife photos from Wikimedia Commons; each photo's author and license are on its card.</p></footer>'''
    return f'''<section class="view" id="pack" aria-label="Pack">
<div class="hero"><span class="coords">PACKING · OFFLINE KIT</span><h1>Before you go</h1><p class="lede">Tick things off as they go in the bag. Then download the offline kit while you still have a good connection at home.</p></div>
{sec("Checklist", "Packing list", prog + checks)}
{sec("Offline kit", "Download before you go", dls)}
{sec("This guide", "How to carry it", how)}
{colophon}
</section>'''


# ------------------------------------------------------------ data for JS
facts_pool = [("Koningsdam", f) for f in SHIP_FACTS] + [("Holland America", f) for f in HAL_FACTS] + [(PORTS[k]["name"], f) for k in ("sd", "pv", "mz", "cb") for f in PORTS[k]["facts"]] + [("San Diego Zoo", f) for f in ZOO["facts"]] + [(w["name"], w["fact"]) for w in WILDLIFE]
DATA = {
    "legs": legs_out, "legOrder": ["sd_pv", "pv_mz", "mz_cb", "cb_sd"], "pois": poi_events, "tropic": tropic,
    "calls": CALLS, "start": "2026-12-27T01:00:00Z", "end": "2027-01-02T15:00:00Z",
    "quiz": [{"c": c, "q": q, "o": o, "a": a, "x": x} for c, q, o, a, x in QUIZ],
    "facts": facts_pool, "decks": [d["n"] for d in DECKS],
    "dep": "2026-12-27T01:00:00Z",
}

def font_face():
    fd = os.path.join(ROOT, "fonts")
    faces = [("Newsreader", "normal", "newsreader-latin-wght-normal.woff2", "200 800"),
             ("Newsreader", "italic", "newsreader-latin-wght-italic.woff2", "200 800"),
             ("Martian Mono", "normal", "martian-mono-latin-wght-normal.woff2", "100 800")]
    css = ""
    for fam, style, path, wght in faces:
        b64 = base64.b64encode(open(os.path.join(fd, path), "rb").read()).decode()
        css += f'@font-face{{font-family:"{fam}";font-style:{style};font-weight:{wght};font-display:swap;src:url(data:font/woff2;base64,{b64}) format("woff2");}}\n'
    return css


def body_html(pwa=False):
    css = open(os.path.join(HERE, "styles.css")).read()
    js = open(os.path.join(HERE, "app.js")).read()
    tabs = [("trip", "Trip"), ("ship", "Ship"), ("ports", "Ports"), ("play", "Play"), ("pack", "Pack")]
    tabbar = '<nav class="tabbar" aria-label="Sections"><div class="wrap">' + "".join(f'<a href="#{k}" data-tab="{k}">{icon(k)}<span>{n}</span></a>' for k, n in tabs) + "</div></nav>"
    top = '<header class="topbar"><div class="wrap"><div class="brand"><b>Koningsdam</b><span>Mexican Riviera · Dec 26 – Jan 2</span></div><span class="status" id="status">7 nights · 3 ports</span></div></header>'
    main = '<main class="wrap">' + view_trip() + view_ship() + view_ports() + view_play() + view_pack() + "</main>"
    data = json.dumps(DATA, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    sw = "<script>if('serviceWorker' in navigator&&(location.protocol==='https:'||location.hostname==='localhost')){addEventListener('load',function(){navigator.serviceWorker.register('sw.js').catch(function(){})})}</script>" if pwa else ""
    return f'''<title>Koningsdam Voyage Guide</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>{font_face()}{css}</style>
<script>document.documentElement.classList.add('js')</script>
{top}{main}{tabbar}
<script type="application/json" id="guideData">{data}</script>
<script>{js}</script>{sw}'''


RESET = ':root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}'

def full_doc(body, pwa=False):
    extra = ""
    if pwa:
        extra = '<link rel="manifest" href="manifest.webmanifest"><link rel="apple-touch-icon" href="apple-touch-icon.png"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="default"><meta name="apple-mobile-web-app-title" content="Koningsdam"><meta name="theme-color" content="#F1F5F5">'
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">{extra}<style>{RESET}</style></head><body>{body}</body></html>'


SW = """// Offline cache for the Koningsdam guide. Bump VERSION to push an update.
const VERSION = "kdg-v1";
const FILES = ["./", "index.html", "manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request).then(res => {
    const copy = res.clone(); caches.open(VERSION).then(c => c.put(e.request, copy)); return res;
  }).catch(() => caches.match("index.html"))));
});
"""


def make_icons(d):
    from PIL import Image, ImageDraw
    for size, name in ((512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png")):
        S2 = size * 4
        im = Image.new("RGB", (S2, S2), (19, 36, 58))
        dr = ImageDraw.Draw(im)
        u = S2 / 100
        # route arc
        pts = [(18 + i * 0.64, 30 + 40 * (i / 100) ** 1.4) for i in range(0, 101, 2)]
        for i in range(0, len(pts) - 1, 2):
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            dr.line([(x1 * u, y1 * u), (x2 * u, y2 * u)], fill=(231, 100, 179), width=int(3.2 * u))
        for cx, cy in ((18, 30), (82, 70)):
            dr.ellipse([(cx - 4.5) * u, (cy - 4.5) * u, (cx + 4.5) * u, (cy + 4.5) * u], fill=(241, 245, 245), outline=(231, 100, 179), width=int(2 * u))
        # ship profile
        dr.polygon([(30 * u, 56 * u), (70 * u, 56 * u), (64 * u, 66 * u), (36 * u, 66 * u)], fill=(241, 245, 245))
        dr.rectangle([38 * u, 47 * u, 62 * u, 56 * u], fill=(241, 245, 245))
        dr.rectangle([44 * u, 40 * u, 54 * u, 47 * u], fill=(241, 245, 245))
        im = im.resize((size, size), Image.LANCZOS)
        im.save(os.path.join(d, name))


if __name__ == "__main__":
    out = os.path.join(ROOT, "dist")
    site = os.path.join(ROOT, "docs")
    os.makedirs(out, exist_ok=True)
    os.makedirs(site, exist_ok=True)
    art = body_html()
    open(os.path.join(out, "koningsdam-guide-artifact.html"), "w").write(art)
    open(os.path.join(out, "Koningsdam-Voyage-Guide.html"), "w").write(full_doc(art))
    open(os.path.join(site, "index.html"), "w").write(full_doc(body_html(pwa=True), pwa=True))
    open(os.path.join(site, ".nojekyll"), "w").write("")
    manifest = {"name": "Koningsdam Voyage Guide", "short_name": "Koningsdam", "start_url": "./", "scope": "./", "display": "standalone",
                "background_color": "#F1F5F5", "theme_color": "#13243A",
                "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}
    json.dump(manifest, open(os.path.join(site, "manifest.webmanifest"), "w"), indent=2)
    import hashlib
    ver = "kdg-" + hashlib.sha1(open(os.path.join(site, "index.html"), "rb").read()).hexdigest()[:10]
    open(os.path.join(site, "sw.js"), "w").write(SW.replace('"kdg-v1"', '"' + ver + '"'))
    make_icons(site)
    print("site:", site, os.path.getsize(os.path.join(site, "index.html")), "bytes; cache", ver)
