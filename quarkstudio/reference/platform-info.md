# QuarkStudio / Quafu-SQC platform information

All items here are `[DURABLE]` unless marked otherwise.

## Identity

- `[DURABLE]` Platform: Quafu-SQC / Quafu cloud.
- `[DURABLE]` Operator: BAQIS.
- `[DURABLE]` This skill is infrastructure-only: authentication, SDK installation, backend status, basic OpenQASM task submission, and result retrieval. It does not bundle advanced algorithms or benchmark suites.

## Official URLs

- `[DURABLE]` Documentation: <https://quafu-sqc.readthedocs.io/en/latest/>
- `[DURABLE]` Login page: <https://quafu-sqc.baqis.ac.cn/login>
- `[DURABLE]` Console home after login: <https://quafu-sqc.baqis.ac.cn/framework/home>
- `[DURABLE]` Registration walkthrough screenshot: <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>
- `[DURABLE]` Support email shown in public docs: `quafu_ts@baqis.ac.cn`

## SDK and import mapping

- `[DURABLE]` Python package: `quarkstudio`.
- `[DURABLE]` Python version requirement in public docs: Python `>=3.12`.
- `[DURABLE]` Install command:

```bash
python -m pip install quarkstudio
```

- `[DURABLE]` Import and client constructor:

```python
from quark import Task
tmgr = Task(token)
```

- `[DURABLE]` Do not confuse this skill with older/general `pyquafu` examples. For this skill, use the QuarkStudio package and `quark.Task` API unless a fresh investigation proves the platform changed.

## Credential model

- `[DURABLE]` QuarkStudio uses an API token passed to `Task(token)`.
- `[DURABLE]` Public docs state tokens expire after 30 days; treat expiration as a runtime check and re-run first-run bootstrap if auth fails.
- `[DURABLE]` Default user-level credential storage for this skill: `$XDG_CONFIG_HOME/quarkstudio/credentials.env`, falling back to `~/.config/quarkstudio/credentials.env`, containing `QUAFU_API_TOKEN=...`, directory mode `0700`, file mode `0600`.
- `[DURABLE]` Optional project-local storage, only if explicitly selected: `.env.local` in the selected project root, containing `QUAFU_API_TOKEN=...`; it should be ignored by version control.
- `[DURABLE]` Browser-assisted retrieval uses an already logged-in Quafu-SQC console session, not password automation. Known authenticated endpoints from console behavior are:
  - `GET /api/api-token` returns `api_token`;
  - `POST /api/api-token` refreshes the token;
  - `GET /api/api-token-expiration` returns `api_token_exp`;
  - requests require browser credentials/cookies.

## Basic operation surface

- `[LIVE]` Backend availability and queue depth are fetched at runtime with `tmgr.status()`.
- `[DURABLE]` Basic task submission uses an OpenQASM 2.0 string in a task dict with keys such as `chip`, `name`, `circuit`, `shots`, and `options`.
- `[DURABLE]` Public docs state `shots` should be an integer multiple of `1024`.
- `[DURABLE]` `tmgr.run(task)` submits asynchronously and returns a task id; `tmgr.result(tid)` fetches result data.

## Confirmation basis

- Quafu-SQC public documentation confirms package/install/import/status/run/result basics.
- Quafu-SQC console behavior confirms browser token endpoints and manual login constraints.
