# SVG generators for the guide. All colors come from CSS classes / tokens.
import math
from html import escape as esc


def fmt(n, d=1):
    return f"{n:.{d}f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- route map
def route_svg(m, pois_along):
    r = m["route"]
    W, H = r["width"], r["height"]
    p = r["pts"]
    out = [f'<svg class="map" id="routeSvg" viewBox="0 0 {W} {H}" role="img" aria-label="Route map: San Diego south along Baja to Puerto Vallarta, north to Mazatlán, across to Cabo San Lucas and back up Baja to San Diego.">']
    out.append(f'<rect class="sea" width="{W}" height="{H}"/>')
    out.append(f'<path class="grid" fill="none" d="{r["graticule"]}"/>')
    # whale zones
    for k, rx, ry in (("ojo", 20, 13), ("sanig", 14, 10), ("mag", 16, 20)):
        x, y = p[k]
        out.append(f'<ellipse class="whale" cx="{x}" cy="{y}" rx="{rx}" ry="{ry}"/>')
    for k in ("cb", "pv"):
        x, y = p[k]
        out.append(f'<circle class="whale" cx="{x - 2}" cy="{y + 2}" r="18"/>')
    out.append(f'<path class="land" d="{r["land"]}"/>')
    ty = p["tropicW"][1]
    out.append(f'<line class="tropic" x1="0" y1="{ty}" x2="{W}" y2="{ty}"/>')
    out.append(f'<text class="d halo" x="4" y="{ty - 4}">TROPIC OF CANCER 23°26′N</text>')
    # graticule labels
    for k, lab in (("t_lat20", "20°N"), ("t_lat25", "25°N"), ("t_lat30", "30°N")):
        x, y = p[k]
        out.append(f'<text class="d" x="3" y="{y - 3}">{lab}</text>')
    for k, lab in (("t_lon115", "115°W"), ("t_lon110", "110°W"), ("t_lon105", "105°W")):
        x, y = p[k]
        out.append(f'<text class="d" x="{x - 3}" y="9" text-anchor="end">{lab}</text>')
    # routes
    for leg, cls in (("sd_pv", "route"), ("pv_mz", "route"), ("mz_cb", "route"), ("cb_sd", "route back")):
        pts = " ".join(f"{s[0]},{s[1]}" for s in r["legs"][leg]["samples"])
        out.append(f'<polyline class="{cls}" points="{pts}"/>')
    # region labels
    for k, lab in (("L_son", "SONORA"), ("L_sin", "SINALOA"), ("L_nay", "NAYARIT"), ("L_usa", "UNITED STATES")):
        x, y = p[k]
        anchor = "end" if k in ("L_nay",) else "middle"
        if k == "L_nay":
            x = 398
        if k == "L_usa":
            x, y = 300, 30
        out.append(f'<text class="d" x="{x}" y="{y}" text-anchor="{anchor}" style="fill:var(--ink-3)">{lab}</text>')
    for k, lab, rot in (("W_pac", "Pacific Ocean", 0), ("W_cortez", "Sea of Cortez", 55)):
        x, y = p[k]
        out.append(f'<text class="w" x="{x}" y="{y}" text-anchor="middle" transform="rotate({rot} {x} {y})">{lab}</text>')
    # pois
    poi_lab = {"coronado": ("Islas Coronado", 6, 3, "start"), "ens": ("Ensenada", 6, 3, "start"), "cedros": ("Isla Cedros", -6, 3, "end"),
               "ojo": ("Ojo de Liebre", 8, 3, "start"), "sanig": ("San Ignacio", 8, 4, "start"), "mag": ("Magdalena Bay", -8, 3, "end"),
               "marias": ("Islas Marías", -6, 4, "end"), "lapaz": ("La Paz", 6, 3, "start")}
    for k, (lab, dx, dy, an) in poi_lab.items():
        x, y = p[k]
        out.append(f'<circle class="poi" cx="{x}" cy="{y}" r="1.8"/><text class="s halo" x="{x + dx}" y="{y + dy}" text-anchor="{an}">{lab}</text>')
    ports = {"sd": ("San Diego", 6, -2, "start"), "pv": ("Puerto Vallarta", -8, 14, "end"), "mz": ("Mazatlán", 8, 3, "start"), "cb": ("Cabo San Lucas", -9, 14, "end")}
    for k, (lab, dx, dy, an) in ports.items():
        x, y = p[k]
        out.append(f'<circle class="pmark" cx="{x}" cy="{y}" r="4"/><text class="halo" x="{x + dx}" y="{y + dy}" text-anchor="{an}" font-weight="700">{lab}</text>')
    out.append('<g id="shipMk" transform="translate(-50,-50)"><circle r="9" fill="var(--accent)" opacity=".18"/><path class="ship" d="M7,0 L-5,-4.5 L-3,0 L-5,4.5 Z"/></g>')
    # legend
    out.append(f'<g transform="translate(12,{H - 44})"><rect width="128" height="36" rx="5" fill="var(--card)" opacity=".92"/>'
               f'<line x1="8" y1="11" x2="28" y2="11" class="route"/><text class="s" x="34" y="14">Southbound legs</text>'
               f'<line x1="8" y1="25" x2="28" y2="25" class="route back"/><text class="s" x="34" y="28">Home via Baja</text></g>')
    out.append(f'<g transform="translate(150,{H - 44})"><rect width="104" height="36" rx="5" fill="var(--card)" opacity=".92"/>'
               f'<circle cx="14" cy="18" r="8" class="whale" style="opacity:.35"/><text class="s" x="28" y="15">Whale nurseries</text><text class="s" x="28" y="27">&amp; hot spots</text></g>')
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------------- tectonics
def tect_svg(m):
    r, t = m["route"], m["tect"]
    W, H = r["width"], r["height"]
    p = r["pts"]
    out = [f'<svg class="map" id="tectSvg" viewBox="0 0 {W} {H}" role="img" aria-label="Baja California sliding back southeast against mainland Mexico as you rewind six million years.">']
    out.append(f'<rect class="sea" width="{W}" height="{H}"/>')
    out.append(f'<path class="land" d="{t["base"]}"/>')
    out.append(f'<g id="bajaPlate" data-dx="{t["dx"]}" data-dy="{t["dy"]}"><path class="land" style="fill:color-mix(in srgb, var(--accent) 22%, var(--land));stroke:var(--accent)" d="{t["baja"]}"/></g>')
    x, y = p["L_bcs"]
    out.append(f'<text class="d halo" x="40" y="250" style="fill:var(--accent)">PACIFIC PLATE</text>')
    out.append(f'<text class="d halo" x="394" y="150" text-anchor="end" style="fill:var(--ink-2)">NORTH AMERICAN PLATE</text>')
    out.append(f'<g id="tectArrow"><line x1="150" y1="300" x2="118" y2="258" stroke="var(--accent)" stroke-width="2" marker-end="url(#ah)"/></g>')
    out.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="var(--accent)"/></marker></defs>')
    out.append(f'<text class="halo" id="tectLabel" x="{W - 10}" y="28" text-anchor="end" font-weight="700" style="font-family:var(--f-data);font-size:13px">Today</text>')
    for k in ("pv", "mz"):
        px, py = p[k]
        out.append(f'<circle class="pmark" cx="{px}" cy="{py}" r="3"/>')
    out.append(f'<text class="s halo" x="{p["pv"][0] - 6}" y="{p["pv"][1] + 12}" text-anchor="end">Puerto Vallarta</text>')
    out.append(f'<text class="s halo" x="{p["mz"][0] + 6}" y="{p["mz"][1] + 3}">Mazatlán</text>')
    out.append("</svg>")
    return "".join(out)


# ---------------------------------------------------------------- PV map
def pv_svg(m):
    v = m["pv"]
    W, H = v["width"], v["height"]
    p = v["pts"]
    out = [f'<svg class="map" viewBox="0 0 {W} {H}" role="img" aria-label="Banderas Bay: the terminal at Marina Vallarta, downtown and the Zona Romántica to the south, Los Arcos, Mismaloya and Boca de Tomatlán further south, and the Marietas Islands at the mouth of the bay.">']
    out.append(f'<rect class="sea" width="{W}" height="{H}"/><path class="land" d="{v["land"]}"/>')
    # ship approach
    tx, ty = p["terminal"]
    out.append(f'<path class="route back" d="M0,150 C120,165 250,200 {tx - 4},{ty}"/>')
    # trail Boca -> Colomitos -> Animas
    bx, by = p["boca"]; cx, cy = p["colomitos"]; ax, ay = p["animas"]
    out.append(f'<path class="walk" d="M{bx},{by + 2} Q{(bx + cx) / 2},{by + 6} {cx},{cy + 3} T{ax},{ay + 3}"/>')
    # panga Boca -> Los Arcos
    rx, ry = p["arcos"]
    out.append(f'<path class="blue" d="M{bx - 2},{by - 2} Q{bx - 20},{(by + ry) / 2} {rx - 3},{ry + 2}"/>')
    labels = [
        ("terminal", "Cruise terminal", -8, -4, "end", "mk"), ("malecon", "Malecón · El Centro", -8, 0, "end", "mk2"),
        ("muertos", "Zona Romántica", -8, 12, "end", "mk2"), ("arcos", "Los Arcos", -7, -4, "end", "mk"),
        ("mismaloya", "Mismaloya", 7, 6, "start", "mk2"), ("boca", "Boca de Tomatlán", 7, 10, "start", "mk"),
        ("animas", "Las Ánimas", -4, 13, "middle", "mk2"), ("yelapa", "Yelapa", 0, -8, "middle", "mk2"),
        ("marietas", "Islas Marietas", 0, -9, "middle", "mk"), ("puntamita", "Punta de Mita", 8, 12, "start", "mk2"),
        ("bucerias", "Bucerías", 0, 14, "middle", "mk2"), ("botanical", "Botanical Garden", 0, -8, "middle", "mk2"),
    ]
    for k, lab, dx, dy, an, cls in labels:
        x, y = p[k]
        out.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="3.4"/><text class="halo" x="{x + dx}" y="{y + dy}" text-anchor="{an}">{lab}</text>')
    out.append('<text class="w halo" x="165" y="190" text-anchor="middle" style="font-size:15px">Bahía de Banderas</text>')
    out.append('<text class="s halo" x="300" y="40" text-anchor="middle" style="fill:var(--ink-3)">NAYARIT</text><text class="s halo" x="372" y="290" text-anchor="middle" style="fill:var(--ink-3)">JALISCO</text>')
    out.append(f'<g transform="translate(14,{H - 52})"><rect width="150" height="44" rx="5" fill="var(--card)" opacity=".92"/>'
               '<line x1="8" y1="12" x2="26" y2="12" class="route back"/><text class="s" x="32" y="15">Ship approach</text>'
               '<line x1="8" y1="24" x2="26" y2="24" class="walk"/><text class="s" x="32" y="27">Jungle trail</text>'
               '<line x1="8" y1="36" x2="26" y2="36" class="blue"/><text class="s" x="32" y="39">Panga to Los Arcos</text></g>')
    out.append(f'<text class="d" x="{W - 6}" y="{H - 6}" text-anchor="end">≈ 10 km</text><line x1="{W - 6 - 87}" y1="{H - 16}" x2="{W - 6}" y2="{H - 16}" stroke="var(--ink-2)" stroke-width="1.5"/>')
    out.append("</svg>")
    return "".join(out)


def pv_scale_px(m):
    v = m["pv"]
    lon0, lat0, lon1, lat1 = v["bbox"]
    km_w = (lon1 - lon0) * 111.32 * math.cos(math.radians((lat0 + lat1) / 2))
    return v["width"] / km_w


# ---------------------------------------------------------------- Cabo schematic
def cabo_svg():
    return """<svg class="map" viewBox="0 0 400 270" role="img" aria-label="Cabo San Lucas schematic: tenders land inside the marina; water taxis run past Pelican Rock to Lover's Beach and El Arco at the tip of Land's End. Divorce Beach faces the Pacific surf on the other side of the sand.">
<rect class="sea" width="400" height="270"/>
<path class="land" d="M0,0 H400 V78 C360,84 330,92 300,103 C268,114 238,126 214,136 L205,141 C214,150 226,160 240,172 C256,186 270,198 282,207 C292,215 300,224 306,232 L311,240 C306,243 300,242 293,238 C286,233 279,229 271,229 C262,229 252,224 240,217 C220,205 196,194 170,186 C130,174 80,170 40,170 C25,170 12,172 0,174 Z"/>
<path class="marina" d="M205,141 C199,134 194,126 188,116 C182,106 176,96 168,88 C160,82 150,82 146,90 C144,98 150,108 158,116 C168,126 178,134 188,140 C194,143 200,143 205,141 Z"/>
<path class="rock" d="M311,240 C316,246 320,252 318,258 C316,262 311,262 309,258 L307,250 C306,246 305,243 306,242 Z"/>
<path class="sea" d="M310.5,249 C311.5,251 312.5,254 312,256 C311,257 310,256 309.8,254 Z"/>
<circle class="rock" cx="326" cy="250" r="3.5"/><circle class="rock" cx="321" cy="259" r="2.5"/>
<circle class="rock" cx="232" cy="156" r="3"/>
<path class="walk" d="M176,108 C200,128 224,150 246,170 C258,182 268,196 276,212"/>
<g transform="translate(332 150) rotate(-20)"><path class="ship" d="M20,0 L-16,-5 L-18,0 L-16,5 Z"/></g><path class="sea" style="stroke:none" d="M199,135 L219,132 L222,151 L203,151 Z"/>
<circle class="mk" cx="176" cy="108" r="4"/><text class="halo" x="168" y="104" text-anchor="end" font-weight="700">Tender dock</text>
<text class="s halo" x="150" y="128" text-anchor="end">Marina Cabo San Lucas</text>
<circle class="mk2" cx="232" cy="156" r="3.4"/><text class="halo" x="240" y="152">Pelican Rock</text>
<circle class="mk" cx="278" cy="214" r="4"/><text class="halo" x="270" y="206" text-anchor="end">Lover's Beach</text><text class="s halo" x="270" y="217" text-anchor="end">calm · swim &amp; snorkel</text>
<circle class="bad" cx="268" cy="232" r="4"/><text class="halo" x="262" y="250" text-anchor="end">Divorce Beach</text><text class="s halo" x="262" y="261" text-anchor="end">Pacific surf · no swimming</text>
<text class="halo" x="336" y="236" font-weight="700">El Arco</text><text class="s halo" x="336" y="247">sea lions</text>
<text class="s halo" x="332" y="170" text-anchor="middle">Koningsdam at anchor</text>
<text class="halo" x="268" y="98">Médano Beach</text>
<text class="w halo" x="350" y="198" text-anchor="middle">Bahía de</text><text class="w halo" x="350" y="212" text-anchor="middle">Cabo San Lucas</text>
<text class="w halo" x="80" y="230" text-anchor="middle" style="font-size:14px">Pacific Ocean</text>
<text class="halo" x="100" y="40" font-weight="700" style="font-size:12px">Cabo San Lucas</text><text class="s halo" x="100" y="53">town &amp; marina boardwalk</text>
<text class="s halo" x="396" y="64" text-anchor="end">Santa María &amp; Chileno bays →</text><text class="s halo" x="396" y="74" text-anchor="end">20–25 min by car</text>
<text class="d" x="6" y="264">SCHEMATIC · NOT TO SCALE</text>
<g transform="translate(380,20)"><path d="M0,-12 L5,4 L0,1 L-5,4 Z" fill="var(--ink)"/><text class="d" x="0" y="15" text-anchor="middle">N</text></g>
</svg>"""


# ---------------------------------------------------------------- Mazatlán schematic
def mz_svg():
    return """<svg class="map" viewBox="0 0 400 460" role="img" aria-label="Mazatlán schematic: the cruise terminal on the harbor channel, the blue line walking route about a mile to Plazuela Machado in the historic center, Olas Altas and the cliff divers on the Pacific shore, El Faro on Cerro del Crestón at the southern tip, and the Malecón running north. Deer Island and Stone Island are outside the advisory zone.">
<rect class="sea" width="400" height="460"/>
<path class="land" d="M178,0 H400 V318 C370,322 340,330 318,340 C300,348 284,356 270,368 C258,378 250,388 238,396 C226,402 214,402 204,398 L198,396 C192,388 186,374 176,360 C168,348 160,336 156,322 C152,306 150,292 152,280 C154,262 160,246 164,232 C168,214 170,196 172,176 C174,150 174,110 176,70 C177,40 177,20 178,0 Z"/>
<path class="land" d="M186,404 C182,410 180,420 184,430 C188,438 198,442 206,438 C214,432 214,420 208,410 C202,404 194,402 186,404 Z"/>
<path class="land" d="M400,350 V460 H250 C258,446 270,432 286,418 C304,402 330,386 356,370 C372,360 386,352 400,350 Z"/>
<path class="land" d="M96,70 C88,72 84,80 88,86 C94,92 104,90 108,84 C110,76 104,68 96,70 Z"/>
<path class="land" d="M58,122 C54,124 54,130 58,132 C62,133 66,130 65,126 C64,122 61,121 58,122 Z"/>
<path class="zone" d="M152,282 C156,262 162,246 166,232 L258,236 C262,262 262,290 258,318 C252,340 246,362 238,382 C226,392 214,394 204,390 C194,380 186,368 178,356 C168,342 158,328 156,316 C152,304 151,292 152,282 Z"/>
<path class="zone-edge" d="M166,232 L258,236 C262,262 262,290 258,318 C252,340 246,362 238,382"/>
<path d="M172,176 C174,150 174,110 176,70 C177,40 177,20 178,0" fill="none" stroke="var(--accent)" stroke-width="9" stroke-opacity=".16"/>
<path d="M164,232 C168,214 170,196 172,176" fill="none" stroke="var(--accent)" stroke-width="9" stroke-opacity=".16"/>
<path class="blue" d="M248,368 C240,350 232,336 224,322 C218,312 212,304 204,298"/>
<line x1="206" y1="402" x2="194" y2="406" stroke="var(--land-edge)" stroke-width="3"/>
<circle class="mk" cx="248" cy="370" r="4.5"/><text class="halo" x="256" y="374" font-weight="700">Cruise terminal</text><text class="s halo" x="256" y="386">free tram to the gate</text>
<circle class="mk" cx="202" cy="298" r="4"/><text class="halo" x="210" y="296">Plazuela Machado</text><text class="s halo" x="210" y="307">Teatro Ángela Peralta</text>
<text class="s halo" x="222" y="342" text-anchor="end" style="fill:var(--sea)">blue line · ~1 mi</text>
<circle class="mk2" cx="214" cy="270" r="3.4"/><text class="halo" x="222" y="273">Cathedral</text>
<circle class="mk2" cx="222" cy="250" r="3.4"/><text class="halo" x="230" y="253">Mercado Pino Suárez</text>
<circle class="mk2" cx="156" cy="300" r="3.4"/><text class="halo" x="148" y="296" text-anchor="end">Olas Altas</text>
<circle class="mk2" cx="163" cy="246" r="3.4"/><text class="halo" x="155" y="243" text-anchor="end">Cliff divers</text>
<circle class="mk" cx="196" cy="422" r="4"/><text class="halo" x="182" y="426" text-anchor="end" font-weight="700">El Faro</text><text class="s halo" x="182" y="437" text-anchor="end">Cerro del Crestón · 157 m</text>
<circle class="mk2" cx="172" cy="182" r="3.4"/><text class="halo" x="164" y="180" text-anchor="end">Monumento al</text><text class="halo" x="164" y="192" text-anchor="end">Pescador</text>
<text class="halo" x="210" y="80" font-weight="700" style="font-size:11px">Malecón ↑</text><text class="s halo" x="210" y="92">continues north to Route 503</text>
<text class="s halo" x="210" y="16">Zona Dorada (Golden Zone) ↑</text>
<circle class="bad" cx="98" cy="80" r="3.4"/><text class="halo" x="98" y="104" text-anchor="middle">Deer Island</text><text class="s halo" x="98" y="115" text-anchor="middle">outside the zone</text>
<circle class="bad" cx="330" cy="420" r="3.4"/><text class="halo" x="330" y="440" text-anchor="middle">Stone Island</text><text class="s halo" x="330" y="451" text-anchor="middle">outside the zone</text>
<text class="halo" x="210" y="226" style="fill:var(--accent);font-weight:700;font-size:10px">Centro Histórico</text>
<text class="w halo" x="56" y="272" text-anchor="middle" style="font-size:14px">Pacific Ocean</text>
<g transform="translate(14,356)"><rect width="122" height="46" rx="5" fill="var(--card)" opacity=".92"/><rect x="8" y="9" width="14" height="10" class="zone" style="opacity:.35"/><text class="s" x="28" y="17">U.S. advisory zone</text><text class="s" x="28" y="27">(approximate)</text><circle class="bad" cx="15" cy="37" r="3.4"/><text class="s" x="28" y="40">Outside the zone</text></g>
<text class="d" x="6" y="454">SCHEMATIC · NOT TO SCALE</text>
<g transform="translate(380,30)"><path d="M0,-12 L5,4 L0,1 L-5,4 Z" fill="var(--ink)"/><text class="d" x="0" y="15" text-anchor="middle">N</text></g>
</svg>"""


# ---------------------------------------------------------------- deck profile
DECK_H = 15
BASE = 214


def deck_y(n):
    return BASE - DECK_H * n


def deck_svg(decks):
    W, H = 400, 262
    o = [f'<svg class="deck-svg" id="deckSvg" viewBox="0 0 {W} {H}" role="img" aria-label="Side profile of Koningsdam, bow to the right, with decks 1 to 12 stacked. Tap a deck to see what is on it.">']
    # water
    o.append(f'<rect class="waterline" x="0" y="{BASE + 8}" width="{W}" height="{H - BASE - 8}"/>')
    # superstructure decks 4-10 (white), front steps back as it rises
    def sx(n):  # forward x of deck n superstructure
        return {4: 352, 5: 350, 6: 348, 7: 346, 8: 344, 9: 338, 10: 330, 11: 322, 12: 318}[n]
    def ax(n):  # aft x
        return {4: 30, 5: 30, 6: 31, 7: 32, 8: 34, 9: 40, 10: 48, 11: 62, 12: 150}[n]
    pts = []
    for n in range(4, 13):
        pts.append((ax(n), deck_y(n)))
    pts_aft = [(ax(n), deck_y(n - 1) if n > 4 else deck_y(3)) for n in range(4, 13)]
    poly = [(ax(4), deck_y(3))]
    for n in range(4, 13):
        poly += [(ax(n), deck_y(n - 1)), (ax(n), deck_y(n))]
    for n in range(12, 3, -1):
        poly += [(sx(n), deck_y(n)), (sx(n), deck_y(n - 1))]
    o.append('<path class="super" d="M' + " L".join(f"{x},{y}" for x, y in poly) + ' Z"/>')
    # windows rows
    for n in range(4, 11):
        y = deck_y(n) + 5
        o.append(f'<rect class="win" x="{ax(n) + 6}" y="{y}" width="{sx(n) - ax(n) - 14}" height="5" rx="1.5"/>')
    # glass: magrodome over Lido pool (deck 9-10 mid), Crow's Nest windows deck 12 fwd
    o.append(f'<path class="glass" d="M170,{deck_y(10)} Q200,{deck_y(10) - 16} 236,{deck_y(10)} Z"/>')
    o.append(f'<rect class="glass" x="256" y="{deck_y(12) + 4}" width="58" height="7" rx="2"/>')
    # funnel aft
    o.append(f'<path class="funnel" d="M92,{deck_y(11)} L100,{deck_y(12) - 14} L128,{deck_y(12) - 14} L132,{deck_y(11)} Z"/>')
    # hull decks 1-3 and below the water
    hull = f"M22,{deck_y(3)} L384,{deck_y(3)} L378,{BASE - 6} L362,{BASE + 20} L60,{BASE + 20} L34,{BASE + 8} L22,{BASE - 12} Z"
    o.append(f'<path class="hull" d="{hull}"/>')
    o.append(f'<line class="wl" x1="0" y1="{BASE + 8}" x2="{W}" y2="{BASE + 8}"/>')
    # lifeboats along deck 3/4 sides
    for x in range(118, 300, 26):
        o.append(f'<rect x="{x}" y="{deck_y(4) + 3}" width="20" height="9" rx="4" fill="var(--warn)"/>')
    # portholes on hull
    for n in (1, 2, 3):
        y = deck_y(n) + 7
        o.append(f'<line x1="44" y1="{y}" x2="364" y2="{y}" stroke="var(--paper)" stroke-opacity=".25" stroke-width="1.6" stroke-dasharray="1.5 3.5"/>')
    # deck bands & labels
    for d in decks:
        n = d["n"]
        y = deck_y(n)
        o.append(f'<rect class="band" data-deck="{n}" x="18" y="{y}" width="370" height="{DECK_H}"><title>Deck {n}</title></rect>')
        o.append(f'<text class="dl" x="14" y="{y + 11}" text-anchor="end">{n}</text>')
    # section axis
    for x, lab in ((70, "AFT"), (205, "MID"), (330, "FWD")):
        o.append(f'<text class="ax" x="{x}" y="{H - 4}" text-anchor="middle">{lab}</text>')
    o.append(f'<text class="ax" x="392" y="{H - 4}" text-anchor="end">BOW →</text>')
    o.append(f'<g id="cabDots" data-base="{BASE}" data-h="{DECK_H}"></g>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- power plant
def power_svg():
    o = ['<svg class="power" id="powerSvg" viewBox="0 0 400 314" role="img" aria-label="Diesel-electric power flow: four generators feed one switchboard, which feeds two Azipod propulsion motors, the bow thrusters and the hotel load. Exhaust goes through scrubbers to the funnel.">']
    o.append('<text class="k" x="10" y="12">GENERATE</text><text class="k" x="390" y="12" text-anchor="end">USE</text>')
    gy = [44, 96, 148, 200]
    for i, y in enumerate(gy):
        o.append(f'<rect class="gen" id="gen{i}" x="8" y="{y}" width="96" height="42" rx="6"/>')
        o.append(f'<text id="genT{i}" x="16" y="{y + 16}" font-weight="700">G{i + 1}</text><text class="k" x="38" y="{y + 16}">MaK 12V43C</text>')
        o.append(f'<text class="v" id="genV{i}" x="16" y="{y + 32}">0 MW</text>')
        o.append(f'<path class="flow" id="genF{i}" d="M104,{y + 21} H146" stroke-width="3"/>')
    o.append('<rect class="bus" x="146" y="44" width="9" height="198" rx="2"/>')
    o.append('<text class="k" x="150" y="258" text-anchor="middle">MAIN</text><text class="k" x="150" y="268" text-anchor="middle">SWITCHBOARD</text>')
    loads = [("pod0", 44, "Azipod · port", "14 MW max"), ("pod1", 96, "Azipod · starboard", "14 MW max"),
             ("thr", 148, "Bow thrusters", "docking only"), ("hotel", 200, "Hotel load", "HVAC · galleys · lights")]
    for lid, y, name, sub in loads:
        o.append(f'<path class="flow" id="{lid}F" d="M155,{y + 21} H226" stroke-width="3"/>')
        o.append(f'<rect class="load" x="226" y="{y}" width="166" height="42" rx="6"/>')
        o.append(f'<text x="234" y="{y + 16}" font-weight="700">{name}</text><text class="k" x="234" y="{y + 30}">{sub.upper()}</text>')
        o.append(f'<text class="v" id="{lid}V" x="384" y="{y + 16}" text-anchor="end">0 MW</text>')
        if lid.startswith("pod"):
            o.append(f'<text class="k" x="190" y="{y + 16}" text-anchor="middle">DRIVE</text>')
            o.append(f'<g transform="translate(360,{y + 30})"><ellipse class="pod" rx="10" ry="4"/><g class="spin" id="{lid}P"><line class="prop" x1="12" y1="-6" x2="12" y2="6"/></g></g>')
    # exhaust & fuel
    o.append('<path class="exh" d="M56,44 V30 H104"/><text class="k" x="108" y="33">EXHAUST → SCRUBBERS → FUNNEL</text>')
    o.append('<rect x="8" y="268" width="96" height="40" rx="6" fill="none" stroke="var(--warn)" stroke-width="1.2"/><text x="16" y="284" font-weight="700">Fuel tanks</text><text class="k" x="16" y="298">HFO · MGO</text>')
    o.append('<path class="fuel" d="M56,268 V242"/><text class="v" id="fuelV" x="62" y="258">0 t/day</text>')
    o.append('<text class="v" id="totV" x="309" y="268" text-anchor="middle" style="font-size:11px">0 MW total</text>')
    o.append('<text class="k" x="309" y="282" text-anchor="middle" id="engV">ENGINES ONLINE: 0 OF 4</text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- size comparison
def size_svg():
    rows = [("Icon of the Seas", 365, "largest cruise ship class"), ("Eiffel Tower", 330, "if laid down"), ("Koningsdam", 299.65, "your ship"),
            ("Titanic", 269, "1912"), ("Space Needle", 184, "if laid down"), ("Football field", 109.7, "incl. end zones")]
    x0, scale = 112, 252 / 365
    rh = 30
    H = 22 + rh * len(rows) + 24
    o = [f'<svg class="size" viewBox="0 0 400 {H}" role="img" aria-label="Lengths compared: Icon of the Seas 365 m, Eiffel Tower 330 m, Koningsdam 300 m, Titanic 269 m, Space Needle 184 m, a football field 110 m.">']
    for m in (0, 100, 200, 300):
        x = x0 + m * scale
        o.append(f'<line class="axis" x1="{fmt(x)}" y1="14" x2="{fmt(x)}" y2="{H - 20}"/><text class="a" x="{fmt(x)}" y="{H - 8}" text-anchor="middle">{m} m</text>')
    for i, (name, L, sub) in enumerate(rows):
        y = 20 + i * rh
        me = " me" if name == "Koningsdam" else ""
        o.append(f'<text x="{x0 - 8}" y="{y + 11}" text-anchor="end" font-weight="{700 if me else 500}">{name}</text>')
        o.append(f'<text class="a" x="{x0 - 8}" y="{y + 21}" text-anchor="end">{sub}</text>')
        o.append(f'<rect class="bar{me}" x="{x0}" y="{y + 3}" width="{fmt(L * scale)}" height="16" rx="3"/>')
        o.append(f'<text class="v" x="{fmt(x0 + L * scale + 5)}" y="{y + 15}">{fmt(L)} m</text>')
    o.append("</svg>")
    return "".join(o)


def tonnage_svg():
    rows = [("Titanic (1912)", 46328, "GRT"), ("Koningsdam", 99863, "GT"), ("Icon class", 248663, "GT")]
    x0, scale = 112, 205 / 248663
    H = 22 + 28 * 3 + 4
    o = [f'<svg class="size" viewBox="0 0 400 {H}" role="img" aria-label="Enclosed volume: Titanic 46,328 gross register tons, Koningsdam 99,863 gross tons, Icon class 248,663 gross tons.">']
    for i, (name, v, unit) in enumerate(rows):
        y = 8 + i * 28
        me = " me" if name == "Koningsdam" else ""
        o.append(f'<text x="{x0 - 8}" y="{y + 14}" text-anchor="end" font-weight="{700 if me else 500}">{name}</text>')
        o.append(f'<rect class="bar{me}" x="{x0}" y="{y + 3}" width="{fmt(v * scale)}" height="16" rx="3"/>')
        o.append(f'<text class="v" x="{fmt(x0 + v * scale + 5)}" y="{y + 15}">{v:,} {unit}</text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- weather chart
def weather_svg(weather):
    W, H = 400, 230
    L, R, T, B = 50, 40, 24, 52
    xs = [L + i * (W - L - R) / (len(weather) - 1) for i in range(len(weather))]
    lo_v, hi_v = 45, 90
    def y(v):
        return T + (hi_v - v) * (H - T - B) / (hi_v - lo_v)
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Late-December temperatures: San Diego 65/49°F, Puerto Vallarta 84/63°F, Mazatlán 78/60°F, Cabo 79/60°F. Sea temperature climbs from 59°F at San Diego to 78°F at Puerto Vallarta.">']
    for v in (50, 60, 70, 80, 90):
        o.append(f'<line class="gridl" x1="{L}" y1="{fmt(y(v))}" x2="{W - R}" y2="{fmt(y(v))}"/><text class="a" x="{L - 6}" y="{fmt(y(v) + 3)}" text-anchor="end">{v}°</text>')
    band = " ".join(f"{fmt(x)},{fmt(y(w['hi']))}" for x, w in zip(xs, weather)) + " " + " ".join(f"{fmt(x)},{fmt(y(w['lo']))}" for x, w in reversed(list(zip(xs, weather))))
    o.append(f'<polygon class="band" points="{band}"/>')
    o.append('<polyline class="hi-line" points="' + " ".join(f"{fmt(x)},{fmt(y(w['hi']))}" for x, w in zip(xs, weather)) + '"/>')
    o.append('<polyline class="lo-line" points="' + " ".join(f"{fmt(x)},{fmt(y(w['lo']))}" for x, w in zip(xs, weather)) + '"/>')
    o.append('<polyline class="w-line" points="' + " ".join(f"{fmt(x)},{fmt(y(w['water']))}" for x, w in zip(xs, weather)) + '"/>')
    short = {"San Diego": "San Diego", "Puerto Vallarta": "P. Vallarta", "Mazatlán": "Mazatlán", "Cabo San Lucas": "Cabo"}
    for x, w in zip(xs, weather):
        o.append(f'<circle class="pt" cx="{fmt(x)}" cy="{fmt(y(w["hi"]))}" r="3.5" style="stroke:var(--accent)"/>')
        o.append(f'<text class="v" x="{fmt(x)}" y="{fmt(y(w["hi"]) - 8)}" text-anchor="middle">{w["hi"]}°</text>')
        o.append(f'<circle class="pt" cx="{fmt(x)}" cy="{fmt(y(w["water"]))}" r="3" style="stroke:var(--sea)"/>')
        wy = y(w["water"]) + 15
        o.append(f'<text class="v" x="{fmt(x)}" y="{fmt(wy)}" text-anchor="middle" style="fill:var(--sea)">{w["water"]}°</text>')
        o.append(f'<text x="{fmt(x)}" y="{H - B + 18}" text-anchor="middle" font-weight="600">{short[w["place"]]}</text>')
        o.append(f'<text class="a" x="{fmt(x)}" y="{H - B + 30}" text-anchor="middle">{w["date"].upper()}</text>')
        o.append(f'<text class="a" x="{fmt(x)}" y="{H - B + 41}" text-anchor="middle">LOW {w["lo"]}°</text>')
    o.append(f'<g class="legend" transform="translate(14,10)"><line x1="0" y1="0" x2="16" y2="0" class="hi-line"/><text x="20" y="3">Air high</text>'
             f'<line x1="78" y1="0" x2="94" y2="0" class="lo-line"/><text x="98" y="3">Air low</text>'
             f'<line x1="150" y1="0" x2="166" y2="0" class="w-line"/><text x="170" y="3">Sea surface</text><text class="a" x="{W - 28}" y="3" text-anchor="end">°F</text></g>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- bar charts
def hbar_svg(rows, highlight, label, unit_fmt, max_v=None, note=None, labw=130):
    W = 400
    x0 = labw
    rh = 24
    H = 10 + rh * len(rows) + 4
    mx = max_v or max(r[1] for r in rows)
    vlen = max(len(unit_fmt(r[1]) + (f"  ·  {r[2]}" if len(r) > 2 else "")) for r in rows)
    scale = (W - x0 - 10 - 6.4 * vlen) / mx
    o = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}">']
    for i, r in enumerate(rows):
        name, v = r[0], r[1]
        sub = r[2] if len(r) > 2 else None
        yy = 6 + i * rh
        hi = " hi" if name in highlight else ""
        o.append(f'<text x="{x0 - 8}" y="{yy + 13}" text-anchor="end" font-weight="{700 if hi else 500}">{esc(name)}</text>')
        o.append(f'<rect class="b{hi}" x="{x0}" y="{yy + 2}" width="{fmt(max(1.5, v * scale))}" height="15" rx="3"/>')
        txt = unit_fmt(v) + (f"  ·  {sub}" if sub else "")
        o.append(f'<text class="v" x="{fmt(x0 + v * scale + 5)}" y="{yy + 13}">{esc(txt)}</text>')
    o.append("</svg>")
    if note:
        o.append(f'<p class="chartnote">{esc(note)}</p>')
    return "".join(o)


# ---------------------------------------------------------------- whale ID
def whale_id_svg():
    o = ['<svg class="whale-id" viewBox="0 0 400 268" role="img" aria-label="Whale identification by blow and back: gray whale has a short heart-shaped blow and no dorsal fin; humpback a bushy blow and a small fin on a hump; blue whale a very tall column and a tiny fin far back; fin whale a tall column and a curved fin seen soon after the blow.">']
    o.append('<text class="h" x="0" y="12">WHALE</text><text class="h" x="128" y="12" text-anchor="middle">BLOW</text><text class="h" x="290" y="12" text-anchor="middle">BACK AS IT SURFACES</text>')
    rows = [
        ("Gray", "heart-shaped, 3–4 m", "no fin, 'knuckles'",
         '<path class="blow" d="M128,58 C122,46 116,38 114,28 M128,58 C134,46 140,38 142,28"/>',
         '<path class="body" d="M190,62 C220,46 290,42 350,56 L350,62 Z"/><circle class="body" cx="300" cy="47" r="2.6"/><circle class="body" cx="312" cy="48" r="2.4"/><circle class="body" cx="323" cy="50" r="2.2"/><circle class="body" cx="333" cy="52" r="2"/>'),
        ("Humpback", "bushy, about 3 m", "small fin on a hump",
         '<path class="blow" d="M128,122 V104"/><ellipse cx="128" cy="96" rx="15" ry="10" fill="none" stroke="var(--sea)" stroke-width="1.6"/>',
         '<path class="body" d="M190,126 C230,108 270,100 300,104 C318,106 336,114 350,120 L350,126 Z"/><path class="body" d="M296,104 L304,94 L312,106 Z"/>'),
        ("Blue", "tall column, 9 m", "tiny fin far back",
         '<path class="blow" d="M128,190 V132"/><path class="blow" d="M124,138 C126,132 130,132 132,138"/>',
         '<path class="body" d="M184,190 C230,180 300,178 360,184 L360,190 Z"/><path class="body" d="M336,181 L340,176 L344,182 Z"/>'),
        ("Fin", "tall column, 4–6 m", "curved fin, seen early",
         '<path class="blow" d="M128,254 V214"/><path class="blow" d="M124,220 C126,214 130,214 132,220"/>',
         '<path class="body" d="M190,254 C236,242 296,238 350,246 L350,254 Z"/><path class="body" d="M292,241 C296,232 302,228 308,227 C304,232 304,238 308,242 Z"/>'),
    ]
    for i, (name, blow, back, bsvg, ksvg) in enumerate(rows):
        base = [62, 126, 190, 254][i]
        o.append(f'<line class="wl" x1="96" y1="{base + 2}" x2="400" y2="{base + 2}"/>')
        o.append(bsvg + ksvg)
        o.append(f'<text x="0" y="{base - 22}" font-weight="700">{name}</text><text class="s" x="0" y="{base - 9}">{blow}</text><text class="s" x="0" y="{base + 3}">{back}</text>')
        if i < 3:
            o.append(f'<line class="rule" x1="0" y1="{base + 12}" x2="400" y2="{base + 12}"/>')
    o.append("</svg>")
    return "".join(o)
