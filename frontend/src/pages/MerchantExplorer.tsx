import React, { useEffect, useState, useCallback } from 'react';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';
import { getMerchants } from '../services/api';
import { LoadingState, ErrorState, EmptyState } from '../components/common/StateView';
import type { MerchantSummaryItem, RiskLevel } from '../types';

interface MerchantExplorerProps {
  onNavigateToInvestigation: (merchantId: string) => void;
}

export const MerchantExplorer: React.FC<MerchantExplorerProps> = ({ onNavigateToInvestigation }) => {
  const [merchants, setMerchants] = useState<MerchantSummaryItem[]>([]);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [search, setSearch] = useState('');
  const [selectedRisk, setSelectedRisk] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  const fetchMerchants = useCallback(async () => {
    setIsLoading(true);
    setLoadError(null);
    try {
      const riskParam = selectedRisk !== 'ALL' ? (selectedRisk as RiskLevel) : undefined;
      const catParam = selectedCategory !== 'ALL' ? selectedCategory : undefined;
      const searchParam = search.trim() ? search.trim() : undefined;

      const data = await getMerchants({
        page,
        page_size: pageSize,
        risk_level: riskParam,
        category: catParam,
        search: searchParam,
      });

      setMerchants(data.merchants);
      setTotalPages(data.total_pages);
      setTotalCount(data.total_count);
    } catch (err: any) {
      console.error('Failed to load merchants:', err);
      setLoadError('Failed to load merchant registry from backend engine.');
    } finally {
      setIsLoading(false);
    }
  }, [page, pageSize, selectedRisk, selectedCategory, search]);

  useEffect(() => {
    fetchMerchants();
  }, [fetchMerchants]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchMerchants();
  };

  return (
    <div className="max-w-[1080px] mx-auto px-6 sm:px-10 pt-8 pb-20 font-sans text-[#E8E6DE] animate-fade-in space-y-6">
      {/* Header & Search */}
      <div className="stagger-summary flex flex-wrap items-center justify-between gap-4 border-b border-[#2A2D35] pb-4">
        <div>
          <h1 className="text-xl font-semibold text-[#E8E6DE] tracking-tight">Merchant directory</h1>
          <p className="text-xs text-[#8B8F98] mt-0.5">
            {totalCount} registered merchants monitored for behavioral anomalies
          </p>
        </div>

        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 min-w-[280px]">
          <div className="flex items-center gap-2 bg-[#1C1F26] border border-[#2A2D35] rounded px-3 py-1.5 text-xs flex-1">
            <Search className="h-3.5 w-3.5 text-[#8B8F98] shrink-0" />
            <input
              type="text"
              placeholder="Search by ID or business name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-transparent text-xs text-[#E8E6DE] placeholder-[#5A5E68] focus:outline-none font-sans"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 rounded bg-[#20232B] hover:bg-[#2A2D35] border border-[#2A2D35] text-xs text-[#E8E6DE] cursor-pointer"
          >
            Search
          </button>
        </form>
      </div>

      {/* Filters Bar */}
      <div className="stagger-tabs flex items-center gap-4 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-[#8B8F98]">Risk tier:</span>
          <select
            value={selectedRisk}
            onChange={(e) => {
              setSelectedRisk(e.target.value);
              setPage(1);
            }}
            className="bg-[#1C1F26] border border-[#2A2D35] rounded px-2.5 py-1 text-xs text-[#E8E6DE] focus:outline-none cursor-pointer"
          >
            <option value="ALL">All tiers</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[#8B8F98]">Category:</span>
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setPage(1);
            }}
            className="bg-[#1C1F26] border border-[#2A2D35] rounded px-2.5 py-1 text-xs text-[#E8E6DE] focus:outline-none cursor-pointer"
          >
            <option value="ALL">All categories</option>
            <option value="E_COMMERCE">E-commerce</option>
            <option value="FINANCIAL_SERVICES">Financial services</option>
            <option value="GAMING_AND_DIGITAL">Gaming & digital</option>
            <option value="TRAVEL_AND_HOSPITALITY">Travel & hospitality</option>
            <option value="UTILITIES_AND_BILLS">Utilities & bills</option>
            <option value="JEWELRY_AND_LUXURY">Jewelry & luxury</option>
            <option value="CONSULTING_SERVICES">Consulting services</option>
          </select>
        </div>
      </div>

      {/* Error state */}
      {loadError && merchants.length === 0 && (
        <ErrorState
          title="Merchant Registry Unavailable"
          message={loadError}
          onRetry={fetchMerchants}
        />
      )}

      {/* Loading State */}
      {isLoading && merchants.length === 0 && (
        <LoadingState message="Loading merchant directory..." />
      )}

      {/* Empty State */}
      {!isLoading && !loadError && merchants.length === 0 && (
        <EmptyState
          title="No merchants match criteria"
          message="Try changing the category filter, risk tier, or clearing the search query."
          actionLabel="Reset filters"
          onAction={() => {
            setSelectedRisk('ALL');
            setSelectedCategory('ALL');
            setSearch('');
            setPage(1);
          }}
        />
      )}

      {/* Merchants Table */}
      {merchants.length > 0 && (
        <>
          <div className="stagger-panel overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="text-left text-[12px] font-medium text-[#8B8F98] border-b border-[#2A2D35]">
                  <th className="py-2.5 px-3 font-medium">Merchant</th>
                  <th className="py-2.5 px-3 text-center font-medium">Score</th>
                  <th className="py-2.5 px-3 font-medium">Category</th>
                  <th className="py-2.5 px-3 text-right font-medium">Volume</th>
                  <th className="py-2.5 px-3 text-right font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#2A2D35] text-[13px]">
                {merchants.map((m) => {
                  const isCritical = m.risk_level === 'CRITICAL';
                  const isHigh = m.risk_level === 'HIGH';
                  const tierColor = isCritical
                    ? 'text-[#A83D3D] bg-[rgba(168,61,61,0.12)] border-[#A83D3D]/30'
                    : isHigh
                    ? 'text-[#B8862E] bg-[rgba(184,134,46,0.12)] border-[#B8862E]/30'
                    : 'text-[#4B7A6F] bg-[rgba(75,122,111,0.12)] border-[#4B7A6F]/30';

                  return (
                    <tr
                      key={m.merchant_id}
                      onClick={() => onNavigateToInvestigation(m.merchant_id)}
                      className="hover:bg-[#1C1F26] transition-colors cursor-pointer group"
                    >
                      <td className="py-3 px-3">
                        <div className="font-medium text-[#E8E6DE] group-hover:text-[#B8862E] transition-colors">
                          {m.business_name}
                        </div>
                        <div className="text-xs font-mono text-[#5A5E68]">{m.merchant_id}</div>
                      </td>

                      <td className="py-3 px-3 text-center">
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-mono font-semibold border ${tierColor}`}>
                          {m.overall_risk.toFixed(0)}
                        </span>
                      </td>

                      <td className="py-3 px-3 text-xs text-[#8B8F98]">
                        {m.category.replace(/_/g, ' ').toLowerCase()}
                      </td>

                      <td className="py-3 px-3 text-right font-mono text-xs text-[#8B8F98]">
                        ₹{(m.total_volume / 100000).toFixed(1)}L
                      </td>

                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onNavigateToInvestigation(m.merchant_id);
                          }}
                          className="text-xs text-[#8B8F98] group-hover:text-[#E8E6DE] font-medium transition-colors cursor-pointer"
                        >
                          Dossier →
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="stagger-actions flex items-center justify-between pt-4 border-t border-[#2A2D35] text-xs">
            <span className="text-[#8B8F98]">
              Showing page <span className="font-mono text-[#E8E6DE]">{page}</span> of{' '}
              <span className="font-mono text-[#E8E6DE]">{totalPages}</span>
            </span>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1 || isLoading}
                className="flex items-center gap-1 px-3 py-1.5 rounded bg-[#1C1F26] border border-[#2A2D35] text-[#8B8F98] hover:text-[#E8E6DE] disabled:opacity-40 cursor-pointer"
              >
                <ChevronLeft className="h-3 w-3" />
                <span>Prev</span>
              </button>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages || isLoading}
                className="flex items-center gap-1 px-3 py-1.5 rounded bg-[#1C1F26] border border-[#2A2D35] text-[#8B8F98] hover:text-[#E8E6DE] disabled:opacity-40 cursor-pointer"
              >
                <span>Next</span>
                <ChevronRight className="h-3 w-3" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

