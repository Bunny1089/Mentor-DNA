import { useState, useEffect } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { Dashboard } from './pages/Dashboard';
import { Alerts } from './pages/Alerts';
import { MerchantExplorer } from './pages/MerchantExplorer';
import { MerchantInvestigation } from './pages/MerchantInvestigation';
import { NetworkExplorer } from './pages/NetworkExplorer';
import { Evaluation } from './pages/Evaluation';
import { Simulation } from './pages/Simulation';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { getSystemStatus } from './services/api';
import type { SystemStatus } from './types';

import { DEMO_CONFIG } from './config/demoConfig';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [selectedMerchantId, setSelectedMerchantId] = useState<string>(DEMO_CONFIG.GOLDEN_MERCHANT_ID);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const [backendError, setBackendError] = useState(false);

  const fetchStatus = async () => {
    setIsSyncing(true);
    try {
      const status = await getSystemStatus();
      setSystemStatus(status);
      setBackendError(false);
    } catch (err) {
      console.error('Backend status check failed:', err);
      setBackendError(true);
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleNavigateToInvestigation = (merchantId: string) => {
    setSelectedMerchantId(merchantId);
    setCurrentTab('investigation');
  };

  const getPageHeaderInfo = () => {
    switch (currentTab) {
      case 'overview':
        return {
          title: 'Risk Intelligence Console',
          subtitle: 'Cross-merchant fraud intelligence for payment platforms — behavioral scoring and network analysis that catch what single-merchant tools structurally can\'t see.',
        };
      case 'alerts':
        return {
          title: 'Alert Queue',
          subtitle: 'Triage anomalous merchants flagged by hybrid ML and graph community detectors',
        };
      case 'merchants':
        return {
          title: 'Merchant Registry',
          subtitle: 'Searchable directory with behavioral and graph risk scores',
        };
      case 'network':
        return {
          title: 'Collusive Syndicates & Entity Graph',
          subtitle: 'Cross-merchant entity graph detecting shared hardware, bank accounts, and VPAs',
        };
      case 'investigation':
        return {
          title: 'Forensic Investigation Dossier',
          subtitle: `Deep-dive case analysis and bounded action execution for ${selectedMerchantId}`,
        };
      case 'evaluation':
        return {
          title: 'Model Evaluation',
          subtitle: 'Offline evaluation benchmarks, sensitivity breakdowns, and false-positive cost analysis',
        };
      case 'simulation':
        return {
          title: 'Live Scenario Simulator',
          subtitle: 'Inject dynamic mule velocity spikes and coordinated syndicates in real time',
        };
      default:
        return {
          title: 'Merchant DNA',
          subtitle: 'Cross-merchant fraud intelligence for payment platforms',
        };
    }
  };

  const { title, subtitle } = getPageHeaderInfo();

  return (
    <ErrorBoundary>
      <div className="flex h-screen w-screen bg-[#14161B] overflow-hidden text-[#E8E6DE] font-sans">
        {/* Left Navigation Sidebar */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          systemStatus={systemStatus}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#14161B]">
          {/* Unreachable Backend Banner */}
          {backendError && (
            <div className="bg-red-950/80 border-b border-red-800/60 px-4 py-2 flex items-center justify-between text-red-200 text-xs font-sans">
              <div className="flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
                <span>Backend server unreachable at 127.0.0.1:8000. Displaying cached intelligence telemetry.</span>
              </div>
              <button
                onClick={fetchStatus}
                disabled={isSyncing}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-red-900/60 hover:bg-red-800 text-white font-sans text-xs transition-colors cursor-pointer border border-red-700/50"
              >
                <RefreshCw className={`w-3 h-3 ${isSyncing ? 'animate-spin' : ''}`} />
                <span>{isSyncing ? 'Connecting...' : 'Reconnect'}</span>
              </button>
            </div>
          )}

          {/* Top Sticky Header */}
          <Header
            title={title}
            subtitle={subtitle}
            systemStatus={systemStatus}
            onRefresh={fetchStatus}
            isLoading={isSyncing}
          />

          {/* Scrollable Page View Container */}
          <main className="flex-1 overflow-y-auto bg-[#14161B]">
            <div className="w-full pb-12">
              <ErrorBoundary fallbackTitle="Page View Error" fallbackMessage="An error occurred while loading this page view. You can safely retry or navigate elsewhere.">
                {currentTab === 'overview' && (
                  <Dashboard
                    onNavigateToInvestigation={handleNavigateToInvestigation}
                    onNavigateToTab={setCurrentTab}
                  />
                )}

                {currentTab === 'alerts' && (
                  <Alerts onNavigateToInvestigation={handleNavigateToInvestigation} />
                )}

                {currentTab === 'merchants' && (
                  <MerchantExplorer onNavigateToInvestigation={handleNavigateToInvestigation} />
                )}

                {currentTab === 'network' && (
                  <NetworkExplorer onNavigateToInvestigation={handleNavigateToInvestigation} />
                )}

                {currentTab === 'investigation' && (
                  <MerchantInvestigation
                    merchantId={selectedMerchantId}
                    onBack={() => setCurrentTab('alerts')}
                    onSelectMerchant={handleNavigateToInvestigation}
                  />
                )}

                {currentTab === 'evaluation' && <Evaluation />}

                {currentTab === 'simulation' && (
                  <Simulation
                    onNavigateToInvestigation={handleNavigateToInvestigation}
                    onNavigateToTab={setCurrentTab}
                  />
                )}
              </ErrorBoundary>
            </div>
          </main>
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;

