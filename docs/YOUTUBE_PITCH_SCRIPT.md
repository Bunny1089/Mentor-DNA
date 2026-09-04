# Merchant DNA — YouTube Pitch & Demo Script (3–4 Minutes)

> **Elevator Pitch:** Merchant DNA is a cross-merchant fraud intelligence and graph detection platform that catches coordinated syndicates, mule networks, and bust-out schemes that transaction-level filters structurally cannot see.

---

## Video Metadata & Packaging

* **YouTube Video Title:** `Merchant DNA: Cross-Merchant Fraud Intelligence & Graph Detection for Payment Platforms`
* **Alternate Title (High CTR):** `Catching Coordinated Mule Rings with Graph Intelligence | Merchant DNA Demo`
* **YouTube Description:**
  ```text
  Merchant DNA is an end-to-end risk intelligence platform designed for payment aggregators and fintech platforms. While traditional fraud systems inspect isolated transactions, organized syndicates operate across distributed shell storefronts sharing physical devices, VOIP numbers, and payout bank accounts. 

  In this 3.5-minute technical walkthrough, we demonstrate:
  1. Real-time multi-merchant risk triage and recovery SLA tracking
  2. Bipartite entity-linkage graph analysis exposing collusive rings
  3. Grounded AI case synthesis with strict evidence constraints
  4. Bounded, reversible settlement actions with immutable audit logging
  5. Live mule burst and syndicate expansion simulations
  6. Out-of-sample holdout benchmarks (97.2% Precision, 95.1% Ring Detection) and honest limitations

  🔗 GitHub Repository: https://github.com/Bunny1089/Mentor-DNA.git
  📊 Full Technical Report: docs/MERCHANT_DNA_EXECUTIVE_REPORT.pdf
  ```
* **YouTube Tags:** `FraudDetection, PaymentGateway, Razorpay, GraphAnalytics, MachineLearning, Fintech, NetworkX, Cytoscape, AIinFintech, RiskIntelligence, FraudPrevention`
* **Thumbnail Text:** `CATCHING COVERT FRAUD RINGS | Cross-Merchant Graph Intelligence`

---

## Timed Script & Recording Actions

### 0:00 – 0:25 | 1. The Hook (Coordinated Syndicate Blind Spot)
* **Visual Action:** `[OPEN DASHBOARD]` — Show the clean, dark-mode Merchant DNA operations console with live metrics and priority alerts.
* **Speaker:**
  > "Every year, payment aggregators lose millions to coordinated merchant syndicates. These aren't solo card hackers. They are organized rings registering dozens of seemingly legitimate shell businesses, keeping individual transaction volumes low to evade standard velocity tripwires, and cashing out settlements before chargebacks hit."

---

### 0:25 – 0:50 | 2. Real-World Problem & The Architectural Gap
* **Visual Action:** `[HOVER OVER ALERT CARDS]` — Highlight high-risk alert items flagged for `RING_MEMBERSHIP` and `BURST_PATTERN`.
* **Speaker:**
  > "Why do existing transaction-level filters fail? Because evaluating a single payment in isolation cannot see that 20 separate merchants are secretly sharing the exact same emulator hardware fingerprint, payout IFSC code, and VOIP batch. Single-merchant tools are structurally blind to cross-entity collusion."

---

### 0:50 – 1:15 | 3. Dual-Engine Intelligence & Operational Dashboard
* **Visual Action:** `[SHOW METRIC CARDS & TRIAGE QUEUE]` — Point out the ₹28.4L Total Volume Restored metric, 4.2-hour dispute SLA, and calibrated risk score distribution.
* **Speaker:**
  > "Merchant DNA solves this with a dual-engine architecture: 30+ behavioral telemetry signals weighted at 60%, combined with bipartite entity-linkage graph community detection weighted at 40%. Our dashboard gives risk analysts instant situational awareness: active ring alerts, portfolio risk distribution, and automated false-positive recovery tracking."

---

### 1:15 – 1:45 | 4. High-Risk Merchant Investigation & Graph Forensics
* **Visual Action:** `[OPEN INVESTIGATION]` — Click into merchant `M-ALPHA-01` (*Nova Retail Systems*, Risk Score 88.5 / Critical).
* **Visual Action:** `[ZOOM INTO SHARED ENTITY]` — Interact with the Cytoscape graph canvas, highlighting red links to `DEV-FARM-991` and shared bank account `ACC-MULE-401`.
* **Speaker:**
  > "Let's open an active investigation on merchant M-ALPHA-01. At first glance, individual ticket sizes look normal. But our ego graph immediately reveals the truth: this merchant is directly tethered to a known 5-merchant collusive ring through shared physical device DEV-FARM-991 and settlement conduit ACC-MULE-401."

---

### 1:45 – 2:10 | 5. Grounded AI Briefing & Business Impact
* **Visual Action:** `[GENERATE AI BRIEFING]` — Click 'Generate Grounded Briefing', highlighting structured citations linking directly to behavioral entropy and graph node IDs.
* **Visual Action:** `[SCROLL TO BUSINESS IMPACT]` — Show ₹18.5L Exposure At Risk and 94% Dispute Win Probability.
* **Speaker:**
  > "Rather than drowning analysts in raw logs, our Grounded AI Copilot synthesizes structured evidence into a 30-second factual briefing. Every statement is strictly constrained to deterministic telemetry inputs with zero hallucination. Below, the system calculates exact financial exposure at risk and dispute recovery probability."

---

### 2:10 – 2:35 | 6. Bounded Reversible Action & Immutable Audit Trail
* **Visual Action:** `[APPROVE ACTION]` — Click 'Execute Settlement Hold' in the action modal with rationale selection.
* **Visual Action:** `[SHOW AUDIT TRAIL]` — Scroll to the append-only Audit Ledger showing `SETTLEMENT_HOLD_APPLIED` and automatic 48-hour cap timer.
* **Speaker:**
  > "Crucially, Merchant DNA enforces bounded, reversible interventions. We don't abruptly ban merchants and create costly customer churn. We apply a targeted settlement hold while keeping checkout active for legitimate buyers. Every decision is logged to an immutable audit trail with automatic 48-hour caps and proactive merchant dispute notices."

---

### 2:35 – 3:00 | 7. Live Interactive Simulation (Mule Burst & Ring Expansion)
* **Visual Action:** `[RUN MULE SIMULATION]` — Navigate to Simulation page, trigger 'Rapid Cashout Burst', watch velocity score spike from 22 to 84.
* **Visual Action:** `[RUN RING SIMULATION]` — Click 'Synthesize Collusive Ring', observe Louvain community clustering automatically link 4 new shell nodes.
* **Speaker:**
  > "Under our Simulation sandbox, risk teams can stress-test defense policies. Triggering a sleeper mule burst immediately trips velocity and entropy alarms. Synthesizing a collusive ring demonstrates how Louvain community clustering autonomously identifies newly connected shell nodes in real time."

---

### 3:00 – 3:25 | 8. Credible Benchmark & Honest Boundary Disclosures
* **Visual Action:** `[OPEN EVALUATION PAGE]` — Display the dual-benchmark comparison and multi-seed ROC-AUC / PR curves.
* **Speaker:**
  > "In controlled synthetic benchmark evaluation on an unseen 30% holdout split of 321 merchants, Merchant DNA delivers 97.2% Precision, 86.4% Recall, 0.938 ROC-AUC, and 95.1% Planted Ring Detection. We explicitly disclose known limitations: subtle sleeper accounts mimic organic SMBs and achieve 60% detection, which our roadmap addresses via rolling temporal graph motifs."

---

### 3:25 – 3:50 | 9. Monetization, Razorpay Fit & Closing Statement
* **Visual Action:** `[SHOW TRUST SIGNAL API CARD / CLOSING SLIDE]` — Show the read-only Trust Signal API response and 5-tier monetization architecture.
* **Speaker:**
  > "With a 5-tier commercial ladder spanning free starter trust badges to enterprise Risk-as-a-Service licensing, Merchant DNA transforms defensive risk into a verifiable merchant trust asset. Sitting at the intersection of gateway, payouts, and UPI routing, Razorpay is uniquely positioned to turn cross-merchant fraud intelligence into unfair competitive advantage. Thank you."
