# progress-server

Stores lesson results from `assets/lp.js`, schedules spaced review, and gives Claude short plain-text digests.
Full endpoint list: the docstring at the top of `app.py`.

## Deploy (next to book-server)
1. Copy this folder to the server next to `book-server/`, and `mkdir -p progress-server/data` (writable by uid 65534: `chown 65534 progress-server/data`).
2. Add `compose.snippet.yml` to your `docker-compose.yml`.
3. Add the `/progress` handler from `serve.json.example` to `book-server/ts-books/serve.json` (keep your existing `/` handler).
4. `docker compose up -d --build progress-server ts-books`
5. Check: `curl https://books.tail59e10.ts.net/progress/health` → `{"ok":true}`

## Pair a device (phone, laptop)
Ask Claude in a session to "pair my phone". It calls `POST /progress/devices` and gives you a link like
`https://rahulsanjay18.github.io/learning/assets/sync.html#endpoint=https://books.tail59e10.ts.net/progress&token=…`.
Open it once on that device. To unpair: the "Turn sync off" button there, or `DELETE /progress/devices/{id}`.

## Tokens
- Teacher token = `BOOKS_TOKEN` (full access; the cloud environment injects it automatically for this hostname).
- Device tokens: write results and read due reviews/feedback only. Stored hashed; revocable.

## Test
`pip install fastapi uvicorn httpx && python3 test_app.py`

## Backups
Everything is in `data/progress.db` (SQLite, WAL mode). Copy it with `sqlite3 data/progress.db ".backup backup.db"`.
