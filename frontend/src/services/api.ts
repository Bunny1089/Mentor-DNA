/**
 * Centralized API Service Layer for Merchant DNA Frontend.
 */

import axios from 'axios';
import type {
  SystemStatus,
  PaginatedMerchantsResponse,
  RiskScoreBreakdown,
  AlertQueueResponse,
  SubgraphResponse,
  RingSummaryItem,
  InvestigationDossier,
  AICaseBriefing,
  ActionRecommendation,
  AnalystDecision,
  AuditLogEntry,
  AnalystFeedback,
  EvaluationReport,
  SimulationResult,
  DecisionFeedback,
  RiskLevel,
  InvestigationState,
  TrustSignal,
  AppealRecord,
  AppealRecoverySummary,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// System & Health
export const getSystemStatus = async (): Promise<SystemStatus> => {
  const { data } = await client.get<SystemStatus>('/api/system/status');
  return data;
};

// Merchants
export const getMerchants = async (params?: {
  page?: number;
  page_size?: number;
  risk_level?: RiskLevel;
  category?: string;
  search?: string;
  ring_id?: string;
}): Promise<PaginatedMerchantsResponse> => {
  const { data } = await client.get<PaginatedMerchantsResponse>('/api/merchants', { params });
  return data;
};

export const getMerchant = async (merchantId: string): Promise<any> => {
  const { data } = await client.get(`/api/merchants/${merchantId}`);
  return data;
};

export const getMerchantRisk = async (merchantId: string): Promise<RiskScoreBreakdown> => {
  const { data } = await client.get<RiskScoreBreakdown>(`/api/merchants/${merchantId}/risk`);
  return data;
};

// Alerts Queue
export const getAlerts = async (params?: {
  risk_level?: RiskLevel;
  status?: InvestigationState;
}): Promise<AlertQueueResponse> => {
  const { data } = await client.get<AlertQueueResponse>('/api/alerts', { params });
  return data;
};

// Graph & Rings
export const getMerchantGraph = async (merchantId: string): Promise<SubgraphResponse> => {
  const { data } = await client.get<SubgraphResponse>(`/api/graph/merchant/${merchantId}`);
  return data;
};

export const getRings = async (): Promise<RingSummaryItem[]> => {
  const { data } = await client.get<RingSummaryItem[]>('/api/graph/rings');
  return data;
};

export const getRing = async (ringId: string): Promise<SubgraphResponse> => {
  const { data } = await client.get<SubgraphResponse>(`/api/graph/rings/${ringId}`);
  return data;
};

// Investigation Workflow
export const openInvestigation = async (merchantId: string): Promise<InvestigationDossier> => {
  const { data } = await client.post<InvestigationDossier>(`/api/investigations/${merchantId}`);
  return data;
};

export const getInvestigation = async (investigationId: string): Promise<InvestigationDossier> => {
  const { data } = await client.get<InvestigationDossier>(`/api/investigations/${investigationId}`);
  return data;
};

export const generateBriefing = async (investigationId: string): Promise<AICaseBriefing> => {
  const { data } = await client.post<AICaseBriefing>(`/api/investigations/${investigationId}/briefing`);
  return data;
};

export const getAction = async (investigationId: string): Promise<ActionRecommendation> => {
  const { data } = await client.get<ActionRecommendation>(`/api/investigations/${investigationId}/action`);
  return data;
};

export const approveAction = async (
  investigationId: string,
  notes?: string
): Promise<AnalystDecision> => {
  const { data } = await client.post<AnalystDecision>(`/api/investigations/${investigationId}/action/approve`, {
    notes: notes || 'Analyst approved bounded risk action.',
  });
  return data;
};

export const rejectAction = async (
  investigationId: string,
  justification: string
): Promise<AnalystDecision> => {
  const { data } = await client.post<AnalystDecision>(`/api/investigations/${investigationId}/action/reject`, {
    justification,
  });
  return data;
};

export const rollbackAction = async (
  investigationId: string,
  rollback_reason: string
): Promise<AuditLogEntry> => {
  const { data } = await client.post<AuditLogEntry>(`/api/investigations/${investigationId}/action/rollback`, {
    rollback_reason,
  });
  return data;
};

export const submitMerchantAppeal = async (
  investigationId: string,
  reason: string,
  contact_email?: string
): Promise<{ status: string; investigation_id: string; merchant_id: string; new_state: InvestigationState; message: string }> => {
  const { data } = await client.post(`/api/investigations/${investigationId}/appeal`, {
    reason,
    contact_email: contact_email || 'merchant@store.com',
  });
  return data;
};

export const recordDecision = async (
  investigationId: string,
  decision: DecisionFeedback,
  justification: string
): Promise<AnalystDecision> => {
  const { data } = await client.post<AnalystDecision>(`/api/investigations/${investigationId}/decision`, {
    decision,
    justification,
  });
  return data;
};

export const getAuditLog = async (investigationId: string): Promise<AuditLogEntry[]> => {
  const { data } = await client.get<AuditLogEntry[]>(`/api/investigations/${investigationId}/audit-log`);
  return data;
};

export const submitFeedback = async (
  investigationId: string,
  feedback_type: DecisionFeedback,
  notes: string
): Promise<AnalystFeedback> => {
  const { data } = await client.post<AnalystFeedback>(`/api/investigations/${investigationId}/feedback`, {
    feedback_type,
    notes,
  });
  return data;
};

export const getAllFeedback = async (): Promise<any> => {
  const { data } = await client.get('/api/feedback');
  return data;
};

// Model Evaluation
export const getEvaluationMetrics = async (threshold: number = 60.0): Promise<EvaluationReport> => {
  const { data } = await client.get<EvaluationReport>('/api/evaluation/metrics', {
    params: { threshold },
  });
  return data;
};

// Live Simulations
export const simulateMule = async (merchantId?: string, seed: number = 42): Promise<SimulationResult> => {
  const { data } = await client.post<SimulationResult>('/api/simulation/mule', {
    merchant_id: merchantId,
    seed,
  });
  return data;
};

export const simulateRing = async (seed: number = 42): Promise<SimulationResult> => {
  const { data } = await client.post<SimulationResult>('/api/simulation/ring', {
    seed,
  });
  return data;
};

// Trust Signal (Agentic Commerce & Positive Qualification)
export const getMerchantTrust = async (merchantId: string): Promise<TrustSignal> => {
  const { data } = await client.get<TrustSignal>(`/api/trust/${merchantId}`);
  return data;
};

// False-Positive Appeal Recovery Tracking
export const getRecoverySummary = async (): Promise<AppealRecoverySummary> => {
  const { data } = await client.get<AppealRecoverySummary>('/api/investigations/recovery/summary');
  return data;
};

export const getRecoveryAppeals = async (): Promise<AppealRecord[]> => {
  const { data } = await client.get<AppealRecord[]>('/api/investigations/recovery/appeals');
  return data;
};

export const resetDemoState = async (): Promise<{ status: string; message: string; merchant_count: number; ring_count: number }> => {
  const { data } = await client.post<{ status: string; message: string; merchant_count: number; ring_count: number }>('/api/simulation/reset');
  return data;
};

export default client;


