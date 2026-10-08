#!/usr/bin/env python3
"""Tests for the STEM-major builder and the checks added with it (build_majors, test_programs entry points,
major_dag terms/entry points, lint_lessons Extra practice warning).   python3 scripts/test_stem_majors.py"""
import copy, importlib.util, json, re, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUGS = ["math", "physics", "mech-eng", "unified-eng"]
HEX10 = re.compile(r"^[0-9a-f]{10}$")


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bsm = load("build_majors")
dag = load("major_dag")
lint = load("lint_lessons")
BUILT = {s: bsm.build(s) for s in SLUGS}
PROGRAMS = json.loads((ROOT / "programs.json").read_text(encoding="utf-8"))
MAJOR_CFG = {m["slug"]: m for m in PROGRAMS["majors"] + PROGRAMS.get("parked", [])}


def refs(books):
    return [books.get("primary", "")] + [r for k in ("secondary", "tertiary", "skip") for r in books.get(k, [])]


class Build(unittest.TestCase):
    def test_requires_exist_in_same_major(self):
        for s, cur in BUILT.items():
            ids = {c["id"] for c in cur["courses"]}
            for c in cur["courses"]:
                for r in c["requires"]:
                    self.assertIn(r, ids, f"{s}/{c['id']} requires {r}")

    def test_no_cycles(self):
        for s, cur in BUILT.items():
            req = {c["id"]: c["requires"] for c in cur["courses"]}
            state = {}

            def visit(cid, path):
                self.assertNotEqual(state.get(cid), 1, f"{s}: cycle {path + [cid]}")
                if state.get(cid) == 2:
                    return
                state[cid] = 1
                for r in req[cid]:
                    visit(r, path + [cid])
                state[cid] = 2
            for cid in req:
                visit(cid, [])

    def test_core_requires_only_core(self):
        for s, cur in BUILT.items():
            grp = {c["id"]: c["group"] for c in cur["courses"]}
            for c in cur["courses"]:
                if c["group"] == "core":
                    for r in c["requires"]:
                        self.assertEqual(grp[r], "core", f"{s}/{c['id']} requires optional {r}")

    def test_shared_ids_identical_and_cross_listed(self):
        owners = {}
        for s, cur in BUILT.items():
            for c in cur["courses"]:
                owners.setdefault(c["id"], []).append((s, c))
        self.assertGreater(len(owners["MA140"]), 1)
        self.assertGreater(len(owners["ES211"]), 1)
        for cid, lst in owners.items():
            first = lst[0][1]
            for s, c in lst:
                for k in ("title", "requires", "est_lessons", "books", "level"):
                    self.assertEqual(c[k], first[k], f"{cid}.{k} differs in {s}")
                xl = "Cross-listed with" in c.get("note", "")
                self.assertEqual(xl, len(lst) > 1, f"{s}/{cid}: cross-listed note {xl}, in {len(lst)} majors")
                if xl:
                    for o, _ in lst:
                        if o != s:
                            self.assertIn(bsm.MAJORS[o]["name"], c["note"])

    def test_committed_files_not_stale(self):
        for s, cur in BUILT.items():
            p = ROOT / "topics" / s / "curriculum.json"
            self.assertEqual(json.loads(p.read_text(encoding="utf-8")), cur, f"{p} is stale: run build_majors.py")

    def test_entry_points(self):
        for s, cur in BUILT.items():
            ep, by = cur["entry_points"], {c["id"]: c for c in cur["courses"]}
            cred, maybe, start = (set(ep[k]) for k in ("credited", "maybe", "start"))
            self.assertFalse(cred & maybe or cred & start or maybe & start, f"{s}: credited/maybe/start overlap")
            for k in ("high_school", "credited", "maybe", "start"):
                for cid in ep[k]:
                    self.assertIn(cid, by, f"{s}: entry_points.{k} {cid}")
            for cid in start:
                self.assertLessEqual(set(by[cid]["requires"]), cred | maybe, f"{s}: start {cid}")
            for cid in ep["high_school"]:
                self.assertEqual(by[cid]["requires"], [], f"{s}: high_school {cid}")
            self.assertTrue(ep["basis"])

    def test_book_ids_in_manifest(self):
        lines = (ROOT / "library" / "MANIFEST.csv").read_text(encoding="utf-8").splitlines()[1:]
        manifest = {l.split(",", 1)[0] for l in lines if l}
        for s, cur in BUILT.items():
            for c in cur["courses"]:
                for ref in refs(c["books"]):
                    bid = ref.split()[0].rstrip(":") if ref else ""
                    if HEX10.match(bid):
                        self.assertIn(bid, manifest, f"{s}/{c['id']}: {ref}")

    def test_build_rejects_broken_majors(self):
        saved_m, saved_c = copy.deepcopy(bsm.MAJORS), copy.deepcopy(bsm.C)
        try:
            bsm.MAJORS["math"]["core"].remove("MA100")      # MA140 now requires a course outside the major
            for g in ("elective", "breadth", "practice", "colloquium", "capstone"):
                if "MA100" in bsm.MAJORS["math"].get(g, []):
                    bsm.MAJORS["math"][g].remove("MA100")
            with self.assertRaises(SystemExit):
                bsm.build("math")
            bsm.MAJORS.clear(); bsm.MAJORS.update(copy.deepcopy(saved_m))
            core = bsm.MAJORS["physics"]["core"]             # core course requiring an optional one
            core.remove("MA100"); bsm.MAJORS["physics"]["elective"].append("MA100")
            with self.assertRaises(SystemExit):
                bsm.build("physics")
        finally:
            bsm.MAJORS.clear(); bsm.MAJORS.update(saved_m)
            bsm.C.clear(); bsm.C.update(saved_c)
        self.assertEqual(bsm.build("math"), BUILT["math"])

    def test_stats_runs(self):
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_majors.py"), "--stats"],
                           capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Unified Engineering", r.stdout)


class Dag(unittest.TestCase):
    def test_render(self):
        ue = dag.render(MAJOR_CFG["unified-eng"], BUILT["unified-eng"])
        ma = dag.render(MAJOR_CFG["math"], BUILT["math"])
        self.assertIn("subgraph", ue)
        self.assertNotIn("subgraph", ma)
        for out, s in ((ue, "unified-eng"), (ma, "math")):
            self.assertIn("## Where you enter", out)
            sid = BUILT[s]["entry_points"]["start"][0]
            self.assertIn(f"class {sid} start", out)
            cid = BUILT[s]["entry_points"]["credited"][0]
            self.assertIn(f"class {cid} credited", out)
        # every term course sits inside its subgraph block
        blocks = re.findall(r'subgraph T\d+\["(.+?)"\]\n(.*?)\n  end', ue, re.S)
        terms = BUILT["unified-eng"]["terms"]
        self.assertEqual([b[0] for b in blocks], list(terms))
        for name, body in blocks:
            self.assertEqual(re.findall(r"^    (\S+?)\[", body, re.M), terms[name])


class Lint(unittest.TestCase):
    PAGE = '<html><body><h1>T</h1><ol class="sources"><li>x</li></ol>{}</body></html>'

    def run_lint(self, html, grandfather=False):
        tmp = Path(tempfile.mkdtemp())
        saved = lint.ROOT, lint.GRANDFATHERED
        try:
            p = tmp / "topics" / "x" / "lessons" / "0001-a.html"
            p.parent.mkdir(parents=True)
            p.write_text(html, encoding="utf-8")
            lint.ROOT = tmp
            lint.GRANDFATHERED = {"topics/x/lessons/0001-a.html"} if grandfather else set()
            return [w for w in lint.lint(p)[2] if "Extra practice" in w]
        finally:
            lint.ROOT, lint.GRANDFATHERED = saved
            shutil.rmtree(tmp)

    def test_warns_without_extra_practice(self):
        self.assertEqual(len(self.run_lint(self.PAGE.format("<h2>Summary</h2>"))), 1)

    def test_quiet_with_extra_practice(self):
        self.assertEqual(self.run_lint(self.PAGE.format('<h2 id="ep">Extra practice (optional)</h2>')), [])

    def test_grandfathered_quiet(self):
        self.assertEqual(self.run_lint(self.PAGE.format(""), grandfather=True), [])

    def test_fixture_entries_exist(self):
        for rel in lint.GRANDFATHERED:
            self.assertTrue((ROOT / rel).exists(), f"pre-extra-practice.txt lists missing {rel}")


class ProgramsEntryCheck(unittest.TestCase):
    def run_programs(self, cur):
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "scripts").mkdir()
            (tmp / "library").mkdir()
            shutil.copy(ROOT / "scripts" / "test_programs.py", tmp / "scripts")
            (tmp / "scripts" / "catalog.py").write_text("import sys; sys.exit(0)\n")
            shutil.copy(ROOT / "library" / "MANIFEST.csv", tmp / "library")
            (tmp / "topics" / "math").mkdir(parents=True)
            (tmp / "topics" / "math" / "curriculum.json").write_text(json.dumps(cur))
            (tmp / "programs.json").write_text(json.dumps({"majors": [], "week": {}, "parked": [
                {"slug": "math", "name": "Mathematics", "curriculum": "topics/math/curriculum.json"}]}))
            r = subprocess.run([sys.executable, str(tmp / "scripts" / "test_programs.py")], capture_output=True, text=True)
            return r.returncode, r.stdout
        finally:
            shutil.rmtree(tmp)

    def test_clean_copy_passes(self):
        code, out = self.run_programs(BUILT["math"])
        self.assertEqual(code, 0, out)

    def test_uncredited_start_prereq_errors(self):
        cur = copy.deepcopy(BUILT["math"])
        ep = cur["entry_points"]
        by = {c["id"]: c for c in cur["courses"]}
        sid = next(s for s in ep["start"] if by[s]["requires"])
        dropped = by[sid]["requires"][0]
        for k in ("credited", "maybe"):
            if dropped in ep[k]:
                ep[k].remove(dropped)
        code, out = self.run_programs(cur)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, rf"ERROR math: entry_points.start {sid} needs .*{dropped}")

    def test_unknown_entry_id_errors(self):
        cur = copy.deepcopy(BUILT["math"])
        cur["entry_points"]["maybe"].append("ZZ999")
        code, out = self.run_programs(cur)
        self.assertEqual(code, 1, out)
        self.assertIn("entry_points.maybe names unknown course ZZ999", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
