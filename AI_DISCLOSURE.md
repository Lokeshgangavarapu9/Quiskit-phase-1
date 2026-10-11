# AI / LLM Assistance Disclosure

**Competition:** Qiskit Fall Fest 2026 — Phase 1  
**Project:** S3 — Noise in Trotter Simulation  
**Repository:** [https://github.com/Lokeshgangavarapu9/Quiskit-phase-1](https://github.com/Lokeshgangavarapu9/Quiskit-phase-1)  

---

## 1. Compliance Statement
This project adheres to the official AI / Large Language Model (LLM) use policy announced by the Qiskit Fall Fest 2026 Hackathon & Competitions Cell. In accordance with the guidelines:
- The use of AI tools has been transparently disclosed.
- All code, architectural benchmarks, mathematical models, and simulated outputs have been independently executed, verified, and inspected for scientific validity.
- The participant takes full responsibility for the correctness and reproducibility of the submitted work.

---

## 2. Tools & Models Used
- **Agentic AI Coding Assistant:** Google Antigravity / Gemini 3.8
- **Role:** Assisting in repository structure setup, script drafting, boilerplate test writing, Markdown documentation structuring, and executing verification commands in the local workspace.

---

## 3. Human Oversight & Verification
- **Architecture Definitions:** Verified against the official organizer instructions (Processor A: 5-qubit linear baseline; Processor B: 7-qubit heavy-hex baseline).
- **Physical Model:** The Transverse-Field Ising Model (TFIM) and first-order Suzuki-Trotter decomposition were validated against classical matrix exponentiation (`scipy.linalg.expm`).
- **Data Authenticity:** All reported metrics (circuit depth, two-qubit gate counts, SWAP operations, TVD, magnetization, and fidelity) are computed from live simulation executions using Qiskit Aer (`seed_simulator=42`, `seed_transpiler=42`) and exported directly to machine-readable CSV/JSON files. No values were fabricated or hardcoded.
