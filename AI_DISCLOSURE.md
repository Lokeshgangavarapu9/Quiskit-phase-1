# AI Disclosure Statement

## Qiskit Fall Fest 2026 — Phase 1: Problem S3 (Noise in Trotter Simulation)

**Project Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Track:** Quantum Simulation  
**Problem Statement:** `S3 — Noise in Trotter Simulation`  
**Submission Date:** October 2026  
**Applicable Rules:** Participant Instructions §11 (AI and Large Language Model Usage Policy)

---

### 1. Statement of Intent & Compliance

In strict compliance with the Qiskit Fall Fest 2026 rules and ethical standards for scientific computing, this document details the scope, tools, prompts, and verification procedures utilized in developing this Phase 1 submission.

All algorithms, mathematical derivations, physical models, and simulation pipelines have been independently understood, scientifically cross-checked, and defended by the student team.

---

### 2. Generative AI Tools Used

- **Tool Name:** Google Antigravity IDE (powered by Gemini models)
- **Role:** Interactive pair-programming assistant, codebase auditor, test authoring aid, and technical documentation formatter.
- **Environment:** Local VS Code / Antigravity development environment with read/write access to the local project workspace under direct student direction.

---

### 3. Scope of AI Assistance

Generative AI was employed for the following specific engineering tasks:

1. **Repository Auditing & Discrepancy Identification:**
   - Comparing local code implementations against the official Master Guide and Problem S3 requirements.
   - Identifying configuration mismatches (e.g., verifying 9-qubit vs. 7-qubit Processor B capacity, correcting two-qubit depolarizing rate from $0.010$ to $0.005$, and identifying symmetric vs. asymmetric readout noise conventions).
   - Auditing Hamiltonian boundary conditions (distinguishing the primary open-chain baseline from the periodic routing-stress extension).

2. **Code Implementation & Refactoring:**
   - Authoring the modular architecture in `src/`:
     - `src/problem.py`: Hamiltonian matrix construction, exact unitary reference via `scipy.linalg.expm`, Trotter circuit generator, and analytical expectation functions.
     - `src/processors.py`: Config parsing, Qiskit `CouplingMap` building, and Qiskit Aer `NoiseModel` construction (quantum errors and symmetric readout error).
     - `src/transpilation.py`: Compiler passes using Qiskit's `generate_preset_pass_manager`, metric extraction (depth, two-qubit depth, native CX count, active physical qubits).
     - `src/metrics.py`: Counts-based observable estimators ($\langle Z_0 \rangle$, $\langle M_z \rangle$) with shot standard error, Total Variation Distance (TVD), classical Bhattacharyya distribution overlap, and statevector pure-state fidelity.
     - `src/visualization.py`: Publication-quality plotting using `matplotlib` and `networkx`.

3. **Test Suite Development:**
   - Authoring comprehensive unit and integration tests in `tests/test_benchmark.py` (Hermiticity, operator norm bounds, convergence tests, reflection anti-symmetry, routing metrics, and statistical edge cases).

4. **Documentation & Formatting:**
   - Formatting and structuring technical reports, comprehensive Markdown tables, mathematical LaTeX equations, and student defense walkthroughs.

---

### 4. Human Verification & Critical Scientific Corrections

The student team actively verified and corrected all outputs generated during pair programming:

1. **Physical Symmetry & Observable Verification:**
   - *Discovery:* Initial automated scripts reported non-zero total magnetization $\langle M_z \rangle$ under asymmetric readout noise.
   - *Student Action:* Proved analytically that spatial reflection parity $\mathcal{P} \hat{H} \mathcal{P}^\dagger = \hat{H}$ acting on the staggered Néel state $|1010\rangle$ enforces $\langle Z_0(t) \rangle = -\langle Z_3(t) \rangle$ and $\langle Z_1(t) \rangle = -\langle Z_2(t) \rangle$, requiring $\langle M_z(t) \rangle \equiv 0.0$ identically for all $t$. The observed non-zero value was an artifact of broken readout symmetry.
   - *Correction:* Implemented the single-site expectation value $\langle Z_0(t) \rangle$ as the true primary convergence observable and verified the symmetric $1\%$ readout matrix.

2. **Coupling Topology & Transpilation Verification:**
   - *Discovery:* Processor B was initially represented as a 7-qubit subgraph with 6 edges.
   - *Student Action:* Re-checked the Master Guide reference architecture, correcting Processor B to a 9-qubit heavy-hex lattice with 12 undirected edges (24 directed pairs).
   - *Verification:* Verified that the 9-qubit lattice contains the 4-cycle `(1, 2, 5, 6)`, which completely eliminates routing SWAPs for the periodic TFIM ring, demonstrating a 56.8% CX reduction over the linear chain.

3. **Metric Precision:**
   - *Clarification:* Distinguished between pure quantum state fidelity $F_{\text{state}} = |\langle \psi_{\text{exact}} | \psi_{\text{trotter}} \rangle|^2$ (computable only from Hilbert space statevectors) and classical distribution fidelity $F_c = \sum_x \sqrt{P_{\text{noisy}}(x) P_{\text{ideal}}(x)}$ (Bhattacharyya coefficient from measurement counts).
   - Clarified that excess CX divided by 3 ($\Delta CX / 3$) is an *estimated equivalent SWAP count*, as modern compilers unroll SWAP operations directly into native basis CX gates.

4. **Independent Execution:**
   - All unit tests (11/11 passing), the full benchmark pipeline (`main.py`), and the executable walkthrough notebook (`main.ipynb`) were executed directly inside the local Python virtual environment (`.venv`, Python 3.11.9, Qiskit 2.5.2, Qiskit Aer 0.17.2).

---

### 5. Confirmation of Authorship & Understanding

The student authors certify that:

- We have personally executed, inspected, and validated every benchmark dataset and figure presented in this repository.
- We understand the theoretical principles, Qiskit implementations, compiler transformations, and physical conclusions.
- We are fully prepared to defend every aspect of this work during the Phase 1 oral defense.

