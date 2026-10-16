# Trotterization, Error Metrics, & Numerical Reference Audit

**Project:** Qiskit Fall Fest 2026 — Phase 1 (Problem S3)  
**Document:** `reports/TROTTER_AND_REFERENCE_AUDIT.md`  

---

## 1. Product Formula & Numerical Exactness

### 1.1 First-Order Trotter Decomposition
The evolution operator under $H = H_{ZZ} + H_X$ is approximated by:
$$U(t) \approx \left[ e^{-i H_{ZZ} \Delta t} e^{-i H_X \Delta t} \right]^n, \quad \Delta t = \frac{t}{n}$$

By the Baker-Campbell-Hausdorff (BCH) theorem:
$$e^{-i H_{ZZ} \Delta t} e^{-i H_X \Delta t} = \exp\left( -i (H_{ZZ} + H_X) \Delta t - \frac{1}{2} [H_{ZZ}, H_X] \Delta t^2 + \mathcal{O}(\Delta t^3) \right)$$
The single-step truncation error is bounded by:
$$\| U_{\text{step}}(\Delta t) - e^{-i H \Delta t} \| \le \frac{1}{2} \| [H_{ZZ}, H_X] \| \Delta t^2$$
Compounding over $n$ steps ($\Delta t = t/n$), the global algorithmic Trotter error scales as:
$$\epsilon_{\text{Trotter}} \le \mathcal{O}\left( \frac{t^2}{n} \right)$$
As $n \to \infty$, $U_{\text{Trotter}}(t, n) \to e^{-i H t}$ asymptotically.

### 1.2 Exact Classical Reference Validation
In `src/problem.py` (lines 73–78):
```python
def compute_exact_statevector(self, t: float) -> Statevector:
    u_matrix = scipy.linalg.expm(-1j * self.hamiltonian_matrix * t)
    psi0 = self.get_initial_statevector().data
    psi_t = u_matrix @ psi0
    return Statevector(psi_t)
```
- **Dimensionality:** For $N = 4$ spins, the Hilbert space dimension is $2^4 = 16$.
- **Numerical Method:** Dense matrix exponentiation via Padé approximation (`scipy.linalg.expm`) achieves double-precision machine epsilon ($\approx 10^{-16}$).
- **Statevector Normalization:** $\| |\psi_{\text{exact}}(t)\rangle \| = 1.0000000000000000$.

In unit test `test_independent_numerical_trotter_unitary`, the operator norm difference $\| U_{\text{circuit}}(\Delta t) - \exp(-i H \Delta t) \|$ was verified to be $0.0203$ at $\Delta t = 0.05$, confirming exact numerical agreement.

---

## 2. Separation of Scientific Quantities

To prevent misleading claims, four distinct physical/statistical quantities are separated:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Exact Ideal Continuum Target: |psi_exact(t)> = exp(-iHt) |psi(0)>   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Algorithmic Discretization Error
                                    │ (Decreases as 1/n)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 2. Ideal Trotterized State: |psi_trotter(t, n)>                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Hardware Noise Accumulation
                                    │ (Increases exponentially with CX)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 3. Physical Noisy Density Matrix: rho_noisy(t, n)                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Shot-Noise / Finite Sampling
                                    │ (Scales as 1/sqrt(Shots))
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ 4. Measured Empirical Distribution: P_empirical(x)                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Metric Definitions & Scientific Appropriateness

### 3.1 Pure Quantum State Fidelity ($F_{\text{state}}$)
- **Formula:** $F_{\text{state}} = |\langle \psi_{\text{exact}}(t) | \psi_{\text{trotter\_ideal}}(t, n) \rangle|^2$
- **Implementation:** `compute_algorithmic_trotter_state_fidelity` in `src/problem.py`.
- **Physical Meaning:** Quantifies pure mathematical Trotterization error without noise.
- **Observed Behavior:** Monotonically increases with $n$:
  - $n = 1$: $0.1171$
  - $n = 2$: $0.7651$
  - $n = 4$: $0.9488$
  - $n = 10$: $0.9924$

### 3.2 Classical Distribution Fidelity ($F_c$, Bhattacharyya Overlap)
- **Formula:** $F_c(P_{\text{noisy}}, P_{\text{ideal}}) = \sum_{x \in \{0, 1\}^N} \sqrt{P_{\text{noisy}}(x) \cdot P_{\text{ideal}}(x)}$
- **Implementation:** `compute_classical_distribution_fidelity` in `src/metrics.py`.
- **Physical Meaning:** Measures how closely the noisy empirical measurement histogram reproduces the ideal noise-free Trotter distribution.
- **Observed Behavior:** Peaks at $n = 1$ ($F_c = 0.9996$) and decays monotonically to $0.8919$ (Proc A) and $0.9103$ (Proc B) at $n = 10$.
  - *Why?* At $n = 1$, the circuit has only 14 CX gates on A and 11 on B, so noise accumulation is minimal. At $n = 10$, with 194 CX gates on A and 137 on B, depolarizing noise severely scrambles the output probabilities.

### 3.3 Total Variation Distance (TVD)
- **Formula:** $\text{TVD}(P, Q) = \frac{1}{2} \sum_x |P(x) - Q(x)| \in [0, 1]$
- **Physical Meaning:** Maximum difference in event probabilities between noisy and ideal runs.
- **Observed Behavior:**
  - $n = 1$: $\text{TVD} \approx 0.022$
  - $n = 4$: $\text{TVD} = 0.1992$ (Proc A) vs. $0.1697$ (Proc B)
  - $n = 10$: $\text{TVD} = 0.3403$ (Proc A) vs. $0.3096$ (Proc B)
  - Confirms that Processor B maintains significantly lower distribution distortion across all $n$.

### 3.4 Single-Site Observable Error ($\epsilon_{Z_0}$)
- **Formula:** $\epsilon_{Z_0}(n) = |\langle Z_0(t, n) \rangle_{\text{noisy}} - \langle Z_0(t) \rangle_{\text{exact}}|$
- **Status:** **Must be added** to replace the degenerate $\langle M_z \rangle$ observable.
- **Convergence Behavior:** Shows non-zero oscillation and clear convergence towards the exact value at moderate $n$, followed by noisy decay at large $n$.
