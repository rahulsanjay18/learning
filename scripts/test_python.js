// Unit tests for the pure helpers in assets/plugins/python.js, and a check that every Python widget in the repo is well formed.
//   node scripts/test_python.js
// (Running the Python itself needs a browser: scripts/test_widgets.mjs drives the gallery's Python section.)
const fs = require("fs"), path = require("path");
const P = require("../assets/plugins/python.js");
let fails = 0;
const check = (name, cond, extra = "") => { console.log((cond ? "ok   " : "FAIL ") + name + (cond ? "" : "  " + JSON.stringify(extra))); if (!cond) fails++; };

// version pin
check("Pyodide pinned to an exact version", /^\d+\.\d+\.\d+$/.test(P.VERSION), P.VERSION);
check("Pyodide URL uses the pin", P.INDEX === `https://cdn.jsdelivr.net/pyodide/v${P.VERSION}/full/`, P.INDEX);

// dedent
check("dedent strips common indent and blank edges", P.dedent("\n    def f():\n        return 1\n\n") === "def f():\n    return 1");
check("dedent keeps relative indent with blank lines inside", P.dedent("  a\n\n    b\n  c") === "a\n\n  b\nc", P.dedent("  a\n\n    b\n  c"));
check("dedent ignores whitespace-only lines for the margin", P.dedent("    x = 1\n  \n    y = 2") === "x = 1\n\ny = 2", P.dedent("    x = 1\n  \n    y = 2"));
check("dedent turns tabs into 4 spaces", P.dedent("\tif x:\n\t\tpass") === "if x:\n    pass", P.dedent("\tif x:\n\t\tpass"));
check("dedent handles CRLF and trailing spaces", P.dedent("a  \r\nb\r\n") === "a\nb");
check("dedent of empty is empty", P.dedent("") === "" && P.dedent("  \n ") === "");
check("dedent leaves unindented code alone", P.dedent("print(1)\nprint(2)") === "print(1)\nprint(2)");

// errorMessage
const tb = 'Traceback (most recent call last):\n  File "<check>", line 3, in <module>\nAssertionError: mean([1, 2, 3]) should be 2\n';
check("assert message shown bare", P.errorMessage(tb) === "mean([1, 2, 3]) should be 2", P.errorMessage(tb));
check("bare AssertionError gives empty message", P.errorMessage("AssertionError\n") === "", P.errorMessage("AssertionError\n"));
check("other exceptions keep their name", P.errorMessage("Traceback (most recent call last):\n  File \"<check>\", line 1\nNameError: name 'f' is not defined") === "NameError: name 'f' is not defined");
check("multi-line messages kept", P.errorMessage("AssertionError: line one\nline two\n") === "line one\nline two", P.errorMessage("AssertionError: line one\nline two\n"));
check("dotted exception names", P.errorMessage("numpy.linalg.LinAlgError: Singular matrix") === "numpy.linalg.LinAlgError: Singular matrix");
check("syntax error summary", P.errorMessage('  File "<your code>", line 1\n    def f(:\n          ^\nSyntaxError: invalid syntax\n') === "SyntaxError: invalid syntax");
check("indented frame lines are skipped", P.errorMessage("Traceback (most recent call last):\n  File \"x\", line 1, in f\n    assert x\nAssertionError: boom") === "boom");
check("empty traceback", P.errorMessage("") === "" && P.errorMessage(null) === "");

// indentFor
check("Enter keeps indent", P.indentFor("    x = 1") === "    ");
check("Enter after colon indents", P.indentFor("def f(x):") === "    " && P.indentFor("    for i in r:  ") === "        ");
check("colon then comment still indents", P.indentFor("if x:  # note") === "    ");
check("colon inside a slice doesn't", P.indentFor("y = xs[1:]") === "");

// packages
check("packages split", JSON.stringify(P.packages("numpy, scipy pandas")) === '["numpy","scipy","pandas"]');
check("no packages", P.packages(undefined).length === 0 && P.packages("").length === 0);

// every Python widget in the repo is well formed
const root = path.resolve(__dirname, "..");
const files = [path.join(root, "assets/gallery.html")];
for (const t of fs.readdirSync(path.join(root, "topics"))) for (const d of ["lessons", "reference"]) {
  const dir = path.join(root, "topics", t, d);
  if (fs.existsSync(dir)) for (const f of fs.readdirSync(dir)) if (f.endsWith(".html")) files.push(path.join(dir, f));
}
const decode = (s) => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, "&");
let n = 0;
for (const f of files) {
  const html = fs.readFileSync(f, "utf8"), rel = path.relative(root, f);
  const re = /<div\b[^>]*>([\s\S]*?)(?=<div class="(?:lp-py|quiz)"|<h2|<ol class="sources"|<\/main>)/g;
  for (let m; (m = re.exec(html));) {
    if (!/class="lp-py"|class="quiz"[^>]*data-type="py"/.test(m[0].slice(0, m[0].indexOf(">")))) { re.lastIndex = m.index + 4; continue; }
    n++;
    const body = m[1], isQuiz = /data-type="py"/.test(m[0].slice(0, m[0].indexOf(">"))), id = (/data-id="([^"]*)"/.exec(m[0]) || [, "snippet"])[1];
    const pre = /<pre class="code">([\s\S]*?)<\/pre>/.exec(body);
    check(`${rel} ${id}: has starter code`, !!pre);
    if (pre) check(`${rel} ${id}: no raw < or & in the <pre> (escape as &lt; &amp;)`, !/<(?!\/?(?:b|i|em|strong|span)\b)|&(?![a-z]+;|#\d+;)/i.test(pre[1]), pre[1].slice(0, 80));
    if (pre) check(`${rel} ${id}: starter code survives dedent`, P.dedent(decode(pre[1])).length > 0);
    if (isQuiz) {
      const sc = /<script type="text\/python" class="check">([\s\S]*?)<\/script>/.exec(body);
      check(`${rel} ${id}: has a check script`, !!sc && /\bassert\b/.test(sc[1]));
    }
  }
}
check(`found Python widgets (${n})`, n >= 2);

console.log(fails ? `\n${fails} failure(s)` : "\nall passed");
process.exit(fails ? 1 : 0);
