import React, { useState } from 'react';
import { Globe, RefreshCw, Trash2, Power, ExternalLink, Radio, Compass, FileCode2, Clock, CheckCircle2, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function CompetitorsView({ competitors, onRefresh, onAddClick }) {
  const [checkingId, setCheckingId] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const handleCheckNow = async (id) => {
    setCheckingId(id);
    try {
      await api.checkCompetitor(id);
      onRefresh();
    } catch (err) {
      alert('Check failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setCheckingId(null);
    }
  };

  const handleToggle = async (id) => {
    try {
      await api.toggleCompetitor(id);
      onRefresh();
    } catch (err) {
      alert('Toggle failed: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to remove ${name} from monitoring?`)) return;
    setDeletingId(id);
    try {
      await api.deleteCompetitor(id);
      onRefresh();
    } catch (err) {
      alert('Delete failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Globe className="h-4 w-4 text-black" />
            Monitored Competitor Ecosystem ({competitors.length})
          </h2>
          <p className="text-xs text-slate-400">
            Real-time multi-target monitoring configurations with automatic source detection
          </p>
        </div>
        <button
          onClick={onAddClick}
          className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-black hover:bg-slate-800 text-white shadow-md shadow-black/10 transition-all"
        >
          + Add Target
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {competitors.map((comp) => {
          const isChecking = checkingId === comp.id;
          const isDeleting = deletingId === comp.id;
          const isDemo = comp.website_url?.includes('/demo');

          return (
            <div
              key={comp.id}
              className={`glass-panel rounded-2xl p-5 border transition-all relative overflow-hidden flex flex-col justify-between ${
                isDemo  ? 'border-slate-300 bg-white/90' : 'border-slate-200/80 hover:border-slate-300'
              }`}
            >
              {isDemo && (
                <div className="absolute top-0 right-0 bg-black text-[10px] font-extrabold uppercase px-3 py-0.5 rounded-bl-lg tracking-wider text-white">
                  Interactive Testbed
                </div>
              )}

              {/* Top Row: Name & Status */}
              <div>
                <div className="flex items-start justify-between gap-2 pr-12">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      {comp.name}
                    </h3>
                    <a
                      href={comp.website_url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-[11px] text-slate-400 hover:text-black flex items-center gap-1 mt-0.5 font-mono truncate max-w-[200px]"
                    >
                      <span>{comp.website_url.replace('https://', '').replace('http://', '')}</span>
                      <ExternalLink className="h-3 w-3 flex-shrink-0" />
                    </a>
                  </div>
                </div>

                {/* Status & Last Check */}
                <div className="mt-3 flex items-center gap-2 text-xs">
                  <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold ${
                    comp.status === 'active' && comp.monitoring_enabled
                      ? 'bg-slate-200 text-black border border-slate-300'
                      : comp.status === 'error'
                       ? 'bg-slate-200 text-black border border-slate-300' : 'bg-white text-slate-400 border border-slate-300'
                  }`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${
                      comp.monitoring_enabled  ? 'bg-black animate-pulse' : 'bg-slate-500'
                    }`} />
                    {comp.monitoring_enabled ? (comp.status === 'active'  ? 'Active' : 'Error') : 'Paused'}
                  </span>

                  <span className="text-slate-400">•</span>

                  <span className="text-[11px] text-slate-400 flex items-center gap-1">
                    <Clock className="h-3 w-3 text-slate-400" />
                    {comp.last_checked ? new Date(comp.last_checked).toLocaleTimeString() : 'Pending'}
                  </span>
                </div>

                {/* Discovered Strategies */}
                <div className="mt-3.5 space-y-1.5 border-t border-slate-200/60 pt-3">
                  <div className="text-[10px] uppercase font-bold text-slate-400">Configured Sources</div>
                  <div className="flex flex-wrap gap-1.5">
                    {comp.sources && comp.sources.length > 0 ? (
                      comp.sources.map((s) => (
                        <span
                          key={s.id}
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-md flex items-center gap-1 ${
                            s.source_type === 'RSS'
                              ? 'bg-black text-white border border-black'
                              : s.source_type === 'SITEMAP'
                               ? 'bg-black text-white border border-black' : 'bg-slate-200 text-black border border-slate-300'
                          }`}
                        >
                          {s.source_type === 'RSS' && <Radio className="h-2.5 w-2.5" />}
                          {s.source_type === 'SITEMAP' && <Compass className="h-2.5 w-2.5" />}
                          {s.source_type === 'DIRECT_PAGE' && <FileCode2 className="h-2.5 w-2.5" />}
                          {s.source_type}
                        </span>
                      ))
                    ) : (
                      <span className="text-[10px] text-slate-400">Auto direct page tracking</span>
                    )}
                  </div>
                </div>

                {/* Stats row */}
                <div className="mt-3 p-2.5 rounded-xl bg-slate-50/60 border border-slate-200/80 flex items-center justify-between text-xs">
                  <span className="text-slate-400 text-[11px]">Detected Articles:</span>
                  <span className="font-mono font-bold text-slate-900">{comp.articles_count}</span>
                </div>
              </div>

              {/* Bottom Actions */}
              <div className="mt-4 pt-3 border-t border-slate-200/60 flex items-center justify-between gap-2">
                <button
                  onClick={() => handleToggle(comp.id)}
                  title={comp.monitoring_enabled  ? 'Pause monitoring' : 'Resume monitoring'}
                  className={`p-2 rounded-lg text-xs transition-colors border ${
                    comp.monitoring_enabled
                       ? 'bg-white text-slate-400 hover:text-slate-600 border-slate-200 hover:border-slate-300' : 'bg-slate-50 text-black border-slate-300 hover:bg-slate-200'
                  }`}
                >
                  <Power className="h-3.5 w-3.5" />
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCheckNow(comp.id)}
                    disabled={isChecking}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white hover:bg-slate-100 text-black border border-slate-300 hover:border-slate-600 transition-all disabled:opacity-50"
                  >
                    <RefreshCw className={`h-3 w-3 ${isChecking  ? 'animate-spin text-black' : 'text-slate-400'}`} />
                    <span>{isChecking  ? 'Checking...' : 'Check Now'}</span>
                  </button>

                  <button
                    onClick={() => handleDelete(comp.id, comp.name)}
                    disabled={isDeleting}
                    className="p-2 rounded-lg text-slate-400 hover:text-black hover:bg-slate-200 border border-transparent hover:border-slate-300 transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
