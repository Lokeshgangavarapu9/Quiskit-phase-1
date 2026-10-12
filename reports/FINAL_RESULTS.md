# Scientific Benchmark Report: Problem S3 (Noise in Trotter Simulation)

## Controlled Architecture Benchmark: Processor A (5-Qubit Line) vs. Processor B (7-Qubit Heavy-Hex Subgraph)

**Project Location:** `C:\Users\LOKESH\quiskit phase 1\`  
**Target Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Track:** Quantum Simulation  
**Problem Statement:** `S3 — Noise in Trotter Simulation`  
**Date:** October 11, 2026  

---

## 1. Executive Summary

This study evaluates the trade-off between **algorithmic discretization error** and **physical device noise** in first-order Suzuki-Trotter quantum simulation across two distinct QPU architectures:
1. **Processor A:** A 5-qubit linear chain baseline ($\text{Q}_0 - \text{Q}_1 - \text{Q}_2 - \text{Q}_3 - \text{Q}_4$).
2. **Processor B:** A 7-qubit heavy-hex subgraph with degree-3 branching hubs representing contemporary IBM Quantum processors.

The physical model is a 4-spin Transverse-Field Ising Model (TFIM) under periodic boundary conditions ($J = 1.0, h = 0.8, J_{\text{cross}} = 0.5$, total time $T = 1.0$) initialized in the staggered Neel state $|\psi_0\rangle = |1010\rangle$.

### Key Findings

1. **Routing Advantage of Heavy-Hex Hubs:**
   Processor B's central degree-3 hub reduces graph distance between opposite spins from 3 hops down to 2 hops. When transpiled into native basis gates (`rz`, `sx`, `x`, `cx`), Processor B achieves a **$28.4\%$ reduction in two-qubit CX gates at $n=4$** ($53$ CX gates on B vs. $74$ on A) and a **$29.4\%$ reduction at $n=10$** ($137$ on B vs. $194$ on A).
2. **Decomposed SWAP Accounting:**
   The transpiler unrolls all routing SWAPs into basis CX gates ($1\text{ SWAP} \equiv 3\text{ CX}$), leaving explicit SWAP instructions at zero on both processors. Processor A incurs $42$ routing CX gates ($14$ equivalent SWAPs) at $n=4$, whereas Processor B incurs only $21$ routing CX gates ($7$ equivalent SWAPs)—a **$50\%$ reduction in routing overhead**.
3. **Critical Path Depth Equality:**
   Despite Processor B saving 21 CX gates, the total critical path depth is identical ($111$ on both at $n=4$) because on Processor B, cross-interactions route through the central hub, putting 53 two-qubit gates on the critical path, matching the busiest qubit on Processor A. However, because depolarizing noise accumulates across all gates in the circuit, Processor B experiences significantly higher fidelity ($F_c = 0.9653$ vs. $0.9577$) and lower Total Variation Distance ($\text{TVD} = 0.1697$ vs. $0.1992$).
4. **Physical Symmetry of Exact Magnetization:**
   The exact total magnetization $\langle M_z(t)\rangle$ is identically zero for all $t$ due to spatial reflection anti-symmetry $\langle Z_0(t)\rangle = -\langle Z_3(t)\rangle$ and $\langle Z_1(t)\rangle = -\langle Z_2(t)\rangle$. Non-zero measured magnetization in noisy simulations ($\sim 0.005 \dots 0.05$) arises from asymmetric readout confusion ($P(0\mid 1) = 0.02 \ne P(1\mid 0) = 0.01$), which introduces a net positive measurement bias.

---

## 2. Parameter Grounding: Official vs. Assumed

| Parameter / Item | Value | Categorization | Source & Justification |
| :--- | :---: | :---: | :--- |
| **Problem Track** | S3 (Noise in Trotter Simulation) | **Officially Verified** | Starter Guide p. 16, Participant Instructions p. 2 |
| **Phase 1 Scope** | Processors A & B only | **Officially Verified** | Participant Instructions p. 3 |
| **Processor A Topology** | 5-qubit linear chain | **Officially Verified** | Starter Guide p. 15 |
| **Processor A Basis Gates** | `['rz', 'sx', 'x', 'cx']` | **Officially Verified** | Starter Guide p. 15 |
| **Noise Model** | Depolarizing + Readout | **Officially Verified** | Starter Guide p. 13 ($p_1=0.001, p_2=0.01$, readout matrix $[[0.99, 0.01], [0.02, 0.98]]$) |
| **Thermal Relaxation** | Omitted | **Officially Verified** | Omitted because official materials do not specify T1/T2 parameters |
| **Hamiltonian** | TFIM with periodic cross-coupling | **Benchmark Assumption** | Standard benchmark choice for S3 routing study |
| **Coupling Constants** | $J=1.0, h=0.8, J_{\text{cross}}=0.5$ | **Benchmark Assumption** | Chosen to balance interaction vs. transverse field and enforce routing |
| **Spin Count & State** | $N=4$ spins, $\vert \psi_0\rangle = \vert 1010\rangle$ | **Benchmark Assumption** | Antiferromagnetic Neel state |
| **Simulation Time** | $T = 1.0$ | **Benchmark Assumption** | Intermediate time scale capturing Trotter convergence and noise crossover |
| **Processor B Graph** | 7-qubit heavy-hex subgraph | **Benchmark Assumption** | Canonical degree-3 heavy-hex motif matching contemporary IBM QPUs |

---

## 3. Physical Model & Trotter Formulation

The 1D Transverse-Field Ising Model with boundary cross-coupling is defined by:
$$H = - J \sum_{i=0}^{N-2} Z_i Z_{i+1} - J_{\text{cross}} Z_0 Z_{N-1} - h \sum_{i=0}^{N-1} X_i$$

### 3.1 First-Order Trotter Decomposition

Unitary evolution $U(T) = \exp(-iHT)$ is approximated into $n$ discrete steps ($\Delta t = T/n$):
$$U(T) \approx \left[ U_{ZZ}(\Delta t) U_{X}(\Delta t) \right]^n$$
Where:
- Interaction propagator: $U_{ZZ}(\Delta t) = \prod_{i=0}^{N-2} \exp(i J \Delta t Z_i Z_{i+1}) \cdot \exp(i J_{\text{cross}} \Delta t Z_0 Z_{N-1})$
  - Gate decomposition: $\text{CX}(j, k) \cdot R_Z(-2 J \Delta t, k) \cdot \text{CX}(j, k)$
- Transverse field propagator: $U_{X}(\Delta t) = \prod_{i=0}^{N-1} \exp(i h \Delta t X_i)$
  - Gate decomposition: $R_X(-2 h \Delta t, i)$

### 3.2 Gate Matrix Verification

In unit tests (`tests/test_benchmark.py::test_independent_numerical_trotter_unitary`), the circuit operator matrix was compared against SciPy matrix exponentiation:
$$\|U_{\text{circuit}}(\Delta t) - \exp(-iH\Delta t)\| \le \mathcal{O}(\Delta t^2)$$
At $\Delta t = 0.05$, the operator norm error is $0.0203$, confirming exact generator signs and mathematical correctness.

---

## 4. Comprehensive Experimental Results

### 4.1 Parameter Sweep Comparison Table ($n \in \{1, 2, 3, 4, 5, 6, 8, 10\}$)

| Trotter Steps ($n$) | Algorithmic State Fidelity ($F_{\text{state}}$) | Logical CX | Proc A Total Depth | Proc B Total Depth | Proc A 2Q Depth | Proc B 2Q Depth | Proc A CX | Proc B CX | Proc A Routing CX | Proc B Routing CX | Proc A Classical Fidelity ($F_c$) | Proc B Classical Fidelity ($F_c$) | Proc A TVD | Proc B TVD |
| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **1** | 0.1171 | 8 | 27 | 27 | 11 | 11 | 14 | 11 | 6 | 3 | **0.9996** | **0.9996** | 0.0217 | 0.0237 |
| **2** | 0.7651 | 16 | 56 | 55 | 26 | 25 | 32 | 25 | 16 | 9 | 0.9803 | 0.9838 | 0.1169 | 0.1001 |
| **3** | 0.9047 | 24 | 83 | 83 | 39 | 39 | 54 | 39 | 30 | 15 | 0.9696 | 0.9749 | 0.1550 | 0.1389 |
| **4** | 0.9488 | 32 | 111 | 111 | 53 | 53 | 74 | **53** | 42 | **21** | 0.9577 | **0.9653** | 0.1992 | **0.1697** |
| **5** | 0.9681 | 40 | 139 | 139 | 67 | 67 | 94 | 67 | 54 | 27 | 0.9451 | 0.9565 | 0.2339 | 0.2002 |
| **6** | 0.9783 | 48 | 167 | 167 | 81 | 81 | 114 | 81 | 66 | 33 | 0.9332 | 0.9475 | 0.2654 | 0.2258 |
| **8** | 0.9880 | 64 | 223 | 223 | 109 | 109 | 154 | 109 | 90 | 45 | 0.9087 | 0.9263 | 0.3103 | 0.2742 |
| **10** | 0.9924 | 80 | 279 | 279 | 137 | 137 | 194 | **137** | 114 | **57** | 0.8919 | **0.9103** | 0.3403 | **0.3096** |

### 4.2 Summary Architecture Metrics

| Metric | Processor A | Processor B | Delta (B - A) | Architectural Cause |
| :--- | :---: | :---: | :---: | :--- |
| **Total Register Qubits** | 5 | 7 | +2 | Processor capacity |
| **Active Computational Spins** | 4 | 4 | 0 | Subgraph allocation |
| **Coupling Map Topology** | Linear Chain | Heavy-Hex Subgraph | Hub vs. line | Degree-3 branching node 1 on B |
| **Two-Qubit CX Gates ($n=4$)** | 74 | 53 | **-21 (-28.4%)** | Reduced graph diameter (2 vs. 3 hops) |
| **Routing CX Overhead ($n=4$)** | 42 | 21 | **-21 (-50.0%)** | Fewer routing transformations on B |
| **Equivalent SWAPs Estimated from Excess CX ($n=4$)** | 14 | 7 | **-7 (-50.0%)** | Excess CX / 3 (verified by pass inspection) |
| **Explicit SWAP Instructions ($n=4$)** | 0 | 0 | 0 | Unrolled to native basis CX gates |
| **Total Circuit Depth ($n=4$)** | 111 | 111 | 0 | Hub critical path matches busiest line qubit |
| **Two-Qubit Depth ($n=4$)** | 53 | 53 | 0 | Two-qubit critical path duration |
| **Two-Qubit CX Gates ($n=10$)** | 194 | 137 | **-57 (-29.4%)** | Sustained scaling reduction on B |
| **Routing CX Overhead ($n=10$)** | 114 | 57 | **-57 (-50.0%)** | 50% fewer routed CX operations |
| **Equivalent SWAPs Estimated from Excess CX ($n=10$)** | 38 | 19 | **-19 (-50.0%)** | Half as many routed paths |
| **Classical Dist Overlap ($n=4$)** | 0.9577 | **0.9653** | **+0.0076** | Higher output fidelity on B |
| **Classical Dist Fidelity ($n=10$)** | 0.8919 | **0.9103** | **+0.0184** | Slower noise degradation on B |
| **Total Variation Distance ($n=4$)** | 0.1992 | **0.1697** | **-0.0295** | Lower probability error on B |
| **Total Variation Distance ($n=10$)** | 0.3403 | **0.3096** | **-0.0308** | Slower distribution divergence on B |

### 4.3 Scientific Claim Classification

1. **Measured Observations:**
   - Transpiled gate operations: CX gates ($74$ on A vs. $53$ on B at $n=4$; $194$ vs. $137$ at $n=10$).
   - Circuit depths: Total depth ($111$ on both at $n=4$) and two-qubit depth ($53$ on both at $n=4$).
   - Explicit SWAP instructions: $0$ in the final unrolled basis circuit.
   - Empirical counts from 4096 shots under Aer simulation with seed 42.

2. **Calculations Derived from Measured Quantities:**
   - Routing CX Overhead: $\text{Compiled CX} - \text{Logical CX}$ ($42$ on A vs. $21$ on B at $n=4$).
   - Equivalent SWAPs Estimated from Excess CX: $\text{Overhead} / 3$ ($14$ on A vs. $7$ on B at $n=4$).
   - Pass-Level Verification: Inspection of Qiskit's intermediate `routing` stage output (`pm.routing.run`) independently confirms that the `SabreSwap` pass explicitly inserted exactly $14$ `swap` operations on Processor A and $7$ `swap` operations on Processor B prior to 3-CX unrolling.
   - Distribution metrics: TVD and classical Bhattacharyya overlap.

3. **Interpretations About Processor Topology:**
   - Processor B's heavy-hex degree-3 hub connects directly to nodes 0, 2, and 3, reducing graph diameter across active spins from 3 hops to 2 hops.
   - This topological property explains why the router required half as many SWAP operations ($7$ vs. $14$), reducing noisy two-qubit entangling gates by $28.4\%$ and protecting output distribution fidelity.

4. **Model Assumptions (Not verbatim in official competition PDF):**
   - Transverse-Field Ising Model parameters: $J=1.0, h=0.8, J_{\text{cross}}=0.5$.
   - Boundary condition: Periodic ring closure ($J_{\text{cross}}=0.5$) adopted to create a non-trivial routing problem.
   - Physical spins & state: $N=4$ spins initialized in $|\psi_0\rangle = |1010\rangle$.
   - Simulation time & sweep: $T=1.0$, $n \in \{1, 2, 3, 4, 5, 6, 8, 10\}$.
   - Processor B graph: 7-qubit heavy-hex subgraph with nodes $0..6$.

---

## 5. Scientific Interpretation

1. **Trade-Off Optimization ($n^* = 1$ vs. $n = 4$):**
   - Pure algorithmic discretization fidelity $F_{\text{state}}$ improves from $0.1171$ at $n=1$ to $0.9488$ at $n=4$ and $0.9924$ at $n=10$.
   - However, empirical noisy measurement fidelity peaks at $n=1$ ($F_c = 0.9996$) and monotonically decays under gate noise as step count increases.
   - For practical simulation requiring acceptable discretization accuracy ($F_{\text{state}} > 0.94$), $n=4$ provides the optimal operational regime.
2. **Impact of Processor Architecture:**
   - Although critical path duration is equalized by serialized hub routing, Processor B eliminates 21 physical CX operations at $n=4$ and 57 at $n=10$.
   - Because each two-qubit CX gate introduces a $1.0 \times 10^{-2}$ depolarizing error across the entire two-qubit subspace, Processor B suffers significantly less total mixed-state entropy growth.
   - Consequently, Processor B maintains higher classical distribution overlap and lower Total Variation Distance across all step counts $n \ge 2$.

---

## 6. How to Reproduce

Commands to reproduce all results from a clean clone:

```powershell
cd "C:\Users\LOKESH\quiskit phase 1"
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python main.py

```

Generated outputs:
- Raw data: [`results/raw/raw_experiment_data.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/raw/raw_experiment_data.json)
- Comparison tables: [`results/tables/AB_comparison.csv`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/tables/AB_comparison.csv), [`results/tables/final_comparison.csv`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/tables/final_comparison.csv)
- Figures: [`results/figures/AB_performance.png`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/AB_performance.png), [`results/figures/architecture_tradeoffs.png`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/architecture_tradeoffs.png)
