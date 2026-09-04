# Merchant DNA — Frontend API Specification Contract

**Base URL**: `http://localhost:8000`  
**OpenAPI Interactive Docs**: `http://localhost:8000/docs`  
**Format**: `application/json`

---

## 1. System & Health

### `GET /health`
- **Description**: Basic service liveness check.
- **Response**:
```json
{
  "status": "ok",
  "service": "merchant-dna",
  "version": "0.1.0"
}
```

### `GET /api/system/status`
- **Description**: Runtime telemetry for dashboard metrics and model status.
- **Response**:
```json
{
  "backend_status": "ONLINE",
  "service": "Merchant Risk Intelligence Platform",
  "version": "0.1.0",
  "data_loaded": true,
  "merchant_count": 240,
  "transaction_count": 10540,
  "graph_nodes_count": 524,
  "graph_edges_count": 1280,
  "detected_rings_count": 3,
  "behavioral_model_loaded": true,
  "server_time": "2026-09-02T02:22:00.000000Z"
}
```

---

## 2. Merchants & Risk Summaries

### `GET /api/merchants`
- **Description**: Filtered, paginated list of all monitored merchants.
- **Query Parameters**:
  - `page` (int, default: 1)
  - `page_size` (int, default: 20)
  - `risk_level` (string: `LOW` | `MEDIUM` | `HIGH` | `CRITICAL`)
  - `category` (string: `ECOMMERCE_FASHION`, `ELECTRONICS`, etc.)
  - `search` (string: merchant ID or business name)
  - `ring_id` (string: e.g. `RING-ALPHA-DEVICE-FARM`)
- **Response**:
```json
{
  "total_count": 240,
  "page": 1,
  "page_size": 20,
  "total_pages": 12,
  "merchants": [
    {
      "merchant_id": "M-ALPHA-01",
      "business_name": "Alpha Deals #1",
      "category": "ELECTRONICS",
      "business_type": "PROPRIETORSHIP",
      "onboarding_date": "2026-06-15T00:00:00Z",
      "transaction_count": 64,
      "total_volume": 3200000.0,
      "behavioral_risk": 78.4,
      "network_risk": 94.2,
      "overall_risk": 87.9,
      "risk_level": "CRITICAL",
      "confidence": 0.96,
      "recommended_action": "URGENT_SETTLEMENT_FREEZE",
      "ring_id": "RING-ALPHA-DEVICE-FARM",
      "top_factor": "48-Hour Velocity Surge"
    }
  ]
}
```

### `GET /api/merchants/{merchant_id}`
- **Description**: Full merchant profile, activity metrics, and current investigation state.
- **Response**:
```json
{
  "merchant_id": "M-ALPHA-01",
  "business_name": "Alpha Deals #1",
  "legal_name": "Alpha Deals Tech Enterprise",
  "category": "ELECTRONICS",
  "business_type": "PROPRIETORSHIP",
  "declared_avg_ticket": 1500.0,
  "onboarding_date": "2026-06-15T00:00:00Z",
  "kyc_status": "VERIFIED",
  "is_active": true,
  "current_state": "NEW",
  "transaction_count": 64,
  "total_volume": 3200000.0,
  "settlement_count": 4,
  "risk_summary": { ... }
}
```

### `GET /api/merchants/{merchant_id}/risk`
- **Description**: Full explainable `RiskScoreBreakdown`.
- **Response**:
```json
{
  "merchant_id": "M-ALPHA-01",
  "behavioral_risk": 78.4,
  "network_risk": 94.2,
  "overall_risk": 87.9,
  "risk_level": "CRITICAL",
  "confidence": 0.96,
  "top_factors": [
    {
      "factor_id": "FACT-VEL-M-ALPHA-01",
      "title": "48-Hour Velocity Surge",
      "description": "Processed volume surged 6.4× over recent 48 hours.",
      "category": "VELOCITY",
      "weight": 0.35,
      "value_observed": "6.4× volume multiplier",
      "benchmark": "1.0× - 1.5× baseline daily average",
      "severity": "CRITICAL"
    }
  ],
  "recommended_action": "URGENT_SETTLEMENT_FREEZE",
  "action_rationale": "Multi-signal anomaly combining high-velocity burst transactions and cross-merchant infrastructure sharing.",
  "ring_id": "RING-ALPHA-DEVICE-FARM",
  "connected_high_risk_count": 9,
  "calculated_at": "2026-09-02T02:00:00Z"
}
```

---

## 3. Alerts Queue

### `GET /api/alerts`
- **Description**: Active risk alert queue for human triage.
- **Query Parameters**:
  - `risk_level` (`LOW` | `MEDIUM` | `HIGH` | `CRITICAL`)
  - `status` (`NEW` | `UNDER_REVIEW` | `ACTION_RECOMMENDED` | `ACTIONED` | `CLEARED` | `CLOSED`)
- **Response**:
```json
{
  "total_alerts": 54,
  "critical_count": 28,
  "high_count": 26,
  "medium_count": 14,
  "low_count": 172,
  "alerts": [
    {
      "alert_id": "ALT-M-ALPHA-01",
      "merchant_id": "M-ALPHA-01",
      "business_name": "Alpha Deals #1",
      "category": "ELECTRONICS",
      "risk_level": "CRITICAL",
      "overall_score": 87.9,
      "behavioral_score": 78.4,
      "network_score": 94.2,
      "top_reasons": ["48-Hour Velocity Surge", "Shared Device Fingerprint"],
      "ring_affiliation": "RING-ALPHA-DEVICE-FARM",
      "created_timestamp": "2026-09-02T02:00:00Z",
      "recommended_action": "URGENT_SETTLEMENT_FREEZE",
      "status": "ACTION_RECOMMENDED"
    }
  ]
}
```

---

## 4. Entity Graph & Ring Exploration

### `GET /api/graph/merchant/{merchant_id}`
- **Description**: Cytoscape-compatible ego subgraph around a merchant.
- **Response**:
```json
{
  "merchant_id": "M-ALPHA-01",
  "nodes": [
    {
      "id": "M-ALPHA-01",
      "label": "Alpha Deals #1",
      "entity_type": "MERCHANT",
      "risk_level": "CRITICAL",
      "risk_score": 87.9,
      "is_ring_member": true,
      "metadata": { "category": "ELECTRONICS" }
    },
    {
      "id": "DEV-FARM-991",
      "label": "DEV-FARM-991 (Emulator)",
      "entity_type": "DEVICE",
      "is_ring_member": true,
      "metadata": { "is_emulator": true }
    }
  ],
  "edges": [
    {
      "id": "EDGE-M-ALPHA-01-DEV-FARM-991",
      "source": "M-ALPHA-01",
      "target": "DEV-FARM-991",
      "relation_type": "OPERATED_ON_DEVICE",
      "weight": 1.0,
      "label": "OPERATED_ON_DEVICE",
      "is_suspicious": true
    }
  ],
  "ring_id": "RING-ALPHA-DEVICE-FARM",
  "cluster_risk_score": 94.2,
  "shared_identifiers_count": 3
}
```

### `GET /api/graph/rings`
- **Description**: List of all detected collusive rings.
- **Response**:
```json
[
  {
    "ring_id": "RING-ALPHA-DEVICE-FARM",
    "name": "Alpha Device Farm",
    "members": ["M-ALPHA-01", "M-ALPHA-02", "M-ALPHA-03", "..."],
    "shared_entities": [
      { "entity_type": "DEVICE", "entity_id": "DEV-FARM-991", "shared_by_merchants_count": 5 }
    ],
    "ring_size": 10,
    "density": 0.45,
    "dominant_shared_identifier": "DEVICE",
    "network_risk": 94.2,
    "confidence": 0.95
  }
]
```

### `GET /api/graph/rings/{ring_id}`
- **Description**: Complete multi-node subgraph of all ring members and shared entities.

---

## 5. Investigation Dossier, Decisions & Actions

### `POST /api/investigations/{merchant_id}`
- **Description**: Opens an investigation for a merchant.
- **Response**: Complete `InvestigationDossier`.

### `GET /api/investigations/{investigation_id}`
- **Description**: Returns full investigation dossier (Profile, Risk Summary, Behavioral & Network Evidence, Timeline, Business Impact, AI Briefing, Action Recommendation).

### `POST /api/investigations/{investigation_id}/briefing`
- **Description**: Generates grounded AI case brief.
- **Response**:
```json
{
  "summary": "Merchant M-ALPHA-01 has been escalated to CRITICAL risk (Overall Score: 87.9/100)...",
  "key_evidence": [
    "48-Hour Velocity Surge: 6.4× volume multiplier (vs. benchmark 1.0× - 1.5× baseline daily average)",
    "Shared Device Fingerprint: 4 shared merchants on DEV-FARM-991"
  ],
  "network_context": "Identified as an active node within collusive ring 'RING-ALPHA-DEVICE-FARM'.",
  "risk_interpretation": "The co-occurrence of high transaction velocity and infrastructure sharing strongly suggests coordinated syndicate operations.",
  "recommended_next_step": "Initiate temporary settlement hold (Action: URGENT_SETTLEMENT_FREEZE).",
  "evidence_count": 5,
  "evidence_ids_used": ["EVD-VEL-M-ALPHA-01", "EVD-DEV-M-ALPHA-01"],
  "grounding_mode": "DETERMINISTIC_FALLBACK"
}
```

### `GET /api/investigations/{investigation_id}/action`
- **Description**: Returns current bounded action recommendation.

### `POST /api/investigations/{investigation_id}/action/approve`
- **Request**: `{ "notes": "Approved hold after review" }` (optional)
- **Response**: `AnalystDecision` object.

### `POST /api/investigations/{investigation_id}/action/reject`
- **Request**: `{ "justification": "Verified wholesale distributor contracts" }` (mandatory)
- **Response**: `AnalystDecision` object.

### `POST /api/investigations/{investigation_id}/action/rollback`
- **Request**: `{ "rollback_reason": "Merchant supplied physical KYC documents" }` (mandatory)
- **Response**: `AuditLogEntry` object.

### `POST /api/investigations/{investigation_id}/decision`
- **Request**:
```json
{
  "decision": "CONFIRMED_FRAUD",
  "justification": "Linked to device farm and high volume surge",
  "analyst_id": "analyst_1",
  "analyst_name": "Senior Investigator"
}
```

### `GET /api/investigations/{investigation_id}/audit-log`
- **Description**: Returns immutable chronological audit events.

### `POST /api/investigations/{investigation_id}/feedback`
- **Request**:
```json
{
  "feedback_type": "CONFIRMED_FRAUD",
  "notes": "Verified botnet farm pattern"
}
```

---

## 6. Feedback & Model Calibration

### `GET /api/feedback`
- **Description**: Aggregate feedback statistics and items for model retraining queue.

---

## 7. Model Evaluation

### `GET /api/evaluation/metrics`
- **Query Parameter**: `threshold` (float, default: 60.0)
- **Response**:
```json
{
  "total_merchants_evaluated": 240,
  "threshold_score": 60.0,
  "metrics": {
    "precision": 0.887,
    "recall": 0.907,
    "f1_score": 0.897,
    "roc_auc": 0.952,
    "false_positive_rate": 0.038,
    "false_negative_rate": 0.093
  },
  "detection_rates": {
    "planted_ring_detection_rate": 1.0,
    "mule_shell_detection_rate": 0.875
  },
  "financial_impact_inr": {
    "total_simulated_volume": 42500000.0,
    "suspicious_fraud_volume": 12800000.0,
    "potential_loss_prevented": 10880000.0,
    "false_positive_delay_friction_cost": 24000.0,
    "net_estimated_savings": 10856000.0
  }
}
```

---

## 8. Live Demo Simulation

### `POST /api/simulation/mule`
- **Request**: `{ "merchant_id": "M-1005", "seed": 42 }` (optional)
- **Response**: Injected transaction count, volume, previous/new risk scores, and new alert state.

### `POST /api/simulation/ring`
- **Request**: `{ "seed": 42 }` (optional)
- **Response**: Created ring details, 4 member merchants, shared device/bank identifiers, and updated network risk.
