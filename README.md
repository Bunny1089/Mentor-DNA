<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:14161B,100:A83D3D&height=200&section=header&text=Merchant%20DNA&fontSize=56&fontColor=E8E6DE&animation=fadeIn&fontAlignY=38&desc=Cross-Merchant%20Fraud%20Intelligence%20for%20Payment%20Platforms&descAlignY=58&descSize=18" width="100%"/>

<img src="https://readme-typing-svg.demolab.com?font=IBM+Plex+Mono&size=16&duration=3000&pause=1200&color=B8862E&center=true&vCenter=true&width=700&lines=Behavioral+scoring+%2B+network+graph+analysis;Catching+fraud+that+single-merchant+tools+can't+see;Built+for+the+Razorpay+AI+Buildathon+2026" alt="typing-svg" />

<br/>

![Track](https://img.shields.io/badge/Track-AI%20Risk%20Manager-A83D3D?style=for-the-badge&labelColor=14161B)
![Status](https://img.shields.io/badge/Status-Prototype-B8862E?style=for-the-badge&labelColor=14161B)
![Python](https://img.shields.io/badge/Python-3.10+-4B7A6F?style=for-the-badge&logo=python&logoColor=white&labelColor=14161B)
![React](https://img.shields.io/badge/React-18-4B7A6F?style=for-the-badge&logo=react&logoColor=white&labelColor=14161B)
![Tests](https://img.shields.io/badge/Backend%20Tests-Passing-4B7A6F?style=for-the-badge&labelColor=14161B)

</div>

---

## Table of Contents

- [About](#about)
- [What It Does](#what-it-does)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Where This Applies](#where-this-applies)
- [Agentic Commerce & Trust Signals](#agentic-commerce--merchant-trust-signals)
- [How It's Monetized](#how-its-monetized)
- [Engineering Finding](#engineering-finding-shared-infrastructure-false-positives)
- [Benchmark Results & Evaluation](#benchmark-results--evaluation)
- [Banking & Compliance Architecture](#banking--payment-aggregator-compliance-architecture)
- [Known Limitations & Roadmap](#known-limitations--engineering-roadmap)
- [Quickstart](#quickstart--verification)

---

## About

**Merchant DNA** provides cross-merchant fraud intelligence for payment platforms — behavioral scoring and network analysis that catch what single-merchant tools structurally can't see.

### The Blind Spot

Traditional payment fraud detection operates at the individual transaction level — buyer card velocity, 3DS challenges, IP geolocation — evaluated in isolation. Modern merchant-side fraud operates through distributed networks instead:

- **Distributed syndicate shells** — fraud rings register 10 to 50 seemingly legitimate storefronts with valid KYC documents, each maintaining low, steady volumes that stay under transaction-level velocity tripwires.
- **Mule accounts & rapid cashouts** — sleeper accounts remain dormant 30–60 days to establish baseline history, then process concentrated bursts followed by immediate settlement withdrawal before chargebacks arrive.
- **Aggregator liability** — when merchant defaults and chargebacks occur, payment aggregators bear the financial liability for unrecoverable negative balances.

### The Approach

Three interconnected components:

1. **Behavioral telemetry (60% weight)** — a gradient boosted decision tree model evaluating 30+ merchant-level features: category ticket deviations, off-peak velocity, buyer concentration (HHI), settlement turnaround speed.
2. **Network graph analysis (40% weight)** — bipartite graph modeling and Louvain community detection to uncover shared devices, phone numbers, bank accounts, and UPI VPAs.
3. **Grounded synthesis & bounded actions** — an AI copilot providing grounded synthesis constrained to structured evidence inputs, coupled with reversible settlement holds that protect liquidity while preserving checkout operations for review.

---

## What It Does

- Detects fraudulent/mule merchant accounts via behavioral pattern analysis instead of relying on KYC alone
- Uncovers coordinated fraud rings across "unrelated" merchants by graphing shared identifiers — catching syndicates no single-merchant tool can see
- Scores every merchant 0–100 with explainable, evidence-backed reasoning, not a black box
- Takes bounded, reversible actions (monitor → hold → review) with a merchant appeal flow for contested holds
- Surfaces the same score as a positive trust signal for verified merchants
- Full audit trail on every flag and action

---

## How It Works

| Step | What Happens |
|:---:|---|
| 1 | **Entity ingestion & indexing** — transaction streams, onboarding metadata, and settlement requests indexed into reverse lookup tables linking merchants to physical/digital identifiers |
| 2 | **Behavioral feature extraction** — rolling windows compute catalog baseline divergence, off-peak ratios, round-denomination frequency, payout turnaround velocity |
| 3 | **Graph topology & community detection** — bipartite projection generates merchant-to-merchant relationship graphs, clustered to identify syndicates |
| 4 | **Hybrid calibrated risk scoring** — behavioral (60%) + graph (40%) combined into a 0–100 score across Low / Medium / High / Critical tiers |
| 5 | **Forensic investigation & grounded synthesis** — analysts inspect cases across Who / How / Who Else / What Next, backed by an interactive Cytoscape graph and evidence-constrained AI summaries |
| 6 | **Bounded actions & immutable audit** — holds or clears logged to an append-only audit ledger |
| 7 | **Merchant appeal / dispute flow** — merchants dispute holds via an appeal form, routed into a `PENDING_APPEAL_REVIEW` queue, logged to the same audit ledger |

---

## Tech Stack

| Layer | Technologies | Role |
|---|---|---|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite, Lucide Icons, Recharts | Analyst console — triage queues, forensic case views |
| **Graph Visualization** | Cytoscape.js, Cola physics layout | Ego-graph visualizer, shared-identifier inspection |
| **Backend** | FastAPI, Python 3.10+, Pydantic v2, Uvicorn, AnyIO | Async REST API, schema validation, modular services |
| **ML & Graph** | Scikit-learn (HistGradientBoosting), NetworkX, NumPy, SciPy | Behavioral classifier, 30+ feature extractors, Louvain clustering |
| **AI Synthesis** | Grounded synthesis constrained to structured evidence | Factual case briefings — no unconstrained generation |
| **Testing** | Pytest, Oxlint, Vite production build | Unit/integration tests, data-leakage prevention tests |

---

## Where This Applies

- **Payment aggregators** (Razorpay, Stripe, Cashfree) — gatekeeping settlement batches before payout disbursement
- **Neobanks & instant payout platforms** (RazorpayX) — real-time risk scoring on instant settlement drawdowns
- **Acquiring banks & card networks** (RuPay, Visa, Mastercard) — portfolio-level merchant risk surveillance
- **E-commerce marketplaces & agentic commerce platforms** — validating seller authenticity, verified trust credentials for autonomous AI purchasing agents

---

## Agentic Commerce & Merchant Trust Signals

In agentic commerce — where AI agents execute programmatic purchases on a user's behalf — verifying merchant legitimacy without human intervention matters. Merchant DNA inverts its internal risk assessment into a lightweight, public **Merchant Trust Signal API** (`GET /api/trust/{merchant_id}`):

- **Zero-leakage attestation** — exposes clean categorical tiers (`VERIFIED`, `STANDARD`, `CAUTION`, or withheld) and eligibility flags, without exposing internal risk models or graph topology
- **Autonomous purchasing clearance** — AI purchasing agents can query the endpoint before completing programmatic checkout
- **Growth re-framing** — turns defensive fraud mitigation into a verification asset high-reputation merchants can leverage

> This is a read-only trust-signal API an external agent could query — no autonomous buying agent system or transaction execution engine is built here.

---

## How It's Monetized

All five tiers run on the **same underlying engine** — the free tier isn't a cost center, it's the network asset that strengthens cross-merchant ring detection for every paying tier above it.

| Tier | Segment | Key Capabilities | Pricing |
|---|---|---|---|
| **1 · Starter** | Individual/informal sellers (WhatsApp, Instagram, gig sellers) | Public trust badge only — a network-effect funnel | Free / ₹49–99/mo |
| **2 · Growing SMB** | Small D2C brands, single-location retailers | Basic dashboard, trust badge, limited alerts, self-serve appeal flow | ₹499–1,999/mo flat SaaS |
| **3 · Established Merchant** | Multi-location retailers, scaling D2C | Full investigation dashboard, instant-settlement eligibility, priority appeals | ₹5,000–25,000/mo or 0.02–0.05% bps on instant settlement |
| **4 · Enterprise / Large Platform** | Large retailers, marketplaces with sub-sellers | Dedicated console, custom SLAs, sub-merchant vetting API, white-labeled badge | Annual license + bps on protected volume |
| **5 · Aggregator / Bank (B2B2B)** | Other aggregators, acquiring banks, neobanks | Full engine as Risk-as-a-Service, cross-platform surveillance | Per-query or annual API licensing — highest margin |

### Projected Impact

- **Projected fraud-loss prevention:** ~₹5.90 Crore against ₹3,108.98 estimated false-positive friction cost, on 321 unseen holdout merchants (from a 1,070-merchant synthetic corpus) — *projected simulation, not measured in live production.*
- **False-positive appeal recovery:** ₹28.4 Lakhs recovered with a 4.2-hour average resolution SLA.

---

## Engineering Finding: Shared-Infrastructure False Positives

<details>
<summary><strong>Click to expand — a real bug we found and fixed during development</strong></summary>

<br/>

During initial graph pipeline testing, we found unrelated merchants using the same generic payment gateway/PSP handle were occasionally linked into collusive clusters by graph projection — a false-positive source.

**Fix implemented:** Added a shared-infrastructure filtering step in `NetworkRiskDetector` that down-weights and excludes edges formed purely by generic processor/gateway infrastructure. A ring candidate now requires at least one strong personal identifier (bank account, phone, device fingerprint) or multi-identifier corroboration before being flagged.

</details>

---

## Benchmark Results & Evaluation

> Standard benchmark confirms separation of obviously anomalous behavior; the **harder out-of-sample holdout is the meaningful result.** All metrics are from controlled synthetic benchmarks.

<details>
<summary><strong>📊 Dual benchmark & multi-seed comparison (5 seeds)</strong></summary>

<br/>

| Metric | Standard (Sanity Check) | Harder Holdout (30% Unseen) | Multi-Seed (Mean ± Std) |
|---|:---:|:---:|:---:|
| Precision (PPV) | 100.0% | 97.2% | **99.2% ± 1.6%** |
| Recall (Sensitivity) | 100.0% | 86.4% | **89.1% ± 2.6%** |
| F1-Score | 1.000 | 0.915 | **0.939 ± 0.017** |
| ROC-AUC | 1.000 | 0.938 | **0.989 ± 0.010** |
| Planted Ring Detection | 100.0% | 95.1% (58/61) | **95.0% ± 1.4%** |
| Mule/Shell Detection | 100.0% | 60.0% (12/20) | **68.2% ± 8.6%** |

</details>

<details>
<summary><strong>⚔️ Adversarial robustness stress test (evasion-aware)</strong></summary>

<br/>

We built an adversarial batch where fraud rings specifically circumvent the model's own top SHAP signals — ticket normalization, buyer entropy dilution, organic settlement cadence.

| Metric | Standard | Harder Holdout | Adversarial Evasion |
|---|:---:|:---:|:---:|
| Precision | 100.0% | 97.2% | **83.3%** |
| Recall | 100.0% | 86.4% | **10.0%** |
| Ring Detection | 100.0% | 95.1% | **25.0%** (5/20) |
| Mule Detection | 100.0% | 60.0% | **0.0%** |

> This quantifies real degradation under evasion conditions we could anticipate — **not** a claim of general adversarial robustness. No fraud model can claim that without live production exposure.

</details>

<details>
<summary><strong>🎯 Score stability & boundary sensitivity</strong></summary>

<br/>

- **Non-borderline merchants** (score <45 or >75, n=20): **0.0% tier flips** under ±5% feature perturbation
- **Borderline merchants** (score 50–70, near the 60.0 threshold, n=16): **12.5% tier flips** (2/16)

Boundary sensitivity is expected for any threshold-based classifier. The 48-hour cap-and-escalate hold policy is the structural safeguard against acting irreversibly on a borderline flip.

</details>

<details>
<summary><strong>🕵️ Approximated blind hard-negative check</strong></summary>

<br/>

10 independently designed edge cases → **80.0% accuracy (8/10)**.

Correctly classified: Diwali silk surge, PSU bank migration, B2B chemical supplier, night-market food truck, creator-drop burst, antiquarian book dealer, franchise WiFi subnet, quarterly tuition collector.

Misclassified: a tech incubator sharing an address with 7 firms, and a corporate travel agent with high buyer concentration — both flagged via network/concentration signals that need further contextual tuning.

> Framed explicitly as an *approximated* blind check — the same team designed both model and test cases in separate passes, not a true independent study.

</details>

<details>
<summary><strong>🔗 Ring-size sensitivity</strong></summary>

<br/>

| Ring Size | Planted | Detected | Rate |
|---|:---:|:---:|:---:|
| 2–3 merchants | 15 | 13 | 86.7% |
| 4–6 merchants | 15 | 15 | 100.0% |
| 7–10 merchants | 4 | 4 | 100.0% |
| 10+ merchants | 2 | 2 | 100.0% |

</details>

<details>
<summary><strong>💰 Audited false-positive cost model (hand-verifiable)</strong></summary>

<br/>

```
Held delayed volume  = ₹1,55,449.01  (3-day hold window; 60-day cumulative volume was ₹15.07L)
Capital friction cost = ₹1,55,449.01 × 2.0% = ₹3,108.98
```

Reversible holds keep checkout active — zero cart abandonment during investigation.

**Recovery-rate sensitivity:**

| Scenario | Recovery Rate | Gross Loss Prevented | Net Fraud Savings |
|---|:---:|:---:|:---:|
| Conservative | 5% | ₹6.60 Cr | **₹6.25 Cr** |
| Baseline (assumed) | 15% | ₹5.90 Cr | **₹5.59 Cr** |
| Optimistic | 30% | ₹4.86 Cr | **₹4.60 Cr** |

> The 15% recovery figure is a modeling assumption, not an empirically measured constant. Net savings stay strongly positive across all three scenarios.

</details>

<details>
<summary><strong>📐 Threshold selection methodology ("why 60.0?")</strong></summary>

<br/>

Selected via grid search on the 70% training partition only (749 merchants), leaving the 30% holdout untouched. At θ=60.0: **100% precision, 0 false alarms, 95.8% recall** on training data. Out-of-sample validation confirmed 97.2% precision / 86.4% recall / 0.915 F1.

</details>

---

## Banking & Payment Aggregator Compliance Architecture

- **48-hour maximum hold cap** — every settlement hold enforces a hard ceiling with mandatory 24-hour supervisor escalation; no indefinite fund freezes
- **Proactive merchant notification** — every hold immediately dispatches a notification with the operational rationale, evidence checklist, and dispute link, logged as `MERCHANT_NOTIFICATION_DISPATCHED`
- **Compliance scope disclaimer** — these safeguards are internal risk-engineering designs aligned with the core principles of the **RBI Payment Aggregator Directions, 2025** (T+1 settlement expectations). They are operational fairness measures, **not** a certified banking-compliance product — production deployment would require formal legal and compliance review.

---

## Known Limitations & Engineering Roadmap

| Limitation | Result | Roadmap |
|---|---|---|
| Adversarial evasion sensitivity | Recall drops to 10.0%, ring detection to 25.0% under evasion-aware fraud | Cross-merchant behavioral embeddings, device attestation, velocity-trajectory graph edges |
| Blind hard-negative edge cases | 80.0% accuracy (8/10) | Deeper contextual tuning for address-sharing and B2B concentration heuristics |
| Subtle sleeper mule detection | 68.2% ± 8.6% detection rate | Longer observation windows, velocity-drift tracking, buyer-entropy evolution features |
| Small syndicate detection | 86.7% on 2–3 merchant rings | Multi-hop temporal graph analysis, fuzzy device/IP correlation, motif clustering |

---

## Quickstart & Verification

<details>
<summary><strong>🖥️ Backend setup</strong></summary>

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --reload
```

</details>

<details>
<summary><strong>🌐 Frontend setup</strong></summary>

```bash
cd frontend
npm install
npm run dev
```

</details>

<details>
<summary><strong>✅ Run the full test suite</strong></summary>

```bash
# Backend unit & integration tests
pytest backend/tests -v

# Frontend lint & build check
cd frontend
npm run lint
npm run build
```

</details>

<details>
<summary><strong>📄 Generate the executive PDF report</strong></summary>

```bash
python generate_pdf_report.py
```

Outputs `Merchant_DNA_Report.pdf`, `Merchant_DNA_Summary_Report.pdf`, and `MERCHANT_DNA_EXECUTIVE_REPORT.pdf`.

</details>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:A83D3D,100:14161B&height=100&section=footer" width="100%"/>

**Built for the Razorpay AI Buildathon 2026 · Track: AI Risk Manager**

</div>
