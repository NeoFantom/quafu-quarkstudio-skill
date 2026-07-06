# QuarkStudio / Quafu-SQC platform information

All items here are `[DURABLE]` unless marked otherwise.

## Identity

- `[DURABLE]` Platform: Quafu-SQC / Quafu cloud.
- `[DURABLE]` Operator: BAQIS.
- `[DURABLE]` This skill covers infrastructure and code-generation workflows: authentication, SDK installation, backend status, basic OpenQASM task submission/result retrieval, and optional QSteed local compile/transpile support.

## Official URLs

- `[DURABLE]` Quafu-SQC documentation: <https://quafu-sqc.readthedocs.io/en/latest/>
- `[DURABLE]` Quafu-SQC login page: <https://quafu-sqc.baqis.ac.cn/login>
- `[DURABLE]` Quafu-SQC console home after login: <https://quafu-sqc.baqis.ac.cn/framework/home>
- `[DURABLE]` Registration walkthrough screenshot: <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>
- `[DURABLE]` QSteed repository: <https://github.com/BAQIS-Quantum/QSteed>
- `[DURABLE]` Support email shown in public Quafu docs: `quafu_ts@baqis.ac.cn`

## QuarkStudio SDK and import mapping

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

- `[DURABLE]` Do not confuse QuarkStudio with older/general `pyquafu` examples. For QuarkStudio cloud tasks, use the `quarkstudio` package and `quark.Task` API unless a fresh investigation proves the platform changed.

## Optional QSteed package mapping

- `[DURABLE]` QSteed repository: `BAQIS-Quantum/QSteed`, Apache-2.0 license, latest GitHub release observed during this update: `v0.2.2` published 2024-10-22.
- `[DURABLE]` Upstream install docs say QSteed needs `pyquafu` and installs with `pip install qsteed`.
- `[LOCAL-VALIDATED]` For this skill, use `pyquafu==0.4.1` and `qsteed==0.2.2` in a Python 3.10/3.11 venv; newer `pyquafu==0.4.5` failed against QSteed 0.2.2 in local validation.
- `[DURABLE]` Local transpiler use does not need a Quafu token. QSteed compiler/resource-manager deployment requires MySQL/configuration; see `qsteed.md`.

## Credential model

- `[DURABLE]` QuarkStudio uses an API token passed to `Task(token)`.
- `[DURABLE]` Public docs state tokens expire after 30 days; treat expiration as a runtime check and re-run first-run bootstrap if auth fails.
- `[DURABLE]` Default user-level credential storage for this skill: `$XDG_CONFIG_HOME/baqis-quafu/credentials.env`, falling back to `~/.config/baqis-quafu/credentials.env`, containing `QUAFU_API_TOKEN=...`, directory mode `0700`, file mode `0600`.
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
- `[LOCAL]` QSteed local transpiler smoke checks are safe local code execution; they do not authenticate or submit hardware jobs.

## Confirmation basis

- Quafu-SQC public documentation confirms QuarkStudio package/install/import/status/run/result basics.
- Quafu-SQC console behavior confirms browser token endpoints and manual login constraints.
- QSteed GitHub README confirms package purpose, install routes, transpiler API, and MySQL-backed compiler deployment requirements.
- Local validation confirms the pinned QSteed smoke path used by `helpers/qsteed_setup.py` and `helpers/qsteed_smoke.py`.
