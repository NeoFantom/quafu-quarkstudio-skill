[English](README.md)

# BAQIS Quafu Skill

面向 Quafu-SQC / QuarkStudio 工作流的跨客户端 Agent Skill：账号/token 设置、安全 SDK 检查、OpenQASM 任务代码、结果读取，以及可选 BAQIS QSteed 编译/transpile 支持。

## 为什么这个 skill 不只是安装配置

这个 skill 的设计目标是让 agent 在安装后能持续完成实际工作：

- 在用户提到 Quafu、QuarkStudio、QSteed、OpenQASM 任务、backend status、token 设置、compile/transpile 和结果读取时触发；
- 只在需要时读取聚焦 reference 文件；
- 运行 bundled helper 完成 redacted token 存储、SDK smoke check、可选 QSteed 设置和本地 QSteed transpile 验证；
- 编写可运行代码，从已批准的本地存储读取 token，而不是把 secret 硬编码进代码；
- 在真实硬件提交前阻止副作用，直到用户授权明确的 backend/circuit/shots/options。

## 安装提示词

语言选择是必需的。安装器必须在安装前选择且只选择一个语言目录；没有顶层目录 fallback，也没有默认语言。

复制下面完整提示词：

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

## 客户端兼容性

| 客户端 | 使用方式 |
|---|---|
| Codex / Agent Skills 客户端 | 安装包含 `SKILL.md`、helper 和 reference 文件的目录。 |
| Claude custom skills | 上传/打包该 skill 目录；其中 `skill.md` 是为 Claude 兼容保留的字节一致镜像。 |
| opencode / Cursor | 如果客户端支持 skills，使用 Agent Skills 兼容目录；否则把目录复制到客户端配置的 skills 目录并重启/重新加载。 |

每个 skill 目录都包含 `SKILL.md` 和 `skill.md`。编辑时必须保持二者同步。

## 按语言区分的 skill 路径

| 语言 | GitHub 路径 | 安装后的 skill 名称 |
|---|---|---|
| English | `skills/en/baqis-quafu` | `$baqis-quafu` |
| 中文 | `skills/zh/baqis-quafu` | `$baqis-quafu` |

只有上面两个按语言区分的路径可以安装。本仓库刻意不提供顶层 `baqis-quafu/` skill 目录，因为安装器必须根据显式语言选择路由。

## 可选 QSteed 支持

QSteed 是 opt-in 的，因为它会安装额外 Python 包，并可能创建 `~/QSteed/config.ini`。

本仓库中验证过的本地流程：

```bash
cd skills/en/baqis-quafu  # or: cd skills/zh/baqis-quafu
python helpers/qsteed_setup.py          # dry run
python helpers/qsteed_setup.py --yes    # after user approval
```

helper 会创建隔离 Python 3.10/3.11 venv，并安装本地验证过的 pins：

```text
pyquafu==0.4.1
qsteed==0.2.2
```

然后运行 `helpers/qsteed_smoke.py --check-import --transpile-demo`，该检查只做本地验证：不读取 Quafu token、不联网、不提交硬件任务。

## 安全边界

本仓库不包含真实 API token。该 skill 禁止打印凭证，并禁止在没有当前明确授权的情况下提交真实硬件任务。
