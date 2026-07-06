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

## Read-only operations

These are appropriate after credential setup, but still avoid surprise network calls:

- importing `quark.Task` (no token, no network);
- loading a token from approved storage;
- `tmgr.status()` after the user agrees to a read-only authenticated check;
- `tmgr.result(tid)` for an existing task id supplied or already persisted.

## Secret leak prevention

- Prefer `helpers/retrieve_token_opencli.py --store ...` over manually copying token values.
- Prefer `helpers/store_token.py --token-stdin` if the user provides a token directly.
- Never place tokens in command history via `--token VALUE` arguments.
- Redact all environment dumps; never run `env` or `set` in a context where `QUAFU_API_TOKEN` may appear.
