# QuarkStudio 基础用法

本 skill 只覆盖最小云端工作流：install/import、初始化 `Task`、检查 status、提交 OpenQASM 2.0 task、读取结果。

## Status（只读）

```python
from quark import Task

tmgr = Task(token)
print(tmgr.status())
```

captured official docs 显示 `tmgr.status()` 返回 backend 名称到 queue count 的映射，或 `Offline` / `Maintenance` 等字符串。把它当作 `[LIVE]`：始终在运行时重新获取当前 status。确认方式：`platform-info.md` 汇总的 Quafu-SQC 官方文档快照；置信度：doc snapshot。

## OpenQASM 2.0 task dict

lesson 使用 OpenQASM 2.0 字符串和 Python dict：

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

## Submission gate

`tmgr.run(task)` 会异步提交并返回 task id。它可能消耗真实 QPU quota/credit。运行前必须：

1. 明确说明 backend、circuit、shots、task name。
2. 确认用户现在授权这一次具体提交。
3. 立即把返回的 `tid` 保存到易恢复的位置，不能只留在聊天上下文。

```python
tid = tmgr.run(task)
print("task id:", tid)  # task id 安全；不是 token
```

## Result retrieval

```python
res = tmgr.result(tid)
print(res["status"])
print(res["count"])
```

captured official lesson 列出重要结果字段：`count`、`corrected`、`transpiled`、`status`、`tid`、`error`、`finished`、`qlisp`。这个 schema 有来源依据，但仍应在运行时检查实际返回 key。确认方式：`platform-info.md` 汇总的 Quafu-SQC 官方文档快照；置信度：doc snapshot。
