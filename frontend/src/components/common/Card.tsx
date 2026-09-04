import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  headerAction?: React.ReactNode;
  accent?: 'none' | 'cyan' | 'red' | 'amber' | 'emerald';
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  headerAction,
  accent = 'none',
}) => {
  const accentBorders = {
    none: 'border-[#2A2D35]',
    cyan: 'border-[#0284C7]/60 shadow-[0_0_15px_rgba(2,132,199,0.1)]',
    red: 'border-[#A83D3D]/60 shadow-[0_0_15px_rgba(168,61,61,0.1)]',
    amber: 'border-[#B8862E]/60 shadow-[0_0_15px_rgba(184,134,46,0.1)]',
    emerald: 'border-[#4B7A6F]/60 shadow-[0_0_15px_rgba(75,122,111,0.1)]',
  };

  return (
    <div
      className={`bg-[#1C1F26] rounded-md border ${accentBorders[accent]} p-5 transition-all duration-200 hover:border-[#3A3E48] ${className}`}
    >
      {(title || headerAction) && (
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#2A2D35]">
          <div>
            {title && <h3 className="text-[14px] font-semibold text-[#E8E6DE] tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-[#8B8F98] mt-0.5">{subtitle}</p>}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
