// Math plugin: typeset math with KaTeX + "type a formula" quizzes checked for equivalence. Load after assets/lp.js.
// Typesetting: write \( inline \) or $$ display $$ (or \[ … \]) anywhere in the page. A single $ is NOT math (prices stay prices).
//   Elements with class "no-math" are skipped. KaTeX is vendored in assets/vendor/katex and loaded by this script.
// Quiz:  <div class="quiz" data-type="math" data-id="…" data-answer="2*x^2 + 2*x" [data-forbid="(|)"] [data-tolerance="0.001"]>
//          <p class="prompt">Expand \(2x(x+1)\).</p><div class="explain" hidden>…</div></div>
//   The learner types plain math (2x^2+2x, sqrt(2)/2, e^(-x), sin(t)^2, 1/(1+e^-x)) and sees it typeset live.
//   Right = equal to data-answer at random sample points (any algebraically equivalent form counts).
//   data-forbid: "|"-separated strings the answer may not contain (e.g. "(|)" forces an expanded form).
//   data-tolerance: absolute tolerance for purely numeric answers (default: tight relative tolerance).
// Engine exported for Node: const M = require("assets/plugins/math.js"); M.parse, M.evaluate, M.toTeX, M.equivalent.
(function () {
  "use strict";

  // ---------- expression engine ----------
  var FUNCS = { sin: Math.sin, cos: Math.cos, tan: Math.tan, asin: Math.asin, acos: Math.acos, atan: Math.atan,
    sinh: Math.sinh, cosh: Math.cosh, tanh: Math.tanh, exp: Math.exp, ln: Math.log, log: Math.log10, sqrt: Math.sqrt, abs: Math.abs };
  var CONSTS = { pi: Math.PI, e: Math.E };
  var GREEK = ["alpha", "beta", "gamma", "delta", "epsilon", "theta", "lambda", "mu", "sigma", "tau", "phi", "omega", "rho", "nu", "kappa"];
  var NAMES = Object.keys(FUNCS).concat(Object.keys(CONSTS), GREEK).sort(function (a, b) { return b.length - a.length; });

  function tokenize(src) {
    var s = String(src).replace(/\*\*/g, "^").replace(/[×·⋅]/g, "*").replace(/÷/g, "/").replace(/[−–]/g, "-").replace(/π/g, "pi").replace(/√/g, "sqrt");
    var out = [], i = 0;
    while (i < s.length) {
      var ch = s[i];
      if (/\s/.test(ch)) { i++; continue; }
      var num = /^(\d+\.?\d*|\.\d+)(e[-+]?\d+)?/i.exec(s.slice(i));
      if (num && !/^e[a-z]/i.test(s.slice(i + num[1].length))) { out.push({ k: "num", v: parseFloat(num[0]) }); i += num[0].length; continue; }
      if (/[a-z_]/i.test(ch)) {
        var word = /^[a-z_]+/i.exec(s.slice(i))[0];
        // split a run of letters into known names, else single-letter variables: "xy" -> x y, "2pix" -> pi x
        var j = 0;
        while (j < word.length) {
          var rest = word.slice(j).toLowerCase(), hit = null;
          for (var n = 0; n < NAMES.length; n++) if (rest.indexOf(NAMES[n]) === 0) { hit = NAMES[n]; break; }
          if (hit) { out.push({ k: FUNCS[hit] ? "fn" : "id", v: hit }); j += hit.length; }
          else { out.push({ k: "id", v: word[j] }); j++; }
        }
        i += word.length; continue;
      }
      if ("+-*/^(),".indexOf(ch) >= 0) { out.push({ k: ch }); i++; continue; }
      throw new Error("Unexpected “" + ch + "”");
    }
    return out;
  }

  // Grammar: sum := term (('+'|'-') term)* ; term := unary (('*'|'/'|implicit) unary)* ; unary := '-' unary | power ;
  //          power := atom ('^' unary)?   (right-assoc, and -x^2 = -(x^2)) ; atom := num | id | fn atomOrParen | '(' sum ')'
  function parse(src) {
    var t = tokenize(src), p = 0;
    if (!t.length) throw new Error("Empty");
    function peek() { return t[p] || { k: "end" }; }
    function eat(k) { if (peek().k !== k) throw new Error(k === ")" ? "Missing “)”" : "Expected “" + k + "”"); return t[p++]; }
    function startsAtom(tok) { return tok.k === "num" || tok.k === "id" || tok.k === "fn" || tok.k === "("; }
    function sum() {
      var a = term();
      while (peek().k === "+" || peek().k === "-") { var op = t[p++].k; a = { t: "op", op: op, a: a, b: term() }; }
      return a;
    }
    function term() {
      var a = unary();
      for (;;) {
        var k = peek().k;
        if (k === "*" || k === "/") { p++; a = { t: "op", op: k, a: a, b: unary() }; }
        else if (startsAtom(peek())) a = { t: "op", op: "*", a: a, b: power(), implicit: true };
        else return a;
      }
    }
    function unary() {
      if (peek().k === "-") { p++; return { t: "neg", a: unary() }; }
      if (peek().k === "+") { p++; return unary(); }
      return power();
    }
    function power() {
      var a = atom();
      if (peek().k === "^") { p++; return { t: "op", op: "^", a: a, b: unary() }; }
      return a;
    }
    function atom() {
      var tok = peek();
      if (tok.k === "num") { p++; return { t: "num", v: tok.v }; }
      if (tok.k === "id") { p++; return CONSTS[tok.v] !== undefined ? { t: "const", n: tok.v } : { t: "var", n: tok.v }; }
      if (tok.k === "fn") {
        p++;
        var arg;
        if (peek().k === "(") { p++; arg = sum(); eat(")"); }
        else if (peek().k === "^") {           // sin^2(x) = (sin x)^2
          p++; var ex = unary(); var inner = atom();
          return { t: "op", op: "^", a: { t: "fn", f: tok.v, a: inner }, b: ex };
        } else arg = power();                   // sin x
        return { t: "fn", f: tok.v, a: arg };
      }
      if (tok.k === "(") { p++; var e = sum(); eat(")"); return { t: "group", a: e }; }
      throw new Error(tok.k === "end" ? "Unfinished expression" : "Unexpected “" + tok.k + "”");
    }
    var ast = sum();
    if (p < t.length) throw new Error("Unexpected “" + (t[p].v || t[p].k) + "”");
    return ast;
  }

  function evaluate(n, env) {
    switch (n.t) {
      case "num": return n.v;
      case "const": return CONSTS[n.n];
      case "var": return env && n.n in env ? env[n.n] : NaN;
      case "group": return evaluate(n.a, env);
      case "neg": return -evaluate(n.a, env);
      case "fn": return FUNCS[n.f](evaluate(n.a, env));
      case "op":
        var a = evaluate(n.a, env), b = evaluate(n.b, env);
        return n.op === "+" ? a + b : n.op === "-" ? a - b : n.op === "*" ? a * b : n.op === "/" ? a / b : Math.pow(a, b);
    }
    return NaN;
  }

  function vars(n, acc) {
    acc = acc || {};
    if (n.t === "var") acc[n.n] = 1;
    ["a", "b"].forEach(function (k) { if (n[k]) vars(n[k], acc); });
    return acc;
  }

  var TEXFN = { asin: "\\arcsin", acos: "\\arccos", atan: "\\arctan", ln: "\\ln", log: "\\log", exp: "\\exp", abs: null, sqrt: null };
  function toTeX(n) {
    switch (n.t) {
      case "num": return String(n.v);
      case "const": return n.n === "pi" ? "\\pi" : "e";
      case "var": return GREEK.indexOf(n.n) >= 0 ? "\\" + n.n : n.n;
      case "group": return n.a.t === "op" && n.a.op === "/" ? toTeX(n.a) : "\\left(" + toTeX(n.a) + "\\right)";
      case "neg": return "-" + wrap(n.a, 2);
      case "fn":
        if (n.f === "sqrt") return "\\sqrt{" + toTeX(strip(n.a)) + "}";
        if (n.f === "abs") return "\\left|" + toTeX(strip(n.a)) + "\\right|";
        return (TEXFN[n.f] || "\\" + n.f) + "\\left(" + toTeX(strip(n.a)) + "\\right)";
      case "op":
        if (n.op === "/") return "\\frac{" + toTeX(strip(n.a)) + "}{" + toTeX(strip(n.b)) + "}";
        if (n.op === "^") return wrap(n.a, 4) + "^{" + toTeX(strip(n.b)) + "}";
        if (n.op === "*") {
          var l = wrap(n.a, 2), r = wrap(n.b, 2);
          var needDot = (n.b.t === "num") || (n.b.t === "neg") || (n.b.t === "op" && n.b.op === "^" && n.b.a.t === "num");
          return l + (needDot ? " \\cdot " : " ") + r;
        }
        return toTeX(n.a) + " " + n.op + " " + wrap(n.b, n.op === "-" ? 2 : 1);
    }
    return "";
  }
  function strip(n) { return n.t === "group" ? n.a : n; }
  function prec(n) {
    if (n.t === "op") return n.op === "+" || n.op === "-" ? 1 : n.op === "^" ? 4 : n.op === "/" ? 5 : 2;
    if (n.t === "neg") return 1.5;
    return 5;
  }
  function wrap(n, min) { return n.t !== "group" && prec(n) < min ? "\\left(" + toTeX(n) + "\\right)" : toTeX(n); }

  // Equal at random sample points? Returns {ok, reason}.
  function equivalent(given, expected, opts) {
    opts = opts || {};
    var g = typeof given === "string" ? parse(given) : given, x = typeof expected === "string" ? parse(expected) : expected;
    var names = Object.keys(Object.assign(vars(g), vars(x)));
    var extra = Object.keys(vars(g)).filter(function (v) { return !(v in vars(x)); });
    var wrong = extra.length ? { ok: false, reason: "The answer shouldn't depend on " + extra.join(", ") + "." } : { ok: false };
    if (!names.length) {
      var a = evaluate(g), b = evaluate(x);
      var tol = opts.tolerance != null ? opts.tolerance : 1e-9 * Math.max(1, Math.abs(b));
      return { ok: isFinite(a) && Math.abs(a - b) <= tol };
    }
    var rnd = opts.random || Math.random, agree = 0, tries = 0;
    var ranges = [[0.3, 3], [-3, -0.3], [3, 9]];
    while (agree < 8 && tries < 60) {
      tries++;
      var env = {}, range = ranges[tries % 3 === 0 ? 1 : tries % 5 === 0 ? 2 : 0];
      names.forEach(function (v) { env[v] = range[0] + rnd() * (range[1] - range[0]); });
      var ea = evaluate(g, env), eb = evaluate(x, env);
      if (!isFinite(eb) || !isFinite(ea)) continue;   // outside either side's domain (e.g. ln of a negative)
      if (Math.abs(ea - eb) > 1e-7 * Math.max(1, Math.abs(ea), Math.abs(eb))) return wrong;
      agree++;
    }
    return { ok: agree >= 4 };
  }

  var engine = { parse: parse, evaluate: evaluate, toTeX: toTeX, equivalent: equivalent, vars: function (n) { return Object.keys(vars(n)); } };
  if (typeof module !== "undefined" && module.exports) { module.exports = engine; return; }
  window.LPMath = engine;

  // ---------- KaTeX loading + typesetting ----------
  var base = new URL("../vendor/katex/", document.currentScript ? document.currentScript.src : location.href).href;
  var katexReady = null;
  function loadKatex() {
    if (katexReady) return katexReady;
    var css = document.createElement("link");
    css.rel = "stylesheet"; css.href = base + "katex.min.css";
    document.head.appendChild(css);
    function script(src) {
      return new Promise(function (res, rej) { var s = document.createElement("script"); s.src = src; s.onload = res; s.onerror = rej; document.head.appendChild(s); });
    }
    katexReady = script(base + "katex.min.js").then(function () { return script(base + "contrib/auto-render.min.js"); })
      .then(function () { return window.katex; }).catch(function () { return null; });
    return katexReady;
  }
  function typeset(root) {
    if (!window.renderMathInElement) return;
    window.renderMathInElement(root, {
      delimiters: [{ left: "$$", right: "$$", display: true }, { left: "\\[", right: "\\]", display: true }, { left: "\\(", right: "\\)", display: false }],
      ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "option", "input"],
      ignoredClasses: ["no-math", "math-preview"], throwOnError: false
    });
  }
  LPMath.typeset = function (root) { return loadKatex().then(function () { typeset(root || document.body); }); };
  LPMath.ready = loadKatex;

  // ---------- quiz widget ----------
  function initMath(q, ctx) {
    var U = LP.util, answer = q.dataset.answer, forbid = U.split(q.dataset.forbid);
    var expected;
    try { expected = parse(answer); } catch (e) { throw new Error("bad data-answer “" + answer + "”: " + e.message); }
    var box = U.el("div", "choices math-row"), input = U.el("input", "math-input"), b = U.el("button", null, "Check");
    input.type = "text"; input.autocomplete = "off"; input.spellcheck = false;
    input.setAttribute("aria-label", "your answer (plain math, e.g. 2x^2 + 3)");
    input.placeholder = q.dataset.placeholder || "e.g. 2x^2 + 3";
    var preview = U.el("div", "math-preview"); preview.setAttribute("aria-live", "polite");
    box.appendChild(input); box.appendChild(b);
    U.beforeExplain(q, box); U.beforeExplain(q, preview);

    function show() {
      var v = input.value.trim();
      if (!v) { preview.textContent = ""; preview.className = "math-preview"; return; }
      try {
        var tex = toTeX(parse(v));
        loadKatex().then(function (k) {
          if (k) k.render(tex, preview, { throwOnError: false }); else preview.textContent = v;
          preview.className = "math-preview";
        });
      } catch (e) { preview.textContent = e.message; preview.className = "math-preview err"; }
    }
    function check() {
      var v = input.value.trim();
      if (!v) return;
      var res;
      try { res = equivalent(v, expected, { tolerance: q.dataset.tolerance ? parseFloat(q.dataset.tolerance) : null }); }
      catch (e) { ctx.feedback(false, "I can't read that yet: " + e.message); return; }   // unreadable input doesn't count
      var banned = forbid.filter(function (f) { return v.indexOf(f) >= 0; });
      if (res.ok && banned.length) { ctx.feedback(false, "Equal, but not in the asked-for form: don't use " + banned.map(function (f) { return "“" + f + "”"; }).join(" or ") + "."); return; }
      ctx.result(res.ok, v);
      input.classList.remove("ok", "no"); input.classList.add(res.ok ? "ok" : "no");
      if (res.ok) { input.disabled = true; b.disabled = true; }
      ctx.feedback(res.ok, res.ok ? null : res.reason || q.dataset.hint);
      if (res.ok) LPMath.typeset(q);
    }
    input.addEventListener("input", show);
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") check(); });
    b.addEventListener("click", check);
  }

  LP.register({ type: "math", init: initMath });
  function start() { loadKatex().then(function () { typeset(document.querySelector("main") || document.body); }); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { setTimeout(start, 0); }); else setTimeout(start, 0);
})();
