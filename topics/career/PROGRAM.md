# Career: earning power and a fallback

*Designed 2026-10-07, revised the same day after your answers (MISSION.md) with `/program setup` (`notes/major-design.md`). **Parked**: nothing is scheduled until you say so.*
*What you asked for: a fallback that pays well if the AI/ML path doesn't pan out; anything goes (certs, frameworks, languages,
other kinds of engineering, math); suggestions welcome. So this file recommends, rather than lists.*

## TL;DR: what I recommend (after your answers, 2026-10-07)
Your answers: insure against AI hype cooling **and** AI automating software work; years of exams are fine; no rush; **remote only**;
no relocation, finance hours or more school. Your goal in your words: **"a chill life and a lot of money"**, so every option below is
scored on both (the "Chill" column). That points away from tech-adjacent fallbacks and toward **exam-gated, remote-friendly
work outside the software job market**.

1. **Main fallback: actuary.** It has the best evidence on both counts: repeatedly ranked a top job for pay, low stress and
   work-life balance (CareerCast ranked it #1; most actuaries rarely work over 50 hours a week, though consulting runs longer) [15]. A ladder of exams (the credentials *are* the career, so certs genuinely pay here), BLS median
   $125,770 [3]. Remote/hybrid is common: in one 2025 survey 89% of insurance/actuarial staff had a remote option, and consultancies
   keep the most flexibility [12]. On automation: routine reserving and reporting are exposed, but signed-off judgment is not, and
   2026 reports describe a shortage, especially of actuaries with data/ML skills [13], which is you. **First step: SOA Exam P
   (probability)**, which overlaps the Statistics major you're already doing [5]. Course CR325.
2. **Second fallback: patent agent.** One exam (the USPTO registration exam), no law degree; your CE and CS degrees qualify you;
   median around $124k [14]. Regulated legal work on software, AI and hardware patents. Fully remote firms exist, some letting you set your own
   billable-hour target; law-firm billable hours are the stress risk, and in-house roles are calmer [16]. Course CR327.
3. **If only AI hype cools** (software still fine): your remote, same-industry pivots are SRE/platform or embedded (CR380, CR370), and
   the boosters below keep your current path strong.
4. **On hold:** quant developer and quant research. They pay the most [1][4], but top firms are mostly on-site in a few hubs.
   Revisit if remote-only changes.
5. **Always worth it:** interviewing and negotiation (CR150) and a public portfolio (CR390).
6. **The chill-and-rich sweet spot is probably where you already are:** a remote AI/ML job at a well-paying company. The cheapest way
   to raise both is the boosters (fine-tuning and inference pay the biggest premiums [2]) plus CR150, since a job switch with good
   negotiation usually moves pay more than a new skill does (my judgment). The fallbacks are there so that a bad year in AI is an
   inconvenience rather than a crisis.

Honest trade-off: both main fallbacks start well below your likely current pay (ML-engineer median $261k [2]). They are insurance
with a solid floor, and actuarial pay climbs with each exam passed. They are not upgrades on day one.

## 1. All the options, compared
| Fallback | Pay evidence | Chill (remote, hours, stress) | Carries over from you | Barrier | Verdict |
|---|---|---|---|---|---|
| **Actuary** | BLS median $125,770 [3] | high: top-ranked for low stress; ~40–50 h; remote/hybrid common [12][15] | probability/stats, Python/ML | years of exams [5] | **main fallback** |
| **Patent agent** | median ~$124k [14] | medium–high: remote firms exist; billable hours at firms, calmer in-house [16] | CE + CS degrees (exam eligibility), technical reading | one exam | **second fallback** |
| SRE / platform | median reported $164k–$225k (sources disagree) [6] | medium: on-call (my judgment) | infra, Kubernetes | low | remote pivot if only AI cools |
| Embedded software | median reported $165k–$220k [7] | medium: often on-site hardware labs (my judgment) | computer engineering, C | moderate | same |
| Quant developer (C++) | $300–550k new grad at top firms [1] | low: on-site, intense (my judgment) | SWE, CE, C++, math | on-site, competitive | on hold (remote) |
| Quant researcher | base median ~$213k [4] | low–medium: on-site (my judgment) | math, stats, ML | PhD near-baseline at top firms [4] | on hold |
| Cloud / AI security, solutions architect | security and architect certs top general IT pay surveys [9] | medium: incident response / client travel (my judgment) | cloud, AI | new domain | optional |
| Operations research analyst | BLS median $88,940 [3] | high | math | low | skill, not a destination |

A note on certs: most "certs raise pay 20–50%" claims come from training and cert-selling sites [10], so treat them as weak evidence.
Certs pay off most where the field is **credential-gated** (actuarial exams, the patent bar, security); in AI hiring, demonstrated
work counts for more. That's why every course here ends in something you can show.

## 2. Courses
**Core (small on purpose; it serves any path)**
| Course | What | Deliverable |
|---|---|---|
| CR000 Skills audit and choosing a fallback | pay benchmark, quick checks per track, pick main fallback + one probe, set exam dates | a one-page plan |
| CR150 Interviewing and negotiation | coding (Skiena), ML/system design (Huyen), negotiation (Qureshi) | a passed mock loop, a negotiation script |
| CR390 Portfolio and visibility (ongoing) | resume/LinkedIn line after each result; public write-ups | the "advertise" part |

**Fallback tracks (recommended: CR325 main, CR327 second)**
| Course | Path |
|---|---|
| CR310 Quant developer (on hold) | C/C++ major CP101→CP204, then CP403 performance; market microstructure (Harris, *Trading and Exchanges*: wanted); a low-latency order-book project |
| CR320 Quant research (on hold) | Statistics major + probability-puzzle prep (*Heard on the Street*, Zhou's "Green Book": wanted) + convex optimization |
| **CR325 Actuary** | SOA Exam P → FM → (ASA path: FAM, SRM, ...) [5] |
| **CR327 Patent agent** | USPTO registration exam |
| CR326 Math toolkit: optimization / OR | Boyd & Vandenberghe (in collection); LP/IP |
| CR330 Cloud and AI security | AWS Security Specialty; LLM security |
| CR340 Solutions architect | AWS SAA (course in hand) → Professional, or GCP Cloud Architect |
| CR370 Embedded and robotics | C/C++ major CP101 + CP120, Holt *Embedded Operating Systems* (A), a microcontroller project |
| CR380 SRE and platform | Google SRE book (free), CKA |
| CR350 Rust · CR360 Go | official books; only if a target job asks |

**Boosters for the current AI/ML path (optional)**
| Course | Deliverable |
|---|---|
| CR100 ML systems design and MLOps (Huyen, *Designing ML Systems*, in collection) | design doc + pipeline repo |
| CR110 Kubernetes for ML | CKAD |
| CR120 LLM apps and agents (Huyen, *AI Engineering*: wanted) | public agent + evals; Claude Certified Architect if you're eligible |
| CR130 Fine-tuning and post-training at scale | NVIDIA NCP-GENL and/or a public fine-tuning repo |
| CR140 Inference optimization and serving | a benchmarked deployment |
| CR210–CR250 other cloud certs | only if a job asks |

Level II: CR490, reproduce a recent paper in public (optional). The full map: `curriculum.json`, `DAG.md`.

## 3. How it keeps itself current
- `catalog.json` holds every cert, skill, language, track and pay figure above, each with its sources and the date it was last checked.
- `python3 scripts/catalog.py` lists entries that are due: older than 60 days, an announced change date coming up, or an
  unconfirmed exam whose course is about to start. `/program` shows the count at session start; the session then re-checks those
  entries on the web (official page first), updates them and logs every change in `CHANGES.md`. If a change affects the plan (an exam
  retires, a track's pay drops), it proposes the change rather than making it.
- Before starting any course: `python3 scripts/catalog.py --course <ID>`.
- Optional: a monthly scheduled refresh, so it updates even when you're not studying (ask, and I'll set it up).

## 4. Books needed
| Book | For | Status |
|---|---|---|
| SOA Exam P study manual (e.g. ACTEX or Coaching Actuaries) | CR325 | **wanted first** (main fallback's first exam) |
| A patent-bar prep course or book (e.g. one built on the MPEP) | CR327 | when you start it |
| Harris, *Trading and Exchanges* | CR310 | only if quant comes off hold |
| Huyen, *AI Engineering* (O'Reilly, 2025) [11] | CR120, CR140 | wanted (booster) |
| Xu, *System Design Interview* vol. 1–2 | CR150 | wanted |
| Crack, *Heard on the Street*; Zhou, *A Practical Guide to Quantitative Finance Interviews* | CR320 | only for quant research |
| In collection: Huyen *Designing ML Systems* (A), Kleppmann *DDIA* (A), Skiena (B), Boyd *Convex Optimization* (B), Holt (A), PMPP (A), Raschka (B) | | |

## Sources
1. Nexus IT Group, *What quant firms are paying for C++ engineers in 2026*. https://nexusitgroup.com/what-quant-firms-are-paying-for-c-engineers/ ; Quantt, *Quant developer salary*. https://www.quantt.co.uk/resources/quant-developer-salary
2. Let's Data Science, *What AI skills actually pay in 2026* (cites Levels.fyi ML engineer median $261k, Q1 2026, n=9,517; fine-tuning +25–40%; inference engineers at NVIDIA $205–331k). https://letsdatascience.com/blog/the-56-premium-what-ai-skills-actually-pay-in-2026
3. U.S. Bureau of Labor Statistics, *Occupational Outlook Handbook: Math occupations* (actuaries, operations research analysts). https://www.bls.gov/ooh/math/
4. TraderMath, *Quant researcher salaries* (updated 2026-09-28). https://www.tradermath.org/salaries/quant-researcher ; Selby Jennings, *USA quantitative compensation guide 2026*. https://www.selbyjennings.com/en-us/industry-insights/compensation-guides/usa-quantitative-analytics-research-trading-compensation-guide-2026
5. Society of Actuaries, *Fellow of the Society of Actuaries (FSA)*. https://www.soa.org/education/fsa/ ; Actuary.info, *Actuarial exams*. https://actuary.info/become-an-actuary/actuarial-exams/
6. Jobspipe, *Site reliability engineer salary, USA*. https://jobspipe.dev/salary/site-reliability-engineer/usa
7. Recruiting from Scratch, *Embedded systems engineer salary in 2026*. https://www.recruitingfromscratch.com/blog/embedded-systems-engineer-salary-in-2026-real-data-from-1-9-million-job-postings
8. ResumeGeni, *Robotics engineer salary guide*. https://resumegeni.com/blog/robotics-engineer-salary-guide
9. Skillsoft, *Top-paying IT certifications* (2025 IT Skills and Salary survey). https://skillsoft.com/jp/blog/top-paying-it-certifications
10. e.g. CertSelect, *AI certification ROI*. https://certselect.com/us/en/ai/ai-certification-roi-salary-impact/
11. O'Reilly, *AI Engineering* (Huyen, 2025). https://www.oreilly.com/library/view/ai-engineering/9781098166298/
12. Actuary.info, *Remote actuary jobs* (cites Selby Jennings 2025 Insurance & Actuarial Talent Report: 89% had a remote option). https://actuary.info/careers/remote-actuary-jobs/
13. Actuary.info, *Big tech AI pivot and the actuarial job market 2026*. https://actuary.info/insights/big-tech-ai-pivot-actuarial-job-market-2026 ; Legal & General, *Can actuaries be replaced by AI?* (2026). https://careers.legalandgeneral.com/blog/2026-4/can-actuaries-be-replaced-by-ai
14. UpCounsel, *What is a patent agent* (eligibility: engineering, computer science or hard-science degree; median ~$123,590 per Salary.com). https://www.upcounsel.com/what-is-a-patent-agent
15. beanactuary.org (SOA/CAS), *Will I have a social life?* and the CareerCast "best job" rankings (2010, 2013, via PlanAdviser and The Globe and Mail). https://beanactuary.org/?p=561 ; https://planadviser.com/?p=20026
16. PatentPC, *Transitioning from private practice to in-house: work-life balance*. https://patentpc.com/blog/transitioning-from-private-practice-to-in-house-how-it-affected-my-work-life-balance ; Patently-O job listing, *Patent agent/attorney, small law firm, remote (flexible hours)*. https://patentlyo.com/jobs/2019/04/patent-attorney-remote-flexible.html
Exam facts (AWS, Azure, NVIDIA, Databricks, Anthropic, CNCF, HashiCorp, PyTorch): per-entry sources in `catalog.json`.
