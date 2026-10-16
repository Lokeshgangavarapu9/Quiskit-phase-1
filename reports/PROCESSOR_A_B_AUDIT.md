# Quantum Processor A & B Architecture Audit

**Project:** Qiskit Fall Fest 2026 — Phase 1 (Problem S3)  
**Document:** `reports/PROCESSOR_A_B_AUDIT.md`  

---

## 1. Specification Comparison: Official Master Guide vs. Repository

| Parameter | Official Master Guide (Authoritative) | Current Repository (`processors/`) | Status | Required Action |
| :--- | :--- | :--- | :---: | :--- |
| **Proc A: Qubits** | 5 physical qubits (Nodes 0 to 4) | 5 physical qubits (Nodes 0 to 4) | **PASS** | Keep 5 qubits. |
| **Proc A: Topology**| Linear chain `[(0,1),(1,2),(2,3),(3,4)]` or Tree `[(0,1),(1,2),(1,3),(3,4)]` | Linear chain `[(0,1),(1,2),(2,3),(3,4)]` | **PASS** | Valid reference baseline. |
| **Proc A: Basis Gates** | `['rz', 'sx', 'x', 'cx']` | `['rz', 'sx', 'x', 'cx']` | **PASS** | Verified. |
| **Proc B: Qubits** | **9 physical qubits (Nodes 0 to 8)** | **7 physical qubits (Nodes 0 to 6)** | **DEFECT** | Upgrade to 9 physical qubits. |
| **Proc B: Topology**| Sparse 9-qubit heavy-hex-inspired graph (12 edges) | 7-qubit heavy-hex subgraph (6 edges) | **DEFECT** | Update to 9-qubit heavy-hex reference. |
| **Proc B: Basis Gates** | `['rz', 'sx', 'x', 'cx']` | `['rz', 'sx', 'x', 'cx']` | **PASS** | Verified. |

---

## 2. Origin of the 7-Qubit Processor B Configuration

Investigation of the provided materials confirms the exact origin of the 7-qubit model:
1. In the partner presentation slide deck **`Geometry-aware quantum cloud challenge` (Steven Rayan / quanTA)**, Slide 4 depicted:
   - Processor A: 5 qubits (Online)
   - Processor B: 7 qubits (Online)
   - Processor C: 8–10 qubits (Shortlisted)
2. The student faithfully modeled Processor B as 7 qubits based on this early slide deck.
3. Subsequently, the organizers issued the **`Processor A/B Benchmark Configuration`** and the **`Phase 1 Master Guide (SRM University-AP)`**, which explicitly corrected Processor B to **9 physical qubits (Nodes 0 to 8)** with 12 edges to reflect IBM's standard heavy-hex unit cell.

**Verdict:** This is not a careless coding blunder, but an artifact of evolving competition documentation. To achieve maximum judging points under the final Master Guide, Processor B must be transitioned to the authoritative 9-qubit architecture.

---

## 3. The 9-Qubit Processor B Topology Specifications

From the Master Guide (p. 2) and Benchmark Configuration (p. 2):
- **Physical Nodes:** `0, 1, 2, 3, 4, 5, 6, 7, 8`
- **Unique Undirected Edges (12 total):**
  $$(0,1), (1,2), (1,6), (2,3), (2,6), (2,5), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0)$$
- **Degree Distribution:**
  - Node 0: degree 2 (connected to 1, 8)
  - Node 1: degree 3 (connected to 0, 2, 6)
  - Node 2: degree 4 (connected to 1, 3, 5, 6)
  - Node 3: degree 2 (connected to 2, 4)
  - Node 4: degree 2 (connected to 3, 5)
  - Node 5: degree 3 (connected to 2, 4, 6)
  - Node 6: degree 5 (connected to 1, 2, 5, 7, 8)
  - Node 7: degree 1 (connected to 6)
  - Node 8: degree 2 (connected to 0, 6)
- **Topological Significance:**
  - Nodes 1, 2, 5, and 6 form a rich, tightly-coupled cluster with multiple alternate routes.
  - The maximum graph diameter is reduced to 2 hops among core computational nodes, providing vastly superior routing efficiency for 4-spin simulation compared to a 1D linear chain.

---

## 4. Transpilation, Routing & SWAP Accounting

### 4.1 Why Explicit SWAPs are Zero
In Qiskit transpilation targeting `{rz, sx, x, cx}`:
1. Qiskit's `SabreSwap` or `StochasticSwap` routing pass identifies pairs of logical qubits that must interact across disconnected physical edges.
2. It inserts logical SWAP gates.
3. The basis unrolling pass decomposes every SWAP gate into **3 native CX gates**:
   $$\text{SWAP}(j, k) \equiv \text{CX}(j, k) \cdot \text{CX}(k, j) \cdot \text{CX}(j, k)$$
4. Therefore, the compiled circuit contains zero explicit `swap` instructions (`explicit_swap_count = 0`).

### 4.2 Routing CX Overhead Calculation
The true routing overhead is calculated directly from the two-qubit gate count:
$$\text{Routing CX Overhead} = N_{\text{CX, compiled}} - N_{\text{CX, logical}}$$
$$\text{Equivalent SWAP Count} = \frac{\text{Routing CX Overhead}}{3}$$

### 4.3 Total Capacity vs. Active Physical Qubits
The repository correctly distinguishes:
- **Total Processor Capacity:** Total qubits in the hardware register (5 on A; 7 currently / 9 target on B).
- **Active Physical Qubits:** The actual physical nodes hosting operations (4 active spins).
This satisfies the Master Guide guideline requiring participants to account for unused ancilla/background qubits.
