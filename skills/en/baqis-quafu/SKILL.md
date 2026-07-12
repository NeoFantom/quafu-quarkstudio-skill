---
name: baqis-quafu
description: >-
  Use for Quafu/QuarkStudio quantum-cloud work: account/token setup, SDK install/status, OpenQASM jobs/results, and optional BAQIS QSteed compile/transpile setup and code.
---

# QuarkStudio / Quafu skill

QuarkStudio is the Python SDK for BAQIS Quafu-SQC. Use this skill to perform Quafu work, not just configure it: install/check SDKs, manage credentials safely, write runnable QuarkStudio/OpenQASM code, optionally set up QSteed compilation support, validate locally, then gate any real hardware submission.

This is a public cross-client Agent Skill. `SKILL.md` is the canonical Agent Skills file; `skill.md` is a byte-for-byte Claude Custom Skills compatibility mirror and must stay in sync.

## Hard rules

1. **Never print or log a Quafu API token.** Treat browser responses, env files, command output, screenshots, and errors as leak surfaces.
2. **Ask whether the user has registered before token setup.** If not registered, guide registration and wait before requesting or retrieving a token.
3. **Ask before browser/token automation.** Open Quafu login only after explicit permission; let the user log in manually; do not automate passwords or CAPTCHA.
4. **Store credentials only in approved local destinations.** Default to user-level XDG config; use project `.env.local` only when explicitly chosen and git-ignored.
5. **Never call `tmgr.run(task)` directly.** Real submission must go through `helpers/submission_policy.py` / `submit_authorized(...)`. The persisted default is `confirm_each`; bounded autonomous design/submit/poll/analyze is allowed only after explicit scoped opt-in and is never inferred. The helper fsync-persists every returned task id immediately.
6. **Use QSteed only after opt-in.** It installs extra packages and may create `~/QSteed/config.ini`; ask first, then use `helpers/qsteed_setup.py`.
7. **Read the focused reference before acting.** Do not answer Quafu/QSteed operational questions from memory.

## Capability map

| Need | Read / run |
|---|---|
| Platform identity, official URLs, package/import mapping | `reference/platform-info.md` |
| First-run registration, token setup, browser-assisted retrieval, storage | `reference/auth.md` |
| Install/check QuarkStudio and run redacted smoke checks | `reference/install.md`; `helpers/sdk_smoke.py` |
| Optional BAQIS QSteed setup, transpile/compile code, known pins/workarounds | `reference/qsteed.md`; `helpers/qsteed_setup.py`; `helpers/qsteed_smoke.py` |
| Backend status, task dict shape, submit/result workflow | `reference/basic-usage.md` |
| Persisted submit policy, exact confirmation, bounded autonomy, inspect/revoke | `helpers/submission_policy.py`; `reference/safety.md`; `reference/basic-usage.md` |
| Retrieve token from a logged-in browser without printing it | `helpers/retrieve_token_opencli.py` |
| Detect existing credentials or capture a token privately from the local terminal | `helpers/capture_token.py` |
| Store a token supplied by a non-chat trusted channel with restrictive permissions | `helpers/store_token.py` |

## First-run workflow

1. Ask: “Have you already registered a Quafu-SQC account?”
2. If no: guide the user to <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png> and wait until registration is complete.
3. Check for `QUAFU_API_TOKEN` or approved local credentials by running `python3 helpers/capture_token.py`. If neither exists, the helper proactively prompts on the local terminal with hidden input and stores directly to the user credential file; never request the token through chat, `request_user_input`, `AskUserQuestion`, `omx question`, MCP form elicitation, or tool/command arguments. Use project dotenv only when explicitly chosen.
4. If they voluntarily already pasted a token into chat, never repeat or quote it. State plainly that the model and transcript already received it; storage cannot undo that exposure. They may continue with that token after this warning: only when the harness can feed the already-received value to stdin without another visible echo/log, invoke `python3 helpers/store_token.py --token-stdin` with the token on stdin (never in command arguments/history). Recommend rotation and secure local capture. If the harness cannot pass it without additional logging, do not replay it; run `helpers/capture_token.py` to collect a replacement locally. If they need browser retrieval, ask permission, open `https://quafu-sqc.baqis.ac.cn/login` with `opencli`, let them log in manually, then run `helpers/retrieve_token_opencli.py --session quafu-token --store user-env`.
5. Ask once: “Do you also want optional Beijing Academy of Quantum Information Sciences QSteed compiler/transpiler support?”
6. If yes, read `reference/qsteed.md`, run `python helpers/qsteed_setup.py` as a dry run, explain the Python 3.10/3.11 + pinned dependency plan, then run with `--yes` only after the user approves installing packages and creating local QSteed config.
7. Verify without exposing secrets: run `helpers/sdk_smoke.py --check-import`; run `helpers/qsteed_smoke.py --check-import --transpile-demo` inside the QSteed venv when QSteed is enabled; run authenticated `--status` only after a read-only status check is approved.

## When writing code for users

- Prefer small runnable scripts/notebooks over prose-only setup answers.
- Load tokens from `QUAFU_API_TOKEN`, the user env file, or an approved project `.env.local`; never hard-code tokens.
- For QuarkStudio jobs, construct explicit OpenQASM 2.0 task dicts, validate `shots` as a multiple of 1024, summarize backend/circuit/options, then read `reference/safety.md`. Use the default exact-job fingerprint confirmation or an explicitly persisted bounded grant; every real submission goes through `submit_authorized(...)`, never direct `tmgr.run(task)`.
- For QSteed requests, use the pinned local QSteed environment and the compatibility pattern in `reference/qsteed.md`; first run local transpile/compile checks, then feed compiled QASM into QuarkStudio only if the user authorizes the downstream submission.
- If a client cannot execute bundled scripts, provide the exact commands from the helper dry run and keep the same safety gates.

## 30-second QuarkStudio model

```python
from quark import Task

tmgr = Task(token)                   # load from local secret storage, never hard-code
print(tmgr.status())                 # read-only backend queue/status

task = {
    "chip": "Dongling",
    "name": "BellDemo",
    "circuit": """OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];""",
    "shots": 1024,
    "options": {"compiler": "quarkcircuit", "correct": False, "open_dd": None, "target_qubits": []},
}
# helpers/ must be importable (for example, run this script from the skill root).
from helpers.submission_policy import exact_confirmation, submit_authorized

# confirm_each is default: show the exact task + fingerprint and obtain explicit approval.
approval = exact_confirmation(task)
tid = submit_authorized(tmgr, task, exact_approval=approval)  # run + immediate fsync log
res = tmgr.result(tid)  # poll only the persisted tid, then analyze the result
```

## Provenance

- Claude custom skill guidance: concise `name`/`description`, resources, scripts, packaging, and testing.
- Agent Skills standard: `SKILL.md` folder format with progressive disclosure and cross-client reuse.
- QSteed official repository: QSteed is BAQIS quantum compilation software; installs via `pyquafu` + `qsteed`; transpiler works locally, while compiler/resource manager deployment requires MySQL and config.
- Local validation: `Python 3.10.19`, `qsteed==0.2.2`, `pyquafu==0.4.1`, plus the `typing` shim in `helpers/qsteed_smoke.py` successfully ran a local transpile demo.
