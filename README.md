[中文说明](README.zh.md)

# BAQIS Quafu Skill

Cross-client Agent Skill for Quafu-SQC / QuarkStudio work: account/token setup, safe SDK checks, OpenQASM task code, result retrieval, and optional BAQIS QSteed compile/transpile support.

## Why this skill is more than setup

The skill is designed so an agent can keep working after installation:

- trigger on Quafu, QuarkStudio, QSteed, OpenQASM jobs, backend status, token setup, compile/transpile, and result retrieval;
- read focused reference files only when needed;
- run bundled helpers for redacted token storage, SDK smoke checks, optional QSteed setup, and local QSteed transpile validation;
- write runnable code that loads tokens from approved local storage instead of hard-coding secrets;
- block real hardware submission until the user authorizes the exact backend/circuit/shots/options.

## Install prompt

Language selection is mandatory. The installer must choose exactly one language-specific folder before installing; there is no root-level fallback and no default language.

Copy the full prompt below:

```text
Please install the BAQIS Quafu skill for me. I must choose one language before installation: English | 中文. No default language is allowed.
If I choose English, use $skill-installer to install from this path:
https://github.com/NeoFantom/quafu-skill/tree/main/skills/en/baqis-quafu
If I choose 中文, use $skill-installer to install from this path:
https://github.com/NeoFantom/quafu-skill/tree/main/skills/zh/baqis-quafu
If I do not choose a language, stop and ask again; do not install a top-level/root baqis-quafu folder.
If a baqis-quafu skill or legacy quarkstudio skill is already installed locally, ask me before replacing it; do not overwrite silently.
After installation, run the skill's first-run workflow: ask whether I have registered Quafu-SQC, configure/store my token only through the skill's safe helper, then ask whether I want optional BAQIS QSteed compiler/transpiler support. If I say yes to QSteed, show the helper dry run first and proceed only after I approve package installation and local QSteed config creation.
After installation, remind me to restart the agent/client if required for skill discovery.
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

Only the two language-specific paths above are installable. The repository intentionally does not provide a top-level `baqis-quafu/` skill folder because installers must route by explicit language choice.

## Optional QSteed support

QSteed is opt-in because it installs extra Python packages and may create `~/QSteed/config.ini`.

Validated local flow in this repository:

```bash
cd skills/en/baqis-quafu  # or: cd skills/zh/baqis-quafu
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
