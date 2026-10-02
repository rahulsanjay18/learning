# Notes (teacher's scratchpad)

## Learner preferences
- Background: BS Math + BS CompE (Penn State), MS CS (Georgia Tech), 5 yrs in AI. Speak at that level; analogies to
  systems, state machines, curricula/schedules are fine.
- Inattentive ADHD: keep lessons short, one idea, tight feedback loops. 20–30 min per session.
- Wants citations in text and at the end of every explanation, and a saved Markdown/HTML copy of explanations.
- Goal mix: side gig + own knowledge + credential + possible fitness tech. Not a job change.

## Working notes
- **Exam facts (official):** 120 questions, 2 hours, scaled score 70 to pass (nasm.org exam-info page). Domain weights from
  NASM's own blueprint PDF (2019 job analysis, updated 2.10.2021): Sciences 15, Client Relations 15, Assessment 16,
  Program Design 20, Technique 24, Professional 10. Some prep sites (ptpioneer) list DIFFERENT, mislabeled weights: trust the PDF.
  Blueprint PDF is served gzip-compressed: `curl ... | zcat > bp.pdf` before `pdftotext`.
- **Edition gap:** library textbook is 4th ed. (2012, grade B, id `9166ed3226`); exam follows the 7th ed. Phase 3 was
  "Hypertrophy" in older material and is "Muscular Development/Hypertrophy" on NASM's current OPT page. Always check
  claims against nasm.org before teaching them; flag edition differences in lessons. Added 7th ed. to library/WANTED.md.
- **Mometrix flashcards (grade A conversion, id `f12a3e814e`)**: conversion is clean but the CONTENT has errors, e.g. one card
  says the stabilization level's phase is "strength endurance". Use only for question styles, never as an authority.
- Acute variables for OPT phases: sourced from https://www.nasm.org/certified-personal-trainer/the-opt-model . Phase 1 sets,
  rest and tempo numbers were NOT on that page; don't teach numbers that aren't sourced.
- Plan (weighting by exam %): L1 OPT model (backbone of Program Design + Technique, 44%). Next candidates:
  L2 acute variables per phase, L3 overhead squat assessment (compensations → over/underactive muscles), then
  planes of motion & muscle actions, stages of change, scope of practice. Interleave older topics as retrieval warm-ups.
