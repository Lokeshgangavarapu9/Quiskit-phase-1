# Student Submission Review & Verification Report

## Qiskit Fall Fest 2026 — Phase 1: Problem S3 (Noise in Trotter Simulation)

**Project Location:** `C:\Users\LOKESH\quiskit phase 1\`  
**Target Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Track:** Quantum Simulation  
**Problem Statement:** `S3 — Noise in Trotter Simulation`  
**Review Date:** October 12, 2026  
**Auditor / Assistant:** Antigravity AI Pair Programmer & Independent Verification Review  

---

## 1. Audit Scope & Review Protocol

This review was conducted to verify that this submission:

1. Complies with the actual competition guidelines and challenge starter materials.
2. Is mathematically and scientifically correct, with supported physical claims.
3. Is completely reproducible from a clean environment without missing dependencies or broken encodings.
4. Contains an honest, transparent AI disclosure conforming to the competition's policy.
5. Is documented in straightforward, undergraduate-level language that the student can personally explain and defend.

---

## 2. Official Requirements Checked & Source Evidence

Every requirement was traced back to official competition documentation stored in `official_materials/`:

| Requirement | Source Document & Exact Citation | Finding Label | Evidence & Traceability |
| :--- | :--- | :---: | :--- |
| **Problem Statement Selection** | `Update_QFF_2026_Hackathon_Phase1_Participant_Instructions.pdf`, p. 2, Table §2; `Updated_QFF_2026_Phase_1_Starter_Guide.pdf`, p. 16, §13.3. | **VERIFIED** | S3 (Noise in Trotter Simulation) under Quantum Simulation track is exclusively implemented. |
| **Phase 1 Scope Boundary** | `Participant_Instructions.pdf`, p. 3, §6; `QFF_IBM_Hackathon_Guideline.pdf`, p. 5, 7. | **VERIFIED** | Scope strictly restricted to Processor A and Processor B. Processor C and D are reserved for Phase 2 and omitted. |
| **Processor A Architecture** | `Starter_Guide.pdf`, p. 15, §12. | **VERIFIED** | 5-qubit linear chain with basis gates `['rz', 'sx', 'x', 'cx']` and ports `[0, 4]` loaded from `processors/processor_A.json`. |
| **Processor B Architecture** | `QFF_IBM_Hackathon_Guideline.pdf`, p. 4, §4; `Starter_Guide.pdf`, p. 24. | **VERIFIED** | 7-qubit heavy-hex-inspired compilation baseline with degree-3 branching hubs loaded from `processors/processor_B.json`. |
| **Noise Model Specifications** | `Starter_Guide.pdf`, p. 13, §10. | **VERIFIED** | $p_1 = 0.001$ on `x, sx`, $p_2 = 0.010$ on `cx`, and readout matrix $[[0.99, 0.01], [0.02, 0.98]]$. No thermal relaxation ($T_1, T_2$) is claimed. |
| **Execution Model** | `Starter_Guide.pdf`, p. 19, §14. | **VERIFIED** | Controlled synthetic noisy simulations executed locally using `qiskit_aer.AerSimulator` comparing ideal baseline to noisy baselines. |
| **Architecture Metrics** | `Starter_Guide.pdf`, p. 14, §11.2. | **VERIFIED** | Circuit depth, two-qubit depth, two-qubit gate counts, routing overhead, and physical qubit footprints are tracked. |
| **Problem-Specific Metrics** | `Participant_Instructions.pdf`, p. 3, §5.2. | **VERIFIED** | Magnetization $\langle M_z \rangle$, Total Variation Distance (TVD), Classical Distribution Fidelity ($F_c$), and pure State Fidelity ($F_{\text{state}}$) are recorded. |
| **Results Deliverables** | `Starter_Guide.pdf`, p. 22, §18. | **VERIFIED** | Exact required filenames generated in `results/tables/` (`AB_comparison.csv`, `final_comparison.csv`, etc.) and `results/figures/`. |
| **Repository Deliverables** | `Participant_Instructions.pdf`, p. 3–4, §7. | **VERIFIED** | Single public GitHub repository with `main.py`, `main.ipynb`, `processors/`, `src/`, `results/`, `README.md`, and environment specification. |
| **AI Disclosure Compliance** | `Participant_Instructions.pdf`, p. 5, §11. | **VERIFIED** | `AI_DISCLOSURE.md` is present, specific, and adheres to transparency rules. |
| **Submission Deadline & Portal** | `Participant_Instructions.pdf`, p. 4, §8. | **NEEDS MANUAL CONFIRMATION** | Final submission portal link and closing deadline must be confirmed directly on the official SRM AP hackathon portal. |

---

## 3. Scientific Correctness Findings

| Scientific Item | Verified Behavior & Proof | Finding Label | Notes |
| :--- | :--- | :---: | :--- |
| **Hermiticity of Hamiltonian** | $H = H^\dagger$, dimension $16 \times 16$. | **VERIFIED** | Verified by `test_problem_s3_hamiltonian_and_hermiticity`. |
| **Trotter Unitary Accuracy** | $\Vert U_{\text{qc}}(\Delta t) - \exp(-i H \Delta t)\Vert  \le \mathcal{O}(\Delta t^2)$. | **VERIFIED** | Verified by `test_independent_numerical_trotter_unitary`. At $\Delta t = 0.05$, norm difference is $0.0203$. |
| **Asymptotic Convergence** | Pure Trotter fidelity $F_{\text{state}} \to 1.0$ as $n \to \infty$. | **VERIFIED** | $F_{\text{state}}$ increases monotonically from $0.1171$ ($n=1$) to $0.9488$ ($n=4$) and $0.9924$ ($n=10$). |
| **Reflection Anti-Symmetry** | Exact $\langle M_z(t) \rangle \equiv 0$ for all $t$. | **VERIFIED** | Spatial reflection parity $[\mathcal{P}, H] = 0$ on $\vert 1010\rangle$ enforces $\langle Z_0 \rangle = -\langle Z_3 \rangle$ and $\langle Z_1 \rangle = -\langle Z_2 \rangle$. |
| **Noisy Magnetization Bias** | Measured $\langle M_z \rangle_{\text{noisy}} \sim 0.005 \dots 0.05$. | **VERIFIED** | Explained by asymmetric readout confusion: $P(0\mid 1) = 0.02 \ne P(1\mid 0) = 0.01$, which induces net positive spin bias. |
| **Processor B Routing Advantage** | Processor B cuts CX gates by $28.4\%$ at $n=4$ (53 vs 74). | **VERIFIED** | Degree-3 branching hubs reduce active spin distance across graph from 3 hops down to 2 hops. |
| **Explicit SWAP Count (0)** | Explicit SWAPs are 0; routing CX overhead is $42$ on A vs. $21$ on B. | **VERIFIED** | Target basis gates `['rz', 'sx', 'x', 'cx']` unroll each routing SWAP into 3 native CX gates ($1\text{ SWAP} \equiv 3\text{ CX}$). |
| **Critical Path Depth Equality** | Depth is 111 on both processors at $n=4$. | **VERIFIED** | Hub routing on Processor B serializes cross-interactions through the degree-3 hub, matching the busiest qubit on Processor A. |

---

## 4. Code Quality & Integrity Findings

1. **Modular Architecture:** Source code is cleanly decomposed into single-responsibility modules:
   - [`src/problem.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/problem.py): Physical Hamiltonian and Trotter circuit formulation.
   - [`src/processors.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/processors.py): Configuration loaders and Aer noise model builder.
   - [`src/transpilation.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/transpilation.py): Compilation wrapper and resource metric extraction.
   - [`src/metrics.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/metrics.py): Mathematical metric calculations.
   - [`src/visualization.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/visualization.py): 300 DPI plot routines.
2. **Deterministic Execution:** Simulation and transpilation passes use pinned random seeds (`seed=42`), guaranteeing byte-level repeatability of all outputs.
3. **No Unofficial Dependencies:** Code imports only standard Qiskit, Qiskit Aer, SciPy, NumPy, Pandas, Matplotlib, and NetworkX.

---

## 5. Corrections & Improvements Made During Final Review

During this final review session, the following specific corrections were implemented:

1. **Synchronized `main.ipynb` Evolution Time:**
   - *Previous state:* Cell 3 of `main.ipynb` hardcoded `total_time = 1.5`, whereas `main.py`, reports, and result tables used $T = 1.0$.
   - *Correction applied:* Updated markdown and code in `main.ipynb` to $T = 1.0$. Both files now strictly agree.
2. **Fixed `requirements.txt` Encoding:**
   - *Previous state:* `requirements.txt` was encoded in `UTF-16LE` with a BOM (`b'\xff\xfe'`), causing potential failures on Unix/Linux systems.
   - *Correction applied:* Re-encoded in clean standard `UTF-8` without BOM while preserving all package pins and versions exactly.
3. **Created `docs/STUDENT_WALKTHROUGH.md`:**
   - *Previous state:* Missing student study guide.
   - *Correction applied:* Authored comprehensive, undergraduate-level walkthrough covering the 15 required sections and an oral defense Q&A.
4. **Created `reports/STUDENT_SUBMISSION_REVIEW.md`:**
   - *Previous state:* Missing final review report.
   - *Correction applied:* Authored this comprehensive report documenting all findings, evidence, tests, and checklists.

---

## 6. Tests Actually Executed & Real Outcomes

The following test suites and scripts were executed in the workspace environment:

### Test Suite 1: Automated Unit & Physical Verification Suite

- **Command:** `.\.venv\Scripts\python.exe -m unittest tests/test_benchmark.py`

- **Execution Date:** October 12, 2026
- **Result:**

  ```text
  Ran 10 tests in 0.326s
  OK
  ```

- **Passed Test Inventory:**
  1. `test_processor_configurations`: PASSED.
  2. `test_coupling_maps_and_noise_models`: PASSED.
  3. `test_problem_s3_hamiltonian_and_hermiticity`: PASSED.
  4. `test_independent_numerical_trotter_unitary`: PASSED.
  5. `test_algorithmic_state_fidelity_convergence`: PASSED.
  6. `test_transpilation_and_active_qubits_extraction`: PASSED.
  7. `test_noise_model_exact_channels`: PASSED.
  8. `test_exact_magnetization_reflection_symmetry`: PASSED.
  9. `test_routing_cx_overhead_and_unrolled_swaps`: PASSED.
  10. `test_statistical_metrics_and_zero_division`: PASSED.

### Test Suite 2: Benchmark Pipeline Execution

- **Command:** `.\.venv\Scripts\python.exe main.py`

- **Result:** Successfully regenerated all CSV tables in `results/tables/`, JSON data in `results/raw/`, and 5 PNG figures in `results/figures/` without runtime warnings or errors.

---

## 7. Remaining Uncertainties & Manual Actions for the Student

The following items cannot be verified automatically by an AI assistant and require manual action:

1. **Submission Portal & Deadline (`NEEDS MANUAL CONFIRMATION`):**  
   Check the official SRM University-AP Qiskit Fall Fest portal / announcements to verify the exact submission deadline date and submission form URL.
2. **Repository Permissions (`NEEDS MANUAL CONFIRMATION`):**  
   Ensure that the GitHub repository [`https://github.com/Lokeshgangavarapu9/Quiskit-phase-1`](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1) is set to **Public** (or that the competition judges' accounts have read access).
3. **Personal Review of Walkthrough (`NEEDS MANUAL CONFIRMATION`):**  
   Read [`docs/STUDENT_WALKTHROUGH.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/docs/STUDENT_WALKTHROUGH.md) thoroughly before presentation or interview to ensure personal comfort explaining the concepts.

---

## 8. Final Student Completion Checklist Before Submission

Complete these steps in order before submitting:

- [x] Problem statement $S3$ exclusively selected and implemented.
- [x] Processor A (5Q line) and Processor B (7Q heavy-hex) analyzed.
- [x] Ideal vs noisy simulations cleanly separated.
- [x] Pure state fidelity distinguished from classical Bhattacharyya distribution fidelity.
- [x] Zero explicit SWAPs explained via 3-CX basis gate unrolling.
- [x] Zero exact magnetization explained via spatial reflection anti-symmetry.
- [x] `requirements.txt` confirmed in UTF-8 encoding.
- [x] `main.ipynb` confirmed to agree with `main.py` ($T = 1.0$).
- [x] All 10 unit tests passing cleanly.
- [x] `AI_DISCLOSURE.md` included and truthful.
- [ ] Confirm submission form link on official SRM AP portal.
- [ ] Inspect GitHub repository visibility on web browser.
- [ ] Final participant git commit and push when satisfied.
