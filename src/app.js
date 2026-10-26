(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("guideData").textContent);
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem("kdg:" + k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem("kdg:" + k, JSON.stringify(v)); } catch (e) { /* storage unavailable */ } }
  };
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var DAY = 864e5, HR = 36e5;
  var START = Date.parse(D.start), END = Date.parse(D.end);
  var DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  function now() { return Date.now(); }
  function fmtLocal(ms, off, withDay) {
    var d = new Date(ms + off * HR), h = d.getUTCHours(), m = d.getUTCMinutes();
    var t = (h % 12 || 12) + ":" + (m < 10 ? "0" : "") + m + (h < 12 ? " am" : " pm");
    return withDay === false ? t : DOW[d.getUTCDay()] + " " + MON[d.getUTCMonth()] + " " + d.getUTCDate() + " · " + t;
  }
  function nf(n, d) { return Number(n).toLocaleString("en-US", { maximumFractionDigits: d || 0, minimumFractionDigits: d || 0 }); }
  function dur(ms) { var m = Math.max(0, Math.round(ms / 6e4)), h = Math.floor(m / 60); return (h ? h + " h " : "") + (m % 60) + " m"; }

  /* ---------------- routing ---------------- */
  var VIEWS = ["trip", "ship", "ports", "play", "pack"];
  function show(hash, keepScroll) {
    var h = (hash || "").replace(/^#/, ""), view = null, port = null, anchor = null;
    if (h.indexOf("ports-") === 0) { view = "ports"; port = h.slice(6); }
    else if (VIEWS.indexOf(h) >= 0) view = h;
    else if (h) {
      var el = document.getElementById(h);
      if (el) { var v = el.closest(".view"); if (v) view = v.id; var pp = el.closest(".port"); if (pp) port = pp.id.slice(6); anchor = el; }
    }
    if (!view) view = "trip";
    VIEWS.forEach(function (v) { var el = document.getElementById(v); if (el) el.classList.toggle("active", v === view); });
    $$(".tabbar a").forEach(function (a) { if (a.dataset.tab === view) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current"); });
    if (view === "ports") {
      if (!port || !document.getElementById("ports-" + port)) port = store.get("port", defaultPort());
      $$("#ports .port").forEach(function (p) { p.hidden = p.id !== "ports-" + port; });
      $$(".portnav .pill").forEach(function (p) { p.setAttribute("aria-current", p.dataset.port === port ? "true" : "false"); });
      store.set("port", port);
    }
    store.set("view", view);
    if (anchor) anchor.scrollIntoView({ block: "start" });
    else if (!keepScroll) window.scrollTo(0, 0);
  }
  function defaultPort() {
    var t = now();
    var map = [["2026-12-29", "pv"], ["2026-12-30", "mz"], ["2026-12-31", "cb"], ["2027-01-02", "sd"], ["2027-01-01", "sd"]];
    var iso = new Date(t - 7 * HR).toISOString().slice(0, 10);
    for (var i = 0; i < map.length; i++) if (map[i][0] === iso) return map[i][1];
    return t < Date.parse("2026-12-30T00:00:00Z") ? "pv" : "sd";
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a) return;
    var hsh = a.getAttribute("href");
    if (hsh.length < 2) return;
    e.preventDefault();
    show(hsh);
    try { history.replaceState(null, "", hsh); } catch (err) { /* ignore */ }
  });
  window.addEventListener("hashchange", function () { show(location.hash); });

  /* ---------------- voyage model ---------------- */
  var legs = D.legOrder.map(function (k) { var L = D.legs[k]; return { k: k, nm: L.nm, s: L.s, dep: Date.parse(L.dep), arr: Date.parse(L.arr), zones: L.zones }; });
  var names = { sd_pv: ["San Diego", "Puerto Vallarta"], pv_mz: ["Puerto Vallarta", "Mazatlán"], mz_cb: ["Mazatlán", "Cabo San Lucas"], cb_sd: ["Cabo San Lucas", "San Diego"] };
  var portZone = { "San Diego": -8, "Puerto Vallarta": -6, "Mazatlán": -7, "Cabo San Lucas": -7 };
  function sampleAt(L, along) {
    var s = L.s, lo = 0, hi = s.length - 1;
    if (along <= s[0][2]) return s[0].concat([s[1]]);
    if (along >= s[hi][2]) return s[hi].concat([s[hi - 1]], [true]);
    while (hi - lo > 1) { var mid = (lo + hi) >> 1; if (s[mid][2] <= along) lo = mid; else hi = mid; }
    var a = s[lo], b = s[hi], f = (along - a[2]) / ((b[2] - a[2]) || 1);
    return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, along, a[3] + (b[3] - a[3]) * f, a[4] + (b[4] - a[4]) * f, b];
  }
  function zoneAt(L, along) { var z = -8; L.zones.forEach(function (p) { if (along >= p[0]) z = p[1]; }); return z; }
  function stateAt(ms) {
    var sailed = 0;
    for (var i = 0; i < legs.length; i++) {
      var L = legs[i];
      if (ms < L.dep) {
        var at = names[L.k][0], p = L.s[0];
        return { mode: "port", place: at, x: p[0], y: p[1], lat: p[3], lon: p[4], hd: 0, zone: portZone[at], sailed: sailed, until: L.dep, leg: L };
      }
      if (ms <= L.arr) {
        var f = (ms - L.dep) / (L.arr - L.dep), along = f * L.nm, smp = sampleAt(L, along);
        var nx = smp[5], hd = Math.atan2(nx[1] - smp[1], nx[0] - smp[0]) * 180 / Math.PI;
        if (smp[6]) hd += 180;
        return { mode: "sea", leg: L, along: along, x: smp[0], y: smp[1], lat: smp[3], lon: smp[4], hd: hd, zone: zoneAt(L, along), sailed: sailed + along, speed: L.nm / ((L.arr - L.dep) / HR) };
      }
      sailed += L.nm;
    }
    var last = legs[legs.length - 1], q = last.s[last.s.length - 1];
    return { mode: "home", place: "San Diego", x: q[0], y: q[1], lat: q[3], lon: q[4], hd: 0, zone: -8, sailed: sailed };
  }
  function sunElev(ms, lat, lon) {
    var rad = Math.PI / 180, d = ms / DAY + 2440587.5 - 2451545.0;
    var g = (357.529 + 0.98560028 * d) * rad, q = 280.459 + 0.98564736 * d;
    var L = (q + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g)) * rad, e = (23.439 - 0.00000036 * d) * rad;
    var ra = Math.atan2(Math.cos(e) * Math.sin(L), Math.cos(L)), dec = Math.asin(Math.sin(e) * Math.sin(L));
    var gmst = ((18.697374558 + 24.06570982441908 * d) % 24 + 24) % 24;
    var ha = (gmst * 15 + lon) * rad - ra;
    return Math.asin(Math.sin(lat * rad) * Math.sin(dec) + Math.cos(lat * rad) * Math.cos(dec) * Math.cos(ha)) / rad;
  }
  function light(el) { return el > 0 ? "daylight" : el > -6 ? "twilight" : "night"; }

  var portNearby = {
    "San Diego": "Point Loma, the Navy piers and the Coronado Bridge.",
    "Puerto Vallarta": "Docked at Marina Vallarta, 3 miles north of the Malecón.",
    "Mazatlán": "Docked in the commercial port below El Faro.",
    "Cabo San Lucas": "At anchor off El Arco. Tenders run to the marina."
  };
  function nearby(st) {
    if (st.mode !== "sea") return portNearby[st.place] || "";
    var L = st.leg, best = null;
    D.pois.forEach(function (p) { if (p.leg === L.k && Math.abs(p.along - st.along) <= 45 && (!best || Math.abs(p.along - st.along) < Math.abs(best.along - st.along))) best = p; });
    var tr = D.tropic[L.k];
    if (tr != null && Math.abs(tr - st.along) <= 25) return "Crossing the Tropic of Cancer, 23°26′ N. " + (L.k === "sd_pv" ? "You're entering the tropics." : "Leaving the tropics behind.");
    if (best) return best.name + ". " + best.text;
    var next = null;
    D.pois.forEach(function (p) { if (p.leg === L.k && p.along > st.along && (!next || p.along < next.along)) next = p; });
    var dest = names[L.k][1];
    return "Open ocean. Next: " + (next ? next.name + " in " + nf(next.along - st.along) + " nm" : dest + " in " + nf(L.nm - st.along) + " nm") + ".";
  }

  /* ---------------- route slider ---------------- */
  var vr = $("#voyage");
  if (vr) {
    var mk = $("#shipMk"), playing = null;
    var render = function () {
      var ms = START + Number(vr.value) * 6e4, st = stateAt(ms);
      mk.setAttribute("transform", "translate(" + st.x.toFixed(1) + "," + st.y.toFixed(1) + ") rotate(" + st.hd.toFixed(0) + ")");
      var el = sunElev(ms, st.lat, st.lon);
      $("#rTime").textContent = fmtLocal(ms, st.zone) + " · " + light(el);
      if (st.mode === "port") $("#rStatus").textContent = (Number(vr.value) === 0 ? "Sailing from " : "In ") + st.place + (Number(vr.value) === 0 ? "" : " until " + fmtLocal(st.until, st.zone, false));
      else if (st.mode === "sea") $("#rStatus").textContent = "At sea → " + names[st.leg.k][1] + " · ETA " + fmtLocal(st.leg.arr, portZone[names[st.leg.k][1]], true);
      else $("#rStatus").textContent = "Home in San Diego";
      $("#rSailed").textContent = nf(st.sailed) + " nm · " + nf(st.sailed * 1.15078) + " mi";
      $("#rSpeed").textContent = st.mode === "sea" ? st.speed.toFixed(1) + " kn average" : "0 kn";
      $("#rNear").textContent = nearby(st);
    };
    vr.addEventListener("input", function () { if (playing) stop(); render(); });
    var stop = function () { cancelAnimationFrame(playing); playing = null; $("#vPlay").textContent = "Play voyage"; };
    $("#vPlay").addEventListener("click", function () {
      if (playing) return stop();
      if (Number(vr.value) >= Number(vr.max)) vr.value = 0;
      var t0 = performance.now(), v0 = Number(vr.value), span = Number(vr.max) - v0, dur = 28000 * span / Number(vr.max);
      $("#vPlay").textContent = "Pause";
      var step = function (t) {
        var f = Math.min(1, (t - t0) / dur);
        vr.value = Math.round((v0 + span * f) / 10) * 10; render();
        if (f < 1) playing = requestAnimationFrame(step); else stop();
      };
      playing = requestAnimationFrame(step);
    });
    $("#vNow").addEventListener("click", function () {
      var t = now();
      if (playing) stop();
      if (t < START) { vr.value = 0; render(); $("#rNear").textContent = "The trip hasn't started. " + Math.ceil((START - t) / DAY) + " days to sail away."; return; }
      vr.value = Math.min(Number(vr.max), Math.round((t - START) / 6e5) * 10); render();
    });
    var t = now();
    vr.value = t > START && t < END ? Math.round((t - START) / 6e5) * 10 : 0;
    render();
  }

  /* ---------------- header status ---------------- */
  var SHORT = { "Puerto Vallarta": "Vallarta", "Cabo San Lucas": "Cabo" };
  function status() {
    var t = now(), el = $("#status"), c2 = $("#countdown2");
    if (t < START) {
      var days = Math.ceil((START - t) / DAY);
      el.textContent = days + (days === 1 ? " day" : " days") + " to sail";
      if (c2) c2.textContent = days + " days until you sail";
    } else if (t <= END) {
      var st = stateAt(t), dayN = Math.floor((t - 8 * HR - Date.parse("2026-12-26T00:00:00Z")) / DAY) + 1;
      el.textContent = "Day " + dayN + " · " + (st.mode === "sea" ? "At sea" : (SHORT[st.place] || st.place));
      if (c2) c2.textContent = "You're on the ship";
    } else { el.textContent = "Welcome home"; if (c2) c2.textContent = ""; }
  }
  status();
  setInterval(status, 60000);

  /* ---------------- days ---------------- */
  (function () {
    var t = now();
    $$("details.day").forEach(function (d) {
      var iso = new Date(t - 8 * HR).toISOString().slice(0, 10);
      if (d.dataset.date === iso) { d.classList.add("today"); d.open = true; }
    });
  })();

  /* ---------------- deck explorer ---------------- */
  (function () {
    var bands = $$("#deckSvg .band");
    if (!bands.length) return;
    function select(n, scroll) {
      $$("#deckSvg [data-deck]").forEach(function (b) { b.classList.toggle("on", b.dataset.deck === String(n)); });
      $$("details.deck").forEach(function (d) { var on = d.dataset.deck === String(n); d.classList.toggle("on", on); if (on) d.open = true; });
      if (scroll) { var d = document.getElementById("deck" + n); if (d) d.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" }); }
    }
    bands.forEach(function (b) { b.addEventListener("click", function () { select(b.dataset.deck, true); }); });
    $$("details.deck").forEach(function (d) { d.addEventListener("toggle", function () { if (d.open) select(d.dataset.deck, false); }); });
    select(12, false);
  })();

  /* ---------------- power lab ---------------- */
  (function () {
    var sp = $("#spd");
    if (!sp) return;
    var GEN = 12.6, VMAX = 22.2, PODMAX = 28, HOTEL = 8.5, SFOC = 0.190, PAX = 2650;
    function setFlow(id, mw) {
      var f = document.getElementById(id);
      if (!f) return;
      f.setAttribute("stroke-width", mw > 0.05 ? (1.6 + mw * 0.32).toFixed(2) : 1.4);
      f.classList.toggle("idle", mw <= 0.05);
      f.classList.toggle("run", mw > 0.05);
      f.style.setProperty("--dur", Math.max(0.35, 2.2 - mw / 8).toFixed(2) + "s");
    }
    function update() {
      var v = Number(sp.value), prop = PODMAX * Math.pow(v / VMAX, 3), hotel = v < 0.5 ? 7.5 : HOTEL, total = prop + hotel;
      var eng = Math.max(1, Math.ceil(total / (GEN * 0.85))), each = total / eng;
      var tday = total * 24 * SFOC, gph = tday / 0.99 * 264.172 / 24, mph = v * 1.15078, gpm = mph > 0 ? gph / mph : 0;
      $("#spdOut").textContent = v.toFixed(1);
      for (var i = 0; i < 4; i++) {
        var on = i < eng;
        document.getElementById("gen" + i).classList.toggle("off", !on);
        document.getElementById("genT" + i).classList.toggle("off", !on);
        $("#genV" + i).textContent = on ? each.toFixed(1) + " MW · " + Math.round(each / GEN * 100) + "%" : "standby";
        setFlow("genF" + i, on ? each : 0);
      }
      ["pod0", "pod1"].forEach(function (p) {
        setFlow(p + "F", prop / 2);
        $("#" + p + "V").textContent = (prop / 2).toFixed(1) + " MW";
        var pr = $("#" + p + "P");
        if (pr) { pr.classList.toggle("spin", v > 0.2); pr.style.setProperty("--spin", Math.max(0.25, 3 - v / 8).toFixed(2) + "s"); }
      });
      setFlow("thrF", 0); $("#thrV").textContent = "0 MW";
      setFlow("hotelF", hotel); $("#hotelV").textContent = hotel.toFixed(1) + " MW";
      $("#fuelV").textContent = nf(tday) + " t/day";
      $("#totV").textContent = total.toFixed(1) + " MW total";
      $("#engV").textContent = "ENGINES ONLINE: " + eng + " OF 4";
      $("#gTotal").textContent = total.toFixed(1) + " MW";
      $("#gHp").textContent = nf(Math.round(total * 1341 / 100) * 100) + " hp";
      $("#gEng").textContent = eng + " of 4 · " + Math.round(each / GEN * 100) + "%";
      $("#gFuel").textContent = nf(tday) + " t";
      $("#gGph").textContent = nf(Math.round(gph / 10) * 10) + " gal";
      $("#gGpm").textContent = v > 0.2 ? nf(gpm) + " gal" : "—";
      $("#gPmpg").textContent = v > 0.2 ? nf(PAX / gpm) : "—";
      $("#gCo2").textContent = nf(tday * 3.114) + " t";
      $("#gLeg").textContent = v > 0.2 ? nf(1037 / v) + " h" : "—";
      $$("#spdPresets .pill").forEach(function (b) { b.classList.toggle("on", Math.abs(Number(b.dataset.v) - v) < 0.05); });
    }
    sp.addEventListener("input", update);
    $$("#spdPresets .pill").forEach(function (b) { b.addEventListener("click", function () { sp.value = b.dataset.v; update(); }); });
    update();
  })();

  /* ---------------- tectonics ---------------- */
  (function () {
    var r = $("#tectR"), g = $("#bajaPlate");
    if (!r || !g) return;
    var dx = Number(g.dataset.dx), dy = Number(g.dataset.dy), anim = null;
    function upd() {
      var f = Number(r.value) / 60, ma = (Number(r.value) / 10).toFixed(1);
      g.setAttribute("transform", "translate(" + (dx * f).toFixed(1) + "," + (dy * f).toFixed(1) + ")");
      var lab = f === 0 ? "Today" : ma + " million years ago";
      $("#tectOut").textContent = f === 0 ? "today" : ma + " million years ago · Baja " + Math.round(300 * f) + " km southeast";
      $("#tectLabel").textContent = lab;
      $("#tectArrow").style.opacity = f === 0 ? 1 : 0.25;
    }
    r.addEventListener("input", function () { if (anim) { cancelAnimationFrame(anim); anim = null; } upd(); });
    $("#tectPlay").addEventListener("click", function () {
      if (anim) { cancelAnimationFrame(anim); anim = null; return; }
      var t0 = performance.now(), D1 = 4000, HOLD = 1200;
      var step = function (t) {
        var e = t - t0, v;
        if (e < D1) v = 60 * (e / D1); else if (e < D1 + HOLD) v = 60; else if (e < 2 * D1 + HOLD) v = 60 * (1 - (e - D1 - HOLD) / D1); else v = 0;
        r.value = Math.round(v); upd();
        if (e < 2 * D1 + HOLD) anim = requestAnimationFrame(step); else anim = null;
      };
      anim = requestAnimationFrame(step);
    });
    upd();
  })();

  /* ---------------- port-day countdowns ---------------- */
  function portClock() {
    var t = now();
    $$(".countdown").forEach(function (c) {
      var off = Number(c.dataset.utc), iso = new Date(t + off * HR).toISOString().slice(0, 10);
      var port = c.closest(".port");
      $$(".track .now", port).forEach(function (n) { n.remove(); });
      if (iso !== c.dataset.date || !c.dataset.aboard) { c.classList.remove("show"); return; }
      var p = c.dataset.date.split("-").map(Number), a = c.dataset.aboard.split(":").map(Number);
      var aboard = Date.UTC(p[0], p[1] - 1, p[2], a[0], a[1]) - off * HR;
      c.classList.add("show");
      $("b", c).textContent = aboard > t ? dur(aboard - t) + " to go" : "Should be aboard now";
      var o = c.dataset.open.split(":").map(Number), cl = c.dataset.close.split(":").map(Number);
      var o0 = Date.UTC(p[0], p[1] - 1, p[2], o[0], o[1]) - off * HR, o1 = Date.UTC(p[0], p[1] - 1, p[2], cl[0], cl[1]) - off * HR;
      if (t > o0 && t < o1) $$(".track", port).forEach(function (tr) { var n = document.createElement("div"); n.className = "now"; n.style.left = ((t - o0) / (o1 - o0) * 100).toFixed(2) + "%"; tr.appendChild(n); });
    });
  }
  portClock();
  setInterval(portClock, 30000);

  /* ---------------- cabins ---------------- */
  (function () {
    var nums = $$(".cabnum");
    if (!nums.length) return;
    var saved = store.get("cabins", []);
    function deckOf(v) { var n = parseInt(v, 10); return n >= 1000 && n < 13000 ? Math.floor(n / 1000) : null; }
    function render() {
      var data = [];
      nums.forEach(function (inp, i) {
        var who = $("#cabWho" + i).value.trim(), num = inp.value.trim(), d = deckOf(num);
        $("#cabDeck" + i).textContent = d ? "Deck " + d : "";
        data.push([who, num]);
      });
      store.set("cabins", data);
      $$("[data-deckcab]").forEach(function (p) {
        var list = data.filter(function (x) { return deckOf(x[1]) === Number(p.dataset.deckcab); });
        p.hidden = !list.length;
        p.textContent = list.map(function (x) { return "Cabin " + x[1] + ": " + x[0]; }).join(" · ");
      });
      var g = $("#cabDots");
      if (g) {
        var cy = JSON.parse(g.dataset.cy);
        g.innerHTML = "";
        data.forEach(function (x, i) {
          var d = deckOf(x[1]);
          if (!d) return;
          var c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          c.setAttribute("class", "cabdot cab" + i);
          c.setAttribute("cx", 190 + 15 * i);
          c.setAttribute("cy", cy[d]);
          c.setAttribute("r", 5);
          var t = document.createElementNS("http://www.w3.org/2000/svg", "title");
          t.textContent = (x[0] || "Cabin") + " · " + x[1];
          c.appendChild(t);
          g.appendChild(c);
        });
      }
    }
    nums.forEach(function (inp, i) {
      var w = $("#cabWho" + i);
      if (saved[i]) { if (saved[i][0]) w.value = saved[i][0]; inp.value = saved[i][1] || ""; }
      inp.addEventListener("input", render); w.addEventListener("input", render);
    });
    render();
  })();

  /* ---------------- trivia ---------------- */
  (function () {
    var box = $("#quiz");
    if (!box) return;
    var cat = "all", list = [], i = 0, answered = false;
    function shuffle(a) { for (var j = a.length - 1; j > 0; j--) { var k = Math.floor(Math.random() * (j + 1)), t = a[j]; a[j] = a[k]; a[k] = t; } return a; }
    function start() { list = shuffle(D.quiz.filter(function (q) { return cat === "all" || q.c === cat; }).slice()); i = 0; ask(); }
    function ask() {
      answered = false;
      var opts = $("#qOpts"); opts.innerHTML = "";
      $("#qEx").textContent = "";
      if (i >= list.length) {
        $("#qText").textContent = "That's every question" + (cat === "all" ? "" : " in " + cat) + ". Shuffle to go again, or pick another category.";
        $("#qProg").textContent = "All done"; $("#qNext").hidden = true; return;
      }
      $("#qNext").hidden = false;
      var q = list[i];
      $("#qProg").textContent = q.c + " · " + (i + 1) + " of " + list.length;
      $("#qText").textContent = q.q;
      var order = shuffle(q.o.map(function (_, k) { return k; }));
      order.forEach(function (k) {
        var b = document.createElement("button"); b.type = "button"; b.className = "opt"; b.textContent = q.o[k]; b.dataset.k = k;
        b.addEventListener("click", function () {
          if (answered) return; answered = true;
          $$(".opt", opts).forEach(function (x) { x.disabled = true; if (Number(x.dataset.k) === q.a) x.classList.add("right"); });
          if (k === q.a) { $("#qEx").textContent = "Right. " + q.x; } else { b.classList.add("wrong"); $("#qEx").textContent = "Not quite. " + q.x; }
        });
        opts.appendChild(b);
      });
    }
    $("#qNext").addEventListener("click", function () { i++; ask(); });
    $("#qRestart").addEventListener("click", start);
    $$("#qCats .pill").forEach(function (p) { p.addEventListener("click", function () { cat = p.dataset.c; $$("#qCats .pill").forEach(function (x) { x.classList.toggle("on", x === p); }); start(); }); });
    start();
  })();

  /* ---------------- fact shuffle ---------------- */
  (function () {
    var btn = $("#fcNext");
    if (!btn) return;
    var deck = [], n = 0;
    function draw() {
      if (n >= deck.length) { deck = D.facts.map(function (_, k) { return k; }); for (var j = deck.length - 1; j > 0; j--) { var k = Math.floor(Math.random() * (j + 1)), t = deck[j]; deck[j] = deck[k]; deck[k] = t; } n = 0; }
      var f = D.facts[deck[n++]];
      $("#fcSrc").textContent = f[0] + " · fact " + n + " of " + deck.length;
      $("#fcText").textContent = f[1];
    }
    btn.addEventListener("click", draw);
    draw();
  })();

  /* ---------------- wildlife ---------------- */
  (function () {
    var boxes = $$("[data-spot]");
    if (!boxes.length) return;
    var seen = store.get("spotted", {});
    function count() { var c = boxes.filter(function (b) { return b.checked; }).length; $("#spotCount").textContent = c + " of " + boxes.length + " spotted so far."; }
    boxes.forEach(function (b) {
      b.checked = !!seen[b.dataset.spot];
      b.addEventListener("change", function () { seen[b.dataset.spot] = b.checked ? Date.now() : 0; store.set("spotted", seen); count(); });
    });
    count();
  })();

  /* ---------------- packing ---------------- */
  (function () {
    var boxes = $$("[data-pack]");
    if (!boxes.length) return;
    var done = store.get("packed2", {});
    function prog() {
      var c = boxes.filter(function (b) { return b.checked; }).length;
      $("#packCount").textContent = c + " of " + boxes.length + " packed";
      $("#packBar").style.width = (c / boxes.length * 100).toFixed(1) + "%";
    }
    boxes.forEach(function (b) {
      b.checked = !!done[b.dataset.pack];
      b.addEventListener("change", function () { done[b.dataset.pack] = b.checked; store.set("packed2", done); prog(); });
    });
    var reset = $("#packReset"), conf = $("#packConfirm"), tmr = null;
    reset.addEventListener("click", function () { conf.hidden = false; clearTimeout(tmr); tmr = setTimeout(function () { conf.hidden = true; }, 5000); });
    conf.addEventListener("click", function () { boxes.forEach(function (b) { b.checked = false; }); done = {}; store.set("packed2", done); conf.hidden = true; prog(); });
    prog();
  })();

  show(location.hash || "#" + store.get("view", "trip"), true);
})();
