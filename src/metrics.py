"""
Problem and architecture performance metrics evaluation.
Provides mathematically rigorous definitions for:
- Quantum State Fidelity (pure statevector overlap in Hilbert space)
- Single-Site Observable Expectation Values <Z_site> & Standard Error (Primary Observable)
- Physical Total Magnetization <M_z> (Secondary Symmetry Diagnostic)
- Classical Measurement Distribution Similarity (Bhattacharyya coefficient F_c)
- Total Variation Distance (TVD)
"""

import math
from typing import Dict, Any, List, Tuple
import numpy as np
from qiskit.quantum_info import state_fidelity, Statevector, DensityMatrix


def compute_quantum_state_fidelity(
    state_a: Statevector | DensityMatrix,
    state_b: Statevector | DensityMatrix
) -> float:
    """
    Compute true Quantum State Fidelity between two quantum states in Hilbert space:
    F(rho, sigma) = (Tr[ sqrt( sqrt(rho) sigma sqrt(rho) ) ])^2
    For pure states: F(|psi>, |phi>) = |<psi|phi>|^2.
    """
    return float(state_fidelity(state_a, state_b))


def compute_single_site_z_from_counts(
    counts: Dict[str, int],
    num_spins: int,
    site: int = 0
) -> Tuple[float, float]:
    """
    Compute single-site expectation value <Z_site> and shot standard error from bitstring counts.
    In Qiskit's bitstring convention ('b_{N-1}...b_1 b_0'), bit 'b_site' is indexed from the right.
    Eigenvalues of Pauli Z: '0' -> +1, '1' -> -1.

    Returns:
        (mean_z_site, standard_error)
    """
    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0, 0.0

    if site < 0 or site >= num_spins:
        raise ValueError(f"Site index {site} out of bounds for {num_spins} spins.")

    # Target index from right: site 0 is index -1, site 1 is index -2, etc.
    char_index = -(site + 1)

    z_values = []
    for bitstr, cnt in counts.items():
        clean_str = bitstr.replace(" ", "")
        bit_char = clean_str[char_index]
        z_val = 1.0 if bit_char == "0" else -1.0
        z_values.extend([z_val] * cnt)

    mean_val = float(np.mean(z_values))
    std_val = float(np.std(z_values, ddof=1)) if len(z_values) > 1 else 0.0
    se = float(std_val / math.sqrt(total_shots))
    return mean_val, se


def compute_magnetization_from_counts(
    counts: Dict[str, int],
    num_spins: int
) -> Tuple[float, float]:
    """
    Compute average Z-magnetization <M_z> = (1/N) * sum_i <Z_i> from bitstring counts.
    Returns:
        (mean_magnetization, standard_error)
    """
    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0, 0.0

    m_values = []
    for bitstr, cnt in counts.items():
        clean_str = bitstr.replace(" ", "")
        # Spin Z eigenvalue: '0' -> +1, '1' -> -1
        z_vals = [1.0 if char == "0" else -1.0 for char in clean_str[-num_spins:]]
        avg_z = np.mean(z_vals)
        m_values.extend([avg_z] * cnt)

    mean_val = float(np.mean(m_values))
    std_val = float(np.std(m_values, ddof=1)) if len(m_values) > 1 else 0.0
    se = float(std_val / math.sqrt(total_shots))
    return mean_val, se


def compute_tvd(counts_p: Dict[str, int], counts_q: Dict[str, int]) -> float:
    """
    Compute Total Variation Distance between two empirical probability distributions:
    TVD(P, Q) = 0.5 * sum_x |P(x) - Q(x)|
    Bounded in [0, 1].
    """
    shots_p = sum(counts_p.values())
    shots_q = sum(counts_q.values())
    if shots_p == 0 or shots_q == 0:
        return 1.0

    all_keys = set(counts_p.keys()) | set(counts_q.keys())
    tvd = 0.0
    for k in all_keys:
        prob_p = counts_p.get(k, 0) / shots_p
        prob_q = counts_q.get(k, 0) / shots_q
        tvd += abs(prob_p - prob_q)
    return float(0.5 * tvd)


def compute_classical_distribution_fidelity(
    counts_noisy: Dict[str, int],
    counts_ideal: Dict[str, int]
) -> float:
    """
    Compute Classical Distribution Fidelity (Bhattacharyya coefficient):
    F_c(P, Q) = sum_x sqrt(P(x) * Q(x))
    NOTE: This is a classical distribution overlap metric for measurement outcomes,
    NOT quantum state fidelity |<psi|phi>|^2.
    """
    shots_n = sum(counts_noisy.values())
    shots_i = sum(counts_ideal.values())
    if shots_n == 0 or shots_i == 0:
        return 0.0

    all_keys = set(counts_noisy.keys()) | set(counts_ideal.keys())
    bc = 0.0
    for k in all_keys:
        p_n = counts_noisy.get(k, 0) / shots_n
        p_i = counts_ideal.get(k, 0) / shots_i
        bc += math.sqrt(p_n * p_i)
    return float(bc)


def compute_classical_fidelity(
    counts_noisy: Dict[str, int],
    counts_ideal: Dict[str, int]
) -> float:
    """Backward-compatible alias for compute_classical_distribution_fidelity."""
    return compute_classical_distribution_fidelity(counts_noisy, counts_ideal)


def compute_proportion_error(p: float, shots: int) -> float:
    """Standard error for a proportion: sqrt(p * (1 - p) / N)."""
    if shots <= 0:
        return 0.0
    p_clamped = max(0.0, min(1.0, p))
    return float(math.sqrt(p_clamped * (1.0 - p_clamped) / shots))
