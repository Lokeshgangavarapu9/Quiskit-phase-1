# Qiskit Fall Fest 2026 — Phase 1 Submission

## Problem S3: Noise in Trotter Simulation

### Controlled Architecture Benchmarking: Processor A (5Q Line) vs. Processor B (9Q Heavy-Hex)

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python: 3.11](https://img.shields.io/badge/python-3.11.9-blue.svg)](https://www.python.org/)
[![Qiskit: 2.5](https://img.shields.io/badge/qiskit-2.5.2-purple.svg)](https://qiskit.org/)
[![Qiskit Aer: 0.17](https://img.shields.io/badge/qiskit--aer-0.17.2-red.svg)](https://github.com/Qiskit/qiskit-aer)

---

## 1. Executive Summary & Problem Scope

In digital quantum simulation, real-time Hamiltonian evolution $\hat{U}(t) = e^{-i \hat{H} t}$ is approximated on quantum processors via Trotter product formulas. This project tackles **Problem Statement S3 — Noise in Trotter Simulation** for **Qiskit Fall Fest 2026 Phase 1**.

### The Central Question

> *How does processor architecture geometry and routing influence the fundamental trade-off between algorithmic Trotter discretization error and physical hardware noise?*

Using the official organizer guidelines, we benchmark the same controlled 4-spin Transverse-Field Ising Model (TFIM) across two distinct quantum architectures:

- **Processor A:** 5-qubit linear chain baseline with synthetic depolarizing and readout noise.
- **Processor B:** 9-qubit heavy-hex reference baseline with identical gate error rates.

All experiments are deterministic, fully reproducible, and evaluated using both physical problem observables ($\langle Z_0(t) \rangle$, Total Variation Distance, Classical Fidelity) and architectural resource metrics (circuit depth, two-qubit gate count, routing SWAPs, physical qubit footprint).

---

## 2. Processor Architecture Definitions

| Architecture Property | Processor A (Baseline) | Processor B (Heavy-Hex Reference) |
| :--- | :--- | :--- |
| **Physical Qubits** | 5 (Nodes 0–4) | 9 (Nodes 0–8) |
| **Topology Graph** | Linear Chain ($0-1-2-3-4$) | Heavy-Hex Unit Cell Subgraph |
| **Undirected Coupling Edges** | 4 edges: `(0,1), (1,2), (2,3), (3,4)` | 12 edges: `(0,1), (1,2), (1,6), (2,3), (2,6), (2,5), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0)` |
| **Directed Pairs** | 8 | 24 |
| **Basis Gates** | `['rz', 'sx', 'x', 'cx']` | `['rz', 'sx', 'x', 'cx']` |
| **Designated Ports** | Qubits 0 and 4 | Qubits 0 and 8 |
| **Single-Qubit Error ($p_1$)** | 0.001 (on $x, sx$) | 0.001 (on $x, sx$) |
| **Two-Qubit Error ($p_2$)** | 0.005 (on $cx$) | 0.005 (on $cx$) |
| **Readout Error Matrix** | Symmetric $1\%$: `[[0.99, 0.01], [0.01, 0.99]]` | Symmetric $1\%$: `[[0.99, 0.01], [0.01, 0.99]]` |

![Processor A Graph](results/figures/processor_A_graph.png)
*Figure 1: Processor A 5-qubit linear chain coupling topology.*

![Processor B Graph](results/figures/processor_B_graph.png)
*Figure 2: Processor B 9-qubit heavy-hex lattice reference coupling topology.*

---

## 3. Physical Model & Methodology

### 3.1 Hamiltonian Specification

We simulate a 4-spin 1D chain governed by the Transverse-Field Ising Model (TFIM):
$$\hat{H} = - J \sum_{i=0}^{N-2} \hat{Z}_i \hat{Z}_{i+1} - J_{\text{cross}} \hat{Z}_0 \hat{Z}_{N-1} - h \sum_{i=0}^{N-1} \hat{X}_i$$

- **Spins:** $N = 4$, initial state $|\psi(0)\rangle = |1010\rangle$ (staggered Néel domain wall).
- **Parameters:** $J = 1.0$, $h = 0.8$, evolution time $T = 1.0$.
- **Boundary Conditions:**
  - **Primary Baseline ($J_{\text{cross}} = 0.0$):** Open-chain nearest-neighbor interactions only.
  - **Architectural Extension ($J_{\text{cross}} = 0.5$):** Periodic ring boundary condition creating a non-local interaction between spins 0 and 3 to stress hardware routing.

### 3.2 Observables & Symmetries

- **Primary Observable $\langle Z_0(t) \rangle$:** Single-site expectation value. At $t=0$, $\langle Z_0(0) \rangle = +1.0$. At $T=1.0$, $\langle Z_0(1.0) \rangle = +0.257957$ (open chain) and $+0.421887$ (periodic ring).
- **Secondary Diagnostic $\langle M_z(t) \rangle$:** Total average magnetization $\frac{1}{4} \sum_i \langle Z_i(t) \rangle \equiv 0.000000$ identically for all $t$ due to spatial reflection anti-symmetry $\mathcal{P} \hat{H} \mathcal{P}^\dagger = \hat{H}$ on $|1010\rangle$.

---

## 4. Benchmark Results & Comparative Findings

Experiments were executed over step counts $n \in \{1, 2, 3, 4, 5, 6, 8, 10\}$ with 4096 shots and fixed deterministic seeds (`seed=42`).

### 4.1 Primary Open-Chain Baseline Summary ($J_{\text{cross}} = 0.0$)

| Metric | Processor A (5Q Line) | Processor B (9Q Heavy-Hex) | Difference (B - A) | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Total Processor Capacity** | 5 | 9 | +4 qubits | Register capacity |
| **Active Physical Qubits** | 4 | 4 | 0 | Both allocate 4 spins |
| **Coupling Topology** | Linear Chain | Heavy-Hex Subgraph | Higher connectivity | Both embed line directly |
| **Total Circuit Depth ($n=4$)** | 49 | 49 | 0 | Equal depth |
| **Two-Qubit Depth ($n=4$)** | 18 | 18 | 0 | Equal 2Q critical path |
| **Two-Qubit CX Gates ($n=4$)** | 24 | 24 | 0 | Zero routing overhead |
| **Routing CX Overhead ($n=4$)** | 0 | 0 | 0 | Direct subgraph match |
| **Two-Qubit CX Gates ($n=10$)** | 60 | 60 | 0 | Identical scaling |
| **Ideal State Fidelity ($n=4$)** | 0.9648 | 0.9648 | 0.0 | Discretization error only |
| **Ideal State Fidelity ($n=10$)** | 0.9949 | 0.9949 | 0.0 | Discretization error only |
| **Classical Dist Overlap $F_c$ ($n=4$)** | 0.9949 | 0.9949 | 0.0 | Under depolarizing + readout |
| **Classical Dist Overlap $F_c$ ($n=10$)** | 0.9842 | 0.9842 | 0.0 | Noise outpaces refinement |
| **Measured $\langle Z_0 \rangle$ ($n=4$)** | 0.2310 | 0.2310 | 0.0 | Exact target: $0.257957$ |
| **Observable Error $\| \langle Z_0 \rangle - \text{exact} \|$ ($n=4$)** | 0.0270 | 0.0270 | 0.0 | Accurate physical recovery |
| **Optimal Step Count $n^*$** | 1 | 1 | 0 | Peak overlap ($F_c = 0.9999$) |

### 4.2 Periodic Ring Extension Routing Comparison ($J_{\text{cross}} = 0.5$)

| Steps $n$ | Logical CX | Proc A CX (5Q Line) | Proc B CX (9Q Heavy-Hex) | Proc A Routing $\Delta CX$ | Proc B Routing $\Delta CX$ | Proc B CX Reduction |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 8 | 14 | **8** | 6 | **0** | **-42.9%** |
| **2** | 16 | 32 | **16** | 16 | **0** | **-50.0%** |
| **4** | 32 | 74 | **32** | 42 | **0** | **-56.8%** |
| **8** | 64 | 154 | **64** | 90 | **0** | **-58.4%** |
| **10** | 80 | 194 | **80** | 114 | **0** | **-58.8%** |

![Logical vs Transpiled Scaling](results/figures/logical_vs_transpiled.png)
*Figure 3: Circuit depth and two-qubit operation scaling vs. Trotter step count $n$.*

![Trotter Fidelity Trade-off](results/figures/AB_performance.png)
*Figure 4: Trotter simulation fidelity trade-off: algorithmic discretization vs. hardware noise accumulation.*

![Architecture Trade-offs Dashboard](results/figures/architecture_tradeoffs.png)
*Figure 5: 4-panel architecture dashboard: TVD, routing CX overhead, observable error, and 2Q gate accumulation.*

---

## 5. Architectural Co-Design Proposal: Processor D

Per the hackathon organizers' WhatsApp instructions:
> *"Illustrate the problem faced when running the problem statement on the provided processors and propose a solution involving Processor D."*

### 5.1 Empirical Failure Modes on Processors A & B

1. **Processor A (1D Line Baseline):** Linear distance between boundary spins causes severe routing overhead for cyclic/periodic spin systems: **14 SWAPs (42 extra CX gates)** at $n=4$, scaling as $\mathcal{O}(N^2)$ for larger chains.
2. **Processor B (9-Qubit Reference Topology):** While its reference heavy-hex unit cell embeds a 4-spin ring with 0 SWAPs, its low maximum vertex degree (degree 3) cannot natively embed 2D lattices ($2 \times 3, 2 \times 4$ spin grids) or larger rings without high-latency routing across sparse bridge nodes.

### 5.2 Proposed Processor D Specification (12-Qubit Ring-Ladder)

We propose a **12-qubit Cylindrical Ring-Ladder Architecture** ($|V|=12, |E|=18$, 3-regular) co-designed for lattice quantum dynamics:

- **Topology:** Two coupled 6-qubit rings with 6 vertical rungs connecting corresponding pairs $(i, i+6)$.
- **Verified Zero-SWAP Subgraphs:** 4-spin ring ($C_4$), 6-spin ring ($C_6$), 8-spin ring ($C_8$), 12-spin ring ($C_{12}$), $2 \times 3$ grid, and $2 \times 4$ grid with **0 routing SWAPs**.
- **Native Gate Co-Design:** Native parameterized $R_{zz}(\theta)$ entangling gates, replacing standard 2-$CX$ decompositions ($CX \to R_z \to CX$) with single direct entangling pulses, yielding an illustrative **70% reduction in entangling gate duration** based on pulse literature ($120\text{ ns}$ vs $400\text{ ns}$).
- **Status:** Architectural proposal and co-design analysis (Category B) based on Phase 1 empirical findings; distinguished strictly from empirical hardware measurements.

---

## 6. Repository Structure

```text
Quiskit-phase-1/
├── README.md                          # Project overview, setup, and key results
├── report.md                          # Full scientific submission report
├── AI_DISCLOSURE.md                   # Truthful AI-use disclosure (Participant Rules §11)
├── requirements.txt                   # Reproducible Python dependencies
├── main.py                            # End-to-end benchmark orchestration pipeline
├── main.ipynb                         # Executed student walkthrough notebook (with saved outputs)
├── main.ipynb.bak                     # Preserved pre-modification notebook backup
├── docs/
│   └── STUDENT_WALKTHROUGH.md         # Comprehensive study & defense guide
├── processors/
│   ├── processor_A.json               # 5-qubit linear chain config + verified noise
│   └── processor_B.json               # 9-qubit heavy-hex config + verified noise
├── src/
│   ├── problem.py                     # TFIM model, exact expm reference, Trotter circuits, observables
│   ├── processors.py                  # Config loading, CouplingMap, and NoiseModel builders
│   ├── transpilation.py               # Preset pass manager compilation & metric extraction
│   ├── metrics.py                     # Counts estimators (Z0, Mz), TVD, classical & state fidelity
│   └── visualization.py               # Publication-grade topology and benchmark figures
├── tests/
│   └── test_benchmark.py              # 11 unit & regression tests (physics, noise, routing, edge cases)
├── results/
│   ├── archived_7q_v1/                # Preserved original baseline outputs before modification
│   ├── raw/
│   │   └── raw_experiment_data.json   # Full raw JSON output + execution metadata
│   ├── tables/                        # Machine-readable CSV summaries
│   │   ├── processor_A_metrics.csv
│   │   ├── processor_B_metrics.csv
│   │   ├── AB_comparison.csv
│   │   ├── periodic_extension_comparison.csv
│   │   ├── combined_benchmark_results.csv
│   │   └── final_comparison.csv
│   └── figures/                       # Publication-grade PNG plots
└── scratch/                           # Verification and execution scripts
```

---

## 7. How to Reproduce

All commands can be executed in the local virtual environment:

```bash
# 1. Run unit test suite (11/11 tests pass)
.venv\Scripts\python.exe -m unittest tests/test_benchmark.py

# 2. Run full benchmark pipeline and regenerate CSVs/plots
.venv\Scripts\python.exe main.py

# 3. Validate clean-kernel notebook execution
.venv\Scripts\python.exe scratch/execute_notebook.py
```
