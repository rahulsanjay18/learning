// Shared lesson widgets: core (item IDs, score bar, event log, sync, lesson footer) + generic widgets. No dependencies.
// Markup reference for lesson authors: assets/README.md. Live examples: assets/gallery.html.
// Plugins (assets/plugins/*.js) add widgets with LP.register({type, init, scored, selector}).
(function () {
  "use strict";
  var LP = window.LP = window.LP || {};
  var regs = [], started = false;
  var total = 0, answered = 0, firstTryRight = 0, bar = null;
  var missed = [], skipped = [], freeAnswers = [];

  // ---------- page identity + item IDs ----------
  var m = location.pathname.match(/\/topics\/([^\/]+)\/(lessons|reference)\/([^\/]+?)(\.html)?$/);
  var meta = document.querySelector('meta[name="lp-page"]');
  LP.page = meta ? meta.content : m ? m[1] + "/" + m[3] : location.pathname.replace(/^.*\//, "").replace(/\.html$/, "") || "page";
  LP.isLesson = m ? m[2] === "lessons" : !!meta;

  function itemId(el) {
    if (el.dataset.id) return el.dataset.id.indexOf("/") >= 0 ? el.dataset.id : LP.page + "#" + el.dataset.id;
    var all = document.querySelectorAll(".quiz[data-type]");
    return LP.page + "#q" + (Array.prototype.indexOf.call(all, el) + 1);
  }

  // ---------- storage, event log, sync ----------
  function store(key, val) {
    try {
      if (val === undefined) return localStorage.getItem(key);
      if (val === null) localStorage.removeItem(key); else localStorage.setItem(key, val);
    } catch (e) { return null; }
  }
  function queue() { try { return JSON.parse(store("lp.queue") || "[]"); } catch (e) { return []; } }
  function saveQueue(q) { store("lp.queue", JSON.stringify(q.slice(-1000))); }

  LP.emit = function (ev) {
    ev.v = 1; ev.page = LP.page; ev.ts = new Date().toISOString();
    ev.eid = Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 12); // server ignores resent events with the same eid
    var q = queue(); q.push(ev); saveQueue(q);
    document.dispatchEvent(new CustomEvent("lp:event", { detail: ev }));
    scheduleFlush();
  };

  var flushTimer = null;
  function scheduleFlush() { clearTimeout(flushTimer); flushTimer = setTimeout(LP.flush, 1500); }
  LP.syncConfigured = function () { return !!(store("lp.endpoint") && store("lp.token")); };
  LP.flush = function (keepalive) {
    var endpoint = store("lp.endpoint"), token = store("lp.token"), q = queue();
    if (!endpoint || !token || !q.length || !window.fetch) return;
    fetch(endpoint.replace(/\/$/, "") + "/events", {
      method: "POST", keepalive: !!keepalive,
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
      body: JSON.stringify({ events: q })
    }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      var now = queue(); saveQueue(now.slice(q.length)); // keep anything added while sending
      setStatus("Synced.");
    }).catch(function () { setStatus("Saved on this device; sync failed, will retry."); });
  };
  LP.configure = function (endpoint, token) { store("lp.endpoint", endpoint || null); store("lp.token", token || null); LP.flush(); };
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") LP.flush(true); });

  // ---------- scoring ----------
  function updateBar() {
    if (!bar) return;
    bar.textContent = answered + " / " + total + " answered · " + firstTryRight + " right first try";
  }

  function makeCtx(el, reg) {
    var id = itemId(el), done = false;
    return {
      id: id,
      // First call counts toward the score and is logged; later calls (retries) only update the UI.
      // ok: true/false, or null for answers sent for grading. kind: "auto" | "self" | "deferred".
      result: function (ok, answer, kind) {
        if (done) return; done = true;
        answered++;
        if (ok === true) firstTryRight++;
        if (kind === "skip") skipped.push(id.replace(/^.*#/, ""));
        else if (ok === false) missed.push(id.replace(/^.*#/, ""));
        if (kind === "deferred") freeAnswers.push({ id: id, answer: answer });
        updateBar();
        LP.emit({ type: "attempt", item: id, widget: reg.type, kind: kind || "auto", correct: ok, answer: answer == null ? null : String(answer).slice(0, 4000) });
      },
      feedback: function (ok, explainOrMsg) { feedback(el, ok, explainOrMsg); }
    };
  }

  // Verdict line; on success shows the .explain element, on failure the hint.
  function feedback(q, ok, extra) {
    var fb = q.querySelector(":scope > .feedback");
    if (!fb) { fb = document.createElement("div"); fb.className = "feedback"; fb.setAttribute("aria-live", "polite"); q.appendChild(fb); }
    fb.innerHTML = "";
    var v = document.createElement("span");
    v.className = "verdict " + (ok ? "ok" : "no");
    v.textContent = ok ? "Right. " : "Not quite. ";
    fb.appendChild(v);
    var explain = q.querySelector(":scope > .explain");
    if (ok && explain) { fb.appendChild(explain); explain.hidden = false; }
    if (!ok) fb.appendChild(document.createTextNode(typeof extra === "string" ? extra : q.dataset.hint || "Look again and try once more."));
  }

  // ---------- registry ----------
  LP.register = function (reg) {
    reg.selector = reg.selector || '.quiz[data-type="' + reg.type + '"]';
    if (reg.scored === undefined) reg.scored = true;
    regs.push(reg);
    if (started) scan();
  };

  function scan() {
    regs.forEach(function (reg) {
      document.querySelectorAll(reg.selector).forEach(function (el) {
        if (el.dataset.lpReady) return;
        el.dataset.lpReady = "1";
        if (reg.scored) total++;
        var ctx = makeCtx(el, reg);
        try { reg.init(el, ctx); if (reg.scored) addSkip(el, ctx); }
        catch (e) { el.dataset.lpError = String(e); console.error("lp widget " + reg.type + " failed:", e); }
      });
    });
    if (total && !bar) {
      bar = document.createElement("div");
      bar.className = "scorebar";
      (document.querySelector("main") || document.body).appendChild(bar);
    }
    updateBar();
  }

  // "I don't know" button, for pretests: <main data-skip="true"> (or on one .quiz). Counts as not known, reveals the answer.
  function addSkip(q, ctx) {
    var host = q.closest("[data-skip]");
    if (!host || host.dataset.skip === "false" || q.dataset.type === "checklist") return;
    var row = el("div", "skiprow"), b = el("button", "skip", "I don't know");
    b.addEventListener("click", function () {
      ctx.result(false, null, "skip");
      q.classList.add("skipped");
      q.querySelectorAll("input, textarea, button").forEach(function (x) { x.disabled = true; });
      var fb = q.querySelector(":scope > .feedback");
      if (!fb) { fb = el("div", "feedback"); q.appendChild(fb); }
      fb.innerHTML = "";
      fb.appendChild(el("span", "verdict no", "Skipped. "));
      var explain = q.querySelector(":scope > .explain");
      if (explain) { fb.appendChild(document.createTextNode("Here's the idea: ")); fb.appendChild(explain); explain.hidden = false; }
      row.remove();
    });
    row.appendChild(b); q.appendChild(row);
    document.addEventListener("lp:event", function (e) { if (e.detail.item === ctx.id && e.detail.kind !== "skip") row.remove(); });
  }

  // ---------- small DOM helpers (also used by plugins) ----------
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    if (tag === "button") e.type = "button";
    return e;
  }
  function split(s) { return (s || "").split("|").map(function (x) { return x.trim(); }).filter(function (x) { return x !== ""; }); }
  function shuffle(a) {
    a = a.slice();
    for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; }
    return a;
  }
  function norm(s, caseSensitive) {
    s = String(s).trim().replace(/\s+/g, " ");
    return caseSensitive ? s : s.toLowerCase();
  }
  // True if `given` matches any accepted answer (text, or number within tolerance).
  function matches(given, accepted, opts) {
    opts = opts || {};
    var g = norm(given, opts.caseSensitive);
    return accepted.some(function (a) {
      var gn = parseFloat(g.replace(/,/g, "")), an = parseFloat(String(a).replace(/,/g, ""));
      var numeric = /^[-+]?[\d.,]+(e[-+]?\d+)?$/i.test(g) && /^[-+]?[\d.,]+(e[-+]?\d+)?$/i.test(String(a).trim());
      if (numeric && !isNaN(gn) && !isNaN(an)) return Math.abs(gn - an) <= (opts.tolerance || 0) + 1e-9;
      return g === norm(a, opts.caseSensitive);
    });
  }
  function beforeExplain(q, node) { q.insertBefore(node, q.querySelector(":scope > .explain")); }
  LP.util = { el: el, split: split, shuffle: shuffle, matches: matches, feedback: feedback, beforeExplain: beforeExplain };

  // ---------- generic widgets ----------

  // Multiple choice. data-options="a|b|c" data-answer="b" [data-hint] [data-shuffle="true"]
  LP.register({ type: "choice", init: function (q, ctx) {
    var answer = q.dataset.answer, box = el("div", "choices");
    var opts = split(q.dataset.options);
    if (q.dataset.shuffle === "true") opts = shuffle(opts);
    opts.forEach(function (opt) {
      var b = el("button", null, opt);
      b.addEventListener("click", function () {
        var ok = opt === answer;
        ctx.result(ok, opt);
        b.classList.add(ok ? "right" : "wrong");
        if (ok) box.querySelectorAll("button").forEach(function (x) { x.disabled = true; });
        else b.disabled = true;
        ctx.feedback(ok);
      });
      box.appendChild(b);
    });
    beforeExplain(q, box);
  } });

  // Typed answer. data-answer="5" or "Paris|paris, france" [data-tolerance="0.1"] [data-case="true"]
  // "number" is the same widget with a numeric keyboard on phones.
  function initExact(q, ctx) {
    var accepted = split(q.dataset.answer), box = el("div", "choices");
    var input = el("input");
    input.type = "text"; input.setAttribute("aria-label", "answer");
    if (q.dataset.type === "number") input.inputMode = "decimal"; else input.style.width = "14rem";
    var b = el("button", null, "Check");
    function check() {
      if (!input.value.trim()) return;
      var ok = matches(input.value, accepted, { tolerance: parseFloat(q.dataset.tolerance) || 0, caseSensitive: q.dataset.case === "true" });
      ctx.result(ok, input.value);
      input.className = ok ? "ok" : "no";
      if (ok) { input.disabled = true; b.disabled = true; }
      ctx.feedback(ok);
    }
    b.addEventListener("click", check);
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") check(); });
    box.appendChild(input); box.appendChild(b);
    beforeExplain(q, box);
  }
  LP.register({ type: "number", init: initExact });
  LP.register({ type: "exact", init: initExact });

  // Free recall: write from memory, reveal the model answer (.explain), mark yourself.
  LP.register({ type: "recall", init: function (q, ctx) {
    var explain = q.querySelector(":scope > .explain");
    var ta = el("textarea"); ta.setAttribute("aria-label", "your answer"); ta.placeholder = "Write it from memory first…";
    var reveal = el("div", "choices reveal"), show = el("button", null, "Show answer");
    reveal.appendChild(show);
    show.addEventListener("click", function () {
      if (explain) explain.hidden = false;
      show.remove();
      var got = el("button", null, "I had it"), miss = el("button", null, "I missed some");
      [got, miss].forEach(function (b) {
        b.addEventListener("click", function () {
          ctx.result(b === got, ta.value, "self");
          b.classList.add(b === got ? "right" : "wrong");
          got.disabled = miss.disabled = true;
        });
        reveal.appendChild(b);
      });
    });
    beforeExplain(q, ta); beforeExplain(q, reveal);
  } });

  // Fill in the blanks: write [[answer|alternative]] inside .prompt (or .text). One Check button for all blanks.
  LP.register({ type: "cloze", init: function (q, ctx) {
    var host = q.querySelector(".text") || q.querySelector(".prompt"), blanks = [];
    var walker = document.createTreeWalker(host, NodeFilter.SHOW_TEXT), nodes = [];
    while (walker.nextNode()) if (/\[\[.+?\]\]/.test(walker.currentNode.nodeValue)) nodes.push(walker.currentNode);
    nodes.forEach(function (node) {
      var frag = document.createDocumentFragment(), parts = node.nodeValue.split(/(\[\[.+?\]\])/);
      parts.forEach(function (p) {
        var mm = p.match(/^\[\[(.+)\]\]$/);
        if (!mm) { if (p) frag.appendChild(document.createTextNode(p)); return; }
        var accepted = split(mm[1]), inp = el("input", "blank");
        inp.type = "text"; inp.setAttribute("aria-label", "blank " + (blanks.length + 1));
        inp.size = Math.max(4, accepted[0].length + 1);
        inp.addEventListener("keydown", function (e) { if (e.key === "Enter") check(); });
        blanks.push({ input: inp, accepted: accepted });
        frag.appendChild(inp);
      });
      node.parentNode.replaceChild(frag, node);
    });
    var box = el("div", "actions"), b = el("button", null, "Check");
    function check() {
      if (blanks.some(function (x) { return !x.input.value.trim(); })) { ctx.feedback(false, "Fill every blank first."); return; }
      var all = true;
      blanks.forEach(function (x) {
        var ok = matches(x.input.value, x.accepted, { caseSensitive: q.dataset.case === "true" });
        x.input.classList.remove("ok", "no"); x.input.classList.add(ok ? "ok" : "no");
        if (ok) x.input.disabled = true; else all = false;
      });
      ctx.result(all, blanks.map(function (x) { return x.input.value; }).join(" | "));
      if (all) b.disabled = true;
      ctx.feedback(all, all ? null : (q.dataset.hint || "The red blanks need another look."));
    }
    b.addEventListener("click", check);
    box.appendChild(b); beforeExplain(q, box);
  } });

  // Put items in order. data-items="first|second|third" (the correct order); shown shuffled, moved with ↑ ↓.
  LP.register({ type: "order", init: function (q, ctx) {
    var correct = split(q.dataset.items), cur = shuffle(correct), tries = 0;
    while (correct.length > 1 && cur.join("|") === correct.join("|") && tries++ < 20) cur = shuffle(correct);
    var list = el("ol", "lp-rows"), locked = false;
    function draw(marks) {
      list.innerHTML = "";
      cur.forEach(function (item, i) {
        var li = el("li"); if (marks) li.className = marks[i] ? "right" : "wrong";
        var up = el("button", null, "↑"), down = el("button", null, "↓");
        up.setAttribute("aria-label", "move up: " + item); down.setAttribute("aria-label", "move down: " + item);
        up.disabled = locked || i === 0; down.disabled = locked || i === cur.length - 1;
        up.addEventListener("click", function () { swap(i, i - 1); });
        down.addEventListener("click", function () { swap(i, i + 1); });
        li.appendChild(el("span", "label", (i + 1) + ". " + item)); li.appendChild(up); li.appendChild(down);
        list.appendChild(li);
      });
    }
    function swap(i, j) { var t = cur[i]; cur[i] = cur[j]; cur[j] = t; draw(); }
    var box = el("div", "actions"), b = el("button", null, "Check order");
    b.addEventListener("click", function () {
      var marks = cur.map(function (x, i) { return x === correct[i]; }), ok = marks.every(Boolean);
      ctx.result(ok, cur.join(" > "));
      if (ok) { locked = true; b.disabled = true; }
      draw(marks);
      ctx.feedback(ok, ok ? null : (q.dataset.hint || "Red rows are out of place."));
    });
    draw(); box.appendChild(b);
    beforeExplain(q, list); beforeExplain(q, box);
  } });

  // Sort items into buckets (also works as matching). data-buckets="A|B" data-items="item one>A|item two>B" [data-shuffle="false"]
  LP.register({ type: "categorize", init: function (q, ctx) {
    var buckets = split(q.dataset.buckets);
    var items = split(q.dataset.items).map(function (s) { var p = s.split(">"); return { text: p[0].trim(), answer: (p[1] || "").trim(), pick: null }; });
    if (q.dataset.shuffle !== "false") items = shuffle(items);
    var list = el("ul", "lp-rows");
    items.forEach(function (it) {
      var li = el("li"); it.li = li; it.btns = [];
      li.appendChild(el("span", "label", it.text));
      buckets.forEach(function (bk) {
        var bb = el("button", null, bk);
        bb.addEventListener("click", function () {
          it.pick = bk; li.className = "";
          it.btns.forEach(function (x) { x.classList.toggle("on", x === bb); });
        });
        it.btns.push(bb); li.appendChild(bb);
      });
      list.appendChild(li);
    });
    var box = el("div", "actions"), b = el("button", null, "Check");
    b.addEventListener("click", function () {
      if (items.some(function (it) { return !it.pick; })) { ctx.feedback(false, "Place every item first."); return; }
      var ok = true;
      items.forEach(function (it) {
        var right = it.pick === it.answer; ok = ok && right;
        it.li.className = right ? "right" : "wrong";
        if (right) it.btns.forEach(function (x) { x.disabled = true; });
      });
      ctx.result(ok, items.map(function (it) { return it.text + ">" + it.pick; }).join(" | "));
      if (ok) b.disabled = true;
      ctx.feedback(ok, ok ? null : (q.dataset.hint || "Red rows are in the wrong place."));
    });
    box.appendChild(b);
    beforeExplain(q, list); beforeExplain(q, box);
  } });

  // Real-world steps to tick off (self-reported). Put an <ol> or <ul> inside the .quiz.
  LP.register({ type: "checklist", init: function (q, ctx) {
    var list = q.querySelector("ol, ul"), lis = list ? list.querySelectorAll(":scope > li") : [];
    if (list) list.classList.add("lp-check");
    lis.forEach(function (li, i) {
      var cb = el("input"); cb.type = "checkbox"; cb.setAttribute("aria-label", "step " + (i + 1) + " done");
      var label = el("span", "label"); while (li.firstChild) label.appendChild(li.firstChild);
      li.appendChild(cb); li.appendChild(label);
      cb.addEventListener("change", function () {
        li.classList.toggle("done", cb.checked);
        var all = Array.prototype.every.call(lis, function (x) { return x.querySelector("input").checked; });
        if (all) { ctx.result(true, lis.length + " steps", "self"); ctx.feedback(true); }
      });
    });
  } });

  // Free response, graded later by the teacher. Optional .explain = model answer shown after submitting;
  // optional hidden .rubric is for the grader only.
  LP.register({ type: "free", init: function (q, ctx) {
    var explain = q.querySelector(":scope > .explain"), rubric = q.querySelector(":scope > .rubric");
    if (rubric) rubric.hidden = true;
    var ta = el("textarea"); ta.setAttribute("aria-label", "your answer"); ta.placeholder = q.dataset.placeholder || "Write your answer…";
    var box = el("div", "actions"), b = el("button", null, "Submit for feedback");
    b.addEventListener("click", function () {
      if (!ta.value.trim()) return;
      ctx.result(null, ta.value, "deferred");
      ta.readOnly = true; b.disabled = true;
      var fb = el("div", "feedback");
      fb.appendChild(el("span", "verdict ok", "Saved. "));
      fb.appendChild(document.createTextNode("Your teacher grades this at the start of the next session." + (explain ? " Compare with the model answer:" : "")));
      q.appendChild(fb);
      if (explain) { explain.hidden = false; fb.appendChild(explain); }
    });
    box.appendChild(b); beforeExplain(q, ta); beforeExplain(q, box);
  } });

  // YouTube embed (privacy-enhanced). <div class="lp-video" data-youtube="VIDEO_ID" [data-start="90"] [data-end="300"] data-caption="..."></div>
  LP.register({ type: "video", selector: ".lp-video[data-youtube]", scored: false, init: function (v) {
    var id = v.dataset.youtube, params = ["rel=0"];
    if (v.dataset.start) params.push("start=" + parseInt(v.dataset.start, 10));
    if (v.dataset.end) params.push("end=" + parseInt(v.dataset.end, 10));
    var frame = el("div", "frame"), f = el("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) + "?" + params.join("&");
    f.title = v.dataset.caption || "Video";
    f.loading = "lazy"; f.allowFullscreen = true;
    f.setAttribute("allow", "encrypted-media; picture-in-picture; fullscreen");
    frame.appendChild(f); v.appendChild(frame);
    var cap = el("div", "caption");
    if (v.dataset.caption) cap.appendChild(document.createTextNode(v.dataset.caption + " · "));
    var a = el("a", null, "open on YouTube");
    a.href = "https://www.youtube.com/watch?v=" + encodeURIComponent(id) + (v.dataset.start ? "&t=" + parseInt(v.dataset.start, 10) + "s" : "");
    a.target = "_blank"; a.rel = "noopener";
    cap.appendChild(a); v.appendChild(cap);
  } });

  // Worked example revealed one .step at a time. <div class="lp-worked"><div class="step">…</div>…</div>
  LP.register({ type: "worked", selector: ".lp-worked", scored: false, init: function (w) {
    var steps = w.querySelectorAll(":scope > .step"), shown = 1;
    if (steps.length < 2) return;
    steps.forEach(function (s, i) { s.hidden = i > 0; });
    var b = el("button", null, w.dataset.next || "Next step");
    b.addEventListener("click", function () {
      steps[shown].hidden = false; shown++;
      if (shown >= steps.length) b.remove();
    });
    w.appendChild(b);
  } });

  // ---------- lesson footer: rating, note, copy results, sync ----------
  var statusEl = null;
  function setStatus(t) { if (statusEl) statusEl.textContent = t; }

  LP.summary = function () {
    var parts = ["lp-results " + LP.page, firstTryRight + "/" + total + " right first try"];
    if (answered < total) parts.push((total - answered) + " unanswered");
    if (missed.length) parts.push("missed: " + missed.join(","));
    if (skipped.length) parts.push("skipped: " + skipped.join(","));
    if (LP.rating) parts.push("rating: " + LP.rating);
    if (LP.note) parts.push("note: " + LP.note.replace(/\s+/g, " "));
    var s = parts.join(" | ");
    freeAnswers.forEach(function (f) { s += "\nfree " + f.id.replace(/^.*#/, "") + ": " + f.answer.replace(/\s+/g, " "); });
    return s;
  };

  function footer() {
    var main = document.querySelector("main");
    if (!main || main.dataset.lpFooter === "off" || (!LP.isLesson && main.dataset.lpFooter !== "on")) return;
    var f = el("section", "lp-footer no-print");
    f.appendChild(el("div", null, "How did this lesson feel?"));
    var row = el("div", "row");
    [["too-easy", "Too easy"], ["just-right", "Just right"], ["too-hard", "Too hard"]].forEach(function (r) {
      var b = el("button", null, r[1]);
      b.addEventListener("click", function () {
        LP.rating = r[0];
        row.querySelectorAll("button").forEach(function (x) { x.classList.toggle("picked", x === b); });
        LP.emit({ type: "rating", value: r[0] });
      });
      row.appendChild(b);
    });
    f.appendChild(row);
    var ta = el("textarea"); ta.placeholder = "Anything confusing? (optional)"; ta.setAttribute("aria-label", "note to your teacher");
    f.appendChild(ta);
    var row2 = el("div", "row"), send = el("button", null, "Save note"), copy = el("button", null, "Copy my results");
    send.addEventListener("click", function () {
      if (!ta.value.trim()) return;
      LP.note = ta.value.trim(); LP.emit({ type: "note", text: LP.note }); setStatus("Note saved.");
    });
    copy.addEventListener("click", function () {
      var s = LP.summary();
      var done = function () { setStatus("Copied. Paste it to your teacher at the start of the next session."); };
      if (navigator.clipboard) navigator.clipboard.writeText(s).then(done, function () { window.prompt("Copy this:", s); });
      else window.prompt("Copy this:", s);
    });
    var cfg = el("button", null, "Sync settings");
    cfg.addEventListener("click", function () {
      var ep = window.prompt("Progress server URL (blank to turn sync off):", store("lp.endpoint") || "");
      if (ep === null) return;
      var tok = ep ? window.prompt("Device token:", "") : "";
      if (tok === null) return;
      LP.configure(ep.trim(), (tok || "").trim());
      setStatus(ep ? "Sync on for this device." : "Sync off. Results stay on this device.");
    });
    row2.appendChild(send); row2.appendChild(copy); row2.appendChild(cfg);
    f.appendChild(row2);
    statusEl = el("div", "status", LP.syncConfigured() ? "Results sync to your progress server." : "Results are saved on this device. Use “Copy my results” to share them.");
    f.appendChild(statusEl);
    var sb = main.querySelector(":scope > .scorebar");
    main.insertBefore(f, sb || null);
  }

  function start() { started = true; scan(); footer(); LP.flush(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else setTimeout(start, 0);
})();
