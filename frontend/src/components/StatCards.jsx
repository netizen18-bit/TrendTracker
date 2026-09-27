import React from 'react';
import { Globe, Clock, Zap, AlertTriangle, ShieldCheck, Flame } from 'lucide-react';

export default function StatCards({ stats }) {
  const comp = stats?.competitors || { total: 0, active: 0, error: 0 };
  const perf = stats?.performance || {
    avg_delay_formatted: 'N/A',
    fastest_delay_formatted: 'N/A',
    slowest_delay_formatted: 'N/A',
    within_sla_percent: 100,
    over_sla_percent: 0,
    total_articles: 0
  };
  const art = stats?.articles || { total: 0, today: 0 };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Card 1: Monitored Competitors */}
      <div className="glass-panel rounded-2xl p-5 relative overflow-hidden border border-slate-200/80 hover:border-slate-300 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Monitored Sites</span>
          <div className="h-8 w-8 rounded-lg bg-black/10 border border-slate-300 flex items-center justify-center text-black">
            <Globe className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-extrabold text-slate-900 tracking-tight">{comp.total}</span>
          <span className="text-xs font-semibold text-black bg-slate-200 border border-slate-300 px-2 py-0.5 rounded-full flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-black animate-pulse"></span>
            {comp.active} Active
          </span>
        </div>
        <div className="mt-2 text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-200/60 pt-2">
          <span>Continuous Polling</span>
          <span className="font-mono text-slate-300">{comp.error} Issues Detected</span>
        </div>
      </div>

      {/* Card 2: Average Detection Delay */}
      <div className="glass-panel-glow rounded-2xl p-5 relative overflow-hidden transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-black uppercase tracking-wider">Avg Detection Delay</span>
          <div className="h-8 w-8 rounded-lg bg-black/10 border border-slate-300 flex items-center justify-center text-black">
            <Clock className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-extrabold text-slate-900 tracking-tight font-mono">
            {perf.avg_delay_formatted || '0s'}
          </span>
          <span className="text-xs font-semibold text-black bg-slate-200 border border-slate-300 px-2 py-0.5 rounded-full">
            Target &lt; 5m
          </span>
        </div>
        <div className="mt-2 text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-200/60 pt-2">
          <span>Total Monitored Articles</span>
          <span className="font-mono text-black font-semibold">{art.total} Articles</span>
        </div>
      </div>

      {/* Card 3: Fastest & Slowest Latency extremes */}
      <div className="glass-panel rounded-2xl p-5 relative overflow-hidden border border-slate-200/80 hover:border-slate-300 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Speed Extremes</span>
          <div className="h-8 w-8 rounded-lg bg-slate-500/10 border border-slate-300 flex items-center justify-center text-slate-600">
            <Zap className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-2">
          <div>
            <div className="text-[10px] uppercase font-bold text-black">Fastest</div>
            <div className="text-xl font-bold font-mono text-slate-900">{perf.fastest_delay_formatted || 'N/A'}</div>
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-slate-600">Slowest</div>
            <div className="text-xl font-bold font-mono text-black">{perf.slowest_delay_formatted || 'N/A'}</div>
          </div>
        </div>
        <div className="mt-2 text-[11px] text-slate-400 flex items-center justify-between border-t border-slate-200/60 pt-2">
          <span>Discovered Today</span>
          <span className="font-mono text-black font-semibold">+{art.today} New</span>
        </div>
      </div>

      {/* Card 4: 5-Minute SLA Compliance */}
      <div className="glass-panel rounded-2xl p-5 relative overflow-hidden border border-slate-200/80 hover:border-slate-300 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">5-Min SLA Compliance</span>
          <div className="h-8 w-8 rounded-lg bg-black/10 border border-slate-300 flex items-center justify-center text-black">
            <ShieldCheck className="h-4 w-4" />
          </div>
        </div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="text-3xl font-extrabold text-slate-900 tracking-tight font-mono">
            {perf.within_sla_percent}%
          </span>
          <span className="text-xs font-semibold text-slate-400">
            Within Target
          </span>
        </div>
        {/* Visual Progress Bar */}
        <div className="mt-3 w-full bg-slate-100 rounded-full h-2 overflow-hidden flex">
          <div
            className="bg-black h-full rounded-full transition-all duration-500"
            style={{ width: `${perf.within_sla_percent}%` }}
          ></div>
          <div
            className="bg-slate-500 h-full transition-all duration-500"
            style={{ width: `${perf.over_sla_percent}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}
