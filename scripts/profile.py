"""Extract Koningsdam's side profile from Holland America's accessible-routes deck plan PDF.

Run once (needs pymupdf); writes data/ship-profile.json, which build_svg.deck_svg draws.
The PDF itself stays out of the repo.

    python3 scripts/profile.py path/to/hal-ko-deckplan-accessibility-routes.pdf
"""
import json, os, sys
import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIP = pymupdf.Rect(440, 530, 740, 600)   # profile drawing, bottom right of the page
GRAY, NAVY = (0.67, 0.69, 0.75), (0.12, 0.16, 0.36)


def close(a, b):
    return all(abs(x - y) < 0.02 for x, y in zip(a, b))


def to_d(items, ox, oy):
    f = lambda p: f"{p.x - ox:.2f},{p.y - oy:.2f}"
    d, end = [], None
    for it in items:
        start = it[1]
        if end is None or abs(start.x - end.x) > 0.01 or abs(start.y - end.y) > 0.01:
            d.append("M" + f(start))
        if it[0] == "l":
            d.append("L" + f(it[2])); end = it[2]
        elif it[0] == "c":
            d.append("C" + " ".join(f(p) for p in it[2:5])); end = it[4]
        else:
            raise ValueError(f"unexpected path item {it[0]}")
    return "".join(d) + "Z"


def main(pdf):
    page = pymupdf.open(pdf)[0]
    paths = [p for p in page.get_drawings() if p.get("fill") and CLIP.contains(p["rect"])]
    sil = [p for p in paths if close(p["fill"], GRAY)]
    bands = [p for p in paths if close(p["fill"], NAVY)]
    box = pymupdf.Rect(sil[0]["rect"])
    for p in sil[1:]:
        box |= p["rect"]
    ox, oy = box.x0, box.y0
    # Bands stack from Main Deck (1) up to Observation (12); a deck can be drawn in pieces.
    levels = sorted({round(p["rect"].y1, 1) for p in bands}, reverse=True)
    assert len(levels) == 12, levels
    decks = {}
    for p in bands:
        n = levels.index(round(p["rect"].y1, 1)) + 1
        decks.setdefault(n, {"d": "", "y0": 99, "y1": 0})
        decks[n]["d"] += to_d(p["items"], ox, oy)
        decks[n]["y0"] = round(min(decks[n]["y0"], p["rect"].y0 - oy), 2)
        decks[n]["y1"] = round(max(decks[n]["y1"], p["rect"].y1 - oy), 2)
    out = {"source": "Holland America Koningsdam accessible-routes deck plan (1/20/26), traced",
           "w": round(box.width, 2), "h": round(box.height, 2),
           "outline": "".join(to_d(p["items"], ox, oy) for p in sil),
           "decks": {str(n): decks[n] for n in sorted(decks)}}
    with open(os.path.join(ROOT, "data", "ship-profile.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("outline", out["w"], "x", out["h"], "pt;", len(decks), "decks")


if __name__ == "__main__":
    main(sys.argv[1])
