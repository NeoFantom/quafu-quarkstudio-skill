# Quafu QuarkStudio Skill

## 中文安装指南

复制下面整段给 Codex / ChatGPT agent：

```text
请帮我安装 Quafu QuarkStudio skill。先询问我语言选择：English | 中文。
如果我选择 English，请使用 $skill-installer 从这个路径安装：
https://github.com/NeoFantom/quafu-quarkstudio-skill/tree/main/skills/en/quarkstudio
如果我选择 中文，请使用 $skill-installer 从这个路径安装：
https://github.com/NeoFantom/quafu-quarkstudio-skill/tree/main/skills/zh/quarkstudio
如果本地已经安装了 quarkstudio skill，请先询问我是否替换；不要静默覆盖。安装完成后，请提醒我重启 Codex 以加载新 skill。
```

## English installation guide

Copy the full prompt below into Codex / ChatGPT agent:

```text
Please install the Quafu QuarkStudio skill for me. First ask me to choose a language: English | 中文.
If I choose English, use $skill-installer to install from this path:
https://github.com/NeoFantom/quafu-quarkstudio-skill/tree/main/skills/en/quarkstudio
If I choose 中文, use $skill-installer to install from this path:
https://github.com/NeoFantom/quafu-quarkstudio-skill/tree/main/skills/zh/quarkstudio
If a quarkstudio skill is already installed locally, ask me before replacing it; do not overwrite silently. After installation, remind me to restart Codex so the new skill is loaded.
```

## Language-specific skill paths

| Language | GitHub path | Installed skill name |
|---|---|---|
| English | `skills/en/quarkstudio` | `$quarkstudio` |
| 中文 | `skills/zh/quarkstudio` | `$quarkstudio` |

The legacy root path `quarkstudio/` is kept as an English compatibility alias. New installs should use one of the language-specific paths above.

## What this skill does

- First asks whether the user has registered a Quafu-SQC account.
- If not registered, guides the user to the registration walkthrough screenshot: <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>.
- After registration, asks for an API token or, with explicit user permission, opens the Quafu-SQC login page and retrieves the token from an authenticated browser session via opencli.
- Stores tokens locally without printing them, defaulting to `~/.config/quarkstudio/credentials.env` with restrictive permissions.
- Supports basic QuarkStudio tasks only: install/import checks, backend status, OpenQASM 2.0 task dictionaries, submission gate, and result retrieval.

## Safety scope

No real API token is included in this repository. The skill forbids printing credentials and forbids submitting real hardware jobs without explicit current authorization.
