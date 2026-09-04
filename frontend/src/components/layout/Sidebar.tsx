import React from 'react';
import {
  LayoutDashboard,
  AlertTriangle,
  Users,
  Network,
  ShieldAlert,
  BarChart3,
  Flame,
  ShieldCheck,
} from 'lucide-react';
import type { SystemStatus } from '../../types';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  systemStatus: SystemStatus | null;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, onSelectTab, systemStatus }) => {
  const sections = [
    {
      title: 'Monitor',
      items: [
        { id: 'overview', label: 'Overview', icon: LayoutDashboard },
        { id: 'alerts', label: 'Alerts', icon: AlertTriangle, count: 54 },
      ],
    },
    {
      title: 'Investigate',
      items: [
        { id: 'merchants', label: 'Merchants', icon: Users, count: systemStatus?.merchant_count || 240 },
        { id: 'network', label: 'Networks', icon: Network, count: systemStatus?.detected_rings_count || 3 },
        { id: 'investigation', label: 'Case dossier', icon: ShieldAlert },
      ],
    },
    {
      title: 'Validate',
      items: [
        { id: 'evaluation', label: 'Evaluation', icon: BarChart3 },
        { id: 'simulation', label: 'Simulation', icon: Flame },
      ],
    },
  ];

  return (
    <aside className="w-52 bg-[#1C1F26] border-r border-[#2A2D35] flex flex-col justify-between h-screen select-none shrink-0 font-sans text-xs">
      {/* Brand Header */}
      <div>
        <div className="p-3.5 border-b border-[#2A2D35] flex items-center gap-2.5">
          <div className="h-6 w-6 rounded bg-[#20232B] border border-[#2A2D35] flex items-center justify-center text-[#B8862E] shrink-0">
            <ShieldCheck className="h-3.5 w-3.5 text-[#B8862E]" />
          </div>
          <div>
            <div className="font-semibold text-[13px] text-[#E8E6DE] tracking-tight leading-none">
              Merchant DNA
            </div>
            <div className="text-[10.5px] text-[#8B8F98] mt-0.5">Risk intelligence</div>
          </div>
        </div>

        {/* Grouped Navigation */}
        <nav className="p-2 space-y-3.5 mt-1">
          {sections.map((sec) => (
            <div key={sec.title}>
              <div className="px-2.5 py-0.5 text-[10px] font-medium text-[#5A5E68] tracking-wider">
                {sec.title}
              </div>
              <div className="space-y-0.5 mt-0.5">
                {sec.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => onSelectTab(item.id)}
                      className={`w-full flex items-center justify-between px-2.5 py-1.5 rounded text-[12px] transition-colors cursor-pointer ${
                        isActive
                          ? 'bg-[#20232B] text-[#E8E6DE] font-medium border border-[#2A2D35]'
                          : 'text-[#8B8F98] hover:text-[#E8E6DE] hover:bg-[#20232B]/60'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <Icon
                          className={`h-3.5 w-3.5 ${
                            isActive ? 'text-[#B8862E]' : 'text-[#8B8F98]'
                          }`}
                        />
                        <span>{item.label}</span>
                      </div>
                      {item.count !== undefined && (
                        <span className="font-mono text-[10.5px] text-[#5A5E68]">
                          {item.count}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </div>

      {/* Subtle System Status */}
      <div className="p-2.5 m-2 rounded bg-[#20232B] border border-[#2A2D35] text-[10.5px] space-y-1 font-sans">
        <div className="flex items-center justify-between text-[#8B8F98]">
          <span className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-[#4B7A6F] animate-pulse"></span>
            Telemetry feed
          </span>
          <span className="text-[#4B7A6F] font-medium">Online</span>
        </div>
        <div className="flex justify-between text-[#5A5E68] pt-1 border-t border-[#2A2D35] font-mono text-[10px]">
          <span>{systemStatus?.merchant_count || 240} monitored</span>
          <span>{systemStatus?.detected_rings_count || 3} rings</span>
        </div>
      </div>
    </aside>
  );
};
