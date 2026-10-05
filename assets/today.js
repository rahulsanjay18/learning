/* Today page: the day's plan from programs.json + each major's curriculum.json, with tick-offs kept in this browser.
   planFor() is pure so scripts/test_today.mjs can check it in node. */
(function (root) {
  var DAYS = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];

  function pretty(stem) { return stem.replace(/^(\d{4})-/, "$1 ").replace(/-/g, " "); }

  // Weekday + ISO date in the program's time zone (falls back to the browser's).
  function localDay(now, tz) {
    try {
      var parts = new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit", weekday: "short" })
        .formatToParts(now);
      var get = function (t) { return parts.filter(function (p) { return p.type === t; })[0].value; };
      return { iso: get("year") + "-" + get("month") + "-" + get("day"), day: get("weekday").slice(0, 3).toLowerCase() };
    } catch (e) {
      return { iso: now.toISOString().slice(0, 10), day: DAYS[now.getDay()] };
    }
  }

  // One block's suggestion for a major: the newest lesson the learner hasn't finished, else "next lesson not written yet".
  function blockFor(major, cur) {
    if (!cur) return { major: major.name, setup: major.setup || "Not set up yet." };
    var items = cur.courses.filter(function (c) { return c.status === "active"; }).map(function (c) {
      var topic = c.topic || major.slug, lessons = c.lessons || [], done = c.completed || [];
      var todo = lessons.filter(function (s) { return done.indexOf(s) < 0; });
      var stem = todo.length ? todo[0] : null;
      return {
        course: c.id + " " + c.title,
        lesson: stem ? { title: pretty(stem), href: "../topics/" + topic + "/lessons/" + stem + ".html" } : null,
        next: (c.plan || [])[0] || null
      };
    });
    return { major: major.name, slug: major.slug, items: items };
  }

  function planFor(cfg, curricula, now) {
    var d = localDay(now, cfg.timezone || "UTC");
    var bySlug = {};
    cfg.majors.forEach(function (m) { bySlug[m.slug] = m; });
    var slugs = (cfg.week[d.day] || []).slice();
    // A full-weight major that isn't set up lends its block to the other full-weight major.
    slugs = slugs.map(function (s) {
      if (curricula[s]) return s;
      var other = cfg.majors.filter(function (m) { return m.weight === "full" && m.slug !== s && curricula[m.slug]; })[0];
      return other ? other.slug + "|" + s : s;
    });
    var blocks = slugs.map(function (s) {
      var parts = s.split("|"), m = bySlug[parts[0]];
      var b = blockFor(m, curricula[parts[0]]);
      if (parts[1]) b.covering = bySlug[parts[1]].name;
      return b;
    });
    return { date: d.iso, day: d.day, review: cfg.review, blocks: blocks };
  }

  root.LPToday = { planFor: planFor, pretty: pretty, localDay: localDay };
  if (typeof module !== "undefined") module.exports = root.LPToday;

  if (typeof document === "undefined") return;

  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); if (v) localStorage.setItem(k, "1"); else localStorage.removeItem(k); }
    catch (e) { return null; }
  }
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { if (k === "text") n.textContent = attrs[k]; else n.setAttribute(k, attrs[k]); });
    (kids || []).forEach(function (c) { n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function getJSON(url) { return fetch(url, { cache: "no-cache" }).then(function (r) { if (!r.ok) throw new Error(url + " " + r.status); return r.json(); }); }

  function render(plan) {
    var out = document.getElementById("today"), status = document.getElementById("today-status");
    var title = plan.day.charAt(0).toUpperCase() + plan.day.slice(1) + " " + plan.date;
    status.textContent = title + (plan.blocks.length ? ": review, then " + plan.blocks.length + " blocks of 25 minutes." : ": rest day. Review is optional.");
    var boxes = [];
    function row(key, label, body) {
      var id = "today." + plan.date + "." + key;
      var cb = el("input", { type: "checkbox", id: id });
      cb.checked = !!store(id);
      cb.addEventListener("change", function () { store(id, cb.checked); finish(); });
      boxes.push(cb);
      var li = el("li", {}, [cb, " ", el("label", { "for": id }, [el("strong", { text: label })])]);
      body.forEach(function (b) { li.appendChild(b); });
      return li;
    }
    var ol = el("ol", { "class": "today-plan" });
    var due = el("span", { "class": "muted" });
    ol.appendChild(row("review", "Daily review (10 min)", [el("p", {}, [el("a", { href: "review.html", text: "Open the review deck" }), " ", due])]));
    plan.blocks.forEach(function (b, i) {
      var body = [];
      if (b.covering) body.push(el("p", { "class": "muted", text: b.covering + " isn't set up yet, so this block goes to " + b.major + "." }));
      if (b.setup) body.push(el("p", { "class": "muted", text: b.setup }));
      (b.items || []).forEach(function (it, j) {
        var p = el("p", {}, [(b.items.length > 1 ? (j ? "or " : "") : "") + it.course + ": "]);
        if (it.lesson) p.appendChild(el("a", { href: it.lesson.href, text: it.lesson.title }));
        else p.appendChild(el("span", { text: "next lesson not written yet (run /program in a Claude session)." }));
        body.push(p);
      });
      ol.appendChild(row("block" + (i + 1), "Block " + (i + 1) + ": " + b.major + " (25 min)", body));
    });
    out.appendChild(ol);
    var done = el("p", { "class": "callout", hidden: "" });
    out.appendChild(done);
    function finish() {
      var all = boxes.every(function (c) { return c.checked; });
      done.hidden = !all;
      done.textContent = all ? "Today's plan is done. Extra time is yours: go deeper on whatever pulled you in, or practise early in the review deck." : "";
    }
    finish();
    var ep = store("lp.endpoint"), tok = store("lp.token");
    if (ep && tok) {
      fetch(ep + "/due?limit=50", { headers: { Authorization: "Bearer " + tok } })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) { if (j) { var n = (j.items || j).length; due.textContent = "(" + n + (n === 50 ? "+" : "") + " due)"; } })
        .catch(function () {});
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    getJSON("../programs.json").then(function (cfg) {
      var curricula = {};
      return Promise.all(cfg.majors.filter(function (m) { return m.curriculum; }).map(function (m) {
        return getJSON("../" + m.curriculum).then(function (c) { curricula[m.slug] = c; }).catch(function () {});
      })).then(function () { render(planFor(cfg, curricula, new Date())); });
    }).catch(function (e) {
      document.getElementById("today-status").textContent = "Couldn't load the plan (" + e.message + ").";
    });
  });
})(typeof window !== "undefined" ? window : globalThis);
