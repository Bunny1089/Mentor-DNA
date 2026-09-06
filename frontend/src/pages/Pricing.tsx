import React from 'react';

interface PricingTier {
  name: string;
  segment: string;
  price: string;
  description: string;
}

const PRICING_TIERS: PricingTier[] = [
  {
    name: 'Starter',
    segment: 'individual/WhatsApp sellers',
    price: 'Free / ₹49–99/mo',
    description: 'Public trust badge only; a network-effect funnel, not a revenue line',
  },
  {
    name: 'Growing SMB',
    segment: 'small D2C brands',
    price: '₹499–1,999/mo',
    description: 'Basic risk dashboard, trust badge, limited alerts',
  },
  {
    name: 'Established Merchant',
    segment: 'multi-location retailers',
    price: '₹5,000–25,000/mo or 0.02–0.05% bps',
    description: 'Full investigation dashboard, instant-settlement eligibility',
  },
  {
    name: 'Enterprise / Large Platform',
    segment: 'large retailers, marketplaces',
    price: 'Annual license + volume bps',
    description: 'Dedicated console, sub-merchant vetting API',
  },
  {
    name: 'Aggregator / Bank (B2B2B)',
    segment: 'other aggregators, banks',
    price: 'Per-query or annual licensing',
    description: 'Risk-as-a-Service, highest margin',
  },
];

export const Pricing: React.FC = () => {
  return (
    <div className="max-w-[880px] mx-auto px-6 sm:px-10 pt-8 pb-24 font-sans text-[#E8E6DE] animate-fade-in">
      {/* Header */}
      <div className="stagger-summary mb-8 pb-6 border-b border-[#2A2D35]">
        <h1 className="text-xl font-semibold text-[#E8E6DE] tracking-tight">How It's Monetized</h1>
        <p className="text-xs text-[#8B8F98] mt-1">
          Tiered commercial packaging and network-effect trust model.
        </p>
      </div>

      {/* Grid of 5 Tier Panels */}
      <div className="stagger-panel grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {PRICING_TIERS.map((tier) => (
          <div
            key={tier.name}
            className="bg-[#1C1F26] border border-[#2A2D35] rounded-md p-5 flex flex-col justify-between"
          >
            <div>
              <h3 className="text-sm font-semibold text-[#E8E6DE]">{tier.name}</h3>
              <div className="text-xs text-[#8B8F98] mt-1">{tier.segment}</div>
              <div className="font-mono text-xs text-[#B8862E] font-medium mt-3 mb-2">
                {tier.price}
              </div>
              <p className="text-xs text-[#8B8F98] leading-relaxed">
                {tier.description}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Closing Line */}
      <div className="mt-8 pt-4 border-t border-[#2A2D35] text-xs text-[#8B8F98] leading-relaxed">
        All tiers share one engine — the free tier strengthens the cross-merchant signal every paying tier depends on.
      </div>
    </div>
  );
};

export default Pricing;
