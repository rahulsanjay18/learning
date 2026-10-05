// Daily review deck (assets/review.html). Re-asks questions that are due on the spaced schedule, across all topics.
// Due items come from this browser's schedule (LP.schedule(), kept by lp.js) and, when sync is on, from the progress server.
// Each question is pulled from its original lesson page, so it looks and behaves exactly as it did there.
// A quiz can name extra elements to bring along with data-context="id1 id2"; otherwise a diagram (.board-wrap, .go-board,
// .lp-plot, .px, figure, table) directly before the quiz is brought along automatically.
(function () {
  "use strict";
  var MAX = 20, DAY = 864e5;
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
    return sec;
  }

  function build(items, note) {
    var list = interleave(items).slice(0, MAX);
    return Promise.all(list.map(function (it) { return fetchPage(it.item.split("#")[0]).then(function (f) { return card(it, f); }); }))
      .then(function (cards) {
        var shown = cards.filter(Boolean);
        shown.forEach(function (c) { root.appendChild(c); });
        var missing = cards.length - shown.length;
        head.textContent = note.replace("{n}", shown.length) + (missing ? " (" + missing + " couldn't be loaded: the lesson changed.)" : "");
        LP.scan();
        if (window.LPMath && LPMath.typeset) LPMath.typeset(root);
      });
  }

  function start() {
    var sched = LP.schedule(), now = new Date().toISOString();
    serverDue().then(function (rows) {
      var all = {};
      Object.keys(sched).forEach(function (k) { all[k] = { item: k, due: sched[k].due }; });
      rows.forEach(function (r) { if (!all[r.item] || r.due < all[r.item].due) all[r.item] = { item: r.item, due: r.due }; });
      var items = Object.keys(all).map(function (k) { return all[k]; }).filter(function (it) { return it.item.indexOf("/") > 0 && it.item.indexOf("#") > 0; });
      var due = items.filter(function (it) { return it.due <= now; });
      var week = items.filter(function (it) { return it.due > now && new Date(it.due) - new Date() < 7 * DAY; }).length;
      if (due.length) return build(due, "{n} due now" + (due.length > MAX ? " (showing the " + MAX + " most overdue)" : "") + " · " + week + " more this week.");
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
