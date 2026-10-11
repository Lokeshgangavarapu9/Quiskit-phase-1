"""
Transpilation and architectural circuit metric extraction.
"""

from typing import Dict, Any, Tuple
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap


def extract_circuit_metrics(qc: QuantumCircuit) -> Dict[str, Any]:
    """
    Extract architecture/resource metrics according to the official Starter Guide:
    depth, num_qubits, total_ops, two_qubit_ops, swap_count, operations dict.
    """
    ops = qc.count_ops()
    two_q_gate_names = {"cx", "cz", "ecr", "swap", "rxx", "ryy", "rzz"}

    two_q_count = sum(count for gate, count in ops.items() if gate.lower() in two_q_gate_names)
    swap_count = ops.get("swap", 0)

    # In standard basis decomposition, SWAP is decomposed into 3 CX gates.
    # We report both explicit SWAP gates and total 2Q operations.
    return {
        "depth": qc.depth(),
        "num_qubits": qc.num_qubits,
        "total_ops": sum(ops.values()),
        "two_qubit_ops": two_q_count,
        "swap_count": swap_count,
        "operations": dict(ops)
    }


def compile_for_processor(
    logical_circuit: QuantumCircuit,
    coupling_map: CouplingMap,
    basis_gates: list[str] = None,
    optimization_level: int = 1,
    seed_transpiler: int = 42
) -> Tuple[QuantumCircuit, Dict[str, Any]]:
    """
    Transpile a logical circuit onto the physical processor target.
    Returns the compiled physical circuit and its architectural resource metrics.
    """
    compiled = transpile(
        logical_circuit,
        coupling_map=coupling_map,
        basis_gates=basis_gates,
        optimization_level=optimization_level,
        seed_transpiler=seed_transpiler
    )

    metrics = extract_circuit_metrics(compiled)
    return compiled, metrics
