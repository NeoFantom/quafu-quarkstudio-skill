# Safety gates

## Real hardware / quota gate

Do not run `tmgr.run(task)` unless the user explicitly authorizes the exact current submission. A safe approval statement includes:

- backend/chip name;
- task name;
- circuit summary or file path;
- shots;
- whether compiler/correction/DD options are enabled;
- expected quota impact if known;
- where the returned task id will be saved.

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
