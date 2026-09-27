import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';
import { Activity, Radio, Cpu, FileText } from 'lucide-react';

const METHOD_COLORS = {
  RSS: '#ea580c',        // Orange
  SITEMAP: '#0284c7',    // Cyan/Blue
  DIRECT_PAGE: '#8b5cf6' // Purple
};

export default function PerformanceCharts({ stats }) {
  const trendData = stats?.delay_trends || [];
  const methodDist = stats?.method_distribution || { RSS: 0, SITEMAP: 0, DIRECT_PAGE: 0 };

  const pieData = [
    { name: 'RSS / Atom', value: methodDist.RSS || 0, color: METHOD_COLORS.RSS },
    { name: 'XML Sitemap', value: methodDist.SITEMAP || 0, color: METHOD_COLORS.SITEMAP },
    { name: 'Direct Page', value: methodDist.DIRECT_PAGE || 0, color: METHOD_COLORS.DIRECT_PAGE },
  ].filter(d => d.value > 0);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white border border-slate-300 p-3 rounded-xl shadow-xl">
          <p className="text-xs font-bold text-slate-900 mb-1">{data.label}</p>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-slate-400">Detection Delay:</span>
            <span className="font-mono font-bold text-black">{data.delay_min} mins ({data.delay_sec}s)</span>
          </div>
          <div className="flex items-center gap-2 text-xs mt-1">
            <span className="text-slate-400">Method:</span>
            <span className="font-semibold text-black">{data.method}</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-1">
            <span>Detected:</span>
            <span>{data.detected_at}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      {/* Chart 1: Detection Delay Timeline */}
      <div className="lg:col-span-2 glass-panel rounded-2xl p-5 border border-slate-200/80">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <Activity className="h-4 w-4 text-black" />
              Detection Delay per Article (Minutes)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Target SLA threshold benchmark is 5 minutes (300 seconds)
            </p>
          </div>
          <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-full bg-white text-black border border-slate-200">
            5.0 min Benchmark
          </span>
        </div>

        <div className="h-64 w-full">
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                <XAxis
                  dataKey="label"
                  tick={{ fill: '#94a3b8', fontSize: 10 }}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={{ stroke: '#334155' }}
                />
                <YAxis
                  tick={{ fill: '#94a3b8', fontSize: 10 }}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={{ stroke: '#334155' }}
                  unit="m"
                />
                <Tooltip content={<CustomTooltip />} />
                <ReferenceLine
                  y={5}
                  stroke="#ef4444"
                  strokeDasharray="4 4"
                  label={{ value: '5m Target SLA', fill: '#ef4444', fontSize: 10, position: 'right' }}
                />
                <Bar dataKey="delay_min" radius={[4, 4, 0, 0]}>
                  {trendData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={entry.delay_min <= 5  ? '#6366f1' : '#f59e0b'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
              <Activity className="h-8 w-8 mb-2 stroke-1 text-slate-300" />
              <span>No detection delay events recorded yet. Trigger a scan or publish a demo article!</span>
            </div>
          )}
        </div>
      </div>

      {/* Chart 2: Method Distribution */}
      <div className="glass-panel rounded-2xl p-5 border border-slate-200/80 flex flex-col justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <Radio className="h-4 w-4 text-black" />
            Detection Strategy Breakdown
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Detections categorized across the 3 mandatory methods
          </p>
        </div>

        <div className="h-48 w-full flex items-center justify-center">
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-slate-400 text-xs text-center">
              Awaiting detection events across RSS, Sitemap, and Direct Page.
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-200/60 text-center">
          <div className="p-2 rounded-lg bg-black border border-black">
            <div className="text-[10px] text-white font-bold uppercase">RSS</div>
            <div className="text-base font-bold font-mono text-white">{methodDist.RSS || 0}</div>
          </div>
          <div className="p-2 rounded-lg bg-black border border-black">
            <div className="text-[10px] text-white font-bold uppercase">Sitemap</div>
            <div className="text-base font-bold font-mono text-white">{methodDist.SITEMAP || 0}</div>
          </div>
          <div className="p-2 rounded-lg bg-slate-200 border border-slate-300">
            <div className="text-[10px] text-black font-bold uppercase">Direct</div>
            <div className="text-base font-bold font-mono text-slate-900">{methodDist.DIRECT_PAGE || 0}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
