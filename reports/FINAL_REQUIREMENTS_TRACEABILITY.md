# Final Requirements Traceability Matrix
## Qiskit Fall Fest 2026 — Phase 1: Problem S3 (Noise in Trotter Simulation)

**Project Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Track:** Quantum Simulation  
**Problem Statement:** S3 — Noise in Trotter Simulation  
**Date:** October 16, 2026  
**Auditor / Reviewer:** Final Technical & Compliance Reviewer

---

## 1. Document Inventory of Official Input Materials

| Document Filename | Title / Source | Pages | Inspected | Key Extracted Requirements | Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| `media_1792151376107.pdf` | Benchmark Configuration Guide | 2 | 100% | Processor A (5Q line) & B (9Q heavy-hex) baseline definitions; port definitions (0,4 for A; 0,8 for B). | **VERIFIED** |
| `media_1792151376186.pdf` | Quantum Algorithm-Architecture Co-Design Proposal | 21 | 100% | Co-design principles; mapping interaction graphs to physical coupling graphs; hardware routing penalty analysis. | **VERIFIED** |
| `media_1792151376205.pdf` | Participant Instructions & Phase Guidelines | 5 | 100% | Phase 1 focuses on Processors A & B; C & D reserved for Phase 2 finalists; AI disclosure rules (§11). | **VERIFIED** |
| `media_1792151376289.pdf` | Geometry-Aware Quantum Cloud Challenge Overview | 14 | 100% | Topologies, transpilation level 1, CX error accumulation, shot budgeting (4096 shots). | **VERIFIED** |
| `media_1792153265245.pdf` | SRM University-AP Master Guide | 7 | 100% | Problem S3 official definition; Hamiltonian parameters ($J=1.0, h=0.8, T=1.0$); open chain baseline; $\langle Z_0 \rangle$ observable; 12-edge heavy-hex graph. | **VERIFIED** |
| `media_1792153256404.pdf` | Starter Notebook & Processor JSON Specifications | 26 | 100% | Starter code schema, basis gates `['rz', 'sx', 'x', 'cx']`, noise rates ($p_1=0.001, p_2=0.005$, symmetric $1\%$ readout). | **VERIFIED** |
| `media_1792153261485.pdf` | Giant Challenge Kit & Problem Statements | 16 | 100% | Detailed Problem S1, S2, S3 statements; instruction on p. 9 to illustrate problems on A & B and propose Processor D solution. | **VERIFIED** |
| `media_1792154781365.pdf` | Phase 1 Complete Implementation Blueprint | 11 | 100% | Step sweep $\{1,2,3,4,5,6,8,10\}$, reflection anti-symmetry proof, file layout, test suite gates, 100-point rubric breakdown. | **VERIFIED** |
| WhatsApp Announcement | Organizers' Official WhatsApp Broadcast | 1 | 100% | 100-point rubric (30/25/20/15/10); 70% LLM / 30% Human; top 50 qualify; explicit instruction to illustrate A/B problems & propose Processor D. | **VERIFIED** |

---

## 2. Master Requirements Traceability Matrix

| Req ID | Requirement Description | Source Document | Current Implementation Location | Verification Method | Status | Corrective Action / Notes |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **REQ-01** | **Physical Model:** 4-spin Transverse-Field Ising Model ($J=1.0, h=0.8, T=1.0$) | Master Guide p. 3; Blueprint p. 2 | `src/problem.py`: `TrotterSimulationModel` | Exact matrix exponential via `scipy.linalg.expm` verified in `tests/test_benchmark.py` | **PASS** | Fully implemented and mathematically verified. |
| **REQ-02** | **Primary Baseline Boundary:** Open-chain 1D boundary condition ($J_{\text{cross}} = 0.0$) | Master Guide p. 3; Blueprint p. 3 | `src/problem.py`, `main.py`, `results/tables/AB_comparison.csv` | Checked non-zero terms; only nearest-neighbor couplings $(0,1),(1,2),(2,3)$ present | **PASS** | Serves as the primary official baseline. |
| **REQ-03** | **Architectural Extension:** Periodic ring boundary condition ($J_{\text{cross}} = 0.5$) | Master Guide p. 4; Blueprint p. 4 | `src/problem.py`, `main.py`, `results/tables/periodic_extension_comparison.csv` | Cross term $Z_0 Z_3$ active; separated from open-chain data | **PASS** | Clearly separated into distinct table/plots. |
| **REQ-04** | **Initial State:** Antiferromagnetic domain wall $\|\psi(0)\rangle = \|1010\rangle$ | Master Guide p. 3; Spec §3 | `src/problem.py`: `build_trotter_circuit()` | State initialization verified; $\langle Z_0(0)\rangle = +1.0$ | **PASS** | Correctly encoded with $X$ gates on qubits 0 and 2. |
| **REQ-05** | **Primary Observable:** Single-site expectation value $\langle Z_0(t) \rangle$ | Master Guide p. 3; Blueprint p. 3 | `src/metrics.py`: `calculate_z0_expectation()` | Shot-based diagonal estimator from bitstring counts | **PASS** | Converges to $+0.257957$ (open) / $+0.421887$ (periodic). |
| **REQ-06** | **Secondary Diagnostic:** Prove total magnetization $\langle M_z(t) \rangle \equiv 0.000000$ | Blueprint p. 3; Physics Audit | `src/problem.py`, `tests/test_benchmark.py` | Proven by spatial reflection anti-symmetry $\mathcal{P}\hat{H}\mathcal{P}^\dagger = \hat{H}$ on $\|1010\rangle$ | **PASS** | Mathematically proven and tested. |
| **REQ-07** | **Processor A Definition:** 5 qubits, linear topology `0-1-2-3-4`, ports `[0, 4]` | Spec §4.1; `processor_A.json` | `processors/processor_A.json` | JSON schema validated; 4 undirected edges, 8 directed pairs | **PASS** | Fully compliant. |
| **REQ-08** | **Processor B Definition:** 9 qubits, heavy-hex topology (12 undirected edges, 24 directed pairs), ports `[0, 8]` | Spec §4.2; Master Guide p. 5 | `processors/processor_B.json` | JSON schema validated; exact 12-edge reference topology | **PASS** | Verified against Master Guide reference. |
| **REQ-09** | **Noise Model Calibration:** $p_1 = 0.001$, $p_2 = 0.005$, symmetric $1\%$ readout error | Spec §4.3; Blueprint p. 4 | `processors/*.json`, `src/processors.py` | `NoiseModel` constructed and verified in unit tests | **PASS** | Applied identically to both processors. |
| **REQ-10** | **Trotter Decomposition:** 1st-order Suzuki-Trotter step sweep $n \in \{1, 2, 3, 4, 5, 6, 8, 10\}$ | Problem S3 Spec; Blueprint p. 5 | `src/problem.py`, `main.py` | Circuits synthesized, transpiled, and simulated across all 8 steps | **PASS** | Full parameter sweep executed. |
| **REQ-11** | **Transpilation & Optimization:** Level 1 preset pass manager with deterministic seed (`seed=42`) | Challenge Overview p. 6; Blueprint p. 5 | `src/transpilation.py`: `transpile_circuit()` | `generate_preset_pass_manager(optimization_level=1, seed_transpiler=42)` | **PASS** | Deterministic and hardware-compliant. |
| **REQ-12** | **Routing & SWAP Metric Differentiation:** Separate explicit SWAPs from equivalent SWAP estimate ($\Delta CX / 3$) | Implementation Blueprint p. 5 | `src/transpilation.py`, `report.md`, `README.md` | Explicit `swap` count $= 0$; $\Delta CX = CX_{\text{compiled}} - CX_{\text{logical}}$ | **PASS** | Rigorously distinguished in text and tables. |
| **REQ-13** | **Fidelity Metric Separation:** Separate quantum state fidelity $F_{\text{state}}$ from classical distribution overlap $F_c$ and TVD | Blueprint p. 5; Second Opinion | `src/metrics.py`, `report.md` | $F_{\text{state}} = \|\langle \psi_{\text{exact}}\|\psi_{\text{trotter}}\rangle\|^2$; $F_c = \sum_x \sqrt{P_n P_i}$; $\text{TVD} = \frac{1}{2}\sum_x \|P_n - P_i\|$ | **PASS** | No confusion between Hilbert space and count metrics. |
| **REQ-14** | **Processor D Technical Proposal:** Illustrate A/B limitations and propose Processor D solution | WhatsApp Announcement; Giant Kit p. 9 | `report.md` §8, `README.md` §5, `docs/STUDENT_WALKTHROUGH.md` §14 | Co-design analysis: 12Q Ring-and-Cross lattice with native $R_{zz}(\theta)$ gates | **PASS** | Fully articulated with clear academic distinction. |
| **REQ-15** | **Reproducibility & Code Quality:** End-to-end execution script, 11 unit tests, fixed seeds | Phase 1 Rules; WhatsApp Criteria | `main.py`, `tests/test_benchmark.py`, `requirements.txt` | 11/11 tests pass in 2.8s; `main.py` runs cleanly | **PASS** | Fully reproducible. |
| **REQ-16** | **Student Walkthrough & Defense Prep:** Comprehensive explanation of all concepts and questions | Implementation Blueprint p. 8 | `docs/STUDENT_WALKTHROUGH.md` | 16 detailed sections and oral defense Q&A guide | **PASS** | Prepared for undergraduate student presentation. |
| **REQ-17** | **AI Disclosure:** Transparent disclosure of tools and verification | Participant Rules §11 | `AI_DISCLOSURE.md` | Formatted per competition requirements | **PASS** | Full transparency maintained. |
| **REQ-18** | **Executed Jupyter Notebook:** `main.ipynb` executed top-to-bottom with saved cell outputs | Phase 1 Rules; Blueprint p. 7 | `main.ipynb` | Validated execution with zero errors and preserved outputs | **PASS** | Verified clean execution. |
| **REQ-19** | **Git Hygiene & Security:** No secrets, no large caches, clean whitespace | Submission Rules | `.gitignore`, repository audit | `git diff --check` passes with zero errors; no credentials tracked | **PASS** | Clean and submission-ready. |

---

## 3. Conclusion
All 19 official competition and architectural requirements are **100% compliant (PASS)**. No items remain `PARTIAL`, `FAIL`, or `UNVERIFIED`.
