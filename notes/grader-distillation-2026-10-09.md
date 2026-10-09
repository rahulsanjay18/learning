# Should the grader be distilled? (2026-10-09)

Question: to build the server grader (many task types, many subjects), should I distill from Claude?

## Short answer
Not first. Start with an **off-the-shelf rubric-grading model** run in shadow mode. Fine-tune it only if shadow mode shows a
gap you can't fix by prompting. If you do fine-tune, it will be "distillation" only in the weak sense, and the terms need a look first.

## Why
1. **You can only do the weak kind.** Classic knowledge distillation trains the student on the teacher's soft probabilities
   (Hinton et al., 2015). To my knowledge the Claude API doesn't return token log-probabilities, so all you can do is
   *sequence-level* distillation: fine-tune on Claude's text outputs (Kim & Rush, 2016). That is just supervised fine-tuning on
   Claude-written labels.
2. **You have ~10 labels.** SFT needs hundreds to thousands. You'd have to pay Claude to generate synthetic student answers and
   grade them, so you spend tokens up front to save them later. That's worth it only if grading volume is high (it's small now).
3. **Someone already distilled a grader for exactly this.** Prometheus 2 (Kim et al., EMNLP 2024) is an open evaluator model.
   Its inputs are what `grade.py` already builds: instruction, response, **reference answer**, and a **custom rubric** with
   score descriptions. It returns feedback plus a 1–5 score. It comes in a 7B size (Mistral-7B-Instruct-v0.2 base, ~5 GB
   at 4-bit, fits the 5070 Ti) and an 8x7B size. It was fine-tuned on 100K + 200K generated feedback examples. "Many subjects" is
   handled by the rubric in the prompt, not by training per subject.
   - Map scores to our 0..1 scale (for example (s−1)/4), and calibrate the 0.7 "known" cut on the shadow data.
   - Its card notes the data is subject to OpenAI's terms for generated data. Fine for personal grading; read it if you redistribute.
4. **Terms.** Anthropic's Consumer Terms (§3) bar using the Services "to develop or train any artificial intelligence or
   machine learning algorithms or models" to "develop any products or services that compete with our Services". A private
   grader for your own lessons arguably doesn't compete, but the clause's wording is broad. **Judgment, not legal advice:**
   read it (and the Commercial Terms, if you grade through the API) before training on Claude outputs.

## What not to send to a small model, whatever it is
- **Proofs (Statistics, C&B).** Checking a proof's validity is the hard case for small judges. Always escalate.
- **Code.** Run the tests (`py` quizzes already have `--- check`). Execution beats any judge.
- **Numeric / multiple-choice answers.** Already auto-graded in the browser. The grader is only for free text.

So the grader's real job is short free-text answers against a rubric (history, economics, staff writing, concept
explanations). That's Prometheus 2's home turf.

## Plan
1. Prometheus 2 7B in Ollama, behind `/ungraded` → `/grades` with `grader: "slm"`, in shadow mode.
2. Track agreement per subject and task type (Clopper-Pearson lower bound; ~100 items to show 90%, see `slm-offload-plan.md`).
3. Only if a subject stays below the bar: try a general instruct model (e.g. a Qwen 14B) with the same prompt, then consider LoRA SFT on
   the accumulated real Claude-graded answers (after checking the terms).

## Sources
- Hinton, Vinyals & Dean, "Distilling the Knowledge in a Neural Network" (2015): https://arxiv.org/abs/1503.02531
- Kim & Rush, "Sequence-Level Knowledge Distillation" (EMNLP 2016): https://arxiv.org/abs/1606.07947
- Kim et al., "Prometheus 2: An Open Source Language Model Specialized in Evaluating Other Language Models" (EMNLP 2024): https://arxiv.org/abs/2405.01535
- Prometheus 2 7B model card (base, inputs, 1–5 scale, training data, license): https://huggingface.co/prometheus-eval/prometheus-7b-v2.0
- Anthropic Consumer Terms of Service, §3: https://www.anthropic.com/legal/consumer-terms
- Earlier plan and test-set math: `notes/slm-offload-plan.md`
