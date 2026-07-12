# Safety gates

## 真实硬件 / quota gate

提交策略持久化在本地，默认是 `confirm_each`；策略文件不存在绝不代表允许自主提交。不能从 token、历史提交、设计电路请求或 poll/analyze 许可中推断提交授权。

检查当前策略：

```bash
python3 helpers/submission_policy.py show
```

只能选择以下两种模式之一：

1. **逐个确认精确任务（默认）。** 使用 `python3 helpers/submission_policy.py confirm-each` 保持或恢复默认模式。构造最终 task，计算 `exact_confirmation(task)`，展示 backend/chip、name、circuit 摘要/路径、shots、全部 options、预计 quota 影响、task-id 日志位置和 fingerprint。只有用户明确批准当前任务的该 fingerprint 才能继续；修改任何 task 字段都会使批准失效。
2. **有边界的自主 design -> submit -> poll -> analyze。** 只有用户明确 opt-in 后，才能用带时区的未来到期时间持久化全部必要边界：

```bash
python3 helpers/submission_policy.py authorize-autonomous \
  --backend Dongling \
  --max-shots-per-job 4096 \
  --max-jobs 3 \
  --expires-at '2026-07-13T18:00:00+08:00'
```

helper 会在提交前检查 backend、shots、剩余任务数和 expiry。在范围内，agent 可以设计 task、调用 `submit_authorized(...)`、用 `tmgr.result(tid)` 轮询立即持久化的 task id，再分析结果。任何边界超出或授权过期时必须停止；新授权必须再次明确 opt-in。

用户随时可以撤销自主模式（恢复 `confirm_each`）并检查结果：

```bash
python3 helpers/submission_policy.py revoke
python3 helpers/submission_policy.py show
```

每次真实提交必须调用 `submit_authorized(...)`；绝不直接调用 `tmgr.run(task)`。helper 在网络调用前验证授权，并在 SDK 返回后第一时间 fsync 追加 task id。

## 只读和本地操作

完成相关 setup gate 后，以下操作通常安全，但仍不要突然发起网络调用：

- import `quark.Task`（无 token、无网络）；
- 从已批准位置加载 token；
- 用户同意只读认证检查后运行 `tmgr.status()`；
- 针对用户提供或已保存的 task id 运行 `tmgr.result(tid)`；
- 用户 opt-in 安装 QSteed 包后，运行 QSteed 本地 import/transpile smoke check。

## QSteed 边界

- QSteed transpiler demo 是本地代码执行；它不等于授权 Quafu 硬件提交。
- QSteed setup 会安装包，并可能创建 `~/QSteed/config.ini`；只能在 opt-in 后运行。
- QSteed `Compiler`/`compiler_api` 路径可能需要 MySQL/resource database deployment，也可能属于真实设备控制管线；除非用户明确要求该 deployment/configuration，否则不要运行这些路径。
- compiled OpenQASM circuit 在 `tmgr.run(task)` 前仍必须经过 QuarkStudio 提交安全门。

## Secret leak prevention

- 优先用 `helpers/retrieve_token_opencli.py --store ...`，不要手工复制 token 值。
- 如果用户直接提供 token，优先用 `helpers/store_token.py --token-stdin`。
- 不要通过 `--token VALUE` 参数把 token 放入 shell history。
- 对环境 dump 做 redaction；在可能存在 `QUAFU_API_TOKEN` 的上下文里，不要运行 `env` 或 `set`。

## 官方提交语义

Quafu-SQC 官方 Quick Guide 说明：`tmgr.run(task)` 会异步提交任务并立即返回 task ID，`tmgr.result(tid)` 用该 ID 获取结果：<https://quafu-sqc.readthedocs.io/en/latest/#quick-guide>。必须把 `run` 视为真实云提交边界，而不是本地 preview。
