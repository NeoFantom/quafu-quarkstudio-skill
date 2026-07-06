# QuarkStudio / Quafu-SQC platform information

All items here are `[DURABLE]` unless marked otherwise.

## Identity

- `[DURABLE]` Platform: Quafu-SQC / Quafu cloud.
- `[DURABLE]` Operator/provider: BAQIS.
- `[DURABLE]` Project registry key in `quantum-benchmarking`: `platforms/baqis-quafu`.
- `[DURABLE]` Platform taxonomy: `single_vendor`; provider and hardware vendor are both `baqis` / BAQIS for this project context.
- `[DURABLE]` This skill is infrastructure-only: authentication, SDK installation, backend status, basic OpenQASM task submission, and result retrieval. It does not bundle advanced algorithms or benchmark suites.

## Official URLs

- `[DURABLE]` Documentation: <https://quafu-sqc.readthedocs.io/en/latest/>
- `[DURABLE]` Login page: <https://quafu-sqc.baqis.ac.cn/login>
- `[DURABLE]` Console home after login: <https://quafu-sqc.baqis.ac.cn/framework/home>
- `[DURABLE]` Registration walkthrough screenshot: <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>
- `[DURABLE]` Support email shown in the captured docs: `quafu_ts@baqis.ac.cn`

## SDK and import mapping

- `[DURABLE]` Python package: `quarkstudio`.
- `[DURABLE]` Python version requirement in the captured official lesson: Python `>=3.12`.
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
- `[DURABLE]` Captured official docs state tokens expire after 30 days; treat expiration as a runtime check and re-run first-run bootstrap if auth fails.
- `[DURABLE]` Default user-level credential storage for this skill: `~/.config/quarkstudio/credentials.env` containing `QUAFU_API_TOKEN=...`, directory mode `0700`, file mode `0600`.
- `[DURABLE]` Project-level storage, only if explicitly selected: `secrets.yaml` top-level key `baqis-quafu`, field `key`.
- `[DURABLE]` Browser-assisted retrieval uses an already logged-in Quafu-SQC console session, not password automation. Known authenticated endpoints from the captured UI bundle are:
  - `GET /api/api-token` returns `api_token`;
  - `POST /api/api-token` refreshes the token;
  - `GET /api/api-token-expiration` returns `api_token_exp`;
  - requests require browser credentials/cookies.

## Basic operation surface

- `[LIVE]` Backend availability and queue depth are fetched at runtime with `tmgr.status()`.
- `[DURABLE]` Basic task submission uses an OpenQASM 2.0 string in a task dict with keys such as `chip`, `name`, `circuit`, `shots`, and `options`.
- `[DURABLE]` Captured docs state `shots` should be an integer multiple of `1024`.
- `[DURABLE]` `tmgr.run(task)` submits asynchronously and returns a task id; `tmgr.result(tid)` fetches result data.

## Confirmation basis

- Official Quafu-SQC docs snapshot from the prior Quafu lesson workspace confirmed package/install/import/status/run/result basics.
- Quafu-SQC console JavaScript bundle snapshot confirmed browser token endpoints and manual login constraints.
- Project `platforms/PLATFORMS.md` confirmed the project-local platform key and taxonomy.
