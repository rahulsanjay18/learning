#!/usr/bin/env python3
"""Build the curriculum.json of the parked majors designed 2026-10-08 (math, physics, mech-eng, unified-eng, music, english)
from ONE course list.

    python3 scripts/build_majors.py          write topics/<major>/curriculum.json for all of them
    python3 scripts/build_majors.py --stats  print size tables (lessons, weeks) from high school and from your entry point

Why one file: the majors share courses (Calculus I is the same course in all four, Statics in two). A shared course has one id and
one definition here, so finishing it in any major counts in every major that lists it ("cross-listed"). Edit here, re-run, then
python3 scripts/major_dag.py and python3 scripts/test_programs.py. Designed 2026-10-08; see each topic's PROGRAM.md.

Book refs: "<library id> Author, Title (chapters)" when in the collection (grade in library/MANIFEST.csv), "(TO ACQUIRE)" when
not, "(free: <url>)" for open books. est_lessons are estimates (one lesson = 2 blocks of 25 min), to be replaced by the course
syllabus when a course starts; chapter ranges marked "to confirm" are checked against the contents page then.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# id: (title, requires, est_lessons, level, books{primary, secondary, tertiary, skip}, note)
C = {}


def course(cid, title, requires, est, books, level="I", note=None):
    C[cid] = dict(id=cid, title=title, requires=requires, est_lessons=est, level=level, books=books, note=note)


B = lambda primary, secondary=(), tertiary=(), skip=(): {k: v for k, v in dict(
    primary=primary, secondary=list(secondary), tertiary=list(tertiary), skip=list(skip)).items() if v}
ACQ = "(TO ACQUIRE)"

# ---------------------------------------------------------------- shared base: math (ids follow Penn State numbers on purpose)
course("MA100", "Precalculus: algebra, functions, trigonometry", [], 20, B(
    "00ac5c759e OpenStax, Precalculus 2e (whole)",
    ["64ac8fea6f OpenStax, Algebra and Trigonometry 2e (extra practice)"],
    ["7bebe8cff5 Rusczyk & Lehoczky, The Art of Problem Solving vol. 1", "7e7a1d8805 Polya, How to Solve It"]))
course("MA140", "Calculus I: limits, derivatives, integrals", ["MA100"], 24, B(
    "94a6ff068c OpenStax, Calculus Volume 1 (whole; equations from the openstax.org web edition)",
    ["Spivak, Calculus " + ACQ + " (the proof-first alternative, for the math major)"],
    skip=["9c143e072e Stewart, Calculus 8th: grade C copy", "71f8006738 Thomas' Calculus: grade C copy"]))
course("MA141", "Calculus II: integration techniques, sequences and series, parametric and polar", ["MA140"], 22, B(
    "0db419bb48 OpenStax, Calculus Volume 2 (whole)"))
course("MA220", "Matrices: computational linear algebra", ["MA100"], 18, B(
    "d694d5cc9d Strang, Introduction to Linear Algebra (ch. 1-7)",
    ["44e0e775eb Lay, Linear Algebra and Its Applications (more worked examples)"],
    ["0ea7f89d5e Savov, No Bullshit Guide to Linear Algebra"]))
course("MA230", "Calculus of several variables and vector analysis", ["MA141", "MA220"], 24, B(
    "8f45554212 OpenStax, Calculus Volume 3 (whole)",
    ["Schey, Div, Grad, Curl, and All That " + ACQ + " (vector calculus the way physics uses it)"]))
course("MA250", "Ordinary differential equations", ["MA141", "MA220"], 20, B(
    "3153c30773 Zill, Differential Equations with Boundary-Value Problems 8th (ch. 1-8, 11-12; to confirm)",
    ["c83f1abba8 Ordinary Differential Equations (second source; identify author when the course starts)"]))
course("MA311", "Proofs: logic, sets, induction, relations, functions", ["MA141"], 18, B(
    "7657f3ebf3 Velleman, How to Prove It (ch. 1-7)",
    ["1bc1423cf5 Halmos, Naive Set Theory (grade A)", "d9694b9899 Chartrand et al., Mathematical Proofs (more exercises)"],
    ["4aaff76254 Cummings, Proofs: A Long-Form Mathematics Textbook"]))
course("MA312", "Real analysis I: the real line, sequences, series, continuity, derivative", ["MA311"], 20, B(
    "1f0fdaeaa7 Abbott, Understanding Analysis (ch. 1-5)",
    ["7bd6779091 Ross, Elementary Analysis (more routine exercises)", "e2b4dd743f Tao, Analysis I (construction of the reals)"]))
course("MA403", "Real analysis II: metric spaces, uniform convergence, Riemann-Stieltjes, several variables", ["MA312", "MA230"], 24, B(
    "eb63d86f9a Rudin, Principles of Mathematical Analysis (ch. 2-7, 9)",
    ["1f0fdaeaa7 Abbott ch. 6-8 (gentler first pass on sequences of functions)"]))
course("MA414", "Probability", ["MA230"], 16, B(
    "4aac0e45ba Bertsekas & Tsitsiklis, Introduction to Probability 2nd (ch. 1-9)",
    ["a53c1f767c Haigh, Probability VSI (grade A)"]),
    note="Also covered by the Statistics major (Casella & Berger ch. 1-5): either one counts.")
course("MA435", "Abstract algebra I: groups and symmetry", ["MA311", "MA220"], 22, B(
    "84078260e2 Artin, Algebra 1st ed. (ch. 2 Groups, 5 Symmetry, 6 More Group Theory; grade A)",
    ["07f3b2e15e Numbers, Groups and Codes (gentler examples)"]))
course("MA436", "Linear algebra done abstractly: vector spaces, operators, spectral theorem", ["MA311", "MA220"], 20, B(
    "b7c48458b1 Axler, Linear Algebra Done Right (ch. 1-8)",
    ["84078260e2 Artin ch. 3-4, 7 (bilinear forms, spectral theorem)"]))
course("MA437", "Abstract algebra II: rings, factorization, fields, Galois theory", ["MA435"], 24, B(
    "84078260e2 Artin, Algebra (ch. 10 Rings, 11 Factorization, 13 Fields, 14 Galois Theory)",
    ["c2d9599de2 Emil Artin, Galois Theory (the classic short treatment)"]))
course("MA421", "Complex analysis", ["MA312", "MA230"], 18, B(
    "1646f5592d Bak & Newman, Complex Analysis 3rd (UTM)",
    [], ["31ba41c2be Ahlfors (saved for Level II)"]))
course("MA429", "Topology: metric and topological spaces", ["MA312"], 16, B(
    "bb6ca17498 Sutherland, Introduction to Metric and Topological Spaces"))
course("MA412", "Fourier series and partial differential equations", ["MA250", "MA230"], 18, B(
    "498a8db119 Strauss, Partial Differential Equations: An Introduction (ch. 1-7)",
    ["4d1d41414b Haberman, Applied Partial Differential Equations (engineering flavour)"]))
course("MA455", "Numerical analysis", ["MA250", "MA220"], 18, B(
    "f489dc5bbb Burden & Faires, Numerical Analysis"))
course("MA360", "Concrete and discrete mathematics: sums, recurrences, generating functions", ["MA311"], 18, B(
    "f33a3eecfe Graham, Knuth & Patashnik, Concrete Mathematics (grade A)"))
course("MA465", "Number theory", ["MA311"], 14, B(
    "Silverman, A Friendly Introduction to Number Theory " + ACQ, ["4dbcaf8f24 Wilson, Number Theory VSI"]))
course("MA417", "Dynamical systems and chaos", ["MA250", "MA220"], 18, B(
    "Strogatz, Nonlinear Dynamics and Chaos 2nd " + ACQ + " (7774a5cc7e is a grade C copy)",
    ["bcad5b159e Smith, Chaos VSI (grade A)"]))
course("MA470", "Geometry: Euclid and beyond", ["MA311"], 14, B(
    "104491854b Euclid, Elements (Books I-VI)", ["Hartshorne, Geometry: Euclid and Beyond " + ACQ]))
course("MA480", "Differential forms and calculus on manifolds", ["MA230", "MA436"], 14, B(
    "5ca9747aa6 Bachman, A Visual Introduction to Differential Forms and Calculus on Manifolds"))
course("MA457", "Mathematical logic", ["MA311"], 16, B(
    "8d01f38f50 Enderton, A Mathematical Introduction to Logic (ch. 1-2)", ["b4cb422d7f Priest, Logic VSI"]))
course("MA190", "Breadth: what mathematics is, and its history", [], 8, B(
    "8b1e10be36 Stedall, The History of Mathematics VSI (grade A)",
    ["23bb8dac0b Gowers, Mathematics VSI", "52315ec509 Gowers (ed.), Princeton Companion to Mathematics (dip in)"]))
course("MA390", "Practice: problem solving (Putnam-style)", ["MA311"], 16, B(
    "57583b8957 Zeitz, The Art and Craft of Problem Solving 3rd",
    ["0e6b3043b5 Engel, Problem-Solving Strategies", "829f2d5a5a Gelca & Andreescu, Putnam and Beyond"]))
course("MA398", "End-of-level conversation (Level I)", ["MA403", "MA437"], 1, B("list of works read + a typed conversation"))
course("MA399", "Capstone: an expository paper on a topic you pick", ["MA403", "MA437"], 8, B("optional; to choose with you"))
# Level II
course("MA501", "Graduate algebra: groups, rings, modules, fields", ["MA437", "MA436"], 36, B(
    "Dummit & Foote, Abstract Algebra 3rd " + ACQ, ["c2d9599de2 E. Artin, Galois Theory"]), level="II")
course("MA511", "Measure and integration", ["MA403", "MA429"], 30, B(
    "Folland, Real Analysis 2nd " + ACQ, ["4dc05f0beb Fremlin, Measure Theory vol. 1"]), level="II",
    note="Overlaps Statistics S501 (measure-theoretic probability): either covers the measure theory.")
course("MA521", "Complex analysis (graduate)", ["MA421", "MA403"], 24, B(
    "ffc847bb21 Ahlfors, Complex Analysis 3rd", ["0c1388fa95 Solutions to Ahlfors"]), level="II")
course("MA531", "Topology (graduate)", ["MA429"], 24, B("Munkres, Topology 2nd " + ACQ), level="II")
course("MA541", "Functional analysis", ["MA511", "MA436"], 24, B(
    "Kreyszig, Introductory Functional Analysis with Applications " + ACQ), level="II")
course("MA551", "Smooth manifolds", ["MA531", "MA403"], 30, B("Lee, Introduction to Smooth Manifolds 2nd " + ACQ), level="II")
course("MA561", "Algebraic topology", ["MA531", "MA501"], 30, B(
    "Hatcher, Algebraic Topology (free: https://pi.math.cornell.edu/~hatcher/AT/ATpage.html)"), level="II")
course("MA595", "Practice: qualifying-exam self-check", ["MA501", "MA511", "MA521"], 6, B(
    "d609983fe4 Problems and Solutions in Mathematics (grade A; graduate qualifying problems)"), level="II")
course("MA598", "End-of-level conversation (Level II)", ["MA501", "MA511"], 1, B("list of works + conversation"), level="II")
course("MA599", "Capstone: reproduce and extend a published result", ["MA501", "MA511"], 12, B("optional"), level="II")

# ---------------------------------------------------------------- physics
course("PH211", "Mechanics (calculus-based)", ["MA140"], 24, B(
    "7a77752ee7 OpenStax, University Physics Volume 1 (ch. 1-13)",
    ["dd59c2b9cb Feynman, Leighton & Sands, The Feynman Lectures vol. 1 (grade A)",
     "1df1fdcbf3 Epstein, Thinking Physics (grade A; concept questions)"],
    ["b467b6c3a7 Irodov, Problems in General Physics (hard problems)"]))
course("PH212", "Electricity and magnetism (calculus-based)", ["PH211", "MA141"], 22, B(
    "9fc1f17d2b OpenStax, University Physics Volume 2 (ch. 5-16)",
    ["dd59c2b9cb Feynman Lectures vol. 2", "837676dd13 Blundell, Magnetism VSI"]))
course("PH213", "Fluids and thermal physics (intro)", ["PH211", "MA141"], 10, B(
    "7a77752ee7 University Physics Vol. 1 ch. 14 (fluids) + 9fc1f17d2b Vol. 2 ch. 1-4 (thermodynamics)",
    ["26a7bb9d15 Atkins, The Laws of Thermodynamics VSI (grade A)"]))
course("PH214", "Waves, optics and the first quantum ideas", ["PH212"], 16, B(
    "8413f9ab20 OpenStax, University Physics Volume 3 (ch. 1-4 optics, 6-7 photons and matter waves) + Vol. 1 ch. 15-17 (waves)",
    ["913318cd5d King, Vibrations and Waves", "8f4b3a9ae8 Walmsley, Light VSI"]))
course("PH237", "Modern physics: relativity, quanta, atoms, nuclei", ["PH214", "MA250"], 22, B(
    "2cd5fda79d Krane, Modern Physics 3rd",
    ["81b23e4acc Krane solutions manual", "dda01c3751 Tipler, Modern Physics (second angle)", "a63c0b132f Stannard, Relativity VSI"]))
course("PH300", "Mathematical methods for physics", ["MA230", "MA250", "MA220"], 30, B(
    "74220179dd Boas, Mathematical Methods in the Physical Sciences 3rd",
    [], ["3974765a7c Neuenschwander, Tensor Calculus for Physics"]))
course("PH341", "Classical mechanics: oscillators, Lagrangian and Hamiltonian mechanics", ["PH211", "PH300"], 28, B(
    "Taylor, Classical Mechanics " + ACQ,
    ["7ac218e2d7 Kleppner & Kolenkow, An Introduction to Mechanics (harder problems, no Lagrangians)",
     "9cb5dfc9e9 Cline, A Student's Guide to Lagrangians and Hamiltonians"],
    ["0c80afee2b Susskind & Friedman, Special Relativity and Classical Field Theory"],
    ["bbbe0ab978 Szolga, Theoretical Mechanics: engineering statics/kinematics notes, not a physics mechanics text"]))
course("PH351", "Electromagnetism I: electrostatics, magnetostatics, fields in matter", ["PH212", "PH300"], 28, B(
    "Griffiths, Introduction to Electrodynamics 4th " + ACQ + " (ch. 1-6; library has only the grade C solutions manual)",
    ["a94084b715 Lim (ed.), Problems and Solutions on Electromagnetism (grade A)", "dd59c2b9cb Feynman Lectures vol. 2"],
    skip=["ab5921bd2c Fleisch, Student's Guide to Maxwell's Equations: grade C copy (nice, but reacquire)"]))
course("PH352", "Electromagnetism II: electrodynamics, waves, radiation, relativity", ["PH351"], 22, B(
    "Griffiths, Introduction to Electrodynamics 4th " + ACQ + " (ch. 7-12)"))
course("PH361", "Quantum mechanics I", ["PH237", "PH300"], 26, B(
    "0ee9b34802 Griffiths & Schroeter, Introduction to Quantum Mechanics 3rd (ch. 1-4)",
    ["4776a751e8 Lim (ed.), Problems and Solutions on Quantum Mechanics (grade A)",
     "86a30c2247 Susskind & Friedman, Quantum Mechanics: The Theoretical Minimum"],
    ["3551f2415d Polkinghorne, Quantum Theory VSI"]))
course("PH362", "Quantum mechanics II: identical particles, perturbation theory, scattering", ["PH361"], 24, B(
    "0ee9b34802 Griffiths & Schroeter (ch. 5-11; to confirm)"))
course("PH371", "Thermal and statistical physics", ["PH213", "PH237", "MA230"], 24, B(
    "Schroeder, An Introduction to Thermal Physics " + ACQ,
    ["762ad02c0c Fermi, Thermodynamics (short classic)",
     "c9b3dec133 Lim (ed.), Problems and Solutions on Thermodynamics and Statistical Mechanics"]))
course("PH380", "Computational physics", ["PH341", "MA250"], 16, B("50192acbf8 Fitzpatrick, Computational Physics",
                                                                   ["cd15b46e63 Computational Physics (KNA)"]))
course("PH391", "Optics", ["PH352"], 16, B("Hecht, Optics 5th " + ACQ, ["8ebb40b916 Problems and Solutions on Optics"]))
course("PH393", "Nuclear and particle physics", ["PH361"], 18, B(
    "Griffiths, Introduction to Elementary Particles 2nd " + ACQ,
    ["d556c60ed7 Problems and Solutions on Atomic, Nuclear and Particle Physics", "e9747c8e44 Close, Nuclear Physics VSI"]))
course("PH394", "General relativity (undergraduate)", ["PH352", "PH341"], 20, B(
    "23146c01f2 Schutz, A First Course in General Relativity 2nd", ["5486fe7ce2 Hartle, Gravity (solutions)"]))
course("PH395", "Solid state physics", ["PH361", "PH371"], 18, B(
    "25c3c4d5a3 Simon, The Oxford Solid State Basics", ["6f96fef10c Simon solutions manual"]))
course("PH396", "Astrophysics", ["PH237", "PH341"], 24, B(
    "ea074d5ccf Carroll & Ostlie, An Introduction to Modern Astrophysics 2nd", ["8145173275 Binney, Astrophysics VSI"]))
course("PH190", "Breadth: what physics is, how it got here, how it knows", [], 8, B(
    "deec23b0f9 Perkowitz, Physics VSI (grade A)",
    ["7037d25245 Iliffe, Newton VSI", "443d179c7f Drake, Galileo VSI",
     "d22758f771 Cover & Curd, Philosophy of Science: The Central Issues (selected)"]))
course("PH390", "Practice: tabletop and phone-sensor experiments", ["PH211"], 8, B(
    "phyphox (free phone-sensor lab app, RWTH Aachen: https://phyphox.org) + University Physics lab-style problems"))
course("PH398", "End-of-level conversation (Level I)", ["PH352", "PH362", "PH371"], 1, B("list of works + conversation"))
course("PH399", "Capstone: senior thesis (reproduce a classic result numerically or on the bench)", ["PH341", "PH361"], 12, B("optional"))
course("PH501", "Classical mechanics (graduate)", ["PH341"], 26, B("Goldstein, Poole & Safko, Classical Mechanics 3rd " + ACQ), level="II")
course("PH511", "Classical electrodynamics (graduate)", ["PH352", "PH541"], 36, B("Jackson, Classical Electrodynamics 3rd " + ACQ), level="II")
course("PH521", "Quantum mechanics (graduate)", ["PH362", "PH541"], 32, B(
    "b37565ad48 Sakurai & Napolitano, Modern Quantum Mechanics",
    ["0e91c77b13 Sakurai solutions manual"], ["3203751eeb Dirac, The Principles of Quantum Mechanics"]), level="II")
course("PH531", "Statistical mechanics (graduate)", ["PH371", "PH362"], 26, B("Pathria & Beale, Statistical Mechanics 3rd " + ACQ), level="II")
course("PH541", "Mathematical methods (graduate)", ["PH300"], 30, B(
    "7d3fe63932 Arfken, Weber & Harris, Mathematical Methods for Physicists 7th", ["448ae974b3 Arfken instructor's manual"]), level="II")
course("PH551", "General relativity (graduate)", ["PH501", "PH511"], 26, B(
    "Carroll, Spacetime and Geometry " + ACQ + " (free precursor: arXiv gr-qc/9712019 lecture notes)",
    [], ["05d9b495d6 Choquet-Bruhat, General Relativity and the Einstein Equations"]), level="II")
course("PH561", "Quantum field theory", ["PH521", "PH511"], 36, B(
    "Tong, Lectures on Quantum Field Theory (free: https://www.damtp.cam.ac.uk/user/tong/qft.html)",
    ["Schwartz, Quantum Field Theory and the Standard Model " + ACQ]), level="II")
course("PH571", "Condensed matter physics", ["PH521", "PH531"], 30, B(
    "Ashcroft & Mermin, Solid State Physics " + ACQ, ["932547ea63 Harrison, Solid State Theory (Dover)"]), level="II")
course("PH595", "Practice: qualifying-exam self-check", ["PH501", "PH511", "PH521", "PH531"], 6, B(
    "Lim (ed.), Major American Universities Ph.D. Qualifying Questions series (4776a751e8 QM, a94084b715 E&M, c9b3dec133 thermo, "
    "8ebb40b916 optics, d556c60ed7 atomic/nuclear)"), level="II")
course("PH598", "End-of-level conversation (Level II)", ["PH501", "PH521"], 1, B("list of works + conversation"), level="II")
course("PH599", "Capstone: reproduce a published result", ["PH501", "PH521"], 12, B("optional"), level="II")

# ---------------------------------------------------------------- engineering science (shared by mech-eng and unified-eng)
course("CH110", "Chemical principles for engineers", ["MA100"], 16, B(
    "705ba8c1cf OpenStax, Chemistry 2e (ch. 1-12 and 16-17; to confirm)",
    ["007dfde23b Cottrell, Matter VSI (grade A)"]))
course("ES150", "Engineering graphics and CAD (sketching, drawings, parametric and code CAD)", ["MA100"], 10, B(
    "843d235737 Gohde & Kintel, Programming with OpenSCAD",
    ["8eac849bc8 Measure Twice, Cut Once (grade A; measuring and drawing for makers)",
     "FreeCAD documentation and tutorials (free: https://wiki.freecad.org)"],
    ["08bb9f58a1 Fine Woodworking's SketchUp Guide (grade A)"]))
course("ES160", "Programming and numerical methods for engineers (Python)", ["MA141", "MA220"], 16, B(
    "505e09624e Hoffman, Numerical Methods for Engineers and Scientists 2nd",
    ["a56cacd7a7 OpenStax, Introduction to Python Programming"], ["071a589458 Press et al., Numerical Recipes"]))
course("ES211", "Statics", ["PH211", "MA141"], 18, B(
    "Baker & Haynes, Engineering Statics: Open and Interactive (free, CC BY-NC-SA: https://engineeringstatics.org; ch. 1-7)",
    ["fe2e3113f4 Hibbeler, Engineering Mechanics: Statics 14th (grade C: chapters only, for more problems from your copy)"],
    ["dfd4403935 Muir Wood, Civil Engineering VSI"]))
course("ES212", "Dynamics", ["ES211", "MA230"], 22, B(
    "411547e234 Hibbeler, Engineering Mechanics: Dynamics 14th (ch. 12-22)",
    ["4192f403ff Hibbeler Dynamics instructor's solutions manual"]))
course("ES213", "Mechanics of materials: stress, strain, axial, torsion, bending, buckling", ["ES211", "MA250"], 22, B(
    "8fdf44f6f1 Hibbeler, Mechanics of Materials 10th (grade C: read your copy; needs reconversion before lessons quote it)",
    ["Philpot, Mechanics of Materials " + ACQ + " (if reconversion fails)", "aa149abd72 Blockley, Structural Engineering VSI"]))
course("ES221", "Thermodynamics", ["PH211", "CH110", "MA141"], 20, B(
    "c4fa854434 Cengel, Introduction to Thermodynamics and Heat Transfer 2nd (thermodynamics chapters; to confirm)",
    ["26a7bb9d15 Atkins, The Laws of Thermodynamics VSI", "762ad02c0c Fermi, Thermodynamics"]))
course("ES231", "Fluid mechanics", ["ES212", "ES221", "MA230"], 26, B(
    "8b71085809 Cengel & Cimbala, Fluid Mechanics: Fundamentals and Applications (ch. 1-10; to confirm)"))
course("ES240", "Materials science and engineering", ["CH110", "PH211"], 20, B(
    "520676d836 Callister & Rethwisch, Materials Science and Engineering: An Introduction 8th",
    ["dbed43e44b Hall, Materials VSI (grade A)", "4111984f2e McLeish, Soft Matter VSI"]))
course("ES250", "Circuits and electronics for engineers", ["PH212", "MA250"], 16, B(
    "Kuphaldt, Lessons in Electric Circuits vols. I-III (free: https://www.ibiblio.org/kuphaldt/electricCircuits/)",
    ["d46e47e293 Horowitz & Hill, The Art of Electronics 3rd (grade A; ch. 1-2)"],
    skip=["e94b9176a5 Agarwal & Lang, Foundations of Analog and Digital Electronic Circuits: grade C copy"]))
course("ES340", "System dynamics and feedback control", ["ES212", "ES250", "MA250"], 22, B(
    "Astrom & Murray, Feedback Systems 2nd (book site: https://fbsbook.org)",
    ["Nise, Control Systems Engineering " + ACQ + " (more drill)"]))
course("ES370", "Heat transfer", ["ES221", "ES231"], 18, B(
    "c4fa854434 Cengel, Introduction to Thermodynamics and Heat Transfer 2nd (heat transfer chapters; to confirm)",
    ["Incropera et al., Fundamentals of Heat and Mass Transfer " + ACQ]))
course("ES380", "Practice: measurement and instrumentation lab (Arduino, phone sensors)", ["ES250", "MA414"], 8, B(
    "d46e47e293 Horowitz & Hill (measurement chapters)",
    ["a7c45d57dd Valvano, Introduction to Embedded Systems (grade A)"]))

# ---------------------------------------------------------------- mechanical engineering (depth)
course("ME310", "Kinematics and dynamics of machinery (linkages, cams, gears)", ["ES212", "ES150"], 18, B(
    "Norton, Design of Machinery " + ACQ, ["Uicker, Pennock & Shigley, Theory of Machines and Mechanisms " + ACQ]))
course("ME330", "Mechanical vibrations", ["ES212", "MA250", "MA220"], 18, B(
    "Rao, Mechanical Vibrations " + ACQ, ["913318cd5d King, Vibrations and Waves"]))
course("ME350", "Machine design (failure theories, fatigue, shafts, bearings, fasteners)", ["ES213", "ES240", "ME310"], 26, B(
    "Budynas & Nisbett, Shigley's Mechanical Engineering Design " + ACQ,
    ["c22369401a Avallone et al., Marks' Standard Handbook for Mechanical Engineers (grade A; reference)"],
    ["c0026d8da4 Machinery's Handbook 31 (grade C; reference from your copy)"]))
course("ME360", "Manufacturing processes (machining, casting, forming, additive)", ["ES240", "ES150"], 18, B(
    "Kalpakjian & Schmid, Manufacturing Engineering and Technology " + ACQ,
    ["b07551d382 OpenStax, Additive Manufacturing Essentials", "ed3f2a9abf Moltrecht, Machining for Hobbyists"],
    ["d9c944e630 Pye, The Nature and Art of Workmanship"]))
course("ME370", "Applied thermodynamics and energy systems (cycles, refrigeration, combustion)", ["ES221", "ES231"], 14, B(
    "Cengel & Boles, Thermodynamics: An Engineering Approach " + ACQ + " (cycles chapters)",
    ["46edc0772f Jenkins, Energy Systems VSI (grade A)"]))
course("ME385", "Practice: shop work (woodworking and machining as engineering)", ["ES150"], 8, B(
    "a5d96fb4c8 Wearing, The Essential Woodworker (grade A)", ["ed3f2a9abf Moltrecht, Machining for Hobbyists"]))
course("ME390", "Practice: FE Mechanical exam self-check", ["ES213", "ES231", "ES340"], 8, B(
    "f269980212 Lindeburg, FE Mechanical Practice Problems (grade A)",
    ["NCEES FE Reference Handbook (free with an NCEES account: https://ncees.org/exams/fe-exam/)"]))
course("ME410", "Finite element analysis", ["ES213", "ES160"], 18, B("Logan, A First Course in the Finite Element Method " + ACQ))
course("ME420", "Computational fluid dynamics", ["ES231", "ES160", "MA412"], 18, B(
    "c13063f4b1 Lohner, Applied Computational Fluid Dynamics Techniques 2nd"))
course("ME430", "Robotics", ["ES212", "ES340", "MA220"], 20, B(
    "Lynch & Park, Modern Robotics (free: https://hades.mech.northwestern.edu/index.php/Modern_Robotics)"))
course("ME440", "Biomechanics", ["ES212", "ES213"], 14, B(
    "7094714a5f Knudson, Fundamentals of Biomechanics 2nd (grade A)",
    ["98f51948ba Winter, Biomechanics and Motor Control of Human Movement"]),
    note="Meets the NASM-CPT and fitness books from the engineering side.")
course("ME190", "Breadth: what engineers do and how things get made", [], 6, B(
    "4fd15e571e Blockley, Engineering VSI (grade A)",
    ["af4f4570dd Hammack, The Things We Make (grade A)", "Petroski, To Engineer Is Human " + ACQ]))
course("ME398", "End-of-level conversation (Level I)", ["ME350", "ES370"], 1, B("list of works + conversation"))
course("ME399", "Capstone: design and build a mechanism", ["ME350"], 16, B("optional; to choose with you"))
course("ME501", "Continuum mechanics", ["ES213", "ES231", "MA230"], 24, B("Gonzalez & Stuart, A First Course in Continuum Mechanics " + ACQ), level="II")
course("ME511", "Advanced dynamics", ["ES212", "ME330"], 22, B("Greenwood, Principles of Dynamics 2nd " + ACQ), level="II")
course("ME521", "Advanced engineering thermodynamics", ["ME370"], 22, B("Bejan, Advanced Engineering Thermodynamics " + ACQ), level="II")
course("ME531", "Viscous fluid flow", ["ES231", "MA412"], 26, B("White, Viscous Fluid Flow " + ACQ), level="II")
course("ME541", "The finite element method", ["ES213", "ES160", "MA412"], 28, B("Hughes, The Finite Element Method (Dover) " + ACQ), level="II")
course("ME551", "Nonlinear control", ["ES340"], 24, B("Khalil, Nonlinear Systems 3rd " + ACQ), level="II")
course("ME561", "Engineering design optimization", ["ES160", "ME350"], 22, B(
    "Martins & Ning, Engineering Design Optimization (free online edition: https://mdobook.github.io)",
    ["942be832c7 Nocedal & Wright, Numerical Optimization", "59fb31351d Boyd & Vandenberghe, Convex Optimization"]), level="II")
course("ME595", "Practice: qualifying-exam self-check", ["ME501", "ME511", "ME531"], 6, B("past quals (to collect)"), level="II")
course("ME599", "Capstone: thesis-scale design or analysis project", ["ME501", "ME541"], 16, B("optional"), level="II")

# ---------------------------------------------------------------- unified engineering (breadth across disciplines)
course("UE202", "Signals and systems", ["ES250", "MA250"], 20, B(
    "Oppenheim, Willsky & Nawab, Signals and Systems 2nd " + ACQ,
    ["MIT OpenCourseWare 6.003 Signals and Systems notes (free: https://ocw.mit.edu)"]))
course("UE204", "Chemical process principles: material and energy balances, kinetics", ["CH110", "ES221"], 18, B(
    "Felder, Rousseau & Bullard, Elementary Principles of Chemical Processes " + ACQ))
course("UE309", "Applied electromagnetics: transmission lines, waves, antennas", ["PH212", "MA230"], 18, B(
    "3d37842821 Ulaby & Ravaioli, Fundamentals of Applied Electromagnetics"))
course("UE310", "Civil and structural engineering: how structures stand", ["ES213"], 12, B(
    "Gordon, Structures: Or Why Things Don't Fall Down " + ACQ,
    ["aa149abd72 Blockley, Structural Engineering VSI (grade A)", "dfd4403935 Muir Wood, Civil Engineering VSI (grade A)"]))
course("UE320", "Environmental and water engineering", ["UE204", "ES231"], 12, B(
    "Davis & Cornwell, Introduction to Environmental Engineering " + ACQ,
    ["67b9e15438 Fundamentals of Air Pollution (grade A)", "9a87e2b584 What We Know About Climate Change (grade A)"]))
course("UE330", "Electronics and embedded systems", ["ES250", "UE202"], 16, B(
    "d46e47e293 Horowitz & Hill, The Art of Electronics 3rd (grade A)",
    ["a7c45d57dd Valvano, Introduction to Embedded Systems (grade A)", "18ce1e24d2 Sedra & Smith, Microelectronic Circuits 7th"]))
course("UE335", "Digital systems and computer organization", ["ES250"], 14, B(
    "Harris & Harris, Digital Design and Computer Architecture " + ACQ,
    ["e2e4d85f05 Bryant & O'Hallaron, Computer Systems: A Programmer's Perspective"]))
course("UE340", "Aerospace engineering: flight, aerodynamics, propulsion, orbits", ["ES231", "ES221", "ES212"], 16, B(
    "Anderson, Introduction to Flight " + ACQ))
course("UE350", "Nuclear engineering", ["PH212", "ES221", "MA250"], 14, B(
    "9eab129029 Lamarsh & Baratta, Introduction to Nuclear Engineering 3rd",
    ["61c68f51f7 Irvine, Nuclear Power VSI (grade A)"]))
course("UE360", "Biomedical engineering: biomechanics and the body as a machine", ["ES212", "ES213"], 12, B(
    "7094714a5f Knudson, Fundamentals of Biomechanics 2nd (grade A)",
    ["528dbed011 OpenStax, Anatomy and Physiology (grade A; selected)", "98f51948ba Winter, Biomechanics and Motor Control"]))
course("UE370", "Industrial and systems engineering: operations research, quality, lean", ["MA414", "MA220"], 16, B(
    "Hillier & Lieberman, Introduction to Operations Research " + ACQ,
    ["77965156a6 Liker, The Toyota Way", "613ff03b6d Six-Hour Safety Culture (grade A)"]))
course("UE400", "Systems engineering and integrated design", ["ES340", "UE310", "UE330", "UE340"], 14, B(
    "NASA Systems Engineering Handbook, SP-2016-6105 Rev 2 (free: https://www.nasa.gov/reference/systems-engineering-handbook/)",
    ["4fd15e571e Blockley, Engineering VSI"]))
course("UE190", "Breadth: what engineering is (all the disciplines, and why things fail)", [], 6, B(
    "4fd15e571e Blockley, Engineering VSI (grade A)",
    ["af4f4570dd Hammack, The Things We Make (grade A)", "Petroski, To Engineer Is Human " + ACQ]))
course("UE195", "Breadth: engineering economics and ethics", ["MA141"], 8, B(
    "Newnan et al., Engineering Economic Analysis " + ACQ,
    ["bec5d9e593 OpenStax, Business Ethics (grade A)", "NSPE Code of Ethics (free: https://www.nspe.org/resources/ethics/code-ethics)"]))
course("UE395", "Practice: FE exam (Other Disciplines) self-check", ["ES231", "ES213", "ES340"], 8, B(
    "NCEES FE Reference Handbook (free with an NCEES account: https://ncees.org/exams/fe-exam/)",
    ["f269980212 Lindeburg, FE Mechanical Practice Problems (grade A; most topics overlap)"]))
course("UE398", "End-of-level conversation (Level I)", ["UE400"], 1, B("list of works + conversation"))
course("UE399", "Capstone: a multidisciplinary design-build", ["UE400"], 16, B("optional; to choose with you"))
course("UE501", "Multidisciplinary design optimization", ["ES160", "UE400"], 22, B(
    "Martins & Ning, Engineering Design Optimization (free online edition: https://mdobook.github.io)",
    ["942be832c7 Nocedal & Wright, Numerical Optimization"]), level="II")
course("UE511", "System architecture", ["UE400"], 18, B(
    "Crawley, Cameron & Selva, System Architecture: Strategy and Product Development for Complex Systems " + ACQ), level="II")
course("UE521", "Linear systems theory (state space)", ["ES340", "UE202", "MA220"], 22, B(
    "Hespanha, Linear Systems Theory 2nd " + ACQ), level="II")
course("UE531", "Reliability, risk and safety engineering", ["MA414", "UE400"], 16, B(
    "Leveson, Engineering a Safer World (free from MIT Press: https://mitpress.mit.edu/9780262533690/)"), level="II")
course("UE599", "Capstone: thesis-scale multidisciplinary project", ["UE501", "UE511"], 16, B("optional"), level="II")

# ---------------------------------------------------------------- music
OMT = "Open Music Theory (free: https://viva.pressbooks.pub/openmusictheory/)"
course("MU100", "Music fundamentals: notation, rhythm, scales, keys, intervals, triads", [], 16, B(
    "e73692249d Clendinning & Marvin, The Musician's Guide to Theory and Analysis (fundamentals chapters; grade A; to confirm)",
    ["d400c8d44a Royal Conservatory of Music, Theory Syllabus (grade A; graded rudiments checklist)", OMT],
    ["639b84c0f8 Taylor, The AB Guide to Music Theory vol. 1"]))
course("MU101", "Listening: how music works", [], 10, B(
    "60312d739e Copland, What to Listen for in Music (grade A)",
    ["806faa35e9 Forney & Machlis, The Enjoyment of Music (listening guides)"]))
course("MU110", "Aural skills I: sight-singing and dictation", ["MU100"], 18, B(
    "501f6a9e3d Ottman & Rogers, Music for Sight Singing (diatonic units)",
    ["48060ae852 Benward & Kolosick, Ear Training: A Technique for Listening"]),
    note="Short daily drills suit spaced review; needs the music-notation and ear-training widget from the wishlist.")
course("MU120", "Keyboard skills (functional piano)", ["MU100"], 20, B(
    "e213219df8 Faber, Adult Piano Adventures All-in-One Book 1",
    ["74f6e6593f Faber, Accelerated Piano Adventures for the Older Beginner"],
    ["e8feff6f46 Palmer et al., The Complete Book of Scales, Chords, Arpeggios and Cadences (grade C; your copy)"]))
course("MU200", "Theory II: diatonic harmony and voice leading", ["MU100"], 24, B(
    "e73692249d Clendinning & Marvin (diatonic harmony chapters; to confirm)",
    ["a0290b01c4 Aldwell, Schachter & Cadwallader, Harmony and Voice Leading", "14e41cafd9 Kostka, Payne & Almen, Tonal Harmony"],
    ["a8a79b9404 Levy, A Theory of Harmony (grade A; the theory behind the rules)"],
    ["f77cae55dc Kostka older edition: grade C copy (use 14e41cafd9)"]))
course("MU210", "Aural skills II: chromatic sight-singing, harmonic dictation", ["MU110", "MU200"], 18, B(
    "501f6a9e3d Ottman & Rogers, Music for Sight Singing (chromatic units)", ["48060ae852 Benward & Kolosick"]))
course("MU300", "Theory III: chromatic harmony, modulation and form", ["MU200"], 24, B(
    "e73692249d Clendinning & Marvin (chromatic harmony and form chapters; to confirm)",
    ["de3227ca92 Laitz, The Complete Musician", "14e41cafd9 Kostka, Payne & Almen"]))
course("MU310", "Counterpoint: species and 18th-century style", ["MU200"], 16, B(
    "Fux, The Study of Counterpoint (Gradus ad Parnassum, trans. Mann) " + ACQ,
    [OMT + " (counterpoint chapters)",
     "28f93f91f0 Gauldin, A Practical Approach to 18th-Century Counterpoint (grade C: exercises from your copy)"]))
course("MU320", "Theory IV: post-tonal music (sets, serialism, minimalism)", ["MU300"], 20, B(
    "e73692249d Clendinning & Marvin (post-tonal chapters; to confirm)",
    ["Straus, Introduction to Post-Tonal Theory " + ACQ]))
course("MU231", "Music history I: antiquity to Bach", ["MU101"], 24, B(
    "Burkholder, Grout & Palisca, A History of Western Music " + ACQ + " (with the Norton Anthology of Western Music)",
    ["da9d880141 Norton Introduction to Music History anthology (grade C: scores from your copy)"]))
course("MU232", "Music history II: Haydn to Mahler", ["MU231"], 24, B(
    "Burkholder, Grout & Palisca, A History of Western Music " + ACQ))
course("MU233", "Music history III: the twentieth century to now", ["MU232"], 20, B(
    "e1b23ab193 Ross, The Rest Is Noise (grade A)",
    ["5ac11c0dc7 Morgan (ed.), Anthology of Twentieth-Century Music (grade C: scores from your copy)"]))
course("MU240", "Hindustani classical music and world music", ["MU100"], 16, B(
    "732f4b1550 Bakshi, 101 Raga-s for the 21st Century and Beyond (grade A)",
    ["6c644b528a Sharma, How to Play Sitar", "Bor (ed.), The Raga Guide " + ACQ]),
    note="Meets the Indian History major (music at the Mughal courts, the bhakti poets).")
course("MU250", "Jazz theory and improvisation", ["MU200"], 20, B(
    "a435b20858 Terefenko, Jazz Theory: From Basic to Advanced Study 2nd",
    ["dd82cef0ea The Great American Songbook: Jazz (tunes to analyze)"]))
course("MU260", "Songwriting and lyric writing", ["MU200"], 14, B(
    "649d3cf76e Davis, The Craft of Lyric Writing (grade A)",
    ["0ce53e3d46 McCandless & McIntyre, The Craft of Contemporary Commercial Music"]))
course("MU270", "Orchestration", ["MU300"], 18, B("Adler, The Study of Orchestration " + ACQ))
course("MU280", "Composition: short pieces in notation software", ["MU300"], 16, B(
    "MuseScore (free notation software: https://musescore.org) + Clendinning & Marvin composition exercises"))
course("MU190", "Breadth: the physics of sound and hearing", [], 8, B(
    "8e3ad00192 Goldsmith, Sound VSI (grade A)", ["8f4b3a9ae8 Walmsley, Light VSI (for the wave ideas)"]),
    note="Meets Physics PH214 (waves).")
course("MU290", "Practice: your instrument (applied lessons, with a teacher if possible)", ["MU100"], 20, B(
    "your instrument's method: guitar, db709588b0 Hal Leonard Guitar Method (complete edition)",
    ["533fd56a14 Guitar Head, Memorize the Fretboard (grade A)",
     "f7b82990ad Shearer, Classic Guitar Technique vol. 1 (grade C: your copy; if you go classical)",
     "piano, if you return to it: e213219df8 Faber Adult Piano Adventures, then the ABRSM grade books"]))
course("MU398", "End-of-level conversation (Level I)", ["MU320", "MU233"], 1, B("list of works + conversation"))
course("MU399", "Capstone: an analysis paper or a short recital", ["MU320", "MU233"], 12, B("optional"))
course("MU501", "Schenkerian analysis", ["MU300", "MU310"], 24, B(
    "Cadwallader & Gagne, Analysis of Tonal Music: A Schenkerian Approach " + ACQ,
    ["a0290b01c4 Aldwell & Schachter (Schenkerian roots)"]), level="II")
course("MU511", "Post-tonal theory (graduate)", ["MU320"], 22, B("Straus, Introduction to Post-Tonal Theory " + ACQ), level="II")
course("MU521", "Musicology: reading music history critically", ["MU233"], 24, B(
    "Taruskin, The Oxford History of Western Music (selected chapters) " + ACQ), level="II")
course("MU531", "Ethnomusicology", ["MU240", "MU233"], 20, B("Nettl, The Study of Ethnomusicology " + ACQ), level="II")
course("MU595", "Practice: graduate entrance diagnostic (theory, aural, history)", ["MU501", "MU521"], 4, B(
    "past diagnostic exams (to collect)"), level="II")
course("MU599", "Capstone: a thesis-scale analysis or composition", ["MU501"], 16, B("optional"), level="II")

# ---------------------------------------------------------------- English
# A reading major (notes/major-design.md, "Reading majors"): most sittings are reading days (one ~25-minute block) with a seminar
# every few days. est_lessons uses the same unit as every other major (one lesson = two blocks), so 30 lessons ≈ 60 sittings.
course("EN015", "Rhetoric and composition: the academic essay", [], 12, B(
    "ed156636dd Zinsser, On Writing Well (grade A)",
    ["29aad591c6 Strunk & White, The Elements of Style 4th (grade A)", "009f44376d Toye, Rhetoric VSI (grade A)",
     "Graff & Birkenstein, They Say / I Say " + ACQ]))
course("EN100", "How to read literature: an introduction to literary study", [], 16, B(
    "86cc8dfe39 Foster, How to Read Literature Like a Professor 2nd (grade A)",
    ["68dc21333b Culler, Literary Theory VSI (grade A)", "ddb25171a8 Adler & Van Doren, How to Read a Book (grade A)",
     "24529ef5be Joyce, Dubliners (the stories practiced on)"]))
course("EN130", "Poetry: form, meter and close reading", ["EN100"], 18, B(
    "db6c479d03 Ferguson, Salter & Stallworthy (eds.), The Norton Anthology of Poetry",
    ["2a5cb957c3 O'Donoghue, Poetry VSI (grade A)", "Fussell, Poetic Meter and Poetic Form " + ACQ]))
course("EN201", "British literature I: Beowulf to the Restoration", ["EN100"], 30, B(
    "Greenblatt (ed.), The Norton Anthology of English Literature vol. 1 (Middle Ages to Restoration) " + ACQ,
    ["afded2e0b5 Beowulf: Old English Text, Translations and Dual Text (grade A)", "1172ccd4a1 Wallace, Chaucer VSI",
     "7a8435a997 Treharne, Medieval Literature VSI", "474dc72906 The Complete Works of William Shakespeare (grade A)"]))
course("EN202", "British literature II: the Romantics to the present", ["EN100"], 30, B(
    "dd0088d6df Greenblatt (ed.), The Norton Anthology of English Literature vol. 2 (grade A)",
    ["c1b4282699 Ferber, Romanticism VSI", "4d6765aa21 Hartley, Charles Dickens VSI", "d5cf574ff7 MacCabe, James Joyce VSI"]))
course("EN211", "American literature I: beginnings to 1865", ["EN100"], 24, B(
    "ad622c35f0 Levine (ed.), The Norton Anthology of American Literature (vols. A-B; grade A)",
    [], ["bfbf59da94 Melville, Moby-Dick (whole, optional)"]))
course("EN212", "American literature II: 1865 to the present", ["EN100"], 24, B(
    "2057305a99 Levine (ed.), The Norton Anthology of American Literature, vols. C-E (grade A)",
    ["7003a0782e Ellison, Invisible Man", "3ab366d4fe Faulkner, The Sound and the Fury", "b45a47fec5 Caplan, American Poetry VSI"]))
course("EN220", "Shakespeare: eight plays and the sonnets", ["EN100"], 30, B(
    "474dc72906 The Complete Works of William Shakespeare (grade A)",
    ["16f09c51b6 Wells, Shakespeare's Tragedies VSI", "3c99a223f7 van Es, Shakespeare's Comedies VSI",
     "Garber, Shakespeare After All " + ACQ]))
course("EN230", "The novel: Cervantes to Woolf", ["EN100"], 36, B(
    "88c7e9ae14 Austen, Complete Works (Pride and Prejudice; grade A)",
    ["9c33a3ab3b Cervantes, Don Quixote (Grossman; part I)", "00a65b8d86 Eliot, Middlemarch",
     "5705dee3e9 Woolf, To the Lighthouse", "Watt, The Rise of the Novel " + ACQ]),
    note="Middlemarch and To the Lighthouse also appear in Critical Theory: one reading counts for both.")
course("EN300", "Literary theory and criticism", ["EN130"], 20, B(
    "68dc21333b Culler, Literary Theory VSI + face941c2e Norton Anthology of Theory and Criticism (selections; grade A)",
    ["Tyson, Critical Theory Today (in the library; the Critical Theory major's main book)"]),
    note="Equivalent to the Critical Theory major's orientation and close-reading courses (CT100, CT201): finishing either counts.")
course("EN310", "The English language: its history and how it works", ["EN100"], 16, B(
    "d953c2c693 Horobin, The English Language VSI (grade A)",
    ["37cdcc8fa1 The Earliest English: An Introduction to Old English Language (grade A)",
     "fd4ffb9c9c Matthews, Linguistics VSI", "447856339f Edwards, Sociolinguistics VSI"]))
course("EN320", "World literature in translation: Homer to Kafka", ["EN100"], 30, B(
    "6418dc4bea Homer, The Odyssey (grade A)",
    ["8af5d41030 Dante, The Divine Comedy (Inferno)", "7070af1518 Voltaire, Candide", "ba765724a5 Kafka, The Trial",
     "03b989e36d Graziosi, Homer VSI", "f2e3b6de81 Hainsworth & Robey, Dante VSI"]))
course("EN330", "Postcolonial and Indian literature in English", ["EN100"], 24, B(
    "a2a924addb Rushdie, Midnight's Children (grade A)",
    ["f6b767de9a Achebe, The African Trilogy (Things Fall Apart)", "30b0d85a0f Adiga, The White Tiger",
     "8b30ac33e8 Sahgal, Rich Like Us"]),
    note="Meets Critical Theory (postcolonial lens) and Indian History.")
course("EN400", "Senior seminar: one author in depth (default: Joyce)", ["EN202", "EN300"], 30, B(
    "6e7b60467d Joyce, Ulysses (grade A)",
    ["24529ef5be Joyce, Dubliners", "d5cf574ff7 MacCabe, James Joyce VSI", "Gifford, Ulysses Annotated " + ACQ]),
    note="Author is your choice; Joyce is the default because the library has him whole.")
course("EN340", "Creative writing: fiction", ["EN015"], 16, B(
    "f4c42b4190 King, On Writing (grade A)",
    ["7e0b635d56 The Elements of Fiction Writing: Characters and Viewpoint (grade A)", "7e1c299bc3 Bell, Refuse to Be Done (grade A)"]))
course("EN341", "Dramatic writing and screenwriting", ["EN015"], 14, B(
    "216adb3f8c Egri, The Art of Dramatic Writing (grade A)",
    ["f18d3d0024 Field, Screenplay (grade A)", "ae4c201b31 Snyder, Save the Cat! (grade A)"]))
course("EN342", "Advanced nonfiction and technical writing", ["EN015"], 12, B(
    "f959bb5a1c Zinsser, Writing to Learn (grade A)", ["b291b01109 Minto, The Pyramid Principle"]),
    note="Feeds the Engineering career major's design-doc work.")
course("EN350", "The Russian novel", ["EN230"], 24, B(
    "f6dbd55b62 Dostoevsky, The Brothers Karamazov (grade A)", ["438c0ee90a Tolstoy, War and Peace", "e0870fea4a Knapp, Tolstoy VSI"]))
course("EN360", "Classical literature: Greek tragedy, Ovid, epic", ["EN100"], 18, B(
    "22ee27b70d Allan, Classical Literature VSI (grade A)",
    ["6cb2ad9fee Homer, The Iliad", "fc35a1e99e Ovid, Erotic Poems", "53a669da9a Sophocles, The Oedipus Plays (study guide only)"]))
course("EN370", "Dystopian fiction", ["EN100"], 12, B(
    "5876f05a9c Orwell, 1984 (grade A)", ["65357a2857 Huxley, Brave New World", "0492b02901 Burgess, A Clockwork Orange"]))
course("EN190", "Breadth: writing systems and the book", [], 6, B(
    "b14ef2d5a0 Robinson, Writing and Script VSI (grade A)", ["561e96a88d Anderson, Languages VSI"]))
course("EN398", "End-of-level conversation (Level I)", ["EN400"], 1, B("list of works + conversation"))
course("EN399", "Capstone: a 20-page critical essay (honors thesis)", ["EN400"], 16, B("optional; topic with you"))
course("EN501", "Graduate theory and methods", ["EN300"], 30, B(
    "face941c2e Norton Anthology of Theory and Criticism (whole; grade A)", ["Rivkin & Ryan (eds.), Literary Theory: An Anthology " + ACQ]),
    level="II")
course("EN511", "Old English: Beowulf in the original", ["EN310", "EN201"], 30, B(
    "Mitchell & Robinson, A Guide to Old English " + ACQ,
    ["afded2e0b5 Beowulf: Old English Text, Translations and Dual Text", "37cdcc8fa1 The Earliest English"]), level="II")
course("EN521", "Chaucer in Middle English", ["EN201", "EN310"], 26, B("Benson (ed.), The Riverside Chaucer " + ACQ), level="II")
course("EN531", "Milton", ["EN201"], 24, B("Milton, Paradise Lost (Norton Critical Edition) " + ACQ), level="II")
course("EN541", "Modernism seminar", ["EN400"], 28, B(
    "5705dee3e9 Woolf, To the Lighthouse", ["3ab366d4fe Faulkner, The Sound and the Fury", "6e7b60467d Joyce, Ulysses"]), level="II")
course("EN595", "Practice: a comprehensive-exam reading list (100 works) and self-check", ["EN501"], 10, B(
    "a list built with you from the anthologies read"), level="II")
course("EN599", "Capstone: a publishable-length essay", ["EN501"], 16, B("optional"), level="II")

# ---------------------------------------------------------------- majors
# group per course in this major (default core). Order = display order.
MAJORS = {
    "math": {
        "name": "Mathematics",
        "core": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250", "MA311", "MA312", "MA403", "MA414",
                 "MA435", "MA436", "MA437", "MA421", "MA429",
                 "MA501", "MA511", "MA521", "MA531", "MA541", "MA551", "MA561"],
        "elective": ["MA412", "MA455", "MA360", "MA465", "MA417", "MA470", "MA480", "MA457"],
        "breadth": ["MA190"], "practice": ["MA390", "MA595"], "colloquium": ["MA398", "MA598"], "capstone": ["MA399", "MA599"],
        "entry": {
            "credited": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250", "MA311", "MA312", "MA414", "MA421",
                         "MA403", "MA436", "MA455"],
            "maybe": ["MA417"],
            "start": ["MA435", "MA429", "MA412"],
            "basis": "Penn State BS Mathematics common core (MATH 140, 141, 220, 230, 250/251, 311W, 312, 414, 415). The option "
                     "you took decides the 'maybe' row: General adds MATH 403 and one of 435/436; Graduate Study adds 403, 404, 421, "
                     "429, 435, 436; Applied adds 403, 412, 436, 455. Course ids here follow Penn State numbers on purpose. You took the Applied option (403, 412, 436, 455 "
                     "required) plus complex analysis (421) and Numerical Analysis II (456, inside MA455's book), so those are credited, except 412 (PDEs), which you want to retake. Applied doesn't require 435, so abstract "
                     "algebra starts at MA435. MA417 is 'maybe': MATH 417 was one of Applied's elective choices.",
        },
    },
    "physics": {
        "name": "Physics",
        "core": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250",
                 "PH211", "PH212", "PH213", "PH214", "PH237", "PH300", "PH341", "PH351", "PH352", "PH361", "PH362", "PH371",
                 "PH501", "PH511", "PH521", "PH531", "PH541", "PH551", "PH561", "PH571"],
        "elective": ["PH380", "PH391", "PH393", "PH394", "PH395", "PH396", "MA412"],
        "breadth": ["PH190"], "practice": ["PH390", "PH595"], "colloquium": ["PH398", "PH598"], "capstone": ["PH399", "PH599"],
        "entry": {
            "credited": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250", "PH211", "PH212", "PH213", "PH214",
                         "PH237", "PH341", "PH351", "PH352", "PH371"],
            "maybe": ["PH300"],
            "start": ["PH361", "MA412"],
            "basis": "Penn State BS Computer Engineering requires PHYS 211 (mechanics), 212 (E&M) and 214 (waves and quantum); "
                     "the math degree covers the calculus, linear algebra and ODE rows. PHYS 213 (fluids, thermal) was not required. "
                     "Boas (PH300) becomes a look-up shelf rather than a course. You also took modern physics, classical mechanics, "
                     "electrodynamics and thermal physics (physics department), so PH237, PH341, PH351, PH352 and PH371 are credited "
                     "(PH213 with them). Penn State's PHYS 400 (Griffiths) runs through potentials and fields and an introduction "
                     "to radiation, i.e. both E&M courses here; only Griffiths ch. 11-12 in depth may be new.",
        },
    },
    "mech-eng": {
        "name": "Mechanical Engineering",
        "core": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250", "MA414", "PH211", "PH212", "CH110",
                 "ES150", "ES160", "ES211", "ES212", "ES213", "ES221", "ES231", "ES240", "ES250", "ES340", "ES370",
                 "ME310", "ME330", "ME350", "ME360", "ME370", "MA412",
                 "ME501", "ME511", "ME521", "ME531", "ME541", "ME551", "ME561"],
        "elective": ["ME410", "ME420", "ME430", "ME440"],
        "breadth": ["ME190"], "practice": ["ES380", "ME385", "ME390", "ME595"], "colloquium": ["ME398"],
        "capstone": ["ME399", "ME599"],
        "entry": {
            "credited": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250", "MA414", "PH211", "PH212", "CH110", "ES250"],
            "maybe": ["ES160"],
            "start": ["ES211", "ES221", "ES240", "ES150", "MA412"],
            "basis": "Penn State BS Computer Engineering: MATH 140/141/220/231/250, PHYS 211/212, CHEM 110, EE 210 (circuits), "
                     "STAT 418 or 414 (probability), CMPSC 121/122 (programming). No engineering mechanics (EMCH) course, so Statics is "
                     "the real start. EE 353 (signals and systems) covers the transform half of ES340, not the feedback half.",
        },
    },
    "unified-eng": {
        "name": "Unified Engineering",
        "core": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250", "MA414", "PH211", "PH212", "CH110", "ES150", "ES160",
                 "ES211", "ES240", "ES250", "ES221",
                 "ES212", "ES213", "ES231", "UE202",
                 "ES340", "ES370", "UE204", "UE309",
                 "UE310", "UE320", "UE330", "UE335", "UE340", "UE350", "UE360", "UE370", "ME360",
                 "UE400",
                 "UE501", "UE511", "UE521", "UE531"],
        "elective": ["ME310", "ME330", "ME350", "ME410", "ME430", "MA412"],
        "breadth": ["UE190", "UE195"], "practice": ["ES380", "UE395", "ME385"], "colloquium": ["UE398"],
        "capstone": ["UE399", "UE599"],
        "terms": {
            "Base": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250", "MA414", "PH211", "PH212", "CH110", "ES150", "ES160"],
            "Unified I": ["ES211", "ES240", "ES250", "ES221"],
            "Unified II": ["ES212", "ES213", "ES231", "UE202"],
            "Unified III": ["ES340", "ES370", "UE204", "UE309"],
            "Discipline tour": ["UE310", "UE320", "UE330", "UE335", "UE340", "UE350", "UE360", "UE370", "ME360"],
            "Integration": ["UE400"],
        },
        "entry": {
            "credited": ["MA100", "MA140", "MA141", "MA220", "MA230", "MA250", "MA414", "PH211", "PH212", "CH110",
                         "ES250", "UE202", "UE335"],
            "maybe": ["ES160", "UE330"],
            "start": ["ES211", "ES240", "ES221", "ES150"],
            "basis": "Penn State BS Computer Engineering: the math and physics base, CHEM 110, EE 210 (circuits), EE 353 (signals and "
                     "systems), CMPEN 270/331 and CMPSC 311/473-level systems courses (digital systems), EE 310 (electronic circuit "
                     "design; the embedded half may be new). So Unified I runs three of its four courses for you.",
        },
    },
    "music": {
        "name": "Music",
        "core": ["MU100", "MU101", "MU110", "MU120", "MU200", "MU210", "MU300", "MU310", "MU320", "MU231", "MU232", "MU233",
                 "MU240", "MU501", "MU511", "MU521", "MU531"],
        "elective": ["MU250", "MU260", "MU270", "MU280"],
        "breadth": ["MU190"], "practice": ["MU290", "MU595"], "colloquium": ["MU398"], "capstone": ["MU399", "MU599"],
        "entry": {
            "credited": [],
            "maybe": ["MU101", "MU120"],
            "start": ["MU100"],
            "basis": "You play guitar, used to play piano and read basic notation; no music courses on either transcript. "
                     "MU100 is the start but runs as a fast pass (skip what you know; keys, intervals and triads are where it "
                     "slows down). MU120 keyboard is 'maybe' (a refresher for a former pianist). MU101 listening is 'maybe'. "
                     "Guitar is the instrument for MU290 practice.",
        },
    },
    "english": {
        "name": "English",
        "core": ["EN015", "EN100", "EN130", "EN201", "EN202", "EN211", "EN212", "EN220", "EN230", "EN300", "EN310", "EN320",
                 "EN330", "EN400", "EN501", "EN511", "EN521", "EN531", "EN541"],
        "elective": ["EN340", "EN341", "EN342", "EN350", "EN360", "EN370"],
        "breadth": ["EN190"], "practice": ["EN595"], "colloquium": ["EN398"], "capstone": ["EN399", "EN599"],
        "entry": {
            "credited": ["EN015"],
            "maybe": [],
            "start": ["EN100"],
            "basis": "Both Penn State degrees required first-year composition (ENGL 15) and the CompE degree ENGL 202C (technical "
                     "writing), so EN015 is credited. No college literature courses. AP Literature in high school (no exam) "
                     "gives no credit, but it covers much of EN100 and some of EN130, so expect both to go quickly.",
        },
    }
}
GROUP_KEYS = ["core", "elective", "breadth", "practice", "colloquium", "capstone"]


def build(slug):
    m = MAJORS[slug]
    ids = [i for g in GROUP_KEYS for i in m.get(g, [])]
    group = {i: g for g in GROUP_KEYS for i in m.get(g, [])}
    owners = {cid: [s for s in MAJORS if cid in [i for g in GROUP_KEYS for i in MAJORS[s].get(g, [])]] for cid in ids}
    courses = []
    for cid in ids:
        c = dict(C[cid])
        missing = [r for r in c["requires"] if r not in group]
        if missing:
            raise SystemExit(f"{slug}/{cid}: requires {missing}, not in this major")
        if group[cid] == "core":
            bad = [r for r in c["requires"] if group[r] != "core"]
            if bad:
                raise SystemExit(f"{slug}/{cid}: core course requires optional {bad}")
        others = [MAJORS[s]["name"] for s in owners[cid] if s != slug]
        notes = [n for n in [c.pop("note")] if n]
        if others:
            notes.insert(0, "Cross-listed with " + ", ".join(others) + ": finishing it in any of them counts here.")
        out = {"id": cid, "title": c["title"], "status": "later", "requires": c["requires"], "group": group[cid],
               "level": c["level"], "est_lessons": c["est_lessons"], "books": c["books"]}
        if notes:
            out["note"] = " ".join(notes)
        courses.append(out)
    cur = {
        "major": slug,
        "program": f"topics/{slug}/PROGRAM.md",
        "generated_by": "scripts/build_majors.py (edit there, not here)",
        "rules": [
            "Designed 2026-10-08 and parked: written as if starting from high school, with your real entry point in entry_points.",
            "No pretests (your call, 2026-10-08): credited courses count from your degrees; 'maybe' courses are yours to skim or skip; "
            "you look things up when a gap shows.",
            "A course shared with another major (same id) is one course: finishing it anywhere counts everywhere.",
        ],
        "entry_points": {"high_school": [c["id"] for c in courses if not c["requires"] and c["group"] == "core"], **m["entry"]},
        "courses": courses,
    }
    if "terms" in m:
        cur["terms"] = m["terms"]
    return cur


def stats():
    print("| Major | Level I core lessons from high school | from your entry point (credited removed; 'maybe' kept) | weeks from entry, half subject (1 lesson/wk) | full subject (2/wk) | Level II core | Optional extras |")
    print("|---|---|---|---|---|---|---|")
    for slug, m in MAJORS.items():
        cur = build(slug)
        cs = cur["courses"]
        core1 = [c for c in cs if c["group"] == "core" and c["level"] == "I"]
        n_hs = sum(c["est_lessons"] for c in core1)
        n_you = sum(c["est_lessons"] for c in core1 if c["id"] not in m["entry"]["credited"])
        n2 = sum(c["est_lessons"] for c in cs if c["group"] == "core" and c["level"] == "II")
        opt = sum(c["est_lessons"] for c in cs if c["group"] != "core")
        print(f"| {m['name']} | {n_hs} ({len(core1)} courses) | {n_you} | {n_you} (≈{n_you / 52:.1f} yr) | {-(-n_you // 2)} (≈{n_you / 104:.1f} yr) | {n2} | {opt} |")
    allI = {c for s, m in MAJORS.items() for c in m["core"] if C[c]["level"] == "I"}
    cred = {c for m in MAJORS.values() for c in m["entry"]["credited"]}
    print(f"\nAll Level I cores together, each shared course counted once: {sum(C[c]['est_lessons'] for c in allI)} lessons "
          f"from high school, {sum(C[c]['est_lessons'] for c in allI - cred)} from your entry points.")


def main():
    if "--stats" in sys.argv:
        stats()
        return
    for slug in MAJORS:
        p = ROOT / "topics" / slug / "curriculum.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(build(slug), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
