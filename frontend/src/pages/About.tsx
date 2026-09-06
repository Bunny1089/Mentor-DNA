import React from 'react';

export const About: React.FC = () => {
  return (
    <div className="max-w-[880px] mx-auto px-6 sm:px-10 pt-8 pb-24 font-sans text-[#E8E6DE] animate-fade-in">
      {/* Header */}
      <div className="stagger-summary mb-8 pb-6 border-b border-[#2A2D35]">
        <h1 className="text-xl font-semibold text-[#E8E6DE] tracking-tight">About Merchant DNA</h1>
        <p className="text-xs text-[#8B8F98] mt-1">
          Cross-merchant fraud intelligence and coordinated risk mitigation architecture.
        </p>
      </div>

      <div className="stagger-panel space-y-6">
        {/* Tagline / Intro Panel */}
        <div className="bg-[#1C1F26] border border-[#2A2D35] rounded-md p-6 space-y-3">
          <div className="text-[11px] font-mono text-[#B8862E] uppercase tracking-wider">
            Executive Summary
          </div>
          <p className="text-sm font-medium text-[#E8E6DE] leading-relaxed">
            Cross-merchant fraud intelligence for payment platforms — behavioral scoring and network analysis that catch what single-merchant tools structurally can't see.
          </p>
        </div>

        {/* The Blind Spot Panel */}
        <div className="bg-[#1C1F26] border border-[#2A2D35] rounded-md p-6 space-y-4">
          <div className="border-b border-[#2A2D35] pb-3">
            <h2 className="text-sm font-semibold text-[#E8E6DE]">The Blind Spot</h2>
            <p className="text-xs text-[#8B8F98] mt-1">
              Traditional payment fraud detection operates at the individual transaction level, evaluating buyer card velocity, 3DS challenges, and IP geolocation in isolation. However, modern merchant-side fraud operates through distributed networks:
            </p>
          </div>

          <ul className="space-y-3 text-xs text-[#8B8F98] leading-relaxed">
            <li className="flex items-start gap-2.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[#B8862E] mt-1.5 shrink-0" />
              <div>
                <strong className="text-[#E8E6DE]">Distributed Syndicate Shells:</strong> Fraud rings register 10 to 50 seemingly legitimate storefronts with valid KYC documents. Each merchant maintains low, steady volumes that stay well below transaction-level velocity tripwires.
              </div>
            </li>
            <li className="flex items-start gap-2.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[#B8862E] mt-1.5 shrink-0" />
              <div>
                <strong className="text-[#E8E6DE]">Mule Accounts & Rapid Cashouts:</strong> Sleeper accounts remain dormant for 30–60 days to establish baseline history, then process concentrated transaction bursts followed by immediate settlement withdrawal requests before chargebacks arrive.
              </div>
            </li>
            <li className="flex items-start gap-2.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[#B8862E] mt-1.5 shrink-0" />
              <div>
                <strong className="text-[#E8E6DE]">Aggregator Liability:</strong> When merchant defaults and chargebacks occur, payment aggregators bear financial liability for unrecoverable negative balances.
              </div>
            </li>
          </ul>
        </div>

        {/* The Approach Panel */}
        <div className="bg-[#1C1F26] border border-[#2A2D35] rounded-md p-6 space-y-4">
          <div className="border-b border-[#2A2D35] pb-3">
            <h2 className="text-sm font-semibold text-[#E8E6DE]">The Approach</h2>
            <p className="text-xs text-[#8B8F98] mt-1">
              Merchant DNA addresses cross-merchant risk through three interconnected components:
            </p>
          </div>

          <ol className="space-y-3 text-xs text-[#8B8F98] leading-relaxed">
            <li className="flex items-start gap-3">
              <span className="font-mono text-xs text-[#B8862E] font-medium shrink-0">1.</span>
              <div>
                <strong className="text-[#E8E6DE]">Behavioral Telemetry (60% Weight):</strong> A gradient boosted decision tree model evaluating 30+ merchant-level features, including category ticket deviations, off-peak velocity, buyer concentration (HHI), and settlement turnaround speed.
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="font-mono text-xs text-[#B8862E] font-medium shrink-0">2.</span>
              <div>
                <strong className="text-[#E8E6DE]">Network Graph Analysis (40% Weight):</strong> Bipartite graph modeling and Louvain community detection to uncover shared devices, phone numbers, bank accounts, and UPI VPAs.
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="font-mono text-xs text-[#B8862E] font-medium shrink-0">3.</span>
              <div>
                <strong className="text-[#E8E6DE]">Grounded Synthesis & Bounded Actions:</strong> An AI copilot providing grounded synthesis constrained to structured evidence inputs, coupled with reversible settlement holds that protect liquidity while preserving checkout operations for review.
              </div>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default About;
