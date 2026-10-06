# Open-weight LLMs vs. Claude, and what self-hosting costs (checked 2026-10-06)

## TL;DR
- **Claude Pro: $200/year** (annual billing; $20/month otherwise) [1].
- **Matching Claude with open models isn't affordable to self-host.** The best open-weight models score a clear notch below the top
  Claude models and need ~8 datacenter GPUs; on AWS that's **≈ $20,000/year at just 1 hour a day**.
- **Small open models are affordable but much weaker.** On your own 5070 Ti they cost **≈ $40/year in electricity**, but they score
  around a quarter of Claude's on the same index. Good enough for narrow, checkable jobs (search, first-pass grading), not for designing lessons.
- **Best setup for you:** keep Claude Pro as the big model, and run small models on the GPU you already own (the ensemble plan).
  AWS hosting loses on every line: cost, and quality per dollar.

## 1. How they compare (Artificial Analysis Intelligence Index, read 2026-10-06 [2])
Composite of many hard benchmarks; higher is better. Scores were read through a summarizing fetch, so treat small gaps loosely.

| Model | Open weights? | Index | Fits your 16 GB GPU? |
|---|---|---|---|
| Claude Opus 5.5 (top overall) | no | 58 | — |
| Claude Sonnet 5.5 | no | 56 | — |
| Best open-weight models: MiMo-V2.6-Pro, Qwen 3.8 Max, GLM-5.x, Kimi K3, DeepSeek-V4.1 | yes | ≈ 46 at the top [2][3] | **no** (hundreds of billions to ~2.8T parameters) |
| Gemma 4 31B | yes | 15 | no (≈ 16 GB at 4-bit before any working memory) |
| Claude Haiku 4.5 (non-reasoning) | no | 15 | — |
| Qwen3.5 9B · Mistral Small 4 · Granite 4.2 8B | yes | 11 | yes |
| gpt-oss-20b | yes | 9 | yes |

Reading it: the best *open* models are roughly 80% of the way to the top Claude model. The ones that fit a single consumer GPU are
at about 15–20% of the top score, which is roughly Haiku-class or below. That gap is why the plan only gives small models tasks they pass
a test set on, and escalates the rest.

## 2. What it costs per year

| Option | GPU memory | 2 h/night | 1 h/day | 24/7 |
|---|---|---|---|---|
| **Your 5070 Ti at home** (300 W, assume $0.18/kWh) | 16 GB | **≈ $39** | — | — |
| AWS g5.xlarge (1× A10G) at $1.006/h [4] | 24 GB | $734 | $367 | $8,813 |
| AWS g6e.xlarge (1× L40S) at $1.861/h [4] | 48 GB | $1,359 | $679 | $16,302 |
| AWS p5.48xlarge (8× H100) at $55.04/h [5]: needed for the big open models | 640 GB | $40,179 | $20,090 | $482,150 |
| **Claude Pro** [1] | — | — | — | **$200** |

On-demand, us-east-1, compute only (storage and data transfer extra). Electricity is an assumption: check your rate.
Hourly figures assume the instance is started and stopped around each job.

- A bigger single AWS GPU (L40S, 48 GB) only buys mid-size models (≈ 30–70B at 4-bit), still far below Claude, at 7–80× Pro's price.
- Your second-5070-Ti question in the same terms: 32 GB total → ~30B models. Worth it only if the grading test set shows the
  9–14B models fall short (unchanged from `slm-offload-plan.md`).

## Sources
1. Claude Pro pricing ($20/month, $17/month billed annually = $200/year): https://www.eesel.ai/blog/claude-pro-pricing
2. Artificial Analysis, LLM leaderboard (Intelligence Index): https://artificialanalysis.ai/leaderboards/models
3. BenchLM, open-source leaderboard (Oct 2026): https://benchlm.ai/best/open-source · Morph, "Best open source LLMs (2026)": https://www.morphllm.com/best-open-source-llm
4. Vantage, g5.xlarge: https://instances.vantage.sh/aws/ec2/g5.xlarge · Economize, g6e.xlarge ($1,358.53/month): https://www.economize.cloud/resources/aws/pricing/ec2/g6e.xlarge/
5. Vantage, p5.48xlarge ($55.04/h): https://instances.vantage.sh/aws/ec2/p5.48xlarge
