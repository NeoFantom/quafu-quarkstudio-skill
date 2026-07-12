# QuarkStudio 基础用法

本 skill 覆盖最小云端工作流：install/import、初始化 `Task`、检查 status、创建 OpenQASM 2.0 task、只在授权后提交、读取结果。可选 QSteed 支持可在 QuarkStudio 提交安全门之前，本地准备/transpile circuit。

## Status（只读）

```python
from quark import Task

tmgr = Task(token)
print(tmgr.status())
```

captured official docs 显示 `tmgr.status()` 返回 backend 名称到 queue count 的映射，或 `Offline` / `Maintenance` 等字符串。把它当作 `[LIVE]`：始终在运行时重新获取当前 status。确认方式：`platform-info.md` 汇总的 Quafu-SQC 官方文档快照；置信度：doc snapshot。

## OpenQASM 2.0 task dict

```python
circuit = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""

task = {
    "chip": "Dongling",
    "name": "BellDemo",
    "circuit": circuit,
    "shots": 1024,
    "options": {
        "compiler": "quarkcircuit",
        "correct": False,
        "open_dd": None,
        "target_qubits": [],
    },
}
```

captured official docs 说明 `shots` 应为 1024 的整数倍。确认方式：`platform-info.md` 汇总的 Quafu-SQC 官方文档快照；置信度：doc snapshot。

## 可选 QSteed 预处理

如果用户启用了 QSteed，并要求编译/transpilation 代码：

1. 读取 `qsteed.md`。
2. 在 QSteed venv 中运行 local-only smoke check。
3. 按 pin 依赖指导生成或编辑 QSteed 代码。
4. 如果 QSteed 输出用于 QuarkStudio job 的 OpenQASM，把该 OpenQASM 放入 `task["circuit"]`。
5. 执行 `tmgr.run(task)` 前仍然必须走普通提交安全门。

## 提交策略与受控工作流

`tmgr.run(task)` 是可能消耗 quota 的异步云提交。不要直接调用。`helpers/submission_policy.py` 是唯一提交边界，默认策略是 `confirm_each`。

### 精确任务确认（默认）

先构造最终 task，再把批准绑定到每个字段：

```python
from helpers.submission_policy import exact_confirmation, submit_authorized

fingerprint = exact_confirmation(task)
print("exact job fingerprint:", fingerprint)
# 展示精确 task 摘要，并取得用户现在对该 fingerprint 的明确批准。
tid = submit_authorized(tmgr, task, exact_approval=fingerprint)
print("task id:", tid)  # submit_authorized 返回前已经 fsync 持久化
```

agent 不能把计算或展示 fingerprint 当作批准。backend、circuit、shots、name 或 option 任一变化，都需要新 fingerprint 和新确认。

### 明确的有边界自主模式

只有用户明确 opt-in 后，运行：

```bash
python3 helpers/submission_policy.py authorize-autonomous \
  --backend Dongling --max-shots-per-job 4096 --max-jobs 3 \
  --expires-at '2026-07-13T18:00:00+08:00'
python3 helpers/submission_policy.py show
```

之后的有边界流程是：设计范围内 task -> `submit_authorized(tmgr, task)` -> 用 `tmgr.result(tid)` 轮询已保存的 tid -> 分析。每次提交前都检查授权，绝不推断 consent。要立即停止自主模式：

```bash
python3 helpers/submission_policy.py revoke
python3 helpers/submission_policy.py show
```

## Result retrieval

```python
res = tmgr.result(tid)
print(res["status"])
print(res["count"])
```

captured official lesson 列出重要结果字段：`count`、`corrected`、`transpiled`、`status`、`tid`、`error`、`finished`、`qlisp`。这个 schema 有来源依据，但仍应在运行时检查实际返回 key。确认方式：`platform-info.md` 汇总的 Quafu-SQC 官方文档快照；置信度：doc snapshot。

## 官方提交语义

Quafu-SQC 官方 Quick Guide 说明：`tmgr.run(task)` 会异步提交任务并立即返回 task ID，`tmgr.result(tid)` 用该 ID 获取结果：<https://quafu-sqc.readthedocs.io/en/latest/#quick-guide>。必须把 `run` 视为真实云提交边界，而不是本地 preview。
