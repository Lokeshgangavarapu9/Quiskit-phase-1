"""
Problem and architecture performance metrics evaluation.
"""

import math
from typing import Dict, Any, List, Tuple
import numpy as np


def compute_magnetization_from_counts(counts: Dict[str, int], num_spins: int) -> Tuple[float, float]:
    """
    Compute average Z-magnetization <M_z> = (1/N) * sum_i <Z_i> from bitstring counts.
    Returns:
        (mean_magnetization, standard_error)
    """
    total_shots = sum(counts.values())
    if total_shots == 0:
        return 0.0, 0.0

    # Magnetization for each bitstring
    # Qiskit bitstring convention: 'b_{N-1}...b_0'
    m_values = []
    for bitstr, cnt in counts.items():
        # Spin Z value: '0' -> +1, '1' -> -1
        # Strip potential spaces
        clean_str = bitstr.replace(" ", "")
        z_vals = [1.0 if char == "0" else -1.0 for char in clean_str[-num_spins:]]
        avg_z = np.mean(z_vals)
        m_values.extend([avg_z] * cnt)

    mean_val = float(np.mean(m_values))
    std_val = float(np.std(m_values, ddof=1)) if len(m_values) > 1 else 0.0
    se = float(std_val / math.sqrt(total_shots))
    return mean_val, se


def compute_tvd(counts_p: Dict[str, int], counts_q: Dict[str, int]) -> float:
    """
    Compute Total Variation Distance between two count distributions:
    TVD(P, Q) = 0.5 * sum_x |P(x) - Q(x)|
    """
    shots_p = sum(counts_p.values())
    shots_q = sum(counts_q.values())
    all_keys = set(counts_p.keys()) | set(counts_q.keys())

    tvd = 0.0
    for k in all_keys:
        prob_p = counts_p.get(k, 0) / shots_p
        prob_q = counts_q.get(k, 0) / shots_q
        tvd += abs(prob_p - prob_q)
    return float(0.5 * tvd)


def compute_classical_fidelity(counts_noisy: Dict[str, int], counts_ideal: Dict[str, int]) -> float:
    """
    Compute Bhattacharyya / Classical Fidelity between noisy and ideal probability distributions:
    F_c(P, Q) = sum_x sqrt(P(x) * Q(x))
    """
    shots_n = sum(counts_noisy.values())
    shots_i = sum(counts_ideal.values())
    all_keys = set(counts_noisy.keys()) | set(counts_ideal.keys())

    bc = 0.0
    for k in all_keys:
        p_n = counts_noisy.get(k, 0) / shots_n
        p_i = counts_ideal.get(k, 0) / shots_i
        bc += math.sqrt(p_n * p_i)
    return float(bc)


def compute_proportion_error(p: float, shots: int) -> float:
    """Standard error for a proportion: sqrt(p * (1 - p) / N)."""
    p_clamped = max(0.0, min(1.0, p))
    return float(math.sqrt(p_clamped * (1.0 - p_clamped) / shots))
