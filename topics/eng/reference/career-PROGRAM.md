# Career: earning more in ML/AI-adjacent tech, with a safety net

*Designed 2026-10-07 and revised twice the same day after your answers (MISSION.md), with `/program setup` (`notes/major-design.md`). **Parked**: nothing is scheduled until you say so.*
*What you asked for: first a fallback; then (revised) **earning more in computer jobs adjacent to ML/AI and software engineering**
as the main priority, keeping the fallback as a safety net. Anything goes (certs, frameworks, languages, math); suggestions welcome,
so this file recommends rather than lists.*

## TL;DR: what earns more in a career like yours (revised 2026-10-07)
You asked to make **computer jobs adjacent to ML/AI and software engineering** the main priority (keeping the safety net), and
"what will earn me more money in a career similar to mine". Ranked by how much each lever moves pay, with evidence:

| # | Lever | How much it moves pay | Course |
|---|---|---|---|
| 1 | **Level: senior → staff** | Senior MLE TC often $250k+; staff at FAANG-tier $600k–$950k (Levels.fyi via ResumeGeni) [17][18] | CR160 + CR150 |
| 2 | **Company tier** | Same title, different employer: data-engineer median TC ~$157k overall vs. ~$240k at Google/Meta/Apple [19]; frontier labs highest [17] | CR150 |
| 3 | **Specialty premium** | Fine-tuning/post-training +25–40% over standard MLEs; inference optimization $205–331k at NVIDIA; ML infra +$20–40k [2]; AI security +31% over non-AI security [20] | CR130, CR140, CR100–CR110, CR330 |
| 4 | **Switching and negotiating** | Usually beats a raise (my judgment; no clean figure) | CR150 |
| 5 | Certifications | Smallest and weakest evidence for AI roles [10]; real value in credential-gated work | as needed |

Two consequences for the plan:
- **Staff-level skills come first**: distributed systems and architecture (also cited as among the most AI-resistant skills [20]) plus
  the interview loop that gets you leveled correctly. Leveling is decided at hiring, so CR150 is not an afterthought.
- **Pick one premium specialty and go deep**, rather than many badges: infrastructure/platform (most remote-friendly, needed whether
  AI booms or cools), or inference/performance (highest premium; uses the C/C++ major), or AI security (fastest growth).

Remote caveat: the very top of levers 1–2 (frontier labs, some big-tech teams) is often hybrid or on-site. Remote-first companies
and infrastructure/security roles are where remote and high pay overlap best (my judgment).

### Main priority: adjacent tech (core courses, in order)
**Update 2026-10-07:** the staff-level part (CR160 design, CR150 interviewing) is now its own major, `topics/staff/PROGRAM.md`, done first.

1. **CR100 ML systems design and MLOps** → **CR160 Distributed systems and architecture** (staff-level design; DDIA, in collection).
2. **CR150 Interviewing and negotiation** alongside, from the start.
3. **Specialty, pick one first:**
   - **Infrastructure/platform:** CR110 Kubernetes (CKAD) → CR380 Platform engineering and SRE (CKA).
   - **Inference/performance (recommended, 2026-10-07):** CUDA has the best pay evidence of the three: senior-to-staff GPU engineers at $300k–$700k+, kernel writers at the top [21]. Path: C/C++ CP101 → CP320 CUDA (PMPP, in collection) → CR140; CR130 fine-tuning optional.
   - **Quick win alongside: Spark** (CR170, ~6 lessons): advertised floor ~$180k, $50–70k above the market median [22]; lower ceiling than CUDA but weeks, not months.
   - **AI and cloud security:** CR330 (after CR110).
4. **CR390 Portfolio** throughout: every course ends in something public.

### Safety net (kept from the first version)
If tech as a whole turns bad: **actuary** (exam ladder, top-ranked low-stress job, remote/hybrid common, BLS median $125,770; first step
SOA Exam P, which overlaps the Statistics major) and **patent agent** (one exam your degrees qualify you for, median ~$124k). Quant
developer/research stay on hold (on-site). Details in the comparison table below.

## 1. All the options, compared
| Option | Pay evidence | Chill (remote, hours, stress) | Carries over from you | Barrier | Verdict |
|---|---|---|---|---|---|
| ML infrastructure / platform | +$20–40k over generalists; roles +41.8% YoY [2] | medium–high: remote-friendly, some on-call (my judgment) | what you do now | low | **main priority** |
| Inference / performance | $205–331k at NVIDIA [2] | medium | ML + C/C++/CUDA | C++ depth | **main priority (specialty)** |
| AI / cloud security | +31% premium; hiring +23% [20] | medium | AI + cloud | new domain | **main priority (specialty)** |
| Data engineering | median TC ~$157k [19] | medium–high | data pipelines, SQL | low | adjacent option (CR170) |
| **Actuary** | BLS median $125,770 [3] | high: top-ranked for low stress; ~40–50 h; remote/hybrid common [12][15] | probability/stats, Python/ML | years of exams [5] | safety net (outside tech) |
| **Patent agent** | median ~$124k [14] | medium–high: remote firms exist; billable hours at firms, calmer in-house [16] | CE + CS degrees (exam eligibility), technical reading | one exam | safety net (outside tech) |
| SRE / platform | median reported $164k–$225k (sources disagree) [6] | medium: on-call (my judgment) | infra, Kubernetes | low | remote pivot if only AI cools |
| Embedded software | median reported $165k–$220k [7] | medium: often on-site hardware labs (my judgment) | computer engineering, C | moderate | same |
| Quant developer (C++) | $300–550k new grad at top firms [1] | low: on-site, intense (my judgment) | SWE, CE, C++, math | on-site, competitive | on hold (remote) |
| Quant researcher | base median ~$213k [4] | low–medium: on-site (my judgment) | math, stats, ML | PhD near-baseline at top firms [4] | on hold |
| Solutions architect | security and architect certs top general IT pay surveys [9] | medium: incident response / client travel (my judgment) | cloud, AI | new domain | optional |
| Operations research analyst | BLS median $88,940 [3] | high | math | low | skill, not a destination |

A note on certs: most "certs raise pay 20–50%" claims come from training and cert-selling sites [10], so treat them as weak evidence.
Certs pay off most where the field is **credential-gated** (actuarial exams, the patent bar, security); in AI hiring, demonstrated
work counts for more. That's why every course here ends in something you can show.

## 2. Courses
**Main priority (core, in order)**
| Course | Primary resource | Deliverable |
|---|---|---|
| CR000 Skills audit and targets | pay benchmark (Levels.fyi band now vs. target level and company), quick checks | a one-page plan; which specialty first |
| CR100 ML systems design and MLOps | Huyen, *Designing ML Systems* (A, in collection) | design doc + pipeline repo |
| CR160 Distributed systems and architecture | Kleppmann, *DDIA* (A, in collection); Xu (wanted) | staff-level design docs |
| CR150 Interviewing and negotiation | Skiena (B), Huyen's ML interviews book (free), Qureshi (free) | a passed mock loop; a negotiation script |
| CR110 → CR380 Infrastructure/platform | CNCF CKAD curriculum, then Google *SRE* book (free) | CKAD, then CKA |
| CR130 → CR140 Inference/performance | NVIDIA NCP-GENL guide, PyTorch distributed docs, vLLM docs (+ C/C++ major) | NCP-GENL and/or a public repo; a benchmarked deployment |
| CR330 AI and cloud security | LLM-security references + AWS Security Specialty guide | a security badge + a public threat model of an LLM app |
| CR390 Portfolio and visibility (ongoing) | — | resume/LinkedIn line after each result; public write-ups |

**Adjacent options (optional)**
| Course | When |
|---|---|
| CR120 LLM apps and agents (Huyen, *AI Engineering*: wanted) | if your work moves toward agents; Claude Certified Architect if eligible |
| CR170 Data engineering | if a target employer is data-platform heavy (Databricks badge: CR230) |
| CR340 Solutions architect | AWS SAA (course in hand) → Professional |
| CR350 Rust · CR360 Go · CR240 Terraform | only if a target job asks |
| CR370 Embedded and robotics | lower pay/remote fit; only for interest |
| CR210 GCP · CR220 Azure · CR230 Databricks · CR250 AWS GenAI Pro | only if a job asks |

**Safety net (outside tech)**
| Course | Path |
|---|---|
| **CR325 Actuary** | SOA Exam P → FM → (ASA path: FAM, SRM, ...) [5] |
| **CR327 Patent agent** | USPTO registration exam |
| CR326 Math toolkit: optimization / OR | Boyd & Vandenberghe (in collection); LP/IP |
| CR310 Quant developer · CR320 Quant research | on hold (on-site) |

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
17. ResumeGeni, *Data scientist / ML engineer hub: staff level* (cites Levels.fyi 2026: FAANG-tier staff $600k–$900k; Google L6 MLE $650k–$950k). https://resumegeni.com/blog/data-scientist/staff
18. Interview Kickstart, *How much do machine learning engineers make in 2026?* (big-tech MLE median TC $264,400; senior). https://interviewkickstart.com/blogs/articles/machine-learning-engineer-salary
19. Levels.fyi, *Data Engineer salary* (US median TC; per-company pages for Google, Meta, Apple). https://www.levels.fyi/t/software-engineer/title/data-engineer
20. Careery, *Will AI replace software engineers?* (most AI-resistant: architecture, distributed systems, security, ML infrastructure); Algeria Tech News summary of Q1 2026 listings (security +23%, AI-security +31% premium). https://careery.pro/research/will-ai-replace-software-engineers ; https://algeriatech.news/?p=28794
21. HeroHunt, *How to recruit GPU kernel engineers (2026)*. https://www.herohunt.ai/blog/how-to-recruit-gpu-kernel-engineers-2026/ ; ctaio.dev, *Nvidia salary (2026)*. https://ctaio.dev/en/salary/nvidia-salary/
22. SeekerScore, *The highest-paid skills in 2026, from 73,374 job postings that disclosed pay*. https://www.seekerscore.com/insights/highest-paying-skills-2026 ; KORE1, *Databricks engineer salary guide*. https://www.kore1.com/databricks-engineer-salary-guide/
Exam facts (AWS, Azure, NVIDIA, Databricks, Anthropic, CNCF, HashiCorp, PyTorch): per-entry sources in `catalog.json`.
