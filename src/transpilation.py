"""
Transpilation and architectural circuit metric extraction.
Distinguishes between total available processor qubits and active physical qubits utilized.
"""

from typing import Dict, Any, Tuple
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap


def extract_circuit_metrics(qc: QuantumCircuit) -> Dict[str, Any]:
    """
    Extract architecture/resource metrics according to the official Starter Guide:
    - depth: Critical path length
    - total_processor_qubits: Total register / processor qubit capacity
    - active_physical_qubits: Number of distinct physical qubits executing operations
    - total_ops: Total gate count
    - two_qubit_ops: Count of two-qubit entangling gates
    - swap_count: Explicit SWAP gates
    - operations: Dictionary of all gate types and counts
    """
    ops = qc.count_ops()
    two_q_gate_names = {"cx", "cz", "ecr", "swap", "rxx", "ryy", "rzz"}

    two_q_count = sum(count for gate, count in ops.items() if gate.lower() in two_q_gate_names)
    swap_count = ops.get("swap", 0)

    # Identify active qubits actually participating in operations
    active_qubits = set()
    for instruction in qc.data:
        for q in instruction.qubits:
            active_qubits.add(qc.find_bit(q).index)

    # Compute critical path depth considering only two-qubit entangling gates
    two_q_depth = qc.depth(filter_function=lambda inst: inst.operation.num_qubits == 2)

    return {
        "depth": qc.depth(),
        "two_qubit_depth": two_q_depth,
        "total_processor_qubits": qc.num_qubits,
        "active_physical_qubits": len(active_qubits),
        "num_qubits": qc.num_qubits,  # Backward compatibility
        "total_ops": sum(ops.values()),
        "two_qubit_ops": two_q_count,
        "explicit_swap_count": swap_count,
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
