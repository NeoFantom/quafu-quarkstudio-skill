# QuarkStudio / Quafu auth and credential bootstrap

## Source-backed facts

- `[DURABLE]` A Quafu-SQC account must exist before token setup. If the user is not registered, guide them to the public registration screenshot: <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>. Confidence: public walkthrough asset.
- `[DURABLE]` QuarkStudio initializes with `from quark import Task` and `Task("token")`. Confirmation: Quafu-SQC public documentation summarized in `platform-info.md`; confidence: public docs.
- `[DURABLE]` The official lesson states a token expires after 30 days and should be requested again after expiry. Confirmation: Quafu-SQC public documentation summarized in `platform-info.md`; confidence: public docs.
- `[DURABLE]` The Quafu-SQC UI has an authenticated `GET /api/api-token` response field named `api_token`, a `POST /api/api-token` refresh path, and `GET /api/api-token-expiration`; requests use browser credentials. Confirmation: console behavior snapshot; confidence: UI behavior snapshot.
- `[DURABLE]` Login uses `/api/token` from a form flow that may include anti-bot checks. Confirmation: console login behavior snapshot; confidence: UI behavior snapshot. Therefore agents must not automate password entry; let the user log in.

## First-run decision tree

1. Ask whether the user has already registered a Quafu-SQC account.
2. If the user has not registered, guide them to this registration screenshot and wait for them to finish registration:

```text
https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png
```

Do not ask for, retrieve, or store an API token until the user says registration is complete.

3. If the user is already registered or has just completed registration, ask whether they already have a Quafu API token.
4. Run `python3 helpers/capture_token.py`. It first detects `QUAFU_API_TOKEN` and approved local credential files. If absent, it reads hidden input directly from the local terminal and stores it without placing token bytes in chat, model-visible question results, tool arguments, or command arguments.
5. If the user voluntarily already pasted a token into chat, never echo or quote it. State plainly that the model and transcript already received it and that storing it cannot undo that exposure. After this warning, the user may continue with that token. Only when the harness can pass the already-received value to stdin without another visible echo or log, invoke `python3 helpers/store_token.py --token-stdin` and supply it through stdin; never put it in command arguments or shell history. Recommend rotation and secure local capture. If the harness cannot avoid additional logging, do not replay the token; run `helpers/capture_token.py` so the user can enter a replacement locally. Do not claim that masking a chat form or later local storage made the original paste secret.
6. If the user does not have a token, ask for permission to open the browser and help retrieve it.
7. If approved, run:

```bash
opencli browser quafu-token open https://quafu-sqc.baqis.ac.cn/login
```

Then tell the user to log in manually. Do not fill username/password yourself.

8. After the user says they are logged in, retrieve and store without printing the token:

```bash
python helpers/retrieve_token_opencli.py --session quafu-token --store user-env
```

Use `--store project-env --project-root PATH` only if the user explicitly chooses per-project dotenv storage.

## Storage destinations

### Default: XDG user config file

`$XDG_CONFIG_HOME/baqis-quafu/credentials.env`, falling back to `~/.config/baqis-quafu/credentials.env`.

The helper writes:

```bash
QUAFU_API_TOKEN=<redacted-secret-value>
```

with directory mode `0700` and file mode `0600`. Future agents can load it with shell or Python dotenv-style parsing.

### Explicit project option: `.env.local`

Only use this when the user chooses per-project storage. The helper writes or updates:

```bash
QUAFU_API_TOKEN=<redacted-secret-value>
```

in `.env.local` under the selected project root, with file mode `0600`. If the selected root is a git repository, the helper refuses to write `.env.local` unless git ignores it, because project-local secrets must not be committed. Add `.env.local` to `.gitignore`, choose `user-env`, or intentionally pass `--allow-unignored-project-env` after explaining the risk.

## Token hygiene checklist

- Never paste the token into source files, task JSON, logs, screenshots, or replies.
- Do not run commands with the token as a visible command-line argument; prefer stdin or browser retrieval.
- Do not pass an entire secrets dict to SDK constructors or error-prone wrappers.
- When reporting success, say where the token was stored and whether an expiration timestamp was available; never include the token value.

## Capability boundary

Agent Skills has no portable secret-input primitive; its instructions are loaded into model context: <https://agentskills.io/specification>. MCP forbids sensitive data in form elicitation and reserves URL mode for out-of-band secret flows: <https://modelcontextprotocol.io/specification/draft/client/elicitation>. Therefore ordinary chat questions, Codex `request_user_input`, and Claude Code `AskUserQuestion`, and `omx question` must be treated as model-visible, not secret channels; use the local terminal capture helper or an external browser/OAuth flow instead.
