# Deploying the progress server

*Written 2026-10-05. Answers: how do I deploy `progress-server/`, and do I need to build a Docker image?*

## Short answer
You don't build the image yourself. `docker compose up -d --build` builds it from `progress-server/Dockerfile`
(python:3.12-slim, FastAPI + uvicorn on port 8089) [1][2]. You do four things on the server: copy the folder, add
one service to your compose file, add one route to the Tailscale config, and start it.

## Steps (run on the machine that already runs book-server)

```bash
# 0. Get the code onto the server (from the folder that holds docker-compose.yml)
git clone https://github.com/rahulsanjay18/learning.git /tmp/learning   # or git pull if you already have it
cp -r /tmp/learning/progress-server ./progress-server

# 1. A writable data folder. The container runs as uid 65534 ("nobody").
mkdir -p progress-server/data
sudo chown 65534 progress-server/data
```

**2. Compose:** paste the `progress-server:` block from `progress-server/compose.snippet.yml` under `services:` in your
`docker-compose.yml`, next to `book-server`. It reuses `${BOOKS_TOKEN}` from your existing `.env`, so the cloud
sessions' injected credential works with no new secret [3].

**3. Tailscale route:** in `book-server/ts-books/serve.json`, add the `/progress` line next to your existing `/` line:

```json
"Handlers": {
  "/": { "Proxy": "http://127.0.0.1:8088" },
  "/progress": { "Proxy": "http://127.0.0.1:8089" }
}
```

**4. Start it** (this is the build step):

```bash
docker compose up -d --build progress-server ts-books
```

The `ts-books` service restarts too, so it picks up the new `serve.json`.

**5. Check:**

```bash
curl https://books.tail59e10.ts.net/progress/health    # expect {"ok":true}
```

Then tell me in a session. I'll run `/progress/status` and pair your phone.

## The one thing that can go wrong: `127.0.0.1` inside the sidecar
`serve.json` sends `/progress` to `127.0.0.1:8089`. Inside a container, `127.0.0.1` means *that container's own
network*, so whether this works depends on how your `ts-books` service is networked [4]. Check with:

```bash
docker compose config | grep -A3 'ts-books:' ; docker compose config | grep network_mode
```

| How `ts-books` is set up | What to do |
|---|---|
| `network_mode: host` | Nothing. The snippet's `127.0.0.1:8089:8089` port mapping is enough. |
| `network_mode: service:book-server` (shares book-server's network) | `127.0.0.1` is book-server's container, so 8089 isn't there. Easiest fix: in `serve.json` use `http://progress-server:8089` instead, and make sure ts-books can reach that service on the compose network (or tell me the setup and I'll adjust it). |
| Neither (its own network) | Same as the row above: point `/progress` at `http://progress-server:8089`. |

Since your existing `/` route uses `127.0.0.1:8088` and works, the first or second row is most likely.
The app answers both at `/` and under `/progress`, so it doesn't matter whether the proxy strips the prefix [5].

## Optional: test before deploying
```bash
cd progress-server && pip install fastapi uvicorn httpx && python3 test_app.py
```

## Backups
All your history is in `progress-server/data/progress.db`. Back it up with
`sqlite3 progress-server/data/progress.db ".backup backup.db"` [1].

## Sources
1. `progress-server/README.md` and `progress-server/Dockerfile` (this repo).
2. Docker docs, *docker compose up*, `--build` flag ("Build images before starting containers"): https://docs.docker.com/reference/cli/docker/compose/up/
3. `progress-server/compose.snippet.yml` (this repo): `PROGRESS_TEACHER_TOKEN: ${BOOKS_TOKEN}`, port `127.0.0.1:8089`.
4. Docker docs, *Networking in Compose* (services reach each other by service name; `network_mode`): https://docs.docker.com/compose/how-tos/networking/ ; Tailscale docs, *Using Tailscale with Docker* (`TS_SERVE_CONFIG`): https://tailscale.com/kb/1282/docker
5. `progress-server/app.py` lines 11 and 281 (routes served at `/` and under `/progress`).

## Update 2026-10-05: your actual setup (`network_mode: service:ts-books`)
Your book-server shares the Tailscale container's network (`network_mode: service:ts-books`). That's why
`127.0.0.1:8088` works from inside ts-books: both share one network namespace [4]. progress-server must join
the same namespace, and then it **can't have a `ports:` section**. Docker refuses to publish ports on a container
that uses another container's network, so `docker compose up` fails [6]. Use this block instead of the snippet:

```yaml
  progress-server:
    build: ./progress-server
    restart: unless-stopped
    network_mode: service:ts-books        # same as book-server; no ports: section
    depends_on: [ts-books]
    environment:
      PROGRESS_TEACHER_TOKEN: ${BOOKS_TOKEN}
      PROGRESS_DB: /data/progress.db
      PROGRESS_ORIGINS: https://rahulsanjay18.github.io
    volumes:
      - ./progress-server/data:/data
```

Keep `"/progress": { "Proxy": "http://127.0.0.1:8089" }` in `serve.json`. Then run
`docker compose up -d --build --force-recreate ts-books book-server progress-server`. Recreate all three: when ts-books
restarts, the containers that share its network need recreating too, or they lose their network.

6. Docker docs, *docker run* `--network container:<name>` ("the new container ... can't publish ports"): https://docs.docker.com/engine/network/#container-networks

## Update 2026-10-05: the `.env` file
`.env` was never in this repo; `git log --all` shows no `.env` in any commit. It belongs on the server, in the same
folder as `docker-compose.yml`, and should stay out of git because it holds secrets. Compose reads it automatically
from that folder and fills in `${BOOKS_TOKEN}`. If it's missing, compose warns "variable is not set. Defaulting to a
blank string", and book-server and progress-server start with an empty token [7].

Recreate it on the server:
```bash
cd /path/to/folder-with-docker-compose.yml
openssl rand -hex 32                 # only if you need a NEW token (see below)
nano .env                            # add the lines below
chmod 600 .env
```
```
BOOKS_TOKEN=<the token>
TS_AUTHKEY=<new Tailscale auth key>   # then use TS_AUTHKEY: ${TS_AUTHKEY} in docker-compose.yml
```
`BOOKS_TOKEN` must be the same value the cloud environment injects for books.tail59e10.ts.net (the `md_lib`
credential in the environment's settings: environment menu in the session title bar, then Edit, then API credentials).
If you can't recover the old value, make a new one and put it in both places.

7. Docker docs, *Set environment variables within your container's environment* / `.env` interpolation: https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/
