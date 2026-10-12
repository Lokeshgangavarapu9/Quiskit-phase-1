# Scientific Audit & Verification Report

## Qiskit Fall Fest 2026 — Phase 1: Problem S3 (Noise in Trotter Simulation)

**Project Location:** `C:\Users\LOKESH\quiskit phase 1\`  
**Target Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Selected Problem Statement:** `S3 — Noise in Trotter Simulation` (Track: Quantum Simulation)  
**Date of Audit:** October 11, 2026  
**Auditor:** Autonomous Verification Engine  

---

## 1. Pre-Submission Defect & Correction Audit Table

| Issue | Original Behavior | Evidence | Correction Applied | Test Performed | Final Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **Noise Model: Unsupported Thermal Relaxation Claims** | Text in reports and README claimed "thermal relaxation channels (T1/T2)". | Starter Guide p. 12–13 specifies single-qubit depolarizing ($p_1=0.001$), two-qubit depolarizing ($p_2=0.01$), and readout errors. Thermal relaxation is **not** specified. | Removed all claims of thermal relaxation. Code in `src/processors.py` strictly adheres to depolarizing and readout noise models as defined in Starter Guide p. 13. | `test_noise_model_exact_channels` confirms depolarizing and readout channels without thermal relaxation. | **PASS** |
| **Routing Overhead vs. Explicit SWAP Accounting** | Tables reported `SWAP count = 0` on both A and B, while text claimed "fewer SWAPs explain gate savings". | The basis gates `['rz', 'sx', 'x', 'cx']` do not include `swap`. The transpiler decomposes each routing SWAP into 3 native CX gates, leaving explicit `swap_count = 0`. | Clarified explicit SWAPs (0) vs. Routing CX Overhead ($42$ on A vs. $21$ on B at $n=4$). Derived equivalent SWAPs ($14$ on A vs. $7$ on B). | `test_routing_cx_overhead_and_unrolled_swaps` validates basis unrolling and gate counts. | **PASS** |
| **Circuit Depth vs. CX Count Discrepancy** | Both processors reported depth $111$ at $n=4$, despite Processor B having 21 fewer CX gates. | Critical path inspection showed that on B, two-qubit interactions route through degree-3 hub node 1, putting 53 CX gates on the critical path, matching A's busiest qubit chain. | Separated Total Critical Path Depth ($111$ on both) from Two-Qubit Depth ($53$ on both) and Total Two-Qubit CX Gates ($74$ on A vs. $53$ on B). | `test_routing_cx_overhead_and_unrolled_swaps` inspects 2Q depth and operations. | **PASS** |
| **Exact Magnetization Sits Near Zero** | Tables reported `Exact_Magnetization = 2.78e-17`, while noisy simulations reported non-zero values. | Spatial reflection symmetry $\mathcal{P} H \mathcal{P}^\dagger = H$ acting on $\vert \psi_0\rangle = \vert 1010\rangle$ enforces $\langle Z_0(t)\rangle = -\langle Z_3(t)\rangle$ and $\langle Z_1(t)\rangle = -\langle Z_2(t)\rangle$, giving identically zero sum for all $t$. | Documented that exact zero magnetization is an exact physical symmetry. Noisy non-zero values arise from asymmetric readout errors ($P(0\mid 1)=0.02 \ne P(1\mid 0)=0.01$). Added `Ideal_Measured_Magnetization`. | `test_exact_magnetization_reflection_symmetry` verifies pairwise cancellation at multiple times $t$. | **PASS** |
| **Parameter Distinction: Official vs. Assumed** | Previous reports presented all parameters as strictly official without separating source-backed from assumed. | Official materials provide problem list, noise template, and processor JSON structure, but lack a standalone problem-specific numerical parameter sheet for S3. | Explicitly cataloged which parameters are source-backed from competition PDFs and which are benchmark model assumptions. | Audited all 5 PDF files in `official_materials/`. | **PASS** |

---

## 2. Official Specification vs. Benchmark Model Assumptions

### 2.1 Strictly Verified from Official Materials

- **Problem Selection:** `S3 — Noise in Trotter Simulation` (Category 13.3 Quantum Simulation, confirmed in Starter Guide p. 16, Participant Instructions p. 2).
- **Phase 1 Boundary:** Scope strictly limited to Processor A and Processor B (Participant Instructions p. 3).
- **Processor A Architecture:** 5-qubit linear topology, basis gates `['rz', 'sx', 'x', 'cx']`, ports `[0, 4]` (Starter Guide p. 15).
- **Processor B Architecture:** Contemporary heavy-hex compilation baseline with junction nodes (Guideline §4, §7; Starter Guide p. 13, p. 24).
- **Noise Model Parameters:** Single-qubit depolarizing $p_{1q}=0.001$ (`x`, `sx`), two-qubit depolarizing $p_{2q}=0.01$ (`cx`), readout confusion matrix $[[0.99, 0.01], [0.02, 0.98]]$ (Starter Guide p. 13).
- **Execution Model:** Synthetic noisy simulations with Aer simulator, separating ideal baseline from noisy baseline (Starter Guide p. 13, p. 19; Guideline p. 7).
- **Required Metrics:** Circuit depth, two-qubit gate count, SWAP count, physical qubits, and problem-specific fidelity/observable error (Starter Guide p. 14, p. 19).

### 2.2 Benchmark Model Assumptions (Explicitly Documented)

- **Hamiltonian Formulation:** 1D Transverse-Field Ising Model ($H = -J \sum Z_i Z_{i+1} - J_{\text{cross}} Z_0 Z_3 - h \sum X_i$) with $J=1.0, h=0.8, J_{\text{cross}}=0.5$.
  - *Rationale:* Standard model for Trotter simulation benchmarks. $J_{\text{cross}}=0.5$ provides a non-local periodic boundary condition that tests processor graph routing.
- **Spin Count & Initial State:** $N=4$ physical spins initialized in the Neel state $|\psi_0\rangle = |1010\rangle$.
- **Evolution Time & Sweeps:** Total simulation time $T=1.0$, swept across Trotter steps $n \in \{1, 2, 3, 4, 5, 6, 8, 10\}$.
- **Processor B 7-Qubit Subgraph:** Coupling map with edges `[[0,1], [1,2], [1,3], [3,5], [4,5], [5,6]]` (bidirectional pairs), representing a canonical heavy-hex degree-3 branching subgraph from contemporary IBM Quantum processors.

---

## 3. Physical Analysis & Symmetry Verification

### 3.1 Spatial Reflection Anti-Symmetry of Exact Magnetization

The 4-spin TFIM Hamiltonian is:
$$H = -J (Z_0 Z_1 + Z_1 Z_2 + Z_2 Z_3) - J_{\text{cross}} Z_0 Z_3 - h (X_0 + X_1 + X_2 + X_3)$$

Under the spatial reflection operator $\mathcal{P}: i \mapsto 3 - i$:
- $Z_0 Z_1 \leftrightarrow Z_3 Z_2 = Z_2 Z_3$
- $Z_1 Z_2 \leftrightarrow Z_2 Z_1 = Z_1 Z_2$
- $Z_0 Z_3 \leftrightarrow Z_3 Z_0 = Z_0 Z_3$
- $\sum_i X_i \leftrightarrow \sum_i X_i$

Thus, $[\mathcal{P}, H] = 0$.

For the staggered initial state $|\psi_0\rangle = |1010\rangle$:
$$\langle Z_0(0)\rangle = +1, \quad \langle Z_1(0)\rangle = -1, \quad \langle Z_2(0)\rangle = +1, \quad \langle Z_3(0)\rangle = -1$$
Note that $\langle Z_0(0)\rangle = -\langle Z_3(0)\rangle$ and $\langle Z_1(0)\rangle = -\langle Z_2(0)\rangle$.

Because Schrödinger evolution preserves this spatial parity anti-symmetry under the reflection-symmetric Hamiltonian, for all time $t$:
$$\langle Z_0(t)\rangle = -\langle Z_3(t)\rangle, \quad \langle Z_1(t)\rangle = -\langle Z_2(t)\rangle$$

Consequently, the exact total magnetization is identically zero:
$$\langle M_z(t)\rangle = \frac{1}{4} \sum_{i=0}^3 \langle Z_i(t)\rangle = 0 \quad (\forall t)$$

Numerical evaluations at $t=1.0$:
- $\langle Z_0\rangle = +0.421887$
- $\langle Z_1\rangle = -0.584543$
- $\langle Z_2\rangle = +0.584543$
- $\langle Z_3\rangle = -0.421887$
- Total sum $= 2.7755 \times 10^{-17} \approx 0.0000$.

### 3.2 Why Noisy Magnetization is Non-Zero

In the noisy simulation, asymmetric readout confusion:
$$P(\text{read } 0 \mid \text{state } 1) = 0.02, \quad P(\text{read } 1 \mid \text{state } 0) = 0.01$$
flips $|1\rangle \to |0\rangle$ at twice the rate of $|0\rangle \to |1\rangle$. This breaks the particle-hole balance and induces a positive bias in empirical magnetization ($\langle M_z\rangle_{\text{noisy}} \approx 0.005 \dots 0.05$).

---

## 4. Transpilation, Routing, and Metric Accounting

### 4.1 Why Explicit SWAPs are Zero

In Qiskit transpilation targeting basis gates `['rz', 'sx', 'x', 'cx']`:
1. The routing pass inserts SWAP operations to route non-adjacent interactions.
2. The basis unroller pass decomposes each SWAP into **3 native CX gates**.
3. Therefore, `swap` operations do not appear in the compiled circuit instructions (`explicit_swap_count = 0`).
4. The routing overhead is directly visible in the CX gate accumulation:
   $$\text{Routing CX Overhead} = \text{Compiled CX Gates} - \text{Logical CX Gates}$$
   $$\text{Equivalent Routing SWAPs} = \frac{\text{Routing CX Overhead}}{3}$$

### 4.2 Architectural Advantage of Processor B

At Trotter step $n=4$:
- **Logical Circuit:** 32 CX gates ($8$ CX per Trotter step).
- **Processor A (Linear Chain):** Compiles to **74 CX gates** (Routing CX Overhead: $42$, Equivalent SWAPs: $14$).
- **Processor B (Heavy-Hex Subgraph):** Compiles to **53 CX gates** (Routing CX Overhead: $21$, Equivalent SWAPs: $7$).
- **Net Saving:** Processor B saves **21 CX gates (-28.4%)** and **7 equivalent routing SWAPs (-50.0%)** because its degree-3 hub (node 1) connects directly to nodes 0, 2, and 3, reducing maximum spin distance across the graph from 3 hops down to 2 hops.

### 4.3 Why Total Circuit Depth is 111 on Both

- On Processor B, all cross-interactions route through the degree-3 hub, so hub node 1 participates in 53 CX gates, forming a critical path of 53 two-qubit layers.
- On Processor A, the 74 CX gates are distributed across the line, and the busiest qubit chain also happens to have 53 two-qubit layers on its critical path.
- Single-qubit $R_x$ rotations (unrolled to `rz-sx-rz`) serialize on the critical path to yield a total depth of 111 layers on both processors.
- However, because depolarizing noise accumulates across all gates regardless of parallelism, Processor B experiences significantly less total noise degradation (higher classical fidelity and lower TVD).

---

## 5. Summary Results Table

| Metric | Processor A (5Q Line) | Processor B (7Q Heavy-Hex) | Difference (B - A) | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Total Processor Qubit Capacity** | 5 | 7 | +2 | Total register size |
| **Active Physical Qubits Used** | 4 | 4 | 0 | 4 active spins on both |
| **Coupling Topology** | Linear Chain (5Q) | Heavy-Hex Subgraph (7Q) | Branching junctions vs. line | Node 1 is degree-3 hub on B |
| **Total Circuit Depth ($n=4$)** | 111 | 111 | 0 | Serialized critical path |
| **Two-Qubit Circuit Depth ($n=4$)** | 53 | 53 | 0 | 2Q critical path duration |
| **Two-Qubit CX Gates ($n=4$)** | 74 | 53 | **-21 (-28.4%)** | Major gate count reduction |
| **Routing CX Overhead ($n=4$)** | 42 | 21 | **-21 (-50.0%)** | Excess CX added by router |
| **Equivalent SWAPs Estimated from Excess CX ($n=4$)** | 14 | 7 | **-7 (-50.0%)** | Excess CX / 3 (verified by pass inspection) |
| **Explicit SWAP Instructions ($n=4$)** | 0 | 0 | 0 | Unrolled into basis CX gates |
| **Two-Qubit CX Gates ($n=10$)** | 194 | 137 | **-57 (-29.4%)** | Scaling reduction on B |
| **Routing CX Overhead ($n=10$)** | 114 | 57 | **-57 (-50.0%)** | Halved routing overhead |
| **Equivalent SWAPs Estimated from Excess CX ($n=10$)** | 38 | 19 | **-19 (-50.0%)** | Half as many routed paths |
| **Algorithmic State Fidelity ($n=4$)** | 0.9488 | 0.9488 | 0.0 | Pure mathematical Trotter |
| **Algorithmic State Fidelity ($n=10$)** | 0.9924 | 0.9924 | 0.0 | Discretization refinement |
| **Classical Dist Fidelity ($n=4$)** | 0.9577 | **0.9653** | **+0.0076** | Higher distribution overlap |
| **Classical Dist Fidelity ($n=10$)** | 0.8919 | **0.9103** | **+0.0184** | Slower noise degradation |
| **Total Variation Distance ($n=4$)** | 0.1992 | **0.1697** | **-0.0295** | Lower distribution error on B |
| **Total Variation Distance ($n=10$)** | 0.3403 | **0.3096** | **-0.0308** | Slower distribution divergence |
| **Optimal Trotter Step ($n^*$)** | $n=1$ | $n=1$ | 0 | Signal/noise trade-off peak |
| **Peak Classical Dist Fidelity** | 0.9996 | 0.9996 | 0.0 | Near-ideal overlap at $n=1$ |

---

## 6. Scientific Classification of Claims

To preserve scientific rigor, all benchmark statements are categorized into four distinct levels:

1. **Directly Measured Observations:**
   - Physical compiled operation counts: CX gates ($74$ on A, $53$ on B at $n=4$; $194$ on A, $137$ on B at $n=10$).
   - Critical path depths: Total depth ($111$ on both at $n=4$) and two-qubit depth ($53$ on both at $n=4$).
   - Explicit SWAP instruction count: $0$ on both processors in the final basis-unrolled circuit.
   - Empirical bitstring counts across 4096 shots under Aer simulation with seeds fixed at 42.

2. **Calculations Derived from Measured Quantities:**
   - Routing CX Overhead: $\text{Compiled CX} - \text{Logical CX}$ ($42$ on A vs. $21$ on B at $n=4$).
   - Equivalent SWAPs Estimated from Excess CX: $\text{Overhead} / 3$ ($14$ on A vs. $7$ on B at $n=4$).
   - Pass-Level Verification: Inspection of Qiskit's intermediate `routing` stage output (`pm.routing.run`) confirms that the `SabreSwap` pass explicitly inserted exactly $14$ `swap` operations on Processor A and $7$ `swap` operations on Processor B prior to 3-CX unrolling, exactly confirming the formula for this circuit.
   - Total Variation Distance ($D_{\text{TVD}} = \frac{1}{2}\sum_x |P(x) - Q(x)|$) and Bhattacharyya overlap ($F_c = \sum_x \sqrt{P(x)Q(x)}$).

3. **Interpretations About Processor Topology:**
   - Processor B's heavy-hex degree-3 branching hub (node 1) connects directly to nodes 0, 2, and 3, reducing graph diameter across active spins from 3 hops down to 2 hops.
   - This topological property explains why the routing pass required half as many SWAP operations ($7$ vs. $14$), reducing noisy two-qubit entangling gates by $28.4\%$ and protecting output distribution fidelity.

4. **Model Assumptions (Not verbatim in official competition PDF):**
   - Hamiltonian: Transverse-Field Ising Model ($J=1.0, h=0.8, J_{\text{cross}}=0.5$).
   - Boundary condition: Periodic ring closure ($J_{\text{cross}}=0.5$) adopted to create a non-trivial routing problem.
   - Physical spins & state: $N=4$ spins initialized in $|\psi_0\rangle = |1010\rangle$.
   - Simulation time & sweep: $T=1.0$, $n \in \{1, 2, 3, 4, 5, 6, 8, 10\}$.
   - Processor B graph: 7-qubit heavy-hex subgraph with nodes $0..6$.

---

## 6. Automated Test Suite Validation

Command executed:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"

```

```text
..........
----------------------------------------------------------------------
Ran 10 tests in 0.298s

OK

```

All 10 tests passed:
1. `test_processor_configurations`: Validates JSON schema, basis gates, and qubit counts.
2. `test_coupling_maps_and_noise_models`: Verifies CouplingMap size and noise instruction generation.
3. `test_problem_s3_hamiltonian_and_hermiticity`: Validates Hermiticity and dimension ($16 \times 16$).
4. `test_independent_numerical_trotter_unitary`: Confirms circuit unitary matches $\exp(-iH\Delta t)$ to order $\mathcal{O}(\Delta t^2)$.
5. `test_algorithmic_state_fidelity_convergence`: Confirms monotonic convergence of $F_{\text{state}} \to 1.0$.
6. `test_transpilation_and_active_qubits_extraction`: Confirms separation of total capacity from active spins.
7. `test_noise_model_exact_channels`: Verifies depolarizing and readout channels, confirming zero thermal relaxation.
8. `test_exact_magnetization_reflection_symmetry`: Confirms pairwise anti-symmetry and zero total magnetization.
9. `test_routing_cx_overhead_and_unrolled_swaps`: Confirms explicit SWAP = 0 and Processor B CX reduction.
10. `test_statistical_metrics_and_zero_division`: Confirms TVD, fidelity, and zero-shot edge cases.

---

## 7. Submission Verification Checklist

- [x] S3 problem statement exclusively implemented.
- [x] Processor A (5Q line) and Processor B (7Q heavy-hex) analyzed.
- [x] Ideal vs. noisy baseline data cleanly separated.
- [x] Exact Trotter state fidelity distinguished from classical Bhattacharyya overlap.
- [x] Active physical qubits ($4$) separated from total register capacity ($5$ and $7$).
- [x] Zero explicit SWAPs explained via basis gate unrolling; routing CX overhead tracked.
- [x] Exact zero magnetization explained via spatial reflection symmetry; noisy bias explained via readout asymmetry.
- [x] Thermal relaxation references removed; exact noise channels documented.
- [x] Automated test suite passing with 10/10 tests.
- [x] Clean machine-readable results exported to `results/raw/` and `results/tables/`.
- [x] All 5 figures generated at 300 DPI in `results/figures/`.
- [x] Repository clean, committed, and synchronized with remote.
