# Notes (teacher's scratchpad)

## Learner preferences
- Background: BS Math + BS CompE (Penn State), MS CS (Georgia Tech), 5 yrs in AI. Speak at that level; analogies to
  search/minimax/evaluation functions are welcome.
- Inattentive ADHD: keep lessons short, one idea, tight feedback loops. 20–30 min per session.
- Wants citations in text and at the end of every explanation, and a saved Markdown/HTML copy of explanations.
- Mission order of priority: (2) deep understanding, then (1) winning online. (3) casual and (4) AI/engines also matter.
- Plays on Chess.com; happy to play untimed bot games so I can diagnose. Ask for the PGN.

## Working notes
- Library: Seirawan "Winning Chess" series (Tactics, Strategies, Endings, Combinations: grade A) is the core
  reading. Polgar 5334 and Henkin 1000 Checkmates are grade B (figures unreliable: recommend only, never take diagrams).
- python-chess won't pip-install in the cloud container (setuptools `install_layout` error). Workaround: `pip download chess`
  and use the unpacked source tarball via PYTHONPATH. Verify every lesson position with `scripts/verify_positions.py`.
- No GLOSSARY.md yet: add terms only after the learner shows they can use them (exchange, hanging, point count are candidates).
- Lesson 1 = counting one square (static exchange). Next candidates, depending on the diagnostic game:
  checks/captures/threats routine, then double attack (fork), then pin.
- Spacing: open lesson 2 with 2–3 retrieval questions on lesson 1 counting (new positions).
