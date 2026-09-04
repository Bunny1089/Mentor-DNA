# Merchant DNA — YouTube Demo Shot List & Recording Guide

This shot list provides step-by-step screen recording cues, mouse paths, zoom focus targets, and on-screen callouts for producing a polished 3.5-minute submission video.

---

## Technical Recording Setup

* **Resolution:** 1920x1080 (1080p, 60fps)
* **Browser Mode:** Fullscreen (F11 / Chrome kiosk mode, dark theme active)
* **Audio:** High-quality directional microphone with noise gate
* **Backend State:** Fresh demo state with seed data loaded (`python -m uvicorn app.main:app --port 8000`)
* **Frontend State:** Production build or live Vite dev server (`http://localhost:5173`)

---

## Detailed Shot-by-Shot Matrix

| Shot # | Timecode | Scene / Target Component | Exact Recording Action | Mouse / Camera Direction | On-Screen Text Callout |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **01** | `0:00 - 0:15` | Landing / Hero Dashboard | `[OPEN DASHBOARD]` | Slow pan across total metrics cards (`1,070 Merchants`, `₹28.4L Volume Restored`). | *Coordinated Syndicate Fraud Detection* |
| **02** | `0:15 - 0:35` | Triage Queue & Alerts | `[HOVER OVER ALERT CARDS]` | Hover over top 2 Critical Risk alerts flagged with `RING_MEMBERSHIP`. | *Evaluating Isolated Transactions Misses Shared Infrastructure* |
| **03** | `0:35 - 0:55` | Recovery SLA & KPI Banner | `[SHOW METRIC CARDS & TRIAGE QUEUE]` | Highlight False-Positive Appeal Recovery (`₹28.4L Restored`, `4.2h SLA`). | *Dual-Engine: 60% Behavioral ML + 40% Graph Analysis* |
| **04** | `0:55 - 1:20` | Merchant Investigation Page | `[OPEN INVESTIGATION]` | Click 'Investigate' button on merchant `M-ALPHA-01` (*Nova Retail Systems*). | *Merchant Risk Score: 88.5 / Critical Tier* |
| **05** | `1:20 - 1:50` | Interactive Ego Network Graph | `[ZOOM INTO SHARED ENTITY]` | Click and zoom into Cytoscape graph canvas. Click on red node `DEV-FARM-991` to highlight connected ring members. | *Uncovering 5-Merchant Syndicate via Shared Physical Hardware* |
| **06** | `1:50 - 2:15` | Grounded AI Case Briefing | `[GENERATE AI BRIEFING]` | Click 'Generate AI Briefing' button. Watch structured grounded briefing render with evidence tags. | *Zero Hallucination: Constrained to Deterministic Evidence* |
| **07** | `2:15 - 2:35` | Financial Exposure & Action Modal | `[APPROVE ACTION]` | Click 'Apply Settlement Hold'. In modal, select rationale `Coordinated ring velocity spike` and click Confirm. | *Bounded Interventions: Hold Settlement, Keep Checkout Open* |
| **08** | `2:35 - 2:55` | Immutable Audit Ledger | `[SHOW AUDIT TRAIL]` | Scroll down to Audit Trail table. Show newly appended event `SETTLEMENT_HOLD_APPLIED` with 48h cap timer. | *48-Hour Hard Ceiling & Reversible Supervisor Escalation* |
| **09** | `2:55 - 3:15` | Simulation Sandbox | `[RUN MULE SIMULATION]` & `[RUN RING SIMULATION]` | Navigate to Simulation tab. Click 'Simulate Cashout Burst', then click 'Simulate Ring Expansion'. | *Real-Time Network Topology Evolution* |
| **10** | `3:15 - 3:35` | Out-of-Sample Holdout Evaluation | `[OPEN EVALUATION PAGE]` | Open Evaluation tab. Hover over PR/ROC curves and 30% unseen holdout metrics table. | *Holdout Test Partition: 97.2% Precision, 0.938 ROC-AUC* |
| **11** | `3:35 - 3:50` | Trust Signal API & Razorpay Fit | `[SHOW TRUST SIGNAL API CARD]` | Show public `GET /api/trust/{id}` JSON response and final summary slide. | *Transforming Defense into Verified Growth* |

---

## Post-Production Checklist

1. **Audio Mixing:** Keep background music ducked at -22dB during speech, normal at -14dB during transitions.
2. **Subtitles:** Embed accurate English captions for all technical terms (Louvain community detection, HistGradientBoosting, bipartite graph, 48-hour hold cap).
3. **End Screen:** Add 10-second end card linking to GitHub repository and executive PDF report.
