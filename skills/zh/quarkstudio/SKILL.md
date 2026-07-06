---
name: quarkstudio
description: >-
  QuarkStudio（Quafu / BAQIS 量子云 SDK）的可安装路由与安全 runbook。用于：检查用户是否已注册、引导注册、安装或检查 SDK、配置 API token、经 opencli 浏览器登录获取 token、安全保存凭证、检查 backend status、提交基础 OpenQASM 2.0 任务、轮询结果、处理 token 过期。回答 Quafu 操作问题前必须读取对应 reference；不得打印凭证；未经当前明确授权不得提交真实硬件任务。
---

# QuarkStudio / Quafu skill

QuarkStudio 是 BAQIS Quafu-SQC 的 Python SDK。稳定平台身份以 `reference/platform-info.md` 为准；具体操作步骤以 capability map 指向的 reference 文件和 helper 脚本为准。除非用户明确要求且通过安全门，不要抓取 live 页面，也不要提交真实硬件任务。

## 硬规则

1. **绝不打印或记录 Quafu API token。** 浏览器响应、env 文件、`secrets.yaml`、命令输出、截图、错误信息都可能泄密。
2. **先问用户是否已注册。** 如果未注册，先引导用户查看注册截图，并等用户完成注册后再请求 API token。
3. **注册后再问是否已有 token。** 如果注册用户没有 token，必须先征求明确许可，再打开浏览器或用 `opencli` 辅助获取。
4. **浏览器取 token 必须用户辅助。** 打开 Quafu 登录页，让用户自己登录；之后只用浏览器 cookie 调认证端点。不要自动填写用户名、密码或验证码。
5. **凭证只存到用户批准的本地位置。** 默认写 `~/.config/quarkstudio/credentials.env` 并设置严格权限；只有用户明确选择项目级 secret 时才写项目 `secrets.yaml`。
6. **不要把硬件任务作为副作用提交。** `tmgr.status()` 和 import 检查是安全的只读检查；`tmgr.run(task)` 需要当前明确授权，并且要立即保存 task id。
7. **只覆盖基础 QuarkStudio 交互。** 本 skill 只包含 install/check、`from quark import Task`、status、OpenQASM 2.0 task dict、`tmgr.run`、`tmgr.result`；不要在这里加入高级算法或 benchmark 套件。

## Capability map

| 需求 | 读取或运行 |
|---|---|
| 稳定平台身份、官方 URL、package/import 映射 | `reference/platform-info.md` |
| first-run 注册门、token 设置、浏览器辅助获取、存储选择 | `reference/auth.md` |
| 安装/检查 SDK，运行只读 smoke check | `reference/install.md`; `helpers/sdk_smoke.py` |
| backend status、task dict 形状、submit/result 流程 | `reference/basic-usage.md` |
| 真实硬件提交和 secret 处理的安全门 | `reference/safety.md` |
| 从已登录浏览器取 token 且不打印 | `helpers/retrieve_token_opencli.py` |
| 以限制权限保存 token | `helpers/store_token.py` |

## First-run workflow

1. 先问：“你已经注册 Quafu-SQC 账号了吗？”
2. 如果没有：引导用户查看注册截图 <https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>，并等用户说注册完成。注册完成前不要请求或获取 API token。
3. 如果已经注册或刚完成注册：再问“你已经有 Quafu API token，并希望我帮你保存或使用它吗？”
4. 如果有：通过安全/私密输入通道接收，不要复述 token；默认用 `helpers/store_token.py --destination user-env --token-stdin` 保存，除非用户明确选择项目 `secrets.yaml`。
5. 如果没有：询问是否允许通过 `opencli` 打开 Quafu 登录页。
6. 用户同意后：运行 `opencli browser quafu-token open https://quafu-sqc.baqis.ac.cn/login`，让用户手动登录，然后运行 `helpers/retrieve_token_opencli.py --session quafu-token --store user-env`。
7. 验证时不要暴露 token：先运行 `helpers/sdk_smoke.py --check-import`；只有用户确认允许只读认证 status check 后，才运行 `helpers/sdk_smoke.py --status`。

## 30 秒心智模型

```python
from quark import Task

tmgr = Task("YOUR_QUAFU_TOKEN")      # 从本地 secret 读取，永远不要硬编码
print(tmgr.status())                 # 只读 backend queue/status

task = {
    "chip": "Dongling",
    "name": "MyJob",
    "circuit": """OPENQASM 2.0;\ninclude \"qelib1.inc\";\nqreg q[2];\ncreg c[2];\nh q[0];\ncx q[0],q[1];\nmeasure q[0] -> c[0];\nmeasure q[1] -> c[1];""",
    "shots": 1024,
    "options": {"compiler": "quarkcircuit", "correct": False, "open_dd": None, "target_qubits": []},
}
# 真机 QPU 上可能消耗 quota：先问用户，再立刻保存 tid。
tid = tmgr.run(task)
res = tmgr.result(tid)
```

## 证据来源

- QuarkStudio install/import/status/run/result 基础：Quafu-SQC 官方文档快照，已汇总在 `reference/platform-info.md`、`reference/install.md`、`reference/basic-usage.md`。
- 浏览器 token 端点：Quafu-SQC 控制台 UI bundle 快照，已汇总在 `reference/auth.md`，包括 `GET /api/api-token`、`POST /api/api-token`、`GET /api/api-token-expiration`，都依赖浏览器 credentials。
- 登录必须保持人工：Quafu-SQC 登录流程包含反机器人分支；本 skill 不得自动填写密码或验证码。
