"""
Unit and integration test suite for Qiskit Fall Fest 2026 Phase 1 (Problem S3).
Includes independent numerical physics checks, metric edge-case handling,
and architectural capacity verification.
"""

import unittest
from pathlib import Path
import numpy as np
import scipy.linalg

from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator, Statevector

from src.processors import (
    load_processor_config,
    build_coupling_map,
    build_noise_model
)
from src.problem import TrotterSimulationModel
from src.transpilation import compile_for_processor, extract_circuit_metrics
from src.metrics import (
    compute_magnetization_from_counts,
    compute_tvd,
    compute_classical_distribution_fidelity,
    compute_quantum_state_fidelity,
    compute_proportion_error
)


class TestTrotterBenchmark(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_dir = Path(__file__).resolve().parent.parent
        cls.proc_a_file = cls.base_dir / "processors" / "processor_A.json"
        cls.proc_b_file = cls.base_dir / "processors" / "processor_B.json"

    def test_processor_configurations(self):
        """Verify Processor A and B configuration files exist and have valid structure."""
        cfg_a = load_processor_config(self.proc_a_file)
        self.assertEqual(cfg_a["num_qubits"], 5)
        self.assertIn("coupling_map", cfg_a)
        self.assertIn("cx", cfg_a["basis_gates"])

        cfg_b = load_processor_config(self.proc_b_file)
        self.assertEqual(cfg_b["num_qubits"], 7)
        self.assertIn("coupling_map", cfg_b)
        self.assertIn("cx", cfg_b["basis_gates"])

    def test_coupling_maps_and_noise_models(self):
        """Verify CouplingMap and NoiseModel generation."""
        cfg_a = load_processor_config(self.proc_a_file)
        cmap_a = build_coupling_map(cfg_a)
        self.assertEqual(cmap_a.size(), cfg_a["num_qubits"])

        noise_a = build_noise_model(cfg_a)
        self.assertGreater(len(noise_a.noise_instructions), 0)

        cfg_b = load_processor_config(self.proc_b_file)
        cmap_b = build_coupling_map(cfg_b)
        self.assertEqual(cmap_b.size(), cfg_b["num_qubits"])

    def test_problem_s3_hamiltonian_and_hermiticity(self):
        """Verify Hamiltonian generation and Hermiticity."""
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5)
        self.assertEqual(model.hamiltonian_matrix.shape, (16, 16))

        # Check Hermiticity H == H^\dagger
        h_mat = model.hamiltonian_matrix
        self.assertTrue(np.allclose(h_mat, h_mat.conj().T))

        # Initial state magnetization for |1010>
        mag_t0 = model.compute_exact_magnetization(0.0)
        self.assertAlmostEqual(mag_t0, 0.0, places=5)

    def test_independent_numerical_trotter_unitary(self):
        """Independent numerical check: verify circuit unitary matches exp(-i H dt) to O(dt^2)."""
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5)
        dt = 0.05

        # Build one Trotter step circuit without state prep X gates
        qc = QuantumCircuit(4)
        for i in range(3):
            qc.cx(i, i + 1)
            qc.rz(-2.0 * model.J * dt, i + 1)
            qc.cx(i, i + 1)
        if model.J_cross != 0.0:
            qc.cx(0, 3)
            qc.rz(-2.0 * model.J_cross * dt, 3)
            qc.cx(0, 3)
        for i in range(4):
            qc.rx(-2.0 * model.h * dt, i)

        op_qc = Operator(qc).data
        u_exact = scipy.linalg.expm(-1j * model.hamiltonian_matrix * dt)

        # Difference must be bounded by first-order Trotter error O(dt^2)
        diff = np.linalg.norm(op_qc - u_exact)
        self.assertLess(diff, 0.05)

    def test_algorithmic_state_fidelity_convergence(self):
        """Verify that algorithmic pure-state Trotter fidelity monotonically increases with n."""
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5)
        fid_1 = model.compute_algorithmic_trotter_state_fidelity(t=1.0, num_steps=1)
        fid_2 = model.compute_algorithmic_trotter_state_fidelity(t=1.0, num_steps=2)
        fid_4 = model.compute_algorithmic_trotter_state_fidelity(t=1.0, num_steps=4)
        fid_8 = model.compute_algorithmic_trotter_state_fidelity(t=1.0, num_steps=8)

        self.assertGreater(fid_2, fid_1)
        self.assertGreater(fid_4, fid_2)
        self.assertGreater(fid_8, fid_4)
        self.assertGreater(fid_8, 0.98)

    def test_transpilation_and_active_qubits_extraction(self):
        """Verify transpilation distinguishes total processor capacity from active physical qubits."""
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5)
        qc = model.build_trotter_circuit(t=1.0, num_steps=1, measure=True)

        cfg_b = load_processor_config(self.proc_b_file)
        cmap_b = build_coupling_map(cfg_b)
        compiled_b, metrics_b = compile_for_processor(qc, cmap_b, basis_gates=cfg_b["basis_gates"])

        # Processor B has 7 qubits total, but logical circuit uses 4 active qubits
        self.assertEqual(metrics_b["total_processor_qubits"], 7)
        self.assertEqual(metrics_b["active_physical_qubits"], 4)
        self.assertGreater(metrics_b["depth"], 0)
        self.assertGreater(metrics_b["two_qubit_ops"], 0)

    def test_noise_model_exact_channels(self):
        """Verify noise model applies exactly depolarizing + readout, without unverified thermal relaxation."""
        cfg_a = load_processor_config(self.proc_a_file)
        noise_a = build_noise_model(cfg_a)
        
        # Check instruction names in noise model
        noisy_ops = set(noise_a._default_quantum_errors.keys())
        self.assertIn("cx", noisy_ops)
        self.assertTrue("x" in noisy_ops or "sx" in noisy_ops)
        # Verify no thermal relaxation instructions or parameters
        self.assertNotIn("thermal_relaxation", [str(inst) for inst in noise_a.noise_instructions])

    def test_exact_magnetization_reflection_symmetry(self):
        """
        Verify exact physical symmetry: spatial reflection symmetry P H P^\dagger = H
        acting on staggered initial state |1010> implies <Z_0(t)> = -<Z_3(t)>
        and <Z_1(t)> = -<Z_2(t)>, ensuring exact total magnetization is identically zero for all t.
        """
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5, initial_state_str="1010")
        for t in [0.0, 0.5, 1.0]:
            psi_t = model.compute_exact_statevector(t)
            z_expectations = []
            for i in range(4):
                z_term = ["I"] * 4
                z_term[i] = "Z"
                from qiskit.quantum_info import SparsePauliOp
                op = SparsePauliOp.from_list([("".join(reversed(z_term)), 1.0)])
                z_expectations.append(psi_t.expectation_value(op).real)

            # Pairwise anti-symmetry check
            self.assertAlmostEqual(z_expectations[0], -z_expectations[3], places=6)
            self.assertAlmostEqual(z_expectations[1], -z_expectations[2], places=6)

            # Total magnetization must equal zero
            mag_exact = model.compute_exact_magnetization(t)
            self.assertAlmostEqual(mag_exact, 0.0, places=6)

    def test_routing_cx_overhead_and_unrolled_swaps(self):
        """Verify routing overhead: explicit SWAP is 0 due to basis unrolling; B has fewer CX gates than A."""
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5)
        qc = model.build_trotter_circuit(t=1.0, num_steps=4, measure=True)

        cfg_a = load_processor_config(self.proc_a_file)
        tc_a, met_a = compile_for_processor(qc, build_coupling_map(cfg_a), basis_gates=cfg_a["basis_gates"])

        cfg_b = load_processor_config(self.proc_b_file)
        tc_b, met_b = compile_for_processor(qc, build_coupling_map(cfg_b), basis_gates=cfg_b["basis_gates"])

        # Explicit SWAP counts are 0 because SWAPs are unrolled to 3 CX gates
        self.assertEqual(met_a["explicit_swap_count"], 0)
        self.assertEqual(met_b["explicit_swap_count"], 0)

        # Processor B heavy-hex hub reduces total CX gates compared to Processor A linear chain
        self.assertLess(met_b["two_qubit_ops"], met_a["two_qubit_ops"])
        self.assertEqual(met_a["two_qubit_ops"], 74)
        self.assertEqual(met_b["two_qubit_ops"], 53)

        # Two-qubit depth is measured
        self.assertGreater(met_a["two_qubit_depth"], 0)
        self.assertGreater(met_b["two_qubit_depth"], 0)

    def test_statistical_metrics_and_zero_division(self):
        """Verify TVD and Classical Fidelity calculations, including zero-shot edge cases."""
        dist_1 = {"00": 500, "01": 500}
        dist_2 = {"00": 500, "01": 500}
        self.assertAlmostEqual(compute_tvd(dist_1, dist_2), 0.0)
        self.assertAlmostEqual(compute_classical_distribution_fidelity(dist_1, dist_2), 1.0)

        # Zero-shot / empty dictionary edge cases
        self.assertEqual(compute_tvd({}, dist_1), 1.0)
        self.assertEqual(compute_classical_distribution_fidelity({}, dist_1), 0.0)
        self.assertEqual(compute_magnetization_from_counts({}, 4), (0.0, 0.0))
        self.assertEqual(compute_proportion_error(0.5, 0), 0.0)


if __name__ == "__main__":
    unittest.main()

