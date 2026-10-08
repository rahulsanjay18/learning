---
major: eng
updated: 2026-10-08
---
## Overview
This major holds everything career-related: growing from senior to staff engineer, interviewing at the staff level, AWS
certification, systems programming in C and C++, CUDA and inference, and a set of optional certifications and fallback paths. It
doesn't end. When one course finishes, the next in its track starts.

There are four tracks, one meeting each per week:

| Day | Track | What it covers |
|---|---|---|
| Monday | Staff | What staff engineers do, writing, system design, software design, leading cross-team work, strategy, and getting the title |
| Wednesday | Tech | AWS first, then CUDA, Spark, C and C++, security, and the rest of the technical courses |
| Thursday | Interview | Practice at the big-tech staff bar: coding, system design, ML system design, behavioral, project deep dives |
| Friday | Interest | Topics you find interesting for their own sake (one active, two queued) |

Three of the four tracks focus on skills with a clear payoff. The interest track is for exploration, and a topic there moves into
the tech track if it turns out to matter for your career.

## How a lesson works
Each lesson starts with a one-minute Vim tip, then a short reading, the idea, and a written exercise. It ends with a **rep**: a real
ticket from your 3D chess projects (or this learning platform, a lab, or your day job) that puts the lesson to use. You do the
staff-level part (the design doc, the decision record, the review) and I write the code, except in the courses where writing the
code is the skill (C, C++, CUDA, Spark). There you write it and I review. The next lesson in a track waits until its rep ships or
you skip it with a reason.

## What you'll be able to do
- Do the job of a staff engineer: set technical direction in writing, lead work across teams, design systems and ML systems at depth, and raise the bar for others.
- Pass a big-tech staff interview loop.
- Hold the AWS Certified Machine Learning Engineer – Associate certification, and run your RL training fleet on AWS with Terraform.
- Write correct, fast C and modern C++, and GPU kernels in CUDA.
- Serve and optimize models in production.

## How the major is organized
**Staff track (required):** SE000 placement (done) → SE101 what staff is → SE110 writing → SE120 system and ML design → SE130
software design → SE140 execution → SE150 strategy → SE160 evidence and leveling. Optional: SE170 mentoring, SE390 a staff-scope
project, SE399 the title itself. Level II: SE401 principal.

**Tech track (required):** AW000 placement → AW101 AWS foundations → AW201 ML on AWS → AW290 the exam; CP000 placement → CP101 C →
CP120 C and the machine → CP201 core C++ → CP202 effective modern C++ → CP203 the standard library → CP204 concurrency; CR100 ML
systems and MLOps → CR110 Kubernetes (CKAD) → CR130 fine-tuning → CR140 inference → CR330 security → CR380 SRE (CKA).
Optional: CP310 Linux systems programming, CP320 CUDA, CP330 game engines, CR120 LLM applications, CR170 Spark, five more
certifications, and the fallback paths (CR310–CR370). Level II: CP401–CP403 advanced C++, CP490, CP499, CR490.

**Interview track:** IV000 baseline → IV100 continuous practice.

**Interest track:** IN100, continuous.

**Vim (VI100):** a tip inside every lesson, with no meetings of its own.

## Order in the tech track
AWS first, because there's an exam. After that, the default is CUDA (CP320, which needs only CP101), then Spark (CR170), then the C
and C++ sequence, then security. You can change the order at any time.

## Interview cadence
Until October 26, 2027, Thursdays alternate a design round with a short coding mock. From then until February 26, 2028 there's a full mock every week.
From February 26 to about April 26, 2028 there are two interview meetings a week, mostly with standard prompts.

## What it takes to finish
This major doesn't finish. The milestones are: the MLA-C02 certification (AW290), the staff title (SE399), and the C/C++ sequence
through CP204.

## Books
**In your library:** Reilly, *The Staff Engineer's Path*; Larson, *Staff Engineer* and *An Elegant Puzzle*; Ousterhout, *A
Philosophy of Software Design* (1st edition); Kleppmann, *Designing Data-Intensive Applications*, 2nd ed. (early release, Chapters
1–7 only); Huyen, *Designing Machine Learning Systems*; Martin, *Clean Architecture*; Brooks, *The Mythical Man-Month*; Voss, *Never
Split the Difference*; Takada, *Distributed Systems for Fun and Profit*; Gustedt, *Modern C*; van der Linden, *Expert C
Programming*; Bryant and O'Hallaron, *Computer Systems: A Programmer's Perspective*; Arpaci-Dusseau, *Operating Systems: Three Easy
Pieces*; Lippman, Lajoie and Moo, *C++ Primer*; Meyers, *Effective Modern C++* and *Effective C++*; Josuttis, *The C++ Standard
Library*; Hwu, Kirk and El Hajj, *Programming Massively Parallel Processors*, 4th ed.; Gamma et al., *Design Patterns*; Feathers,
*Working Effectively with Legacy Code*; Rosso et al., *Production Kubernetes*; Raschka, *Build a Large Language Model (From
Scratch)*; Neil, *Practical Vim*; Skiena, *The Algorithm Design Manual*; McMahon, *Machine Learning Engineering with Python*.

**Free online:** *Software Engineering at Google* (your copy is an early release; the full book is free at abseil.io); Google's
*Site Reliability Engineering*; Drepper, *What Every Programmer Should Know About Memory*; Agner Fog's optimization manuals; *The Rust
Programming Language*; the AWS, Kubernetes, NVIDIA and vLLM documentation.

**To buy, in the order you'll need them:** Xu, *System Design Interview*, Volumes 1–2, and Aminian and Xu, *Machine Learning System
Design Interview* (IV100, SE120); Huyen, *AI Engineering* (CR120, CR140); Rumelt, *Good Strategy/Bad Strategy* (SE150); Williams,
*C++ Concurrency in Action*, 2nd ed. (CP204); Stroustrup, *A Tour of C++*, 3rd ed. (CP201); Kerrisk, *The Linux Programming
Interface* (CP310); Gregory, *Game Engine Architecture*, 3rd ed. (CP330); Vandevoorde, Josuttis and Gregor, *C++ Templates*, 2nd ed.,
and Iglberger, *C++ Software Design* (Level II); Donovan and Kernighan, *The Go Programming Language* (CR360); Skelton and Pais,
*Team Topologies* (SE150).
