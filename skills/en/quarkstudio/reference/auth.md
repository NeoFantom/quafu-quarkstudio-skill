# QuarkStudio / Quafu auth and credential bootstrap

## Source-backed facts

- `[DURABLE]` A Quafu-SQC account must exist before token setup. If the user is not registered, guide them to the registration screenshot: <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>. Confirmation: project lesson asset supplied by the user; confidence: project walkthrough asset.
- `[DURABLE]` QuarkStudio initializes with `from quark import Task` and `Task("token")`. Confirmation: Quafu-SQC official docs snapshot summarized in `platform-info.md`; confidence: doc snapshot.
- `[DURABLE]` The official lesson states a token expires after 30 days and should be requested again after expiry. Confirmation: Quafu-SQC official docs snapshot summarized in `platform-info.md`; confidence: doc snapshot.
- `[DURABLE]` The Quafu-SQC UI has an authenticated `GET /api/api-token` response field named `api_token`, a `POST /api/api-token` refresh path, and `GET /api/api-token-expiration`; requests use browser credentials. Confirmation: console UI bundle snapshot; confidence: UI bundle snapshot.
- `[DURABLE]` Login uses `/api/token` from a form flow with reCAPTCHA/slider branches. Confirmation: console login bundle snapshot; confidence: UI bundle snapshot. Therefore agents must not automate password entry; let the user log in.

## First-run decision tree

1. Ask whether the user has already registered a Quafu-SQC account.
2. If the user has not registered, guide them to this registration screenshot and wait for them to finish registration:

```text
https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png
```

Do not ask for, retrieve, or store an API token until the user says registration is complete.

3. If the user is already registered or has just completed registration, ask whether they already have a Quafu API token.
4. If the user provides or pastes a token into a safe input channel, do not echo it. Store it immediately with `helpers/store_token.py`.
5. If the user does not have a token, ask for permission to open the browser and help retrieve it.
6. If approved, run:

```bash
opencli browser quafu-token open https://quafu-sqc.baqis.ac.cn/login
```

Then tell the user to log in manually. Do not fill username/password yourself.

7. After the user says they are logged in, retrieve and store without printing the token:

```bash
python .claude/skills/quarkstudio/helpers/retrieve_token_opencli.py --session quafu-token --store user-env
```

Use `--store project-secrets --project-root <repo>` only if the user explicitly chooses project `secrets.yaml`.

## Storage destinations

### Default: user env file

`~/.config/quarkstudio/credentials.env`

The helper writes:

```bash
QUAFU_API_TOKEN=<redacted-secret-value>
```

with directory mode `0700` and file mode `0600`. Future agents can load it with shell or Python dotenv-style parsing.

### Explicit project option: `secrets.yaml`

Only use this when the user chooses project-level storage. The helper writes under top-level key `baqis-quafu` by default:

```yaml
baqis-quafu:
  key: <redacted-secret-value>
```

The helper preserves other keys when PyYAML is available. It refuses to print the token.

## Token hygiene checklist

- Never paste the token into source files, task JSON, logs, screenshots, or replies.
- Do not run commands with the token as a visible command-line argument; prefer stdin or browser retrieval.
- Do not pass an entire secrets dict to SDK constructors or error-prone wrappers.
- When reporting success, say where the token was stored and whether an expiration timestamp was available; never include the token value.
