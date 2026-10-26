// Build SVG path data for the guide's maps from OSM-derived land polygons.
// usage: node maps.mjs <lands-1km.geojson> <lands-100m.geojson> <out.json>
import fs from 'node:fs';
import { geoMercator, geoPath, geoContains, geoDistance, geoInterpolate, geoGraticule } from 'd3-geo';

const [, , f1km, f100m, outFile] = process.argv;

function loadGeoms(file) {
  const j = JSON.parse(fs.readFileSync(file, 'utf8'));
  const geoms = j.type === 'GeometryCollection' ? j.geometries
    : j.type === 'FeatureCollection' ? j.features.map(f => f.geometry) : [j];
  const polys = [];
  for (const g of geoms) {
    if (!g) continue;
    if (g.type === 'Polygon') polys.push(g.coordinates);
    else if (g.type === 'MultiPolygon') polys.push(...g.coordinates);
  }
  return polys;
}

function ringArea(r) { let a = 0; for (let i = 0, n = r.length; i < n; i++) { const [x1, y1] = r[i], [x2, y2] = r[(i + 1) % n]; a += x1 * y2 - x2 * y1; } return a / 2; }
// d3-geo wants exterior rings clockwise (negative planar area with y=lat up), holes counter-clockwise
function rewind(poly) {
  return poly.map((ring, i) => {
    const a = ringArea(ring);
    const wantNeg = i === 0;
    return (wantNeg ? a > 0 : a < 0) ? ring.slice().reverse() : ring;
  });
}
function bboxOf(poly) { let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9; for (const [x, y] of poly[0]) { if (x < x0) x0 = x; if (x > x1) x1 = x; if (y < y0) y0 = y; if (y > y1) y1 = y; } return [x0, y0, x1, y1]; }

function selectPolys(polys, [lon0, lat0, lon1, lat1]) {
  const out = [];
  for (const p of polys) {
    const [x0, y0, x1, y1] = bboxOf(p);
    if (x1 < lon0 || x0 > lon1 || y1 < lat0 || y0 > lat1) continue;
    out.push(rewind(p));
  }
  return out;
}

function chaikin(ring, it) { let r = ring; for (let k = 0; k < it; k++) { const o = []; for (let i = 0; i < r.length - 1; i++) { const [x0, y0] = r[i], [x1, y1] = r[i + 1]; o.push([0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1], [0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1]); } o.push(o[0]); r = o; } return r; }
function makeMap(polys, bbox, width, points = {}, smooth = 0) {
  const [lon0, lat0, lon1, lat1] = bbox;
  let sel = selectPolys(polys, bbox);
  if (smooth) sel = sel.map(p => p.map(r => r.length > 4 ? chaikin(r, smooth) : r));
  const frame = { type: 'Polygon', coordinates: [[[lon0, lat0], [lon0, lat1], [lon1, lat1], [lon1, lat0], [lon0, lat0]]] };
  const proj = geoMercator().fitWidth(width, frame);
  const [[, ty], [, by]] = [proj([lon0, lat1]), proj([lon0, lat0])];
  const height = Math.round(by - ty);
  proj.translate([proj.translate()[0], proj.translate()[1] - ty]);
  proj.clipExtent([[-2, -2], [width + 2, height + 2]]);
  const path = geoPath(proj).digits(1);
  const land = path({ type: 'MultiPolygon', coordinates: sel }) || '';
  const pts = {};
  for (const [k, ll] of Object.entries(points)) { const [x, y] = proj(ll); pts[k] = [+x.toFixed(1), +y.toFixed(1)]; }
  const graticule = [];
  return { width, height, bbox, land, pts, sel, proj, graticule };
}

console.error('loading 1km…');
const p1 = loadGeoms(f1km);
console.error('loading 100m…');
const p100 = loadGeoms(f100m);

// ---------- Route map ----------
const ports = {
  sd: [-117.1735, 32.7130], pv: [-105.2520, 20.6550], mz: [-106.4180, 23.1930], cb: [-109.9000, 22.8760],
};
// Offshore waypoints (lon, lat)
const legsWP = {
  sd_pv: [ports.sd, [-117.24, 32.66], [-117.33, 32.55], [-117.32, 32.25], [-117.05, 31.6], [-116.65, 30.8], [-116.2, 30.0], [-115.75, 29.0], [-115.55, 28.25], [-115.35, 27.75], [-114.6, 27.05], [-113.9, 26.45], [-113.1, 25.75], [-112.55, 25.05], [-112.15, 24.45], [-111.3, 23.75], [-110.5, 23.15], [-110.05, 22.78], [-109.85, 22.80], [-108.5, 22.0], [-106.6, 21.05], [-105.65, 20.72], [-105.45, 20.70], [-105.30, 20.66], ports.pv],
  pv_mz: [ports.pv, [-105.30, 20.66], [-105.45, 20.70], [-105.62, 20.74], [-105.75, 20.92], [-106.05, 21.25], [-106.35, 21.85], [-106.55, 22.35], [-106.55, 22.85], [-106.45, 23.12], [-106.425, 23.17], ports.mz],
  mz_cb: [ports.mz, [-106.425, 23.17], [-106.5, 23.13], [-107.5, 23.0], [-108.7, 22.9], [-109.6, 22.83], [-109.85, 22.85], ports.cb],
  cb_sd: [ports.cb, [-109.88, 22.83], [-110.05, 22.78], [-110.5, 23.12], [-111.3, 23.72], [-112.2, 24.4], [-112.6, 25.0], [-113.15, 25.72], [-113.95, 26.42], [-114.65, 27.02], [-115.4, 27.72], [-115.6, 28.25], [-115.8, 29.0], [-116.25, 30.0], [-116.7, 30.8], [-117.1, 31.6], [-117.35, 32.25], [-117.33, 32.55], [-117.24, 32.66], ports.sd],
};

const routeBBox = [-118.6, 19.9, -104.4, 33.3];
const poiLL = {
  sd: ports.sd, pv: ports.pv, mz: ports.mz, cb: ports.cb,
  la: [-118.41, 33.94], ens: [-116.60, 31.86], cedros: [-115.25, 28.18], ojo: [-114.15, 27.75],
  sanig: [-113.20, 26.80], mag: [-112.05, 24.60], lapaz: [-110.31, 24.14], marias: [-106.55, 21.60],
  marietas: [-105.58, 20.70], coronado: [-117.25, 32.42], tropicW: [-118.6, 23.4366], tropicE: [-104.4, 23.4366],
  guad: [-103.35, 20.67], tij: [-117.03, 32.53], culiacan: [-107.39, 24.80],
  L_bc: [-115.6, 30.6], L_bcs: [-112.15, 26.2], L_son: [-110.6, 29.6], L_sin: [-107.6, 25.3], L_jal: [-104.95, 20.15], L_nay: [-105.0, 21.75], L_usa: [-116.2, 33.05],
  W_pac: [-116.2, 24.6], W_cortez: [-111.4, 27.2], W_band: [-105.55, 20.55],
  t_lat20: [-118.55, 20], t_lat25: [-118.55, 25], t_lat30: [-118.55, 30], t_lon115: [-115, 33.25], t_lon110: [-110, 33.25], t_lon105: [-105, 33.25],
};
const route = makeMap(p1, routeBBox, 400, poiLL);
route.graticule = geoPath(route.proj).digits(1)(geoGraticule().step([5, 5]).extent([[-120, 15], [-100, 35]])());

// sample legs densely, check against land, compute nautical-mile lengths
const NM = 3440.065; // earth radius in nm
const landSel = route.sel.map(c => ({ type: 'Polygon', coordinates: c }));
function onLand(ll) { for (const g of landSel) if (geoContains(g, ll)) return true; return false; }
const legs = {};
for (const [k, wps] of Object.entries(legsWP)) {
  const samples = []; let dist = 0; const landHits = [];
  for (let i = 0; i < wps.length - 1; i++) {
    const a = wps[i], b = wps[i + 1];
    const d = geoDistance(a, b) * NM; const n = Math.max(2, Math.ceil(d / 4));
    const interp = geoInterpolate(a, b);
    for (let s = (i === 0 ? 0 : 1); s <= n; s++) {
      const ll = interp(s / n); const dd = dist + d * s / n;
      const inner = !(i === 0 && s < 3) && !(i === wps.length - 2 && s > n - 3);
      if (inner && onLand(ll)) landHits.push([ll.map(v => +v.toFixed(3)), +dd.toFixed(1)]);
      const [x, y] = route.proj(ll); samples.push([+x.toFixed(1), +y.toFixed(1), +dd.toFixed(1)]);
    }
    dist += d;
  }
  legs[k] = { nm: +dist.toFixed(0), samples, landHits: landHits.slice(0, 8), landHitCount: landHits.length };
}

// ---------- POIs along the track, tropic crossings ----------
const poiTrack = {};
const poiNames = ['coronado', 'ens', 'cedros', 'ojo', 'sanig', 'mag', 'cb', 'marias', 'marietas', 'pv', 'mz', 'lapaz', 'sd'];
for (const k of poiNames) {
  const ll = poiLL[k]; let best = null;
  for (const [leg, wps] of Object.entries(legsWP)) {
    let dist = 0;
    for (let i = 0; i < wps.length - 1; i++) {
      const a = wps[i], b = wps[i + 1], d = geoDistance(a, b) * NM, n = Math.max(2, Math.ceil(d / 2)), interp = geoInterpolate(a, b);
      for (let s = 0; s <= n; s++) { const p = interp(s / n), off = geoDistance(p, ll) * NM; if (!best || off < best.off) best = { leg, along: +(dist + d * s / n).toFixed(1), off: +off.toFixed(1) }; }
      dist += d;
    }
  }
  poiTrack[k] = best;
}
const tropic = {};
for (const [leg, wps] of Object.entries(legsWP)) {
  let dist = 0;
  for (let i = 0; i < wps.length - 1; i++) {
    const a = wps[i], b = wps[i + 1], d = geoDistance(a, b) * NM;
    if ((a[1] - 23.4366) * (b[1] - 23.4366) < 0) { const t = (23.4366 - a[1]) / (b[1] - a[1]); tropic[leg] = +(dist + d * t).toFixed(1); }
    dist += d;
  }
}

// ---------- Tectonics: split Baja (Pacific plate side) from mainland ----------
function nearestIdx(ring, ll) { let bi = 0, bd = 1e9; ring.forEach((p, i) => { const d = (p[0] - ll[0]) ** 2 + (p[1] - ll[1]) ** 2; if (d < bd) { bd = d; bi = i; } }); return bi; }
let na = route.sel[0]; for (const p of route.sel) if (p[0].length > na[0].length) na = p;
const ring = na[0].slice(0, -1);
const iT = nearestIdx(ring, [-117.12, 32.535]), iC = nearestIdx(ring, [-114.80, 31.70]), iK = nearestIdx(ring, [-109.90, 22.88]);
function chain(i0, i1) { const out = []; for (let i = i0; ; i = (i + 1) % ring.length) { out.push(ring[i]); if (i === i1) break; } return out; }
let c1 = chain(iT, iC), c2 = chain(iC, iT);
const inC1 = (() => { const n = ring.length; return ((iK - iT + n) % n) <= ((iC - iT + n) % n); })();
const bajaRing = inC1 ? c1 : c2, restRing = inC1 ? c2 : c1;
const close = r => [...r, r[0]];
const bajaPoly = rewind([close(bajaRing)]), restPoly = rewind([close(restRing), ...na.slice(1)]);
const axis = lat => { const t = (31.5 - lat) / 9; return -114.6 + t * 6.1; };
const islandsBaja = [], islandsRest = [];
for (const p of route.sel) {
  if (p === na) continue;
  const [x0, y0, x1, y1] = bboxOf(p), cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
  (cy < 32.3 && cx < axis(cy) ? islandsBaja : islandsRest).push(p);
}
const rpath = geoPath(route.proj).digits(1);
const tectBase = rpath({ type: 'MultiPolygon', coordinates: [restPoly, ...islandsRest] });
const tectBaja = rpath({ type: 'MultiPolygon', coordinates: [bajaPoly, ...islandsBaja] });
// 300 km rewind toward bearing 143° (reverse of ~N37W Pacific-plate motion)
const ctr = [-112.5, 27.0], R = 6371, brg = 143 * Math.PI / 180, dkm = 300;
const lat1 = ctr[1] * Math.PI / 180, lon1 = ctr[0] * Math.PI / 180, dd = dkm / R;
const lat2 = Math.asin(Math.sin(lat1) * Math.cos(dd) + Math.cos(lat1) * Math.sin(dd) * Math.cos(brg));
const lon2 = lon1 + Math.atan2(Math.sin(brg) * Math.sin(dd) * Math.cos(lat1), Math.cos(dd) - Math.sin(lat1) * Math.sin(lat2));
const [ax, ay] = route.proj(ctr), [bx, by] = route.proj([lon2 * 180 / Math.PI, lat2 * 180 / Math.PI]);
const tect = { base: tectBase, baja: tectBaja, dx: +(bx - ax).toFixed(1), dy: +(by - ay).toFixed(1), chainLen: bajaRing.length };
const capeTo = route.proj([-109.9 + (bx - ax) / route.proj.scale() * 180 / Math.PI, 22.88]);

// ---------- Port maps (100 m data) ----------
const cabo = makeMap(p100, [-109.935, 22.866, -109.875, 22.902], 400, {
  arch: [-109.8916, 22.8758], lovers: [-109.8935, 22.8778], divorce: [-109.8985, 22.8768], pelican: [-109.8985, 22.8800],
  marina: [-109.9125, 22.8835], tender: [-109.9108, 22.8818], medano: [-109.9030, 22.8890], anchor: [-109.9020, 22.8700],
  downtown: [-109.9160, 22.8890], pedregal: [-109.9235, 22.8780], solmar: [-109.9050, 22.8745],
});
const pv = makeMap(p100, [-105.66, 20.42, -105.17, 20.80], 400, {
  terminal: [-105.2525, 20.6545], malecon: [-105.2335, 20.6115], romantica: [-105.2370, 20.6010], muertos: [-105.2395, 20.6015],
  arcos: [-105.2985, 20.5440], mismaloya: [-105.2930, 20.5325], boca: [-105.3180, 20.5125], colomitos: [-105.3290, 20.5105],
  animas: [-105.3430, 20.5045], yelapa: [-105.4440, 20.4890], marietas: [-105.5800, 20.6990], puntamita: [-105.5230, 20.7690],
  botanical: [-105.3165, 20.4395], bucerias: [-105.3340, 20.7560], airport: [-105.2540, 20.6800],
}, 3);
const mz = makeMap(p100, [-106.475, 23.168, -106.395, 23.248], 400, {
  terminal: [-106.4180, 23.1930], faro: [-106.4270, 23.1790], machado: [-106.4235, 23.1990], cathedral: [-106.4215, 23.2005],
  olasaltas: [-106.4275, 23.1985], divers: [-106.4270, 23.2050], mercado: [-106.4185, 23.2030], venados: [-106.4645, 23.2365],
  piedra: [-106.4050, 23.1840], golden: [-106.4440, 23.2400], valentinos: [-106.4480, 23.2330], monumento: [-106.4290, 23.2180],
});

const strip = m => ({ width: m.width, height: m.height, bbox: m.bbox, land: m.land, pts: m.pts, graticule: m.graticule });
const out = {
  route: { ...strip(route), legs: Object.fromEntries(Object.entries(legs).map(([k, v]) => [k, { nm: v.nm, samples: v.samples }])), poiTrack, tropic },
  tect,
  cabo: strip(cabo), pv: strip(pv), mz: strip(mz),
};
fs.writeFileSync(outFile, JSON.stringify(out));
for (const [k, v] of Object.entries(legs)) console.error(k, 'nm=', v.nm, 'samples', v.samples.length, 'landHits', v.landHitCount, JSON.stringify(v.landHits));
console.error('poiTrack', JSON.stringify(poiTrack)); console.error('tropic', JSON.stringify(tropic)); console.error('tect', tect.dx, tect.dy, 'chain', tect.chainLen, 'baja chars', tect.baja.length, 'base chars', tect.base.length, 'islandsBaja', islandsBaja.length);
for (const k of ['route', 'cabo', 'pv', 'mz']) console.error(k, out[k].width + 'x' + out[k].height, 'landPathChars', out[k].land.length);
