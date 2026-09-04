/**
 * TypeScript Interfaces mirroring the Merchant DNA Backend API Models.
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type ActionType = 
  | 'CONTINUE_MONITORING'
  | 'ENHANCED_MONITORING'
  | 'SETTLEMENT_REVIEW'
  | 'URGENT_SETTLEMENT_FREEZE';

export type DecisionFeedback = 
  | 'CONFIRMED_FRAUD'
  | 'FALSE_POSITIVE'
  | 'CLEARED'
  | 'NEEDS_INVESTIGATION';

export type InvestigationState = 
  | 'NEW'
  | 'UNDER_REVIEW'
  | 'ESCALATED'
  | 'ACTION_RECOMMENDED'
  | 'ACTIONED'
  | 'PENDING_APPEAL_REVIEW'
  | 'CLEARED'
  | 'CLOSED';

export type EntityType = 
  | 'MERCHANT'
  | 'BUYER'
  | 'DEVICE'
  | 'PHONE'
  | 'BANK_ACCOUNT'
  | 'UPI_HANDLE'
  | 'ADDRESS'
  | 'TRANSACTION';

export type EvidenceType = 
  | 'BEHAVIORAL'
  | 'NETWORK'
  | 'TRANSACTION'
  | 'SETTLEMENT'
  | 'REFUND'
  | 'IDENTITY'
  | 'TEMPORAL';

export interface SystemStatus {
  backend_status: string;
  service: string;
  version: string;
  data_loaded: boolean;
  merchant_count: number;
  transaction_count: number;
  graph_nodes_count: number;
  graph_edges_count: number;
  detected_rings_count: number;
  behavioral_model_loaded: boolean;
  server_time: string;
}

export interface MerchantSummaryItem {
  merchant_id: string;
  business_name: string;
  category: string;
  business_type: string;
  onboarding_date: string;
  transaction_count: number;
  total_volume: number;
  behavioral_risk: number;
  network_risk: number;
  overall_risk: number;
  risk_level: RiskLevel;
  confidence: number;
  recommended_action: string;
  ring_id?: string;
  top_factor: string;
}

export interface PaginatedMerchantsResponse {
  total_count: number;
  page: number;
  page_size: number;
  total_pages: number;
  merchants: MerchantSummaryItem[];
}

export interface RiskFactorContribution {
  factor_id: string;
  title: string;
  description: string;
  category: string;
  weight: number;
  value_observed: string;
  benchmark: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface RiskScoreBreakdown {
  merchant_id: string;
  behavioral_risk: number;
  network_risk: number;
  overall_risk: number;
  risk_level: RiskLevel;
  confidence: number;
  top_factors: RiskFactorContribution[];
  recommended_action: ActionType;
  action_rationale: string;
  ring_id?: string;
  connected_high_risk_count: number;
  calculated_at: string;
}

export interface AlertItem {
  alert_id: string;
  merchant_id: string;
  business_name: string;
  category: string;
  risk_level: RiskLevel;
  overall_score: number;
  behavioral_score: number;
  network_score: number;
  top_reasons: string[];
  ring_affiliation?: string;
  created_timestamp: string;
  recommended_action: string;
  status: InvestigationState;
}

export interface AlertQueueResponse {
  total_alerts: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  alerts: AlertItem[];
}

export interface GraphNode {
  id: string;
  label: string;
  entity_type: EntityType;
  risk_level?: RiskLevel;
  risk_score?: number;
  is_ring_member: boolean;
  metadata: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation_type: string;
  weight: number;
  label: string;
  is_suspicious: boolean;
  metadata: Record<string, any>;
}

export interface SubgraphResponse {
  merchant_id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  ring_id?: string;
  cluster_risk_score: number;
  shared_identifiers_count: number;
}

export interface RingSummaryItem {
  ring_id: string;
  name: string;
  members: string[];
  shared_entities: Array<{ entity_type: string; entity_id: string; shared_by_merchants_count: number }>;
  ring_size: number;
  density: number;
  dominant_shared_identifier: string;
  network_risk: number;
  confidence: number;
}

export interface EvidenceItem {
  evidence_id: string;
  evidence_type: EvidenceType;
  title: string;
  observed_value: string;
  baseline_value: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  source: string;
  explanation: string;
}

export interface TimelineEvent {
  event_id: string;
  event_type: string;
  title: string;
  description: string;
  timestamp: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  metadata: Record<string, any>;
}

export interface ActionRecommendation {
  action: ActionType;
  risk_level: RiskLevel;
  reason: string;
  supporting_evidence: string[];
  confidence: number;
  created_at: string;
  reversible: boolean;
  requires_analyst_approval: boolean;
}

export interface AICaseBriefing {
  summary: string;
  key_evidence: string[];
  network_context: string;
  risk_interpretation: string;
  recommended_next_step: string;
  evidence_count: number;
  evidence_ids_used: string[];
  generated_at: string;
  grounding_mode: 'LLM' | 'DETERMINISTIC_FALLBACK';
}

export interface BusinessImpact {
  merchant_id: string;
  total_processed_volume: number;
  suspicious_volume: number;
  estimated_exposure: number;
  potential_loss_prevented: number;
  false_positive_cost: number;
  expected_net_loss: number;
  is_estimated: boolean;
}

export interface InvestigationDossier {
  investigation_id: string;
  merchant_id: string;
  merchant_profile: {
    merchant_id: string;
    business_name: string;
    legal_name: string;
    category: string;
    business_type: string;
    declared_avg_ticket: number;
    onboarding_date: string;
    kyc_status: string;
    total_transaction_count: number;
    total_processed_volume: number;
    is_active: boolean;
    current_state: string;
  };
  current_state: InvestigationState;
  risk_summary: RiskScoreBreakdown;
  behavioral_evidence: EvidenceItem[];
  network_evidence: EvidenceItem[];
  all_evidence: EvidenceItem[];
  timeline: TimelineEvent[];
  action_recommendation: ActionRecommendation;
  ai_briefing?: AICaseBriefing;
  business_impact: BusinessImpact;
  created_at: string;
  updated_at: string;
}

export interface AuditLogEntry {
  event_id: string;
  merchant_id: string;
  investigation_id: string;
  event_type: string;
  actor: 'SYSTEM' | 'ANALYST';
  actor_id: string;
  description: string;
  timestamp: string;
  previous_state?: InvestigationState;
  new_state?: InvestigationState;
  metadata: Record<string, any>;
}

export interface AnalystDecision {
  decision_id: string;
  investigation_id: string;
  merchant_id: string;
  analyst_id: string;
  analyst_name: string;
  decision: DecisionFeedback;
  action_taken: ActionType;
  analyst_reason: string;
  timestamp: string;
  previous_state: InvestigationState;
  new_state: InvestigationState;
  reversible: boolean;
}

export interface AnalystFeedback {
  feedback_id: string;
  investigation_id: string;
  merchant_id: string;
  analyst_id: string;
  feedback_type: DecisionFeedback;
  notes: string;
  created_at: string;
}

export interface RingSizeSensitivityItem {
  size_bracket: string;
  rings_total: number;
  rings_detected: number;
  detection_rate: number;
}

export interface FalsePositiveCostAnalysis {
  fp_merchants_count: number;
  hold_period_days: number;
  fp_delayed_volume_inr: number;
  fp_cumulative_historical_volume_inr?: number;
  fp_delay_friction_rate?: number;
  fp_estimated_friction_cost_inr: number;
  formula_definition?: string;
  summary_stat: string;
}

export interface ThresholdSweepGridItem {
  threshold: number;
  precision: number;
  recall: number;
  f1_score: number;
  tp: number;
  fp: number;
  fn: number;
  tn: number;
  training_business_loss_inr: number;
}

export interface ThresholdSelectionMethodology {
  methodology: string;
  train_sample_size: number;
  selected_threshold: number;
  best_training_f1: number;
  sweep_grid: ThresholdSweepGridItem[];
  selection_rationale: string;
}

export interface KnownLimitationDetail {
  observed_rate: number;
  caught_ratio: string;
  explanation: string;
  future_roadmap: string;
}

export interface KnownLimitations {
  mule_shell_detection: KnownLimitationDetail;
  small_ring_detection: KnownLimitationDetail;
}

export interface SideBySideComparison {
  metrics: Array<{
    metric: string;
    standard: number;
    harder: number;
  }>;
  false_positive_cost: {
    standard_summary: string;
    harder_summary: string;
  };
}

export interface EvaluationReport {
  primary_benchmark?: string;
  benchmark_role_note?: string;
  controlled_benchmark_disclaimer?: string;
  total_merchants_evaluated: number;
  threshold_used: number;
  metrics: {
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    false_positive_rate: number;
    false_negative_rate: number;
  };
  confusion_matrix: {
    true_negatives: number;
    false_positives: number;
    false_negatives: number;
    true_positives: number;
  };
  detection_rates: {
    planted_ring_detection_rate: number;
    mule_shell_detection_rate: number;
    ring_merchants_total?: number;
    ring_merchants_detected?: number;
    mule_merchants_total?: number;
    mule_merchants_detected?: number;
  };
  ring_size_sensitivity?: RingSizeSensitivityItem[];
  false_positive_cost_analysis?: FalsePositiveCostAnalysis;
  financial_impact_inr: {
    detected_suspicious_volume: number;
    potential_loss_prevented_projected?: number;
    potential_loss_prevented?: number;
    false_positive_volume_delayed?: number;
    false_positive_cumulative_volume?: number;
    false_positive_friction_cost?: number;
    false_negative_exposure_cost?: number;
    expected_net_loss?: number;
    net_fraud_savings?: number;
    projected_loss_prevention_roi?: string;
  };
  threshold_selection_methodology?: ThresholdSelectionMethodology;
  known_limitations?: KnownLimitations;
  standard_benchmark?: any;
  harder_benchmark?: any;
  side_by_side_comparison?: SideBySideComparison;
}

export interface SimulationResult {
  scenario: string;
  merchant_id?: string;
  business_name?: string;
  transactions_injected?: number;
  injected_volume?: number;
  previous_risk_score?: number;
  previous_risk_level?: string;
  new_risk_score?: number;
  new_risk_level?: string;
  risk_score_delta?: number;
  recommended_action?: string;
  top_contributing_factors?: string[];
  simulated_ring_id?: string;
  created_merchants_count?: number;
  member_merchant_ids?: string[];
  shared_infrastructure?: Record<string, string>;
  sample_member_risk_score?: number;
  sample_member_risk_level?: string;
  sample_member_recommended_action?: string;
  network_risk_score?: number;
  confidence?: number;
  simulated_at: string;
}

export interface TrustSignal {
  merchant_id: string;
  business_name: string;
  category: string;
  trust_tier: 'VERIFIED' | 'STANDARD' | 'CAUTION' | null;
  short_reason: string;
  instant_settlement_eligible: boolean;
  agentic_purchasing_approved: boolean;
  last_updated: string;
}

export interface AppealRecord {
  appeal_id: string;
  investigation_id: string;
  merchant_id: string;
  business_name: string;
  reason: string;
  contact_email?: string;
  status: 'PENDING_REVIEW' | 'APPROVED_RELEASED' | 'REJECTED_UPHELD';
  appeal_submitted_at: string;
  appeal_resolved_at?: string | null;
  recovered_amount?: number | null;
  resolution_time_hours?: number | null;
}

export interface AppealRecoverySummary {
  pending_appeals_count: number;
  resolved_appeals_count: number;
  total_recovered_amount: number;
  avg_resolution_time_hours: number;
  recent_appeals: AppealRecord[];
}

