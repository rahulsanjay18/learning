#!/usr/bin/env python3
"""Test scripts/render_lesson.py: renders scripts/fixtures/render-sample.md into a scratch topic, lints it, checks the HTML,
then removes the scratch topic.   python3 scripts/test_render.py"""
import pathlib, shutil, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
tmp = ROOT / "topics" / "zz-render-test" / "lessons"
tmp.mkdir(parents=True, exist_ok=True)
fails = 0
try:
    md = tmp / "0001-sample.md"
    shutil.copy(ROOT / "scripts/fixtures/render-sample.md", md)
    r = subprocess.run([sys.executable, str(ROOT / "scripts/render_lesson.py"), str(md), "--no-index"], capture_output=True, text=True)
    if r.returncode: print("FAIL render:", r.stderr); sys.exit(1)
    html = md.with_suffix(".html").read_text()
    lint = subprocess.run([sys.executable, str(ROOT / "scripts/lint_lessons.py"), str(md.with_suffix(".html"))], capture_output=True, text=True)
    checks = {
        "lint clean": lint.returncode == 0,
        "choice from [x] list": 'data-options="Cramming|Spacing|Rereading" data-answer="Spacing"' in html,
        "hint section": 'data-hint="Think about time between sessions."' in html,
        "order items": 'data-items="Mercury|Venus|Earth"' in html,
        "categorize buckets": 'data-buckets="Mammal|Bird"' in html,
        "free rubric": '<div class="rubric">' in html,
        "explain hidden": '<div class="explain" hidden>' in html,
        "deck nests cards": '<div class="lp-deck"><div class="quiz" data-type="card" data-id="fc1">' in html,
        "math < escaped": r"\(x &lt; y\)" in html,
        "plugins auto: math + chess": "plugins/math.js" in html and "plugins/chess.js" in html and "plugins/go.js" not in html,
        "sources list": '<ol class="sources">' in html,
        "main attrs": '<main data-confidence="true">' in html,
        "estimate attrs": 'data-type="estimate" data-id="est1" data-answer="1526" data-unit="CE" data-level="90"' in html,
        "find-error steps list + answer": 'data-type="find-error" data-id="fe1" data-answer="4"' in html and '<ol class="steps"><li>Let \\(a = b\\).</li>' in html,
        "highlight passage": '<div class="passage"><p>The Kalinga war' in html and "[[After the conquest" in html,
        "worked steps": '<div class="step"><p>Step two.</p></div>' in html,
    }
    for name, ok in checks.items():
        print(("ok   " if ok else "FAIL ") + name)
        fails += not ok
    if lint.returncode: print(lint.stdout)
finally:
    shutil.rmtree(ROOT / "topics" / "zz-render-test", ignore_errors=True)
print("render: all passed" if not fails else f"render: {fails} failed")
sys.exit(1 if fails else 0)
