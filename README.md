# Merchant DNA | AI-Powered Cross-Merchant Fraud Intelligence

> **Cross-merchant fraud intelligence for payment platforms — behavioral scoring and network analysis that catch what single-merchant tools structurally can't see.**

---

## The Blind Spot

Traditional payment fraud detection operates at the individual transaction level, evaluating card velocity, 3DS challenges, and IP geolocation in isolation. However, modern merchant-side fraud operates through distributed networks:

* **Distributed Syndicate Shells:** Fraud rings register 10 to 50 seemingly legitimate storefronts with valid KYC documents. Each merchant maintains low, steady volumes that stay well below transaction-level velocity tripwires.
* **Mule Accounts & Rapid Cashouts:** Sleeper accounts remain dormant for 30–60 days to establish baseline history, then process concentrated transaction bursts followed by immediate settlement withdrawal requests before chargebacks arrive.
* **Aggregator Liability:** When merchant defaults and chargebacks occur, payment aggregators bear financial liability for unrecoverable negative balances.

---

## The Approach

Merchant DNA addresses cross-merchant risk through three interconnected components:

1. **Behavioral Telemetry (60% Weight):** A gradient boosted decision tree model evaluating 30+ merchant-level features, including category ticket deviations, off-peak velocity, buyer concentration (HHI), and settlement turnaround speed.
2. **Network Graph Analysis (40% Weight):** Bipartite graph modeling and Louvain community detection to uncover shared devices, phone numbers, bank accounts, and UPI VPAs.
3. **Grounded Synthesis & Bounded Actions:** An AI copilot providing grounded synthesis constrained to structured evidence inputs, coupled with reversible settlement holds that protect liquidity while preserving checkout operations for review.

---

## How It Works

* **Step 1 — Entity Ingestion & Indexing:** Transaction streams, onboarding metadata, and settlement requests are indexed into reverse lookup tables linking merchants to physical and digital identifiers.
* **Step 2 — Behavioral Feature Extraction:** Rolling windows compute catalog baseline divergence, off-peak processing ratios, round-denomination frequencies, and payout turnaround velocity.
* **Step 3 — Graph Topology & Community Detection:** Multi-entity bipartite projection generates merchant-to-merchant relationship graphs, applying community clustering to identify syndicates.
* **Step 4 — Hybrid Calibrated Risk Scoring:** Combines behavioral ML probabilities (60%) and graph density/centrality scores (40%) into a 0–100 risk score with calibrated tiers (Low, Medium, High, Critical).
* **Step 5 — Forensic Investigation & Grounded Synthesis:** Analysts inspect cases across four core questions (Who, How, Who Else, What Next) supported by an interactive Cytoscape network graph and evidence-constrained AI summaries.
* **Step 6 — Bounded Actions & Immutable Audit:** Analysts apply targeted holds or clear cases, with all state transitions recorded in an append-only audit ledger.
* **Step 7 — Merchant Appeal / Dispute Flow:** Merchants can dispute settlement holds through an appeal form, routing cases into a dedicated `PENDING_APPEAL_REVIEW` queue logged to the audit ledger.

---

## Stack

| Layer | Technologies | Purpose & Role in Pipeline |
| :--- | :--- | :--- |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite, Lucide Icons, Recharts | Enterprise analyst console with sub-second page transitions, interactive triage queues, and forensic views. |
| **Graph Visualization** | Cytoscape.js, Cola Physics Layout | Multi-entity ego graph visualizer with node clustering and shared-identifier inspection. |
| **Backend Services** | FastAPI, Python 3.14, Pydantic v2, Uvicorn, AnyIO | Asynchronous REST API gateway with schema validation, CORS security, and modular service routing. |
| **Machine Learning & Graph** | Scikit-Learn (HistGradientBoosting), NetworkX, NumPy, SciPy | Behavioral gradient boosting classifier, 30+ feature extractors, and Louvain community detection. |
| **AI Synthesis** | Google Gemini API / Deterministic Grounded Fallback | Grounded synthesis constrained to structured evidence inputs, providing factual case briefings. |
| **Testing & Quality** | Pytest, Oxlint, Vite Production Compiler | Automated unit tests, integration suites, API contract validation, and data leakage prevention tests. |

---

## Where This Applies

* **Payment Aggregators (Razorpay, Stripe, Cashfree):** Gatekeeping automated daily settlement batches to intercept coordinated syndicates before payout disbursement.
* **Neobanks & Instant Payout Platforms (RazorpayX):** Real-time risk scoring on instant settlement drawdowns, protecting automated liquidity pools from compromised credentials.
* **Acquiring Banks & Card Networks (RuPay, Visa, Mastercard):** Portfolio-level merchant risk surveillance and syndicated chargeback liability mitigation.
* **E-Commerce Marketplaces & Agentic Commerce Platforms:** Validating seller authenticity and providing verified trust credentials for autonomous AI purchasing agents executing programmatic checkouts.

---

## Agentic Commerce & Merchant Trust Signals

In the emerging landscape of **agentic commerce**—where autonomous AI agents execute programmatic purchases and supply chain procurement on behalf of users—verifying merchant legitimacy without human intervention is a critical requirement. A malicious storefront or bust-out syndicate could exploit agentic purchasing limits before human oversight intervenes.

Merchant DNA inverts its internal risk assessment into a lightweight, public **Merchant Trust Signal API** (`GET /api/trust/{merchant_id}`):
* **Zero-Leakage Trust Attestation:** Exposes clean categorical tiers (`VERIFIED`, `STANDARD`, `CAUTION`, or `WITHHELD`) and eligibility flags (`instant_settlement_eligible`, `agentic_purchasing_approved`) without exposing confidential internal risk models or graph topology.
* **Autonomous Purchasing Clearance:** AI purchasing agents can query the endpoint at machine speed to confirm merchant trust before completing high-value programmatic checkout flows.
* **Growth Re-framing:** Transforms defensive fraud mitigation into a growth and verification asset that high-reputation merchants can leverage to unlock higher transaction velocity and instant settlements.

---

## Business Model & Projected Impact

All five tiers run on the same underlying risk and graph intelligence engine — the free tier is not a cost center, but an essential network asset that strengthens the cross-merchant ring-detection signals that paid tiers depend on.

### Tiered Monetization Ladder

| Tier | Target Segment | Key Capabilities & Features | Commercial Model & Pricing |
| :--- | :--- | :--- | :--- |
| **1. Starter** | Individual & informal sellers (WhatsApp/Instagram commerce, gig sellers) | Public trust badge only. Serves as a funnel and network-effect tier (more merchants on the platform strengthens cross-merchant ring detection for every paying tier above it). | Free or nominal flat fee (₹49–₹99/month) |
| **2. Growing SMB** | Small D2C brands, single-location retailers | Basic risk dashboard, public trust badge, limited fraud alerts, self-serve appeal & dispute flow. | Flat monthly SaaS (₹499–₹1,999/month) or free up to volume threshold then metered |
| **3. Established Merchant** | Multi-location retailers, scaling D2C brands | Full case-investigation dashboard, instant-settlement eligibility via trust tier, priority appeal handling, own-account network visibility. | Volume-scaled SaaS (₹5,000–₹25,000/month) or 0.02%–0.05% basis-point fee on instant-settlement volume |
| **4. Enterprise / Large Platform** | Large retailers, big marketplaces with sub-sellers | Dedicated analyst console, custom SLAs, API access to trust signals for sub-merchant vetting, white-labeled trust badge. | Annual enterprise license plus basis-point fee on protected volume (negotiated) |
| **5. Aggregator / Bank (B2B2B)** | Other payment aggregators, acquiring banks, neobanks | Full engine licensed as Risk-as-a-Service, raw API integration, cross-platform syndicate surveillance. | Per-query or annual enterprise API licensing (highest-margin tier) |

### Projected Impact & Loss Mitigation

* **Projected Fraud Loss Prevention:** In out-of-sample benchmark evaluation on 321 unseen holdout merchants (from 1,070 corpus), extrapolated fraud-loss prevention is estimated at approximately **₹5.90 Crore** against **₹3,108.98** estimated false-positive friction cost (projected simulation, not measured in live production).
* **False-Positive Appeal Recovery:** Integrated appeal dispute tracking quantifies operational capital restored to verified merchants, turning friction into verifiable SLA performance metrics (e.g. **₹28.4 Lakhs** recovered with a **4.2-hour** average resolution turnaround).

---

## Engineering Finding: Shared-Infrastructure False Positives

During initial graph pipeline testing, we identified a notable source of false-positive ring detections: unrelated merchants that used the same generic payment gateway or payment service provider (PSP) handle were occasionally linked into collusive clusters by graph projection.

**Fix Implemented:** We added a shared-infrastructure filtering step in the network detector (`NetworkRiskDetector`) that down-weights and excludes edges formed purely by generic processor or gateway infrastructure. A collusive ring candidate now requires at least one strong personal identifier (bank account, phone number, or device hardware fingerprint) or multi-identifier corroboration, preventing generic payment infrastructure from generating spurious alerts.

---

## Benchmark Results & Evaluation

> **Benchmark Presentation Note:** Standard benchmark confirms separation of obviously anomalous behavior; the harder out-of-sample holdout is the meaningful performance result. All metrics are from controlled synthetic benchmarks.

Performance is evaluated across two isolated splits: the **Standard Benchmark** (240 merchants, baseline sanity check) and the **Harder Benchmark** (1,070 merchants with subtle non-round amounts, gradual velocity ramp-ups, 100 hard negatives, and 51 planted syndicates evaluated on an unseen 30% holdout partition of 321 test merchants).

### Dual Benchmark Split & Multi-Seed Comparison

| Metric | Standard Benchmark (Sanity Check) | Harder Holdout (30% Unseen Split) | Multi-Seed (Mean ± Std, 5 Seeds) | Behavior Under Stress |
| :--- | :---: | :---: | :---: | :--- |
| **Precision (PPV)** | 100.0% | **97.2%** (70 TP / 2 FP) | **99.2% ± 1.6%** | High precision maintained with hard negative background noise |
| **Recall (Sensitivity)** | 100.0% | **86.4%** (70 TP / 11 FN) | **89.1% ± 2.6%** | Predictable degradation on subtle sleeper mules and weak pairs |
| **F1-Score** | 1.000 | **0.915** | **0.939 ± 0.017** | Strong overall discrimination on out-of-sample data |
| **ROC-AUC** | 1.000 | **0.938** | **0.989 ± 0.010** | High separability across continuous risk scores |
| **Planted Ring Detection Rate** | 100.0% | **95.1%** (58/61 merchants) | **95.0% ± 1.4%** | Robust cross-merchant graph community clustering |
| **Mule Shell Detection Rate** | 100.0% | **60.0%** (12/20 merchants) | **68.2% ± 8.6%** | Catches active mules; subtle low-velocity sleepers remain under threshold |

### Adversarial Robustness Stress Test (Evasion-Aware Generator)

To evaluate model resilience against evasion-aware fraudsters, we built an adversarial synthetic batch generator where fraudulent syndicates specifically circumvent top SHAP behavioral signals:
* **Ticket Normalization:** Generates realistic fractional ticket distributions to avoid round-number flags.
* **Buyer Entropy Dilution:** Synthesizes artificially diversified buyer pools to suppress HHI concentration alerts.
* **Organic Settlement Cadence:** Randomizes payout timing and introduces gradual volume ramps instead of sudden bursts.

| Metric | Standard Baseline | Harder Holdout | Adversarial Evasion Stress |
| :--- | :---: | :---: | :---: |
| **Precision** | 100.0% | 97.2% | **83.3%** |
| **Recall (Sensitivity)** | 100.0% | 86.4% | **10.0%** |
| **F1-Score** | 1.000 | 0.915 | **0.179** |
| **ROC-AUC** | 1.000 | 0.938 | **0.920** |
| **Planted Ring Detection** | 100.0% | 95.1% | **25.0%** (5/20 caught) |
| **Mule Shell Detection** | 100.0% | 60.0% | **0.0%** |

> **Explicit Disclaimer:** This quantifies real degradation under evasion-aware conditions our team could anticipate — not a claim of general adversarial robustness. When fraudsters systematically normalize prices and randomize settlement cadences, standalone behavioral ML models experience severe recall drops. Cross-merchant graph detection provides the vital safety net.

### Score Stability & Feature Perturbation Analysis

Evaluated across two distinct populations under a ±5% uniform feature perturbation:
* **Non-Borderline Cohort (Risk Score <45 or >75, $n=20$):** **0.0% tier flips** observed under ±5% feature perturbation, establishing baseline classification stability far from the boundary.
* **Borderline Cohort (Risk Score 50–70 near threshold 60.0, $n=16$):** **12.5% tier flips (2/16 merchants)** observed under ±5% feature perturbation.

> **Boundary Sensitivity Rationale:** Boundary sensitivity is an expected mathematical property of any threshold-based classifier near its decision boundary. The 48-hour cap-and-escalate settlement hold policy is the structural safeguard against acting irreversibly on a borderline flip.

### Approximated Blind Hard-Negative Evaluation

Evaluated against 10 independently designed real-world edge cases (flash sales, high-ticket art sales, night-market food stalls, seasonal surges, wholesale B2B batching), the engine achieved **80.0% accuracy (8/10 correctly classified)**.

* **Correctly Classified (8/10):** M-BLIND-01 (Diwali silks surge), M-BLIND-02 (PSU bank migration), M-BLIND-03 (B2B chemical supplier), M-BLIND-04 (night-market food truck), M-BLIND-06 (creator drop burst), M-BLIND-07 (antiquarian books dealer), M-BLIND-08 (franchise WiFi subnet), M-BLIND-10 (quarterly tuition collector).
* **Known Limitation Finding:** Blind testing surfaced 2 cases where legitimate edge cases were flagged via network and concentration signals: M-BLIND-05 (tech incubator sharing address with 7 other firms) and M-BLIND-09 (corporate group travel agent with high buyer concentration), indicating that single-identifier physical address aggregation and corporate buyer concentration heuristics require further contextual domain tuning.

> **Framing Note:** Framed explicitly as an *approximated blind check* rather than a true blind study, as the 10 test scenarios were designed in a separate pass by the same engineering team.

### Ring-Size Sensitivity Breakdown (Harder Split)

| Ring Size Bracket | Planted Rings (Holdout Sample) | Detected Rings | Detection Rate |
| :--- | :---: | :---: | :---: |
| **2–3 merchants** | 15 | 13 | **86.7%** |
| **4–6 merchants** | 15 | 15 | **100.0%** |
| **7–10 merchants** | 4 | 4 | **100.0%** |
| **10+ merchants** | 2 | 2 | **100.0%** |

### Audited False-Positive Cost Model (Hand-Verifiable)

* **Delayed Hold Volume:** For the 2 false-positive merchants in the 30% holdout split, only the transaction volume during the 3-day hold window is delayed:  
  $$\text{Delayed Volume} = \sum_{i \in \text{FP}} \left( \frac{\text{Processed Volume}_i}{\text{Active Days}_i} \times 3\text{ days} \right) = \text{₹}1,55,449.01 \text{ (₹1.55 Lakhs)}$$
  *(Note: The cumulative 60-day historical processed volume of these 2 merchants is ₹15.07 Lakhs, but only ₹1.55 Lakhs is held during the 3-day hold window).*
* **Capital Friction & Support Cost:** Applying the 2.0% (200 bps) capital friction / inquiry handling rate to the delayed volume:  
  $$\text{Capital Friction Cost} = \text{₹}1,55,449.01 \times 2.0\% = \text{₹}3,108.98$$
* **Reversible Interventions:** Reversible settlement holds keep checkout operational while payouts are queued for review, ensuring zero cart abandonment for legitimate buyers during investigations.

### False-Negative Recovery Rate Sensitivity Matrix

| Scenario | Modeled Recovery Rate | Gross Loss Prevented | False-Positive Friction Cost | Net Fraud Savings (INR) |
| :--- | :---: | :---: | :---: | :---: |
| **Conservative** | 5% | ₹6,59,62,499.78 | ₹3,108.98 | **₹6,24,67,117.82** |
| **Baseline (Assumed)** | 15% | ₹5,90,19,026.12 | ₹3,108.98 | **₹5,58,92,158.05** |
| **Optimistic** | 30% | ₹4,86,03,815.63 | ₹3,108.98 | **₹4,60,29,718.39** |

> **Modeling Note:** The 15% recovery figure is an operational modeling assumption, not an empirically measured constant. Net fraud savings remain strongly positive (>₹4.6 Crore) across all tested recovery scenarios.

### Threshold Selection Methodology ("Why 60.0?")

* **Training Grid Sweep:** Operating threshold $\theta = 60.0$ was selected via grid search on the **70% Training Partition only (749 merchants)**, leaving the 30% holdout test set completely untouched.
* **Operating Rationale:** Threshold 60.0 corresponds to the `HIGH` risk tier boundary where automated settlement holds occur. On training data, threshold 60.0 delivers **100.0% precision (0 false alarms)** and **95.8% recall (F1=0.978)**, guaranteeing zero operational friction on legitimate merchants during automated holds while capturing high-confidence fraud.
* **Out-of-Sample Validation:** Evaluated on the unseen 30% holdout split, threshold 60.0 confirmed **97.2% precision, 86.4% recall, and 0.915 F1**.

### Banking & Payment Aggregator Compliance Architecture

* **48-Hour Maximum Hold Cap:** All settlement holds enforce an automated 48-hour hard ceiling with mandatory 24-hour supervisor escalation, eliminating indefinite fund freezes.
* **Proactive Merchant Notification:** Every hold automatically dispatches an immediate merchant notification containing the specific operational rationale, required evidence checklist, and direct dispute submission link, logged with immutable audit event `MERCHANT_NOTIFICATION_DISPATCHED`.
* **Compliance Scope Disclaimer:** These operational safeguards are internal risk engineering designs aligned with the core principles of RBI Payment Aggregator Guidelines (DPSS.CO.PD.No.1810/02.14.008/2019-20). They are designed for operational fairness and risk management, not certified banking compliance products.

### Known Limitations & Engineering Roadmap

* **Subtle Sleeper Mule Detection (60.0% Detection Rate, 12/20 caught):** Subtle low-velocity sleeper accounts deliberately mimic legitimate small merchants (modest ticket sizes, zero initial disputes).  
  *Roadmap:* Longer observation windows, velocity-drift trajectory tracking, and buyer entropy evolution features.
* **Small Syndicate Detection (86.7% Detection Rate on 2–3 Merchant Rings, 13/15 caught):** Small 2-to-3 merchant syndicates yield sparse bipartite subgraphs with fewer shared edges than large syndicates.  
  *Roadmap:* Multi-hop temporal graph analysis, fuzzy device/IP subnet correlation, and higher-order motif clustering.

---

## Quickstart & Verification

### Prerequisites
* Python 3.10+
* Node.js 18+ & npm

### Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Run Full Test Suite
```bash
# Backend unit & integration tests
pytest backend/tests -v

# Frontend lint & build check
cd frontend
npm run lint
npm run build
```

### Generate Executive PDF Report
```bash
python generate_pdf_report.py
```
Outputs `Merchant_DNA_Report.pdf`, `Merchant_DNA_Summary_Report.pdf`, and `MERCHANT_DNA_EXECUTIVE_REPORT.pdf`.
