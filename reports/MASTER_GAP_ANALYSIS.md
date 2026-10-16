# Master Gap Analysis & Prioritized Defect Register

**Project:** Qiskit Fall Fest 2026 — Phase 1 (Problem S3)  
**Document:** `reports/MASTER_GAP_ANALYSIS.md`  
**Classification System:**
- **P0:** Critical scientific, model, or official-compliance problems.
- **P1:** Stale benchmark calculations or superseded result artifacts.
- **P2:** Reproducibility, testing, or pipeline execution gaps.
- **P3:** Documentation, presentation, or structural inconsistencies.
- **P4:** Optional enhancements and scientific extensions.

---

## 1. Prioritized Defect Register

### [P0] Critical Scientific & Compliance Issues

#### Issue P0-1: Processor B Qubit Count & Graph Mismatch
- **Artifact Affected:** [`processors/processor_B.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_B.json), [`src/visualization.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/visualization.py), [`README.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/README.md)
- **Current Behavior:** Models a 7-qubit subgraph (nodes 0 to 6, 6 undirected edges).
- **Authoritative Requirement:** Master Guide (p. 2) specifies a **9-qubit physical budget (Nodes 0 to 8)** with a **12-edge heavy-hex-inspired graph**:
  $$(0,1), (1,2), (1,6), (2,3), (2,6), (2,5), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0)$$
- **Impact:** Severity **CRITICAL**. Evaluation under an outdated 7-qubit model risks deduction under the "Processor A vs B Architectural Analysis" rubric category (35 points).
- **Classification:** **CONFIRMED REQUIREMENT MISMATCH**
- **Recommended Correction:** Update `processors/processor_B.json` to 9 physical qubits with the 12 specified undirected edges. Update layout coordinates in `src/visualization.py`.

#### Issue P0-2: Two-Qubit CX Depolarizing Noise Rate ($p_2$)
- **Artifact Affected:** [`processors/processor_A.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_A.json), [`processors/processor_B.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_B.json)
- **Current Behavior:** `two_qubit_depolarizing_p = 0.01` ($1.0\%$).
- **Authoritative Requirement:** Master Guide (p. 2) sets `2-qubit CX depolarizing: 0.5% (p = 0.005)`.
- **Impact:** Severity **HIGH**. A $1.0\%$ error rate accelerates noise decay by $2\times$, causing the crossover point $n^*$ to occur prematurely at $n=1$.
- **Classification:** **CONFIRMED REQUIREMENT MISMATCH**
- **Recommended Correction:** Set `two_qubit_depolarizing_p = 0.005` in both processor JSON files.

#### Issue P0-3: Readout Error Confusion Matrix Symmetry
- **Artifact Affected:** [`processors/processor_A.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_A.json), [`processors/processor_B.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/processors/processor_B.json)
- **Current Behavior:** Asymmetric confusion matrix:
  $$\begin{pmatrix} 0.99 & 0.01 \\ 0.02 & 0.98 \end{pmatrix}$$
- **Authoritative Requirement:** Master Guide (p. 2) specifies `Readout error: 1.0% (p = 0.01)` (symmetric).
- **Impact:** Severity **MEDIUM**. The asymmetric matrix flips $|1\rangle \to |0\rangle$ at twice the rate of $|0\rangle \to |1\rangle$, inducing an artificial positive spin bias into empirical measurements.
- **Classification:** **CONFIRMED REQUIREMENT MISMATCH**
- **Recommended Correction:** Update readout error matrix to symmetric $[[0.99, 0.01], [0.01, 0.99]]$.

#### Issue P0-4: Primary Physical Observable Cancellation ($\langle M_z(t) \rangle \equiv 0$)
- **Artifact Affected:** [`src/problem.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/problem.py), [`main.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/main.py)
- **Current Behavior:** Tracks total magnetization $\langle M_z(t) \rangle = \frac{1}{4} \sum_i \langle Z_i(t) \rangle$.
- **Authoritative Requirement:** Master Guide PS-S2 (p. 5) explicitly instructs: *"Measure $\langle Z_0(t) \rangle$ and compare accuracy and SWAP overhead on A vs B."*
- **Impact:** Severity **CRITICAL**. Spatial reflection parity anti-symmetry on the staggered Néel state forces exact total magnetization to be identically zero for all $t$, masking true Trotter convergence.
- **Classification:** **CONFIRMED SCIENTIFIC DEFECT**
- **Recommended Correction:** Implement single-site expectation value $\langle Z_0(t) \rangle$ alongside $\langle M_z(t) \rangle$.

---

### [P1] Superseded Benchmark Results

#### Issue P1-1: Existing Results Generated Under Old Configurations
- **Artifact Affected:** All files in [`results/tables/`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/tables/), [`results/figures/`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/), and [`results/raw/`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/raw/).
- **Current Behavior:** Data reflects 7Q Processor B, $p_2 = 0.01$, and asymmetric readout noise.
- **Impact:** Severity **HIGH**. Results in tables and plots disagree with Master Guide specifications.
- **Classification:** **STALE BENCHMARK OUTPUTS**
- **Recommended Correction:** Re-execute `main.py` after correcting P0 issues to regenerate all CSV tables, JSON dumps, and PNG plots.

---

### [P2] Reproducibility & Testing Issues

#### Issue P2-1: Unexecuted Jupyter Notebook (`main.ipynb`)
- **Artifact Affected:** [`main.ipynb`](file:///c:/Users/LOKESH/quiskit%20phase%201/main.ipynb)
- **Current Behavior:** All cells have `"outputs": []` and `"execution_count": null`.
- **Authoritative Requirement:** Master Guide & Participant Instructions mandate an end-to-end executed notebook with visible outputs.
- **Impact:** Severity **HIGH**. Automated evaluation scripts check for notebook variable outputs and penalize empty notebooks.
- **Classification:** **CONFIRMED REQUIREMENT MISMATCH**
- **Recommended Correction:** Author self-contained cell-by-cell execution with markdown explanations and execute cleanly from a fresh kernel.

#### Issue P2-2: Unit Test Assertions Hardcoded to 7Q Processor B
- **Artifact Affected:** [`tests/test_benchmark.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/tests/test_benchmark.py)
- **Current Behavior:** Line 47 asserts `cfg_b["num_qubits"] == 7` and line 185 asserts `assertEqual(met_b["two_qubit_ops"], 53)`.
- **Impact:** Severity **MEDIUM**. Upgrading Processor B to 9 qubits will cause tests to fail unless assertions are updated to the 9Q values.
- **Classification:** **DEPENDENT TEST UPDATE**
- **Recommended Correction:** Update unit test assertions to validate 9 physical qubits and updated 9Q compiled CX counts.

---

### [P3] Documentation & Structural Inconsistencies

#### Issue P3-1: Missing Root Deliverable `report.md`
- **Artifact Affected:** Project root directory
- **Current Behavior:** Reports are stored in `reports/` (`FINAL_AUDIT.md`, `FINAL_RESULTS.md`, etc.).
- **Authoritative Requirement:** Master Guide repository structure lists `report.md` directly at the project root.
- **Impact:** Severity **MEDIUM**. Automated repo scanners look for `project/report.md`.
- **Classification:** **CONFIRMED REQUIREMENT MISMATCH**
- **Recommended Correction:** Create a comprehensive, synthesized `report.md` at the project root.

#### Issue P3-2: Empty AI Disclosure Statement (`AI_DISCLOSURE.md`)
- **Artifact Affected:** [`AI_DISCLOSURE.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/AI_DISCLOSURE.md)
- **Current Behavior:** File exists but is empty (0 bytes). README line 231 claims it is provided.
- **Authoritative Requirement:** Participant Instructions (p. 5, §11) mandate a transparent AI disclosure.
- **Impact:** Severity **HIGH**. Submissions can be penalized for undisclosed AI usage.
- **Classification:** **CONFIRMED DEFECT**
- **Recommended Correction:** Populate `AI_DISCLOSURE.md` with an honest, transparent description of AI pair-programming assistance.

#### Issue P3-3: README & Walkthrough Documentation Outdated
- **Artifact Affected:** [`README.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/README.md), [`docs/STUDENT_WALKTHROUGH.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/docs/STUDENT_WALKTHROUGH.md)
- **Current Behavior:** Documents still describe Processor B as 7 qubits and CX noise as $1.0\%$.
- **Impact:** Severity **MEDIUM**. Narrative text must match updated configurations and data tables.
- **Classification:** **DOCUMENTATION INCONSISTENCY**
- **Recommended Correction:** Update README and walkthrough text to describe 9-qubit Processor B, $p_2=0.005$, and single-site $\langle Z_0(t) \rangle$ observable.

---

### [P4] Scientific Enhancements

#### Issue P4-1: Open Chain vs. Periodic Ring Boundary Setting
- **Artifact Affected:** [`src/problem.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/problem.py)
- **Current Behavior:** $J_{\text{cross}} = 0.5$ is hardcoded as default.
- **Enhancement:** Add an explicit configuration toggle:
  - `boundary = 'open'` ($J_{\text{cross}} = 0.0$, official baseline).
  - `boundary = 'periodic'` ($J_{\text{cross}} = 0.5$, routing stress test).
- **Benefit:** Allows the student to present both the exact official open chain and the advanced periodic routing study.
