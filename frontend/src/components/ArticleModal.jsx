import React, { useState } from 'react';
import { X, ExternalLink, Calendar, Clock, User, Tag, Layers, CheckCircle2, AlertTriangle, Image as ImageIcon, Link2 } from 'lucide-react';

export default function ArticleModal({ article, onClose }) {
  const [activeTab, setActiveTab] = useState('content');

  if (!article) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-50/80 backdrop-blur-md">
      <div className="glass-panel rounded-2xl w-full max-w-3xl border border-slate-300/80 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-start justify-between px-6 py-4 border-b border-slate-200 bg-white/60">
          <div className="pr-6">
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs font-bold text-black uppercase tracking-wider">
                {article.competitor_name}
              </span>
              <span className="text-slate-300">•</span>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                article.detection_method === 'RSS'
                  ? 'bg-black text-white border border-black'
                  : article.detection_method === 'SITEMAP'
                   ? 'bg-black text-white border border-black' : 'bg-slate-200 text-black border border-slate-300'
              }`}>
                Detected via {article.detection_method}
              </span>
            </div>
            <h2 className="text-lg font-bold text-slate-900 leading-snug">{article.title}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Timing Performance Banner */}
        <div className="px-6 py-3 bg-slate-50 border-b border-slate-200/80 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-4">
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Published</span>
              <span className="font-mono text-slate-300">
                {article.published_at ? new Date(article.published_at).toLocaleString() : 'Unknown'}
              </span>
            </div>
            <div className="h-6 w-px bg-slate-100" />
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Detected</span>
              <span className="font-mono text-slate-300">
                {article.detected_at ? new Date(article.detected_at).toLocaleString() : 'Now'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="text-right">
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Detection Delay</span>
              <span className={`font-mono text-sm font-extrabold ${
                article.is_within_sla  ? 'text-black' : 'text-slate-600'
              }`}>
                {article.detection_delay_formatted || '0s'}
              </span>
            </div>
            <div className={`px-2 py-1 rounded-lg text-[10px] font-bold uppercase flex items-center gap-1 ${
              article.is_within_sla
                 ? 'bg-slate-200 text-black border border-slate-300' : 'bg-slate-200 text-slate-600 border border-slate-300'
            }`}>
              {article.is_within_sla ? <CheckCircle2 className="h-3 w-3" /> : <AlertTriangle className="h-3 w-3" />}
              {article.is_within_sla  ? 'Target Met (<5m)' : 'Over 5m Target'}
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex px-6 border-b border-slate-200 bg-white/30 gap-4 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('content')}
            className={`py-3 border-b-2 transition-colors ${
              activeTab === 'content'  ? 'border-slate-300 text-black' : 'border-transparent text-slate-400 hover:text-black'
            }`}
          >
            Extracted Content
          </button>
          <button
            onClick={() => setActiveTab('metadata')}
            className={`py-3 border-b-2 transition-colors ${
              activeTab === 'metadata'  ? 'border-slate-300 text-black' : 'border-transparent text-slate-400 hover:text-black'
            }`}
          >
            Structured Metadata & Signals
          </button>
        </div>

        {/* Body Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs text-slate-300 flex-1">
          {activeTab === 'content' ? (
            <>
              {/* Featured Image */}
              {article.featured_image && (
                <div className="rounded-xl overflow-hidden border border-slate-200 max-h-64 mb-4">
                  <img
                    src={article.featured_image}
                    alt={article.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              {/* Author and URL */}
              <div className="flex items-center justify-between pb-3 border-b border-slate-200/80 text-slate-400">
                <span className="flex items-center gap-1.5">
                  <User className="h-3.5 w-3.5 text-black" />
                  Author: <strong className="text-black">{article.author || 'Editorial Team'}</strong>
                </span>
                <a
                  href={article.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1 text-black hover:text-black font-mono"
                >
                  <span>Open Source Article</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>

              {/* Body Text */}
              <div className="whitespace-pre-wrap leading-relaxed text-slate-300 font-sans text-sm bg-slate-50/50 p-4 rounded-xl border border-slate-900">
                {article.content || article.meta_description || 'No textual content extracted.'}
              </div>

              {/* Categories & Tags */}
              <div className="flex flex-wrap gap-2 pt-2">
                {article.categories?.map((cat, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded-md bg-slate-200 text-black border border-slate-300 text-[11px] font-semibold flex items-center gap-1">
                    <Layers className="h-3 w-3" />
                    {cat}
                  </span>
                ))}
                {article.tags?.map((tag, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded-md bg-white text-slate-300 border border-slate-200 text-[11px] flex items-center gap-1">
                    <Tag className="h-3 w-3 text-slate-400" />
                    {tag}
                  </span>
                ))}
              </div>
            </>
          ) : (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-white/60 border border-slate-200 font-mono text-[11px] space-y-2">
                <div><span className="text-slate-400">Canonical URL:</span> <span className="text-black">{article.canonical_url}</span></div>
                <div><span className="text-slate-400">Original URL:</span> <span className="text-slate-300">{article.url}</span></div>
                <div><span className="text-slate-400">Detection Method:</span> <span className="text-black font-bold">{article.detection_method}</span></div>
                <div><span className="text-slate-400">Detection Delay (sec):</span> <span className="text-slate-600 font-bold">{article.detection_delay_seconds}s</span></div>
              </div>

              {article.raw_metadata && Object.keys(article.raw_metadata).length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-slate-900 mb-2">Raw OpenGraph & HTML Meta Signals</h4>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-900 font-mono text-[10px] space-y-1 text-slate-400 max-h-48 overflow-y-auto">
                    {Object.entries(article.raw_metadata).map(([k, v]) => (
                      <div key={k} className="flex justify-between border-b border-slate-900/80 py-0.5">
                        <span className="text-black">{k}:</span>
                        <span className="text-slate-300 truncate max-w-xs">{v}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
