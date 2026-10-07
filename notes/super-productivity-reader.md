# Reading Super Productivity from Claude sessions (plan, 2026-10-07)

*The learner will self-host Super Productivity (SP) on their server, to stay productive at the new job (starts 2026-10-26) and for
non-work tasks, and wants Claude, as a personal assistant, to be able to read it. Status: waiting for the install.*

## TL;DR
- The self-hosted (Docker/web) build is a static app: tasks live in the browser unless you turn on **sync** [2]. Its local REST API exists
  only in the desktop app [1]. So the thing to read is the **sync data on your server**.
- Plan: sync SP to a **WebDAV folder on your server**, then a tiny **read-only digest endpoint** on the book-server host parses that
  file and returns a few lines of text. Claude calls it like `books.py` ("compute, don't narrate"; narrow, read-only).
- First step after you install: sync once, then send Claude a copy of what lands in the WebDAV folder (or its file names and the
  first few lines). The file layout isn't documented clearly enough to code against yet [2], so it gets verified on your real file.

## The endpoint (draft spec)
```
GET /sp/today      → today's tasks (title, project, estimate, time spent), overdue items, done count
GET /sp/week       → time tracked per project this week, tasks completed, what slipped
GET /sp/search?q=  → matching open tasks (title + project only)
```
Read-only, same auth as the book server, plain-text output under ~30 lines.

## Decisions for you
1. **Work privacy.** Your employer's task titles may be confidential. Options: exclude a "Work" project from the endpoint, return only
   counts and time for it, or include it. Default: counts and time only, until you say otherwise.
2. **Encryption.** If SP's sync encryption is on, the reader needs the key **on your server** (never in Claude sessions or this repo).
   Off is simpler; your server and Tailscale are the protection then.
3. **Writing later?** Adding tasks for you (e.g. reps and "things I need from you") is a separate step: SP's GitHub-issues import from a
   private repo needs no code; writing into the sync file directly would risk corrupting it, so don't.

## What I'd do with it (once it exists)
- `/program` start: one line about today's SP load, so learning doesn't collide with a heavy work day.
- Weekly: where your time actually went vs. the plan; flag when learning or rest got squeezed out (the "more time for me" goal).
- Reps and to-dos show up in SP via GitHub issues (option above), so there's one task list, not two.

## Sources
1. Super Productivity docs, *API* (Local REST API: "Electron desktop app only", 127.0.0.1:3876, bearer token; sync server has no task CRUD). https://github.com/super-productivity/super-productivity/blob/master/docs/wiki/3.01-API.md
2. selfhosting.sh, *How to self-host Super Productivity with Docker* (static frontend; data in the browser unless WebDAV sync). https://selfhosting.sh/apps/super-productivity/ ; Privacy Guides forum thread (WebDAV needs CORS configured). https://discuss.privacyguides.net/t/super-productivity-open-source-task-manager/32908
