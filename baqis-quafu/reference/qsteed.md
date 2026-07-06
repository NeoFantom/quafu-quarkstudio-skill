# Optional BAQIS QSteed support

QSteed is optional. Ask before installing or configuring it because it adds a separate Python environment, installs packages, and may create `~/QSteed/config.ini`.

## Source-backed facts

- `[DURABLE]` QSteed is BAQIS quantum compilation software for real quantum devices. It includes a quantum compiler, resource virtualization manager, and task scheduler.
- `[DURABLE]` The upstream README says to install `pyquafu` and `qsteed`; QSteed can be installed from PyPI with `pip install qsteed`.
- `[DURABLE]` The upstream README shows a local transpiler API with `RandomCircuit`, `Backend`, `Model`, and `Transpiler` and preset optimization levels `0-3`.
- `[DURABLE]` The upstream README says the `Compiler` path requires MySQL deployment/configuration and a QSteed config file.
- `[LOCAL-VALIDATED]` On this workstation, `qsteed==0.2.2` with latest `pyquafu==0.4.5` installed but failed at import (`QuantumGate` import mismatch). `qsteed==0.2.2` with `pyquafu==0.4.1` plus the temporary typing shim in `helpers/qsteed_smoke.py` successfully ran a local transpile demo.

## Setup flow after user opts in

1. Read this file and `reference/safety.md`.
2. Run a dry-run plan:

```bash
python helpers/qsteed_setup.py
```

3. Explain that the plan uses Python 3.10/3.11, creates an isolated venv, installs these locally validated pins, then runs local smoke checks:

```bash
pyquafu==0.4.1
qsteed==0.2.2
```

4. After the user approves package installation and local QSteed config creation, run:

```bash
python helpers/qsteed_setup.py --yes
```

Use `--python /path/to/python3.10` if auto-discovery fails. Use `--venv PATH` if the user wants a project-specific environment. Use `--skip-config` when they only need local transpiler demos and do not want `~/QSteed/config.ini`.

## Smoke checks

Inside the QSteed venv, run:

```bash
python helpers/qsteed_smoke.py --check-import --transpile-demo
```

These checks are local-only: no Quafu token, no network call, no hardware submission.

## Compatibility shim for generated QSteed code

Until upstream QSteed fixes its missing typing imports, include this before importing QSteed in generated scripts that target the validated pins:

```python
import builtins
import typing

_added = []
for _name in ("List", "Dict", "Tuple", "Union", "Optional"):
    if not hasattr(builtins, _name):
        setattr(builtins, _name, getattr(typing, _name))
        _added.append(_name)

try:
    from qsteed import Backend, Model, RandomCircuit, Transpiler
finally:
    for _name in _added:
        delattr(builtins, _name)
```

Do not use this shim to hide unrelated import failures. If the error mentions `QuantumGate`, pin `pyquafu==0.4.1`.

## Minimal local transpiler example

```python
# Run with the QSteed venv Python created by helpers/qsteed_setup.py.
import builtins
import typing

_added = []
for _name in ("List", "Dict", "Tuple", "Union", "Optional"):
    if not hasattr(builtins, _name):
        setattr(builtins, _name, getattr(typing, _name))
        _added.append(_name)
try:
    from qsteed import Backend, Model, RandomCircuit, Transpiler
finally:
    for _name in _added:
        delattr(builtins, _name)

rqc = RandomCircuit(num_qubit=3, gates_number=10, gates_list=["cx", "rx", "rz", "ry", "h"])
qc = rqc.random_circuit()

basis_gates = ["cx", "rx", "ry", "rz", "id", "h"]
coupling_list = [(0, 1, 0.98), (1, 0, 0.98), (1, 2, 0.97), (2, 1, 0.97)]
backend = Backend(
    name="SkillDemoBackend",
    backend_type="superconducting",
    qubits_num=3,
    coupling_list=coupling_list,
    basis_gates=basis_gates,
)
model = Model(backend=backend)
transpiler = Transpiler(initial_model=model)
transpiled = transpiler.transpile(qc, optimization_level=1)
print(transpiled.to_openqasm())
```

## Compiler/resource-manager boundary

QSteed `Compiler` and `call_compiler_api` are not the same as the local transpiler demo. The upstream README says the compiler path requires MySQL deployment and resource database initialization. Only use it when the user explicitly asks for QSteed deployment/compiler configuration, understands the MySQL requirement, and provides or approves the chip/resource configuration.

Never treat QSteed compilation as permission to submit a Quafu hardware job. A compiled OpenQASM string still goes through the QuarkStudio submission gate in `reference/safety.md`.
