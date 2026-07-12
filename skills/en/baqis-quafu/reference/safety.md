# Safety gates

## Real hardware / quota gate

Submission policy is persisted locally and defaults to `confirm_each`; absence of a policy file never implies autonomy. Never infer consent from a token, an earlier submission, a request to design a circuit, or permission to poll/analyze.

Inspect the current policy:

```bash
python3 helpers/submission_policy.py show
```

Choose one of two modes:

1. **Confirm every exact job (default).** Keep or restore it with `python3 helpers/submission_policy.py confirm-each`. Construct the final task, compute `exact_confirmation(task)`, show the backend/chip, name, circuit summary/path, shots, all options, expected quota impact, task-id log location, and fingerprint. Continue only when the user explicitly approves that fingerprint for this current job. Changing any task field invalidates the approval.
2. **Bounded autonomous design -> submit -> poll -> analyze.** Only after the user explicitly opts in, persist all required bounds with a timezone-aware future expiry:

```bash
python3 helpers/submission_policy.py authorize-autonomous \
  --backend Dongling \
  --max-shots-per-job 4096 \
  --max-jobs 3 \
  --expires-at '2026-07-13T18:00:00+08:00'
```

The helper checks backend, shots, remaining job count, and expiry before submission. Within those bounds the agent may design the task, call `submit_authorized(...)`, poll the immediately persisted task id with `tmgr.result(tid)`, and analyze the result. It must stop when any bound is exceeded or the grant expires; a new grant requires another explicit opt-in.

Revoke autonomy at any time (this restores `confirm_each`) and inspect the result:

```bash
python3 helpers/submission_policy.py revoke
python3 helpers/submission_policy.py show
```

Every real submission must call `submit_authorized(...)`; never call `tmgr.run(task)` directly. The helper validates authorization before the network call and fsync-appends the returned task id as its first action after the SDK returns.

## Read-only and local operations

These are appropriate after the relevant setup gate, but still avoid surprise network calls:

- importing `quark.Task` (no token, no network);
- loading a token from approved storage;
- `tmgr.status()` after the user agrees to a read-only authenticated check;
- `tmgr.result(tid)` for an existing task id supplied or already persisted;
- QSteed local import/transpile smoke checks after the user opts into QSteed package installation.

## QSteed boundaries

- QSteed transpiler demos are local code execution; they do not authorize Quafu hardware submission.
- QSteed setup installs packages and may create `~/QSteed/config.ini`; run only after opt-in.
- QSteed `Compiler`/`compiler_api` paths can require MySQL/resource database deployment and may be part of a real device control pipeline; do not run those paths unless the user explicitly asks for that deployment/configuration.
- A compiled OpenQASM circuit must still pass the QuarkStudio submission gate before `tmgr.run(task)`.

## Secret leak prevention

- Prefer `helpers/retrieve_token_opencli.py --store ...` over manually copying token values.
- Prefer `helpers/store_token.py --token-stdin` if the user provides a token directly.
- Never place tokens in command history via `--token VALUE` arguments.
- Redact all environment dumps; never run `env` or `set` in a context where `QUAFU_API_TOKEN` may appear.

## Official submission semantics

The official Quafu-SQC Quick Guide documents that `tmgr.run(task)` submits a task asynchronously and immediately returns its task ID, while `tmgr.result(tid)` retrieves the result: <https://quafu-sqc.readthedocs.io/en/latest/#quick-guide>. Treat `run` as a real cloud submission boundary, not a local preview.
