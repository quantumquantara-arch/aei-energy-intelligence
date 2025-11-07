# AEI — Artificial Energy Intelligence  

**Predictive orchestration and coherence-weighted energy management**  
*(Powered by Quantara)*  

---

## Overview  
AEI (Artificial Energy Intelligence) is a predictive orchestration engine that learns to balance renewable and stored energy intelligently.  
It integrates Quantara’s Coherence principles, κ-scoring, and the Veyn temporal operator to improve energy efficiency, stability, and ethical performance in distributed microgrids.  

AEI represents the “thinking brain” of decentralized energy — continuously learning to forecast, balance, and optimise power flows across local and global networks.  

---

## How to Run the Demo  

Once you clone the repository on a computer:  

```bash
git clone https://github.com/<your-username>/aei-energy-intelligence.git
cd aei-energy-intelligence
python -m venv .venv && source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
python examples/minimal_microgrid/run_demo.py

--- AEI Demo ---
kappa_mean: 0.74
TCI: 0.82
First 5 forecast pts: [8.6, 8.6, 8.6, 8.6, 8.6]
First 5 SOC: [10.0, 10.5, 11.0, 11.4, 11.9]
----------------
