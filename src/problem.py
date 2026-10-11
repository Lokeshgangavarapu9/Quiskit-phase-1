"""
Problem S3: Noise in Trotter Simulation
Hamiltonian formulation, exact statevector dynamics, and Trotterized circuit construction.
"""

import numpy as np
import scipy.linalg
from typing import List, Tuple, Dict, Any, Optional

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import Statevector, SparsePauliOp


class TrotterSimulationModel:
    """
    1D Spin Chain Simulation under Transverse-Field Ising Model (TFIM):
    H = - J * sum_{i} Z_i Z_{i+1} - J_cross * Z_0 Z_{N-1} - h * sum_i X_i
    """

    def __init__(
        self,
        num_spins: int = 4,
        J: float = 1.0,
        h: float = 0.8,
        J_cross: float = 0.5,
        initial_state_str: str = "1010"
    ):
        self.num_spins = num_spins
        self.J = J
        self.h = h
        self.J_cross = J_cross
        self.initial_state_str = initial_state_str

        # Build Pauli operator representation
        self.hamiltonian_op = self._build_hamiltonian_pauli()
        self.hamiltonian_matrix = self.hamiltonian_op.to_matrix()

    def _build_hamiltonian_pauli(self) -> SparsePauliOp:
        pauli_list = []
        # Nearest-neighbor ZZ terms
        for i in range(self.num_spins - 1):
            z_term = ["I"] * self.num_spins
            z_term[i] = "Z"
            z_term[i + 1] = "Z"
            pauli_list.append(("".join(reversed(z_term)), -self.J))

        # Cross coupling (boundary condition forcing non-local routing)
        if self.J_cross != 0.0 and self.num_spins > 2:
            z_cross = ["I"] * self.num_spins
            z_cross[0] = "Z"
            z_cross[self.num_spins - 1] = "Z"
            pauli_list.append(("".join(reversed(z_cross)), -self.J_cross))

        # Transverse X magnetic field terms
        for i in range(self.num_spins):
            x_term = ["I"] * self.num_spins
            x_term[i] = "X"
            pauli_list.append(("".join(reversed(x_term)), -self.h))

        return SparsePauliOp.from_list(pauli_list)

    def get_initial_statevector(self) -> Statevector:
        """Construct initial statevector from initial_state_str."""
        return Statevector.from_label(self.initial_state_str)

    def compute_exact_statevector(self, t: float) -> Statevector:
        """Exact unitary evolution |psi(t)> = exp(-i H t) |psi(0)>."""
        u_matrix = scipy.linalg.expm(-1j * self.hamiltonian_matrix * t)
        psi0 = self.get_initial_statevector().data
        psi_t = u_matrix @ psi0
        return Statevector(psi_t)

    def compute_exact_magnetization(self, t: float) -> float:
        """Compute exact expectation value <M_z(t)> = 1/N sum_i <Z_i(t)>."""
        psi_t = self.compute_exact_statevector(t)
        total_z = 0.0
        for i in range(self.num_spins):
            z_term = ["I"] * self.num_spins
            z_term[i] = "Z"
            op = SparsePauliOp.from_list([("".join(reversed(z_term)), 1.0)])
            val = psi_t.expectation_value(op).real
            total_z += val
        return float(total_z / self.num_spins)

    def build_trotter_circuit(
        self,
        t: float,
        num_steps: int,
        measure: bool = True
    ) -> QuantumCircuit:
        """
        Build first-order Suzuki-Trotter circuit for duration t with num_steps:
        U(t) ~= [ U_ZZ(dt) * U_X(dt) ]^num_steps, where dt = t / num_steps.
        """
        if num_steps <= 0:
            raise ValueError("num_steps must be >= 1")

        dt = t / num_steps
        qc = QuantumCircuit(self.num_spins, self.num_spins if measure else 0)

        # State preparation
        # initial_state_str is ordered q_{N-1}...q_0
        for idx, char in enumerate(reversed(self.initial_state_str)):
            if char == "1":
                qc.x(idx)

        # Trotter steps
        for step in range(num_steps):
            # Nearest-neighbor ZZ interactions
            for i in range(self.num_spins - 1):
                # exp(-i (-J) dt Z_i Z_{i+1}) -> RZZ(-2 * J * dt)
                qc.cx(i, i + 1)
                qc.rz(-2.0 * self.J * dt, i + 1)
                qc.cx(i, i + 1)

            # Cross-boundary ZZ interaction
            if self.J_cross != 0.0 and self.num_spins > 2:
                qc.cx(0, self.num_spins - 1)
                qc.rz(-2.0 * self.J_cross * dt, self.num_spins - 1)
                qc.cx(0, self.num_spins - 1)

            # Single-qubit X transverse field rotations
            for i in range(self.num_spins):
                # exp(-i (-h) dt X_i) -> RX(-2 * h * dt)
                qc.rx(-2.0 * self.h * dt, i)

        if measure:
            qc.measure(range(self.num_spins), range(self.num_spins))

        return qc
