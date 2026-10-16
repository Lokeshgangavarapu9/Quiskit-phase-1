# Official Competition Requirements & Compliance Audit

**Project:** Qiskit Fall Fest 2026 — Phase 1  
**Track:** Quantum Simulation (Hamiltonian Dynamics)  
**Problem Statement:** `PS-S3: Noise Accumulation in Trotter Circuits`  
**Host Institution:** SRM University-AP  
**Authoritative Reference:** *Qiskit Fall Fest 2026 — Phase 1 Master Guide (Official Unified Challenge Kit)*  

---

## 1. Authoritative Requirements Summary

### 1.1 Problem Identity

- **Track:** Track 3 — Quantum Simulation (Hamiltonian Dynamics)
- **Problem Code:** `PS-S3`
- **Official Problem Title:** *Noise Accumulation in Trotter Circuits* (also referred to as *Noise in Trotter Simulation*)
- **Core Scientific Question:** How does quantum processor connectivity and gate routing influence the fundamental trade-off between algorithmic Trotter discretization error and synthetic physical hardware noise as the number of Trotter steps increases?

### 1.2 Physical System & Evolution Specifications

- **Model:** 4-spin 1D Transverse-Field Ising Model (TFIM):
  $$H = - J \sum_{i=0}^{N-2} Z_i Z_{i+1} - g \sum_{i=0}^{N-1} X_i$$
  with standard coupling $J = 1.0$ and external transverse field $g \in \{0.5, 1.0, 1.5\}$.
- **Spin Count:** $N = 4$ qubits.
- **Initial State:** Ferromagnetic ground state $|0000\rangle$ or staggered antiferromagnetic Néel state $|0101\rangle$.
- **Evolution Duration:** Real-time unitary evolution $U(t) = \exp(-iHt)$ up to $t = 2.0$.
- **Trotterization Formula:** First-order Suzuki-Trotter product formula:
  $$U(t) \approx \left[ \prod_i e^{-i H_{ZZ, i} \Delta t} \prod_j e^{-i H_{X, j} \Delta t} \right]^n, \quad \Delta t = \frac{t}{n}$$
- **Required Trotter Step Counts:** $n = 1, 2, 4$ (at minimum; higher steps permitted for scaling curves).
- **Core Physical Observables:**
  - Single-site expectation value $\langle Z_0(t) \rangle$ or two-point correlators.
  - State fidelity with respect to exact matrix exponentiation ($\exp(-iHt)$ via `scipy.linalg.expm`).
  - Total Variation Distance (TVD) and measurement probability distributions.

---

## 2. Processor & Noise Specifications

### 2.1 Processor A (Baseline Reference)

- **Qubit Count:** 5 physical qubits (Nodes 0 to 4).
- **Coupling Topologies (Reference):**
  - Linear chain: `[(0,1), (1,2), (2,3), (3,4)]`
  - Branching tree: `[(0,1), (1,2), (1,3), (3,4)]`
- **Native Basis Gates:** `['rz', 'sx', 'x', 'cx']`
- **Designated I/O Ports:** Qubits 0 and 4.

### 2.2 Processor B (Contemporary Heavy-Hex Reference)

- **Qubit Count:** 9 physical qubits (Nodes 0 to 8).
- **Coupling Topology (Reference):** Sparse 9-qubit heavy-hex-inspired graph with 12 undirected edges:
  $$(0,1), (1,2), (1,6), (2,3), (2,6), (2,5), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0)$$
- **Native Basis Gates:** `['rz', 'sx', 'x', 'cx']`
- **Creative Freedom Clause:** The Master Guide explicitly states that coupling maps are *reference baselines*. Participants may design, justify, and transpile valid 5-qubit and 9-qubit graphs to explore routing trade-offs.

### 2.3 Synthetic Noise Model

- **Single-Qubit Gate Error:** Depolarizing noise $p_1 = 0.001$ ($0.1\%$) applied to `x` and `sx` gates.
- **Two-Qubit Gate Error:** Depolarizing noise $p_2 = 0.005$ ($0.5\%$) applied to `cx` gates.
- **Readout Error:** Symmetric measurement bit-flip error of $1.0\%$ ($p = 0.01$).
- **Thermal Relaxation ($T_1, T_2$):** Excluded by official specification.

### 2.4 Transpilation & Simulation Baseline

- **Optimization Level:** `optimization_level = 1`
- **Transpiler Seed:** `seed_transpiler = 42`
- **Simulator Shots:** `shots = 4096`
- **Simulator Seed:** `seed_simulator = 42`

---

## 3. Scope Boundaries: Phase 1 vs. Phase 2

| Element | Phase 1 (Online Qualification) | Phase 2 (Offline Onsite Finals) |
| :--- | :--- | :--- |
| **Processor Models** | **Processor A (5Q) and Processor B (9Q) ONLY** | Introduces Processor C (experimental) & custom Processor D |
| **Hardware Execution** | Controlled synthetic Qiskit Aer simulation | Possible QPU cloud execution or specialized backends |
| **Special Protocols** | Trotterization error vs. noise trade-off | Bell-state correlation & error mitigation / protection |
| **Submission Deadline** | **Saturday, October 17, 2026, 23:59 IST** | Onsite hackathon dates (TBA for shortlisted finalists) |

---

## 4. Deliverables & Repository Structure Compliance

The Master Guide defines the mandatory submission layout:

```text
project/
├── README.md                 # Problem statement, setup, methodology, key results
├── main.ipynb                # End-to-end reproducible experiment notebook (WITH OUTPUTS)
├── requirements.txt          # Pinned dependencies (qiskit, qiskit-aer, networkx, etc.)
├── data/
│   ├── raw/                  # Raw simulation dumps
│   └── processed/            # Cleaned arrays/matrices
├── processors/
│   ├── processor_A.json      # Processor A coupling map & config
│   └── processor_B.json      # Processor B coupling map & config
├── src/
│   ├── __init__.py
│   ├── problem.py            # Hamiltonian formulation & Trotter circuit logic
│   ├── processors.py         # Topology graph definition & noise model loaders
│   ├── routing.py            # Transpilation & layout routing routines
│   ├── metrics.py            # Circuit metrics (depth, CX, SWAP, fidelity)
│   └── visualization.py      # Plotting & coupling graph visualizers
├── results/
│   ├── tables/               # Exported CSV/JSON benchmark comparison tables
│   └── figures/              # Exported comparison figures (depth, fidelity, trade-offs)
├── report.md                 # Architectural analysis, trade-off interpretation
└── assets/                   # Visual or equation assets
```

---

## 5. Official Judging Rubric (SRM University-AP Phase 1)

| Category | Weight | Indicative Judging Criteria | Repository Status |
| :--- | :---: | :--- | :---: |
| **Scientific & Algorithmic Correctness** | **30 pts** | Does the algorithm execute without errors? Are results compared against an exact classical theoretical reference? Is Trotter convergence verified? | **PARTIAL** (Trotterization is exact, but $\langle M_z \rangle$ vanishes under parity; needs $\langle Z_0(t) \rangle$) |
| **Processor A vs B Architectural Analysis & Creativity** | **35 pts** | Quantitative comparison: circuit depth, CX count, SWAP routing overhead, noise impact. Reasoned exploration of coupling topologies. | **PARTIAL** (Excellent analysis, but Processor B is currently 7Q instead of 9Q, and $p_2=0.01$ instead of $0.005$) |
| **Reproducibility & Code Quality** | **20 pts** | Clean environment, pinned requirements.txt, structured repository, and end-to-end runnable notebook. | **PARTIAL** (`main.py` is reproducible, but `main.ipynb` has unexecuted empty outputs) |
| **Documentation & Visualizations** | **15 pts** | Clear README, coupling map diagrams, legible performance comparison plots, and comprehensive report. | **PARTIAL** (README is strong, but root `report.md` is missing and `AI_DISCLOSURE.md` is empty) |
| **Total** | **100 pts** | | |

---

## 6. Categorization of All Project Elements

### 6.1 Officially Stated Requirements

1. Problem Statement: PS-S3 under Quantum Simulation.
2. Two-processor comparison: Processor A (5 qubits) vs. Processor B (9 qubits).
3. Basis gate set: `{rz, sx, x, cx}`.
4. Noise model: 1Q depolarizing (0.1%), 2Q depolarizing (0.5%), Readout error (1.0%).
5. Controlled simulation: Same shots (4096), optimization level (1), seed (42).
6. Required deliverables: `README.md`, `main.ipynb`, `processors/`, `src/`, `results/`, `requirements.txt`, `report.md`.
7. Scope constraint: Strictly Processor A and B.

### 6.2 Repository Assumptions

1. Fixed total simulation time $T = 1.0$ (within the $t \le 2.0$ window).
2. Evaluation over an expanded sweep $n \in \{1, 2, 3, 4, 5, 6, 8, 10\}$ (encompassing the required $n \in \{1, 2, 4\}$).
3. Estimation of equivalent SWAPs via $(\text{Transpiled CX} - \text{Logical CX}) / 3$.

### 6.3 Research Extensions (Non-Mandatory Additions)

1. **Periodic Cross-Boundary Coupling ($J_{\text{cross}} = 0.5$):** Added by the student to force non-local routing across the processor graph.
   - *Assessment:* Scientifically insightful, but must be presented alongside the official open-chain baseline ($J_{\text{cross}} = 0$) so judges see exact compliance first.
2. **Measurement Distribution Similarity Metrics (Classical Fidelity / TVD):** Supplements the required observable and state fidelity metrics.

### 6.4 Unresolved Requirements / Clarifications

1. **Module Naming Convention:** Master Guide lists `src/routing.py`, while repo uses `src/transpilation.py`. Both function identically; aliasing or renaming solves this cleanly.
2. **Report Placement:** Master Guide specifies `report.md` at root, whereas existing documents reside in `reports/`. Placing a synthesized `report.md` at root fulfills the requirement directly.
