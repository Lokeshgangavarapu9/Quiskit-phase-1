"""
Unit and integration test suite for Qiskit Fall Fest 2026 Phase 1 (Problem S3).
"""

import unittest
from pathlib import Path

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
    compute_classical_fidelity
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

    def test_problem_s3_hamiltonian(self):
        """Verify Hamiltonian generation and exact unitary propagation."""
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5)
        self.assertEqual(model.hamiltonian_matrix.shape, (16, 16))

        # Check Hermiticity
        h_mat = model.hamiltonian_matrix
        self.assertTrue((h_mat == h_mat.conj().T).all())

        # Exact magnetization calculation
        mag_t0 = model.compute_exact_magnetization(0.0)
        # For initial state |1010>, spins are alternating, so sum is 0
        self.assertAlmostEqual(mag_t0, 0.0, places=5)

    def test_trotter_circuit_building(self):
        """Verify Trotter circuit generation with expected gate components."""
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5)
        qc = model.build_trotter_circuit(t=1.0, num_steps=2, measure=True)
        self.assertEqual(qc.num_qubits, 4)
        self.assertIn("cx", qc.count_ops())
        self.assertIn("rx", qc.count_ops())
        self.assertIn("rz", qc.count_ops())

    def test_transpilation_and_architecture_metrics(self):
        """Verify transpilation preserves functionality and records routing metrics."""
        model = TrotterSimulationModel(num_spins=4, J=1.0, h=0.8, J_cross=0.5)
        qc = model.build_trotter_circuit(t=1.0, num_steps=1, measure=True)

        cfg_a = load_processor_config(self.proc_a_file)
        cmap_a = build_coupling_map(cfg_a)
        compiled_a, metrics_a = compile_for_processor(qc, cmap_a, basis_gates=cfg_a["basis_gates"])

        self.assertGreater(metrics_a["depth"], 0)
        self.assertGreater(metrics_a["two_qubit_ops"], 0)
        self.assertEqual(metrics_a["num_qubits"], 5)

    def test_statistical_metrics(self):
        """Verify TVD and Classical Fidelity calculations."""
        dist_1 = {"00": 500, "01": 500}
        dist_2 = {"00": 500, "01": 500}
        self.assertAlmostEqual(compute_tvd(dist_1, dist_2), 0.0)
        self.assertAlmostEqual(compute_classical_fidelity(dist_1, dist_2), 1.0)

        dist_3 = {"10": 500, "11": 500}
        self.assertAlmostEqual(compute_tvd(dist_1, dist_3), 1.0)
        self.assertAlmostEqual(compute_classical_fidelity(dist_1, dist_3), 0.0)


if __name__ == "__main__":
    unittest.main()
