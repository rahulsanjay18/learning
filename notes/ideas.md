# Ideas parking lot (focus keeper)

*Started 2026-10-07. The learner (chronic ADHD, a million interests) asked Claude to "steer me to focusing on a handful so I make
meaningful progress": they share what they think is cool, and Claude keeps it in mind **here**, not in the active plans.*

## The rules
- **New idea → this file**, with the date and what it could feed. Not into a curriculum, not into a lesson plan.
- **Work-in-progress limits:** the eng interest lane has **1 active topic + 2 queued**. Each other major has one active course
  (Games: two). Statistics, Indian History, Games and the eng major are the active majors; everything else stays parked.
- **One in, one out:** an idea moves from here into a plan only when it replaces something, or when the current topic finishes.
  Claude proposes the swap; the learner decides.
- **Gentle redirect:** when a new idea comes up mid-session, Claude logs it here, says so in one line, and goes back to the day's plan.
- **Review:** once a month (or when the interest lane's active topic finishes), Claude suggests at most one promotion from this list,
  favoring ideas that feed something already active (the "tie it to what you're doing" rule).
- **Mine it for intersections** (learner, 2026-10-07: "the most interesting things often occur at the intersections of domains").
  Before writing a lesson or choosing a rep's venue, scan this list. A parked idea can be used **as material** (an example, a design
  prompt, a dataset, a venue) whenever it fits what's already being taught, e.g. an interview design prompt about distributed
  astrophoto stacking, or a statistics example from 3D chess self-play. Using an idea as material adds no new commitment, so it
  doesn't count against the limits. Say in the lesson which idea it came from. Turning it into its own course or topic still
  goes through one in, one out.
- Long-term subject wishes live in `notes/learning-wishlist.md`; this file is for smaller ideas and project tangents.

## Parked ideas
| Added | Idea | Could feed | Note |
|---|---|---|---|
| 2026-10-07 | Build a small HPC cluster from mini PCs (Slurm/Ray, MPI) | eng interest lane; ML-infra experience; RL `hpc-learning` tickets; compute for everything | strong candidate: feeds 3D chess self-play |
| 2026-10-07 | Astrophotography processing on that cluster (calibrate, align, stack) | CUDA lab (CP320), HPC practice | depends on the cluster existing |
| 2026-10-07 | A forum-search research service (Reddit API) on the book-server host | research quality | spec in notes/design-private-source-public-site.md §6 |
| 2026-10-07 | Compute-access job API for Claude on the learner's server | platform; staff design practice | ticket in topics/eng/backlog.json |
| 2026-10-07 | WebAssembly: how the C++ engine runs in the browser | eng interest lane | was in the interest queue; parked to keep the queue at 2 |
| 2026-10-07 | 3D chess as a side income (skins, subscriptions, Steam) | exploit lane, later | after the web MVP ships |
| 2026-10-07 | OR-Tools (Google's optimization library) | a study-week scheduler (CP-SAT: blocks, lanes, exam deadlines, review load); RL tournament pairings; cluster job scheduling; the CR326 optimization toolkit | **not a service**: it's a pip library and runs in Claude's sessions already (ortools 9.15 tested 2026-10-07). Revisit when the weekly plan has real constraints (exam dates, variable availability). **Learner's angle (agreed): save tokens and get exact answers** by having Claude write the model once and a solver do the reasoning, instead of re-deriving plans in prose each session (same principle as status.py). LLMs alone are weak at exact planning and combinatorial search (PlanBench, Valmeekam et al. 2023, GPT-4 ~12% valid plans; newer models better but not saturated, Valmeekam et al. 2024; natural-language CO degrades with size, NLCO 2026), and the recommended pattern is LLM + sound solver/verifier. **The first real service use case:** the Today page runs in a browser and can't run OR-Tools, so a `/plan` endpoint on the server would let you re-plan from your phone ("I lost Wednesday"). |
| 2026-10-07 | A personal tool server: write a tool once, deploy it on your server, Claude calls it forever (exact outputs, no rewriting programs per session) | everything; the book and progress servers are already two of these | worth it when a tool needs heavy deps (OR-Tools, torch), your data or hardware, or must work from a browser/phone; an MCP server is the standard shape for it (modelcontextprotocol.io). Brainstorm only |
