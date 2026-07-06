# Install and smoke-check QuarkStudio

## Install

QuarkStudio requires Python `>=3.12` in the captured official lesson and installs as:

```bash
python -m pip install quarkstudio
```

The import used by the lesson is:

```python
from quark import Task
```

Confirmation: Quafu-SQC official docs snapshot summarized in `platform-info.md`; confidence: doc snapshot.

## Checks

Use the bundled helper for deterministic, redacted checks:

```bash
python .claude/skills/quarkstudio/helpers/sdk_smoke.py --check-import
```

This imports `quark.Task` but does not use a token or make network calls.

For a read-only authenticated check, ask the user first, then run:

```bash
python .claude/skills/quarkstudio/helpers/sdk_smoke.py --status
```

The helper loads the token from `QUAFU_API_TOKEN`, `~/.config/quarkstudio/credentials.env`, or project `secrets.yaml` if `--project-root` is supplied. It prints status output only; it never prints the token.
