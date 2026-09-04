import React, { useState } from 'react';
import {
  ArrowRight,
  RotateCcw,
  Zap,
  Network,
} from 'lucide-react';
import { simulateMule, simulateRing, resetDemoState } from '../services/api';
import type { SimulationResult } from '../types';

interface SimulationProps {
  onNavigateToInvestigation: (merchantId: string) => void;
  onNavigateToTab: (tab: string) => void;
}

export const Simulation: React.FC<SimulationProps> = ({
  onNavigateToInvestigation,
  onNavigateToTab,
}) => {
  const [muleResult, setMuleResult] = useState<SimulationResult | null>(null);
  const [ringResult, setRingResult] = useState<SimulationResult | null>(null);
  const [isMuleLoading, setIsMuleLoading] = useState(false);
  const [isRingLoading, setIsRingLoading] = useState(false);
  const [isResetLoading, setIsResetLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);
  const [simError, setSimError] = useState<string | null>(null);

  const handleSimulateMule = async () => {
    setIsMuleLoading(true);
    setSimError(null);
    try {
      const res = await simulateMule(undefined, Math.floor(Math.random() * 1000) + 1);
      setMuleResult(res);
    } catch (err: any) {
      console.error('Failed to simulate mule spike:', err);
      setSimError('Failed to execute mule burst simulation against backend.');
    } finally {
      setIsMuleLoading(false);
    }
  };

  const handleSimulateRing = async () => {
    setIsRingLoading(true);
    setSimError(null);
    try {
      const res = await simulateRing(Math.floor(Math.random() * 1000) + 1);
      setRingResult(res);
    } catch (err: any) {
      console.error('Failed to simulate ring emergence:', err);
      setSimError('Failed to execute syndicate emergence simulation.');
    } finally {
      setIsRingLoading(false);
    }
  };

  const handleReset = async () => {
    setIsResetLoading(true);
    setSimError(null);
    try {
      await resetDemoState();
      setMuleResult(null);
      setRingResult(null);
      setResetSuccess(true);
      setTimeout(() => setResetSuccess(false), 3000);
    } catch (err: any) {
      console.error('Failed to reset demo state:', err);
      setSimError('Failed to reset simulation state.');
    } finally {
      setIsResetLoading(false);
    }
  };

  return (
    <div className="max-w-[880px] mx-auto px-6 sm:px-10 pt-8 pb-24 font-sans text-[#E8E6DE] animate-fade-in">
      {simError && (
        <div className="mb-6 p-3 rounded bg-red-950/60 border border-red-800/40 text-red-200 text-xs flex justify-between items-center">
          <span>{simError}</span>
          <button onClick={() => setSimError(null)} className="text-red-400 hover:text-white font-bold ml-4">✕</button>
        </div>
      )}

      {/* Header */}
      <div className="stagger-summary flex items-baseline justify-between mb-8 pb-6 border-b border-[#2A2D35]">
        <div>
          <h1 className="text-xl font-semibold text-[#E8E6DE] tracking-tight">Scenario simulation</h1>
          <p className="text-xs text-[#8B8F98] mt-1">
            Trigger dynamic fraud patterns to demonstrate real-time risk escalation and graph discovery.
          </p>
        </div>

        <button
          onClick={handleReset}
          disabled={isResetLoading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-[#20232B] hover:bg-[#2A2D35] border border-[#2A2D35] text-xs font-mono text-[#8B8F98] hover:text-[#E8E6DE] transition-colors cursor-pointer disabled:opacity-50"
        >
          <RotateCcw className={`h-3 w-3 ${isResetLoading ? 'animate-spin text-[#B8862E]' : ''}`} />
          <span>{isResetLoading ? 'Resetting...' : 'Reset demo'}</span>
        </button>
      </div>

      {resetSuccess && (
        <div className="mb-6 p-3 bg-[rgba(75,122,111,0.15)] border border-[#4B7A6F] rounded text-xs font-mono text-[#4B7A6F]">
          ✓ State restored to clean initial baseline.
        </div>
      )}

      <div className="stagger-panel space-y-8">
        {/* Scenario 1: Dormant Sleeper Account Burst */}
        <div className="bg-[#1C1F26] border border-[#2A2D35] rounded-md p-6 space-y-5">
          <div className="flex items-center justify-between border-b border-[#2A2D35] pb-3">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-[#B8862E]" />
              <h2 className="text-sm font-semibold text-[#E8E6DE]">Scenario A: Dormant mule cashout burst</h2>
            </div>
            <button
              onClick={handleSimulateMule}
              disabled={isMuleLoading}
              className="px-3.5 py-1.5 rounded text-xs font-medium bg-[#B8862E] text-[#14161B] hover:bg-[#B8862E]/90 transition-all cursor-pointer disabled:opacity-50"
            >
              {isMuleLoading ? 'Injecting burst...' : 'Trigger mule burst'}
            </button>
          </div>

          {/* Visual Causal State Transition */}
          {!muleResult ? (
            <div className="flex items-center justify-between p-4 bg-[#20232B] border border-[#2A2D35] rounded text-xs">
              <div className="space-y-0.5">
                <span className="text-[#8B8F98] block">Current state:</span>
                <span className="font-semibold text-[#4B7A6F]">Low risk (12.0 / 100)</span>
              </div>
              <span className="text-xs text-[#5A5E68]">Dormant sleeper account awaiting activation</span>
            </div>
          ) : (
            <div className="space-y-4 tab-content-enter">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 items-center p-4 bg-[#20232B] border border-[#A83D3D]/40 rounded">
                <div className="space-y-0.5">
                  <span className="text-xs text-[#8B8F98] block">Baseline state</span>
                  <span className="font-medium text-xs text-[#4B7A6F]">
                    <span className="font-mono">{muleResult.previous_risk_score?.toFixed(1) || '12.0'}</span> (Low risk)
                  </span>
                </div>

                <div className="text-center">
                  <span className="text-xs font-mono text-[#A83D3D] font-bold block">
                    +{((muleResult.risk_score_delta ?? (muleResult.new_risk_score ? muleResult.new_risk_score - (muleResult.previous_risk_score || 12) : 82.5))).toFixed(1)} pts
                  </span>
                  <span className="text-[11.5px] text-[#8B8F98]">35 round transactions injected</span>
                </div>

                <div className="space-y-0.5 sm:text-right">
                  <span className="text-xs text-[#8B8F98] block">New risk state</span>
                  <span className="font-bold text-sm text-[#A83D3D]">
                    <span className="font-mono">{muleResult.new_risk_score?.toFixed(1) || '94.5'}</span> (Critical)
                  </span>
                </div>
              </div>

              {/* Contributing Factors */}
              <div className="p-3.5 bg-[#14161B] rounded border border-[#2A2D35] text-xs space-y-1.5 leading-relaxed">
                <div className="text-[11px] font-medium text-[#8B8F98]">Contributing causal signals:</div>
                <div className="text-[#E8E6DE]">
                  • High-velocity off-peak spike: 35 transactions in 2 hours<br />
                  • 91.4% round-amount distribution (₹25,000 increments)<br />
                  • Rapid payout turnaround: settlement requested in under 2 hours
                </div>
              </div>

              {muleResult.merchant_id && (
                <div className="flex justify-end">
                  <button
                    onClick={() => onNavigateToInvestigation(muleResult.merchant_id!)}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-[#A83D3D] text-[#14161B] text-xs font-semibold hover:bg-[#A83D3D]/90 transition-all cursor-pointer"
                  >
                    <span>Investigate {muleResult.merchant_id}</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Scenario 2: Syndicate Ring Emergence */}
        <div className="bg-[#1C1F26] border border-[#2A2D35] rounded-md p-6 space-y-5">
          <div className="flex items-center justify-between border-b border-[#2A2D35] pb-3">
            <div className="flex items-center gap-2">
              <Network className="h-4 w-4 text-[#B8862E]" />
              <h2 className="text-sm font-semibold text-[#E8E6DE]">Scenario B: Coordinated ring emergence</h2>
            </div>
            <button
              onClick={handleSimulateRing}
              disabled={isRingLoading}
              className="px-3.5 py-1.5 rounded text-xs font-medium bg-[#B8862E] text-[#14161B] hover:bg-[#B8862E]/90 transition-all cursor-pointer disabled:opacity-50"
            >
              {isRingLoading ? 'Forming ring...' : 'Trigger ring emergence'}
            </button>
          </div>

          {/* Visual Causal Chain */}
          {!ringResult ? (
            <div className="flex items-center justify-between p-4 bg-[#20232B] border border-[#2A2D35] rounded text-xs">
              <div className="space-y-0.5">
                <span className="text-[#8B8F98] block">Network state:</span>
                <span className="font-semibold text-[#E8E6DE]">3 isolated clusters</span>
              </div>
              <span className="text-xs text-[#5A5E68]">Ready to inject cross-merchant collusive ring</span>
            </div>
          ) : (
            <div className="space-y-4 tab-content-enter">
              <div className="p-4 bg-[#20232B] border border-[#B8862E]/40 rounded space-y-2 text-xs">
                <div className="flex justify-between items-baseline">
                  <span className="font-semibold text-[#E8E6DE]">New syndicate discovered: <span className="font-mono text-[#B8862E]">{ringResult.simulated_ring_id || 'RING-SIM-EMERGE'}</span></span>
                  <span className="font-mono text-[#B8862E]">{ringResult.created_merchants_count || 4} linked merchants</span>
                </div>
                <div className="text-xs text-[#8B8F98] leading-relaxed">
                  4 freshly registered storefronts connected via shared rooted emulator <code className="font-mono text-[#E8E6DE]">DEV-SIM-09</code> and payout account <code className="font-mono text-[#E8E6DE]">ACC-SIM-77</code>.
                </div>
              </div>

              <div className="flex justify-end gap-2.5">
                <button
                  onClick={() => onNavigateToTab('network')}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-[#20232B] hover:bg-[#2A2D35] border border-[#2A2D35] text-xs font-medium text-[#E8E6DE] transition-colors cursor-pointer"
                >
                  <span>Explore in network graph</span>
                  <ArrowRight className="h-3 w-3" />
                </button>
                {ringResult.member_merchant_ids && ringResult.member_merchant_ids[0] && (
                  <button
                    onClick={() => onNavigateToInvestigation(ringResult.member_merchant_ids![0])}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded bg-[#A83D3D] text-[#14161B] text-xs font-semibold hover:bg-[#A83D3D]/90 transition-all cursor-pointer"
                  >
                    <span>Investigate anchor merchant</span>
                    <ArrowRight className="h-3 w-3" />
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
