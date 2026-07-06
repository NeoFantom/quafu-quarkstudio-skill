---
name: quarkstudio
description: >-
  Installable bilingual-safe runbook for QuarkStudio, the Quafu / BAQIS quantum-cloud SDK. Use whenever the task touches QuarkStudio or Quafu: checking whether the user is registered, guiding account registration, installing/checking the SDK, configuring an API token, using opencli/browser login to obtain a token, storing credentials safely in user-level or explicit dotenv locations, checking backend status, submitting basic OpenQASM 2.0 tasks, polling results, or handling token expiration. Do not answer Quafu operational questions from memory — read the matching reference file first, never print credentials, and never submit real hardware jobs without explicit current authorization.
---

# QuarkStudio / Quafu skill

QuarkStudio is the Python SDK for BAQIS Quafu-SQC. This is a standalone public skill: do not assume any private repository layout, registry path, local secrets file convention, or project-specific data pipeline. Durable platform identity lives in `reference/platform-info.md`; operational steps live in the focused reference file plus the helper script named in the capability map. Do not scrape or submit live jobs unless the user explicitly asks and the safety gate allows it.

## Hard rules

1. **Never print or log a Quafu API token.** Treat browser responses, env files, command output, screenshots, and error messages as potential leak surfaces.
2. **Ask whether the user has registered first.** If not, guide them to the registration screenshot and wait until they complete registration before requesting an API token.
3. **Ask for an existing token after registration.** If the registered user has no token, ask for explicit permission before opening a browser or using `opencli` to help retrieve one.
4. **Browser token retrieval is user-assisted.** Open the Quafu login page, let the user log in manually, then call the authenticated browser endpoint with cookies. Do not automate password entry.
5. **Store credentials only in an approved local destination.** Default to the XDG user config file `$XDG_CONFIG_HOME/quarkstudio/credentials.env` or `~/.config/quarkstudio/credentials.env`; use project-local `.env.local` only when the user explicitly chooses per-project dotenv storage.
6. **Do not submit hardware jobs as a side effect.** `tmgr.status()` and import checks are safe read-only checks; `tmgr.run(task)` requires explicit current authorization and a saved task id.
7. **Use basic QuarkStudio only.** This skill covers install/check, `from quark import Task`, status, OpenQASM 2.0 task dicts, `tmgr.run`, and `tmgr.result`; do not add advanced algorithms or benchmark suites here.

## Capability map

| Need | Read / run |
|---|---|
| Durable platform identity, official URLs, package/import mapping | `reference/platform-info.md` |
| First-run registration gate, token setup, browser-assisted retrieval, storage choices | `reference/auth.md` |
| Install/check SDK and run read-only smoke checks | `reference/install.md`; `helpers/sdk_smoke.py` |
| Backend status, task dict shape, submit/result workflow | `reference/basic-usage.md` |
| Safety gates for real hardware submission and secret handling | `reference/safety.md` |
| Retrieve token from a logged-in browser without printing it | `helpers/retrieve_token_opencli.py` |
| Store a token with restrictive local permissions | `helpers/store_token.py` |

## First-run workflow

1. Ask: “Have you already registered a Quafu-SQC account?”
2. If no: guide the user to the registration screenshot at <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png> and wait until they say registration is complete. Do not request or retrieve an API token before registration is done.
3. If yes or after registration completes: ask “Do you already have a Quafu API token you want me to store/use?”
4. If yes: receive it through a private/approved channel, then store it with `helpers/store_token.py --destination user-env --token-stdin` unless the user explicitly chooses project-local dotenv storage.
5. If no: ask permission to open the Quafu login page via `opencli`.
6. After permission: run `opencli browser quafu-token open https://quafu-sqc.baqis.ac.cn/login`, tell the user to log in manually, then run `helpers/retrieve_token_opencli.py --session quafu-token --store user-env`.
7. Verify without exposing the token: run `helpers/sdk_smoke.py --check-import`; only run `helpers/sdk_smoke.py --status` after the user confirms a read-only authenticated status check is OK.

## 30-second mental model

```python
from quark import Task

tmgr = Task("YOUR_QUAFU_TOKEN")      # load from a local secret file, never hard-code
print(tmgr.status())                 # read-only backend queue/status

task = {
    "chip": "Dongling",
    "name": "MyJob",
    "circuit": """OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];""",
    "shots": 1024,
    "options": {"compiler": "quarkcircuit", "correct": False, "open_dd": None, "target_qubits": []},
}
# Quota-consuming on real QPU: ask first, then persist tid immediately.
tid = tmgr.run(task)
res = tmgr.result(tid)
```

## Provenance

- QuarkStudio install/import/status/run/result basics: Quafu-SQC public documentation summarized in `reference/platform-info.md`, `reference/install.md`, and `reference/basic-usage.md`.
- Browser token endpoints: Quafu-SQC console behavior summarized in `reference/auth.md` (`GET /api/api-token`, `POST /api/api-token`, `GET /api/api-token-expiration`, all with browser credentials).
- Login should remain manual: the Quafu-SQC login flow may include anti-bot branches; this skill must not automate password entry.
