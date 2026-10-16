# Benchmark Results & Output Data Audit

**Project:** Qiskit Fall Fest 2026 — Phase 1 (Problem S3)  
**Document:** `reports/BENCHMARK_AND_RESULTS_AUDIT.md`  

---

## 1. Existing Generated Data Inventory & Provenance

The repository contains a complete set of generated benchmark tables, raw simulation dumps, and figures:

| File Path | Description | Generated Under | Current Validity |
| :--- | :--- | :--- | :---: |
| [`results/tables/processor_A_metrics.csv`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/tables/processor_A_metrics.csv) | Processor A step-by-step metrics ($n \in \{1 \dots 10\}$) | 5Q Line, $p_2=0.01$ | **Valid for 5Q Line, but $p_2$ needs update to 0.005** |
| [`results/tables/processor_B_metrics.csv`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/tables/processor_B_metrics.csv) | Processor B step-by-step metrics ($n \in \{1 \dots 10\}$) | **7Q Heavy-Hex, $p_2=0.01$** | **Superseded by 9Q Master Guide requirement** |
| [`results/tables/AB_comparison.csv`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/tables/AB_comparison.csv) | Side-by-side comparative table | 5Q Line vs. 7Q Heavy-Hex | **Superseded** |
| [`results/tables/final_comparison.csv`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/tables/final_comparison.csv) | Executive summary comparison table | 5Q Line vs. 7Q Heavy-Hex | **Superseded** |
| [`results/raw/raw_experiment_data.json`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/raw/raw_experiment_data.json) | Complete JSON count dictionaries and metric dumps | 5Q Line vs. 7Q Heavy-Hex | **Superseded** |
| [`results/figures/processor_A_graph.png`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/processor_A_graph.png) | Topology diagram for Processor A | 5Q Line | **Valid** |
| [`results/figures/processor_B_graph.png`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/processor_B_graph.png) | Topology diagram for Processor B | 7Q Heavy-Hex | **Superseded (Must depict 9Q graph)** |
| [`results/figures/logical_vs_transpiled.png`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/logical_vs_transpiled.png) | Depth and CX scaling curves | 5Q Line vs. 7Q Heavy-Hex | **Superseded** |
| [`results/figures/AB_performance.png`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/AB_performance.png) | Fidelity decay trade-off plot | 5Q Line vs. 7Q Heavy-Hex | **Superseded** |
| [`results/figures/architecture_tradeoffs.png`](file:///c:/Users/LOKESH/quiskit%20phase%201/results/figures/architecture_tradeoffs.png) | 4-panel comprehensive dashboard | 5Q Line vs. 7Q Heavy-Hex | **Superseded** |

---

## 2. Mathematical Verification of Existing Reported Numbers

Every key number reported in the README and reports was audited against the raw JSON dump (`results/raw/raw_experiment_data.json`):

### 2.1 Circuit Depth & Gate Counts ($n = 4$)
- **Logical Circuit:** Depth $= 33$, Two-Qubit CX gates $= 32$.
- **Processor A (5Q Line):**
  - Total Depth $= 111$.
  - Two-Qubit Depth $= 53$.
  - Two-Qubit CX Gates $= 74$.
  - Routing CX Overhead $= 74 - 32 = 42$.
  - Equivalent SWAPs $= 42 / 3 = 14$.
- **Processor B (7Q Heavy-Hex):**
  - Total Depth $= 111$.
  - Two-Qubit Depth $= 53$.
  - Two-Qubit CX Gates $= 53$.
  - Routing CX Overhead $= 53 - 32 = 21$.
  - Equivalent SWAPs $= 21 / 3 = 7$.
- **Delta (B - A):** Saves $21$ CX gates ($-28.4\%$) and $7$ equivalent SWAPs ($-50.0\%$).
- **Mathematical Integrity:** **VERIFIED.** The numbers are internally consistent, derived from real transpilation, and fully reproduced by unit tests.

### 2.2 Fidelity and TVD Values ($n = 4$)
- **Pure Trotter State Fidelity ($F_{\text{state}}$):** $0.9488$ (pure mathematical discretization).
- **Processor A Classical Distribution Fidelity ($F_c$):** $0.9577$.
- **Processor B Classical Distribution Fidelity ($F_c$):** $0.9653$ ($+0.0076$ higher than A).
- **Processor A Total Variation Distance (TVD):** $0.1992$.
- **Processor B Total Variation Distance (TVD):** $0.1697$ ($-0.0295$ lower distortion on B).
- **Mathematical Integrity:** **VERIFIED.** Derived directly from shot distributions (4096 shots, seed 42).

---

## 3. Why Existing Results Must Be Re-run Post-Approval

While the existing results are mathematically authentic and reproducible under the previous configuration, they represent an earlier iteration of the project:
1. They reflect the **7-qubit Processor B** instead of the **9-qubit Master Guide baseline**.
2. They reflect a **$1.0\%$ CX depolarizing rate** instead of the **$0.5\%$ Master Guide rate**.
3. They reflect **asymmetric readout confusion** instead of **symmetric $1.0\%$ readout error**.
4. They evaluate **total magnetization $\langle M_z \rangle$** (which is identically zero by reflection anti-symmetry) rather than **single-site magnetization $\langle Z_0(t) \rangle$**.

When implementation begins, re-running the benchmark under the 9-qubit Master Guide parameters will generate clean, authoritative results while preserving all original data as a documented historical stage.
