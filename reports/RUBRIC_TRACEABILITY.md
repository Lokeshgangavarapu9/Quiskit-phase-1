# Official Rubric Traceability Matrix

**Project:** Qiskit Fall Fest 2026 — Phase 1 (Problem S3)  
**Host Institution:** SRM University-AP  
**Authoritative Reference:** *Phase 1 Master Guide (Page 7, Section 4)*  
**Document:** `reports/RUBRIC_TRACEABILITY.md`  

---

## 1. Traceability Matrix

| Official Rubric Criterion | Indicative Requirement | Existing Implementation | Evidence File & Location | Verification Status | Identified Gap | Proposed Correction |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| **1. Scientific & Algorithmic Correctness (30 pts)** | Does the algorithm execute without errors? Are results compared against an exact or classical theoretical reference? | Implements first-order Trotter circuit. Compares against SciPy matrix exponential (`expm`). Pure Trotter state fidelity increases from $0.117 \to 0.992$. | [`src/problem.py#L73-L102`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/problem.py#L73-L102); [`tests/test_benchmark.py#L77-L114`](file:///c:/Users/LOKESH/quiskit%20phase%201/tests/test_benchmark.py#L77-L114) | **PARTIAL** | Measures total $\langle M_z(t) \rangle$, which is identically 0.0 due to spatial reflection anti-symmetry. | Add $\langle Z_0(t) \rangle$ single-site magnetization tracking as explicitly requested by Master Guide PS-S2. |
| **2. Processor A vs B Architectural Analysis & Creativity (35 pts)** | Quantitative comparison: circuit depth, CX count, SWAP routing overhead, and noise impact. Evaluation of how creatively the participant designed and reasoned about their coupling topologies. | Compares 5Q Line vs. Heavy-Hex. Measures total depth, 2Q depth, CX gates, and derives equivalent SWAPs ($1\text{ SWAP} \equiv 3\text{ CX}$). Evaluates noisy simulation under Qiskit Aer. | [`src/transpilation.py#L11-L48`](file:///c:/Users/LOKESH/quiskit%20phase%201/src/transpilation.py#L11-L48); [`results/tables/final_comparison.csv`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/tables/final_comparison.csv) | **PARTIAL** | Processor B currently models a 7-qubit subgraph instead of Master Guide's 9-qubit reference. Noise model uses $p_2=0.01$ instead of $0.005$. | Upgrade Processor B to the 9-qubit, 12-edge heavy-hex graph. Update noise model to $p_2=0.005$ and symmetric $1\%$ readout error. |
| **3. Reproducibility & Code Quality (20 pts)** | Clean environment, pinned requirements.txt, structured repository, and end-to-end runnable notebook. | Pinned `requirements.txt` in clean UTF-8. Modular `src/` directory. All 10 unit tests pass in 0.33s. Deterministic execution with seed 42. | [`requirements.txt`](file:///c:/Users/LOKESH/quiskit%20phase%201/requirements.txt); [`tests/test_benchmark.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/tests/test_benchmark.py); [`main.py`](file:///c:/Users/LOKESH/quiskit%20phase%201/main.py) | **PARTIAL** | `main.ipynb` has unexecuted cells with empty outputs (`outputs: []`). | Expand `main.ipynb` with self-contained markdown and code cells; execute end-to-end and save outputs. |
| **4. Documentation & Visualizations (15 pts)** | Clear README, coupling map diagrams, legible performance comparison plots, and comprehensive report. | Comprehensive 232-line README. 5 publication-quality 300 DPI plots in `results/figures/`. Detailed technical explanations. | [`README.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/README.md); [`results/figures/`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/); [`docs/STUDENT_WALKTHROUGH.md`](file:///c:/Users/LOKESH/quiskit%20phase%201/docs/STUDENT_WALKTHROUGH.md) | **PARTIAL** | Root `report.md` is missing from the root level. `AI_DISCLOSURE.md` is empty (0 bytes). | Create comprehensive root `report.md` per Master Guide tree. Populate `AI_DISCLOSURE.md` with transparent disclosure. |

---

## 2. Overall Compliance Assessment

- **Current Overall Status:** **PARTIALLY COMPLIANT — READY FOR CORRECTION PLAN**
- **Strengths:** High code modularity, strict reproducibility of `main.py`, rigorous BCH operator norm bounding, robust SWAP deconstruction logic.
- **Remediable Gaps:** Four targeted technical adjustments (9Q Processor B, $p_2=0.005$ noise, $\langle Z_0(t) \rangle$ observable, executed `main.ipynb`, root `report.md`, and `AI_DISCLOSURE.md`) will bring the submission into **100% full compliance** with the SRM University-AP judging rubric.
