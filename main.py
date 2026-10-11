"""
Qiskit Fall Fest 2026 Phase 1
Main Benchmark Pipeline for Problem S3: Noise in Trotter Simulation
Controlled Architecture Benchmark: Processor A (5Q Line) vs Processor B (7Q Heavy-Hex)
"""

import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from qiskit_aer import AerSimulator

from src.processors import (
    load_processor_config,
    build_coupling_map,
    build_noise_model
)
from src.problem import TrotterSimulationModel
from src.transpilation import compile_for_processor, extract_circuit_metrics
from src.metrics import (
    compute_magnetization_from_counts,
    compute_tvd,
    compute_classical_distribution_fidelity,
    compute_quantum_state_fidelity,
    compute_proportion_error
)
from src.visualization import (
    plot_processor_topology,
    plot_logical_vs_transpiled,
    plot_ab_performance,
    plot_architecture_tradeoffs
)


def run_experiment():
    print("=" * 80)
    print("  QISKIT FALL FEST 2026 - PHASE 1: S3 NOISE IN TROTTER SIMULATION")
    print("  Controlled Architecture Benchmark: Processor A vs. Processor B")
    print("=" * 80)

    # 1. Directories setup
    base_dir = Path(__file__).resolve().parent
    results_raw_dir = base_dir / "results" / "raw"
    results_tables_dir = base_dir / "results" / "tables"
    results_figures_dir = base_dir / "results" / "figures"

    results_raw_dir.mkdir(parents=True, exist_ok=True)
    results_tables_dir.mkdir(parents=True, exist_ok=True)
    results_figures_dir.mkdir(parents=True, exist_ok=True)

    # 2. Load Processors
    proc_a_cfg = load_processor_config(base_dir / "processors" / "processor_A.json")
    proc_b_cfg = load_processor_config(base_dir / "processors" / "processor_B.json")

    cmap_a = build_coupling_map(proc_a_cfg)
    cmap_b = build_coupling_map(proc_b_cfg)

    noise_a = build_noise_model(proc_a_cfg)
    noise_b = build_noise_model(proc_b_cfg)

    print(f"Loaded {proc_a_cfg['display_name']} ({proc_a_cfg['num_qubits']} qubits)")
    print(f"Loaded {proc_b_cfg['display_name']} ({proc_b_cfg['num_qubits']} qubits)")

    # 3. Plot Topologies
    print("\n[Step 1/5] Generating processor coupling graph figures...")
    plot_processor_topology(proc_a_cfg, results_figures_dir / "processor_A_graph.png")
    plot_processor_topology(proc_b_cfg, results_figures_dir / "processor_B_graph.png")
    print("  -> Saved processor_A_graph.png and processor_B_graph.png")

    # 4. Initialize Problem Model
    num_spins = 4
    total_time = 1.0  # T=1.0 shows clear Trotter convergence and noise crossover
    shots = 4096
    seed = 42

    print(f"\n[Step 2/5] Initializing Problem S3 Spin-Chain System:")
    print(f"  - Number of spins: {num_spins}")
    print(f"  - Hamiltonian: TFIM with J=1.0, h=0.8, J_cross=0.5 (periodic boundary / routing test)")
    print(f"  - Initial state: |1010>")
    print(f"  - Evolution time: T = {total_time}")
    print(f"  - Measurement shots: {shots} (Seed: {seed})")

    model = TrotterSimulationModel(
        num_spins=num_spins,
        J=1.0,
        h=0.8,
        J_cross=0.5,
        initial_state_str="1010"
    )

    exact_mag = model.compute_exact_magnetization(total_time)
    print(f"  - Exact analytical <M_z(T={total_time})> = {exact_mag:.4f}")

    # Simulators
    sim_ideal = AerSimulator(seed_simulator=seed)
    sim_a = AerSimulator(noise_model=noise_a, seed_simulator=seed)
    sim_b = AerSimulator(noise_model=noise_b, seed_simulator=seed)

    # 5. Sweep Trotter Steps
    trotter_steps_list = [1, 2, 3, 4, 5, 6, 8, 10]
    records_a = []
    records_b = []
    raw_dumps = []
    ideal_trotter_state_fids = []

    print(f"\n[Step 3/5] Executing controlled Trotter simulations over n = {trotter_steps_list}...")

    for n in trotter_steps_list:
        print(f"  --> Running Trotter step count n = {n}...")

        # Algorithmic pure-state Trotter fidelity (discretization error only)
        fid_algorithmic = model.compute_algorithmic_trotter_state_fidelity(t=total_time, num_steps=n)
        ideal_trotter_state_fids.append(fid_algorithmic)

        # Build Logical Circuit with measurements
        qc_logical = model.build_trotter_circuit(t=total_time, num_steps=n, measure=True)
        logical_metrics = extract_circuit_metrics(qc_logical)

        # Ideal Reference Run (Noise-Free)
        res_ideal = sim_ideal.run(qc_logical, shots=shots).result()
        counts_ideal = res_ideal.get_counts()
        mag_ideal, _ = compute_magnetization_from_counts(counts_ideal, num_spins)

        # Compile and Run on Processor A
        compiled_a, metrics_a = compile_for_processor(
            qc_logical,
            coupling_map=cmap_a,
            basis_gates=proc_a_cfg["basis_gates"],
            optimization_level=1,
            seed_transpiler=seed
        )
        res_a = sim_a.run(compiled_a, shots=shots).result()
        counts_a = res_a.get_counts()
        mag_a, mag_se_a = compute_magnetization_from_counts(counts_a, num_spins)
        tvd_a = compute_tvd(counts_a, counts_ideal)
        fid_classical_a = compute_classical_distribution_fidelity(counts_a, counts_ideal)

        # Compile and Run on Processor B
        compiled_b, metrics_b = compile_for_processor(
            qc_logical,
            coupling_map=cmap_b,
            basis_gates=proc_b_cfg["basis_gates"],
            optimization_level=1,
            seed_transpiler=seed
        )
        res_b = sim_b.run(compiled_b, shots=shots).result()
        counts_b = res_b.get_counts()
        mag_b, mag_se_b = compute_magnetization_from_counts(counts_b, num_spins)
        tvd_b = compute_tvd(counts_b, counts_ideal)
        fid_classical_b = compute_classical_distribution_fidelity(counts_b, counts_ideal)

        routing_cx_a = metrics_a["two_qubit_ops"] - logical_metrics["two_qubit_ops"]
        routing_cx_b = metrics_b["two_qubit_ops"] - logical_metrics["two_qubit_ops"]

        record_a = {
            "num_steps": n,
            "logical_depth": logical_metrics["depth"],
            "logical_2q_gates": logical_metrics["two_qubit_ops"],
            "depth_a": metrics_a["depth"],
            "two_q_depth_a": metrics_a["two_qubit_depth"],
            "two_q_gates_a": metrics_a["two_qubit_ops"],
            "routing_cx_overhead_a": routing_cx_a,
            "equivalent_swaps_a": routing_cx_a // 3,
            "explicit_swaps_a": metrics_a["explicit_swap_count"],
            "swap_count_a": metrics_a["swap_count"],
            "total_processor_qubits_a": metrics_a["total_processor_qubits"],
            "active_physical_qubits_a": metrics_a["active_physical_qubits"],
            "exact_mag": exact_mag,
            "ideal_mag": mag_ideal,
            "mag_a": mag_a,
            "mag_se_a": mag_se_a,
            "mag_error_a": abs(mag_a - exact_mag),
            "tvd_a": tvd_a,
            "classical_dist_fidelity_a": fid_classical_a,
            "ideal_trotter_state_fidelity": fid_algorithmic,
            "fidelity_a": fid_classical_a  # for visualization compatibility
        }
        records_a.append(record_a)

        record_b = {
            "num_steps": n,
            "logical_depth": logical_metrics["depth"],
            "logical_2q_gates": logical_metrics["two_qubit_ops"],
            "depth_b": metrics_b["depth"],
            "two_q_depth_b": metrics_b["two_qubit_depth"],
            "two_q_gates_b": metrics_b["two_qubit_ops"],
            "routing_cx_overhead_b": routing_cx_b,
            "equivalent_swaps_b": routing_cx_b // 3,
            "explicit_swaps_b": metrics_b["explicit_swap_count"],
            "swap_count_b": metrics_b["swap_count"],
            "total_processor_qubits_b": metrics_b["total_processor_qubits"],
            "active_physical_qubits_b": metrics_b["active_physical_qubits"],
            "exact_mag": exact_mag,
            "ideal_mag": mag_ideal,
            "mag_b": mag_b,
            "mag_se_b": mag_se_b,
            "mag_error_b": abs(mag_b - exact_mag),
            "tvd_b": tvd_b,
            "classical_dist_fidelity_b": fid_classical_b,
            "ideal_trotter_state_fidelity": fid_algorithmic,
            "fidelity_b": fid_classical_b  # for visualization compatibility
        }
        records_b.append(record_b)

        raw_dumps.append({
            "num_steps": n,
            "ideal_trotter_state_fidelity": fid_algorithmic,
            "counts_ideal": counts_ideal,
            "counts_processor_A": counts_a,
            "counts_processor_B": counts_b,
            "metrics_processor_A": metrics_a,
            "metrics_processor_B": metrics_b
        })

    # 6. Save Data
    print("\n[Step 4/5] Saving machine-readable result tables and raw data...")
    with (results_raw_dir / "raw_experiment_data.json").open("w", encoding="utf-8") as f:
        json.dump(raw_dumps, f, indent=2)

    df_a = pd.DataFrame(records_a)
    df_b = pd.DataFrame(records_b)

    df_a.to_csv(results_tables_dir / "processor_A_metrics.csv", index=False)
    df_b.to_csv(results_tables_dir / "processor_B_metrics.csv", index=False)

    # Merged comparison table
    comparison_records = []
    for ra, rb in zip(records_a, records_b):
        comparison_records.append({
            "Trotter_Steps_n": ra["num_steps"],
            "Ideal_Algorithmic_State_Fidelity": ra["ideal_trotter_state_fidelity"],
            "Logical_Depth": ra["logical_depth"],
            "Logical_2Q_Gates": ra["logical_2q_gates"],
            "ProcA_Total_Depth": ra["depth_a"],
            "ProcB_Total_Depth": rb["depth_b"],
            "ProcA_2Q_Depth": ra["two_q_depth_a"],
            "ProcB_2Q_Depth": rb["two_q_depth_b"],
            "ProcA_2Q_Gates": ra["two_q_gates_a"],
            "ProcB_2Q_Gates": rb["two_q_gates_b"],
            "2Q_Gate_Delta_B_minus_A": rb["two_q_gates_b"] - ra["two_q_gates_a"],
            "ProcA_Routing_CX_Overhead": ra["routing_cx_overhead_a"],
            "ProcB_Routing_CX_Overhead": rb["routing_cx_overhead_b"],
            "ProcA_Equivalent_SWAPs": ra["equivalent_swaps_a"],
            "ProcB_Equivalent_SWAPs": rb["equivalent_swaps_b"],
            "ProcA_Explicit_SWAPs": ra["explicit_swaps_a"],
            "ProcB_Explicit_SWAPs": rb["explicit_swaps_b"],
            "ProcA_Active_Qubits": ra["active_physical_qubits_a"],
            "ProcB_Active_Qubits": rb["active_physical_qubits_b"],
            "ProcA_Total_Qubits": ra["total_processor_qubits_a"],
            "ProcB_Total_Qubits": rb["total_processor_qubits_b"],
            "Exact_Magnetization": exact_mag,
            "Ideal_Measured_Magnetization": ra["ideal_mag"],
            "ProcA_Magnetization": ra["mag_a"],
            "ProcB_Magnetization": rb["mag_b"],
            "ProcA_Mag_Error": ra["mag_error_a"],
            "ProcB_Mag_Error": rb["mag_error_b"],
            "ProcA_Classical_Dist_Fidelity": ra["classical_dist_fidelity_a"],
            "ProcB_Classical_Dist_Fidelity": rb["classical_dist_fidelity_b"],
            "ProcA_TVD": ra["tvd_a"],
            "ProcB_TVD": rb["tvd_b"]
        })

    df_comp = pd.DataFrame(comparison_records)
    df_comp.to_csv(results_tables_dir / "AB_comparison.csv", index=False)

    # Final summary comparison table
    summary_row = {
        "Metric": [
            "Total Processor Qubit Capacity",
            "Active Physical Qubits Used",
            "Coupling Topology",
            "Total Circuit Depth (n=4)",
            "Two-Qubit Circuit Depth (n=4)",
            "Two-Qubit CX Gates (n=4)",
            "Routing CX Overhead (n=4)",
            "Equivalent SWAPs Estimated from Excess CX (n=4)",
            "Explicit SWAP Instructions (n=4)",
            "Two-Qubit CX Gates (n=10)",
            "Routing CX Overhead (n=10)",
            "Equivalent SWAPs Estimated from Excess CX (n=10)",
            "Algorithmic State Fidelity (n=4)",
            "Algorithmic State Fidelity (n=10)",
            "Classical Dist Fidelity (n=4)",
            "Classical Dist Fidelity (n=10)",
            "Optimal Step Count n*",
            "Peak Classical Dist Fidelity"
        ],
        "Processor A": [
            proc_a_cfg["num_qubits"],
            df_comp.loc[0, "ProcA_Active_Qubits"],
            "Linear Chain (5Q)",
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcA_Total_Depth"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcA_2Q_Depth"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcA_2Q_Gates"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcA_Routing_CX_Overhead"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcA_Equivalent_SWAPs"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcA_Explicit_SWAPs"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "ProcA_2Q_Gates"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "ProcA_Routing_CX_Overhead"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "ProcA_Equivalent_SWAPs"].values[0],
            round(df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "Ideal_Algorithmic_State_Fidelity"].values[0], 4),
            round(df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "Ideal_Algorithmic_State_Fidelity"].values[0], 4),
            round(df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcA_Classical_Dist_Fidelity"].values[0], 4),
            round(df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "ProcA_Classical_Dist_Fidelity"].values[0], 4),
            int(df_comp.loc[df_comp["ProcA_Classical_Dist_Fidelity"].idxmax(), "Trotter_Steps_n"]),
            round(df_comp["ProcA_Classical_Dist_Fidelity"].max(), 4)
        ],
        "Processor B": [
            proc_b_cfg["num_qubits"],
            df_comp.loc[0, "ProcB_Active_Qubits"],
            "Heavy-Hex Subgraph (7Q)",
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcB_Total_Depth"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcB_2Q_Depth"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcB_2Q_Gates"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcB_Routing_CX_Overhead"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcB_Equivalent_SWAPs"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcB_Explicit_SWAPs"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "ProcB_2Q_Gates"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "ProcB_Routing_CX_Overhead"].values[0],
            df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "ProcB_Equivalent_SWAPs"].values[0],
            round(df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "Ideal_Algorithmic_State_Fidelity"].values[0], 4),
            round(df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "Ideal_Algorithmic_State_Fidelity"].values[0], 4),
            round(df_comp.loc[df_comp["Trotter_Steps_n"] == 4, "ProcB_Classical_Dist_Fidelity"].values[0], 4),
            round(df_comp.loc[df_comp["Trotter_Steps_n"] == 10, "ProcB_Classical_Dist_Fidelity"].values[0], 4),
            int(df_comp.loc[df_comp["ProcB_Classical_Dist_Fidelity"].idxmax(), "Trotter_Steps_n"]),
            round(df_comp["ProcB_Classical_Dist_Fidelity"].max(), 4)
        ]
    }
    df_summary = pd.DataFrame(summary_row)
    df_summary["Difference (B - A)"] = [
        "+2 qubits capacity",
        "0 (Both utilize 4 active spins)",
        "Branching junctions vs simple line",
        df_summary.loc[3, "Processor B"] - df_summary.loc[3, "Processor A"],
        df_summary.loc[4, "Processor B"] - df_summary.loc[4, "Processor A"],
        df_summary.loc[5, "Processor B"] - df_summary.loc[5, "Processor A"],
        df_summary.loc[6, "Processor B"] - df_summary.loc[6, "Processor A"],
        df_summary.loc[7, "Processor B"] - df_summary.loc[7, "Processor A"],
        df_summary.loc[8, "Processor B"] - df_summary.loc[8, "Processor A"],
        df_summary.loc[9, "Processor B"] - df_summary.loc[9, "Processor A"],
        df_summary.loc[10, "Processor B"] - df_summary.loc[10, "Processor A"],
        df_summary.loc[11, "Processor B"] - df_summary.loc[11, "Processor A"],
        0.0,
        0.0,
        round(df_summary.loc[14, "Processor B"] - df_summary.loc[14, "Processor A"], 4),
        round(df_summary.loc[15, "Processor B"] - df_summary.loc[15, "Processor A"], 4),
        "Same optimal trade-off peak",
        round(df_summary.loc[17, "Processor B"] - df_summary.loc[17, "Processor A"], 4)
    ]
    df_summary.to_csv(results_tables_dir / "final_comparison.csv", index=False)

    print("  -> Exported processor_A_metrics.csv")
    print("  -> Exported processor_B_metrics.csv")
    print("  -> Exported AB_comparison.csv")
    print("  -> Exported final_comparison.csv")

    # 7. Generate Comparison Plots
    print("\n[Step 5/5] Generating publication-quality comparative plots...")
    plot_logical_vs_transpiled(records_a, records_b, results_figures_dir / "logical_vs_transpiled.png")
    
    plot_ab_performance(
        steps=trotter_steps_list,
        exact_fidelity=[1.0] * len(trotter_steps_list),
        ideal_trotter_fidelity=ideal_trotter_state_fids,
        noisy_fidelity_a=[r["classical_dist_fidelity_a"] for r in records_a],
        noisy_fidelity_b=[r["classical_dist_fidelity_b"] for r in records_b],
        output_path=results_figures_dir / "AB_performance.png"
    )

    plot_architecture_tradeoffs(records_a, records_b, results_figures_dir / "architecture_tradeoffs.png")
    print("  -> Saved logical_vs_transpiled.png")
    print("  -> Saved AB_performance.png")
    print("  -> Saved architecture_tradeoffs.png")

    print("\n" + "=" * 80)
    print("  FINAL A/B ARCHITECTURE BENCHMARK SUMMARY TABLE")
    print("=" * 80)
    print(df_summary.to_string(index=False))
    print("=" * 80)
    print("\nBenchmark experiment successfully completed!")


if __name__ == "__main__":
    run_experiment()
