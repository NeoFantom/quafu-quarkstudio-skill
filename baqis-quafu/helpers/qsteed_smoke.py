#!/usr/bin/env python3
"""Safe, local-only QSteed smoke checks.

This helper never reads Quafu tokens and never submits cloud/hardware jobs. It validates
only the locally installed QSteed transpiler stack.
"""
from __future__ import annotations

import argparse
import builtins
import importlib.metadata
import sys
from typing import Iterable

TYPING_SHIM_NAMES = ("List", "Dict", "Tuple", "Union", "Optional")
EXPECTED_QSTEED = "0.2.2"
EXPECTED_PYQUAFU = "0.4.1"


def package_version(distribution: str) -> str:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def install_typing_shim() -> list[str]:
    """Temporarily expose typing aliases needed by QSteed 0.2.2 annotations."""
    import typing

    added: list[str] = []
    for name in TYPING_SHIM_NAMES:
        if not hasattr(builtins, name):
            setattr(builtins, name, getattr(typing, name))
            added.append(name)
    return added


def cleanup_typing_shim(added: Iterable[str]) -> None:
    for name in added:
        if hasattr(builtins, name):
            delattr(builtins, name)


def qsteed_error_hint(exc: BaseException) -> str:
    qsteed_ver = package_version("qsteed")
    pyquafu_ver = package_version("pyquafu")
    base = f"QSteed import failed ({type(exc).__name__}: {exc}). Installed versions: qsteed={qsteed_ver}, pyquafu={pyquafu_ver}."
    text = str(exc)
    if "QuantumGate" in text:
        return base + " This matches the tested incompatibility with newer pyquafu; reinstall with: python -m pip install 'pyquafu==0.4.1' 'qsteed==0.2.2'."
    if "List" in text:
        return base + " This matches QSteed 0.2.2 missing typing imports; use this helper or the compatibility shim in reference/qsteed.md."
    return base


def import_qsteed_symbols():
    added = install_typing_shim()
    try:
        import qsteed  # noqa: F401
        from qsteed import Backend, Model, RandomCircuit, Transpiler
    except Exception as exc:  # pragma: no cover - exercised in real env, message tested indirectly
        raise SystemExit(qsteed_error_hint(exc)) from exc
    finally:
        cleanup_typing_shim(added)
    return RandomCircuit, Backend, Model, Transpiler


def check_versions(strict: bool) -> None:
    qsteed_ver = package_version("qsteed")
    pyquafu_ver = package_version("pyquafu")
    print(f"QSteed packages: qsteed={qsteed_ver}, pyquafu={pyquafu_ver}")
    if strict and (qsteed_ver != EXPECTED_QSTEED or pyquafu_ver != EXPECTED_PYQUAFU):
        raise SystemExit(
            "QSteed version check failed. This skill was locally validated with "
            f"qsteed=={EXPECTED_QSTEED} and pyquafu=={EXPECTED_PYQUAFU}; "
            "rerun helpers/qsteed_setup.py --yes or install those pins manually."
        )


def run_import_check(strict: bool) -> None:
    check_versions(strict=strict)
    import_qsteed_symbols()
    print("PASS qsteed import: QSteed symbols loaded with local compatibility shim.")


def run_transpile_demo(strict: bool) -> None:
    check_versions(strict=strict)
    RandomCircuit, Backend, Model, Transpiler = import_qsteed_symbols()
    rqc = RandomCircuit(num_qubit=3, gates_number=10, gates_list=["cx", "rx", "rz", "ry", "h"])
    qc = rqc.random_circuit()
    basis_gates = ["cx", "rx", "ry", "rz", "id", "h"]
    coupling_list = [(0, 1, 0.98), (1, 0, 0.98), (1, 2, 0.97), (2, 1, 0.97)]
    backend = Backend(
        name="SkillSmokeBackend",
        backend_type="superconducting",
        qubits_num=3,
        coupling_list=coupling_list,
        basis_gates=basis_gates,
    )
    model = Model(backend=backend)
    transpiler = Transpiler(initial_model=model)
    transpiled = transpiler.transpile(qc, optimization_level=1)
    qasm = transpiled.to_openqasm() if hasattr(transpiled, "to_openqasm") else ""
    first_line = qasm.splitlines()[0] if qasm else "<no qasm exporter>"
    print(f"PASS qsteed transpile: produced {type(transpiled).__name__}; first line: {first_line}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run safe local QSteed smoke checks.")
    parser.add_argument("--check-import", action="store_true", help="Import QSteed symbols only; no token/network/hardware.")
    parser.add_argument("--transpile-demo", action="store_true", help="Run a small local transpiler demo; no token/network/hardware.")
    parser.add_argument("--allow-version-drift", action="store_true", help="Warn but do not fail if package versions differ from the locally validated pins.")
    args = parser.parse_args()

    if not args.check_import and not args.transpile_demo:
        args.check_import = True
    strict = not args.allow_version_drift
    if args.check_import:
        run_import_check(strict=strict)
    if args.transpile_demo:
        run_transpile_demo(strict=strict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
