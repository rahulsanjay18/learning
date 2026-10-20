// Daily review deck (assets/review.html). Re-asks questions that are due on the spaced schedule, across all topics.
// Due items come from this browser's schedule (LP.schedule(), kept by lp.js) and, when sync is on, from the progress server.
// Each question is pulled from its original lesson page, so it looks and behaves exactly as it did there.
// A quiz can name extra elements to bring along with data-context="id1 id2"; otherwise a diagram (.board-wrap, .go-board,
// .lp-plot, .px, figure, table) directly before the quiz is brought along automatically.
(function () {
  "use strict";
  // A session is a time budget, not a count (2026-10-10: "20 questions in 10 minutes is not realistic, especially free response").
  // Minutes per question type are estimates (judgment, not measured yet); a free response is the expensive one, so at most
  // MAX_FREE per session. Whatever doesn't fit stays due and comes first next time; "A few more" adds another short batch.
  var BUDGET = 10, MORE = 5, MAX_FREE = 1, DAY = 864e5;
  var COST = { free: 3, recall: 1, math: 1, number: 1, order: 1, categorize: 1, highlight: 1, "find-error": 1, "timeline-place": 1,
    "map-locate": 1, estimate: 1, py: 2, "chess-move": 1, "go-move": 1, "game-move": 1, "xiangqi-move": 1, "shogi-move": 1, "plot-set": 1 };
  function cost(type) { return COST[type] || 0.5; }   // choice, exact, cloze, card: about 30 seconds

  // What comes back is decided by mastery, not by "every question ever answered" (2026-10-10):
  //  1. NOT YET: items missed, skipped or guessed (box 0), and anything a learning record graded Not yet (mastery.json).
  //  2. STALE: items known (box >= 1, or graded Got it) come back only when last seen STALE_DAYS or more ago.
  //  One item per question family (page#family, "-vN" or "-N" suffix dropped) per session.
  // topics/<topic>/mastery.json: {"not_yet": ["page#id-or-family", ...], "got": [...]}, written with the learning records.
  var STALE_DAYS = 14;
  function family(item) { return item.replace(/-v?\d+$/, ""); }
  var mastery = {};
  function loadMastery(topics) {
    return Promise.all(topics.map(function (t) {
      return fetch(new URL("../topics/" + t + "/mastery.json", location.href).href)
        .then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })
        .then(function (m) { (m.not_yet || []).forEach(function (k) { mastery[k] = "not_yet"; }); (m.got || []).forEach(function (k) { mastery[k] = "got"; }); });
    }));
  }
  function graded(item) { return mastery[item] || mastery[family(item)] || null; }
  function notYet(it) { var g = graded(it.item); return g ? g === "not_yet" : !(it.box >= 1); }
  function stale(it, now) { return !it.last || now - new Date(it.last) >= STALE_DAYS * DAY; }
  function oneEach(items) {
    var seen = {};
    return items.filter(function (it) { var f = family(it.item); if (seen[f]) return false; seen[f] = 1; return true; });
  }
  var root = document.getElementById("deck"), head = document.getElementById("deck-status");

  function store(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function fmtDay(iso) { return new Date(iso).toLocaleDateString(undefined, { weekday: "short", month: "short", day: "numeric" }); }

  function serverDue() {
    var ep = store("lp.endpoint"), tok = store("lp.token");
    if (!ep || !tok || !window.fetch) return Promise.resolve([]);
    return fetch(ep.replace(/\/$/, "") + "/due?limit=200", { headers: { Authorization: "Bearer " + tok } })
      .then(function (r) { return r.ok ? r.json() : []; }).catch(function () { return []; });
  }

  // Reading-guide boxes (ids "read-…") are the learner's notes on a reading, not questions: never re-ask them.
  var NOTE = /#read-/;
  // Interleave topics: round-robin over topics, each topic's items oldest-due first.
  function interleave(items) {
    var by = {};
    items.forEach(function (it) { var t = it.item.split("/")[0]; (by[t] = by[t] || []).push(it); });
    Object.keys(by).forEach(function (t) { by[t].sort(function (a, b) { return a.due < b.due ? -1 : 1; }); });
    var out = [], topics = Object.keys(by);
    while (out.length < items.length) topics.forEach(function (t) { if (by[t].length) out.push(by[t].shift()); });
    return out;
  }

  var docs = {};
  function fetchPage(page) {
    if (docs[page]) return docs[page];
    var parts = page.split("/");
    var base = new URL("../topics/" + parts[0] + "/", location.href).href;
    var urls = [base + "lessons/" + parts[1] + ".html", base + "reference/" + parts[1] + ".html"];
    docs[page] = urls.reduce(function (p, u) {
      return p.then(function (found) {
        if (found) return found;
        return fetch(u).then(function (r) { return r.ok ? r.text().then(function (t) { return { url: u, doc: new DOMParser().parseFromString(t, "text/html") }; }) : null; })
          .catch(function () { return null; });
      });
    }, Promise.resolve(null));
    return docs[page];
  }

  function findQuiz(doc, local) {
    var byId = Array.prototype.find.call(doc.querySelectorAll(".quiz[data-type]"), function (q) { return q.dataset.id === local; });
    if (byId) return byId;
    var m = /^q(\d+)$/.exec(local);
    return m ? doc.querySelectorAll(".quiz[data-type]")[parseInt(m[1], 10) - 1] || null : null;
  }

  function contextFor(doc, q) {
    var out = [];
    (q.dataset.context || "").split(/\s+/).filter(Boolean).forEach(function (id) { var c = doc.getElementById(id); if (c) out.push(c); });
    if (!out.length) {
      var prev = q.previousElementSibling;
      if (prev && prev.matches(".board-wrap, .go-board, .lp-plot, .px, figure, table")) out.push(prev);
    }
    return out;
  }

  // Imported nodes keep relative links; point them at the lesson's folder.
  function rebase(node, baseUrl) {
    [node].concat(Array.prototype.slice.call(node.querySelectorAll("[href], [src]"))).forEach(function (n) {
      ["href", "src"].forEach(function (a) {
        var v = n.getAttribute && n.getAttribute(a);
        if (v && !/^(#|[a-z]+:)/i.test(v)) n.setAttribute(a, new URL(v, baseUrl).href);
      });
    });
    return node;
  }

  function card(it, found) {
    if (found && found.doc.querySelector('main[data-pretest="true"]')) { LP.unschedule(it.item); return "pretest"; }   // never taught: not review
    var local = it.item.slice(it.item.indexOf("#") + 1);
    var q = found && findQuiz(found.doc, local);
    if (!q) return null;
    var sec = el("section", "review-card");
    var topic = it.item.split("/")[0], title = (found.doc.title || it.item.split("#")[0].split("/")[1]).trim();
    var label = el("p", "small muted"), a = el("a", null, title);
    a.href = found.url; label.appendChild(document.createTextNode(topic.charAt(0).toUpperCase() + topic.slice(1).replace(/-/g, " ") + " · ")); label.appendChild(a);
    sec.appendChild(label);
    contextFor(found.doc, q).forEach(function (c) { sec.appendChild(rebase(document.importNode(c, true), found.url)); });
    var clone = rebase(document.importNode(q, true), found.url);
    clone.dataset.id = it.item;            // keep the original item id, so answers update the right schedule entry
    sec.appendChild(clone);
    return { sec: sec, type: q.dataset.type };
  }

  // Take cards in order until the budget is spent; free responses beyond MAX_FREE wait for another day.
  function pick(cards, budget, freeLeft) {
    var take = [], rest = [], spent = 0;
    cards.forEach(function (c) {
      var m = cost(c.type), isFree = c.type === "free";
      if ((take.length && spent + m > budget) || (isFree && freeLeft <= 0)) { rest.push(c); return; }
      take.push(c); spent += m; if (isFree) freeLeft--;
    });
    return { take: take, rest: rest, spent: spent };
  }

  function show(list) {
    list.forEach(function (c) { root.appendChild(c.sec); });
    LP.scan();
    if (window.LPMath && LPMath.typeset) LPMath.typeset(root);
  }

  function moreButton(rest) {
    if (!rest.length) return;
    var b = el("button", null, "A few more (about " + MORE + " minutes)");
    b.type = "button";
    b.addEventListener("click", function () {
      b.remove();
      var p = pick(rest, MORE, MAX_FREE);
      show(p.take);
      moreButton(p.rest);
    });
    root.parentNode.appendChild(b);
  }

  function build(items, note) {
    var list = items;
    return Promise.all(list.map(function (it) { return fetchPage(it.item.split("#")[0]).then(function (f) { return card(it, f); }); }))
      .then(function (cards) {
        var pre = cards.filter(function (c) { return c === "pretest"; }).length;
        var ok = cards.filter(function (c) { return c && c !== "pretest"; });
        var missing = cards.length - ok.length - pre;
        if (!ok.length && !missing) { head.textContent = "All caught up."; return; }
        var p = pick(ok, BUDGET, MAX_FREE);
        show(p.take);
        head.textContent = note.replace("{n}", p.take.length).replace("{m}", Math.round(p.spent)) +
          (p.rest.length ? " " + p.rest.length + " more wait for another day." : "") +
          (missing ? " (" + missing + " couldn't be loaded: the lesson changed.)" : "");
        moreButton(p.rest);
      });
  }

  function start() {
    var sched = LP.schedule(), now = new Date().toISOString();
    serverDue().then(function (rows) {
      var tops = {}; Object.keys(sched).concat(rows.map(function (r) { return r.item; })).forEach(function (k) { tops[k.split("/")[0]] = 1; });
      return loadMastery(Object.keys(tops)).then(function () { return rows; });
    }).then(function (rows) {
      var all = {};
      Object.keys(sched).forEach(function (k) { var g = sched[k]; all[k] = { item: k, due: g.due, box: g.box, last: g.last }; });
      rows.forEach(function (r) { if (!all[r.item] || r.due < all[r.item].due) all[r.item] = { item: r.item, due: r.due, box: r.box, last: r.last }; });
      var items = Object.keys(all).map(function (k) { return all[k]; }).filter(function (it) { return it.item.indexOf("/") > 0 && it.item.indexOf("#") > 0 && !NOTE.test(it.item); });
      var t = new Date();
      // Not yet: due, or graded Not yet and not seen today. Known: due and stale.
      var due = items.filter(function (it) {
        return notYet(it) ? (it.due <= now || !it.last || t - new Date(it.last) >= DAY) : (it.due <= now && stale(it, t));
      });
      due = oneEach(interleave(due.filter(notYet)).concat(interleave(due.filter(function (it) { return !notYet(it); }))));
      var week = items.filter(function (it) { return it.due > now && new Date(it.due) - new Date() < 7 * DAY; }).length;
      if (due.length) return build(due, "Today: {n} questions, about {m} minutes, most overdue first. " + week + " more come due this week.");
      if (!items.length) { head.textContent = "Nothing to review yet. Questions you miss or skip in lessons show up here on a spaced schedule."; return; }
      var next = items.slice().sort(function (a, b) { return a.due < b.due ? -1 : 1; });
      head.textContent = "All caught up. Next review: " + fmtDay(next[0].due) + " · " + week + " this week.";
      var b = el("button", null, "Practice the next " + Math.min(10, next.length) + " early");
      b.type = "button";
      b.addEventListener("click", function () { b.remove(); build(next.slice(0, 10), "{n} practiced early."); });
      head.appendChild(document.createTextNode(" ")); head.appendChild(b);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { setTimeout(start, 0); }); else setTimeout(start, 0);
})();
