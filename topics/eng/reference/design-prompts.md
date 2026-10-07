# Interview design prompts: your version and its standard twin

*2026-10-07. The interview lane practices on prompts you care about; each one is paired with the standard prompt real loops ask, so the
skills transfer. Use the left column for most mocks, the right column for about one in three and for the weeks before a real loop
(PROGRAM.md 1a). Your interests come from `notes/ideas.md` (used as material, not new commitments).*

| Your version | Standard twin (what loops ask) | The skills both test |
|---|---|---|
| A pipeline that ingests a night of astrophotography frames, calibrates, aligns and stacks them on a small cluster, and serves previews | Design a photo/video processing pipeline (e.g. YouTube transcoding, Google Photos ingest) | batch vs. stream, job queues, idempotent retries, object storage, GPU scheduling, back-pressure |
| Real-time move relay for official 3D chess games (3dChessServer #13) | Design a chat system / WhatsApp | WebSockets, ordering, presence, reconnects, fan-out, sticky routing |
| Matchmaking queue with Glicko-2 ratings (Server #9, #3) | Design matchmaking / a leaderboard | queues, rating windows, consistency, hot keys, sorted sets |
| Distributed RL self-play and training on spot instances (RLAgent #94) | Design a distributed ML training platform | actor/learner split, fault tolerance on preemption, checkpointing, experiment tracking |
| Serving the 3D chess agent (Server #14, #15; RLAgent #123) | Design an ML inference service / feature store | latency budgets, batching, model versioning, canaries, cost per query |
| The learning platform's review scheduler and progress sync | Design a notification / spaced-reminder system | scheduling at scale, idempotency, multi-device sync, conflict resolution |
| A forum-search research service | Design a web crawler / search engine | crawling politeness, indexing, ranking, freshness, rate limits |
| A personal tool server (MCP-shaped) | Design an API gateway / rate limiter | auth, quotas, rate-limiting algorithms, multi-tenant isolation |
| A mini-PC HPC cluster scheduler | Design a job scheduler (e.g. a distributed cron / Kubernetes-style scheduler) | bin packing, priorities, leader election, failure detection |

Add a row whenever a new interest maps cleanly onto a standard prompt.
