---
name: baqis-quafu
description: >-
  用于 Quafu/QuarkStudio 量子云：账号/token、SDK 安装/status、OpenQASM 任务/结果，以及可选 BAQIS QSteed 编译/transpile 配置和代码。
---

# QuarkStudio / Quafu skill

QuarkStudio 是 BAQIS Quafu-SQC 的 Python SDK。使用本 skill 时不要只做配置说明；要能实际完成 Quafu 工作：安装/检查 SDK、安全管理凭证、编写可运行的 QuarkStudio/OpenQASM 代码、可选配置 QSteed 编译能力、先在本地验证，再对真实硬件提交设置安全门。

这是跨客户端的公开 Agent Skill。`SKILL.md` 是 Agent Skills 标准文件；`skill.md` 是 Claude Custom Skills 兼容镜像，必须与 `SKILL.md` 字节一致。

## 硬规则

1. **绝不打印或记录 Quafu API token。** 浏览器响应、env 文件、命令输出、截图、错误信息都可能泄密。
2. **token 设置前先问用户是否已注册。** 未注册时先引导注册，并等用户完成后再请求或获取 token。
3. **浏览器/token 自动化前必须先问。** 只有用户明确同意后才打开 Quafu 登录页；用户手动登录；不要自动填写密码或验证码。
4. **凭证只保存到已批准的本地位置。** 默认使用用户级 XDG 配置；只有用户明确选择且 `.env.local` 已被 git 忽略时，才写项目 dotenv。
5. **绝不直接调用 `tmgr.run(task)`。** 真实提交必须通过 `helpers/submission_policy.py` / `submit_authorized(...)`。持久化默认策略是 `confirm_each`；只有用户明确选择并限定范围后，才能自主 design/submit/poll/analyze，绝不能推断授权。helper 会立即 fsync 持久化每个返回的 task id。
6. **QSteed 只有 opt-in 后才能用。** 它会安装额外包，并可能创建 `~/QSteed/config.ini`；先问，再使用 `helpers/qsteed_setup.py`。
7. **行动前读取聚焦 reference。** 不要凭记忆回答 Quafu/QSteed 操作问题。

## Capability map

| 需求 | 读取或运行 |
|---|---|
| 平台身份、官方 URL、package/import 映射 | `reference/platform-info.md` |
| first-run 注册、token 设置、浏览器辅助获取、存储 | `reference/auth.md` |
| 安装/检查 QuarkStudio，运行 redacted smoke check | `reference/install.md`; `helpers/sdk_smoke.py` |
| 可选 BAQIS QSteed 设置、transpile/compile 代码、已知 pin/workaround | `reference/qsteed.md`; `helpers/qsteed_setup.py`; `helpers/qsteed_smoke.py` |
| backend status、task dict 形状、submit/result 流程 | `reference/basic-usage.md` |
| 持久化提交策略、精确确认、有边界自主模式、检查/撤销 | `helpers/submission_policy.py`; `reference/safety.md`; `reference/basic-usage.md` |
| 从已登录浏览器取 token 且不打印 | `helpers/retrieve_token_opencli.py` |
| 检测已有凭证，或从本地终端私密采集 token | `helpers/capture_token.py` |
| 从非聊天可信通道接收 token 并以限制权限保存 | `helpers/store_token.py` |

## First-run workflow

1. 先问：“你已经注册 Quafu-SQC 账号了吗？”
2. 如果没有：引导用户查看 <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>，并等待注册完成。
3. 运行 `python3 helpers/capture_token.py` 检查 `QUAFU_API_TOKEN` 或已批准的本地凭证。若都不存在，helper 会主动在本地终端用隐藏输入采集，并直接保存到用户凭证文件；绝不要通过聊天、`request_user_input`、`AskUserQuestion`、`omx question`、MCP form elicitation 或 tool/command 参数请求 token。只有用户明确选择时才使用项目 dotenv。
4. 如果用户自愿把 token 粘贴到聊天中，绝不复述或引用。明确说明 model 和 transcript 已经收到它；保存操作不能撤销这次暴露。警告后用户可以继续使用该 token：只有 harness 能把已经收到的值通过 stdin 传入且不再次显示/记录时，才运行 `python3 helpers/store_token.py --token-stdin` 并通过 stdin 提供 token（绝不放入 command 参数/history）。建议轮换并改用安全本地采集。如果 harness 无法避免额外日志，不要 replay；运行 `helpers/capture_token.py` 在本地采集替换 token。如果需要浏览器获取，先请求许可，用 `opencli` 打开 `https://quafu-sqc.baqis.ac.cn/login`，让用户手动登录，然后运行 `helpers/retrieve_token_opencli.py --session quafu-token --store user-env`。
5. 安装后的首次引导中问一次：“你是否还要启用北京量子院 BAQIS QSteed 编译/transpiler 支持？”
6. 如果要，读取 `reference/qsteed.md`，先运行 `python helpers/qsteed_setup.py` dry run，解释 Python 3.10/3.11 + pin 依赖方案；只有用户同意安装包并创建本地 QSteed 配置后，才加 `--yes` 执行。
7. 验证时不要暴露 secret：运行 `helpers/sdk_smoke.py --check-import`；启用 QSteed 时，在 QSteed venv 内运行 `helpers/qsteed_smoke.py --check-import --transpile-demo`；只有用户允许只读认证检查后才运行 `--status`。

## 为用户写代码时

- 优先写小型可运行脚本/notebook，不要只给 prose 配置说明。
- token 从 `QUAFU_API_TOKEN`、用户 env 文件或已批准的项目 `.env.local` 读取；永远不要硬编码。
- QuarkStudio 任务要构造明确的 OpenQASM 2.0 task dict，检查 `shots` 是 1024 的整数倍，说明 backend/circuit/options，再读取 `reference/safety.md`。使用默认的精确任务 fingerprint 确认，或用户明确持久化的有边界授权；每次真实提交都通过 `submit_authorized(...)`，绝不直接运行 `tmgr.run(task)`。
- QSteed 请求要使用 pin 后的本地 QSteed 环境和 `reference/qsteed.md` 中的兼容模式；先本地 transpile/compile 验证，再把 compiled QASM 接入 QuarkStudio；下游提交仍需用户授权。
- 如果客户端不能执行 bundled scripts，给出 helper dry run 里的精确命令，并保持同样安全门。

## 30 秒 QuarkStudio 模型

```python
from quark import Task

tmgr = Task(token)                   # 从本地 secret 读取，永远不要硬编码
print(tmgr.status())                 # 只读 backend queue/status

task = {
    "chip": "Dongling",
    "name": "BellDemo",
    "circuit": """OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];""",
    "shots": 1024,
    "options": {"compiler": "quarkcircuit", "correct": False, "open_dd": None, "target_qubits": []},
}
# 确保 helpers/ 可 import（例如从 skill 根目录运行脚本）。
from helpers.submission_policy import exact_confirmation, submit_authorized

# confirm_each 是默认值：展示精确 task + fingerprint，并取得用户明确批准。
approval = exact_confirmation(task)
tid = submit_authorized(tmgr, task, exact_approval=approval)  # submit + 立即 fsync 记录
res = tmgr.result(tid)  # 只轮询已保存的 tid，再分析结果
```

## 证据来源

- Claude custom skill 指南：精简 `name`/`description`、resources、scripts、打包与测试。
- Agent Skills 标准：`SKILL.md` 文件夹格式、progressive disclosure、跨客户端复用。
- QSteed 官方仓库：QSteed 是 BAQIS 量子编译软件；通过 `pyquafu` + `qsteed` 安装；transpiler 可本地运行，compiler/resource manager 部署需要 MySQL 和配置。
- 本机验证：`Python 3.10.19`、`qsteed==0.2.2`、`pyquafu==0.4.1`，加 `helpers/qsteed_smoke.py` 中的 `typing` shim，成功跑通本地 transpile demo。
