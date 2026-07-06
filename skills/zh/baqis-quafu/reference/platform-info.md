# QuarkStudio / Quafu-SQC 平台信息

除非特别标注，本文件中的条目均为 `[DURABLE]`。

## Identity

- `[DURABLE]` 平台：Quafu-SQC / Quafu cloud。
- `[DURABLE]` 运营方：BAQIS。
- `[DURABLE]` 本 skill 覆盖基础设施与代码生成工作流：认证、SDK 安装、backend status、基础 OpenQASM task 提交/结果获取，以及可选 QSteed 本地 compile/transpile 支持。

## Official URLs

- `[DURABLE]` Quafu-SQC 文档：<https://quafu-sqc.readthedocs.io/en/latest/>
- `[DURABLE]` Quafu-SQC 登录页：<https://quafu-sqc.baqis.ac.cn/login>
- `[DURABLE]` 登录后的 console home：<https://quafu-sqc.baqis.ac.cn/framework/home>
- `[DURABLE]` 注册 walkthrough 截图：<https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>
- `[DURABLE]` QSteed 仓库：<https://github.com/BAQIS-Quantum/QSteed>
- `[DURABLE]` Quafu 公开文档中展示的支持邮箱：`quafu_ts@baqis.ac.cn`

## QuarkStudio SDK and import mapping

- `[DURABLE]` Python package：`quarkstudio`。
- `[DURABLE]` 公开文档中的 Python 版本要求：Python `>=3.12`。
- `[DURABLE]` 安装命令：

```bash
python -m pip install quarkstudio
```

- `[DURABLE]` import 与 client constructor：

```python
from quark import Task
tmgr = Task(token)
```

- `[DURABLE]` 不要和旧版或泛用 `pyquafu` 示例混淆。QuarkStudio 云任务默认使用 `quarkstudio` package 与 `quark.Task` API，除非新的调查证明平台已经变化。

## 可选 QSteed package mapping

- `[DURABLE]` QSteed 仓库：`BAQIS-Quantum/QSteed`，Apache-2.0 license；本次更新观察到的最新 GitHub release：`v0.2.2`，发布于 2024-10-22。
- `[DURABLE]` 上游安装文档说明 QSteed 需要 `pyquafu`，并可用 `pip install qsteed` 安装。
- `[LOCAL-VALIDATED]` 对本 skill，使用 Python 3.10/3.11 venv 中的 `pyquafu==0.4.1` 与 `qsteed==0.2.2`；本机验证中较新的 `pyquafu==0.4.5` 与 QSteed 0.2.2 不兼容。
- `[DURABLE]` 本地 transpiler 使用不需要 Quafu token。QSteed compiler/resource-manager deployment 需要 MySQL/configuration；见 `qsteed.md`。

## Credential model

- `[DURABLE]` QuarkStudio 使用传给 `Task(token)` 的 API token。
- `[DURABLE]` 公开文档说明 token 30 天过期；把过期视为 runtime 检查，认证失败时重新走 first-run bootstrap。
- `[DURABLE]` 本 skill 默认用户级凭证位置：`$XDG_CONFIG_HOME/baqis-quafu/credentials.env`，未设置时回退到 `~/.config/baqis-quafu/credentials.env`，内容为 `QUAFU_API_TOKEN=...`，目录权限 `0700`，文件权限 `0600`。
- `[DURABLE]` 可选项目本地存储仅在用户明确选择时使用：选定项目根目录下的 `.env.local`，内容为 `QUAFU_API_TOKEN=...`；它应被版本控制忽略。
- `[DURABLE]` 浏览器辅助获取依赖已经登录的 Quafu-SQC console session，而不是密码自动化。已知认证端点来自 console 行为：
  - `GET /api/api-token` 返回 `api_token`；
  - `POST /api/api-token` 刷新 token；
  - `GET /api/api-token-expiration` 返回 `api_token_exp`；
  - 请求需要浏览器 credentials/cookies。

## Basic operation surface

- `[LIVE]` Backend 可用性和 queue depth 在运行时通过 `tmgr.status()` 获取。
- `[DURABLE]` 基础任务提交使用 OpenQASM 2.0 字符串，放在包含 `chip`、`name`、`circuit`、`shots`、`options` 等 key 的 task dict 中。
- `[DURABLE]` 公开文档说明 `shots` 应为 `1024` 的整数倍。
- `[DURABLE]` `tmgr.run(task)` 异步提交并返回 task id；`tmgr.result(tid)` 获取结果数据。
- `[LOCAL]` QSteed 本地 transpiler smoke check 是安全的本地代码执行；它不认证，也不提交硬件任务。

## Confirmation basis

- Quafu-SQC 公开文档确认了 QuarkStudio package/install/import/status/run/result 基础。
- Quafu-SQC 控制台行为确认了浏览器 token 端点和手动登录约束。
- QSteed GitHub README 确认 package 目的、安装路径、transpiler API，以及基于 MySQL 的 compiler deployment 要求。
- 本机验证确认了 `helpers/qsteed_setup.py` 与 `helpers/qsteed_smoke.py` 使用的 pin 后 QSteed smoke 路径。
