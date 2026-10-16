# Quantum Noise Model & Qiskit Aer Implementation Audit

**Project:** Qiskit Fall Fest 2026 — Phase 1 (Problem S3)  
**Document:** `reports/NOISE_MODEL_AUDIT.md`  

---

## 1. Noise Parameter Traceability & Discrepancies

| Parameter | Official Master Guide (Authoritative) | Current Repository (`src/processors.py`) | Status | Impact / Finding |
| :--- | :--- | :--- | :---: | :--- |
| **1-Qubit Depolarizing ($p_1$)** | $0.1\%$ ($p_1 = 0.001$) on `x`, `sx` | $p_1 = 0.001$ on `x`, `sx` | **PASS** | Exact match. Correctly attached to single-qubit basis gates. |
| **2-Qubit Depolarizing ($p_2$)** | **$0.5\%$ ($p_2 = 0.005$) on `cx`** | **$1.0\%$ ($p_2 = 0.010$) on `cx`** | **DEFECT** | Repo value is $2\times$ higher than Master Guide. Accelerates noise decay prematurely. |
| **Readout Error Matrix** | **Symmetric $1.0\%$ ($p = 0.01$)** | Asymmetric: $[[0.99, 0.01], [0.02, 0.98]]$ | **DEFECT** | Asymmetric matrix induces artificial positive spin bias into empirical measurements. |
| **Thermal Relaxation ($T_1, T_2$)** | Excluded | Excluded | **PASS** | Correctly omitted to avoid fabricating unverified calibration data. |

---

## 2. Origin of the Parameter Mismatch

Investigation of the provided materials reveals why the repository currently uses $p_2 = 0.01$ and asymmetric readout:
1. In the **`Processor A/B Benchmark Configuration` (PDF 1, Section 1)**, the organizers noted:
   > *"Different challenge materials contain different example CX-noise values (approximately 0.5% in the executive summary and p=0.005 in one detailed problem statement, while the Starter Guide's illustrative code uses p=0.01)."*
2. The student initially copied the illustrative snippet from page 13 of the early Starter Guide ($p_2 = 0.01$, asymmetric readout matrix $[[0.99, 0.01], [0.02, 0.98]]$).
3. The final **`Phase 1 Master Guide (SRM University-AP)` (PDF 5, Page 2)** explicitly resolved this ambiguity by establishing:
   - **2-qubit CX depolarizing: 0.5% (p = 0.005)**
   - **Readout error: 1.0% (p = 0.01)**

**Conclusion:** The repository implementation must be updated to $p_2 = 0.005$ and symmetric $1.0\%$ readout error to comply with the authoritative SRM AP Master Guide.

---

## 3. Mathematical Noise Model Implementation in Qiskit Aer

In `src/processors.py` (lines 40–58):
```python
# 1-qubit depolarizing error on ['x', 'sx']
error_1q = depolarizing_error(p1, 1)
noise_model.add_all_qubit_quantum_error(error_1q, ["x", "sx"])

# 2-qubit depolarizing error on ['cx']
error_2q = depolarizing_error(p2, 2)
noise_model.add_all_qubit_quantum_error(error_2q, ["cx"])

# Readout error
ro_error = ReadoutError(ro_matrix)
noise_model.add_all_qubit_readout_error(ro_error)
```

### 3.1 Basis Gate Attachment Verification
1. **Virtual vs. Physical Gates:** In Qiskit's `{rz, sx, x, cx}` basis, $R_Z$ rotations are executed virtually in software via frame changes (zero duration, zero error). Noise is applied exclusively to physical microwave pulses (`x`, `sx`) and two-qubit entangling gates (`cx`). This is physically realistic for superconducting transmon processors.
2. **Post-Transpilation Execution:** Because the circuit is transpiled into the basis gates before entering `AerSimulator`, every gate in the transpiled circuit receives the appropriate noise channel.

### 3.2 Impact of Symmetric Readout Error
Under the current asymmetric readout error matrix:
$$\mathbf{M}_{\text{readout}} = \begin{pmatrix} 1 - \epsilon_{0\to 1} & \epsilon_{0\to 1} \\ \epsilon_{1\to 0} & 1 - \epsilon_{1\to 0} \end{pmatrix} = \begin{pmatrix} 0.99 & 0.01 \\ 0.02 & 0.98 \end{pmatrix}$$
Here, $\epsilon_{1\to 0} = 0.02$ is twice as large as $\epsilon_{0\to 1} = 0.01$. This models classical thermal relaxation during measurement, but it creates a net positive spin polarization ($\langle Z \rangle > 0$).

When corrected to the Master Guide's symmetric $1.0\%$ specification:
$$\mathbf{M}_{\text{readout}} = \begin{pmatrix} 0.99 & 0.01 \\ 0.01 & 0.99 \end{pmatrix}$$
the measurement confusion is completely unbiased, preserving the true physical symmetries of the underlying quantum state.
