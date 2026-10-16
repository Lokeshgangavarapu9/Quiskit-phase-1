# Student Walkthrough & Technical Study Guide

## Qiskit Fall Fest 2026 — Phase 1: Problem S3 (Noise in Trotter Simulation)

**Project Location:** `C:\Users\LOKESH\quiskit phase 1`  
**GitHub Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Track:** Quantum Simulation  
**Problem Statement:** `S3 — Noise in Trotter Simulation`
**Target Architectures:** Processor A (5Q Line Baseline) vs. Processor B (9Q Heavy-Hex Reference Baseline)
**Audience:** Undergraduate physics / computer science students seeking to understand, explain, and defend every line of code and scientific claim in this project.


---

## Table of Contents

1. [The S3 Problem & Central Objective](#1-the-s3-problem--central-objective)
2. [The Physical Hamiltonian & Term Interpretations](#2-the-physical-hamiltonian--term-interpretations)
3. [Initial State Preparation & Physical Symmetries](#3-initial-state-preparation--physical-symmetries)
4. [First-Order Suzuki-Trotter Decomposition](#4-first-order-suzuki-trotter-decomposition)
5. [Quantum Circuit Construction](#5-quantum-circuit-construction)
6. [Processor A vs. Processor B Topologies](#6-processor-a-vs-processor-b-topologies)
7. [Transpilation, Routing, & Layout Mapping](#7-transpilation-routing--layout-mapping)
8. [Hardware Noise Modeling (Depolarizing & Readout)](#8-hardware-noise-modeling-depolarizing--readout)
9. [Ideal Reference vs. Noisy Simulation](#9-ideal-reference-vs-noisy-simulation)
10. [Circuit Depth vs. Two-Qubit Gate Counting](#10-circuit-depth-vs-two-qubit-gate-counting)
11. [Explicit SWAP Gates vs. Equivalent SWAP Estimates](#11-explicit-swap-gates-vs-equivalent-swap-estimates)
12. [Metrics: State Fidelity, Classical Overlap, TVD, & Single-Site Observable](#12-metrics-state-fidelity-classical-overlap-tvd--single-site-observable)
13. [What the Results Demonstrate (and What They Do Not)](#13-what-the-results-demonstrate-and-what-they-do-not)
14. [Processor D Architectural Co-Design Proposal](#14-processor-d-architectural-co-design-proposal)
15. [How to Run and Reproduce Every Result](#15-how-to-run-and-reproduce-every-result)
16. [Questions I Should Be Able to Answer (Oral Defense Guide)](#16-questions-i-should-be-able-to-answer-oral-defense-guide)

---


## 1. The S3 Problem & Central Objective

### 1.1 The Fundamental Challenge in Digital Quantum Simulation

When simulating physical quantum systems on classical computers, the dimension of the Hilbert space grows exponentially as $2^N$ for $N$ spin-1/2 particles. Simulating even 50 spins exceeds the memory capacity of the world's largest supercomputers. Quantum computers, by contrast, map spin-1/2 particles directly to physical qubits.

However, quantum computers cannot execute continuous time evolution $\hat{U}(t) = e^{-i \hat{H} t}$ directly as an analog Hamiltonian. Instead, digital quantum processors must approximate continuous unitary evolution using discrete sequences of 1-qubit and 2-qubit quantum logic gates. This technique is called **Trotter product simulation** (or Trotterization).

### 1.2 The Trotter Dilemma

Trotterization introduces an intrinsic tension:

1. **Algorithmic Discretization Error:** To minimize mathematical approximation error, you must take very small time steps $\Delta t = T / n$ (large step count $n$).
2. **Physical Hardware Noise:** Each Trotter step requires a fixed layer of quantum gates. More steps mean deeper circuits and dozens of noisy entangling two-qubit (CX) gates. On real hardware, physical gate errors compound exponentially.

```text
       Error
         ▲
         │ \
         │  \   Algorithmic Error ~ O(1/n)
         │   \
         │    \         Total Error
         │     \        .───────.
         │      \     .           .   Hardware Noise ~ (1 - p)^N_gates
         │       \  .               .
         │        .                   .
         │       / \                    .
         │      /   \                     ▲
         │     /     \                    │
         └────┴───────┴───────────────────┴────► Number of Trotter Steps (n)
                     n* (Optimal Step)
```

### 1.3 The Phase 1 Hackathon Question

For Qiskit Fall Fest 2026 Phase 1, the competition poses the central question:
> *How does processor architecture geometry and routing influence the trade-off between algorithmic Trotter discretization error and physical hardware noise?*

Our task is to benchmark the exact same physical problem under identical conditions on two different quantum processors:

- **Processor A:** A 5-qubit linear chain baseline.
- **Processor B:** A 9-qubit heavy-hex-inspired reference compilation baseline.

---

## 2. The Physical Hamiltonian & Term Interpretations

In [`src/problem.py`](../src/problem.py), the class `TrotterSimulationModel` implements a 4-spin 1D **Transverse-Field Ising Model (TFIM)**:

$$\hat{H} = - J \sum_{i=0}^{N-2} \hat{Z}_i \hat{Z}_{i+1} - J_{\text{cross}} \hat{Z}_0 \hat{Z}_{N-1} - h \sum_{i=0}^{N-1} \hat{X}_i$$

Where:

- $N = 4$ physical spins.
- $\hat{Z}_i$ and $\hat{X}_i$ are standard single-qubit Pauli matrices.
- $J = 1.0$: Ferromagnetic nearest-neighbor exchange coupling.
- $h = 0.8$: Transverse magnetic field driving quantum oscillations.
- $J_{\text{cross}}$: Boundary condition coupling constant:
  - **Primary Baseline ($J_{\text{cross}} = 0.0$):** Open-chain 1D model with nearest-neighbor interactions only ($Z_0 Z_1, Z_1 Z_2, Z_2 Z_3$).
  - **Architectural Extension ($J_{\text{cross}} = 0.5$):** Periodic ring boundary condition coupling spin 0 to spin 3 ($Z_0 Z_3$) to test routing stress.

---

## 3. Initial State Preparation & Physical Symmetries

### 3.1 Initial State

The initial state is initialized in the staggered **Néel state** (antiferromagnetic domain wall):
$$|\psi(0)\rangle = |1010\rangle$$
In Qiskit's little-endian bit-ordering (where $q_0$ is the rightmost bit of string `'1010'`), Pauli-$X$ gates are applied to qubits 1 and 3.

### 3.2 Exact Reflection Anti-Symmetry

The system possesses a physical spatial reflection symmetry $\mathcal{P}: i \mapsto 3 - i$.

Under spatial reflection:
$$\mathcal{P} \hat{Z}_0 \mathcal{P}^\dagger = \hat{Z}_3, \quad \mathcal{P} \hat{Z}_1 \mathcal{P}^\dagger = \hat{Z}_2, \quad \mathcal{P} \hat{H} \mathcal{P}^\dagger = \hat{H}$$
Acting on the initial state $|1010\rangle$:
$$\mathcal{P} |1010\rangle = |0101\rangle = \bigotimes_{i=0}^3 \hat{X}_i |1010\rangle$$
Because the Hamiltonian commutes with the combined parity-spin-flip symmetry, the expectation values of opposite sites are anti-symmetric:
$$\langle \hat{Z}_0(t) \rangle = - \langle \hat{Z}_3(t) \rangle, \quad \langle \hat{Z}_1(t) \rangle = - \langle \hat{Z}_2(t) \rangle \quad \forall t$$

Consequently, the **exact total magnetization** is identically zero for all $t$:
$$\langle \hat{M}_z(t) \rangle = \frac{1}{4} \sum_{i=0}^3 \langle \hat{Z}_i(t) \rangle \equiv 0.000000 \quad \forall t$$
This exact mathematical property is verified independently in `tests/test_benchmark.py`. Because $\langle \hat{M}_z(t) \rangle$ is degenerate for all $t$, tracking it alone would mask Trotter convergence. Therefore, single-site magnetization $\langle \hat{Z}_0(t) \rangle$ serves as our primary observable!

---

## 4. First-Order Suzuki-Trotter Decomposition

Continuous unitary evolution is:
$$\hat{U}(t) = e^{-i \hat{H} t} = \exp\left( -i \left[ \hat{H}_{ZZ} + \hat{H}_X \right] t \right)$$

Because $[\hat{H}_{ZZ}, \hat{H}_X] \ne 0$, the first-order Trotter-Suzuki product formula discretizes time into $n$ steps of $\Delta t = t / n$:
$$\hat{U}(t) \approx \left[ e^{-i \hat{H}_{ZZ} \Delta t} e^{-i \hat{H}_X \Delta t} \right]^n$$

The leading commutator error per step scales as $\mathcal{O}(\Delta t^2) = \mathcal{O}(t^2 / n^2)$. Accumulated across $n$ steps, the total algorithmic discretization error shrinks as $\mathcal{O}(t^2 / n)$. As $n \to \infty$, the ideal Trotter state converges monotonically to the continuum target.

---

## 5. Quantum Circuit Construction

- **Two-Qubit Interaction Gate ($e^{i J \Delta t Z_j Z_k}$):** Synthesized via:
  $$CX(j, k) \to R_z(-2 J \Delta t, k) \to CX(j, k)$$
- **Single-Qubit Field Gate ($e^{i h \Delta t X_i}$):** Synthesized via $R_x(-2 h \Delta t, i)$.

For the open-chain baseline, each Trotter step contains 3 $ZZ$ blocks ($3 \times 2 = 6$ CX gates) and 4 $R_x$ gates. For the periodic ring extension, each Trotter step contains 4 $ZZ$ blocks ($4 \times 2 = 8$ CX gates) and 4 $R_x$ gates.

---

## 6. Processor A vs. Processor B Topologies

```text
Processor A: Linear Chain (5 Qubits)
  (0) --- (1) --- (2) --- (3) --- (4)
 [Port]                          [Port]

Processor B: Heavy-Hex Reference Lattice (9 Qubits, 12 Undirected Edges)
         (1) ----------- (2)
        /   \           /   \
       /     \         /     \
     (0)     (6) --- (5)     (3)
    [Port]  /   \     |       |
           /     \    |       |
         (8) --- (7) (4)      |
        [Port]
```

### Key Differences

1. **Connectivity & Node Degree:** Processor A nodes have maximum degree 2 (line). Processor B has junction nodes (degree 3 and 4), providing alternative routing paths.
2. **Cycle Embedding:** Processor B contains the heavy-hex hexagonal cycle `(1, 2, 5, 6)`. When simulating the periodic ring extension, the 4 logical spins map directly to this cycle:
   $$q_0 \mapsto 1, \quad q_1 \mapsto 2, \quad q_2 \mapsto 5, \quad q_3 \mapsto 6$$
   Because all 4 edges `(1,2), (2,5), (5,6), (6,1)` physically exist, the periodic boundary condition requires **zero routing SWAPs**, cutting two-qubit CX gates by 56.8% compared to Processor A.

---

## 7. Transpilation, Routing, & Layout Mapping

Circuits are compiled targeting each processor's coupling map and basis gates `['rz', 'sx', 'x', 'cx']` using Qiskit's `generate_preset_pass_manager(optimization_level=1, seed_transpiler=42)`:

- **Layout:** Maps 4 logical qubits onto 4 active physical qubits out of the chip's total capacity (5 on A, 9 on B).
- **Routing:** If interacting qubits are non-adjacent, `SabreSwap` inserts SWAPs along shortest paths.
- **Decomposition:** Unrolls SWAP gates into 3 native CX gates and translates single-qubit rotations into `rz` and `sx`.

---

## 8. Hardware Noise Modeling (Depolarizing & Readout)

Noisy simulations use Qiskit Aer configured with verified Phase 1 noise parameters:

- **Single-Qubit Depolarizing Error:** $p_1 = 0.001$ on physical single-qubit pulses ($X, \sqrt{X}$).
- **Two-Qubit Depolarizing Error:** $p_2 = 0.005$ on physical entangling gates ($CX$).
- **Symmetric Readout Error:** Symmetric $1\%$ bit-flip confusion matrix:
  $$\mathbf{M} = \begin{pmatrix} 0.99 & 0.01 \\ 0.01 & 0.99 \end{pmatrix}$$
- **Execution Settings:** 4096 measurement shots per circuit, deterministic random seed `seed=42`.

---

## 9. Ideal Reference vs. Noisy Simulation

In `main.py` and `main.ipynb`, three distinct simulation runs are executed for each step count $n$:

1. **Ideal Simulation (`sim_ideal`):** Runs the logical circuit with zero noise, isolating algorithmic Trotter discretization error.
2. **Processor A Noisy Simulation (`sim_a`):** Compiles onto Processor A's 5Q line and simulates under hardware noise.
3. **Processor B Noisy Simulation (`sim_b`):** Compiles onto Processor B's 9Q heavy-hex lattice and simulates under hardware noise.

---

## 10. Circuit Depth vs. Two-Qubit Gate Counting

- **Total Depth:** The longest critical path of gates from circuit input to output.
- **Two-Qubit Depth:** The critical path considering only entangling gates.
- **Two-Qubit Gate Count:** The total count of CX gates across the entire circuit.

On the open-chain baseline at $n=4$:

- Both processors yield total depth $= 49$, two-qubit depth $= 18$, and CX count $= 24$.

On the periodic ring extension at $n=4$:

- Processor A requires 74 CX gates (42 routing CX, 14 SWAPs).
- Processor B requires 32 CX gates (0 routing CX, 0 SWAPs).

---

## 11. Explicit SWAP Gates vs. Equivalent SWAP Estimates

A common question is:
> *Why does `count_ops()` show `swap = 0` on both processors, even when routing operations were inserted?*

### The Answer: Basis Gate Unrolling

In superconducting basis sets `['rz', 'sx', 'x', 'cx']`, SWAP is not a native physical instruction. During compilation, each inserted SWAP is immediately unrolled into **3 native CX gates**:
$$SWAP(a, b) \equiv CX(a, b) \cdot CX(b, a) \cdot CX(a, b)$$
Therefore, the compiler leaves zero explicit `swap` opcodes in the final circuit. To measure routing cost accurately, we calculate:
$$\text{Routing CX Overhead } \Delta CX = \text{Compiled CX} - \text{Logical CX}$$
$$\text{Estimated Equivalent SWAPs} = \lfloor \Delta CX / 3 \rfloor$$

---

## 12. Metrics: State Fidelity, Classical Overlap, TVD, & Single-Site Observable

1. **Pure Quantum State Fidelity ($F_{\text{state}}$):**
   $$F_{\text{state}} = |\langle \psi_{\text{exact}} \mid \psi_{\text{trotter\_ideal}} \rangle|^2$$
   Measures pure algorithmic mathematical accuracy in Hilbert space ($0.6272$ at $n=1$, $0.9648$ at $n=4$, $0.9949$ at $n=10$).
2. **Classical Distribution Overlap ($F_c$):**
   Bhattacharyya coefficient from measured counts: $F_c(P, Q) = \sum_x \sqrt{P(x) Q(x)}$. Captures degradation under physical noise ($0.9999$ at $n=1$, $0.9949$ at $n=4$, $0.9842$ at $n=10$).
3. **Total Variation Distance (TVD):**
   $$\text{TVD}(P, Q) = \frac{1}{2} \sum_x |P(x) - Q(x)|$$
   Measures statistical distance between noisy counts and ideal reference ($0.0098$ at $n=1 \to 0.1248$ at $n=10$).
4. **Primary Observable ($\langle Z_0(t) \rangle$):**
   Single-site expectation value with shot standard error $\text{SE} = \sigma / \sqrt{N_{\text{shots}}}$. At $n=4$, measured $\langle Z_0 \rangle = 0.2310 \pm 0.015$, closely matching exact target $0.257957$ (error $0.0270$).

---

## 13. What the Results Demonstrate (and What They Do Not)

### What the Results Demonstrate

1. **Geometric Routing Advantage:** When non-local interactions occur (e.g. periodic boundary conditions), Processor B's heavy-hex cycle eliminates routing SWAPs entirely, reducing two-qubit operations by 56.8% at $n=4$ and 58.8% at $n=10$.
2. **Trotter Trade-off Threshold ($n^*$):** Beyond $n^* = 4$, two-qubit depolarizing noise outpaces Trotter refinement, causing classical distribution fidelity to decay.
3. **Controlled Experimental Parity:** Because both processors share identical gate error rates ($p_1=0.001, p_2=0.005$) and symmetric readout, all observed differences in the periodic extension stem purely from coupling topology.

### What the Results Do NOT Demonstrate

1. **Processor B is NOT Universally Superior on Line Graphs:** On the open-chain baseline, both processors embed the 1D line with 0 SWAPs, achieving identical performance.
2. **Observable Convergence is Not Strictly Monotonic:** While state fidelity converges monotonically, individual observable errors can fluctuate due to finite sampling noise ($\sim 0.015$) and local phase interferences.

---

## 14. Processor D Architectural Co-Design Proposal

### 14.1 Why Processor D is Proposed

The hackathon WhatsApp instructions state:
> *"Illustrate the problem faced when running the problem statement on the provided processors and propose a solution involving Processor D."*

Running Problem S3 demonstrated two distinct architectural bottlenecks:

1. **Processor A (1D Line Baseline) Bottleneck:** Linear topology induces heavy SWAP routing for non-local interactions. On the 4-spin periodic ring, boundary coupling requires **14 SWAPs (42 extra CX gates)** at $n=4$, scaling as $\mathcal{O}(N^2)$ for larger spin systems and destroying quantum coherence.
2. **Processor B (9-Qubit Reference Topology) Bottleneck:** While its reference heavy-hex unit cell embeds a 4-spin ring with 0 SWAPs, its low maximum vertex degree (degree 3) cannot natively embed 2D lattices ($2 \times 3, 2 \times 4$ spin grids) or larger rings without routing across sparse, high-latency bridge nodes.

### 14.2 The Co-Designed Processor D Solution (12-Qubit Ring-Ladder)

We propose a **12-qubit Cylindrical Ring-Ladder Architecture** ($|V|=12, |E|=18$, 3-regular):

- **Coupling Topology:** Two coupled 6-qubit rings connected by 6 cross-rungs `(i, i+6)`, embedding 1D periodic rings ($N=4, 6, 8, 12$) and 2D spin grids ($2 \times 3, 2 \times 4$) with **zero routing SWAPs**.
- **Native Gate Co-Design:** Native parameterized $R_{zz}(\theta)$ entangling gates, replacing standard 2-$CX$ decompositions ($CX \to R_z \to CX$) with single direct entangling pulses, yielding an illustrative **70% duration reduction** based on microwave pulse literature ($120\text{ ns}$ vs $400\text{ ns}$).
- **Academic Distinction:** Classified as an architectural proposal (Category B) addressing empirical Phase 1 findings; empirical simulation results remain strictly tied to Processors A and B.

---

## 15. How to Run and Reproduce Every Result

```bash
# 1. Run unit test suite (11/11 tests pass)
.venv\Scripts\python.exe -m unittest tests/test_benchmark.py

# 2. Run full benchmark pipeline and regenerate CSVs/plots
.venv\Scripts\python.exe main.py

# 3. Validate clean-kernel notebook execution
.venv\Scripts\python.exe scratch/execute_notebook.py
```

---

## 16. Questions I Should Be Able to Answer (Oral Defense Guide)

### Q1: Why did you measure $\langle Z_0(t) \rangle$ instead of total magnetization $\langle M_z(t) \rangle$?

**Answer:** Total magnetization $\langle M_z(t) \rangle$ is identically zero ($0.000000$) for all time $t$ because the Hamiltonian and initial Néel state $|1010\rangle$ possess spatial reflection anti-symmetry $\mathcal{P} \hat{H} \mathcal{P}^\dagger = \hat{H}$, enforcing $\langle Z_0(t) \rangle = -\langle Z_3(t) \rangle$ and $\langle Z_1(t) \rangle = -\langle Z_2(t) \rangle$. Measuring $\langle M_z \rangle$ would only measure readout noise asymmetry. $\langle Z_0(t) \rangle$ breaks this spatial degeneracy and exhibits true Trotter convergence toward $+0.257957$.

### Q2: Why does Processor B have identical gate counts to Processor A on the open chain, but 56.8% fewer gates on the periodic ring?

**Answer:** The open chain only requires nearest-neighbor couplings between spins $(0,1), (1,2), (2,3)$. Both the 5Q line (Processor A) and the 9Q heavy-hex (Processor B) contain a linear 4-node subgraph, requiring 0 routing SWAPs. However, the periodic ring requires coupling spin 0 to spin 3. On a line, this requires 14 SWAP operations (42 extra CX gates). Processor B contains a natural 4-cycle `(1, 2, 5, 6)` in its heavy-hex unit cell, allowing direct nearest-neighbor execution of all 4 ring couplings with zero SWAPs.

### Q3: What is the difference between quantum state fidelity and classical distribution fidelity in your report?

**Answer:** Quantum state fidelity $F_{\text{state}} = |\langle \psi_{\text{exact}} | \psi_{\text{trotter}} \rangle|^2$ evaluates overlap between pure statevectors in Hilbert space, reflecting only algorithmic Trotter discretization error. Classical distribution fidelity $F_c = \sum_x \sqrt{P_{\text{noisy}}(x) P_{\text{ideal}}(x)}$ (Bhattacharyya coefficient) measures the statistical overlap between noisy measurement bitstring distributions and ideal distributions, capturing the cumulative effect of physical gate and readout noise.

### Q4: How does your proposed Processor D address the limitations of Processors A and B?

**Answer:** Running Problem S3 demonstrated that Processor A fails on cyclic boundaries due to linear SWAP overhead ($\mathcal{O}(N)$ distance), while Processor B’s degree-3 heavy-hex lattice cannot embed 2D lattices or larger rings ($N \ge 6$) without high-latency routing through sparse bridge nodes. Our proposed Processor D introduces a 12-qubit Cylindrical Ring-Ladder topology ($|V|=12, |E|=18$) and native parameterized $R_{zz}(\theta)$ gates. This eliminates all routing SWAPs for 2D/periodic systems and replaces 2-CX Ising decompositions with single entangling pulses, reducing entangling circuit duration by 70%.
