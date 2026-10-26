# Koningsdam cruise guide: instructions for agents

An offline, phone-first guide for the Holland America **ms Koningsdam** "7-Day Mexican Riviera
Holiday", **Dec 26, 2026 – Jan 2, 2027**, San Diego round trip (Puerto Vallarta Dec 29, Mazatlán
Dec 30, Cabo San Lucas Dec 31). It's for a group of six: Daniel & Taylor, Taylor's parents, and
Tyson & Malea.

Live (unlisted) at **https://daniel-beachy.github.io/cruise-guide-v1/** via GitHub Pages from
`main` / `docs/`. It is deliberately **not** linked from the portfolio and has **no "More projects"
link**. The repo is private; the Pages site is still reachable by anyone with the link, and the
group is fine with cabin numbers being in it.

## How it's built

`src/build.py` generates everything from the content files. No framework.

| What | Where |
| --- | --- |
| Trip days, weather, ship specs and facts, deck plan, Holland America facts, **cabins**, site URL | `src/content_trip.py` |
| Ports (overview, stats, facts, history, getting around, snorkeling, food, phrases, safety), Zoo, Mexico briefing incl. advisory | `src/content_ports.py` |
| Port-day "vibes" (loose plans), San Diego embark/disembark, night-sky targets and tips | `src/content_vibes.py` |
| Wildlife, base trivia, packing list, downloads, small games | `src/content_play.py` |
| Extra trivia (no scoring, options shuffle in the app) | `src/content_trivia.py` |
| Card-game rules | `src/content_cards.py` |
| Night-sky computation (needs `ephem`) | `src/sky.py` |
| SVG charts, maps and diagrams | `src/build_svg.py` |
| Page script / styles | `src/app.js`, `src/styles.css` |
| Projected coastline + route data (generated once by `scripts/maps.mjs`) | `data/build-maps.json` |
| Wildlife photos (Wikimedia Commons; credits in `PHOTO_CREDITS` in `build.py`) | `photos/` |
| Embedded fonts (OFL) | `fonts/` |

```bash
pip install ephem pillow            # once
python3 src/build.py                # writes docs/ (the Pages site) and dist/ (single-file copies)
```

`docs/sw.js` gets a cache name derived from the page's hash, so phones pick up a new version the
next time they open the guide online.

## Checks before pushing

```bash
pip install playwright              # if not present; uses an installed Chromium
CHROME_PATH=/path/to/chrome python3 scripts/functest.py        # slider, power lab, ticks, trivia, offline reload
CHROME_PATH=/path/to/chrome python3 scripts/shoot.py "trip" "ports-mz" "play@#quiz"  # phone-width screenshots, light + dark
```

Look at the screenshots. The page must not scroll sideways at 390 px, and `errors: []` must be clean.

## Deploy

```bash
git add -A && git commit -m "<what changed>"
git push origin main                # Pages rebuilds from docs/ in a minute or two
```

Then open https://daniel-beachy.github.io/cruise-guide-v1/ and confirm the change is live.

## Content rules (from Daniel)

- Write for anyone in the group. No "your family"/"the adventurous four" splits; port days use 2–3
  **vibes** (Easy, Active, Chill, etc.) with loose ideas, nothing presented as booked.
- No animal-welfare editorializing; captive encounters and horseback rides are fine to list.
- Trivia has **no scoring, scoreboard or answer key**. Heading is just "Trivia".
- Keep the "One fact at a time" shuffle.
- Mazatlán ideas stay inside the U.S. advisory's cruise-visitor zone (historic center + Malecón to
  Route 503), and the guide explains why Sinaloa is Level 4.
- Facts must be checked. Mark estimates as estimates.

## Pre-cruise fact check (Dec 23, 2026 scheduled run)

Re-verify and update, then rebuild, test and push:
- U.S. travel advisory for Mexico, Sinaloa, Jalisco, Baja California Sur; recent incidents in
  Mazatlán and Puerto Vallarta (`content_ports.py` safety lists and `MEXICO["advisory"]`).
- Port changes, closures or restrictions (e.g. Marietas Hidden Beach days, El Faro, tenders).
- Holland America notices for the Dec 26 sailing; Wi-Fi isn't used by the group, so skip it.
- San Diego Zoo hours, prices, parking and panda status (`ZOO` in `content_ports.py`).
- Weather: replace climate averages in `WEATHER` with the forecast where useful, and note it.
- Cabin numbers in `CABINS` if Daniel has sent them.
- Football: an Activities section is planned once Daniel sends Navigator app screenshots
  (art/origami classes, sports viewing, CFP games, Seahawks or Broncos games in ship time).
