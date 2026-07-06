# BAQIS Quafu Skill

Cross-client Agent Skill for Quafu-SQC / QuarkStudio work: account/token setup, safe SDK checks, OpenQASM task code, result retrieval, and optional BAQIS QSteed compile/transpile support.

## Why this skill is more than setup

The skill is designed so an agent can keep working after installation:

- trigger on Quafu, QuarkStudio, QSteed, OpenQASM jobs, backend status, token setup, compile/transpile, and result retrieval;
- read focused reference files only when needed;
- run bundled helpers for redacted token storage, SDK smoke checks, optional QSteed setup, and local QSteed transpile validation;
- write runnable code that loads tokens from approved local storage instead of hard-coding secrets;
- block real hardware submission until the user authorizes the exact backend/circuit/shots/options.

## Install prompts

### Codex / ChatGPT agent

Copy the full prompt below:

```text
Please install the BAQIS Quafu skill for me. First ask me to choose a language: English | 中文.
If I choose English, use $skill-installer to install from this path:
https://github.com/NeoFantom/quafu-skill/tree/main/skills/en/baqis-quafu
If I choose 中文, use $skill-installer to install from this path:
https://github.com/NeoFantom/quafu-skill/tree/main/skills/zh/baqis-quafu
If a baqis-quafu skill or legacy quarkstudio skill is already installed locally, ask me before replacing it; do not overwrite silently.
After installation, run the skill's first-run workflow: ask whether I have registered Quafu-SQC, configure/store my token only through the skill's safe helper, then ask whether I want optional BAQIS QSteed compiler/transpiler support. If I say yes to QSteed, show the helper dry run first and proceed only after I approve package installation and local QSteed config creation.
After installation, remind me to restart the agent/client if required for skill discovery.
```

### 中文安装提示

```text
请帮我安装 BAQIS Quafu skill。先询问我语言选择：English | 中文。
如果我选择 English，请使用 $skill-installer 从这个路径安装：
https://github.com/NeoFantom/quafu-skill/tree/main/skills/en/baqis-quafu
如果我选择 中文，请使用 $skill-installer 从这个路径安装：
https://github.com/NeoFantom/quafu-skill/tree/main/skills/zh/baqis-quafu
如果本地已经安装了 baqis-quafu skill 或旧版 quarkstudio skill，请先询问我是否替换；不要静默覆盖。
安装后运行该 skill 的 first-run workflow：询问我是否已注册 Quafu-SQC；只通过 skill 的安全 helper 配置/保存 token；然后询问我是否要启用北京量子院 BAQIS QSteed 编译/transpiler 支持。如果我选择启用 QSteed，先展示 helper dry run，只有我同意安装包并创建本地 QSteed 配置后再继续。
安装完成后提醒我按客户端需要重启 agent/client 以加载新 skill。
```

## Client compatibility

| Client | Use |
|---|---|
| Codex / Agent Skills clients | Install a folder containing `SKILL.md` plus helpers/reference files. |
| Claude custom skills | Upload/package the skill folder; `skill.md` is included as a byte-for-byte mirror for Claude compatibility. |
| opencode / Cursor | Use the Agent Skills-compatible folder if the client supports skills; otherwise copy the folder into the client's configured skills directory and restart/reload. |

Each skill folder contains both `SKILL.md` and `skill.md`. Keep them synchronized when editing.

## Language-specific skill paths

| Language | GitHub path | Installed skill name |
|---|---|---|
| English | `skills/en/baqis-quafu` | `$baqis-quafu` |
| 中文 | `skills/zh/baqis-quafu` | `$baqis-quafu` |

The root path `baqis-quafu/` is kept as an English compatibility alias. New installs should use one of the language-specific paths above.

## Optional QSteed support

QSteed is opt-in because it installs extra Python packages and may create `~/QSteed/config.ini`.

Validated local flow in this repository:

```bash
python helpers/qsteed_setup.py          # dry run
python helpers/qsteed_setup.py --yes    # after user approval
```

The helper creates an isolated Python 3.10/3.11 venv and installs the locally validated pins:

```text
pyquafu==0.4.1
qsteed==0.2.2
```

Then it runs `helpers/qsteed_smoke.py --check-import --transpile-demo`, which performs only local checks: no Quafu token, no network call, no hardware submission.

## Safety scope

No real API token is included in this repository. The skill forbids printing credentials and forbids submitting real hardware jobs without explicit current authorization.
