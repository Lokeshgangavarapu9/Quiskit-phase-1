"""
Processor architecture and noise model definitions for Processor A and B.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import networkx as nx

from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError


def load_processor_config(config_path: str | Path) -> Dict[str, Any]:
    """Load processor definition JSON file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Processor config file not found: {config_path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_coupling_map(config: Dict[str, Any]) -> CouplingMap:
    """Construct Qiskit CouplingMap from processor configuration."""
    raw_map = config["coupling_map"]
    # Ensure bidirectional edges if only directed are specified, or keep as provided
    return CouplingMap(raw_map)


def build_noise_model(config: Dict[str, Any]) -> NoiseModel:
    """
    Construct Qiskit Aer NoiseModel based on official Starter Guide (p. 13) specification:
      - 1-qubit depolarizing error on physical pulses ('x', 'sx') with p = 0.001
      - 2-qubit depolarizing error on CX entangling gates with p = 0.01
      - Readout measurement confusion matrix [[0.99, 0.01], [0.02, 0.98]]
    Note: Thermal relaxation (T1/T2) is NOT specified by the official Starter Guide
    and is intentionally not included to prevent inventing unofficial physical parameters.
    """
    noise_cfg = config.get("noise", {})
    noise_model = NoiseModel()

    p1 = noise_cfg.get("single_qubit_depolarizing_p", 0.001)
    p2 = noise_cfg.get("two_qubit_depolarizing_p", 0.01)
    ro_matrix = noise_cfg.get("readout_error_matrix", [[0.99, 0.01], [0.02, 0.98]])

    # 1-qubit errors on ['x', 'sx']
    error_1q = depolarizing_error(p1, 1)
    noise_model.add_all_qubit_quantum_error(error_1q, ["x", "sx"])

    # 2-qubit errors on ['cx']
    error_2q = depolarizing_error(p2, 2)
    noise_model.add_all_qubit_quantum_error(error_2q, ["cx"])

    # Readout error
    ro_error = ReadoutError(ro_matrix)
    noise_model.add_all_qubit_readout_error(ro_error)

    return noise_model


def get_processor_networkx_graph(config: Dict[str, Any]) -> nx.Graph:
    """Convert processor coupling map to NetworkX undirected graph for analysis and plotting."""
    g = nx.Graph()
    g.add_nodes_from(range(config["num_qubits"]))
    for u, v in config["coupling_map"]:
        g.add_edge(u, v)
    return g
