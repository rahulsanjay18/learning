# Books Claude has asked for

I'll get these myself, add them to the server, then regrade + reindex.
Last reviewed 2026-10-06. Find what's new on the server with `python3 scripts/books.py new` (needs the redeployed book server).
Every "missing" line was also checked on the server by title on 2026-10-06 (one request each).

## Games (G101 chess, G150 strategy, design)
- _Arms and Influence_ — Thomas C. Schelling — for: military-strategy / deterrence & coercion — why: the classic theory of coercion — status: got (4bdcba34b3, grade A, 2026-10-06; on the server, not yet in MANIFEST.csv)
- _Is Your Move Safe?_ — Dan Heisman — for: chess / lesson 0001 is-it-safe — why: the definitive treatment of the safety-check skill for improving adults — status: missing (not on server 2026-10-06)
- _A Guide to Chess Improvement: The Best of Novice Nook_ — Dan Heisman — for: chess thinking process — why: award-winning column for adult improvers, matches the learner's level — status: missing
- _Makers of Modern Strategy from Machiavelli to the Nuclear Age_ — Peter Paret (ed.) — for: military-strategy / theorists — why: standard survey of the theorists the mission names — status: got (6979109f6e, grade A, 2026-10-06; on the server, not yet in MANIFEST.csv)
- _The Art of Wargaming_ — Peter Perla — for: military-strategy / wargaming — why: standard text on professional and hobby wargaming — status: got (eb72110b76, grade A, 2026-10-06; on the server, not yet in MANIFEST.csv)
- _The First Punic War: A Military History_ — J. F. Lazenby — for: military-strategy / First Punic War analysis — why: standard modern military history of the war; checks Polybius — status: missing
- _An Introduction to Game Theory_ — Martin J. Osborne (OUP, 2003) — for: games / classical game theory course — why: the real textbook PROGRAM.md's gap list asks for; light on math prerequisites, covers extensive and repeated games — status: missing
- _Characteristics of Games_ — Elias, Garfield & Gutschera — for: games / design notebook — why: the most analytical of the design classics (balance, first-player advantage, luck vs. skill), fits the 3D-chess project — status: missing
- _Rules of Play_ — Salen & Zimmerman — for: games / design — why: the standard game-design theory text — status: missing

## Statistics (full list with reasons: topics/statistics/PROGRAM.md §0)
- _Trustworthy Online Controlled Experiments_ — Kohavi, Tang & Xu — for: S320 (soonest) — why: the A/B-testing reference; S150's examples already lean that way — status: missing
- _Introduction to Probability_ — Blitzstein & Hwang — for: probability review — why: free from the authors — status: missing
- _Bayesian Data Analysis_, 3rd ed. — Gelman et al. — for: Bayesian course — why: free from the authors — status: missing
- _Causal Inference: What If_ — Hernán & Robins — for: causal course — why: free from the authors — status: missing
- _Elements of Statistical Learning_ and _Introduction to Statistical Learning_ — for: ML-flavoured stats — why: free from the authors — status: needs reconversion (e34f922e7e, 707f288ce8: garbled, grade C)
- _Understanding Analysis_ — Abbott — for: S500 — why: equations unusable at grade B — status: needs reconversion (1f0fdaeaa7)
- _Forecasting: Principles and Practice_ — Hyndman & Athanasopoulos — for: time series — why: equations unusable at grade B; FPP3 is free online — status: needs reconversion (f85506d7bf)

## Indian History
- _A History of Ancient and Early Medieval India_, 2nd ed. — Upinder Singh (Pearson, 2024) — for: IH201 Ancient India — why: the standard deep text for the period, built around primary sources and archaeology (fits the "one source in your hands" lesson design) — status: missing
- _The Economic History of India, 1857–2010_, 4th ed. — Tirthankar Roy (OUP, 2020) — for: IH330 economic history (the "economic history of India" PROGRAM.md asks for); links to Economics — status: got (8b573d9c6b, grade A; on the server, not yet in MANIFEST.csv; found 2026-10-08)

## Fitness and art (parked)
- _NASM Essentials of Personal Fitness Training, 7th ed._ — NASM (Jones & Bartlett) — for: nasm-cpt / all lessons — why: the textbook the current exam is written from; collection only has the 4th ed. (2012) — status: missing
- _Pixel Logic: A Guide to Pixel Art_ — Michael Azzi — for: pixel-art / all early lessons — why: the most-recommended visual beginner guide (lines, clusters, palettes, shading) — status: missing

## Engineering career: C and C++ (topics/eng/, CP courses)
- _C++ Concurrency in Action_, 2nd ed. — Anthony Williams (Manning, 2019) — for: CP204 Concurrency (Level I core primary) — why: the standard book on C++ threads, memory model, atomics — status: missing (buy)
- _The Linux Programming Interface_ — Michael Kerrisk (No Starch, 2010) — for: CP310 systems elective — status: missing
- _A Tour of C++_, 3rd ed. — Bjarne Stroustrup (2022) — for: CP201/CP203, the C++20 delta over C++ Primer 5e — status: missing
- _Effective C_, 2nd ed. — Robert Seacord (No Starch, 2024) — for: CP101 (would become primary; C23) — status: missing
- _Modern C_, 3rd ed. — Jens Gustedt (Manning, 2025) — for: CP101, C23 update of the 2018 draft in collection (030e99498b) — status: missing
- _Game Engine Architecture_, 3rd ed. — Jason Gregory (CRC, 2018) — for: CP330 elective — status: missing
- _C++ Templates: The Complete Guide_, 2nd ed. (2017) and Iglberger, _C++ Software Design_ (2022) — for: Level II CP401/CP402 — status: missing (collection has only the 2002 1st ed. of Templates, 1062457b20)

## Engineering career: staff (topics/eng/, SE courses)
- _The Staff Engineer's Path_ — Tanya Reilly (O'Reilly, 2022) — for: SE101/SE140/SE150/SE160, the backbone — status: owned by the learner (2026-10-07), not on the book server yet
- _A Philosophy of Software Design_, 2nd ed. — John Ousterhout (2021) — for: SE130 — status: missing
- _An Elegant Puzzle_ — Will Larson (2019) — for: SE150 strategy — status: missing
- _System Design Interview_ vol. 1–2 — Alex Xu; _Machine Learning System Design Interview_ — Aminian & Xu — for: SE120/SE160 — status: missing
- _Good Strategy/Bad Strategy_ — Richard Rumelt; _Team Topologies_ — Skelton & Pais — for: SE150 (nice to have) — status: missing

## Engineering career: career extras (topics/eng/, CR courses)
- SOA Exam P study manual (ACTEX or Coaching Actuaries) — for: CR325 actuary, the main fallback's first exam — status: missing (wanted first)
- A USPTO patent-bar prep course or book — for: CR327 patent agent — status: missing (later)
- _AI Engineering_ — Chip Huyen (O'Reilly, 2025) — for: CR120/CR140 boosters — status: missing
- _System Design Interview_ vol. 1–2 — Alex Xu — for: CR150 interviewing — status: missing
- _Trading and Exchanges_ — Larry Harris — for: CR310 quant developer (on hold: remote-only) — status: got (ae0bc03662, grade A; on the server, not yet in MANIFEST.csv; found 2026-10-08)

AWS ML certification (topics/eng/, AW courses): MLA-C02 exam guide (free); your 2024 Solutions Architect course (you have it).

## Added 2026-10-08 for the course syllabi (topics/<major>/syllabi/)
Ordered by when each is first needed. Every syllabus assumes these are available; if one can't be found as a convertible copy, say so
and the syllabus gets an alternative. All status: missing (checked on the server by title, 2026-10-08) unless noted.

**Free from the authors (please download):**
- _Probability: Theory and Examples_, 5th ed. — Durrett — for: S501–S502
- _Computer Age Statistical Inference_ — Efron & Hastie — for: S330, S511, S570
- _Bandit Algorithms_ — Lattimore & Szepesvári — for: S580
- _Reinforcement Learning: An Introduction_, 2nd ed. — Sutton & Barto — for: G401, G504
- _Software Engineering at Google_ — Winters, Manshreck & Wright — for: SE110, SE130 — status: your copy (cd049207e7) is an early release with 3 chapters; the full book is free at abseil.io
- _Designing Data-Intensive Applications_, 2nd ed. (final) — Kleppmann & Riccomini — for: SE120 weeks 7–9 — status: your copy (e66241afb4) is an early release, Chapters 1–7 only
- _Site Reliability Engineering_ — Beyer et al. — for: CR380 (free at sre.google)
- _The Rust Programming Language_ — Klabnik & Nichols — for: CR350 (free at doc.rust-lang.org)

**Engineering (to buy):**
- _System Design Interview_ vols 1–2 — Xu (vol 2 with Lam) — for: IV100, SE120
- _Machine Learning System Design Interview_ — Aminian & Xu — for: IV100, SE120
- _Good Strategy/Bad Strategy_ — Rumelt — for: SE150
- _AI Engineering_ — Huyen (2025) — for: CR120, CR140
- _A Tour of C++_, 3rd ed. — Stroustrup — for: CP201, CP203
- _C++ Concurrency in Action_, 2nd ed. — Williams — for: CP204
- _Learning Spark_, 2nd ed. — Damji et al. — for: CR170
- _Threat Modeling: Designing for Security_ — Shostack — for: CR330
- _The Linux Programming Interface_ — Kerrisk — for: CP310
- _Game Engine Architecture_, 3rd ed. — Gregory — for: CP330
- _C++ Templates_, 2nd ed. — Vandevoorde, Josuttis & Gregor; _C++ Software Design_ — Iglberger — for: CP401, CP402
- _Team Topologies_ — Skelton & Pais — for: SE150 (optional)
- _The Go Programming Language_ — Donovan & Kernighan — for: CR360
- _A Practical Guide to Quantitative Finance Interviews_ — Zhou; _Heard on the Street_ — Crack — for: CR320 (on hold). (_Trading and Exchanges_ — Harris is already on the server: ae0bc03662, grade A)

**Statistics (to buy):**
- _Foundations of Linear and Generalized Linear Models_ — Agresti — for: S310, S520
- _Design and Analysis of Experiments_ — Montgomery (any recent edition) — for: S320
- _The Lady Tasting Tea_ — Salsburg — for: S190
- _Sampling: Design and Analysis_, 3rd ed. — Lohr — for: S370
- Level II: _Theory of Point Estimation_ — Lehmann & Casella; _Testing Statistical Hypotheses_ — Lehmann & Romano; _Asymptotic Statistics_ — van der Vaart; _Theoretical Statistics_ — Keener; _Causal Inference for Statistics, Social, and Biomedical Sciences_ — Imbens & Rubin; _High-Dimensional Statistics_ — Wainwright; _All of Nonparametric Statistics_ — Wasserman; _Monte Carlo Statistical Methods_ — Robert & Casella; _Statistical Inference as Severe Testing_ — Mayo; _The Foundations of Statistics_ — Savage

**Indian History (to buy):**
- _What Is History?_ — E. H. Carr — for: IH150
- _India in the Persianate Age, 1000–1765_ — Richard Eaton — for: IH202, IH203
- _The Mughal Empire_ (New Cambridge History) — John F. Richards — for: IH203
- _Modern South Asia_, 4th ed. — Bose & Jalal — for: IH203–IH205
- _The Great Partition_, 2nd ed. — Yasmin Khan — for: IH205
- _India After Gandhi_ (2017 or later) — Ramachandra Guha — for: IH206
- _The Other Side of Silence_ — Urvashi Butalia — for: IH205, IH390, IH540
- _King, Governance, and Law in Ancient India: Kautilya's Arthaśāstra_ — Olivelle (trans.) — for: IH201, IH320, IH520
- _The Baburnama_ — Thackston (trans.) — for: IH203, IH520 (Alberuni's _India_, Sachau trans., and the _Ain-i-Akbari_ are public domain)
- _Mughal Warfare_ — Jos Gommans — for: IH320
- _Indian Art_ (Oxford History of Art) — Partha Mitter — for: IH340
- Level II: _Orientalism_ — Said; _Aryans and British India_ — Trautmann; _An Introduction to the Study of Indian History_ — Kosambi; _Indian Feudalism_ — R. S. Sharma; _India's Struggle for Independence_ — Bipan Chandra et al.; _The Emergence of Indian Nationalism_ — Seal; _Indian Society and the Making of the British Empire_ — Bayly; _Provincializing Europe_ — Chakrabarty; _The Past Before Us_ — Thapar; _Aśoka and the Decline of the Mauryas_ — Thapar; _A Concise History of South India_ — Karashima (ed.); _A Social History of the Deccan_ — Eaton; _The Long Partition_ — Zamindar; _The Cambridge Introduction to Sanskrit_ — Ruppel; _An Introduction to Persian_ — Thackston

**Games (to buy):**
- _Lessons in Play_, 2nd ed. — Albert, Nowakowski & Wolfe — for: G102, G502
- _Backgammon_ — Paul Magriel — for: G401
- _The Oxford History of Board Games_ — Parlett — for: G190 (also _A History of Chess_ — Murray, public domain; _Ancient Board Games in Perspective_ — Finkel)
- _Simulating War_ — Philip Sabin — for: G350
- _Game Balance_ — Schreiber & Romero — for: G602
- _Combinatorial Game Theory_ — Siegel — for: G502 (optional)
