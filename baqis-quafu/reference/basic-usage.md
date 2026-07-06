# Basic QuarkStudio usage

This skill covers the minimal cloud workflow: install/import, initialize `Task`, check status, create OpenQASM 2.0 tasks, submit only after authorization, and read results. Optional QSteed support can prepare/transpile circuits locally before the QuarkStudio submission gate.

## Status (read-only)

```python
from quark import Task

tmgr = Task(token)
print(tmgr.status())
```

The captured official docs show `tmgr.status()` returning a mapping from backend names to either queue counts or strings like `Offline` / `Maintenance`. Treat this as `[LIVE]`: always fetch current status at runtime. Confirmation: Quafu-SQC official docs snapshot summarized in `platform-info.md`; confidence: doc snapshot.

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

Captured official docs say `shots` should be an integer multiple of 1024. Confirmation: Quafu-SQC official docs snapshot summarized in `platform-info.md`; confidence: doc snapshot.

## Optional QSteed pre-processing

If the user enabled QSteed and asks for compilation/transpilation code:

1. Read `qsteed.md`.
2. Run local-only smoke checks in the QSteed venv.
3. Generate or edit QSteed code using the pinned dependency guidance.
4. If QSteed outputs OpenQASM for a QuarkStudio job, place that OpenQASM in `task["circuit"]`.
5. Still apply the normal submission gate before `tmgr.run(task)`.

## Submission gate

`tmgr.run(task)` submits asynchronously and returns a task id. This may consume real QPU quota/credits. Before running it:

1. State backend, circuit source/path, shots, task name, and options.
2. Confirm the user authorizes this exact submission now.
3. Immediately persist the returned `tid` outside volatile chat context.

```python
tid = tmgr.run(task)
print("task id:", tid)  # safe: task id, not token
```

## Result retrieval

```python
res = tmgr.result(tid)
print(res["status"])
print(res["count"])
```

The captured official lesson lists important result fields: `count`, `corrected`, `transpiled`, `status`, `tid`, `error`, `finished`, and `qlisp`. Treat the result schema as source-backed but still inspect actual returned keys at runtime. Confirmation: Quafu-SQC official docs snapshot summarized in `platform-info.md`; confidence: doc snapshot.
