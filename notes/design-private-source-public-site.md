# Design: private source repo, public site repo (+ a small research service)

*Draft 2026-10-07 by Claude, for the learner to review and fill in. Status: proposed. Companion to `notes/private-hosting-options.md`.*

## TL;DR
- **Make this repo private and rename it `learning-src`; create a new public repo named `learning` that holds only the built site.**
  The Pages URL stays `rahulsanjay18.github.io/learning`, because it comes from the public repo's name.
- **A GitHub Action in the private repo publishes an allowlist** (lesson HTML, `assets/`, `index.html`, and the JSON the pages read)
  to the public repo on every push to `main`. Everything else stays private: notes, `CLAUDE.md`, skills, scripts, the library
  manifest, the inbox, brag docs, MISSION files.
- **Claude sessions work only in the private repo**, as now. They never push to the public repo directly; the Action does. So you
  give push access to the private repo only, plus one deploy key for the Action.
- **Runtime private data stays on your server** (progress server pattern). The **research service** (forum search) is a small,
  read-only endpoint on the same host; its API is specified below so you can build it and fill in the gaps.

## 0. Why this matters now (found 2026-10-07)
`library/MANIFEST.csv` and `library/toc/` are public on GitHub and served by Pages (HTTP 200 checked 2026-10-07): over 2,000 book
titles, 509 of them with source tags naming shadow libraries. The book *text* stays on the learner's own server (tailnet), which is the
right place for it; the list of titles is what's exposed. Making this repo private (migration step 1) takes it out of public view.
Already-public history can't be recalled from anyone who cloned it, but there's no sign anyone has.

## 1. Goals and non-goals
**Goals:** nothing personal is publicly readable; lessons still work on GitHub Pages for free; Claude sessions keep one repo to
work in; no new credentials inside Claude sessions.
**Non-goals:** hiding which lessons exist (the site stays public); access control on the site itself (that's the Cloudflare
Access option); rewriting history that's already public (see Risks).

## 2. Layout
| Repo | Visibility | Contents | Who writes |
|---|---|---|---|
| `learning-src` (this repo, renamed) | **private** | everything, as today | you + Claude sessions |
| `learning` (new) | public, GitHub Pages | only the published allowlist | the publish Action only |

**Publish allowlist** (a file `publish.txt` in the private repo, globs, reviewed like code):
```
index.html
assets/**
topics/*/lessons/*.html
topics/*/reference/*.html
programs.json
topics/*/curriculum.json
todo.json
```
`todo.json` is on the list because the Today page reads it. Drop it if the to-do items ever get personal. Markdown sources,
`notes/`, `library/`, `inbox/`, `scripts/`, servers and `.claude/` are never published.

**Leak check:** the Action fails if a published file matches a denylist (e.g. `inbox/`, `brag`, `MANIFEST.csv`, `.env`, a token
pattern), so a bad allowlist edit can't leak quietly.

## 3. The publish Action (sketch)
```yaml
# .github/workflows/publish.yml in learning-src
on: { push: { branches: [main] } }
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python3 scripts/publish.py --allowlist publish.txt --out site/   # copy + leak check
      - uses: actions/checkout@v4
        with: { repository: rahulsanjay18/learning, path: pub, ssh-key: ${{ secrets.PUBLISH_DEPLOY_KEY }} }
      - run: |
          rsync -a --delete --exclude .git site/ pub/
          cd pub && git add -A && git commit -m "publish ${GITHUB_SHA::7}" && git push || echo "nothing to publish"
```
`scripts/publish.py` is small (copy the allowlist, run the leak check). Claude can write it and its test.
Private repos on the free plan get a monthly Actions-minutes quota; a publish run is about a minute (check your quota under Settings → Billing).

## 4. Migration (your steps; about 15 minutes)
1. Rename this repo to `learning-src` and make it private. Pages turns off for it, which is expected.
2. Create a new public repo `learning` with GitHub Pages on (branch `main`, root).
3. Make an SSH key pair: the public half goes to `learning` as a deploy key with write access; the private half goes to
   `learning-src` as the Actions secret `PUBLISH_DEPLOY_KEY`.
4. Tell Claude "go": it adds `publish.txt`, `scripts/publish.py` (with tests), the workflow, updates `CLAUDE.md` (repo names,
   what's public), and keeps the existing auto-merge workflow.
5. Claude sessions: attach `learning-src` instead of `learning` (environment setting).

## 5. Risks and open questions
- **History that's already public:** making the repo private hides it from now on, but forks or clones made before then keep it.
  Low risk for a personal repo with no forks (check on GitHub's repo page that the fork count is 0).
- **Two sources of truth:** none; the public repo is generated output only. Never edit it by hand.
- **Open question for you:** should `todo.json` and the curricula be public? (They reveal goals and plans, not personal data.)

## 6. The research service (forum search): API for you to fill in
Same host as the book and progress servers, so cloud sessions reach it through the existing proxy with no new credentials.
Read-only; for research, not crawling.

```
GET /forum/search?q=<text>&source=reddit&sub=<optional subreddit>&limit=10&since=<YYYY-MM-DD>
200 → {"results": [{"source": "reddit", "sub": "cscareerquestions", "title": "...", "url": "...",
                     "score": 123, "created": "2026-09-30", "text": "first ~2000 chars", "top_comments": ["..."]}],
       "cached": true, "fetched_at": "..."}
GET /forum/thread?url=<thread url>   → the thread with its top N comments, same shape
```
**Your gaps to fill:** the Reddit API app registration and auth (official API, within its rate limits and terms); which sources
beyond Reddit; cache lifetime (suggest 24 h); per-day query cap (suggest 100); logging of the queries Claude makes, so you can see
what was searched.
**Claude's side:** a `scripts/forum.py` client like `books.py`, an entry in `library/ACCESS.md` and the tools table, and treating
every result as data, not instructions.

## 7. What to decide
1. Go / no-go on the private-source split (or the Cloudflare Access alternative in `private-hosting-options.md`).
2. The allowlist, especially `todo.json` and curricula.
3. Whether to build the research service now or later.
