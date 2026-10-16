# Detailed Project Correction Plan

**Project:** Qiskit Fall Fest 2026 — Phase 1 (Problem S3)  
**Document:** `reports/CORRECTION_PLAN.md`  
**Execution Condition:** **AWAITING EXPLICIT USER APPROVAL ("START IMPLEMENTATION")**  

---

## 1. Overview & Strategy

This correction plan brings the existing repository into **100% compliance** with the authoritative **Phase 1 Master Guide (SRM University-AP)** while preserving all working architectural abstractions, mathematical proofs, and modular design.

The plan is structured in 6 strictly sequential stages based on code dependencies:

```text
Stage 1: Physical Model & Observable Updates
   │
   ▼
Stage 2: Processor Architecture & Noise Configuration Updates
   │
   ▼
Stage 3: Benchmark Re-Execution & Artifact Generation
   │
   ▼
Stage 4: Test Suite Synchronization & Regression Checks
   │
   ▼
Stage 5: Self-Contained Jupyter Notebook Execution
   │
   ▼
Stage 6: Report Synthesis, AI Disclosure, & Documentation Reconciliation
```

---

## 2. Stage-by-Stage Implementation Plan

### Stage 1: Physical Model & Observable Updates

- **Files Affected:** [`src/problem.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/problem.py), [`src/metrics.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/metrics.py)
- **Exact Modifications:**
  1. Add method `compute_exact_single_site_z(t, site=0)` in `TrotterSimulationModel` to compute $\langle Z_0(t) \rangle_{\text{exact}} = \langle \psi(t) | Z_0 | \psi(t) \rangle$.
  2. Add method `compute_single_site_z_from_counts(counts, num_spins, site=0)` in `src/metrics.py` to extract $\langle Z_0 \rangle$ and its standard error from empirical measurement shot distributions.
  3. Ensure boundary condition parameter allows both `boundary='open'` ($J_{\text{cross}}=0.0$, official baseline) and `boundary='periodic'` ($J_{\text{cross}}=0.5$, routing stress test).
- **Rationale:** Resolves Issue P0-4. Directly satisfies the Master Guide PS-S2 instruction to measure $\langle Z_0(t) \rangle$ while preserving $\langle M_z(t) \rangle$ for symmetry demonstration.
- **Validation Method:** Unit test verifying $\langle Z_0(0) \rangle = +1.0$ and non-zero oscillation over time $t$.

---

### Stage 2: Hardware Architecture & Noise Configuration Updates

- **Files Affected:**
  - [`processors/processor_A.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_A.json)
  - [`processors/processor_B.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_B.json)
  - [`src/visualization.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/visualization.py)
- **Exact Modifications:**
  1. **Processor A JSON:**
     - Update `two_qubit_depolarizing_p` from `0.01` to `0.005` ($0.5\%$).
     - Update `readout_error_matrix` to symmetric $[[0.99, 0.01], [0.01, 0.99]]$.
  2. **Processor B JSON:**
     - Set `"num_qubits": 9`.
     - Update `"display_name": "Processor B (9-Qubit Heavy-Hex Baseline)"`.
     - Update `"coupling_map"` to the 12 bidirectional pairs of the Master Guide graph:
       $$(0,1), (1,2), (1,6), (2,3), (2,6), (2,5), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0)$$
     - Set `two_qubit_depolarizing_p = 0.005` ($0.5\%$).
     - Set symmetric readout error matrix $[[0.99, 0.01], [0.01, 0.99]]$.
     - Set `"ports": [0, 8]` (or designated graph boundary nodes).
  3. **Visualization Module (`src/visualization.py`):**
     - Update `plot_processor_topology` node coordinate dictionary `pos` for Processor B to display all 9 nodes in a clean heavy-hex layout.
- **Rationale:** Resolves Issues P0-1, P0-2, and P0-3. Brings hardware models into exact compliance with the Master Guide.
- **Validation Method:** Test loading both processor JSON files into Qiskit `CouplingMap` and `NoiseModel` without errors.

---

### Stage 3: Benchmark Re-Execution & Artifact Generation

- **Files Affected:** [`main.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/main.py)
- **Exact Modifications:**
  1. Track both $\langle Z_0(t) \rangle$ and $\langle M_z(t) \rangle$ across all Trotter step counts $n \in \{1, 2, 3, 4, 5, 6, 8, 10\}$.
  2. Extract both the official baseline ($n \in \{1, 2, 4\}$) and the extended sweep.
  3. Re-run `main.py` using `.venv\Scripts\python.exe main.py` with pinned seeds (`seed=42`).
- **Regenerated Artifacts:**
  - `results/tables/processor_A_metrics.csv`
  - `results/tables/processor_B_metrics.csv`
  - `results/tables/AB_comparison.csv`
  - `results/tables/final_comparison.csv`
  - `results/raw/raw_experiment_data.json`
  - `results/figures/processor_A_graph.png`
  - `results/figures/processor_B_graph.png`
  - `results/figures/logical_vs_transpiled.png`
  - `results/figures/AB_performance.png`
  - `results/figures/architecture_tradeoffs.png`
- **Rationale:** Resolves Issue P1-1. Replaces stale results with authoritative 9-qubit, $p_2=0.005$ benchmark data.
- **Validation Method:** Verify that all output CSVs and JSON files are non-empty and report valid numerical ranges.

---

### Stage 4: Test Suite Synchronization & Regression Checks

- **Files Affected:** [`tests/test_benchmark.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/tests/test_benchmark.py)
- **Exact Modifications:**
  1. Update `test_processor_configurations` to assert `cfg_b["num_qubits"] == 9`.
  2. Update `test_transpilation_and_active_qubits_extraction` to verify 9 total register qubits and 4 active physical qubits.
  3. Update `test_routing_cx_overhead_and_unrolled_swaps` to verify the new CX gate counts on 9-qubit Processor B.
  4. Add unit test `test_single_site_z_magnetization` verifying non-zero $\langle Z_0(t) \rangle$ oscillation and Trotter convergence.
  5. Run test suite: `.\.venv\Scripts\python.exe -m unittest tests/test_benchmark.py`.
- **Rationale:** Resolves Issue P2-2. Ensures 100% passing tests reflecting the new hardware and physical observable.
- **Validation Method:** All unit tests pass with `OK`.

---

### Stage 5: Self-Contained Jupyter Notebook Execution

- **Files Affected:** [`main.ipynb`](file:///c:/Users/LOKESH/quiskit%20phase%201/main.ipynb)
- **Exact Modifications:**
  1. Restructure `main.ipynb` into modular, instructional cells with complete markdown descriptions.
  2. Include explicit cell steps:
     - Cell 1: Environment check & imports.
     - Cell 2: Processor loading & coupling graph visualization.
     - Cell 3: TFIM Hamiltonian formulation & exact SciPy diagonalization.
     - Cell 4: Trotter circuit generation & transpilation onto Processors A and B.
     - Cell 5: Ideal vs. Noisy Qiskit Aer simulation sweeps.
     - Cell 6: Metric calculation ($\langle Z_0 \rangle$, State Fidelity, Classical Fidelity, TVD, Depth, CX count).
     - Cell 7: Display formatted benchmark comparison table.
     - Cell 8: Inline rendering of comparison plots.
     - Cell 9: Scientific conclusions and architectural insights.
  3. Execute the notebook from start to finish via `nbconvert` or automated runner.
  4. Save the executed notebook with all outputs, tables, and images preserved.
- **Rationale:** Resolves Issue P2-1. Fulfills the official requirement for a reproducible notebook that automated judging scripts can inspect.
- **Validation Method:** Verify that `main.ipynb` contains populated `"execution_count"` and `"outputs"` fields.

---

### Stage 6: Report Synthesis, AI Disclosure, & Documentation

- **Files Affected:**
  - [`report.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/report.md) (Create at root)
  - [`AI_DISCLOSURE.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/AI_DISCLOSURE.md)
  - [`README.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/README.md)
  - [`docs/STUDENT_WALKTHROUGH.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/docs/STUDENT_WALKTHROUGH.md)
- **Exact Modifications:**
  1. **Root `report.md`:** Create a comprehensive, professional scientific report at the project root matching the Master Guide file tree. Include sections: Executive Summary, Official Requirements Compliance, Model & Hamiltonian, Architecture & Routing Analysis, Benchmark Results Table, Trotter Error vs. Noise Discussion, Limitations, and Oral Defense Guide.
  2. **`AI_DISCLOSURE.md`:** Populate with a transparent disclosure conforming to Participant Instructions Section 11, detailing the use of Antigravity AI pair programming for code modularization, auditing, and documentation verification.
  3. **`README.md`:** Update executive summary table, topology descriptions, and scaling figures to reflect the 9-qubit Processor B and $0.5\%$ CX depolarizing noise model.
  4. **`docs/STUDENT_WALKTHROUGH.md`:** Update study notes to reflect the 9-qubit topology and $\langle Z_0(t) \rangle$ observable.
- **Rationale:** Resolves Issues P3-1, P3-2, and P3-3. Guarantees top marks in "Documentation & Visualizations" (15 pts).
- **Validation Method:** Cross-check final files against the Participant Closing Checklist in the Master Guide.

---

## 3. Risk Assessment & Safeguards

| Risk | Mitigation |
| :--- | :--- |
| **Accidental loss of original experimental data** | Original CSV and JSON files will be backed up in a `results/archived_7q_v1/` subfolder before regenerating. |
| **Transpilation seed divergence across Qiskit versions** | `seed_transpiler=42` and `seed_simulator=42` are strictly pinned, guaranteeing deterministic compilation. |
| **Global environment contamination** | All executions use the project's existing isolated `.venv` (`Python 3.11.9`). No global `pip install` commands will be run. |

---

## 4. Execution Hold Statement

> [!IMPORTANT]
> **AUDIT AND PLANNING COMPLETE.**
> In accordance with your explicit instructions, **no existing project code or configuration files have been modified**.
> Implementation will **NOT** begin until you explicitly provide the approval phrase:
> **"START IMPLEMENTATION"**
