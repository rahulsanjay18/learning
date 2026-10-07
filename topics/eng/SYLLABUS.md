# Engineering career: syllabus (lesson-level plan for the active courses)

Lanes: **Mon staff · Wed tech · Thu interview · Fri interest** (`curriculum.json` → `lanes`). Every lesson opens with a Vim drill
(`vim-drills.json`, checked by `scripts/vimcheck.py`) and ends with a rep from `backlog.json` (required except in the interest lane).
Objectives are graded Got it / Not yet (TEACHING-LOG rule 20).

## SE000 Placement: where you are against a staff rubric (staff lane)
**0001 Staff placement** (written 2026-10-07, `lessons/0001-staff-placement.md`) · reading: Larson's archetypes; Dropbox IC4 vs IC5
- You can name Larson's four staff archetypes and say which one your current work most resembles, with evidence.
- You can rate yourself on six staff dimensions with one concrete piece of evidence each, and name your two biggest gaps.
- You can produce a first-draft design for a real system (3dChessServer #13, the WebSocket move relay) in 25 minutes that covers
  requirements, failure modes and trade-offs at staff depth.
Objectives as written in the lesson itself (it was written before this syllabus); the #13 sketch becomes a full design doc in SE120.

## AW000 AWS placement and exam date (tech lane)
**0002 AWS placement** (written 2026-10-07, `lessons/0002-aws-placement.md`) · reading: the MLA-C02 exam guide's domain list
- You can place each of the four MLA-C02 domains as known / shaky / new, from a short pretest per domain.
- You can say which AWS services the RL training fleet (3dChessRLAgent) already uses and which exam domains they cover.
Rep: pick the exam date (todo `mla-date`).

## IV000 Interview baseline (interview lane)
**0003 Interview baseline** · reading: one 2026 guide to the Google L6 / Meta E6 loop
- You can list the round types in a big-tech staff loop and what each one is grading.
- You can solve one medium coding problem in 35 minutes, in Vim, talking through trade-offs.
- You can tell one leadership story at staff scope (several teams, your direction, a measured outcome) in about 3 minutes.
Rep: write the story in your brag doc in STAR form.

## IN100 Things I find interesting (interest lane, continuous)
**0004 How chess engines search, and what changes on an 8×8×8 board** · reading: Chess Programming Wiki, alpha-beta
- You can explain why alpha-beta prunes and how move ordering changes its cost.
- You can estimate how the branching factor of your 3D variant changes search depth at a fixed budget.

## Changes
- 2026-10-07: syllabus created; interview lane added (learner's bar: big-tech staff interviews); interest lane added ("some parts
  things I find interesting").
