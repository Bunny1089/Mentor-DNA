import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { Search } from 'lucide-react';
import { getAlerts } from '../services/api';
import { DEMO_CONFIG } from '../config/demoConfig';
import { LoadingState, ErrorState, EmptyState } from '../components/common/StateView';
import type { AlertItem, RiskLevel, InvestigationState } from '../types';

interface AlertsProps {
  onNavigateToInvestigation: (merchantId: string) => void;
}

export const Alerts: React.FC<AlertsProps> = ({ onNavigateToInvestigation }) => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRisk, setSelectedRisk] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const fetchAlerts = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const riskParam = selectedRisk !== 'ALL' ? (selectedRisk as RiskLevel) : undefined;
      const statusParam = selectedStatus !== 'ALL' ? (selectedStatus as InvestigationState) : undefined;
      const data = await getAlerts({ risk_level: riskParam, status: statusParam });
      setAlerts(data.alerts);
    } catch (err: any) {
      console.error('Failed to fetch alerts:', err);
      setLoadError('Failed to load active risk alerts from engine.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedRisk, selectedStatus]);

  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  const filteredAlerts = useMemo(() => {
    let result = alerts;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = alerts.filter(
        (a) =>
          a.merchant_id.toLowerCase().includes(q) ||
          a.business_name.toLowerCase().includes(q) ||
          a.category.toLowerCase().includes(q) ||
          (a.ring_affiliation && a.ring_affiliation.toLowerCase().includes(q))
      );
    }
    return [...result].sort((a, b) => {
      if (a.merchant_id === DEMO_CONFIG.GOLDEN_MERCHANT_ID) return -1;
      if (b.merchant_id === DEMO_CONFIG.GOLDEN_MERCHANT_ID) return 1;
      return b.overall_score - a.overall_score;
    });
  }, [searchQuery, alerts]);

  const counts = {
    total: alerts.length,
    critical: alerts.filter((a) => a.risk_level === 'CRITICAL').length,
    high: alerts.filter((a) => a.risk_level === 'HIGH').length,
    medium: alerts.filter((a) => a.risk_level === 'MEDIUM').length,
    low: alerts.filter((a) => a.risk_level === 'LOW').length,
  };

  if (isLoading && alerts.length === 0) {
    return <LoadingState message="Loading alert queue telemetry..." />;
  }

  if (loadError && alerts.length === 0) {
    return (
      <div className="max-w-[800px] mx-auto my-12">
        <ErrorState
          title="Alert Queue Unavailable"
          message={loadError}
          onRetry={fetchAlerts}
        />
      </div>
    );
  }

  return (
    <div className="max-w-[1080px] mx-auto px-6 sm:px-10 pt-8 pb-20 font-sans text-[#E8E6DE] animate-fade-in space-y-6">
      {/* Triage Summary Filter Tabs */}
      <div className="stagger-summary flex flex-wrap gap-2 border-b border-[#2A2D35] pb-4">
        <button
          onClick={() => setSelectedRisk('ALL')}
          className={`px-3.5 py-2 rounded text-xs transition-colors cursor-pointer ${
            selectedRisk === 'ALL'
              ? 'bg-[#20232B] text-[#E8E6DE] font-medium border border-[#2A2D35]'
              : 'text-[#8B8F98] hover:text-[#E8E6DE]'
          }`}
        >
          All alerts <span className="font-mono text-[#5A5E68] ml-1">({counts.total})</span>
        </button>

        <button
          onClick={() => setSelectedRisk('CRITICAL')}
          className={`px-3.5 py-2 rounded text-xs transition-colors cursor-pointer ${
            selectedRisk === 'CRITICAL'
              ? 'bg-[rgba(168,61,61,0.12)] text-[#A83D3D] font-medium border border-[#A83D3D]/30'
              : 'text-[#8B8F98] hover:text-[#A83D3D]'
          }`}
        >
          Critical <span className="font-mono text-[#A83D3D] ml-1">({counts.critical})</span>
        </button>

        <button
          onClick={() => setSelectedRisk('HIGH')}
          className={`px-3.5 py-2 rounded text-xs transition-colors cursor-pointer ${
            selectedRisk === 'HIGH'
              ? 'bg-[rgba(184,134,46,0.12)] text-[#B8862E] font-medium border border-[#B8862E]/30'
              : 'text-[#8B8F98] hover:text-[#B8862E]'
          }`}
        >
          High <span className="font-mono text-[#B8862E] ml-1">({counts.high})</span>
        </button>

        <button
          onClick={() => setSelectedRisk('MEDIUM')}
          className={`px-3.5 py-2 rounded text-xs transition-colors cursor-pointer ${
            selectedRisk === 'MEDIUM'
              ? 'bg-[#20232B] text-[#E8E6DE] font-medium border border-[#2A2D35]'
              : 'text-[#8B8F98] hover:text-[#E8E6DE]'
          }`}
        >
          Medium <span className="font-mono text-[#5A5E68] ml-1">({counts.medium})</span>
        </button>

        <button
          onClick={() => setSelectedRisk('LOW')}
          className={`px-3.5 py-2 rounded text-xs transition-colors cursor-pointer ${
            selectedRisk === 'LOW'
              ? 'bg-[rgba(75,122,111,0.12)] text-[#4B7A6F] font-medium border border-[#4B7A6F]/30'
              : 'text-[#8B8F98] hover:text-[#4B7A6F]'
          }`}
        >
          Low <span className="font-mono text-[#4B7A6F] ml-1">({counts.low})</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="stagger-tabs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-[260px] bg-[#1C1F26] border border-[#2A2D35] rounded px-3 py-1.5 text-xs">
          <Search className="h-3.5 w-3.5 text-[#8B8F98] shrink-0" />
          <input
            type="text"
            placeholder="Search by merchant name, ID, category, or ring..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent text-xs text-[#E8E6DE] placeholder-[#5A5E68] focus:outline-none font-sans"
          />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-[#8B8F98]">Status:</span>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-[#1C1F26] border border-[#2A2D35] rounded px-2.5 py-1 text-xs text-[#E8E6DE] focus:outline-none cursor-pointer"
          >
            <option value="ALL">All statuses</option>
            <option value="PENDING_ANALYSIS">Pending analysis</option>
            <option value="RESTRICTED_SETTLEMENT_HELD">Settlement held</option>
            <option value="RESOLVED_CLEARED">Cleared</option>
          </select>
        </div>
      </div>
      {/* Alert Queue Table / Empty State */}
      {filteredAlerts.length === 0 ? (
        <EmptyState
          title="No alerts matching active filters"
          message="No anomalous merchants found for the selected risk tier, status, or search query."
          actionLabel="Reset filters"
          onAction={() => {
            setSelectedRisk('ALL');
            setSelectedStatus('ALL');
            setSearchQuery('');
          }}
        />
      ) : (
        <div className="stagger-panel overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="text-left text-[12px] font-medium text-[#8B8F98] border-b border-[#2A2D35]">
                <th className="py-2.5 px-3 font-medium">Merchant</th>
                <th className="py-2.5 px-3 text-center font-medium">Score</th>
                <th className="py-2.5 px-3 font-medium">Primary signal</th>
                <th className="py-2.5 px-3 font-medium">Network</th>
                <th className="py-2.5 px-3 text-right font-medium">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#2A2D35] text-[13px]">
              {filteredAlerts.map((alert) => {
                const isCritical = alert.risk_level === 'CRITICAL';
                const isHigh = alert.risk_level === 'HIGH';
                const tierBadge = isCritical
                  ? 'text-[#A83D3D] bg-[rgba(168,61,61,0.12)] border-[#A83D3D]/30'
                  : isHigh
                  ? 'text-[#B8862E] bg-[rgba(184,134,46,0.12)] border-[#B8862E]/30'
                  : 'text-[#4B7A6F] bg-[rgba(75,122,111,0.12)] border-[#4B7A6F]/30';

                return (
                  <tr
                    key={alert.alert_id}
                    onClick={() => onNavigateToInvestigation(alert.merchant_id)}
                    className="hover:bg-[#1C1F26] transition-colors cursor-pointer group"
                  >
                    <td className="py-3 px-3">
                      <div className="font-medium text-[#E8E6DE] group-hover:text-[#B8862E] transition-colors">
                        {alert.business_name}
                      </div>
                      <div className="text-xs text-[#5A5E68]">
                        <span className="font-mono">{alert.merchant_id}</span> · {alert.category}
                      </div>
                    </td>

                    <td className="py-3 px-3 text-center">
                      <span className={`font-serif font-bold text-base ${isCritical ? 'text-[#A83D3D]' : isHigh ? 'text-[#B8862E]' : 'text-[#4B7A6F]'}`}>
                        {Math.round(alert.overall_score)}
                      </span>
                    </td>

                    <td className="py-3 px-3">
                      <span className="text-xs text-[#E8E6DE] truncate max-w-[280px] block">
                        {alert.top_reasons[0] || 'Baseline anomalous deviation'}
                      </span>
                    </td>

                    <td className="py-3 px-3">
                      {alert.ring_affiliation ? (
                        <span className="inline-flex items-center text-xs text-[#B8862E] font-medium">
                          {alert.ring_affiliation.replace('RING-', '').replace('-', ' ').toLowerCase()}
                        </span>
                      ) : (
                        <span className="text-xs text-[#5A5E68]">None</span>
                      )}
                    </td>

                    <td className="py-3 px-3 text-right">
                      <span className={`text-[11px] px-2.5 py-1 rounded font-bold uppercase tracking-wider border ${tierBadge}`}>
                        {alert.risk_level}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
