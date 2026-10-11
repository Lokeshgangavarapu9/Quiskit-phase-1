"""
Visualization module for processor topologies, circuit costs, and Trotter benchmark results.
"""

from pathlib import Path
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def plot_processor_topology(
    config: Dict[str, Any],
    output_path: str | Path,
    title: str = None
) -> None:
    """Plot processor coupling map with designated ports and node labels."""
    g = nx.Graph()
    num_q = config["num_qubits"]
    g.add_nodes_from(range(num_q))
    for u, v in config["coupling_map"]:
        g.add_edge(u, v)

    plt.figure(figsize=(7, 5), dpi=300)
    
    # Custom layout
    if config.get("topology_type") == "linear_chain":
        pos = {i: (i, 0) for i in range(num_q)}
    elif config.get("topology_type") == "heavy_hex_subgraph":
        # Layout for 7-qubit heavy-hex subgraph:
        # 0: (0, 1), 1: (1, 1), 2: (2, 1)
        # 3: (1, 0)
        # 4: (0, -1), 5: (1, -1), 6: (2, -1)
        pos = {
            0: (0.0, 1.0),
            1: (1.0, 1.0),
            2: (2.0, 1.0),
            3: (1.0, 0.0),
            4: (0.0, -1.0),
            5: (1.0, -1.0),
            6: (2.0, -1.0),
        }
    else:
        pos = nx.spring_layout(g, seed=42)

    ports = config.get("ports", [])
    node_colors = ["#FF6F61" if node in ports else "#4A90E2" for node in g.nodes()]

    nx.draw_networkx_nodes(g, pos, node_color=node_colors, node_size=1100, edgecolors="#1C2833", linewidths=2.0)
    nx.draw_networkx_edges(g, pos, width=2.5, edge_color="#2C3E50")
    nx.draw_networkx_labels(g, pos, font_size=12, font_weight="bold", font_color="white")

    plot_title = title or config.get("display_name", config.get("name", "Processor Topology"))
    plt.title(f"{plot_title}\n(Red nodes denote designated I/O ports)", fontsize=13, fontweight="bold", pad=15)
    plt.axis("off")
    plt.tight_layout()

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()


def plot_logical_vs_transpiled(
    results_a: List[Dict[str, Any]],
    results_b: List[Dict[str, Any]],
    output_path: str | Path
) -> None:
    """Plot comparison of circuit depth and 2Q gate count for logical vs A vs B."""
    step_counts = [r["num_steps"] for r in results_a]
    logical_depths = [r["logical_depth"] for r in results_a]
    depths_a = [r["depth_a"] for r in results_a]
    depths_b = [r["depth_b"] for r in results_b]

    logical_2q = [r["logical_2q_gates"] for r in results_a]
    two_q_a = [r["two_q_gates_a"] for r in results_a]
    two_q_b = [r["two_q_gates_b"] for r in results_b]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Circuit Depth
    ax1.plot(step_counts, logical_depths, "k--o", label="Logical Circuit", linewidth=2.0)
    ax1.plot(step_counts, depths_a, "b-s", label="Processor A (5Q Line)", linewidth=2.2)
    ax1.plot(step_counts, depths_b, "r-^", label="Processor B (7Q Heavy-Hex)", linewidth=2.2)
    ax1.set_xlabel("Trotter Steps (n)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Circuit Depth", fontsize=12, fontweight="bold")
    ax1.set_title("Circuit Depth Scaling", fontsize=13, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(frameon=True, fontsize=11)

    # 2Q Gates
    ax2.plot(step_counts, logical_2q, "k--o", label="Logical Circuit", linewidth=2.0)
    ax2.plot(step_counts, two_q_a, "b-s", label="Processor A (5Q Line)", linewidth=2.2)
    ax2.plot(step_counts, two_q_b, "r-^", label="Processor B (7Q Heavy-Hex)", linewidth=2.2)
    ax2.set_xlabel("Trotter Steps (n)", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Two-Qubit (CX) Gates", fontsize=12, fontweight="bold")
    ax2.set_title("Two-Qubit Operation Overhead", fontsize=13, fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(frameon=True, fontsize=11)

    plt.tight_layout()
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()


def plot_ab_performance(
    steps: List[int],
    exact_fidelity: List[float],
    ideal_trotter_fidelity: List[float],
    noisy_fidelity_a: List[float],
    noisy_fidelity_b: List[float],
    output_path: str | Path
) -> None:
    """Plot Trotter fidelity trade-off: Algorithmic Error vs. Hardware Noise."""
    plt.figure(figsize=(10, 6), dpi=300)

    plt.axhline(1.0, color="gray", linestyle=":", label="Exact Unitary Evolution (F=1.0)", linewidth=1.5)
    plt.plot(steps, ideal_trotter_fidelity, "g--o", label="Ideal Trotter (Discretization Error Only)", linewidth=2.2)
    plt.plot(steps, noisy_fidelity_a, "b-s", label="Processor A (Noisy Baseline)", linewidth=2.5)
    plt.plot(steps, noisy_fidelity_b, "r-^", label="Processor B (Noisy Baseline)", linewidth=2.5)

    plt.xlabel("Number of Trotter Steps (n)", fontsize=12, fontweight="bold")
    plt.ylabel("State Fidelity / Classical Overlap", fontsize=12, fontweight="bold")
    plt.title("Trotter Simulation Fidelity: Discretization vs. Noise Decay\n(Demonstrating Optimal Trotter Step n*)", fontsize=13, fontweight="bold", pad=12)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend(frameon=True, fontsize=11, loc="lower left")

    plt.tight_layout()
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()


def plot_architecture_tradeoffs(
    results_a: List[Dict[str, Any]],
    results_b: List[Dict[str, Any]],
    output_path: str | Path
) -> None:
    """Generate comprehensive 4-panel architecture trade-off dashboard."""
    steps = [r["num_steps"] for r in results_a]
    
    fig, axs = plt.subplots(2, 2, figsize=(15, 11), dpi=300)

    # 1. Total Variation Distance
    tvd_a = [r["tvd_a"] for r in results_a]
    tvd_b = [r["tvd_b"] for r in results_b]
    axs[0, 0].plot(steps, tvd_a, "b-s", label="Processor A (Line)", linewidth=2.2)
    axs[0, 0].plot(steps, tvd_b, "r-^", label="Processor B (Heavy-Hex)", linewidth=2.2)
    axs[0, 0].set_xlabel("Trotter Steps (n)", fontsize=11, fontweight="bold")
    axs[0, 0].set_ylabel("Total Variation Distance (TVD)", fontsize=11, fontweight="bold")
    axs[0, 0].set_title("(a) Output Distribution Deviation from Ideal", fontsize=12, fontweight="bold")
    axs[0, 0].grid(True, linestyle="--", alpha=0.5)
    axs[0, 0].legend()

    # 2. Routing SWAP Overhead
    swaps_a = [r["swap_count_a"] for r in results_a]
    swaps_b = [r["swap_count_b"] for r in results_b]
    axs[0, 1].bar([s - 0.15 for s in steps], swaps_a, width=0.3, color="#4A90E2", label="Processor A SWAPs")
    axs[0, 1].bar([s + 0.15 for s in steps], swaps_b, width=0.3, color="#E74C3C", label="Processor B SWAPs")
    axs[0, 1].set_xlabel("Trotter Steps (n)", fontsize=11, fontweight="bold")
    axs[0, 1].set_ylabel("SWAP Operations Added", fontsize=11, fontweight="bold")
    axs[0, 1].set_title("(b) Architecture-Induced Routing SWAPs", fontsize=12, fontweight="bold")
    axs[0, 1].grid(True, linestyle="--", alpha=0.5)
    axs[0, 1].legend()

    # 3. Magnetization Error
    mag_err_a = [abs(r["mag_a"] - r["exact_mag"]) for r in results_a]
    mag_err_b = [abs(r["mag_b"] - r["exact_mag"]) for r in results_b]
    axs[1, 0].plot(steps, mag_err_a, "b-s", label="|⟨M_z⟩_A - ⟨M_z⟩_exact|", linewidth=2.2)
    axs[1, 0].plot(steps, mag_err_b, "r-^", label="|⟨M_z⟩_B - ⟨M_z⟩_exact|", linewidth=2.2)
    axs[1, 0].set_xlabel("Trotter Steps (n)", fontsize=11, fontweight="bold")
    axs[1, 0].set_ylabel("Absolute Magnetization Error", fontsize=11, fontweight="bold")
    axs[1, 0].set_title("(c) Physical Observable Error", fontsize=12, fontweight="bold")
    axs[1, 0].grid(True, linestyle="--", alpha=0.5)
    axs[1, 0].legend()

    # 4. Two-Qubit Gate Accumulation
    two_q_a = [r["two_q_gates_a"] for r in results_a]
    two_q_b = [r["two_q_gates_b"] for r in results_b]
    axs[1, 1].plot(steps, two_q_a, "b-s", label="Processor A Total 2Q Gates", linewidth=2.2)
    axs[1, 1].plot(steps, two_q_b, "r-^", label="Processor B Total 2Q Gates", linewidth=2.2)
    axs[1, 1].set_xlabel("Trotter Steps (n)", fontsize=11, fontweight="bold")
    axs[1, 1].set_ylabel("Two-Qubit (CX) Gates", fontsize=11, fontweight="bold")
    axs[1, 1].set_title("(d) Gate Accumulation vs. Trotter Depth", fontsize=12, fontweight="bold")
    axs[1, 1].grid(True, linestyle="--", alpha=0.5)
    axs[1, 1].legend()

    plt.tight_layout()
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
