# Notes (teacher's scratchpad)

## Learner preferences
- Background: BS Math + BS CompE (Penn State), MS CS (Georgia Tech), 5 yrs in AI. Game-theory, search and RL analogies welcome
  (label them as analogies when they're mine, not the source's).
- Inattentive ADHD. For this topic they asked for *longer, reading-heavy* sessions (vs. chess's 20–30 min quiz-heavy ones):
  structure = guided reading (questions to hold) -> idea in brief -> a few classification/judgment items -> free recall -> take-it-outside task.
- Wants citations in text and at the end of every explanation, and a saved copy.
- Scope: theory first; tactics AND weapons are IN scope (they first ticked "skip", then corrected it at once); include nuclear/modern.

## Working notes
- Backbone text: Echevarria, *Military Strategy: A VSI* (grade A, id 940de01b70). Its chapter order makes a natural syllabus:
  Ch1 definition and types -> Ch2 annihilation/dislocation -> Ch3 attrition/exhaustion -> Ch4 deterrence/coercion -> Ch5 terror ->
  Ch6 decapitation -> Ch7 cyber -> Ch8 success and failure.
- Lesson 1 = capacity vs. will 2x2 (done). First analysis = First Punic War (see LR 0002 + analyses/). Lesson 2 should be LEVELS AND PHASES
  (battle -> campaign -> war nesting; ends/ways shifting mid-war), First Punic War as the running case. Other candidates after that:
  - Clausewitz: war as continuation of policy, and the trinity (On War Bk1 Ch1, id 8cb37bf97d, plus Howard VSI c589beef4b).
  - Lanchester's laws: attrition as ODEs (Echevarria Ch3 mentions them; derive in-lesson and check with sympy, don't take equations from text).
  - Boyd/OODA and dislocation (Discourse is free from Air University Press).
  - Tactics and weapons as constraints on strategy (Manila Bay tech gap, blitzkrieg combined arms) since they're in scope.
- Spacing: open lesson 2 with 2–3 new cases to classify on the 2x2 (not the ones from lesson 1).
- No GLOSSARY.md yet. Candidates once the learner uses them correctly: annihilation, dislocation, attrition, exhaustion, ends/ways/means.
- Network (checked 2 Oct 2026): US military sites block this container. apps.dtic.mil, airuniversity.af.edu and media.defense.gov
  return 403 from their own firewall (Akamai, "The request is blocked"); our proxy lets the connection through. warroom.armywarcollege.edu
  fails at our proxy gateway (502 on CONNECT), so it may need adding to the environment's allowed domains. Workaround: the learner downloads
  the PDF in a browser and commits it to the repo, or use clausewitzstudies.org / gutenberg.org, which work.
- Polybius, *Rise of the Roman Empire* (Penguin, grade A, id a1de43a246): Book I = First Punic War, Book VI ch 52 = Rome vs Carthage.
  Paragraphs in the server text start with the chapter number (e.g. '20\\.'), so cite as book.chapter.
- Put learner analyses in analyses/YYYY-MM-DD-<war>.md: their text verbatim, then feedback, then a revision task.
