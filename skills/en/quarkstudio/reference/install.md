# Install and smoke-check QuarkStudio

## Install

QuarkStudio requires Python `>=3.12` in the public docs and installs as:

```bash
python -m pip install quarkstudio
```

The import used by the docs is:

```python
from quark import Task
```

Confirmation: Quafu-SQC public documentation summarized in `platform-info.md`; confidence: public docs.

## Checks

Use the bundled helper for deterministic, redacted checks:

```bash
python helpers/sdk_smoke.py --check-import
```

This imports `quark.Task` but does not use a token or make network calls.

For a read-only authenticated check, ask the user first, then run:

```bash
python helpers/sdk_smoke.py --status
```

The helper loads the token from `QUAFU_API_TOKEN`, the XDG user config file, or an explicitly supplied project `.env.local`. It prints status output only; it never prints the token.
