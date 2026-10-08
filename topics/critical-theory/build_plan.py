#!/usr/bin/env python3
"""Critical Theory major: the reading plan as data. Computes reading days per course, writes READING-PLAN.md and the
`plan` / `est_lessons` / `books` fields of curriculum.json. Re-run after editing COURSES:

    python3 topics/critical-theory/build_plan.py

Day sizes are judgment (stated in PROGRAM.md §3): one reading day = one ~25-minute sitting.
Lengths: word counts from library/MANIFEST.csv, page spans from each book's own table of contents
(Norton Anthology of Theory and Criticism 2nd ed., Held, Norton Critical Heart of Darkness), Tyson chapters from line spans
on the book server. Marked "≈" where the length is an estimate (a selection from a longer book).
"""
import json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent

# words a 25-minute sitting covers, by kind of prose (judgment: ~240 wpm easy prose, ~200 VSI, ~140 dense theory)
RATE = {"easy": 6000, "vsi": 5000, "dense": 3500, "drama": 4000}
# words per page, from MANIFEST word counts / page count in each book's contents
WPP = {"norton": 646,   # Norton Anthology of Theory and Criticism: 1,679,888 words / ~2,600 pp
       "held": 397,     # Held: 191,670 words / 483 pp
       "nce": 465}      # Norton Critical Heart of Darkness: 241,818 words / ~520 pp
PAGE_KIND = {"norton": "dense", "held": "dense", "nce": "dense"}

# Tyson, Critical Theory Today (4th ed., 2023), chapter start lines on the book server (DOI lines), and words/line
TYSON_LINES = [451, 512, 859, 1156, 1693, 2077, 2488, 2930, 3355, 3720, 4173, 4747, 5225, 5804, 5862]
TYSON_WPL = 290072 / 6846  # rough: whole-book words / lines


def tyson(ch):
    """≈ words in Tyson chapter ch (1-14)."""
    return round((TYSON_LINES[ch] - TYSON_LINES[ch - 1]) * TYSON_WPL, -2)


def T(ch, title):
    return {"what": f"Tyson ch. {ch}: {title}", "words": tyson(ch), "kind": "easy", "src": "dd5a1301fb", "est": True}


def N(author, title, p0, p1):
    """A Norton Anthology of Theory and Criticism selection, pages p0-p1 (2nd ed., 2010)."""
    return {"what": f"Norton: {author}, \"{title}\" (pp. {p0}-{p1})", "pages": (p1 - p0, "norton"), "src": "face941c2e"}


def W(what, words, kind="easy", src="", est=False):
    return {"what": what, "words": words, "kind": kind, "src": src, "est": est}


def days(r):
    if "pages" in r:
        n, book = r["pages"]
        words, kind = n * WPP[book], PAGE_KIND[book]
    else:
        words, kind = r["words"], r["kind"]
    return max(1, math.ceil(words / RATE[kind])), words


# Each course: theory readings (background), then application readings (the literature). `fry` = Open Yale ENGL 300 lecture
# numbers (optional video, oyc.yale.edu/english/engl-300). Seminar day every SEM reading days, then one course-check day.
SEM = 4
COURSES = [
    {"id": "CT100", "title": "Orientation: what theory is (and read Gatsby)", "fry": [1, 2, 3],
     "primary": "68dc21333b Culler, Literary Theory: A Very Short Introduction (whole)",
     "theory": [W("Culler, Literary Theory VSI (whole: 8 chapters + appendix of schools)", 44479, "vsi", "68dc21333b"),
                T(1, "Everything you wanted to know about critical theory")],
     "apply": [W("Fitzgerald, The Great Gatsby (whole; Tyson's running example)", 50193, "easy", "20cdc786dd")]},

    # ---- Foundations: the thinkers the lenses stand on (philosophy, social theory, psychology) ----
    {"id": "CT110", "title": "Foundations I: philosophy (Hegel, Nietzsche; Kant optional)",
     "primary": "b37abce0ee Singer, Hegel: A Very Short Introduction",
     "theory": [W("Singer, Hegel VSI (whole)", 40237, "vsi", "b37abce0ee"),
                N("Hegel", "Phenomenology of Spirit [The Master-Slave Dialectic]", 630, 636),
                W("Tanner, Nietzsche VSI (whole)", 39541, "vsi", "db1ca8dea1"),
                N("Nietzsche", "On Truth and Lying in a Non-Moral Sense", 874, 884)],
     "apply": []},
    {"id": "CT120", "title": "Foundations II: social theory (Marx, Weber, Durkheim)",
     "primary": "b01fb90f16 Tucker (ed.), The Marx-Engels Reader, 2nd ed. (selections)",
     "theory": [W("Singer, Marx VSI (whole)", 31643, "vsi", "48e175129a"),
                W("Marx & Engels, The Communist Manifesto (Marx-Engels Reader)", 12000, "dense", "b01fb90f16", True),
                W("Marx, 'Estranged Labour' (1844 Manuscripts) and German Ideology Part I selection (Reader)", 17000, "dense", "b01fb90f16", True),
                W("Marx, Capital vol. 1 ch. 1 §4, 'The Fetishism of Commodities' (Reader)", 6000, "dense", "b01fb90f16", True),
                W("Weber, The Protestant Ethic: ch. 2 'The Spirit of Capitalism' and ch. 5 'Asceticism and the Spirit of Capitalism'", 25000, "dense", "4c885b6657", True),
                W("Aron, Main Currents in Sociological Thought vol. 2: Durkheim chapter, opening sections", 15000, "vsi", "0b7173c20a", True),
                W("Mills, The Sociological Imagination, ch. 1 'The Promise'", 8000, "easy", "7fd3ab615b", True)],
     "apply": []},
    {"id": "CT130", "title": "Foundations III: psychology (Freud)",
     "primary": "9c9ab8e41a Storr, Freud: A Very Short Introduction",
     "theory": [W("Storr, Freud VSI (whole)", 48035, "vsi", "9c9ab8e41a"),
                N("Freud", "The Interpretation of Dreams (Ch. V-VI selections)", 919, 929),
                W("Freud, Civilization and Its Discontents (BOOK NEEDED; Columbia CC's long-time last text)", 30000, "dense", "", True)],
     "apply": []},

    # ---- The lenses (Tyson chapter = background + a model reading of Gatsby; Norton = the theorists themselves) ----
    {"id": "CT201", "title": "New Criticism and formalism (close reading)", "fry": [5, 6, 7],
     "primary": "dd5a1301fb Tyson ch. 5",
     "theory": [T(5, "New Criticism"),
                N("T. S. Eliot", "Tradition and the Individual Talent", 1092, 1098),
                N("Ransom", "Criticism, Inc.", 1108, 1118),
                N("Wimsatt & Beardsley", "The Intentional Fallacy", 1374, 1387),
                N("Brooks", "The Heresy of Paraphrase", 1353, 1366)],
     "apply": [W("Joyce, Dubliners: 'Araby', 'Eveline', 'The Dead'", 20000, "easy", "24529ef5be", True)]},
    {"id": "CT202", "title": "Reader-response criticism", "fry": [3, 4, 16],
     "primary": "dd5a1301fb Tyson ch. 6",
     "theory": [T(6, "Reader-response criticism"),
                N("Iser", "Interaction between Text and Reader", 1673, 1682),
                N("Fish", "Interpreting the Variorum", 2071, 2089)],
     "apply": [W("Kafka, The Trial (whole)", 80000, "easy", "ba765724a5", True)]},
    {"id": "CT203", "title": "Structuralism, semiotics and narratology", "fry": [8, 9],
     "primary": "dd5a1301fb Tyson ch. 7",
     "theory": [T(7, "Structuralist criticism"),
                N("Saussure", "Course in General Linguistics (selections)", 960, 977),
                N("Jakobson", "Linguistics and Poetics", 1258, 1265),
                N("Barthes", "Mythologies (three essays)", 1461, 1466),
                N("Todorov", "Structural Analysis of Narrative", 2099, 2106)],
     "apply": [W("Shelley, Frankenstein (whole; a story inside a story inside a story)", 75000, "easy", "cee70ee239", True)]},
    {"id": "CT204", "title": "Deconstruction and poststructuralism", "fry": [10, 11],
     "primary": "dd5a1301fb Tyson ch. 8",
     "theory": [T(8, "Deconstructive criticism"),
                W("Belsey, Poststructuralism VSI (whole)", 33671, "vsi", "6fd2babb95"),
                N("Barthes", "The Death of the Author; From Work to Text", 1466, 1476),
                N("Derrida", "Of Grammatology (Exergue; The Exorbitant. Question of Method)", 1822, 1830),
                N("de Man", "Semiology and Rhetoric", 1514, 1527)],
     "apply": [W("Frankenstein again: re-read the frame letters and the creature's own narrative (ch. 11-16) for its binaries", 20000, "easy", "cee70ee239", True)]},
    {"id": "CT205", "title": "Psychoanalytic criticism", "fry": [12, 13, 15],
     "primary": "dd5a1301fb Tyson ch. 2",
     "theory": [T(2, "Psychoanalytic criticism"),
                N("Freud", "The \"Uncanny\"; Fetishism", 929, 956),
                N("Lacan", "The Mirror Stage", 1286, 1290)],
     "apply": [W("Shakespeare, Hamlet (whole)", 30000, "drama", "474dc72906", True)]},
    {"id": "CT206", "title": "Marxist criticism", "fry": [18],
     "primary": "dd5a1301fb Tyson ch. 3",
     "theory": [T(3, "Marxist criticism"),
                N("Gramsci", "The Formation of the Intellectuals", 1138, 1144),
                N("Althusser", "Ideology and Ideological State Apparatuses (from)", 1483, 1509),
                N("Raymond Williams", "Marxism and Literature: 'Literature'", 1567, 1575),
                N("Jameson", "The Political Unconscious (Preface; from ch. 1)", 1937, 1960)],
     "apply": [W("Yashpal, Dada Comrade (whole; 1941 Hindi novel of the revolutionary underground, tr. Sawhney)", 70000, "easy", "692fb41445", True)]},
    {"id": "CT260", "title": "The Frankfurt School (Critical Theory proper)", "fry": [17],
     "primary": "b6f3f5f15a Held, Introduction to Critical Theory: Horkheimer to Habermas (selected chapters)",
     "theory": [W("Bronner, Critical Theory: A Very Short Introduction (whole)", 50285, "vsi", "4eb171370b"),
                {"what": "Held Introduction: The historical context; the character of critical theory (pp. 13-29)", "pages": (29 - 13, "held"), "src": "b6f3f5f15a"},
                {"what": "Held ch. 1: The formation of the Institute of Social Research (pp. 29-40)", "pages": (40 - 29, "held"), "src": "b6f3f5f15a"},
                {"what": "Held ch. 2: Class, class conflict and the development of capitalism (pp. 40-77)", "pages": (77 - 40, "held"), "src": "b6f3f5f15a"},
                {"what": "Held ch. 3: The culture industry: critical theory and aesthetics (pp. 77-111)", "pages": (111 - 77, "held"), "src": "b6f3f5f15a"},
                {"what": "Held ch. 4: The changing structure of the family and the individual: critical theory and psychoanalysis (pp. 111-148)", "pages": (148 - 111, "held"), "src": "b6f3f5f15a"},
                {"what": "Held ch. 5: The critique of instrumental reason (pp. 148-175)", "pages": (175 - 148, "held"), "src": "b6f3f5f15a"},
                {"what": "Held ch. 9: Introduction to Habermas (pp. 249-260)", "pages": (260 - 249, "held"), "src": "b6f3f5f15a"},
                {"what": "Held ch. 14: The concept of critical theory (pp. 379-401)", "pages": (401 - 379, "held"), "src": "b6f3f5f15a"},
                N("Horkheimer & Adorno", "The Culture Industry: Enlightenment as Mass Deception", 1223, 1240),
                N("Benjamin", "The Work of Art in the Age of Mechanical Reproduction", 1166, 1186),
                W("Marcuse, One-Dimensional Man: Introduction and ch. 1", 12000, "dense", "c1cf685a4d", True),
                N("Habermas", "Structural Transformation of the Public Sphere (from); Modernity: An Incomplete Project", 1745, 1759)],
     "apply": [W("The culture industry now: one film, game or feed of your choice, read with Adorno and Benjamin (no fixed text)", 6000, "easy", "", True)]},
    {"id": "CT207", "title": "Feminist criticism", "fry": [20],
     "primary": "dd5a1301fb Tyson ch. 4",
     "theory": [T(4, "Feminist criticism"),
                W("Beauvoir, The Second Sex: Introduction", 12000, "dense", "d004f50be2", True),
                N("Woolf", "A Room of One's Own [Shakespeare's Sister]; [Androgyny]", 1021, 1030),
                N("Gilbert & Gubar", "The Madwoman in the Attic, ch. 2 (from)", 2023, 2035),
                N("Cixous", "The Laugh of the Medusa", 2039, 2056)],
     "apply": [W("Woolf, To the Lighthouse (whole)", 70000, "easy", "5705dee3e9", True),
               W("Chughtai, 'Lihaaf' (The Quilt), in Manto and Chughtai: The Essential Stories", 3000, "easy", "744967e342", True)]},
    {"id": "CT208", "title": "New historicism and cultural studies", "fry": [19, 24],
     "primary": "dd5a1301fb Tyson ch. 9",
     "theory": [T(9, "New historical and cultural criticism"),
                W("Gutting, Foucault VSI (whole)", 36551, "vsi", "fe70b104b9"),
                N("Foucault", "What Is an Author?; Discipline and Punish: The Carceral", 1622, 1648),
                N("Greenblatt", "Introduction to The Power of Forms in the English Renaissance", 2251, 2255),
                N("Stuart Hall", "Cultural Studies and Its Theoretical Legacies", 1898, 1910)],
     "apply": [W("Conrad, Heart of Darkness (Norton Critical Ed.): the novella", 38000, "easy", "1f7632613f", True),
               {"what": "Heart of Darkness NCE: Backgrounds and Contexts (Conrad's Congo Diary, letters, 'Geography and Some Explorers')", "pages": (307 - 253, "nce"), "src": "1f7632613f"}]},
    {"id": "CT209", "title": "Lesbian, gay and queer criticism", "fry": [23],
     "primary": "dd5a1301fb Tyson ch. 10",
     "theory": [T(10, "Lesbian, gay, and queer criticism"),
                N("Foucault", "The History of Sexuality vol. 1: The Incitement to Discourse", 1648, 1659),
                N("Sedgwick", "Between Men (from Introduction); Epistemology of the Closet (Axiomatic)", 2434, 2445),
                N("Butler", "Gender Trouble (Preface; Subversive Bodily Acts)", 2488, 2502)],
     "apply": [W("Gatsby again: Nick Carraway (Tyson's queer reading, then ch. 1-2 re-read); 'Lihaaf' again", 12000, "easy", "20cdc786dd", True),
               {"what": "HoD NCE: Roberts, '[Masculinity, Modernity, and Homosexual Desire]'", "pages": (463 - 455, "nce"), "src": "1f7632613f"}]},
    {"id": "CT210", "title": "African American criticism and critical race theory", "fry": [21],
     "primary": "dd5a1301fb Tyson ch. 11",
     "theory": [T(11, "African American criticism"),
                N("Du Bois", "Criteria of Negro Art", 980, 987),
                N("Hurston", "Characteristics of Negro Expression; What White Publishers Won't Print", 1146, 1163),
                N("Hughes", "The Negro Artist and the Racial Mountain", 1313, 1317),
                N("Gates", "Talking Black: Critical Signs of the Times", 2424, 2432),
                N("Barbara Smith", "Toward a Black Feminist Criticism", 2302, 2316)],
     "apply": [W("Ellison, Invisible Man (whole)", 180000, "easy", "7003a0782e", True)]},
    {"id": "CT211", "title": "Postcolonial criticism", "fry": [22],
     "primary": "dd5a1301fb Tyson ch. 12",
     "theory": [T(12, "Postcolonial criticism"),
                W("Kennedy, Decolonization: A Very Short Introduction (history background; whole)", 62148, "vsi", "fb7f89f762"),
                N("Fanon", "The Wretched of the Earth (two chapters, from)", 1578, 1595),
                N("Said", "Orientalism: Introduction", 1991, 2012),
                N("Spivak", "[Can the Subaltern Speak?]", 2197, 2208),
                N("Ngugi et al.", "On the Abolition of the English Department", 2092, 2097),
                N("Achebe", "An Image of Africa: Racism in Conrad's Heart of Darkness", 1783, 1794)],
     "apply": [W("Achebe, Things Fall Apart (whole; in The African Trilogy)", 50000, "easy", "f6b767de9a", True),
               W("Manto, 'Toba Tek Singh'", 3000, "easy", "744967e342", True)]},
    {"id": "CT212", "title": "Ecocriticism",
     "primary": "dd5a1301fb Tyson ch. 13",
     "theory": [T(13, "Ecocriticism"),
                N("Haraway", "A Manifesto for Cyborgs (from)", 2269, 2283)],
     "apply": [W("Woolf, To the Lighthouse, 'Time Passes' re-read; Frankenstein's Alpine chapters (ch. 9-10) re-read", 12000, "easy", "", True)]},
    {"id": "CT290", "title": "One text, many lenses: Heart of Darkness and its critics", "fry": [25, 26],
     "primary": "1f7632613f Conrad, Heart of Darkness, Norton Critical Edition (4th ed., ed. Armstrong): the essays in criticism",
     "theory": [T(14, "Gaining an overview")],
     "apply": [{"what": "HoD NCE essays: Guerard; Watt; Hawkins; Brooks; Brantlinger; Torgovnick; Hawthorn; Said; Armstrong; Miller (Achebe and Roberts already read)", "pages": (474 - 326 - (349 - 336) - (463 - 455), "nce"), "src": "1f7632613f"}]},
]


def build():
    out = ["# Critical Theory: reading plan (generated)", "",
           "Generated by `build_plan.py` from its `COURSES` list; edit there, not here. One **reading day** = one ~25-minute sitting.",
           f"A **seminar day** (a real lesson page) comes after every {SEM} reading days (Fridays); each course's last Friday is its **course check**",
           "(a short lens essay). ≈ = length estimated from a selection of a longer book. `src` = library id (all grade A).", ""]
    tot = {"read": 0, "sem": 0}
    for c in COURSES:
        rows, rd = [], 0
        for part in ("theory", "apply"):
            for r in c.get(part, []):
                d, words = days(r)
                rd += d
                rows.append(f"| {'theory' if part == 'theory' else 'apply'} | {r['what']} | {r.get('src') or '—'} | "
                            f"{'≈' if r.get('est') else ''}{int(words):,} | {d} |")
        sem = math.ceil(rd / SEM)  # one Friday per week; the last one is the lens essay
        c["reading_days"], c["seminar_days"] = rd, sem
        tot["read"] += rd; tot["sem"] += sem
        fry = f" · optional video: Open Yale ENGL 300 lectures {', '.join(map(str, c['fry']))}" if c.get("fry") else ""
        out += [f"## {c['id']} {c['title']}", f"{rd} reading days + {sem} seminar/check days = **{rd + sem} days**{fry}", "",
                "| part | reading | src | words | days |", "|---|---|---|---|---|", *rows, ""]
    n = tot["read"] + tot["sem"]
    out += ["## Totals (Level I core)", "",
            f"- {tot['read']} reading days + {tot['sem']} seminar/check days = **{n} days** (one ~25-minute sitting each)",
            f"- daily (7/week): ≈ {n / 7 / 4.345:.0f} months · 5/week: ≈ {n / 5 / 4.345:.0f} months · "
            f"half subject (2/week): ≈ {n / 2 / 52:.1f} years", ""]
    (HERE / "READING-PLAN.md").write_text("\n".join(out), encoding="utf-8")

    cur_p = HERE / "curriculum.json"
    cur = json.loads(cur_p.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cur["courses"]}
    for c in COURSES:
        cc = by_id[c["id"]]
        cc["est_lessons"] = c["reading_days"] + c["seminar_days"]
        cc.setdefault("books", {})["primary"] = c["primary"]
        pid = c["primary"].split()[0]
        cc["books"]["secondary"] = [f"{r['src']} {r['what']}".strip() for part in ("theory", "apply") for r in c.get(part, [])
                                    if r.get("src") != pid]
    cur_p.write_text(json.dumps(cur, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\n".join(out[-4:]))
    for c in COURSES:
        print(f"{c['id']}: {c['reading_days']} + {c['seminar_days']}")


if __name__ == "__main__":
    build()
