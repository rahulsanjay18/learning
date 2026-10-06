#!/usr/bin/env python3
"""Render a compact Markdown lesson (topics/<t>/lessons/NNNN-slug.md) to the full HTML page next to it.

    python3 scripts/render_lesson.py topics/statistics/lessons/0005-likelihood-ratios.md [--course S150] [--no-index]

Why: the HTML shell, crumbs, quiz wrappers, plugin <link>/<script> tags and sources list are the same every time, so the
author writes only content. Plugins are detected from what the page uses. Also: appends the lesson to index.html (unless
--no-index) and, with --course, records it in the major's curriculum.json (adds the stem, drops the plan entry it fulfils).
Syntax reference: assets/README.md "Writing lessons in Markdown". Standard library only.
"""
import html, json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = "../../../assets/"

# ---------- inline Markdown ----------
INLINE_TAGS = r"</?(?:em|strong|a|sup|sub|br|span|code|abbr|kbd|small|cite|mark|b|i|u|s|q|dfn|time|wbr)(?:\s[^<>]*)?/?>"


def inline(text):
    """Escape &, <, > (so math can use them freely), keep a small set of inline HTML tags, then apply **, *, `, [](), [[ ]] stays."""
    keep = []

    def stash(m):
        keep.append(m if isinstance(m, str) else m.group(0))
        return f"\x00{len(keep) - 1}\x00"
    text = re.sub(r"`([^`]+)`", lambda m: stash("<code>" + html.escape(m.group(1), quote=False) + "</code>"), text)
    text = re.sub(INLINE_TAGS, stash, text)
    text = re.sub(r"&(#?\w+);", lambda m: stash(m.group(0)), text)       # existing entities stay
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]\[]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*\\])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], text)


# ---------- block Markdown ----------
def blocks(lines):
    """Markdown body lines -> HTML. Handles headings, lists (with [x]/[ ] kept raw for quizzes), blockquotes, raw HTML, paragraphs."""
    out, i, sources_next = [], 0, False
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^(#{2,4})\s+(.*)", line)
        if m:
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            sources_next = m.group(2).strip().lower() == "sources"
            i += 1
            continue
        if line.lstrip().startswith("<"):                       # raw HTML block: until a blank line
            while i < len(lines) and lines[i].strip():
                out.append(lines[i]); i += 1
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.", line)) or sources_next
            items = []
            while i < len(lines) and (re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]) or (lines[i].startswith("  ") and lines[i].strip() and items)):
                if re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                    items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i]))
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            tag = "ol" if ordered else "ul"
            cls = ' class="sources"' if sources_next else ""
            out.append(f"<{tag}{cls}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            sources_next = False
            continue
        if line.startswith(">"):
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i][1:].strip()); i += 1
            out.append("<blockquote>" + blocks(q) + "</blockquote>")
            continue
        if line.strip().startswith("$$"):                       # display math: keep verbatim (escaped) until the closing $$
            buf = [line]
            if not (line.strip().endswith("$$") and len(line.strip()) > 2):
                i += 1
                while i < len(lines):
                    buf.append(lines[i])
                    if lines[i].strip().endswith("$$"): break
                    i += 1
            i += 1
            out.append("<p>" + html.escape("\n".join(buf), quote=False) + "</p>")
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{2,4}\s|\s*[-*]\s|\s*\d+\.\s|>|<|\$\$)", lines[i]):
            para.append(lines[i].strip()); i += 1
        if not para:          # a line that looked special but wasn't consumed above
            para.append(lines[i].strip()); i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


# ---------- ::: widget blocks ----------
QUIZ_TYPES = {"choice", "number", "exact", "cloze", "order", "categorize", "recall", "checklist", "free", "card", "math",
              "plot-set", "chess-move", "go-move", "timeline-place", "map-locate", "py", "game-move", "xiangqi-move",
              "shogi-move", "estimate", "find-error", "highlight"}
DIV_CLASSES = {"board": "board-wrap", "go": "go-board", "plot": "lp-plot", "timeline": "lp-timeline", "map": "lp-map",
               "game": "lp-game", "xiangqi": "xq-board", "shogi": "shogi-board", "python": "lp-py", "video": "lp-video",
               "worked": "lp-worked", "deck": "lp-deck", "reading": "reading", "callout": "callout", "sim": "lp-sim"}
PLUGIN_OF = {"chess-move": ["chess"], "board-wrap": ["chess"], "go-move": ["go"], "go-board": ["go"], "math": ["math"],
             "plot-set": ["math", "plot"], "lp-plot": ["math", "plot"], "timeline-place": ["timeline"], "lp-timeline": ["timeline"],
             "map-locate": ["map"], "lp-map": ["map"], "py": ["python"], "lp-py": ["python"], "game-move": ["games"],
             "lp-game": ["games"], "xiangqi-move": ["xiangqi"], "xq-board": ["xiangqi"], "shogi-move": ["shogi"],
             "shogi-board": ["shogi"], "lp-sim": ["sim"]}
PLUGIN_ORDER = ["math", "plot", "chess", "go", "timeline", "map", "python", "games", "xiangqi", "shogi", "sim", "pixels"]


def parse_attrs(s):
    """'id key=value key="a b" flag' -> (first bare word, {key: value})"""
    toks = re.findall(r'(\w[\w-]*)=("([^"]*)"|\'([^\']*)\'|\S+)|("([^"]*)"|\S+)', s)
    first, attrs = None, {}
    for k, v, dq, sq, bare, bq in toks:
        if k:
            attrs[k] = dq if v.startswith('"') else sq if v.startswith("'") else v
        elif first is None:
            first = bq if bare.startswith('"') else bare
        else:
            attrs[bare] = "true"
    return first, attrs


def esc(v):
    return html.escape(str(v), quote=True)


def list_items(lines):
    return [re.sub(r"^\s*([-*]|\d+\.)\s+", "", l).strip() for l in lines if re.match(r"^\s*([-*]|\d+\.)\s+", l)]


def render_widget(kind, header, body, used):
    """One ::: block. Sections after the prompt: '--- explain', '--- rubric', '--- hint', '--- code', '--- check', '--- step'."""
    ident, attrs = parse_attrs(header)
    cls = DIV_CLASSES.get(kind, kind)
    if kind not in QUIZ_TYPES and cls not in ("lp-py", "lp-worked"):     # containers: the body is ordinary content (may nest blocks)
        used.update(PLUGIN_OF.get(cls, []))
        attr_s = (f' id="{esc(ident)}"' if ident else "") + "".join(f' data-{k}="{esc(v)}"' for k, v in attrs.items())
        return f'<div class="{cls}"{attr_s}>' + (render_body(body, used) if any(l.strip() for l in body) else "") + "</div>"
    sections = [["prompt", []]]
    for l in body:
        m = re.match(r"^---\s*(\w+)\s*$", l)
        if m:
            sections.append([m.group(1), []])
        else:
            sections[-1][1].append(l)
    sec = {}
    for name, ls in sections:
        sec.setdefault(name, []).append(ls)
    prompt = sec.get("prompt", [[]])[0]

    if kind in QUIZ_TYPES:
        used.update(PLUGIN_OF.get(kind, []))
        data = {"type": kind}
        if ident: data["id"] = ident
        # list shorthands
        items = list_items(prompt)
        text_lines = [l for l in prompt if not re.match(r"^\s*([-*]|\d+\.)\s+", l)]
        if kind == "choice" and items and "options" not in attrs:
            opts = [re.sub(r"^\[[ xX]\]\s*", "", x) for x in items]
            right = [o for x, o in zip(items, opts) if re.match(r"^\[[xX]\]", x)]
            if len(right) != 1: raise ValueError(f"choice {ident}: mark exactly one option with [x]")
            data["options"], data["answer"] = "|".join(opts), right[0]
            prompt = text_lines
        elif kind == "order" and items and "items" not in attrs:
            data["items"] = "|".join(items); prompt = text_lines
        elif kind == "categorize" and items and "items" not in attrs:
            pairs = [x.rsplit(">", 1) for x in items]
            if any(len(p) != 2 for p in pairs): raise ValueError(f"categorize {ident}: write items as '- item > Bucket'")
            buckets = attrs.pop("buckets", None) or "|".join(dict.fromkeys(p[1].strip() for p in pairs))
            data["buckets"], data["items"] = buckets, "|".join(f"{p[0].strip()}>{p[1].strip()}" for p in pairs)
            prompt = text_lines
        elif kind == "find-error" and items:
            # steps: '- [x] wrong step' marks the error
            data["steps"] = "|".join(re.sub(r"^\[[ xX]\]\s*", "", x) for x in items)
            data["answer"] = str([i for i, x in enumerate(items) if re.match(r"^\[[xX]\]", x)][0] + 1) if any(re.match(r"^\[[xX]\]", x) for x in items) else ""
            prompt = text_lines
        if "hint" in sec: data["hint"] = " ".join(" ".join(x) for x in sec["hint"]).strip()
        for k, v in attrs.items(): data[k] = v
        attr_s = "".join(f' data-{k}="{esc(v)}"' for k, v in data.items())
        inner = []
        if any(l.strip() for l in prompt):
            p = blocks(prompt)
            inner.append(re.sub(r"^<p>", '<p class="prompt">', p, count=1) if p.startswith("<p>") else p)
        if kind == "py" or "code" in sec:
            code = "\n".join(sec.get("code", [[]])[0]).strip("\n")
            inner.append(f'<pre class="code">{html.escape(code, quote=False)}</pre>')
        if "check" in sec:
            inner.append('<script type="text/python" class="check">\n' + "\n".join(sec["check"][0]).strip("\n") + "\n</script>")
        if "rubric" in sec: inner.append('<div class="rubric">' + blocks(sec["rubric"][0]) + "</div>")
        if "explain" in sec: inner.append('<div class="explain" hidden>' + blocks(sec["explain"][0]) + "</div>")
        return f'<div class="quiz"{attr_s}>\n' + "\n".join(inner) + "\n</div>"

    cls = DIV_CLASSES.get(kind, kind)
    used.update(PLUGIN_OF.get(cls, []))
    attr_s = (f' id="{esc(ident)}"' if ident else "") + "".join(f' data-{k}="{esc(v)}"' for k, v in attrs.items())
    if cls == "lp-py":
        code = "\n".join(sec.get("code", [prompt])[0]).strip("\n")
        return f'<div class="lp-py"{attr_s}><pre class="code">{html.escape(code, quote=False)}</pre></div>'
    if cls == "lp-worked":
        steps = [prompt] + sec.get("step", [])
        return f'<div class="lp-worked"{attr_s}>' + "".join(f'<div class="step">{blocks(s)}</div>' for s in steps if any(x.strip() for x in s)) + "</div>"
    return f'<div class="{cls}"{attr_s}>' + (render_body(prompt, used) if any(l.strip() for l in prompt) else "") + "</div>"


def render_body(lines, used):
    out, i, buf = [], 0, []
    while i < len(lines):
        m = re.match(r"^(:{3,})\s*([\w-]+)\s*(.*)$", lines[i])
        if not m:
            buf.append(lines[i]); i += 1
            continue
        if buf: out.append(blocks(buf)); buf = []
        fence, kind, header, body, depth = m.group(1), m.group(2), m.group(3), [], 0
        i += 1
        while i < len(lines):
            if re.match(rf"^{fence}\s*$", lines[i]) and depth == 0:
                break
            if re.match(rf"^{fence}\s*[\w-]+", lines[i]): depth += 1
            elif re.match(rf"^{fence}\s*$", lines[i]): depth -= 1
            body.append(lines[i]); i += 1
        else:
            raise ValueError(f"unclosed '{fence} {kind}' block")
        i += 1
        out.append(render_widget(kind, header, body, used))
    if buf: out.append(blocks(buf))
    return "\n".join(out)


def front_matter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m: raise ValueError("missing front matter (--- title: … ---)")
    meta = {}
    for l in m.group(1).splitlines():
        if ":" in l:
            k, v = l.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, text[m.end():]


def render(md_path):
    md_path = pathlib.Path(md_path).resolve()
    topic, stem = md_path.parts[-3], md_path.stem
    meta, body = front_matter(md_path.read_text(encoding="utf-8"))
    if "title" not in meta: raise ValueError("front matter needs title:")
    used = set()
    body_html = render_body(body.splitlines(), used)
    if re.search(r"\\\(|\$\$|\\\[", body): used.add("math")
    if "plot" in used: used.add("math")
    for p in meta.get("plugins", "").split(): used.add(p)
    plugins = [p for p in PLUGIN_ORDER if p in used]
    num = int(stem[:4]) if stem[:4].isdigit() else None
    crumb = meta.get("crumb") or f"{topic.replace('-', ' ').title()}" + (f" · Lesson {num}" if num else "")
    css = "".join(f'<link rel="stylesheet" href="{ASSETS}plugins/{p}.css">\n' for p in plugins if p != "sim" or (ROOT / "assets/plugins/sim.css").exists())
    if meta.get("css"): css += f'<link rel="stylesheet" href="{esc(meta["css"])}">\n'
    js = "".join(f'<script src="{ASSETS}plugins/{p}.js"></script>\n' for p in plugins)
    main_attrs = "".join(f' {k}="{esc(v)}"' for k, v in (parse_attrs("x " + meta.get("main", ""))[1].items()))
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta['title'])}</title>
<link rel="stylesheet" href="{ASSETS}lp.css">
{css}<!-- generated by scripts/render_lesson.py from {md_path.name}; edit the .md and re-render -->
</head>
<body>
<main{main_attrs}>
<nav class="crumbs"><a href="../../../index.html">All topics</a> · {inline(crumb)}</nav>
<h1>{inline(meta['title'])}</h1>
{('<p class="subtitle">' + inline(meta['subtitle']) + '</p>') if meta.get('subtitle') else ''}
{body_html}
</main>
<script src="{ASSETS}lp.js"></script>
{js}</body>
</html>
"""
    out = md_path.with_suffix(".html")
    out.write_text(page, encoding="utf-8")
    return out, topic, stem, meta


def add_to_index(topic, stem, meta):
    idx = ROOT / "index.html"
    s = idx.read_text(encoding="utf-8")
    href = f"topics/{topic}/lessons/{stem}.html"
    if href in s: return "already listed"
    links = list(re.finditer(rf'<li><a href="topics/{re.escape(topic)}/lessons/[^"]+">.*?</a></li>\n', s))
    if not links: return f"WARN: no lesson list for {topic} in index.html; add one by hand"
    text = inline(meta.get("index") or meta["title"])
    pos = links[-1].end()
    idx.write_text(s[:pos] + f'  <li><a href="{href}">{text}</a></li>\n' + s[pos:], encoding="utf-8")
    return "added to index.html"


def record_in_curriculum(topic, stem, course_id):
    progs = json.loads((ROOT / "programs.json").read_text())
    for m in progs["majors"]:
        if not m.get("curriculum"): continue
        p = ROOT / m["curriculum"]
        cur = json.loads(p.read_text())
        for c in cur["courses"]:
            if c["id"] != course_id: continue
            if c.get("topic", m["slug"]) != topic:
                return f"WARN: course {course_id} uses topic {c.get('topic', m['slug'])}, not {topic}"
            c.setdefault("lessons", [])
            if stem not in c["lessons"]: c["lessons"].append(stem)
            plan = c.get("plan", [])
            if plan and plan[0][:4] == stem[:4]: plan.pop(0)
            if c["status"] in ("next", "later"): c["status"] = "active"
            p.write_text(json.dumps(cur, indent=2, ensure_ascii=False) + "\n")
            return f"recorded in {m['curriculum']} ({course_id})"
    return f"WARN: course {course_id} not found"


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0].startswith("-"): sys.exit(__doc__)
    course = args[args.index("--course") + 1] if "--course" in args else None
    try:
        out, topic, stem, meta = render(args[0])
    except ValueError as e:
        sys.exit(f"render_lesson: {e}")
    print(f"wrote {out.relative_to(ROOT)}")
    if "--no-index" not in args: print(add_to_index(topic, stem, meta))
    if course: print(record_in_curriculum(topic, stem, course))
