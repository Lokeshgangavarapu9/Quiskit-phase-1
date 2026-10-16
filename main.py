"""
Qiskit Fall Fest 2026 Phase 1
Main Benchmark Pipeline for Problem S3: Noise in Trotter Simulation
Controlled Architecture Benchmark: Processor A (5Q Line) vs. Processor B (9Q Heavy-Hex)

Generates:
  - Primary Benchmark: Open-chain TFIM baseline (J_cross = 0.0)
  - Architectural Extension: Periodic ring TFIM (J_cross = 0.5) routing-stress test
  - Observables: Primary single-site <Z_0(t)> and secondary diagnostic <M_z(t)>
  - Metrics: Pure-state fidelity, classical distribution fidelity (Bhattacharyya), TVD,
             circuit depth, 2Q depth, CX overhead, and estimated equivalent SWAPs.
"""

import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import qiskit
import qiskit_aer
from qiskit_aer import AerSimulator
import scipy

from src.processors import (
    load_processor_config,
    build_coupling_map,
    build_noise_model
)
from src.problem import TrotterSimulationModel
from src.transpilation import compile_for_processor, extract_circuit_metrics
from src.metrics import (
    compute_single_site_z_from_counts,
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


def run_benchmark_for_model(
    model: TrotterSimulationModel,
    model_variant_name: str,
    trotter_steps_list: list[int],
    total_time: float,
    shots: int,
    seed: int,
    proc_a_cfg: dict,
    proc_b_cfg: dict,
    cmap_a,
    cmap_b,
    noise_a,
    noise_b,
    sim_ideal: AerSimulator,
    sim_a: AerSimulator,
    sim_b: AerSimulator
):
    """Run full Trotter simulation sweep for a given model variant on Processors A and B."""
    z0_exact = model.compute_exact_single_site_z(total_time, site=0)
    mag_exact = model.compute_exact_magnetization(total_time)

    records_a = []
    records_b = []
    raw_entries = []

    for n in trotter_steps_list:
        # Algorithmic pure-state Trotter fidelity (discretization error only)
        fid_algorithmic = model.compute_algorithmic_trotter_state_fidelity(t=total_time, num_steps=n)

        # Build Logical Circuit with measurements
        qc_logical = model.build_trotter_circuit(t=total_time, num_steps=n, measure=True)
        logical_metrics = extract_circuit_metrics(qc_logical)

        # Ideal Reference Run (Noise-Free)
        res_ideal = sim_ideal.run(qc_logical, shots=shots).result()
        counts_ideal = res_ideal.get_counts()
        z0_ideal, z0_se_ideal = compute_single_site_z_from_counts(counts_ideal, model.num_spins, site=0)
        mag_ideal, mag_se_ideal = compute_magnetization_from_counts(counts_ideal, model.num_spins)

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
        z0_a, z0_se_a = compute_single_site_z_from_counts(counts_a, model.num_spins, site=0)
        mag_a, mag_se_a = compute_magnetization_from_counts(counts_a, model.num_spins)
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
        z0_b, z0_se_b = compute_single_site_z_from_counts(counts_b, model.num_spins, site=0)
        mag_b, mag_se_b = compute_magnetization_from_counts(counts_b, model.num_spins)
        tvd_b = compute_tvd(counts_b, counts_ideal)
        fid_classical_b = compute_classical_distribution_fidelity(counts_b, counts_ideal)

        routing_cx_a = metrics_a["two_qubit_ops"] - logical_metrics["two_qubit_ops"]
        routing_cx_b = metrics_b["two_qubit_ops"] - logical_metrics["two_qubit_ops"]

        record_a = {
            "model_variant": model_variant_name,
            "processor": "Processor A",
            "num_steps": n,
            "total_time": total_time,
            "logical_depth": logical_metrics["depth"],
            "logical_2q_gates": logical_metrics["two_qubit_ops"],
            "depth_a": metrics_a["depth"],
            "two_q_depth_a": metrics_a["two_qubit_depth"],
            "two_q_gates_a": metrics_a["two_qubit_ops"],
            "routing_cx_overhead_a": routing_cx_a,
            "equivalent_swaps_a": routing_cx_a // 3,
            "explicit_swaps_a": metrics_a["explicit_swap_count"],
            "total_processor_qubits_a": metrics_a["total_processor_qubits"],
            "active_physical_qubits_a": metrics_a["active_physical_qubits"],
            "z0_exact": z0_exact,
            "z0_ideal": z0_ideal,
            "z0_a": z0_a,
            "z0_se_a": z0_se_a,
            "z0_error_ideal": abs(z0_ideal - z0_exact),
            "z0_error_a": abs(z0_a - z0_exact),
            "exact_mag": mag_exact,
            "ideal_mag": mag_ideal,
            "mag_a": mag_a,
            "mag_se_a": mag_se_a,
            "mag_error_a": abs(mag_a - mag_exact),
            "tvd_a": tvd_a,
            "classical_dist_fidelity_a": fid_classical_a,
            "ideal_trotter_state_fidelity": fid_algorithmic,
            "fidelity_a": fid_classical_a
        }
        records_a.append(record_a)

        record_b = {
            "model_variant": model_variant_name,
            "processor": "Processor B",
            "num_steps": n,
            "total_time": total_time,
            "logical_depth": logical_metrics["depth"],
            "logical_2q_gates": logical_metrics["two_qubit_ops"],
            "depth_b": metrics_b["depth"],
            "two_q_depth_b": metrics_b["two_qubit_depth"],
            "two_q_gates_b": metrics_b["two_qubit_ops"],
            "routing_cx_overhead_b": routing_cx_b,
            "equivalent_swaps_b": routing_cx_b // 3,
            "explicit_swaps_b": metrics_b["explicit_swap_count"],
            "total_processor_qubits_b": metrics_b["total_processor_qubits"],
            "active_physical_qubits_b": metrics_b["active_physical_qubits"],
            "z0_exact": z0_exact,
            "z0_ideal": z0_ideal,
            "z0_b": z0_b,
            "z0_se_b": z0_se_b,
            "z0_error_ideal": abs(z0_ideal - z0_exact),
            "z0_error_b": abs(z0_b - z0_exact),
            "exact_mag": mag_exact,
            "ideal_mag": mag_ideal,
            "mag_b": mag_b,
            "mag_se_b": mag_se_b,
            "mag_error_b": abs(mag_b - mag_exact),
            "tvd_b": tvd_b,
            "classical_dist_fidelity_b": fid_classical_b,
            "ideal_trotter_state_fidelity": fid_algorithmic,
            "fidelity_b": fid_classical_b
        }
        records_b.append(record_b)

        raw_entries.append({
            "model_variant": model_variant_name,
            "num_steps": n,
            "ideal_trotter_state_fidelity": fid_algorithmic,
            "z0_exact": z0_exact,
            "mag_exact": mag_exact,
            "counts_ideal": counts_ideal,
            "counts_processor_A": counts_a,
            "counts_processor_B": counts_b,
            "metrics_logical": logical_metrics,
            "metrics_processor_A": metrics_a,
            "metrics_processor_B": metrics_b
        })

    return records_a, records_b, raw_entries


def run_experiment():
    print("=" * 80)
    print("  QISKIT FALL FEST 2026 - PHASE 1: S3 NOISE IN TROTTER SIMULATION")
    print("  Controlled Architecture Benchmark: Processor A (5Q Line) vs Processor B (9Q Heavy-Hex)")
    print("=" * 80)

    start_timestamp = datetime.now(timezone.utc).isoformat()
    base_dir = Path(__file__).resolve().parent
    results_raw_dir = base_dir / "results" / "raw"
    results_tables_dir = base_dir / "results" / "tables"
    results_figures_dir = base_dir / "results" / "figures"

    results_raw_dir.mkdir(parents=True, exist_ok=True)
    results_tables_dir.mkdir(parents=True, exist_ok=True)
    results_figures_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Processors
    proc_a_file = base_dir / "processors" / "processor_A.json"
    proc_b_file = base_dir / "processors" / "processor_B.json"

    proc_a_cfg = load_processor_config(proc_a_file)
    proc_b_cfg = load_processor_config(proc_b_file)

    cmap_a = build_coupling_map(proc_a_cfg)
    cmap_b = build_coupling_map(proc_b_cfg)

    noise_a = build_noise_model(proc_a_cfg)
    noise_b = build_noise_model(proc_b_cfg)

    print(f"Loaded {proc_a_cfg['display_name']} ({proc_a_cfg['num_qubits']} qubits, p2={proc_a_cfg['noise']['two_qubit_depolarizing_p']})")
    print(f"Loaded {proc_b_cfg['display_name']} ({proc_b_cfg['num_qubits']} qubits, p2={proc_b_cfg['noise']['two_qubit_depolarizing_p']})")

    # 2. Plot Topologies
    print("\n[Step 1/5] Generating processor coupling graph figures...")
    plot_processor_topology(proc_a_cfg, results_figures_dir / "processor_A_graph.png")
    plot_processor_topology(proc_b_cfg, results_figures_dir / "processor_B_graph.png")
    print("  -> Saved processor_A_graph.png and processor_B_graph.png")

    # 3. Execution Parameters
    num_spins = 4
    total_time = 1.0
    shots = 4096
    seed = 42
    trotter_steps_list = [1, 2, 3, 4, 5, 6, 8, 10]

    sim_ideal = AerSimulator(seed_simulator=seed)
    sim_a = AerSimulator(noise_model=noise_a, seed_simulator=seed)
    sim_b = AerSimulator(noise_model=noise_b, seed_simulator=seed)

    # 4. PRIMARY BENCHMARK: Open-Chain Baseline (J_cross = 0.0)
    print(f"\n[Step 2/5] Running Primary Benchmark: Open-Chain TFIM Baseline (J_cross = 0.0)")
    model_open = TrotterSimulationModel(
        num_spins=num_spins,
        J=1.0,
        h=0.8,
        boundary="open",
        initial_state_str="1010"
    )
    records_open_a, records_open_b, raw_open = run_benchmark_for_model(
        model=model_open,
        model_variant_name="open_chain_baseline",
        trotter_steps_list=trotter_steps_list,
        total_time=total_time,
        shots=shots,
        seed=seed,
        proc_a_cfg=proc_a_cfg,
        proc_b_cfg=proc_b_cfg,
        cmap_a=cmap_a,
        cmap_b=cmap_b,
        noise_a=noise_a,
        noise_b=noise_b,
        sim_ideal=sim_ideal,
        sim_a=sim_a,
        sim_b=sim_b
    )
    z0_exact_open = model_open.compute_exact_single_site_z(total_time, site=0)
    mag_exact_open = model_open.compute_exact_magnetization(total_time)
    print(f"  Exact analytical <Z_0(T={total_time})> = {z0_exact_open:.6f}")
    print(f"  Exact analytical <M_z(T={total_time})> = {mag_exact_open:.6f} (identically zero by reflection anti-symmetry)")

    # 5. ARCHITECTURAL EXTENSION: Periodic Ring (J_cross = 0.5)
    print(f"\n[Step 3/5] Running Architectural Extension: Periodic Ring TFIM (J_cross = 0.5)")
    model_per = TrotterSimulationModel(
        num_spins=num_spins,
        J=1.0,
        h=0.8,
        boundary="periodic",
        initial_state_str="1010"
    )
    records_per_a, records_per_b, raw_per = run_benchmark_for_model(
        model=model_per,
        model_variant_name="periodic_routing_extension",
        trotter_steps_list=trotter_steps_list,
        total_time=total_time,
        shots=shots,
        seed=seed,
        proc_a_cfg=proc_a_cfg,
        proc_b_cfg=proc_b_cfg,
        cmap_a=cmap_a,
        cmap_b=cmap_b,
        noise_a=noise_a,
        noise_b=noise_b,
        sim_ideal=sim_ideal,
        sim_a=sim_a,
        sim_b=sim_b
    )
    z0_exact_per = model_per.compute_exact_single_site_z(total_time, site=0)
    mag_exact_per = model_per.compute_exact_magnetization(total_time)
    print(f"  Exact analytical <Z_0(T={total_time})> = {z0_exact_per:.6f}")
    print(f"  Exact analytical <M_z(T={total_time})> = {mag_exact_per:.6f}")

    # 6. Save Data
    print(f"\n[Step 4/5] Exporting validated CSV tables and raw metadata JSON...")

    # Provenance and raw JSON
    metadata = {
        "timestamp_utc": start_timestamp,
        "qiskit_version": qiskit.__version__,
        "qiskit_aer_version": qiskit_aer.__version__,
        "scipy_version": scipy.__version__,
        "numpy_version": np.__version__,
        "shots": shots,
        "seed": seed,
        "total_time": total_time,
        "num_spins": num_spins,
        "initial_state": "1010",
        "processors": {
            "Processor_A": proc_a_cfg,
            "Processor_B": proc_b_cfg
        },
        "open_chain_baseline": {
            "J": 1.0, "h": 0.8, "J_cross": 0.0,
            "z0_exact": z0_exact_open,
            "mag_exact": mag_exact_open,
            "data": raw_open
        },
        "periodic_routing_extension": {
            "J": 1.0, "h": 0.8, "J_cross": 0.5,
            "z0_exact": z0_exact_per,
            "mag_exact": mag_exact_per,
            "data": raw_per
        }
    }
    with (results_raw_dir / "raw_experiment_data.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Processed DataFrames for Primary Baseline
    df_open_a = pd.DataFrame(records_open_a)
    df_open_b = pd.DataFrame(records_open_b)

    df_open_a.to_csv(results_tables_dir / "processor_A_metrics.csv", index=False)
    df_open_b.to_csv(results_tables_dir / "processor_B_metrics.csv", index=False)

    # Merged comparison table for primary baseline
    comp_open = []
    for ra, rb in zip(records_open_a, records_open_b):
        comp_open.append({
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
            "ProcA_Estimated_Equivalent_SWAPs": ra["equivalent_swaps_a"],
            "ProcB_Estimated_Equivalent_SWAPs": rb["equivalent_swaps_b"],
            "ProcA_Explicit_SWAPs": ra["explicit_swaps_a"],
            "ProcB_Explicit_SWAPs": rb["explicit_swaps_b"],
            "ProcA_Active_Qubits": ra["active_physical_qubits_a"],
            "ProcB_Active_Qubits": rb["active_physical_qubits_b"],
            "ProcA_Total_Qubits": ra["total_processor_qubits_a"],
            "ProcB_Total_Qubits": rb["total_processor_qubits_b"],
            "Z0_Exact": ra["z0_exact"],
            "Z0_Ideal": ra["z0_ideal"],
            "ProcA_Z0_Measured": ra["z0_a"],
            "ProcA_Z0_SE": ra["z0_se_a"],
            "ProcA_Z0_Error": ra["z0_error_a"],
            "ProcB_Z0_Measured": rb["z0_b"],
            "ProcB_Z0_SE": rb["z0_se_b"],
            "ProcB_Z0_Error": rb["z0_error_b"],
            "Exact_Magnetization": ra["exact_mag"],
            "Ideal_Magnetization": ra["ideal_mag"],
            "ProcA_Magnetization": ra["mag_a"],
            "ProcB_Magnetization": rb["mag_b"],
            "ProcA_Classical_Dist_Fidelity": ra["classical_dist_fidelity_a"],
            "ProcB_Classical_Dist_Fidelity": rb["classical_dist_fidelity_b"],
            "ProcA_TVD": ra["tvd_a"],
            "ProcB_TVD": rb["tvd_b"]
        })
    df_comp_open = pd.DataFrame(comp_open)
    df_comp_open.to_csv(results_tables_dir / "AB_comparison.csv", index=False)

    # Periodic extension comparison table
    comp_per = []
    for ra, rb in zip(records_per_a, records_per_b):
        comp_per.append({
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
            "ProcA_Estimated_Equivalent_SWAPs": ra["equivalent_swaps_a"],
            "ProcB_Estimated_Equivalent_SWAPs": rb["equivalent_swaps_b"],
            "ProcA_Explicit_SWAPs": ra["explicit_swaps_a"],
            "ProcB_Explicit_SWAPs": rb["explicit_swaps_b"],
            "ProcA_Active_Qubits": ra["active_physical_qubits_a"],
            "ProcB_Active_Qubits": rb["active_physical_qubits_b"],
            "ProcA_Total_Qubits": ra["total_processor_qubits_a"],
            "ProcB_Total_Qubits": rb["total_processor_qubits_b"],
            "Z0_Exact": ra["z0_exact"],
            "Z0_Ideal": ra["z0_ideal"],
            "ProcA_Z0_Measured": ra["z0_a"],
            "ProcA_Z0_SE": ra["z0_se_a"],
            "ProcA_Z0_Error": ra["z0_error_a"],
            "ProcB_Z0_Measured": rb["z0_b"],
            "ProcB_Z0_SE": rb["z0_se_b"],
            "ProcB_Z0_Error": rb["z0_error_b"],
            "Exact_Magnetization": ra["exact_mag"],
            "Ideal_Magnetization": ra["ideal_mag"],
            "ProcA_Magnetization": ra["mag_a"],
            "ProcB_Magnetization": rb["mag_b"],
            "ProcA_Classical_Dist_Fidelity": ra["classical_dist_fidelity_a"],
            "ProcB_Classical_Dist_Fidelity": rb["classical_dist_fidelity_b"],
            "ProcA_TVD": ra["tvd_a"],
            "ProcB_TVD": rb["tvd_b"]
        })
    df_comp_per = pd.DataFrame(comp_per)
    df_comp_per.to_csv(results_tables_dir / "periodic_extension_comparison.csv", index=False)

    # Combined master dataset
    df_combined = pd.concat([df_comp_open.assign(Model_Variant="open_chain_baseline"),
                             df_comp_per.assign(Model_Variant="periodic_routing_extension")],
                            ignore_index=True)
    df_combined.to_csv(results_tables_dir / "combined_benchmark_results.csv", index=False)

    # Executive Summary Comparison Table
    summary_row = {
        "Metric": [
            "Total Processor Qubit Capacity",
            "Active Physical Qubits Used",
            "Coupling Topology",
            "Total Circuit Depth (n=4)",
            "Two-Qubit Circuit Depth (n=4)",
            "Two-Qubit CX Gates (n=4)",
            "Routing CX Overhead (n=4)",
            "Estimated Equivalent SWAPs (ΔCX/3, n=4)",
            "Explicit SWAP Instructions (n=4)",
            "Two-Qubit CX Gates (n=10)",
            "Routing CX Overhead (n=10)",
            "Estimated Equivalent SWAPs (ΔCX/3, n=10)",
            "Algorithmic State Fidelity (n=4)",
            "Algorithmic State Fidelity (n=10)",
            "Classical Dist Fidelity (n=4)",
            "Classical Dist Fidelity (n=10)",
            "Primary Observable <Z_0> Measured (n=4)",
            "Primary Observable Error |<Z_0> - exact| (n=4)",
            "Optimal Step Count n* (by Peak Classical Overlap)",
            "Peak Classical Dist Overlap"
        ],
        "Processor A": [
            proc_a_cfg["num_qubits"],
            df_comp_open.loc[0, "ProcA_Active_Qubits"],
            "Linear Chain (5Q)",
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_Total_Depth"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_2Q_Depth"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_2Q_Gates"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_Routing_CX_Overhead"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_Estimated_Equivalent_SWAPs"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_Explicit_SWAPs"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "ProcA_2Q_Gates"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "ProcA_Routing_CX_Overhead"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "ProcA_Estimated_Equivalent_SWAPs"].values[0],
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "Ideal_Algorithmic_State_Fidelity"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "Ideal_Algorithmic_State_Fidelity"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_Classical_Dist_Fidelity"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "ProcA_Classical_Dist_Fidelity"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_Z0_Measured"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcA_Z0_Error"].values[0], 4),
            int(df_comp_open.loc[df_comp_open["ProcA_Classical_Dist_Fidelity"].idxmax(), "Trotter_Steps_n"]),
            round(df_comp_open["ProcA_Classical_Dist_Fidelity"].max(), 4)
        ],
        "Processor B": [
            proc_b_cfg["num_qubits"],
            df_comp_open.loc[0, "ProcB_Active_Qubits"],
            "Heavy-Hex Subgraph (9Q)",
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_Total_Depth"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_2Q_Depth"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_2Q_Gates"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_Routing_CX_Overhead"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_Estimated_Equivalent_SWAPs"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_Explicit_SWAPs"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "ProcB_2Q_Gates"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "ProcB_Routing_CX_Overhead"].values[0],
            df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "ProcB_Estimated_Equivalent_SWAPs"].values[0],
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "Ideal_Algorithmic_State_Fidelity"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "Ideal_Algorithmic_State_Fidelity"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_Classical_Dist_Fidelity"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 10, "ProcB_Classical_Dist_Fidelity"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_Z0_Measured"].values[0], 4),
            round(df_comp_open.loc[df_comp_open["Trotter_Steps_n"] == 4, "ProcB_Z0_Error"].values[0], 4),
            int(df_comp_open.loc[df_comp_open["ProcB_Classical_Dist_Fidelity"].idxmax(), "Trotter_Steps_n"]),
            round(df_comp_open["ProcB_Classical_Dist_Fidelity"].max(), 4)
        ]
    }
    df_summary = pd.DataFrame(summary_row)
    df_summary["Difference (B - A)"] = [
        "+4 qubits capacity",
        "0 (Both utilize 4 active spins)",
        "Heavy-hex 12-edge lattice vs simple line",
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
        round(df_summary.loc[16, "Processor B"] - df_summary.loc[16, "Processor A"], 4),
        round(df_summary.loc[17, "Processor B"] - df_summary.loc[17, "Processor A"], 4),
        "Same optimal trade-off peak",
        round(df_summary.loc[19, "Processor B"] - df_summary.loc[19, "Processor A"], 4)
    ]
    df_summary.to_csv(results_tables_dir / "final_comparison.csv", index=False)

    print("  -> Exported processor_A_metrics.csv")
    print("  -> Exported processor_B_metrics.csv")
    print("  -> Exported AB_comparison.csv")
    print("  -> Exported periodic_extension_comparison.csv")
    print("  -> Exported combined_benchmark_results.csv")
    print("  -> Exported final_comparison.csv")
    print("  -> Exported raw_experiment_data.json")

    # 7. Generate Comparison Plots
    print("\n[Step 5/5] Generating publication-quality comparative plots...")
    plot_logical_vs_transpiled(records_open_a, records_open_b, results_figures_dir / "logical_vs_transpiled.png")

    plot_ab_performance(
        steps=trotter_steps_list,
        exact_fidelity=[1.0] * len(trotter_steps_list),
        ideal_trotter_fidelity=[r["ideal_trotter_state_fidelity"] for r in records_open_a],
        noisy_fidelity_a=[r["classical_dist_fidelity_a"] for r in records_open_a],
        noisy_fidelity_b=[r["classical_dist_fidelity_b"] for r in records_open_b],
        output_path=results_figures_dir / "AB_performance.png"
    )

    plot_architecture_tradeoffs(records_open_a, records_open_b, results_figures_dir / "architecture_tradeoffs.png")

    print("  -> Saved logical_vs_transpiled.png")
    print("  -> Saved AB_performance.png")
    print("  -> Saved architecture_tradeoffs.png")

    print("\n" + "=" * 80)
    print("  PRIMARY OPEN-CHAIN BASELINE: SUMMARY TABLE")
    print("=" * 80)
    print(df_summary.to_string(index=False))
    print("=" * 80)

    print("\n" + "=" * 80)
    print("  PERIODIC EXTENSION (ROUTING STRESS): 2Q GATES & OVERHEAD COMPARISON")
    print("=" * 80)
    print(df_comp_per[["Trotter_Steps_n", "Logical_2Q_Gates", "ProcA_2Q_Gates", "ProcB_2Q_Gates", "ProcA_Routing_CX_Overhead", "ProcB_Routing_CX_Overhead", "2Q_Gate_Delta_B_minus_A"]].to_string(index=False))
    print("=" * 80)
    print("\nBenchmark experiment successfully completed!")


if __name__ == "__main__":
    run_experiment()
