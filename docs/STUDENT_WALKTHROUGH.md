# Student Walkthrough & Technical Study Guide

## Qiskit Fall Fest 2026 — Phase 1: Problem S3 (Noise in Trotter Simulation)

**Project Location:** `C:\Users\LOKESH\quiskit phase 1`  
**GitHub Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Track:** Quantum Simulation  
**Problem Statement:** `S3 — Noise in Trotter Simulation`  
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
12. [Metrics: State Fidelity, Classical Overlap, TVD, & Magnetization](#12-metrics-state-fidelity-classical-overlap-tvd--magnetization)
13. [What the Results Demonstrate (and What They Do Not)](#13-what-the-results-demonstrate-and-what-they-do-not)
14. [How to Run and Reproduce Every Result](#14-how-to-run-and-reproduce-every-result)
15. [Questions I Should Be Able to Answer (Oral Defense Guide)](#15-questions-i-should-be-able-to-answer-oral-defense-guide)

---

## 1. The S3 Problem & Central Objective

### 1.1 The Fundamental Challenge in Digital Quantum Simulation

When simulating physical quantum systems on classical computers, the dimension of the Hilbert space grows exponentially as $2^N$ for $N$ spin-1/2 particles. Simulating even 50 spins exceeds the memory capacity of the world's largest supercomputers. Quantum computers, by contrast, map spin-1/2 particles directly to physical qubits.

However, quantum computers cannot execute continuous time evolution $U(t) = e^{-i H t}$ directly as an analog Hamiltonian. Instead, digital quantum processors must approximate continuous unitary evolution using discrete sequences of 1-qubit and 2-qubit quantum logic gates. This technique is called **Trotter product simulation** (or Trotterization).

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
- **Processor B:** A 7-qubit heavy-hex-inspired contemporary compilation baseline.

---

## 2. The Physical Hamiltonian & Term Interpretations

In [`src/problem.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/problem.py), the class `TrotterSimulationModel` implements a 4-spin 1D **Transverse-Field Ising Model (TFIM)**:

$$H = - J \sum_{i=0}^{N-2} Z_i Z_{i+1} - J_{\text{cross}} Z_0 Z_{N-1} - h \sum_{i=0}^{N-1} X_i$$

Where:

- $N = 4$ physical spins.
- $Z_i$ and $X_i$ are standard single-qubit Pauli matrices:
  $$Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}, \quad X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}$$

### What each physical term means

1. **Nearest-Neighbor Interaction ($-J \sum Z_i Z_{i+1}$):**  
   Couples adjacent spins along the chain ($Z_0 Z_1$, $Z_1 Z_2$, $Z_2 Z_3$). When $J > 0$ (ferromagnetic), aligned parallel spins ($\uparrow\uparrow$ or $\downarrow\downarrow$) have lower energy than anti-parallel spins ($\uparrow\downarrow$). In our benchmark, $J = 1.0$.

2. **Periodic Cross-Boundary Coupling ($-J_{\text{cross}} Z_0 Z_{N-1}$):**  
   Couples the two ends of the chain ($Z_0 Z_3$). This turns an open 1D string into a closed ring.  
   *Why this term matters architecturally:* This is the critical routing benchmark term. On a linear processor graph like Processor A, physical qubit 0 and physical qubit 3 are separated by 3 hops. The compiler must insert routing operations (SWAPs) to bring their quantum states together. In our benchmark, $J_{\text{cross}} = 0.5$.

3. **Transverse Magnetic Field ($-h \sum X_i$):**  
   Applies an external magnetic field perpendicular to the spin alignment axis (in the $X$ direction). This term drives quantum tunneling and state oscillations between $|0\rangle$ and $|1\rangle$, preventing the spins from being frozen in static classical eigenstates. In our benchmark, $h = 0.8$.

---

## 3. Initial State Preparation & Physical Symmetries

### 3.1 Initial State

The initial state is initialized in the staggered **Neel state** (antiferromagnetic domain wall):
$$|\psi(0)\rangle = |1010\rangle$$

In `TrotterSimulationModel.build_trotter_circuit()`:

```python
# State preparation in Qiskit (q0 is rightmost bit in string '1010')
for idx, char in enumerate(reversed(self.initial_state_str)):
    if char == "1":
        qc.x(idx)
```

Qubits 1 and 3 receive Pauli-$X$ gates (bit-flips from $|0\rangle$ to $|1\rangle$), preparing $|\psi(0)\rangle = |1010\rangle$.

### 3.2 Exact Reflection Anti-Symmetry

The system possesses a physical spatial reflection symmetry $\mathcal{P}: i \mapsto 3 - i$.
Under spatial reflection:

- $Z_0 Z_1 \leftrightarrow Z_2 Z_3$
- $Z_1 Z_2 \leftrightarrow Z_1 Z_2$
- $Z_0 Z_3 \leftrightarrow Z_0 Z_3$
- $\sum X_i \leftrightarrow \sum X_i$

Because $[\mathcal{P}, H] = 0$, Schrödinger evolution preserves reflection parity. For initial state $|1010\rangle$:
$$\langle Z_0(0) \rangle = +1, \quad \langle Z_1(0) \rangle = -1, \quad \langle Z_2(0) \rangle = +1, \quad \langle Z_3(0) \rangle = -1$$
Notice that $\langle Z_0 \rangle = -\langle Z_3 \rangle$ and $\langle Z_1 \rangle = -\langle Z_2 \rangle$.  
By symmetry, this anti-symmetry holds for all time $t$:
$$\langle Z_0(t) \rangle = -\langle Z_3(t) \rangle, \quad \langle Z_1(t) \rangle = -\langle Z_2(t) \rangle$$

Consequently, the **exact total magnetization** is identically zero for all $t$:
$$\langle M_z(t) \rangle = \frac{1}{4} \sum_{i=0}^3 \langle Z_i(t) \rangle \equiv 0$$
This exact mathematical property is verified independently in `tests/test_benchmark.py::test_exact_magnetization_reflection_symmetry`.

---

## 4. First-Order Suzuki-Trotter Decomposition

Continuous unitary evolution is:
$$U(t) = e^{-i H t} = \exp\left( -i \left[ H_{ZZ} + H_X \right] t \right)$$

Because $[H_{ZZ}, H_X] \ne 0$ (Pauli $Z$ and $X$ anti-commute: $Z X = - X Z$), the matrix exponential cannot be split into a simple product:
$$e^{-i (H_{ZZ} + H_X) t} \ne e^{-i H_{ZZ} t} e^{-i H_X t}$$

### 4.1 The Baker-Campbell-Hausdorff (BCH) Formula

For small time step $\Delta t = t / n$:
$$e^{-i H_{ZZ} \Delta t} e^{-i H_X \Delta t} = \exp\left( -i (H_{ZZ} + H_X) \Delta t - \frac{\Delta t^2}{2} [H_{ZZ}, H_X] + \mathcal{O}(\Delta t^3) \right)$$

By taking $n$ steps of duration $\Delta t = t / n$:
$$U(t) \approx \left[ e^{-i H_{ZZ} \Delta t} e^{-i H_X \Delta t} \right]^n$$

The leading commutator error per step is $\mathcal{O}(\Delta t^2) = \mathcal{O}(t^2 / n^2)$.  
Accumulated across $n$ steps, the total algorithmic discretization error scales as:
$$\text{Total Trotter Error} \sim n \cdot \mathcal{O}\left(\frac{t^2}{n^2}\right) = \mathcal{O}\left(\frac{t^2}{n}\right)$$
As $n \to \infty$, the Trotter approximation converges monotonically to the exact unitary operator.

---

## 5. Quantum Circuit Construction

How do we implement $e^{-i H_{ZZ} \Delta t}$ and $e^{-i H_X \Delta t}$ with standard quantum gates?

### 5.1 Two-Qubit Interaction Gate: $e^{i J \Delta t Z_j Z_k}$

We use the mathematical identity:
$$CX_{j, k} (I \otimes Z_k) CX_{j, k} = Z_j \otimes Z_k$$
Therefore, conjugating an $R_Z$ rotation by CNOT gates synthesizes a $Z \otimes Z$ interaction:
$$CX_{j, k} \cdot R_Z(\theta, k) \cdot CX_{j, k} = \exp\left( -i \frac{\theta}{2} Z_j Z_k \right)$$

To achieve $\exp(-i (-J \Delta t) Z_j Z_k) = \exp(i J \Delta t Z_j Z_k)$, we choose $\theta = -2 J \Delta t$:

```python
# In src/problem.py:
qc.cx(i, i + 1)
qc.rz(-2.0 * self.J * dt, i + 1)
qc.cx(i, i + 1)
```

### 5.2 Single-Qubit Field Gate: $e^{i h \Delta t X_i}$

An $R_X$ rotation generates an $X$ rotation:
$$R_X(\phi, i) = \exp\left( -i \frac{\phi}{2} X_i \right)$$
Setting $\phi = -2 h \Delta t$ gives $\exp(i h \Delta t X_i)$:

```python
# In src/problem.py:
qc.rx(-2.0 * self.h * dt, i)
```

Each Trotter step consists of:

- 3 nearest-neighbor $ZZ$ blocks ($2 \times 3 = 6$ CX gates).
- 1 cross-boundary $ZZ$ block ($2 \times 1 = 2$ CX gates).
- 4 single-qubit $R_X$ gates.
- **Logical Two-Qubit Total:** Exactly $8$ CX gates per Trotter step.

---

## 6. Processor A vs. Processor B Topologies

The processor configurations are defined in [`processors/processor_A.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_A.json) and [`processors/processor_B.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_B.json):

```text
Processor A: Linear Chain (5 Qubits)
  0 ── 1 ── 2 ── 3 ── 4
  (Designated I/O ports: 0, 4)

Processor B: Heavy-Hex Subgraph (7 Qubits)
  0 ── 1 ── 2
       │
       3
       │
  4 ── 5 ── 6
  (Designated I/O ports: 0, 6)
```

### Key Differences

1. **Node Degree (Connectivity):**  
   - On Processor A, every internal node has degree 2 (simple line).
   - On Processor B, nodes 1 and 5 have **degree 3** (junction hubs).
2. **Graph Diameter for 4 Spins:**  
   - On Processor A, spins arranged $0, 1, 2, 3$ have distance 3 between spin 0 and spin 3.
   - On Processor B, spin 0 and spin 2 can connect to spin 1 directly, and node 3 connects 1 to 5. The effective graph diameter across the active spins is reduced to 2 hops.

---

## 7. Transpilation, Routing, & Layout Mapping

In [`src/transpilation.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/transpilation.py), the function `compile_for_processor()` calls Qiskit's compiler:

```python
compiled = transpile(
    logical_circuit,
    coupling_map=coupling_map,
    basis_gates=['rz', 'sx', 'x', 'cx'],
    optimization_level=1,
    seed_transpiler=42
)
```

### The 4 Transpilation Stages

1. **Layout / Placement:** Maps logical qubits $q_0, q_1, q_2, q_3$ to physical processor qubits. Both processors select 4 active qubits out of their available capacity (5 on A, 7 on B).
2. **Routing:** If a CNOT gate is required between two non-adjacent physical qubits, the `SabreSwap` pass inserts SWAP operations to exchange qubit states along the graph until they are adjacent.
3. **Basis Gate Decomposition:** Decomposes non-native gates into the physical basis set: `['rz', 'sx', 'x', 'cx']`.
4. **Optimization:** Cancels adjacent inverse gates ($CX \cdot CX = I$, $RZ(\alpha) RZ(\beta) = RZ(\alpha + \beta)$).

---

## 8. Hardware Noise Modeling (Depolarizing & Readout)

In [`src/processors.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/processors.py), `build_noise_model()` configures Qiskit Aer's `NoiseModel` according to the official Starter Guide (p. 13):

### 8.1 Single-Qubit Depolarizing Error

Applied to physical 1-qubit pulses (`x`, `sx`) with error rate $p_1 = 0.001$:
$$\mathcal{E}_{1}(\rho) = (1 - p_1) \rho + \frac{p_1}{3} (X \rho X + Y \rho Y + Z \rho Z)$$

### 8.2 Two-Qubit Depolarizing Error

Applied to physical entangling gates (`cx`) with error rate $p_2 = 0.010$ (10x higher than 1Q gates):
$$\mathcal{E}_{2}(\rho) = (1 - p_2) \rho + \frac{p_2}{15} \sum_{P \in \{I, X, Y, Z\}^{\otimes 2} \setminus \{II\}} P \rho P$$

### 8.3 Asymmetric Readout Confusion

Measurement outcomes are corrupted by a classical confusion matrix:
$$R = \begin{pmatrix} P(\text{read } 0 \mid \text{state } 0) & P(\text{read } 0 \mid \text{state } 1) \\ P(\text{read } 1 \mid \text{state } 0) & P(\text{read } 1 \mid \text{state } 1) \end{pmatrix} = \begin{pmatrix} 0.99 & 0.02 \\ 0.01 & 0.98 \end{pmatrix}$$

Notice:
$$P(\text{read } 0 \mid \text{state } 1) = 0.02 \ne P(\text{read } 1 \mid \text{state } 0) = 0.01$$
The probability of misreading a true $|1\rangle$ as a $0$ is twice as large as misreading a true $|0\rangle$ as a $1$. This asymmetry induces a slight positive bias in empirical magnetization measurements.

> [!NOTE]
> **No Thermal Relaxation ($T_1/T_2$):** The official competition guide does not specify qubit lifetimes ($T_1$) or coherence times ($T_2$). In strict adherence to scientific integrity, thermal relaxation is omitted rather than inventing unofficial parameter values.

---

## 9. Ideal Reference vs. Noisy Simulation

In `main.py`, three simulation runs are executed for each step count $n$:

1. **Ideal Simulation (`sim_ideal`):** Runs the logical circuit with zero noise, capturing the pure algorithmic discretization state.
2. **Processor A Noisy Simulation (`sim_a`):** Compiles onto Processor A's coupling map and simulates under Processor A's noise model.
3. **Processor B Noisy Simulation (`sim_b`):** Compiles onto Processor B's coupling map and simulates under Processor B's noise model.

All simulators use 4096 measurement shots and fixed seeds (`seed=42`).

---

## 10. Circuit Depth vs. Two-Qubit Gate Counting

In [`src/transpilation.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/transpilation.py):

- **Total Depth:** The longest critical path of gates from circuit input to output, including 1-qubit and 2-qubit gates.
- **Two-Qubit Depth:** The critical path considering only entangling gates (`operation.num_qubits == 2`).
- **Two-Qubit Gate Count:** The total count of CX gates across the entire circuit.

### Why is Total Depth Equal (111) while CX Gate Counts Differ (74 vs. 53 at $n=4$)

- On Processor B, cross-interactions route through the degree-3 hub (qubit 1). Qubit 1 participates in 53 CX gates, forming a critical path of 53 two-qubit layers.
- On Processor A, the 74 CX gates are distributed across the line, and the busiest qubit chain also has 53 two-qubit layers on its critical path.
- When single-qubit $R_X$ pulses (unrolled to `rz-sx-rz`) are added, both processors yield a total depth of 111.
- **Key Insight:** Equal depth does *not* mean equal error. Because depolarizing noise occurs on *every* gate regardless of whether gates execute in parallel, Processor B's 21 fewer gates result in significantly less total mixed-state noise entropy.

---

## 11. Explicit SWAP Gates vs. Equivalent SWAP Estimates

A common source of confusion in Qiskit transpilation is:
> *Why does `count_ops()` show `swap_count = 0` on both processors, even though Processor B saves routing operations?*

### The Answer: Basis Gate Unrolling

In standard superconducting hardware, a physical SWAP gate is not native. Instead, the basis set is `['rz', 'sx', 'x', 'cx']`. During compilation:

1. The routing pass inserts SWAP operations.
2. The basis unrolling pass decomposes each SWAP into **3 native CX gates**:
   $$SWAP(a, b) \equiv CX(a, b) \cdot CX(b, a) \cdot CX(a, b)$$

3. As a result, explicit SWAPs are eliminated from the final gate list (`explicit_swap_count = 0`).

### Mathematical Derivation of Equivalent SWAPs

To measure routing overhead honestly:
$$\text{Routing CX Overhead} = \text{Compiled 2Q Gates} - \text{Logical 2Q Gates}$$
$$\text{Equivalent SWAPs} = \frac{\text{Routing CX Overhead}}{3}$$

At $n=4$:

- Logical CX gates = $32$.
- Processor A compiled CX gates = $74 \implies \text{Overhead} = 42 \implies 14 \text{ Equivalent SWAPs}$.
- Processor B compiled CX gates = $53 \implies \text{Overhead} = 21 \implies 7 \text{ Equivalent SWAPs}$.
- **Net Saving on Processor B:** 21 fewer CX gates (-28.4%) and 7 fewer equivalent SWAPs (-50.0%).

---

## 12. Metrics: State Fidelity, Classical Overlap, TVD, & Magnetization

In [`src/metrics.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/metrics.py), metrics are strictly separated into distinct mathematical categories:

### 12.1 Pure Quantum State Fidelity ($F_{\text{state}}$)

Measures the pure mathematical overlap between the exact continuous-time state $|\psi_{\text{exact}}(t)\rangle$ and the ideal Trotter state $|\psi_{\text{trotter}}(t)\rangle$:
$$F_{\text{state}} = |\langle \psi_{\text{exact}}(t) \mid \psi_{\text{trotter}}(t) \rangle|^2$$
At $n=1$, $F_{\text{state}} = 0.1171$. At $n=4$, $F_{\text{state}} = 0.9488$. At $n=10$, $F_{\text{state}} = 0.9924$. This measures *algorithmic discretization error only*.

### 12.2 Classical Distribution Fidelity ($F_c$)

Computed from measured bitstring count distributions via the classical **Bhattacharyya coefficient**:
$$F_c(P, Q) = \sum_{x \in \{0, 1\}^N} \sqrt{P(x) \cdot Q(x)}$$
Where $P(x)$ is the empirical noisy probability distribution and $Q(x)$ is the ideal reference distribution. $F_c = 1.0$ represents identical output probability distributions.

### 12.3 Total Variation Distance (TVD)

The standard statistical distance between probability distributions:
$$\text{TVD}(P, Q) = \frac{1}{2} \sum_{x \in \{0, 1\}^N} |P(x) - Q(x)|, \quad \text{TVD} \in [0, 1]$$
At $n=4$, Processor B achieves $\text{TVD} = 0.1697$, compared to $0.1992$ on Processor A ($14.8\%$ lower distribution error).

### 12.4 Z-Magnetization ($\langle M_z \rangle$)

$$\langle M_z \rangle = \frac{1}{N} \sum_{i=0}^{N-1} \langle Z_i \rangle$$
Computed from bitstring counts where bit '0' corresponds to eigenvalue $+1$ and bit '1' corresponds to $-1$. Standard error is computed as $\text{SE} = \sigma / \sqrt{N_{\text{shots}}}$.

---

## 13. What the Results Demonstrate (and What They Do Not)

### What the Results Demonstrate

1. **Branching Topologies Reduce Routing Overhead:** For non-local interactions, a processor graph with degree-3 branching nodes (Processor B) reduces interaction distance across active qubits, cutting routing operations by $50\%$ compared to a 1D linear chain (Processor A).
2. **Noise Decay Dominates Trotter Refinement:** Under $1\%$ two-qubit depolarizing error, the marginal benefit of taking smaller Trotter steps ($n > 4$) is quickly overwhelmed by gate error accumulation.
3. **Geometric Advantage with Identical Noise:** Because both processors share identical gate noise parameters ($p_1 = 0.001, p_2 = 0.010$), Processor B's performance improvement is purely a consequence of architectural geometry.

### What the Results Do NOT Demonstrate

1. **Processor B is NOT Universally Superior:** If the simulated Hamiltonian was a strictly 1D open chain ($J_{\text{cross}} = 0$), Processor A would require zero routing operations, eliminating Processor B's topological advantage.
2. **Results Depend on Transpiler Heuristics:** Compilation counts depend on Qiskit 2.5.2's `SabreSwap` heuristic router and fixed seed (`seed=42`). Different optimization levels or seeds may produce minor gate count variations.
3. **Synthetic Simulation is Not Physical Hardware:** Real IBM QPUs exhibit spatially heterogeneous error rates, crosstalk, spectator qubit errors, and drift, which are not captured in uniform depolarizing models.

---

## 14. How to Run and Reproduce Every Result

### Step 1: Clean Environment Setup

```powershell
cd "C:\Users\LOKESH\quiskit phase 1"
# Activate virtual environment
.\.venv\Scripts\Activate.ps1
# Install pinned dependencies
pip install -r requirements.txt
```

### Step 2: Run Automated Test Suite

```powershell
python -m unittest tests/test_benchmark.py
```

*Expected output: `Ran 10 tests in ~0.3s ... OK`.*

### Step 3: Run Full Benchmark Pipeline

```powershell
python main.py
```

*Expected output: Generates all CSV files in `results/tables/`, JSON data in `results/raw/`, and 5 PNG figures in `results/figures/`.*

### Step 4: Interactive Notebook

Open `main.ipynb` in VS Code or JupyterLab and execute all cells. All outputs will match `main.py`.

---

## 15. Questions I Should Be Able to Answer (Oral Defense Guide)

### Q1: What is Trotterization

> **Answer:** Trotterization is an approximation technique for simulating continuous quantum dynamics on digital quantum computers. Because physical terms in the Hamiltonian do not commute ($[H_A, H_B] \ne 0$), we approximate $e^{-i(H_A+H_B)t} \approx (e^{-i H_A \Delta t} e^{-i H_B \Delta t})^n$ using $n$ small time steps $\Delta t = t/n$. The error per step scales as $\mathcal{O}(\Delta t^2)$, giving a total discretization error that shrinks as $\mathcal{O}(1/n)$.

### Q2: Why does processor connectivity matter

> **Answer:** Quantum processors can only execute two-qubit entangling gates (like CNOT) between qubits that are physically connected by coupling edges in the hardware graph. If two interacting logical spins are not connected, the compiler must insert SWAP gates to move their quantum states adjacent to each other. More SWAP gates mean deeper circuits, more noisy gates, and degraded fidelity.

### Q3: What is a CNOT gate, and why is it expensive

> **Answer:** A Controlled-NOT (CNOT or CX) gate is a fundamental two-qubit entangling gate that flips the target qubit if the control qubit is $|1\rangle$. In physical superconducting architectures, CNOT gates require microwave cross-resonance pulses between adjacent resonators. They typically take 5 to 10 times longer to execute and suffer from error rates roughly 10 times higher than single-qubit gates ($10^{-2}$ vs $10^{-3}$).

### Q4: What is the difference between ideal and noisy simulation

> **Answer:** In ideal simulation, quantum circuits are treated as pure unitary statevectors with perfect gates and zero decoherence. In noisy simulation (using Qiskit Aer), physical noise channels—such as depolarizing error (random Pauli gate corruptions) and readout error (measurement bit-flips)—are applied to the state after every gate, modeling realistic hardware imperfections.

### Q5: What is Total Variation Distance (TVD)

> **Answer:** Total Variation Distance is a standard statistical metric measuring the distance between two probability distributions: $\text{TVD}(P, Q) = \frac{1}{2} \sum_x |P(x) - Q(x)|$. It is bounded between $0$ (identical distributions) and $1$ (disjoint distributions). We use TVD to quantify how far the noisy measured distribution deviates from the ideal reference distribution.

### Q6: Why does the measured result change with shot count

> **Answer:** Quantum computers do not directly output state amplitudes; they measure quantum states projectively, collapsing them to classical bitstrings. Empirical probabilities are estimates derived from finite sampling (shots). By the Central Limit Theorem, statistical shot noise scales as $1/\sqrt{N_{\text{shots}}}$. In our experiments, we use $4096$ shots to ensure shot noise standard error is below $1\%$.

### Q7: What assumptions did this project make

> **Answer:** While the problem track (S3), noise parameters ($p_1=0.001, p_2=0.01$, readout matrix), and Processor A topology are taken directly from the official competition materials, our benchmark assumed:
> 1. A 4-spin Transverse-Field Ising Model ($J=1.0, h=0.8$) with a cross-boundary ring term ($J_{\text{cross}}=0.5$) to create a non-trivial routing problem.
> 2. An initial Neel domain wall state $|1010\rangle$.
> 3. Total evolution time $T = 1.0$.
> 4. A 7-qubit heavy-hex subgraph for Processor B based on contemporary IBM Quantum devices.

### Q8: What would you improve with another week

> **Answer:** With another week, I would:
> 1. Implement second-order Suzuki-Trotter (Strang splitting: $e^{-i H_X \Delta t / 2} e^{-i H_{ZZ} \Delta t} e^{-i H_X \Delta t / 2}$), which reduces discretization error to $\mathcal{O}(\Delta t^3)$.
> 2. Apply Zero-Noise Extrapolation (ZNE) error mitigation using Mitiq or Qiskit Runtime to extrapolate noisy measurement expectation values back to the zero-noise limit.
> 3. Test alternative Qiskit routing passes (such as Lookahead or Sabre with custom heuristic weights) to further minimize two-qubit gate overhead.
