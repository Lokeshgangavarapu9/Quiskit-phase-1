# Project Architecture & Execution Pipeline Audit

**Project:** Qiskit Fall Fest 2026 — Phase 1 (Problem S3)  
**Document:** `reports/PROJECT_ARCHITECTURE_AUDIT.md`  

---

## 1. End-to-End Pipeline Architecture

The experimental pipeline is orchestrated to follow a rigorous scientific simulation workflow:

```text
┌─────────────────────────────────────────────────────────────┐
│                 1. Processor Configuration                  │
│       processors/processor_A.json & processor_B.json        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 2. Physical System Definition               │
│                  src/problem.py                             │
│  - 4-spin TFIM Hamiltonian Operator                         │
│  - Exact unitary reference: exp(-i H t) via SciPy expm      │
│  - Exact observable: <Z_0(t)> and <M_z(t)>                  │
│  - Logical Trotter circuits: U_Trotter(t, n)                │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            3. Transpilation & Hardware Compilation          │
│                  src/transpilation.py                       │
│  - Target coupling maps: 5Q Line vs. 9Q Heavy-Hex           │
│  - Basis gate unrolling: {rz, sx, x, cx}                    │
│  - Layout placement & routing (Sabre/Stochastic)            │
│  - Metric extraction: depth, 2Q depth, CX count, active Q   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             4. Controlled Simulation Execution              │
│                  src/processors.py & AerSimulator           │
│  - Case 1: Noise-free ideal AerSimulator                    │
│  - Case 2: Noisy AerSimulator with synthetic depolarizing    │
│            (p1=0.001, p2=0.005) + readout confusion         │
│  - 4096 measurement shots, seed = 42                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               5. Metric Computation Engine                  │
│                  src/metrics.py                             │
│  - Algorithmic Trotter State Fidelity: |<psi_exact|psi_T>|^2│
│  - Problem Observable: <Z_0(t)>, <M_z(t)> & standard error  │
│  - Classical Distribution Fidelity: sum sqrt(P_noisy * P_id)│
│  - Total Variation Distance (TVD): 0.5 * sum |P_noisy - P_id│
│  - Routing overhead & equivalent SWAPs: (CX_trans - CX_log)/3
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               6. Artifact Export & Visualization            │
│  - tables/processor_A_metrics.csv & processor_B_metrics.csv │
│  - tables/AB_comparison.csv & final_comparison.csv          │
│  - raw/raw_experiment_data.json                             │
│  - figures/ (5 publication-quality 300 DPI figures)         │
│  - reports/ and root report.md                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Component-by-Component Module Analysis

### 2.1 Configuration Layer (`processors/`)
- **`processor_A.json`**: Specifies a 5-qubit system. Currently configured with a linear chain (`0-1-2-3-4`), which is one of the two permitted reference baselines in the Master Guide.
  - *Finding:* Basis gates (`rz`, `sx`, `x`, `cx`) comply. Noise rates currently use $p_2 = 0.01$ and asymmetric readout instead of Master Guide's $p_2 = 0.005$ and symmetric $1\%$.
- **`processor_B.json`**: Specifies a 7-qubit heavy-hex subgraph (`nodes 0 to 6`).
  - *Finding:* Mismatched with Master Guide's 9-qubit physical budget (nodes 0 to 8) and 12-edge heavy-hex graph.

### 2.2 Problem Formulation Layer (`src/problem.py`)
- **Class `TrotterSimulationModel`**:
  - Encapsulates Pauli Hamiltonian representation (`SparsePauliOp`), dense matrix representation, exact classical statevector evolution via `scipy.linalg.expm`, and parameterized Trotter circuit building.
  - Correctly implements little-endian bit-ordering for Qiskit statevectors.
  - Implements state preparation from bitstrings and first-order Trotter loops.
  - *Finding:* Includes non-local $J_{\text{cross}}$ term. This term is an excellent routing benchmark, but should be configurable so the official open chain ($J_{\text{cross}} = 0$) can be demonstrated as the baseline.
  - *Finding:* Currently measures only total magnetization $\langle M_z(t) \rangle$, which vanishes under parity reflection. Needs to compute single-spin observable $\langle Z_0(t) \rangle$ as required by Master Guide PS-S2.

### 2.3 Compilation & Transpilation Layer (`src/transpilation.py`)
- **Function `compile_for_processor`**:
  - Invokes `qiskit.transpile` with fixed `optimization_level=1` and `seed_transpiler=42`.
- **Function `extract_circuit_metrics`**:
  - Accurately inspects `qc.data` to extract active physical qubits vs. total processor register size.
  - Computes critical path depth filtered for two-qubit operations (`two_qubit_depth`).
  - Correctly notes that explicit SWAPs are 0 because they are unrolled to native basis CX gates.

### 2.4 Noise Model Layer (`src/processors.py`)
- **Function `build_noise_model`**:
  - Constructs `qiskit_aer.noise.NoiseModel`.
  - Attaches 1Q depolarizing error to `['x', 'sx']` and 2Q depolarizing error to `['cx']`.
  - Attaches readout measurement error via `ReadoutError`.
  - Avoids unverified thermal relaxation ($T_1, T_2$).

### 2.5 Metrics Layer (`src/metrics.py`)
- Implements:
  1. `compute_quantum_state_fidelity`: Pure state fidelity $|\langle \psi | \phi \rangle|^2$.
  2. `compute_magnetization_from_counts`: Expectation value and standard error.
  3. `compute_tvd`: Total Variation Distance.
  4. `compute_classical_distribution_fidelity`: Bhattacharyya coefficient.
  5. `compute_proportion_error`: Statistical sampling error.
  - Handles edge cases cleanly (empty counts, division by zero).

### 2.6 Visualization Layer (`src/visualization.py`)
- Generates 5 figures at 300 DPI:
  - `processor_A_graph.png`
  - `processor_B_graph.png`
  - `logical_vs_transpiled.png`
  - `AB_performance.png`
  - `architecture_tradeoffs.png`
- *Finding:* The layout positions in `plot_processor_topology` currently hardcode coordinates for the 7-qubit Processor B. Updating Processor B to 9 qubits will require updating the node coordinate dictionary.

---

## 3. Discrepancies Between Entry Points: `main.py` vs. `main.ipynb`

1. **Notebook Execution State:**
   - In `main.py`, the benchmark runs from end to end and prints comprehensive terminal diagnostics.
   - In `main.ipynb`, cell execution counts are `null` and outputs are `[]`. The notebook has not been executed and saved with figures and tables embedded.
2. **Notebook Architectural Role:**
   - Cell 4 of `main.ipynb` imports `main` and calls `main.run_experiment()`.
   - The competition guidelines expect the notebook itself to clearly demonstrate the steps, display inline dataframes, and render plots directly for human and automated review.
