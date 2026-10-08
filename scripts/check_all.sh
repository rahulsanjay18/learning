#!/usr/bin/env bash
# Run every check before committing; prints one line per suite. Usage: bash scripts/check_all.sh [--quick]
# (--quick skips the browser smoke test and the depth-4 perfts.)
cd "$(dirname "$0")/.." || exit 1
fail=0
run() { local name="$1"; shift; if out=$("$@" 2>&1); then echo "ok    $name"; else echo "FAIL  $name"; echo "$out" | grep -E "FAIL|ERROR|Error" | head -5; fail=1; fi; }
run lint        python3 scripts/lint_lessons.py
run programs    python3 scripts/test_programs.py
run syllabi     python3 scripts/render_syllabi.py --check
run dags        python3 scripts/major_dag.py --check
run built-majors python3 scripts/test_stem_majors.py
run render      python3 scripts/test_render.py
run today       node scripts/test_today.mjs
run games       node scripts/test_games.js
run sim         node scripts/test_sim.js
run math        node scripts/test_math.js
run plot        node scripts/test_plot.js
run go          node scripts/test_go_rules.js
run timeline    node scripts/test_timeline_map.js
run diagram     node scripts/test_diagram.js
run python      node scripts/test_python.js
run progress-server bash -c "cd progress-server && python3 test_app.py"
run book-server bash -c "cd book-server && python3 test_app.py"
if [ "$1" = "--quick" ]; then run xiangqi-shogi node scripts/test_xiangqi_shogi.js --quick
else run xiangqi-shogi node scripts/test_xiangqi_shogi.js; run widgets node scripts/test_widgets.mjs; fi
exit $fail
