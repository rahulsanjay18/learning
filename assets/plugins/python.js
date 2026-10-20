// Python plugin: runnable Python snippets and auto-checked coding exercises, via Pyodide (CPython compiled to WebAssembly).
// Load after assets/lp.js. Style: plugins/python.css.
//
// Snippet (unscored):  <div class="lp-py" [data-packages="numpy"] [data-timeout="10"]><pre class="code">print(sum(range(10)))</pre></div>
//   The learner gets an editable code box, Run (also Ctrl/Cmd+Enter), Reset (back to the original code) and an output panel.
// Exercise (scored):   <div class="quiz" data-type="py" data-id="…" [data-packages="numpy"] [data-timeout="10"]>
//                        <p class="prompt">…</p>
//                        <pre class="code">def mean(xs):
//     ...</pre>
//                        <script type="text/python" class="check">assert abs(mean([1, 2, 3]) - 2) < 1e-9, "mean([1, 2, 3]) should be 2"</script>
//                        <div class="explain" hidden>…</div></div>
//   Check runs the learner's code, then the check code in the same namespace. Right = no exception. A failed check shows
//   only the exception's message (the assert message), never the check source. First Check is the scored attempt.
//   Not scored: syntax errors, timeouts, and Python failing to load. Run (without checking) is never scored.
// Markup: the starter code is the <pre>'s textContent, so write < as &lt; and & as &amp; inside <pre class="code">.
//   The check is a <script type="text/python">: raw text, so write < and & as is (only "</script" is not allowed).
//   Both are dedented, so indent them with the surrounding HTML if you like.
// Runtime: Pyodide (pinned below) from jsDelivr, loaded on the first Run/Check in a Web Worker shared by the page
//   (~10 MB the first time, then from the browser cache; numpy adds ~3 MB). Every run gets a fresh namespace, so widgets
//   don't share variables. A run longer than data-timeout seconds (default 10) is stopped by restarting the worker,
//   so infinite loops don't freeze the tab. Text output only (stdout/stderr); input() raises EOFError; no plots.
// Pure helpers are exported for Node (node scripts/test_python.js): dedent, errorMessage, indentFor, packages.
(function () {
  "use strict";
  var VERSION = "314.0.7";
  var INDEX = "https://cdn.jsdelivr.net/pyodide/v" + VERSION + "/full/";

  // ---------- pure helpers ----------
  // Remove leading/trailing blank lines and the common leading whitespace; tabs become 4 spaces.
  function dedent(s) {
    var lines = String(s || "").replace(/\r\n?/g, "\n").replace(/\t/g, "    ").split("\n");
    while (lines.length && !lines[0].trim()) lines.shift();
    while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
    var pad = Infinity;
    lines.forEach(function (l) { if (l.trim()) pad = Math.min(pad, /^ */.exec(l)[0].length); });
    if (!isFinite(pad)) pad = 0;
    return lines.map(function (l) { return l.slice(pad).replace(/\s+$/, ""); }).join("\n");
  }

  // The message of the last exception in a Python traceback (or format_exception_only) string.
  //   "…\nAssertionError: mean([1]) should be 1\n" -> "mean([1]) should be 1"   (assert messages are shown bare)
  //   "AssertionError\n" -> ""   (no message: the caller falls back to the hint)
  //   "…\nNameError: name 'f' is not defined" -> "NameError: name 'f' is not defined"
  function errorMessage(tb) {
    var lines = String(tb || "").replace(/\s+$/, "").split("\n"), i = lines.length - 1;
    // the exception line is the last line that starts at column 0 with Name or Name: (dotted names allowed)
    while (i >= 0 && !/^[A-Za-z_][\w.]*(:|$)/.test(lines[i])) i--;
    if (i < 0) return lines[lines.length - 1] ? lines[lines.length - 1].trim() : "";
    var msg = lines.slice(i).join("\n").trim(), m = /^(?:builtins\.)?AssertionError(?::\s*([\s\S]*))?$/.exec(msg);
    return m ? (m[1] || "").trim() : msg;
  }

  // Indentation for the line after `line` when Enter is pressed: keep its indent, add 4 after a trailing ":".
  function indentFor(line) {
    var ind = /^ */.exec(line)[0];
    return /:\s*(#.*)?$/.test(line) ? ind + "    " : ind;
  }

  // "numpy, scipy" or "numpy scipy" -> ["numpy", "scipy"]
  function packages(s) { return String(s || "").split(/[\s,|]+/).filter(Boolean); }

  var helpers = { VERSION: VERSION, INDEX: INDEX, dedent: dedent, errorMessage: errorMessage, indentFor: indentFor, packages: packages };
  if (typeof module !== "undefined" && module.exports) { module.exports = helpers; return; }
  window.LPPython = helpers;
  if (!window.LP || !LP.register) return;

  // ---------- Python side of the runner (lives in the worker) ----------
  var RUNNER = [
    "import sys, io, json, traceback, linecache",
    "class _LPOut(io.TextIOBase):",
    "    def __init__(self, chunks, tag): self.chunks, self.tag = chunks, tag",
    "    def writable(self): return True",
    "    def write(self, s):",
    "        if self.chunks and self.chunks[-1][0] == self.tag: self.chunks[-1][1] += s",
    "        else: self.chunks.append([self.tag, s])",
    "        return len(s)",
    "def _lp_run(code, check):",
    "    chunks, res, ns = [], {'phase': 'ok', 'error': None}, {'__name__': '__main__'}",
    "    old = sys.stdout, sys.stderr",
    "    sys.stdout, sys.stderr = _LPOut(chunks, 'out'), _LPOut(chunks, 'err')",
    "    try:",
    "        linecache.cache['<your code>'] = (len(code), None, code.splitlines(True), '<your code>')",
    "        try:",
    "            compiled = compile(code, '<your code>', 'exec')",
    "        except SyntaxError as e:",
    "            res['phase'] = 'syntax'",
    "            sys.stderr.write(''.join(traceback.format_exception_only(type(e), e)))",
    "            compiled = None",
    "        if compiled is not None:",
    "            try:",
    "                exec(compiled, ns)",
    "            except BaseException as e:",
    "                res['phase'] = 'code'",
    "                sys.stderr.write(''.join(traceback.format_exception(type(e), e, e.__traceback__.tb_next)))",
    "                res['error'] = ''.join(traceback.format_exception_only(type(e), e))",
    "        if check is not None and res['phase'] == 'ok':",
    "            try:",
    "                exec(compile(check, '<check>', 'exec'), ns)",
    "            except BaseException as e:",
    "                res['phase'] = 'check'",
    "                res['error'] = ''.join(traceback.format_exception_only(type(e), e))",
    "    finally:",
    "        sys.stdout.flush(); sys.stdout, sys.stderr = old",
    "    res['out'] = chunks",
    "    return json.dumps(res)"
  ].join("\n");

  // Runs inside a module worker (serialised with toString, so it must not use anything from this closure).
  // Pyodide no longer supports classic workers, so it is imported as an ES module.
  function workerMain(cfg) {
    var py = null;
    self.onmessage = function (e) {
      var m = e.data;
      function reply(x) { x.id = m.id; self.postMessage(x); }
      Promise.resolve().then(function () {
        if (m.op === "init") {
          return import(cfg.index + "pyodide.mjs").then(function (mod) { return mod.loadPyodide({ indexURL: cfg.index }); }).then(function (p) {
            py = p;
            py.setStdin({ stdin: function () { return null; } });   // input() -> EOFError instead of a prompt
            py.runPython(cfg.runner);
            return {};
          });
        }
        if (m.op === "packages") return py.loadPackage(m.packages, { messageCallback: function () {} }).then(function () { return {}; });
        if (m.op === "run") {
          var fn = py.globals.get("_lp_run");
          try { return { result: JSON.parse(fn(m.code, m.check == null ? undefined : m.check)) }; } finally { fn.destroy(); }
        }
        throw new Error("unknown op " + m.op);
      }).then(reply, function (err) { reply({ error: String((err && err.message) || err) }); });
    };
  }

  // ---------- page side: one worker per page, one job at a time ----------
  var worker = null, ready = null, loaded = {}, seq = 0, pending = {}, queue = Promise.resolve();
  function spawn() {
    var src = "(" + workerMain.toString() + ")(" + JSON.stringify({ index: INDEX, runner: RUNNER }) + ");";
    worker = new Worker(URL.createObjectURL(new Blob([src], { type: "text/javascript" })), { type: "module" });
    worker.onmessage = function (e) { var p = pending[e.data.id]; if (p) { delete pending[e.data.id]; p(e.data); } };
    worker.onerror = function (e) { e.preventDefault(); fail("Python worker error: " + (e.message || "unknown")); };
  }
  function fail(msg) { Object.keys(pending).forEach(function (k) { pending[k]({ error: msg }); delete pending[k]; }); }
  function kill() { if (worker) worker.terminate(); worker = null; ready = null; loaded = {}; fail("stopped"); }
  // Send one message; resolve with the reply, or with {timeout: true} after `secs` seconds (the worker is then restarted).
  function send(msg, secs) {
    if (!worker) spawn();
    return new Promise(function (resolve) {
      var id = ++seq, timer = setTimeout(function () { delete pending[id]; kill(); resolve({ timeout: true }); }, secs * 1000);
      pending[id] = function (r) { clearTimeout(timer); resolve(r); };
      msg.id = id; worker.postMessage(msg);
    });
  }
  function boot(status) {
    if (!ready) {
      status(worker === null && seq === 0 ? "Loading Python… (first time ~10 MB)" : "Starting Python…");
      ready = send({ op: "init" }, 120).then(function (r) {
        if (r.timeout || r.error) { ready = null; if (worker) { worker.terminate(); worker = null; } throw new Error(r.timeout ? "timed out" : r.error); }
      });
    }
    return ready;
  }
  function need(pkgs, status) {
    var missing = pkgs.filter(function (p) { return !loaded[p]; });
    if (!missing.length) return Promise.resolve();
    status("Loading " + missing.join(", ") + "…");
    return send({ op: "packages", packages: missing }, 120).then(function (r) {
      if (r.timeout || r.error) throw new Error("couldn't load " + missing.join(", ") + (r.error ? ": " + r.error : ""));
      missing.forEach(function (p) { loaded[p] = true; });
    });
  }
  // -> {result} | {timeout} | {loadError}
  function run(code, check, pkgs, secs, status) {
    var job = queue.then(function () {
      return boot(status).then(function () { return need(pkgs, status); }).then(function () {
        status("Running…");
        return send({ op: "run", code: code, check: check }, secs);
      }).catch(function (e) { return { loadError: e.message }; });
    });
    queue = job.then(function () {}, function () {});
    return job;
  }

  // ---------- editor ----------
  var U = LP.util;
  function editor(host, opts) {
    var pre = host.querySelector(":scope > pre.code");
    if (!pre) throw new Error("needs a <pre class=\"code\"> with the starter code");
    var original = dedent(pre.textContent);
    pre.hidden = true;
    var wrap = U.el("div", "py-editor"), ta = U.el("textarea", "py-code"), bar = U.el("div", "py-bar");
    ta.value = original; ta.spellcheck = false; ta.autocomplete = "off"; ta.setAttribute("autocapitalize", "off");
    ta.setAttribute("aria-label", "Python code (Tab indents; press Esc then Tab to leave the box)");
    function size() { ta.rows = Math.min(24, Math.max(3, ta.value.split("\n").length + 1)); }
    size();
    var escaped = false;
    ta.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { escaped = true; return; }
      var was = escaped; escaped = false;
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); opts.onRun(); return; }
      if (e.key === "Tab" && !e.shiftKey && !was && !e.ctrlKey && !e.altKey && !e.metaKey) { e.preventDefault(); insert("    "); return; }
      if (e.key === "Enter" && !e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
        var before = ta.value.slice(0, ta.selectionStart), line = before.slice(before.lastIndexOf("\n") + 1);
        e.preventDefault(); insert("\n" + indentFor(line));
      }
    });
    function insert(text) {
      var a = ta.selectionStart, b = ta.selectionEnd;
      ta.setRangeText(text, a, b, "end");
      ta.dispatchEvent(new Event("input", { bubbles: true }));
    }
    ta.addEventListener("input", size);
    var out = U.el("pre", "py-out"), status = U.el("span", "py-status");
    out.hidden = true; out.setAttribute("aria-live", "polite"); out.setAttribute("aria-label", "output");
    var runB = U.el("button", null, "Run"), resetB = U.el("button", null, "Reset");
    runB.addEventListener("click", function () { opts.onRun(); });
    resetB.addEventListener("click", function () { ta.value = original; size(); out.hidden = true; out.textContent = ""; status.textContent = ""; });
    bar.appendChild(runB);
    if (opts.checkButton) bar.appendChild(opts.checkButton);
    bar.appendChild(resetB); bar.appendChild(status);
    wrap.appendChild(ta); wrap.appendChild(bar); wrap.appendChild(out);
    return {
      node: wrap, ta: ta, status: function (s) { status.textContent = s || ""; },
      busy: function (on) { runB.disabled = on; if (opts.checkButton) opts.checkButton.disabled = on; },
      show: function (chunks, note) {
        out.textContent = "";
        var total = 0;
        (chunks || []).forEach(function (c) {
          var text = c[1];
          if (total > 20000) return;
          if (total + text.length > 20000) text = text.slice(0, 20000 - total) + "\n… (output cut off)";
          total += text.length;
          var span = U.el("span", c[0] === "err" ? "err" : null, text); out.appendChild(span);
        });
        if (note) out.appendChild(U.el("span", "note", (out.textContent && !/\n$/.test(out.textContent) ? "\n" : "") + note));
        if (!out.textContent) out.appendChild(U.el("span", "note", "(no output)"));
        out.hidden = false;
      }
    };
  }

  function settings(el) {
    var t = parseFloat(el.dataset.timeout);
    return { pkgs: packages(el.dataset.packages), secs: t > 0 ? t : 10 };
  }
  function timeoutNote(secs) { return "Stopped after " + secs + " s (an endless loop?). Python restarts on the next run."; }

  // Run a job with the editor's UI states; calls done(res) with the worker's reply.
  function go(ed, code, check, s, done) {
    ed.busy(true);
    var t0 = Date.now();
    run(code, check, s.pkgs, s.secs, ed.status).then(function (r) {
      ed.busy(false);
      if (r.loadError) { ed.status("Couldn't load Python (" + r.loadError + "). Check your connection and try again."); done(r); return; }
      if (r.timeout) { ed.status(""); ed.show([], timeoutNote(s.secs)); done(r); return; }
      if (r.error) { ed.status(""); ed.show([["err", r.error]]); done(r); return; }
      ed.status("Ran in " + ((Date.now() - t0) / 1000).toFixed(2) + " s");
      ed.show(r.result.out);
      done(r);
    });
  }

  function initSnippet(el) {
    var s = settings(el), ed;
    ed = editor(el, { onRun: function () { go(ed, ed.ta.value, null, s, function () {}); } });
    el.insertBefore(ed.node, el.querySelector(":scope > pre.code").nextSibling);
  }

  function initExercise(q, ctx) {
    var s = settings(q), checkEl = q.querySelector("script.check");
    if (!checkEl) throw new Error("needs a <script type=\"text/python\" class=\"check\">");
    var check = dedent(checkEl.textContent), checkB = U.el("button", null, "Check"), ed;
    ed = editor(q, { checkButton: checkB, onRun: function () { go(ed, ed.ta.value, null, s, function () {}); } });
    U.beforeExplain(q, ed.node);
    checkB.addEventListener("click", function () {
      var code = ed.ta.value;
      go(ed, code, check, s, function (r) {
        if (r.loadError) { ctx.feedback(false, "Python didn't load, so this wasn't checked (not counted)."); return; }
        if (r.timeout) { ctx.feedback(false, "Your code didn't finish within " + s.secs + " s, so it wasn't checked (not counted)."); return; }
        if (r.error) { ctx.feedback(false, "Something went wrong running Python (not counted): " + r.error); return; }
        var res = r.result;
        if (res.phase === "syntax") { ctx.feedback(false, "Python can't read your code yet (see the output). Not counted."); return; }
        if (res.phase === "ok") { ctx.result(true, code); ctx.feedback(true); return; }
        ctx.result(false, code);
        var msg = errorMessage(res.error);
        if (res.phase === "code") ctx.feedback(false, "Your code raised an error: " + msg + " (see the output).");
        else ctx.feedback(false, msg || q.dataset.hint || "A check failed. Look again and try once more.");
      });
    });
  }

  LP.register({ type: "py-snippet", selector: ".lp-py", scored: false, init: initSnippet });
  LP.register({ type: "py", init: initExercise });
})();
