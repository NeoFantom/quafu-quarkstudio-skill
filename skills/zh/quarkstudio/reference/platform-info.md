# QuarkStudio / Quafu-SQC 平台信息

除非特别标注，本文件中的条目均为 `[DURABLE]`。

## Identity

- `[DURABLE]` 平台：Quafu-SQC / Quafu cloud。
- `[DURABLE]` 运营方 / provider：BAQIS。
- `[DURABLE]` `quantum-benchmarking` 项目 registry key：`platforms/baqis-quafu`。
- `[DURABLE]` 平台类型：`single_vendor`；在本项目语境下 provider 与 hardware vendor 均为 `baqis` / BAQIS。
- `[DURABLE]` 本 skill 只做基础设施：认证、SDK 安装、backend status、基础 OpenQASM task 提交、结果获取。不包含高级算法或 benchmark 套件。

## Official URLs

- `[DURABLE]` 文档：<https://quafu-sqc.readthedocs.io/en/latest/>
- `[DURABLE]` 登录页：<https://quafu-sqc.baqis.ac.cn/login>
- `[DURABLE]` 登录后的 console home：<https://quafu-sqc.baqis.ac.cn/framework/home>
- `[DURABLE]` 注册 walkthrough 截图：<https://neofantom.github.io/quafu-lesson1/assets/screenshots/00-register.png>
- `[DURABLE]` 文档中展示的支持邮箱：`quafu_ts@baqis.ac.cn`

## SDK and import mapping

- `[DURABLE]` Python package：`quarkstudio`。
- `[DURABLE]` 官方 lesson 快照中的 Python 版本要求：Python `>=3.12`。
- `[DURABLE]` 安装命令：

```bash
python -m pip install quarkstudio
```

- `[DURABLE]` import 与 client constructor：

```python
from quark import Task
tmgr = Task(token)
```

- `[DURABLE]` 不要和旧版或泛用 `pyquafu` 示例混淆。本 skill 默认使用 QuarkStudio package 与 `quark.Task` API，除非新的调查证明平台已经变化。

## Credential model

- `[DURABLE]` QuarkStudio 使用传给 `Task(token)` 的 API token。
- `[DURABLE]` 官方文档快照说明 token 30 天过期；把过期视为 runtime 检查，认证失败时重新走 first-run bootstrap。
- `[DURABLE]` 本 skill 默认用户级凭证位置：`~/.config/quarkstudio/credentials.env`，包含 `QUAFU_API_TOKEN=...`，目录权限 `0700`，文件权限 `0600`。
- `[DURABLE]` 项目级存储仅在用户明确选择时使用：`secrets.yaml` 顶层 key `baqis-quafu`，字段 `key`。
- `[DURABLE]` 浏览器辅助获取依赖已经登录的 Quafu-SQC console session，而不是密码自动化。已知认证端点来自 captured UI bundle：
  - `GET /api/api-token` 返回 `api_token`；
  - `POST /api/api-token` 刷新 token；
  - `GET /api/api-token-expiration` 返回 `api_token_exp`；
  - 请求需要浏览器 credentials/cookies。

## Basic operation surface

- `[LIVE]` Backend 可用性和 queue depth 在运行时通过 `tmgr.status()` 获取。
- `[DURABLE]` 基础任务提交使用 OpenQASM 2.0 字符串，放在包含 `chip`、`name`、`circuit`、`shots`、`options` 等 key 的 task dict 中。
- `[DURABLE]` captured docs 说明 `shots` 应为 `1024` 的整数倍。
- `[DURABLE]` `tmgr.run(task)` 异步提交并返回 task id；`tmgr.result(tid)` 获取结果数据。

## Confirmation basis

- prior Quafu lesson workspace 中的官方 Quafu-SQC 文档快照确认了 package/install/import/status/run/result 基础。
- Quafu-SQC console JavaScript bundle snapshot 确认了浏览器 token 端点和手动登录约束。
- 项目 `platforms/PLATFORMS.md` 确认了项目内平台 key 与 taxonomy。
