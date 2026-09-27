import React from 'react';
import { Target, Radio, RefreshCw, Plus, Cpu, PlaySquare, BarChart3, Globe, Newspaper } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, onAddCompetitor, onGlobalCheck, isCheckingAll, wsConnected }) {
  const navTabs = [
    { id: 'dashboard', label: 'Executive Dashboard', icon: BarChart3 },
    { id: 'competitors', label: 'Competitors & Sources', icon: Globe },
    { id: 'articles', label: 'Detected Articles & SLA', icon: Newspaper },
    { id: 'demo', label: 'Interactive Demo Blog', icon: PlaySquare, badge: 'Testbed' },
    { id: 'benchmark', label: '100-Website Scale Bench', icon: Cpu, badge: 'Scale' },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-slate-50/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-black flex items-center justify-center shadow-lg shadow-black/10">
              <Target className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight text-black">
                  TrendTracker
                </span>
                <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-100 text-black border border-slate-300">
                  v1.0 Pro
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium hidden sm:block">
                Real-Time Competitor Content Monitoring & Intelligence
              </p>
            </div>
          </div>

          {/* Right Action Bar */}
          <div className="flex items-center gap-3">
            {/* Live WebSocket Status Indicator */}
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-xs text-slate-300">
              <span className="relative flex h-2 w-2">
                {wsConnected ? (
                  <>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-black opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-black"></span>
                  </>
                ) : (
                  <span className="inline-flex rounded-full h-2 w-2 bg-slate-500"></span>
                )}
              </span>
              <span className="font-mono text-[11px] text-slate-300">
                {wsConnected  ? 'Live Stream Active' : 'Connecting Stream...'}
              </span>
            </div>

            {/* Check All Button */}
            <button
              onClick={onGlobalCheck}
              disabled={isCheckingAll}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                isCheckingAll
                   ? 'bg-slate-100 text-slate-400 border-slate-300 cursor-not-allowed' : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-300 hover:border-slate-400 shadow-sm'
              }`}
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isCheckingAll  ? 'animate-spin text-black' : 'text-slate-500'}`} />
              <span className="hidden md:inline">{isCheckingAll  ? 'Checking All Sites...' : 'Trigger Scan'}</span>
            </button>

            {/* Add Competitor Button */}
            <button
              onClick={onAddCompetitor}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold bg-black hover:bg-slate-800 text-white shadow-md shadow-black/10 transition-all border border-black"
            >
              <Plus className="h-4 w-4" />
              <span>Add Competitor</span>
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex space-x-1 sm:space-x-2 overflow-x-auto py-2 scrollbar-none border-t border-slate-200/60">
          {navTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                     ? 'bg-slate-100 text-black border border-slate-300 shadow-sm' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-transparent'
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive  ? 'text-black' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold uppercase tracking-wider ${
                    isActive  ? 'bg-black/10 text-black' : 'bg-slate-100 text-slate-400'
                  }`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
