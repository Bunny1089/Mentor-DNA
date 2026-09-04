"""Canonical report and project content for Merchant DNA.

Single source of truth for documentation, PDF generation, and executive summaries.
Uses restrained, factual language and structured typographic hierarchy.
"""

PROJECT_NAME = "Merchant DNA"
PROJECT_TAGLINE = (
    "Cross-merchant fraud intelligence for payment platforms — "
    "behavioral scoring and network analysis that catch what single-merchant tools structurally can't see."
)

REPORT_SECTIONS = {
    "the_blind_spot": {
        "title": "The Blind Spot",
        "content": (
            "Traditional payment fraud detection operates at the individual transaction level, "
            "evaluating buyer card velocity, 3DS challenges, and IP geolocation in isolation. "
            "However, modern merchant-side fraud operates through distributed networks:\n\n"
            "• Distributed Syndicate Shells: Fraud rings register 10 to 50 seemingly legitimate "
            "storefronts with valid KYC documents. Each merchant maintains low, steady volumes "
            "that stay well below transaction-level velocity tripwires.\n"
            "• Mule Accounts & Rapid Cashouts: Sleeper accounts remain dormant for 30–60 days "
            "to establish baseline history, then process concentrated transaction bursts followed "
            "by immediate settlement withdrawal requests before chargebacks arrive.\n"
            "• Aggregator Liability: When merchant defaults and chargebacks occur, payment aggregators "
            "bear financial liability for unrecoverable negative balances."
        ),
    },
    "the_approach": {
        "title": "The Approach",
        "content": (
            "Merchant DNA addresses cross-merchant risk through three interconnected components:\n\n"
            "1. Behavioral Telemetry (60% Weight): A gradient boosted decision tree model evaluating "
            "30+ merchant-level features, including category ticket deviations, off-peak velocity, "
            "buyer concentration (HHI), and settlement turnaround speed.\n"
            "2. Network Graph Analysis (40% Weight): Bipartite graph modeling and Louvain community "
            "detection to uncover shared devices, phone numbers, bank accounts, and UPI VPAs.\n"
            "3. Grounded Synthesis & Bounded Actions: An AI copilot providing grounded synthesis "
            "constrained to structured evidence inputs, coupled with reversible settlement holds "
            "that protect liquidity while preserving checkout operations for review."
        ),
    },
    "how_it_works": {
        "title": "How It Works",
        "content": (
            "• Step 1 — Entity Ingestion & Indexing: Transaction streams, onboarding metadata, and "
            "settlement requests are indexed into reverse lookup tables linking merchants to physical "
            "and digital identifiers.\n"
            "• Step 2 — Behavioral Feature Extraction: Rolling windows compute catalog baseline divergence, "
            "off-peak processing ratios, round-denomination frequencies, and payout turnaround velocity.\n"
            "• Step 3 — Graph Topology & Community Detection: Multi-entity bipartite projection generates "
            "merchant-to-merchant relationship graphs, applying community clustering to identify syndicates.\n"
            "• Step 4 — Hybrid Calibrated Risk Scoring: Combines behavioral ML probabilities (60%) and "
            "graph density/centrality scores (40%) into a 0–100 risk score with calibrated tiers "
            "(Low, Medium, High, Critical).\n"
            "• Step 5 — Forensic Investigation & Grounded Synthesis: Analysts inspect cases across four core "
            "questions (Who, How, Who Else, What Next) supported by an interactive Cytoscape network graph "
            "and evidence-constrained AI summaries.\n"
            "• Step 6 — Bounded Actions & Immutable Audit: Analysts apply targeted holds or clear cases, "
            "with all state transitions recorded in an append-only audit ledger."
        ),
    },
    "stack": {
        "title": "Stack",
        "layers": [
            {
                "layer": "Frontend",
                "tech": "React 18, TypeScript, Tailwind CSS, Vite, Lucide Icons, Recharts",
                "description": "Enterprise analyst console with sub-second page transitions, interactive triage queues, and forensic views.",
            },
            {
                "layer": "Graph Visualization",
                "tech": "Cytoscape.js, Cola Physics Layout",
                "description": "Multi-entity ego graph visualizer with node clustering and shared-identifier inspection.",
            },
            {
                "layer": "Backend Services",
                "tech": "FastAPI, Python 3.14, Pydantic v2, Uvicorn, AnyIO",
                "description": "Asynchronous REST API gateway with schema validation, CORS security, and modular service routing.",
            },
            {
                "layer": "Machine Learning & Graph",
                "tech": "Scikit-Learn (HistGradientBoosting), NetworkX, NumPy, SciPy",
                "description": "Behavioral gradient boosting classifier, 30+ feature extractors, and Louvain community detection.",
            },
            {
                "layer": "AI Synthesis",
                "tech": "Google Gemini API / Deterministic Grounded Fallback",
                "description": "Grounded synthesis constrained to structured evidence inputs, providing factual case briefings.",
            },
            {
                "layer": "Testing & Quality",
                "tech": "Pytest, Oxlint, Vite Production Compiler",
                "description": "Automated unit tests, integration suites, API contract validation, and data leakage prevention tests.",
            },
        ],
    },
    "where_this_applies": {
        "title": "Where This Applies",
        "content": (
            "• Payment Aggregators (Razorpay, Stripe, Cashfree): Gatekeeping automated daily settlement "
            "batches to intercept coordinated syndicates before payout disbursement.\n"
            "• Neobanks & Instant Payout Platforms (RazorpayX): Real-time risk scoring on instant settlement "
            "drawdowns, protecting automated liquidity pools from compromised credentials.\n"
            "• Acquiring Banks & Card Networks (RuPay, Visa, Mastercard): Portfolio-level merchant risk surveillance "
            "and syndicated chargeback liability mitigation.\n"
            "• E-Commerce Marketplaces: Detecting seller collusion, device-farm review manipulation, and bust-out accounts."
        ),
    },
    "business_model": {
        "title": "Business Model",
        "framing": (
            "All five tiers run on the same underlying risk and graph intelligence engine — "
            "the free tier is not a cost center, but an essential network asset that strengthens "
            "the cross-merchant ring-detection signals that paid tiers depend on."
        ),
        "tiers": [
            {
                "tier": "1. Starter",
                "target": "Individual & informal sellers (WhatsApp/Instagram, gig sellers)",
                "features": "Public trust badge only. Serves as a funnel/network-effect tier (more merchants on platform strengthens cross-merchant ring detection for every paying tier).",
                "pricing": "Free or nominal ₹49–₹99/mo",
            },
            {
                "tier": "2. Growing SMB",
                "target": "Small D2C brands, single-location retailers",
                "features": "Basic risk dashboard, public trust badge, limited fraud alerts, self-serve appeal & dispute flow.",
                "pricing": "₹499–₹1,999/mo flat SaaS or volume-metered",
            },
            {
                "tier": "3. Established Merchant",
                "target": "Multi-location retailers, scaling D2C brands",
                "features": "Full case-investigation dashboard, instant-settlement eligibility via trust tier, priority appeal handling, own-account network visibility.",
                "pricing": "₹5,000–₹25,000/mo SaaS or 0.02%–0.05% bps on instant settlement volume",
            },
            {
                "tier": "4. Enterprise / Large Platform",
                "target": "Large retailers, big marketplaces with sub-sellers",
                "features": "Dedicated analyst console, custom SLAs, API access to trust signals for sub-merchant vetting, white-labeled trust badge.",
                "pricing": "Annual license + protected volume bps (negotiated)",
            },
            {
                "tier": "5. Aggregator / Bank (B2B2B)",
                "target": "Other payment aggregators, acquiring banks, neobanks",
                "features": "Full engine licensed as Risk-as-a-Service, raw API integration, cross-platform syndicate surveillance.",
                "pricing": "Per-query or annual API licensing (highest margin)",
            },
        ],
        "content": (
            "All five tiers run on the same underlying risk and graph intelligence engine — "
            "the free tier is not a cost center, but an essential network asset that strengthens "
            "the cross-merchant ring-detection signals that paid tiers depend on.\n\n"
            "• 1. Starter (Individual & Informal Sellers): Public trust badge only. Free or nominal flat fee (₹49–₹99/month). Serves as a network-effect funnel.\n"
            "• 2. Growing SMB (Small D2C & Retailers): Basic risk dashboard, trust badge, limited alerts, self-serve appeal flow. ₹499–₹1,999/month flat SaaS.\n"
            "• 3. Established Merchant (Multi-Location & Scaling D2C): Full investigation dashboard, instant-settlement eligibility, priority appeals, network visibility. ₹5,000–₹25,000/month or 0.02%–0.05% bps on instant payouts.\n"
            "• 4. Enterprise / Large Platform (Marketplaces & Retailers): Dedicated analyst console, custom SLAs, sub-merchant vetting API, white-labeled badge. Annual contract + volume bps.\n"
            "• 5. Aggregator / Bank (B2B2B): Full engine licensed as Risk-as-a-Service, API-first cross-platform surveillance. Per-query or annual enterprise licensing.\n\n"
            "• Projected Loss Mitigation: In out-of-sample benchmark evaluation on 321 unseen holdout merchants (from 1,070 corpus), "
            "extrapolated fraud-loss prevention is estimated at approximately ₹5.90 Crore against ₹3,108.98 estimated false-positive friction cost (projected simulation, not measured in live production).\n"
            "• False-Positive Appeal Recovery: Integrated appeal dispute tracking quantifies operational capital restored to verified merchants (e.g. ₹28.4L recovered with a 4.2-hour resolution SLA)."
        ),
    },
    "engineering_finding": {
        "title": "Engineering Finding: Shared-Infrastructure False Positives",
        "content": (
            "During initial graph pipeline testing, we identified a notable source of false-positive ring detections: "
            "unrelated merchants that used the same generic payment gateway or payment service provider (PSP) handle "
            "were occasionally linked into collusive clusters by graph projection.\n\n"
            "Fix Implemented: We added a shared-infrastructure filtering step in the network detector that down-weights "
            "and excludes edges formed purely by generic processor or gateway infrastructure. A collusive ring candidate "
            "now requires at least one strong personal identifier (bank account, phone number, or device hardware fingerprint) "
            "or multi-identifier corroboration, preventing generic payment infrastructure from generating spurious alerts."
        ),
    },
    "known_limitations_section": {
        "title": "Known Limitations & Engineering Roadmap",
        "content": (
            "• Adversarial Evasion Sensitivity Gap (Precision 83.3%, Recall dropping to 10.0%, Ring Detection to 25.0%): "
            "When fraudsters specifically normalize ticket sizes, randomize payout intervals, and dilute buyer concentration, "
            "single-merchant behavioral ML models experience severe recall degradation. Graph ring detection catches shared hardware/accounts, "
            "but standalone behavioral signals drop significantly. "
            "Roadmap: Cross-merchant behavioral embedding similarity, hardware-rooted device attestation, and velocity trajectory graph edges.\n\n"
            "• Blind Hard-Negative Edge Cases (80.0% Accuracy, 8/10 correctly classified): "
            "Blind testing surfaced 2 cases where legitimate edge cases received high risk scores: M-BLIND-05 (tech incubator sharing a corporate address with 7 other firms) "
            "and M-BLIND-09 (corporate group travel agent with high corporate buyer concentration). "
            "This indicates that physical address sharing filters and high-concentration B2B heuristics require deeper contextual domain conditioning.\n\n"
            "• Sleeper Mule Detection on Low-Velocity Accounts (68.2% ± 8.6% Detection Rate): "
            "Subtle sleeper accounts deliberately mimic legitimate small merchants by processing modest ticket sizes "
            "with zero customer disputes during their incubation window. "
            "Roadmap: Longer observation windows, velocity-drift trajectory tracking, and buyer entropy evolution metrics.\n\n"
            "• Small Syndicate Detection Sensitivity (86.7% Detection Rate on 2–3 Merchant Rings, 13/15 caught): "
            "2-to-3 merchant rings yield sparse bipartite subgraphs with fewer shared entities than large syndicates. "
            "Roadmap: Multi-hop temporal graph analysis, fuzzy device/IP subnet correlation, and higher-order motif clustering."
        ),
    },
    "threshold_methodology_section": {
        "title": "Threshold Selection Methodology (Why 60.0?)",
        "content": (
            "Operating threshold 60.0 was selected via a structured threshold sweep grid search on the 70% training partition (749 merchants). "
            "Threshold 60.0 corresponds to the HIGH risk tier boundary where targeted interventions occur, achieving 100.0% precision with 0 false positives "
            "and 95.8% recall on training data. This balances zero merchant friction on legitimate accounts with high fraud capture. "
            "The 30% holdout test partition remained strictly out-of-sample and verified 99.2% ± 1.6% precision, 89.1% ± 2.6% recall, and 0.939 ± 0.017 F1-Score across 5 random seeds."
        ),
    },
    "adversarial_stress_test": {
        "title": "Adversarial Robustness & Evasion Stress Testing",
        "content": (
            "To evaluate model resilience against evasion-aware fraudsters, we built an adversarial synthetic batch generator "
            "where fraudulent rings specifically circumvent the top behavioral signals identified by SHAP feature importances:\n\n"
            "• Ticket Normalization: Avoids round-denomination flags by generating realistic fractional price distributions.\n"
            "• Buyer Entropy Dilution: Synthesizes artificially diversified buyer pools to suppress HHI concentration alerts.\n"
            "• Organic Settlement Cadence: Randomizes payout timing and introduces gradual volume ramps instead of sudden bursts.\n\n"
            "Evaluation Findings: Precision remains 83.3%, while recall drops significantly to 10.0%, and ring detection drops to 25.0% (5/20 merchants caught).\n\n"
            "Framing: This quantifies real degradation under evasion-aware conditions our team could anticipate — not a claim of general adversarial robustness. "
            "No fraud model can claim general robustness without live production exposure."
        ),
    },
    "score_stability_section": {
        "title": "Score Stability & Feature Perturbation Analysis",
        "content": (
            "We evaluated score stability across two distinct populations under a ±5% uniform feature perturbation:\n\n"
            "• Non-Borderline Cohort (Risk Score <45 or >75, n=20): 0.0% tier flips observed under ±5% feature perturbation, "
            "confirming baseline classification stability far from the decision boundary.\n"
            "• Borderline Cohort (Risk Score 50–70 near threshold 60.0, n=16): 12.5% tier flips (2/16 merchants) observed under a ±5% feature perturbation.\n\n"
            "Boundary Sensitivity Rationale: Boundary sensitivity is an expected mathematical property of any threshold-based classifier "
            "near its decision boundary. The 48-hour cap-and-escalate settlement hold policy is the structural safeguard against acting irreversibly on a borderline flip."
        ),
    },
    "blind_eval_section": {
        "title": "Approximated Blind Hard-Negative Evaluation",
        "content": (
            "Evaluated against 10 independently designed real-world edge cases, the engine achieved 80.0% accuracy (8/10 correctly classified):\n\n"
            "• Correctly Classified (8 Cases): Seasonal festival surge (Diwali silks), PSU bank merger migration, B2B industrial chemicals, "
            "weekend night-market food vendor, creator drop apparel burst, rare book art dealer, franchise shared WiFi subnet, and quarterly round tuition fees.\n"
            "• Misclassified Edge Cases (2 Cases): M-BLIND-05 (tech incubator sharing address with 7 firms) and M-BLIND-09 (corporate group travel agent with high buyer concentration).\n\n"
            "Framing Note: Framed explicitly as an 'approximated blind check' rather than a true blind study, as the 10 test scenarios were designed "
            "in a separate pass by the same engineering team."
        ),
    },
    "recovery_sensitivity_section": {
        "title": "False-Negative Recovery Rate Sensitivity Analysis",
        "content": (
            "Financial impact modeling evaluates net fraud savings across three recovery rate scenarios:\n\n"
            "• Conservative (5% recovery / 95% unrecovered loss): ₹6.59 Crore gross loss prevented, ₹6.25 Crore net fraud savings.\n"
            "• Baseline Assumed (15% recovery / 85% unrecovered loss): ₹5.90 Crore gross loss prevented, ₹5.59 Crore net fraud savings.\n"
            "• Optimistic (30% recovery / 70% unrecovered loss): ₹4.86 Crore gross loss prevented, ₹4.60 Crore net fraud savings.\n\n"
            "Modeling Note: The 15% recovery figure is an operational modeling assumption, not an empirically measured constant. "
            "Net fraud savings remain strongly positive (>₹4.6 Crore) across all tested recovery scenarios."
        ),
    },
    "banking_compliance_section": {
        "title": "Banking & Payment Aggregator Compliance Architecture",
        "content": (
            "• 48-Hour Maximum Hold Cap: All settlement holds enforce an automated 48-hour hard ceiling with mandatory 24-hour supervisor escalation, eliminating indefinite fund freezes.\n"
            "• Proactive Merchant Notification: Every hold automatically dispatches an immediate merchant notification containing the specific operational rationale, required evidence checklist, and direct dispute submission link, logged with immutable audit event MERCHANT_NOTIFICATION_DISPATCHED.\n"
            "• Compliance Scope Disclaimer: These operational safeguards are internal risk engineering designs aligned with the core principles of RBI Payment Aggregator Guidelines (DPSS.CO.PD.No.1810/02.14.008/2019-20). They are designed for risk operational fairness, not certified banking compliance products."
        ),
    },
    "results": {
        "title": "Results & Evaluation",
        "note": (
            "Standard benchmark confirms separation of obviously anomalous behavior; "
            "the harder out-of-sample holdout is the meaningful performance result. "
            "All metrics are from controlled synthetic benchmarks with configured 3-day hold windows."
        ),
    },
}

