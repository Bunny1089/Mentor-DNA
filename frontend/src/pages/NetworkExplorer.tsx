import React, { useEffect, useState, useCallback } from 'react';
import { ArrowRight } from 'lucide-react';
import { CytoscapeGraph } from '../components/graph/CytoscapeGraph';
import { ErrorBoundary } from '../components/common/ErrorBoundary';
import { LoadingState, ErrorState, EmptyState } from '../components/common/StateView';
import { getRings, getRing } from '../services/api';
import type { RingSummaryItem, SubgraphResponse } from '../types';

interface NetworkExplorerProps {
  onNavigateToInvestigation: (merchantId: string) => void;
}

export const NetworkExplorer: React.FC<NetworkExplorerProps> = ({ onNavigateToInvestigation }) => {
  const [rings, setRings] = useState<RingSummaryItem[]>([]);
  const [selectedRingId, setSelectedRingId] = useState<string | null>(null);
  const [ringGraph, setRingGraph] = useState<SubgraphResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const fetchRings = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const data = await getRings();
      setRings(data);
      if (data.length > 0 && !selectedRingId) {
        const hasGolden = data.find((r) => r.ring_id === 'RING-ALPHA-DEVICE-FARM');
        setSelectedRingId(hasGolden ? 'RING-ALPHA-DEVICE-FARM' : data[0].ring_id);
      }
    } catch (err: any) {
      console.error('Failed to load rings:', err);
      setLoadError('Failed to load syndicate networks from backend.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedRingId]);

  useEffect(() => {
    fetchRings();
  }, [fetchRings]);

  const fetchRingGraph = useCallback(async (ringId: string) => {
    try {
      const graphData = await getRing(ringId);
      setRingGraph(graphData);
    } catch (err) {
      console.error(`Failed to load graph for ring ${ringId}:`, err);
    }
  }, []);

  useEffect(() => {
    if (selectedRingId) {
      fetchRingGraph(selectedRingId);
    }
  }, [selectedRingId, fetchRingGraph]);

  const currentRing = rings.find((r) => r.ring_id === selectedRingId);

  if (isLoading && rings.length === 0) {
    return <LoadingState message="Loading syndicate network graph..." />;
  }

  if (loadError && rings.length === 0) {
    return (
      <div className="max-w-[800px] mx-auto my-12">
        <ErrorState
          title="Syndicate Explorer Unavailable"
          message={loadError}
          onRetry={fetchRings}
        />
      </div>
    );
  }

  if (rings.length === 0) {
    return (
      <div className="max-w-[800px] mx-auto my-12">
        <EmptyState
          title="No Collusive Syndicates Detected"
          message="No multi-merchant collusive ring structures found in current graph dataset."
          actionLabel="Refresh Graph"
          onAction={fetchRings}
        />
      </div>
    );
  }

  return (
    <div className="max-w-[1080px] mx-auto px-6 sm:px-10 pt-8 pb-20 font-sans text-[#E8E6DE] animate-fade-in space-y-6">
      {/* Header */}
      <div className="stagger-summary border-b border-[#2A2D35] pb-4">
        <h1 className="text-xl font-semibold text-[#E8E6DE] tracking-tight">Syndicate network graph</h1>
        <p className="text-xs text-[#8B8F98] mt-0.5">
          Cross-merchant community clustering detecting shared devices, bank accounts, and UPI proxies
        </p>
      </div>

      {/* Main Grid: Ring Selector on Left, Graph on Right */}
      <div className="stagger-panel grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ring Selector List */}
        <div className="space-y-3">
          <div className="text-xs font-medium text-[#8B8F98]">
            Detected syndicates ({rings.length})
          </div>

          <div className="space-y-2">
            {rings.map((ring) => {
              const isSelected = ring.ring_id === selectedRingId;
              return (
                <div
                  key={ring.ring_id}
                  onClick={() => setSelectedRingId(ring.ring_id)}
                  className={`p-3.5 rounded-md border transition-colors cursor-pointer space-y-2 ${
                    isSelected
                      ? 'bg-[#1C1F26] border-[#B8862E] text-[#E8E6DE]'
                      : 'bg-[#1C1F26] border-[#2A2D35] text-[#8B8F98] hover:border-[#3A3E48]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium text-[#E8E6DE]">{ring.name}</span>
                    <span className="text-[11.5px] font-mono text-[#A83D3D] font-semibold">{ring.network_risk.toFixed(0)} risk</span>
                  </div>

                  <div className="text-[12px] text-[#8B8F98] space-y-0.5">
                    <div>{ring.ring_size} collusive merchants</div>
                    <div className="text-[11.5px] text-[#B8862E]">Anchor: <span className="font-mono">{ring.dominant_shared_identifier}</span></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Interactive Graph Panel */}
        <div className="lg:col-span-2 bg-[#1C1F26] border border-[#2A2D35] rounded-md p-4 space-y-3">
          <div className="flex justify-between items-center pb-2 border-b border-[#2A2D35]">
            <div className="text-xs text-[#E8E6DE]">
              <span className="text-[#8B8F98] mr-1.5">Selected ring:</span>
              <span className="font-semibold">{currentRing?.name || selectedRingId}</span>
            </div>

            {currentRing?.members[0] && (
              <button
                onClick={() => onNavigateToInvestigation(currentRing.members[0])}
                className="flex items-center gap-1 text-xs text-[#B8862E] hover:text-[#E8E6DE] transition-colors cursor-pointer"
              >
                <span>Investigate {currentRing.members[0]}</span>
                <ArrowRight className="h-3 w-3" />
              </button>
            )}
          </div>

          <div className="h-[440px] rounded border border-[#2A2D35] overflow-hidden relative">
            <ErrorBoundary
              isComponentLevel
              fallbackTitle="Syndicate Graph Layout Paused"
              fallbackMessage="Could not render the topological layout for this syndicate. Cluster metadata is available."
            >
              <CytoscapeGraph
                graphData={ringGraph}
                selectedMerchantId={currentRing?.members[0]}
                onSelectMerchant={onNavigateToInvestigation}
                height="440px"
                title=""
              />
            </ErrorBoundary>
          </div>
        </div>
      </div>
    </div>
  );
};
