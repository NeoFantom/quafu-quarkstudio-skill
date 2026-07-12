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

## Submission policy and guarded workflow

`tmgr.run(task)` is asynchronous, quota-consuming cloud submission. Do not call it directly. `helpers/submission_policy.py` provides the only submission boundary and defaults to `confirm_each`.

### Exact-job confirmation (default)

Build the final task first, then bind approval to every field:

```python
from helpers.submission_policy import exact_confirmation, submit_authorized

fingerprint = exact_confirmation(task)
print("exact job fingerprint:", fingerprint)
# Show the exact task summary and obtain the user's explicit approval of this fingerprint now.
tid = submit_authorized(tmgr, task, exact_approval=fingerprint)
print("task id:", tid)  # fsync-persisted before submit_authorized returns
```

The agent must not treat computing or displaying the fingerprint as approval. A changed backend, circuit, shots, name, or option requires a new fingerprint and new confirmation.

### Explicit bounded autonomous mode

Only after explicit user opt-in, run:

```bash
python3 helpers/submission_policy.py authorize-autonomous \
  --backend Dongling --max-shots-per-job 4096 --max-jobs 3 \
  --expires-at '2026-07-13T18:00:00+08:00'
python3 helpers/submission_policy.py show
```

Then the bounded flow is: design the in-scope task -> `submit_authorized(tmgr, task)` -> poll the persisted `tid` with `tmgr.result(tid)` -> analyze. Authorization is checked before every submission and is never inferred. To stop autonomy immediately:

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

The captured official lesson lists important result fields: `count`, `corrected`, `transpiled`, `status`, `tid`, `error`, `finished`, and `qlisp`. Treat the result schema as source-backed but still inspect actual returned keys at runtime. Confirmation: Quafu-SQC official docs snapshot summarized in `platform-info.md`; confidence: doc snapshot.

## Official submission semantics

The official Quafu-SQC Quick Guide documents that `tmgr.run(task)` submits a task asynchronously and immediately returns its task ID, while `tmgr.result(tid)` retrieves the result: <https://quafu-sqc.readthedocs.io/en/latest/#quick-guide>. Treat `run` as a real cloud submission boundary, not a local preview.
