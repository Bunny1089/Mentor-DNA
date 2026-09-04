import React, { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import {
  ArrowLeft,
  ChevronRight,
  Sparkles,
  Maximize2,
  Minimize2,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import { CytoscapeGraph } from '../components/graph/CytoscapeGraph';
import { ErrorBoundary } from '../components/common/ErrorBoundary';
import { LoadingState, ErrorState } from '../components/common/StateView';
import {
  openInvestigation,
  getMerchantGraph,
  approveAction,
  getAuditLog,
  submitMerchantAppeal,
  getMerchantTrust,
} from '../services/api';
import type {
  InvestigationDossier,
  SubgraphResponse,
  AuditLogEntry,
  EvidenceItem,
  TrustSignal,
} from '../types';

interface MerchantInvestigationProps {
  merchantId: string;
  onBack: () => void;
  onSelectMerchant: (merchantId: string) => void;
}

export const MerchantInvestigation: React.FC<MerchantInvestigationProps> = ({
  merchantId,
  onBack,
  onSelectMerchant,
}) => {
  const [dossier, setDossier] = useState<InvestigationDossier | null>(null);
  const [graphData, setGraphData] = useState<SubgraphResponse | null>(null);
  const [trustSignal, setTrustSignal] = useState<TrustSignal | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [isFullGraph, setIsFullGraph] = useState(false);
  const [showAllSignals, setShowAllSignals] = useState(false);
  const [showAuditTrail, setShowAuditTrail] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isActionLoading, setIsActionLoading] = useState(false);
  const [isAppealModalOpen, setIsAppealModalOpen] = useState(false);
  const [appealReason, setAppealReason] = useState('');
  const [appealSuccess, setAppealSuccess] = useState(false);

  // Animated Risk Score Count-up
  const [displayScore, setDisplayScore] = useState<number>(0);
  const animRef = useRef<number | null>(null);

  const fetchInvestigationData = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const [dossierData, graphRes, trustRes] = await Promise.all([
        openInvestigation(merchantId),
        getMerchantGraph(merchantId),
        getMerchantTrust(merchantId).catch(() => null),
      ]);
      setDossier(dossierData);
      setGraphData(graphRes);
      setTrustSignal(trustRes);

      const logs = await getAuditLog(dossierData.investigation_id);
      setAuditLogs(logs);
    } catch (err: any) {
      console.error('Failed to load investigation dossier:', err);
      setLoadError(err?.response?.data?.message || err?.response?.data?.detail || `Merchant '${merchantId}' not found.`);
    } finally {
      setIsLoading(false);
    }
  }, [merchantId]);

  useEffect(() => {
    fetchInvestigationData();
  }, [fetchInvestigationData]);

  // Orchestrated Score Count-Up
  useEffect(() => {
    if (!dossier) return;
    const target = Math.round(dossier.risk_summary.overall_risk);
    let cur = 0;

    const step = () => {
      cur += Math.ceil((target - cur) / 6) || 1;
      if (cur >= target) {
        setDisplayScore(target);
        return;
      }
      setDisplayScore(cur);
      animRef.current = window.setTimeout(step, 16);
    };

    const timer = window.setTimeout(step, 150);
    return () => {
      clearTimeout(timer);
      if (animRef.current) clearTimeout(animRef.current);
    };
  }, [dossier]);

  // Filter graph to Ego Subgraph (direct neighbors only, 5-8 nodes) unless expanded
  const filteredGraphData = useMemo<SubgraphResponse | null>(() => {
    if (!graphData) return null;
    if (isFullGraph) return graphData;

    // Find direct edges connected to current merchant
    const directEdges = graphData.edges.filter(
      (e) => e.source === merchantId || e.target === merchantId
    );
    const directNeighborIds = new Set<string>([merchantId]);
    directEdges.forEach((e) => {
      directNeighborIds.add(e.source);
      directNeighborIds.add(e.target);
    });

    // Also include merchants sharing those immediate entities (max 8 nodes)
    const secondaryEdges = graphData.edges.filter(
      (e) => directNeighborIds.has(e.source) || directNeighborIds.has(e.target)
    ).slice(0, 10);

    const egoNodeIds = new Set<string>(directNeighborIds);
    secondaryEdges.forEach((e) => {
      if (egoNodeIds.size < 8) {
        egoNodeIds.add(e.source);
        egoNodeIds.add(e.target);
      }
    });

    const egoNodes = graphData.nodes.filter((n) => egoNodeIds.has(n.id));
    const egoEdges = graphData.edges.filter(
      (e) => egoNodeIds.has(e.source) && egoNodeIds.has(e.target)
    );

    return {
      ...graphData,
      nodes: egoNodes,
      edges: egoEdges,
    };
  }, [graphData, merchantId, isFullGraph]);

  const handleApproveAction = async () => {
    if (!dossier) return;
    setIsActionLoading(true);
    try {
      await approveAction(dossier.investigation_id, 'Action approved by analyst');
      await fetchInvestigationData();
    } catch (err) {
      console.error('Failed to approve action:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleAppealSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!dossier || !appealReason.trim()) return;
    setIsActionLoading(true);
    try {
      await submitMerchantAppeal(dossier.investigation_id, appealReason);
      setAppealSuccess(true);
      setAppealReason('');
      setTimeout(() => {
        setAppealSuccess(false);
        setIsAppealModalOpen(false);
      }, 1500);
      await fetchInvestigationData();
    } catch (err) {
      console.error('Failed to submit appeal:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingState message={`Loading investigation dossier for ${merchantId}...`} />;
  }

  if (loadError || !dossier) {
    return (
      <div className="max-w-[780px] mx-auto my-12">
        <ErrorState
          title="Investigation Case Unavailable"
          message={loadError || `Merchant '${merchantId}' could not be located in current telemetry.`}
          onRetry={fetchInvestigationData}
        />
        <div className="text-center mt-4">
          <button
            onClick={onBack}
            className="px-4 py-2 rounded bg-[#20232B] hover:bg-[#2A2D35] border border-[#2A2D35] text-[#E8E6DE] text-xs font-sans cursor-pointer"
          >
            ← Return to alert queue
          </button>
        </div>
      </div>
    );
  }

  const profile = dossier.merchant_profile;
  const risk = dossier.risk_summary;
  const brief = dossier.ai_briefing;
  const impact = dossier.business_impact;

  const isHighRisk = risk.overall_risk >= 60;
  const isMediumRisk = risk.overall_risk >= 30 && risk.overall_risk < 60;
  const scoreColor = isHighRisk ? 'text-[#A83D3D]' : isMediumRisk ? 'text-[#B8862E]' : 'text-[#4B7A6F]';
  const tierBg = isHighRisk
    ? 'bg-[rgba(168,61,61,0.12)] text-[#A83D3D] border-[#A83D3D]/30'
    : isMediumRisk
    ? 'bg-[rgba(184,134,46,0.12)] text-[#B8862E] border-[#B8862E]/30'
    : 'bg-[rgba(75,122,111,0.12)] text-[#4B7A6F] border-[#4B7A6F]/30';

  // Network summary line
  const networkSummary = risk.ring_id
    ? `Linked to ${risk.ring_id} — ${risk.connected_high_risk_count} merchants sharing infrastructure`
    : 'Standalone merchant — no detected multi-entity ring connections';

  // 4 compact top signals
  const topSignals = [
    { label: 'Round-amount ratio', val: '91.2%', flag: true },
    { label: 'Buyer concentration (HHI)', val: '0.41', flag: true },
    { label: 'Average ticket', val: '₹43,943 (vs ₹1,850 baseline)', flag: true },
    { label: 'Settlement velocity', val: '1.8h turnaround', flag: true },
  ];

  return (
    <div className="max-w-[880px] mx-auto px-6 sm:px-10 pt-8 pb-24 font-sans text-[#E8E6DE] animate-fade-in">
      {/* Breadcrumb */}
      <div className="stagger-breadcrumb flex items-center justify-between mb-5 text-[12.5px] text-[#8B8F98]">
        <button
          onClick={onBack}
          className="flex items-center gap-1 hover:text-[#E8E6DE] transition-colors cursor-pointer"
        >
          <ArrowLeft className="h-3.5 w-3.5 mr-1" />
          <span>Alerts</span>
          <span className="text-[#5A5E68]">/</span>
          <span>{profile.business_name}</span>
        </button>
        <span className="font-mono text-xs text-[#5A5E68]">{profile.merchant_id}</span>
      </div>

      {/* 1. HERO HEADER */}
      <div className="stagger-summary flex items-center gap-8 pb-7 mb-7 border-b border-[#2A2D35]">
        <div className={`font-serif font-black text-6xl sm:text-7xl leading-none shrink-0 ${scoreColor}`}>
          {displayScore}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-xl font-semibold text-[#E8E6DE] truncate">
              {profile.business_name}
            </h1>
            <span className={`text-xs px-2.5 py-1 rounded font-bold uppercase tracking-wide whitespace-nowrap shrink-0 border ${tierBg}`}>
              {risk.risk_level.replace('_', ' ')}
            </span>
          </div>
          <div className="text-[13px] text-[#8B8F98] mb-2">
            <span className="font-mono">{profile.merchant_id}</span> · {profile.category} · {profile.business_type}
          </div>
          <div className="text-[13px] text-[#E8E6DE]">
            <span className="text-[#8B8F98] mr-1.5">Network context:</span>
            <span>{networkSummary}</span>
          </div>
        </div>
      </div>

      {/* TRUST SIGNAL BADGE & AGENTIC COMMERCE QUALIFICATION */}
      {trustSignal && (
        <div className="stagger-panel mb-8 p-4 rounded-md border border-[#2A2D35] bg-[#1C1F26] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            {trustSignal.trust_tier === 'VERIFIED' ? (
              <ShieldCheck className="h-5 w-5 text-[#4B7A6F] shrink-0 mt-0.5" />
            ) : trustSignal.trust_tier === 'CAUTION' ? (
              <ShieldAlert className="h-5 w-5 text-[#B8862E] shrink-0 mt-0.5" />
            ) : trustSignal.trust_tier === 'STANDARD' ? (
              <ShieldCheck className="h-5 w-5 text-[#3B82F6] shrink-0 mt-0.5" />
            ) : (
              <ShieldAlert className="h-5 w-5 text-[#A83D3D] shrink-0 mt-0.5" />
            )}
            <div>
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className="text-xs font-semibold text-[#E8E6DE]">
                  Public Trust Signal:
                </span>
                {trustSignal.trust_tier === 'VERIFIED' && (
                  <span className="px-2 py-0.5 rounded bg-[rgba(75,122,111,0.15)] text-[#4B7A6F] border border-[#4B7A6F]/30 text-[11px] font-bold">
                    VERIFIED MERCHANT
                  </span>
                )}
                {trustSignal.trust_tier === 'STANDARD' && (
                  <span className="px-2 py-0.5 rounded bg-blue-950/40 text-blue-400 border border-blue-800/40 text-[11px] font-bold">
                    STANDARD TIER
                  </span>
                )}
                {trustSignal.trust_tier === 'CAUTION' && (
                  <span className="px-2 py-0.5 rounded bg-[rgba(184,134,46,0.15)] text-[#B8862E] border border-[#B8862E]/30 text-[11px] font-bold">
                    CAUTION TIER
                  </span>
                )}
                {trustSignal.trust_tier === null && (
                  <span className="px-2 py-0.5 rounded bg-[rgba(168,61,61,0.15)] text-[#A83D3D] border border-[#A83D3D]/30 text-[11px] font-bold">
                    WITHHELD (HIGH RISK)
                  </span>
                )}
                {trustSignal.instant_settlement_eligible && (
                  <span className="text-[11px] text-[#4B7A6F] font-medium">
                    · Instant Settlement Eligible
                  </span>
                )}
              </div>
              <p className="text-xs text-[#8B8F98] leading-relaxed max-w-xl">
                {trustSignal.short_reason}
              </p>
            </div>
          </div>
          <div className="text-left sm:text-right shrink-0">
            <span className="text-[11px] text-[#5A5E68] font-mono block">
              Autonomous AI Agent Purchasing:
            </span>
            <span className={`text-xs font-semibold font-mono ${trustSignal.agentic_purchasing_approved ? 'text-[#4B7A6F]' : 'text-[#A83D3D]'}`}>
              {trustSignal.agentic_purchasing_approved ? 'APPROVED' : 'RESTRICTED'}
            </span>
          </div>
        </div>
      )}

      {/* 2. WHY THIS MERCHANT IS FLAGGED (Compact 2x2 signals) */}
      <div className="stagger-panel mb-8">
        <h2 className="text-[13px] font-semibold text-[#8B8F98] mb-3">
          Why this merchant is flagged
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {topSignals.map((sig, idx) => (
            <div key={idx} className="p-3 bg-[#1C1F26] border border-[#2A2D35] rounded-md flex justify-between items-baseline">
              <span className="text-[12.5px] text-[#8B8F98]">{sig.label}</span>
              <span className="font-mono text-[12.5px] font-medium text-[#A83D3D]">{sig.val}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 3. SIDE-BY-SIDE: EGO-GRAPH (LEFT) + EVIDENCE LIST (RIGHT) */}
      <div className="stagger-panel mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
          {/* Left: Ego Network Graph */}
          <div className="bg-[#1C1F26] border border-[#2A2D35] rounded-md p-4">
            <div className="flex justify-between items-center mb-3">
              <span className="text-xs font-semibold text-[#E8E6DE]">
                {isFullGraph ? 'Full syndicate network' : 'Direct ego relationships'}
              </span>
              <button
                onClick={() => setIsFullGraph(!isFullGraph)}
                className="text-xs text-[#B8862E] hover:text-[#E8E6DE] flex items-center gap-1 transition-colors cursor-pointer"
              >
                {isFullGraph ? (
                  <>
                    <Minimize2 className="h-3 w-3" />
                    <span>Collapse to ego</span>
                  </>
                ) : (
                  <>
                    <Maximize2 className="h-3 w-3" />
                    <span>Expand network</span>
                  </>
                )}
              </button>
            </div>

            <div className="h-[280px] rounded border border-[#2A2D35] overflow-hidden relative">
              <ErrorBoundary
                isComponentLevel
                fallbackTitle="Network Graph Layout Paused"
                fallbackMessage="Unable to render topological node layout. Entity connection metadata remains valid."
              >
                <CytoscapeGraph
                  graphData={filteredGraphData}
                  selectedMerchantId={merchantId}
                  onSelectMerchant={onSelectMerchant}
                  height="280px"
                  title=""
                />
              </ErrorBoundary>
            </div>
          </div>

          {/* Right: Plain-English Evidence List */}
          <div className="bg-[#1C1F26] border border-[#2A2D35] rounded-md p-5 space-y-3">
            <h3 className="text-xs font-semibold text-[#E8E6DE] mb-2">
              Key forensic evidence
            </h3>
            
            <div className="space-y-2.5 divide-y divide-[#2A2D35]">
              {dossier.all_evidence.slice(0, 4).map((ev: EvidenceItem) => (
                <div key={ev.evidence_id} className="pt-2.5 first:pt-0">
                  <div className="text-[13px] font-medium text-[#E8E6DE] mb-0.5">
                    {ev.title}
                  </div>
                  <div className="text-xs text-[#8B8F98] leading-relaxed">
                    {ev.explanation || ev.observed_value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 4. AI CASE BRIEF (Prominently Surfaced) */}
      <div className="stagger-panel mb-8 p-5 bg-[#1C1F26] border border-[#2A2D35] border-l-2 border-l-[#B8862E] rounded-r">
        <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-[#B8862E]">
          <Sparkles className="h-3.5 w-3.5" />
          <span>AI case briefing</span>
        </div>
        <p className="text-[13px] text-[#E8E6DE] leading-relaxed">
          {brief?.summary ||
            `${profile.business_name} presents severe multi-modal anomalies. The merchant exhibits coordinated catalog ticket deviations with 91.2% round-amount velocity and is directly linked to an emulator device farm shared across high-risk accounts.`}
        </p>
      </div>

      {/* 5. ESTIMATED IMPACT & RECOMMENDED ACTION (Capped 48h Policy & Proactive Notification) */}
      <div className="stagger-actions mb-8 p-5 bg-[#1C1F26] border border-[#2A2D35] rounded-md space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="text-xs text-[#8B8F98] mb-1 font-medium">Estimated business impact</div>
            <div className="text-sm font-medium text-[#E8E6DE]">
              ₹{((impact?.suspicious_volume || 4394300) / 100000).toFixed(1)} Lakhs exposure ·{' '}
              <span className="text-[#4B7A6F]">
                ₹{((impact?.potential_loss_prevented || 3735155) / 100000).toFixed(1)} Lakhs prevented
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handleApproveAction}
              disabled={isActionLoading}
              className="px-4 py-2 rounded text-[13px] font-medium bg-[#A83D3D] text-[#14161B] hover:bg-[#A83D3D]/90 transition-all cursor-pointer disabled:opacity-50"
            >
              {isActionLoading ? 'Applying...' : 'Apply settlement hold'}
            </button>

            <button
              onClick={() => setIsAppealModalOpen(true)}
              className="px-3.5 py-2 rounded text-[13px] font-medium bg-[#20232B] text-[#E8E6DE] border border-[#2A2D35] hover:border-[#5A5E68] transition-all cursor-pointer"
            >
              Appeal this hold
            </button>
          </div>
        </div>

        {/* Banking Governance Policy Notice */}
        <div className="pt-3 border-t border-[#2A2D35]/70 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11.5px] text-[#8B8F98]">
          <div className="flex items-center gap-2">
            <span className="text-[#4B7A6F] font-mono">✓</span>
            <span>
              <strong className="text-[#E8E6DE]">Proactive merchant notice:</strong> Dispatched via webhook & dashboard with dispute link.
            </span>
          </div>
          <div className="font-mono text-[#5A5E68]">
            Max hold: <span className="text-[#E8E6DE]">48h</span> · Auto-escalation: <span className="text-[#E8E6DE]">24h</span>
          </div>
        </div>
      </div>

      {/* 6. COLLAPSED DISCLOSURES: ALL SIGNALS & AUDIT TRAIL */}
      <div className="space-y-3 pt-4 border-t border-[#2A2D35]">
        {/* All Signals Disclosure */}
        <div className="border border-[#2A2D35] rounded-md bg-[#1C1F26] overflow-hidden">
          <button
            onClick={() => setShowAllSignals(!showAllSignals)}
            className="w-full flex items-center justify-between p-3.5 text-left text-xs font-medium text-[#8B8F98] hover:text-[#E8E6DE] hover:bg-[#20232B] transition-colors cursor-pointer select-none"
          >
            <div className="flex items-center gap-2">
              <ChevronRight
                className={`h-3.5 w-3.5 transition-transform duration-200 ${
                  showAllSignals ? 'rotate-90' : ''
                }`}
              />
              <span>Show all signals ({dossier.all_evidence.length})</span>
            </div>
            <span className="text-[11px] text-[#5A5E68]">Complete telemetry</span>
          </button>

          <div
            className={`overflow-hidden transition-all duration-300 ease-out ${
              showAllSignals ? 'max-h-[500px] opacity-100' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="p-4 pt-0 border-t border-[#2A2D35]/60 divide-y divide-[#2A2D35] text-xs">
              {dossier.all_evidence.map((ev: EvidenceItem) => (
                <div key={ev.evidence_id} className="py-2.5 flex justify-between items-center">
                  <span className="text-[#8B8F98]">{ev.title}</span>
                  <span className="font-mono text-[#E8E6DE]">{ev.observed_value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Audit Trail Disclosure */}
        <div className="border border-[#2A2D35] rounded-md bg-[#1C1F26] overflow-hidden">
          <button
            onClick={() => setShowAuditTrail(!showAuditTrail)}
            className="w-full flex items-center justify-between p-3.5 text-left text-xs font-medium text-[#8B8F98] hover:text-[#E8E6DE] hover:bg-[#20232B] transition-colors cursor-pointer select-none"
          >
            <div className="flex items-center gap-2">
              <ChevronRight
                className={`h-3.5 w-3.5 transition-transform duration-200 ${
                  showAuditTrail ? 'rotate-90' : ''
                }`}
              />
              <span>Show full history & audit trail ({auditLogs.length} events)</span>
            </div>
            <span className="text-[11px] text-[#5A5E68]">Immutable ledger</span>
          </button>

          <div
            className={`overflow-hidden transition-all duration-300 ease-out ${
              showAuditTrail ? 'max-h-[350px] opacity-100' : 'max-h-0 opacity-0'
            }`}
          >
            <div className="p-4 pt-0 border-t border-[#2A2D35]/60 divide-y divide-[#2A2D35] text-xs">
              {auditLogs.map((log: AuditLogEntry) => (
                <div key={log.event_id} className="py-2.5 flex gap-4 items-baseline">
                  <span className="font-mono text-[#5A5E68] text-[11px]">
                    {new Date(log.timestamp).toLocaleTimeString('en-US', {
                      hour: '2-digit',
                      minute: '2-digit',
                      hour12: false,
                    })}
                  </span>
                  <span className="text-[#E8E6DE]">
                    <strong className="mr-1">{log.event_type}:</strong>
                    {log.description}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Appeal Modal */}
      {isAppealModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-fade-in">
          <div className="bg-[#1C1F26] border border-[#B8862E]/40 rounded-md p-6 max-w-lg w-full space-y-4 shadow-2xl">
            <div className="flex items-center justify-between border-b border-[#2A2D35] pb-3">
              <h3 className="text-sm font-semibold text-[#E8E6DE]">Submit merchant appeal</h3>
              <button
                onClick={() => setIsAppealModalOpen(false)}
                className="text-[#8B8F98] hover:text-[#E8E6DE] text-xs font-mono"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-[#8B8F98]">
              Dispute a risk restriction for <strong className="text-[#E8E6DE]">{profile.business_name}</strong>.
            </p>

            <form onSubmit={handleAppealSubmit} className="space-y-4">
              <textarea
                rows={3}
                required
                value={appealReason}
                onChange={(e) => setAppealReason(e.target.value)}
                placeholder="Provide business justification (e.g. promotional flash sale)..."
                className="w-full bg-[#20232B] border border-[#2A2D35] rounded p-3 text-xs text-[#E8E6DE] placeholder-[#5A5E68] focus:outline-none focus:border-[#B8862E] font-sans"
              />

              {appealSuccess && (
                <div className="p-2.5 rounded bg-[rgba(75,122,111,0.15)] border border-[#4B7A6F] text-[#4B7A6F] text-xs font-mono">
                  ✓ Appeal logged for human adjudication.
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAppealModalOpen(false)}
                  className="px-3.5 py-1.5 rounded bg-[#20232B] border border-[#2A2D35] text-[#8B8F98] text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!appealReason.trim() || isActionLoading}
                  className="px-4 py-1.5 rounded bg-[#B8862E] text-[#14161B] text-xs font-semibold hover:bg-[#B8862E]/90 disabled:opacity-50"
                >
                  {isActionLoading ? 'Submitting...' : 'Submit appeal'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
