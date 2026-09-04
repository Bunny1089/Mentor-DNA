# Merchant DNA — 3-Minute Live Buildathon Demo Script

**Presenter Timing:** Exactly 3:00 Minutes  
**Golden Target Merchant:** `M-ALPHA-01` (*Alpha Fashion Outlet*)  
**Golden Target Ring:** `RING-ALPHA-DEVICE-FARM` (*Device Farm Syndicate*)

---

## 0:00 – 0:30 | The Core Problem (Hook)

> **[Presenter facing judges]**  
> *"Traditional payment fraud detection operates at the individual transaction level. When a transaction comes through, rule engines evaluate card velocity, geolocations, and buyer risk in isolation.*  
>  
> *However, modern merchant fraud is **coordinated**. Bad actors don't operate one rogue store; they spin up entire syndicates of 10 to 50 seemingly legitimate shell merchants sharing rooted emulator boxes, VOIP gateways, and rotating payout handles. By keeping transaction amounts below individual velocity thresholds, they siphon millions before traditional monitoring triggers.*  
>  
> *Welcome to **Merchant DNA** — an AI-powered Merchant Risk Intelligence & Collusive Fraud Network Detection platform designed for hyper-scale payment aggregators like Razorpay."*

---

## 0:30 – 1:00 | Detection & Triage Dashboard

> **[Presenter opens Merchant DNA Dashboard]**  
> *"Here on the operations dashboard, Merchant DNA continuously evaluates 240 active merchants across two distinct pillars:*  
> 1. *A **Behavioral ML Model (60% weight)** evaluating ticket deviations, off-peak velocity, and buyer concentration.*  
> 2. *A **Network Graph Detector (40% weight)** running Louvain community graph algorithms on shared hardware, bank accounts, and UPI handles.*  
>  
> *Notice our top alert in the queue: **Alpha Fashion Outlet (`M-ALPHA-01`)**, flagged at **100/100 Critical Risk** with a recommended action of `URGENT_SETTLEMENT_FREEZE`. Let's click into this case."*

---

## 1:00 – 1:45 | Forensic Investigation Dossier

> **[Presenter clicks 'Investigate' for `M-ALPHA-01` to open the Forensic Dossier]**  
> *"The investigation dossier answers the four critical forensic questions in seconds:*  
>  
> 1. ***WHO?** Alpha Fashion Outlet is registered as an e-commerce fashion vendor with standard KYC verification.*  
> 2. ***HOW?** Looking at our structured evidence below, this merchant exhibits a severe catalog ticket anomaly — averaging ₹43,943 per transaction against an expected ₹1,850 baseline — with 92% round amounts and extreme buyer concentration.*  
> 3. ***WHO ELSE?** Look at this interactive Cytoscape network graph. While this merchant passed individual onboarding, Merchant DNA reveals it is operating from a rooted Android emulator (`DEV-FARM-991`) and a VOIP gateway (`PH-VOIP-ALPHA`) shared across **9 other active storefronts** in `RING-ALPHA-DEVICE-FARM`.*  
>  
> *No single transaction was flagged, but the network topology proves syndicated collusive fraud."*

---

## 1:45 – 2:15 | Grounded AI Copilot & Bounded Action

> **[Presenter clicks 'Generate Brief' in the AI Copilot card]**  
> *"Investigating complex graph topologies takes human analysts 30 to 45 minutes. Watch our **Grounded AI Copilot**: with one click, it synthesizes the multi-modal evidence into a strictly factual executive synopsis — showing grounding mode, exact ticket deviations, and shared infrastructure without hallucination.*  
>  
> **[Presenter clicks 'Approve Action']**  
> *"The Copilot recommends `URGENT_SETTLEMENT_FREEZE`. As a human analyst, I click **Approve Action**. Notice that Merchant DNA enforces bounded, reversible interventions — settlement payouts are held immediately, preventing fund drainage without terminating customer checkout.*  
>  
> **[Presenter scrolls to Audit Trail]**  
> *Every action is instantly recorded in this immutable audit trail for compliance and model feedback."*

---

## 2:15 – 2:50 | Live Real-Time Fraud Simulations

> **[Presenter navigates to 'Simulation' tab]**  
> *"To prove Merchant DNA's dynamic responsiveness, let's run two live real-time fraud attacks:*  
>  
> **[Presenter clicks 'Simulate Mule Burst Cashout']**  
> 1. ***Scenario A: Dormant Mule Burst.*** *A sleeper account wakes up and processes 35 high-velocity round transactions totaling ₹2.6M. Instantly, our risk engine recalculates the merchant score in real time — escalating risk from **12.0 (Low) to 94.5 (Critical)** with a **+82.5 point delta**, automatically proposing settlement review.*  
>  
> **[Presenter clicks 'Simulate New Fraud Ring']**  
> 2. ***Scenario B: Coordinated Ring Emergence.*** *A brand-new 4-merchant syndicate registers on the platform sharing an automated script box and payout hub. Merchant DNA's graph detector discovers the new topology in real time, generates `RING-SIM`, and raises priority alerts across the cluster."*

---

## 2:50 – 3:00 | Business Value & Closing

> **[Presenter closes with conviction]**  
> *"In summary:*  
> *Merchant DNA empowers payment platforms like Razorpay to detect coordinated syndicates traditional tools miss, accelerate investigation turnaround from 45 minutes to under 60 seconds, and execute bounded, high-ROI settlement interventions.*  
>  
> *Thank you — we are ready for questions."*
