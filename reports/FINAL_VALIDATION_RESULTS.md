# Final Validation Results & Reproducibility Report
## Qiskit Fall Fest 2026 — Phase 1: Problem S3 (Noise in Trotter Simulation)

**Project Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  
**Execution Date:** October 16, 2026  
**Environment:** Windows 11, Python 3.11.9, Qiskit 2.5.2, Qiskit Aer 0.17.2, NumPy 2.4.6, SciPy 1.17.1  

---

## 1. Automated Unit & Regression Test Suite

- **Execution Command:**
  ```bash
  .venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
  ```
- **Execution Output:**
  ```text
  test_algorithmic_state_fidelity_convergence (test_benchmark.TestTrotterBenchmark.test_algorithmic_state_fidelity_convergence)
  Verify that algorithmic pure-state Trotter fidelity monotonically increases with n. ... ok
  test_coupling_maps_and_noise_models (test_benchmark.TestTrotterBenchmark.test_coupling_maps_and_noise_models)
  Verify CouplingMap and NoiseModel generation for both processors. ... ok
  test_exact_magnetization_reflection_symmetry (test_benchmark.TestTrotterBenchmark.test_exact_magnetization_reflection_symmetry)
  Verify exact physical symmetry: spatial reflection symmetry P H P^dagger = H ... ok
  test_independent_numerical_trotter_unitary (test_benchmark.TestTrotterBenchmark.test_independent_numerical_trotter_unitary)
  Independent numerical check: verify circuit unitary matches exp(-i H dt) to O(dt^2). ... ok
  test_noise_model_exact_channels (test_benchmark.TestTrotterBenchmark.test_noise_model_exact_channels)
  Verify noise model applies exactly depolarizing + readout, without unverified thermal relaxation. ... ok
  test_problem_s3_hamiltonian_and_hermiticity (test_benchmark.TestTrotterBenchmark.test_problem_s3_hamiltonian_and_hermiticity)
  Verify Hamiltonian generation, boundary conditions, and Hermiticity. ... ok
  test_processor_configurations (test_benchmark.TestTrotterBenchmark.test_processor_configurations)
  Verify Processor A and B configuration files exist, match official budgets, and have valid schema. ... ok
  test_routing_cx_overhead_and_unrolled_swaps (test_benchmark.TestTrotterBenchmark.test_routing_cx_overhead_and_unrolled_swaps)
  Verify routing overhead: explicit SWAP is 0 due to basis unrolling; Processor B has fewer CX gates than A for periodic extension. ... ok
  test_single_site_z_magnetization (test_benchmark.TestTrotterBenchmark.test_single_site_z_magnetization)
  Validate primary observable <Z_0(t)>: ... ok
  test_statistical_metrics_and_zero_division (test_benchmark.TestTrotterBenchmark.test_statistical_metrics_and_zero_division)
  Verify TVD and Classical Fidelity calculations, including zero-shot edge cases. ... ok
  test_transpilation_and_active_qubits_extraction (test_benchmark.TestTrotterBenchmark.test_transpilation_and_active_qubits_extraction)
  Verify transpilation distinguishes total processor capacity from active physical qubits on 9Q Processor B. ... ok

  ----------------------------------------------------------------------
  Ran 11 tests in 0.323s

  OK
  ```
- **Exit Code:** `0` (ALL 11 TESTS PASSED).

---

## 2. End-to-End Benchmark Pipeline Execution

- **Execution Command:**
  ```bash
  .venv\Scripts\python.exe main.py
  ```
- **Execution Log Highlights:**
  - Loaded Processor A (5-qubit line) and Processor B (9-qubit heavy-hex).
  - Computed exact analytical continuum targets via `scipy.linalg.expm`:
    - Open-chain baseline: $\langle Z_0(1.0) \rangle_{\text{exact}} = 0.257957$, $\langle M_z(1.0) \rangle_{\text{exact}} \equiv 0.000000$.
    - Periodic extension: $\langle Z_0(1.0) \rangle_{\text{exact}} = 0.421887$, $\langle M_z(1.0) \rangle_{\text{exact}} \equiv 0.000000$.
  - Successfully generated coupling topologies:
    - `results/figures/processor_A_graph.png`
    - `results/figures/processor_B_graph.png`
  - Exported all machine-readable CSV tables and raw metadata JSON:
    - `results/tables/processor_A_metrics.csv`
    - `results/tables/processor_B_metrics.csv`
    - `results/tables/AB_comparison.csv`
    - `results/tables/periodic_extension_comparison.csv`
    - `results/tables/combined_benchmark_results.csv`
    - `results/tables/final_comparison.csv`
    - `results/raw/raw_experiment_data.json`
  - Exported all publication figures:
    - `results/figures/logical_vs_transpiled.png`
    - `results/figures/AB_performance.png`
    - `results/figures/architecture_tradeoffs.png`
- **Exit Code:** `0` (SUCCESS).

---

## 3. Git Formatting & Whitespace Verification

- **Execution Command:**
  ```bash
  git diff --check
  ```
- **Output:** Clean (zero trailing whitespace, zero carriage return conflicts, zero EOF errors).
- **Exit Code:** `0`.

---

## 4. First-Principles Numerical Verification Summary

| Physical Quantity | Independent `scipy.linalg.expm` Target | Qiskit Statevector ($n=10$) | Measured Noisy QPU Simulation ($n=4$) | Verification Status |
| :--- | :---: | :---: | :---: | :---: |
| **Open Chain $\langle Z_0(1.0) \rangle$** | $+0.257957$ | $+0.245844$ | $+0.231000$ (Error: $0.0270$) | **VERIFIED** |
| **Open Chain $\langle M_z(1.0) \rangle$** | $0.000000$ | $0.000000$ | $0.000000$ (Zero by anti-symmetry) | **VERIFIED** |
| **Periodic Ring $\langle Z_0(1.0) \rangle$** | $+0.421887$ | $+0.418295$ | $+0.395500$ (Error: $0.0264$) | **VERIFIED** |
| **Periodic Ring $\langle M_z(1.0) \rangle$** | $0.000000$ | $0.000000$ | $0.000000$ (Zero by anti-symmetry) | **VERIFIED** |
| **Pure State Fidelity $F_{\text{state}}(n=4)$** | Analytical | $0.964821$ | N/A (Hilbert space metric) | **VERIFIED** |
| **Pure State Fidelity $F_{\text{state}}(n=10)$** | Analytical | $0.994914$ | N/A (Hilbert space metric) | **VERIFIED** |
| **Classical Overlap $F_c(n=4)$** | Analytical | $1.000000$ | $0.994928$ (Degraded by noise) | **VERIFIED** |
| **Classical Overlap $F_c(n=10)$** | Analytical | $1.000000$ | $0.984183$ (Noise outpaces refinement) | **VERIFIED** |

---

## 5. Identified Known Limitations

1. **Synthetic Depolarizing Noise:** The project simulates Pauli depolarizing noise and symmetric bit-flip readout errors using Qiskit Aer. Real physical devices incur coherent phase drift, $T_1/T_2$ relaxation, and non-Markovian crosstalk.
2. **Deterministic Random Seed:** Experiments were conducted with `seed=42` to guarantee exact reproducibility for competition judges. Multi-seed Monte Carlo distributions can be added for deeper statistical bounds in Phase 2.
3. **Implicit SWAP Decomposition:** Compiler unrolling translates SWAP gates into $3 \times CX$. Explicit `swap` opcodes equal zero; SWAP counts are mathematically estimated via $\lfloor \Delta CX / 3 \rfloor$.
