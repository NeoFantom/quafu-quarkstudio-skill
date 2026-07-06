# Install and smoke-check QuarkStudio

## QuarkStudio install

QuarkStudio requires Python `>=3.12` in the public docs and installs as:

```bash
python -m pip install quarkstudio
```

The import used by the docs is:

```python
from quark import Task
```

Confirmation: Quafu-SQC public documentation summarized in `platform-info.md`; confidence: public docs.

## QuarkStudio checks

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

## Optional QSteed install

QSteed is not required for basic QuarkStudio. If the user opts into BAQIS QSteed compile/transpile support, read `qsteed.md` and use:

```bash
python helpers/qsteed_setup.py          # dry run
python helpers/qsteed_setup.py --yes    # after approval
```

The locally validated QSteed path uses Python 3.10/3.11, an isolated venv, `pyquafu==0.4.1`, and `qsteed==0.2.2`. Do not install QSteed into the user project implicitly.
