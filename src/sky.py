# Night-by-night sky data for the voyage (approximate ship positions, ship time).
import ephem
from datetime import datetime, timedelta

NIGHTS = [
    ("Sat", "Dec 26", "2026-12-26", 31.3, -116.9, -8, "Off northern Baja"),
    ("Sun", "Dec 27", "2026-12-27", 27.0, -114.8, -7, "Off central Baja"),
    ("Mon", "Dec 28", "2026-12-28", 22.2, -108.0, -7, "Mouth of the Sea of Cortez"),
    ("Tue", "Dec 29", "2026-12-29", 21.7, -106.3, -6, "Leaving Puerto Vallarta"),
    ("Wed", "Dec 30", "2026-12-30", 23.0, -108.0, -7, "Mazatlán to Cabo"),
    ("Thu", "Dec 31", "2026-12-31", 24.3, -112.3, -7, "New Year's Eve off Baja"),
    ("Fri", "Jan 1", "2027-01-01", 29.5, -116.0, -8, "Heading home"),
]

START_H = 16.0  # chart runs 4 pm to 8 am


def _h(e, off, day0):
    dt = ephem.Date(e).datetime() + timedelta(hours=off)
    return (dt - day0).total_seconds() / 3600


def compute():
    rows = []
    for dow, md, iso, lat, lon, off, where in NIGHTS:
        o = ephem.Observer(); o.lat = str(lat); o.lon = str(lon); o.pressure = 0
        d = datetime.fromisoformat(iso)
        day0 = d  # local midnight at start of the evening's date
        o.date = ephem.Date(d + timedelta(hours=12 - off))
        sun, moon = ephem.Sun(), ephem.Moon()
        o.horizon = "-0:34"
        sset, srise = o.next_setting(sun), o.next_rising(sun)
        o.horizon = "-18"
        dusk, dawn = o.next_setting(sun, use_center=True), o.next_rising(sun, use_center=True)
        o.horizon = "-0:34"
        o.date = ephem.Date(d + timedelta(hours=12 - off))
        mrise = o.next_rising(moon)
        o.date = mrise
        mset = o.next_setting(moon)
        moon.compute(ephem.Date(mrise))
        r = dict(dow=dow, md=md, where=where, off=off,
                 sunset=_h(sset, off, day0), dusk=_h(dusk, off, day0), dawn=_h(dawn, off, day0), sunrise=_h(srise, off, day0),
                 moonrise=_h(mrise, off, day0), moonset=_h(mset, off, day0), illum=round(moon.phase))
        r["dark"] = max(0.0, min(r["moonrise"], r["dawn"]) - r["dusk"])
        rows.append(r)
    return rows


def clock(hours):
    hh = int(hours) % 24
    mm = int(round((hours - int(hours)) * 60))
    if mm == 60:
        hh, mm = (hh + 1) % 24, 0
    return f"{hh % 12 or 12}:{mm:02d} {'am' if hh < 12 else 'pm'}"
