# 可选 BAQIS QSteed 支持

QSteed 是可选能力。安装或配置前必须先问用户，因为它会创建单独 Python 环境、安装包，并可能创建 `~/QSteed/config.ini`。

## 有来源依据的事实

- `[DURABLE]` QSteed 是 BAQIS 面向真实量子设备的量子编译软件，包含 quantum compiler、resource virtualization manager、task scheduler。
- `[DURABLE]` 上游 README 说明需要安装 `pyquafu` 和 `qsteed`；QSteed 可用 `pip install qsteed` 从 PyPI 安装。
- `[DURABLE]` 上游 README 展示了本地 transpiler API：`RandomCircuit`、`Backend`、`Model`、`Transpiler`，并支持 preset optimization level `0-3`。
- `[DURABLE]` 上游 README 说明 `Compiler` 路径需要 MySQL 部署/配置和 QSteed config 文件。
- `[LOCAL-VALIDATED]` 在本机，`qsteed==0.2.2` 搭配最新 `pyquafu==0.4.5` 虽能安装但 import 失败（`QuantumGate` 不兼容）。`qsteed==0.2.2` 搭配 `pyquafu==0.4.1` 并使用 `helpers/qsteed_smoke.py` 的临时 typing shim，可成功运行本地 transpile demo。

## 用户 opt-in 后的设置流程

1. 读取本文件和 `reference/safety.md`。
2. 先运行 dry-run plan：

```bash
python helpers/qsteed_setup.py
```

3. 向用户解释该计划使用 Python 3.10/3.11、创建隔离 venv、安装下面这些本机验证过的 pin，然后运行本地 smoke check：

```bash
pyquafu==0.4.1
qsteed==0.2.2
```

4. 用户同意安装包并创建本地 QSteed 配置后，运行：

```bash
python helpers/qsteed_setup.py --yes
```

自动发现失败时用 `--python /path/to/python3.10`。用户想要项目专用环境时用 `--venv PATH`。如果只需要本地 transpiler demo 且不想创建 `~/QSteed/config.ini`，用 `--skip-config`。

## Smoke checks

在 QSteed venv 内运行：

```bash
python helpers/qsteed_smoke.py --check-import --transpile-demo
```

这些检查只在本地执行：不需要 Quafu token，不发网络请求，不提交硬件任务。

## 生成 QSteed 代码时的兼容 shim

在上游 QSteed 修复缺失 typing import 前，面向已验证 pin 的脚本需要在 import QSteed 前加入：

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

不要用这个 shim 掩盖无关 import 失败。如果错误提到 `QuantumGate`，改为 pin `pyquafu==0.4.1`。

## 最小本地 transpiler 示例

```python
# 使用 helpers/qsteed_setup.py 创建的 QSteed venv Python 运行。
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

## Compiler/resource-manager 边界

QSteed `Compiler` 与 `call_compiler_api` 不等同于本地 transpiler demo。上游 README 说明 compiler 路径需要 MySQL 部署和资源数据库初始化。只有用户明确要求 QSteed deployment/compiler 配置、理解 MySQL 要求、并提供或批准 chip/resource 配置时，才使用这些路径。

QSteed 编译完成不代表可以提交 Quafu 硬件任务。compiled OpenQASM 仍然必须经过 `reference/safety.md` 的 QuarkStudio 提交安全门。
