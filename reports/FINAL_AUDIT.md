# Scientific Audit & Verification Report
## Qiskit Fall Fest 2026 — Phase 1: Problem S3 (Noise in Trotter Simulation)

**Project Location:** `C:\Users\LOKESH\quiskit phase 1\`  
**Target Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Selected Problem Statement:** `S3 — Noise in Trotter Simulation` (Track: Quantum Simulation)  
**Date of Audit:** October 11, 2026  

---

## 1. Official Requirement-to-Evidence Traceability Matrix

| # | Official Requirement | Source Document & Section | Implementation File | Verification Status & Evidence |
| :-: | :--- | :--- | :--- | :--- |
| **1** | Select exactly one problem statement | Participant Instructions §2; Starter Guide §13 | `src/problem.py`, `README.md` | **PASS** — Exclusively implements Problem `S3`. |
| **2** | Processor A: 5-qubit baseline graph & synthetic noise | Guideline §4; Starter Guide §6, §10, §12 | `processors/processor_A.json`, `src/processors.py` | **PASS** — Verified 5-qubit linear coupling map, basis gates, and noise parameters. |
| **3** | Processor B: 7-qubit heavy-hex contemporary compilation baseline | Guideline §4, §7; Starter Guide §12 | `processors/processor_B.json`, `src/processors.py` | **PASS** — Canonical 7-qubit heavy-hex subgraph with degree-3 junction nodes. |
| **4** | Separate ideal/reference and noisy baseline cases | Guideline §7 (Cases A1, A2, B1, B2) | `main.py`, `src/problem.py` | **PASS** — Noise-free statevector/Aer baseline evaluated alongside noisy simulation. |
| **5** | Controlled benchmark settings | Participant Instructions §5; Starter Guide §14 | `main.py` | **PASS** — Identical Hamiltonian ($J=1, h=0.8$), initial state $|1010\rangle$, shots ($4096$), and seed ($42$). |
| **6** | Extract problem & architecture metrics | Starter Guide §11.1, §11.2 | `src/transpilation.py`, `src/metrics.py` | **PASS** — Reports depth, CX gates, active vs total qubits, SWAPs, magnetization, TVD, and fidelities. |
| **7** | Distinguish quantum state fidelity from classical distribution overlap | Scientific Audit Priority 5 | `src/metrics.py`, `main.py` | **PASS** — Discretization pure-state fidelity is separated from classical Bhattacharyya overlap ($F_c$). |
| **8** | Machine-readable exports | Starter Guide §18 | `results/raw/`, `results/tables/` | **PASS** — Generated `raw_experiment_data.json` and 4 CSV tables. |
| **9** | Required figures generated | Starter Guide §18 | `results/figures/` | **PASS** — All 5 required PNG figures generated at 300 DPI. |
| **10** | Reproducibility & automated test suite | Participant Instructions §7, §10 | `tests/test_benchmark.py`, `requirements.txt` | **PASS** — 7 unit tests pass with zero failures. |
| **11** | AI Assistance Disclosure | Participant Instructions §11 | `AI_DISCLOSURE.md` | **PASS** — Disclosed according to competition policy. |

---

## 2. Processor Definitions Verification

### 2.1 Processor A ([processors/processor_A.json](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_A.json))
- **Qubit Count:** 5 physical qubits ($q_0 \dots q_4$).
- **Coupling Graph:** Directed bidirectional linear chain:
  `[[0,1], [1,0], [1,2], [2,1], [2,3], [3,2], [3,4], [4,3]]`.
- **Basis Gates:** `["rz", "sx", "x", "cx"]`.
- **Designated Ports:** `[0, 4]`.
- **Noise Model:**
  - Single-qubit depolarizing error: $p_1 = 0.001$ on `['x', 'sx']` (virtual $R_Z$ gates have 0 duration/error).
  - Two-qubit depolarizing error: $p_2 = 0.010$ on `['cx']`.
  - Readout error: $\begin{pmatrix} 0.99 & 0.01 \\ 0.02 & 0.98 \end{pmatrix}$.
- **Verification Status:** **VERIFIED** against Sections 6, 9, 10, and 12 of the official Starter Guide.

### 2.2 Processor B ([processors/processor_B.json](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_B.json))
- **Qubit Count:** 7 physical qubits ($q_0 \dots q_6$).
- **Coupling Graph:** Heavy-hex-inspired graph with junction nodes:
  Edges: $(0,1), (1,2), (1,3), (3,5), (4,5), (5,6)$.
  Coupling Map: 12 directed edges (bidirectional pairs).
- **Basis Gates:** `["rz", "sx", "x", "cx"]`.
- **Designated Ports:** `[0, 6]`.
- **Noise Model:**
  - Evaluated with identical gate noise rates ($p_1 = 0.001, p_2 = 0.010$) as Processor A.
  - **Scientific Rationale:** As mandated by the competition instructions (*"Distinguish connectivity effects from differences in gate sets or noise"*), holding noise parameters constant isolates the pure geometric compilation impact of the heavy-hex topology.
- **Verification Status:** **VERIFIED IMPLEMENTATION** matching contemporary IBM Falcon heavy-hex subgraphs (Slide 4 of `QFF_IBM_Hackathon_Guideline.pdf`).

---

## 3. Physics & Hamiltonian Audit

### 3.1 Model Formulation
The system simulates the 1D Transverse-Field Ising Model (TFIM):
$$H = - J \sum_{i=0}^{N-2} Z_i Z_{i+1} - J_{\text{cross}} Z_0 Z_{N-1} - h \sum_{i=0}^{N-1} X_i$$
with parameters $N = 4$ spins, $J = 1.0$, $h = 0.8$, $J_{\text{cross}} = 0.5$, initial state $|1010\rangle$, evolution time $T = 1.0$.

### 3.2 Gate Signs & Unitary Matching
- Unitary time propagation: $U(dt) = \exp(-i H dt)$.
- Single-spin rotation: $\exp(i h dt X_i) = R_X(-2 h dt, i)$ (since $R_X(\theta) = \exp(-i \theta X / 2)$).
- Two-spin interaction: $\exp(i J dt Z_j Z_k) = CX(j, k) \cdot R_Z(-2 J dt, k) \cdot CX(j, k)$ (since $R_Z(\theta) = \exp(-i \theta Z / 2)$).
- **Independent Numerical Verification:**
  In `tests/test_benchmark.py::test_independent_numerical_trotter_unitary`, the operator matrix of the circuit step was compared directly against `scipy.linalg.expm(-1j * H * dt)`.
  $$\|U_{\text{circuit}}(dt) - \exp(-i H dt)\| = 0.0203 \quad (\text{for } dt = 0.05)$$
  matching first-order Trotter error $\mathcal{O}(dt^2)$ with exact sign consistency.

### 3.3 Role of the Cross-Boundary Interaction ($J_{\text{cross}}$)
- Under pure Open Boundary Conditions ($J_{\text{cross}} = 0$), a 4-spin chain embeds directly onto both Processor A and Processor B with identical 2Q gate counts (24 CX gates at $n=4$).
- Under Periodic / Cross-Boundary Conditions ($J_{\text{cross}} > 0$), the logical ring requires non-local routing across the processor graph. Processor B's heavy-hex junctions allow compiling the interaction with **21 fewer CX gates at $n=4$** (53 vs 74) and **57 fewer CX gates at $n=10$** (137 vs 194), directly demonstrating the architectural routing advantage.

---

## 4. Metric Definitions & Scientific Integrity

To prevent misleading claims, all metrics are strictly defined and labeled:

1. **Ideal Algorithmic State Fidelity ($F_{\text{state}}$):**
   $$F_{\text{state}}(n) = |\langle \psi_{\text{exact}}(T) | \psi_{\text{trotter\_ideal}}(T) \rangle|^2$$
   Measures pure mathematical Trotter discretization error. Increases monotonically with step count $n$ ($0.1171$ at $n=1 \to 0.9488$ at $n=4 \to 0.9924$ at $n=10$).
2. **Classical Distribution Fidelity ($F_c$ / Bhattacharyya Overlap):**
   $$F_c(P_{\text{noisy}}, P_{\text{ideal}}) = \sum_x \sqrt{P_{\text{noisy}}(x) P_{\text{ideal}}(x)}$$
   Measures empirical measurement statistics overlap. Correctly labeled as a classical probability similarity metric, NOT quantum state fidelity.
3. **Total Variation Distance ($\text{TVD}$):**
   $$\text{TVD}(P, Q) = \frac{1}{2} \sum_x |P(x) - Q(x)| \in [0, 1]$$
4. **Physical Magnetization Error:**
   $$\epsilon_{M_z} = |\langle M_z \rangle_{\text{measured}} - \langle M_z \rangle_{\text{exact}}|$$
5. **Physical Qubit Accounting:**
   - `total_processor_qubits`: 5 (Processor A), 7 (Processor B).
   - `active_physical_qubits`: 4 active spins on both processors.

---

## 5. Actual Experiment & Test Outcomes

### 5.1 Test Suite Status
Command: `.venv\Scripts\python -m unittest tests/test_benchmark.py`
```text
Ran 7 tests in 0.262s
OK
```

### 5.2 Corrected Benchmark Results Table

| Metric | Processor A (5Q Line) | Processor B (7Q Heavy-Hex) | Difference (B - A) | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Total Processor Qubits** | 5 | 7 | +2 | Register capacity |
| **Active Physical Qubits** | 4 | 4 | 0 | Subgraph allocation |
| **Circuit Depth ($n=4$)** | 111 | 111 | 0 | Critical path depth |
| **Circuit Depth ($n=10$)** | 279 | 279 | 0 | Critical path depth |
| **Two-Qubit CX Gates ($n=4$)** | 74 | 53 | **-21 (-28.4%)** | Geometry routing reduction |
| **Two-Qubit CX Gates ($n=10$)** | 194 | 137 | **-57 (-29.4%)** | Less noise accumulation |
| **Algorithmic State Fidelity ($n=4$)** | 0.9488 | 0.9488 | 0.0 | Pure mathematical Trotter |
| **Algorithmic State Fidelity ($n=10$)** | 0.9924 | 0.9924 | 0.0 | Discretization refinement |
| **Classical Dist Fidelity ($n=4$)** | 0.9577 | **0.9653** | **+0.0076** | Measured distribution overlap |
| **Classical Dist Fidelity ($n=10$)** | 0.8919 | **0.9103** | **+0.0184** | Slower noise degradation on B |
| **Total Variation Distance ($n=10$)** | 0.3801 | **0.3477** | **-0.0324** | Closer to ideal distribution |
| **Optimal Step Count ($n^*$)** | $n=1$ | $n=1$ | 0 | Noise crossover threshold |

---

## 6. Limitations & Unverified Aspects

1. **Simulation Model vs. Physical Hardware:**
   All noisy benchmark runs were executed using Qiskit Aer's synthetic noise simulator with thermal depolarizing and readout errors. No physical quantum processor (cloud QPU) was executed.
2. **Phase 2 Scope Boundary:**
   In strict compliance with the competition instructions, Processor C (8-10 qubits) and participant-designed Processor D belong exclusively to Phase 2 and are omitted from this submission.
3. **Absence of Separate Organizer S3 File:**
   The organizer Google Drive contains general starter guides and slides, but no standalone `S3_Starter_Guide.pdf`. The implementation follows the general Phase 1 starter guide and S3 problem definition specifications.
