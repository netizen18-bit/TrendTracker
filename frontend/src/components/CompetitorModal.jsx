import React, { useState } from 'react';
import { X, Search, Sparkles, CheckCircle2, XCircle, Globe, Radio, Compass, FileCode2, ArrowRight, Loader2 } from 'lucide-react';
import { api } from '../services/api';

export default function CompetitorModal({ isOpen, onClose, onCreated }) {
  const [name, setName] = useState('');
  const [url, setUrl] = useState('');
  const [interval, setInterval] = useState(60);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleInspect = async () => {
    if (!url || url.length < 4) {
      setError('Please enter a valid website URL');
      return;
    }
    setError(null);
    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      const data = await api.inspectWebsite(url);
      setAnalysisResult(data);
      if (!name) {
        // Auto derive name from URL domain
        try {
          const parsed = new URL(data.target_url);
          const domainName = parsed.hostname.replace('www.', '').split('.')[0];
          setName(domainName.charAt(0).toUpperCase() + domainName.slice(1) + ' Blog');
        } catch {
          setName('New Competitor');
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to inspect website. Check URL and connectivity.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!name || !url) {
      setError('Name and Website URL are required');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await api.createCompetitor({
        name,
        website_url: url,
        check_interval_sec: interval,
        auto_investigate: !analysisResult // If already analyzed, backend uses URL, otherwise probes
      });
      onCreated();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save competitor.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-50/80 backdrop-blur-md">
      <div className="glass-panel rounded-2xl w-full max-w-2xl border border-slate-300/80 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white/50">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-black/10 flex items-center justify-center text-black">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900">Add Competitor with AI Analysis</h2>
              <p className="text-xs text-slate-400">Autonomous investigation of feeds, sitemaps, and article structure</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-5">
          {error && (
            <div className="p-3 rounded-xl bg-slate-200 border border-slate-300 text-black text-xs flex items-center gap-2">
              <XCircle className="h-4 w-4 text-black flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* URL Input with Inspect Button */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">
              Website or Blog URL to Monitor
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Globe className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="e.g. techcrunch.com, aws.amazon.com/blogs, or http://127.0.0.1:8000/demo/blog"
                  className="w-full pl-9 pr-3 py-2 bg-white/80 border border-slate-300 rounded-xl text-xs text-slate-900 placeholder-slate-500 focus:outline-none focus:border-slate-300 font-mono"
                />
              </div>
              <button
                type="button"
                onClick={handleInspect}
                disabled={isAnalyzing || !url}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-black hover:bg-slate-800 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-black/10"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Search className="h-4 w-4" />
                    <span>Analyze</span>
                  </>
                )}
              </button>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              The analyzer will investigate RSS feeds, XML sitemaps, robots.txt, and HTML article markup.
            </p>
          </div>

          {/* Autonomous Analysis Results Matrix */}
          {analysisResult && (
            <div className="rounded-xl bg-white/90 border border-slate-300 p-4 space-y-4 animate-in fade-in duration-300">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <span className="text-xs font-bold text-slate-900 flex items-center gap-1.5">
                  <Sparkles className="h-3.5 w-3.5 text-black" />
                  Investigation Findings ({analysisResult.analysis_duration_ms}ms)
                </span>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded-md bg-slate-200 text-black border border-slate-300 font-semibold">
                  Selected Strategy: {analysisResult.selected_strategy}
                </span>
              </div>

              {/* 3 Methods Grid */}
              <div className="grid grid-cols-3 gap-3">
                {/* Method 1: RSS */}
                <div className={`p-3 rounded-lg border text-xs ${
                  analysisResult.strategies_available.rss
                     ? 'bg-black border-black text-white' : 'bg-slate-50/40 border-slate-200 text-slate-400'
                }`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold flex items-center gap-1 text-[11px]">
                      <Radio className="h-3 w-3 text-black" />
                      RSS / Atom Feed
                    </span>
                    {analysisResult.strategies_available.rss ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-black" />
                    ) : (
                      <XCircle className="h-3.5 w-3.5 text-slate-300" />
                    )}
                  </div>
                  <div className="text-[10px] truncate text-slate-400">
                    {analysisResult.feed_details?.feed_url || 'None detected'}
                  </div>
                </div>

                {/* Method 2: Sitemap */}
                <div className={`p-3 rounded-lg border text-xs ${
                  analysisResult.strategies_available.sitemap
                     ? 'bg-black border-black text-white' : 'bg-slate-50/40 border-slate-200 text-slate-400'
                }`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold flex items-center gap-1 text-[11px]">
                      <Compass className="h-3 w-3 text-black" />
                      XML Sitemap
                    </span>
                    {analysisResult.strategies_available.sitemap ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-black" />
                    ) : (
                      <XCircle className="h-3.5 w-3.5 text-slate-300" />
                    )}
                  </div>
                  <div className="text-[10px] truncate text-slate-400">
                    {analysisResult.sitemap_details?.sitemap_url || 'None detected'}
                  </div>
                </div>

                {/* Method 3: Direct Page */}
                <div className={`p-3 rounded-lg border text-xs ${
                  analysisResult.strategies_available.direct_page
                     ? 'bg-slate-200 border-slate-300 text-black' : 'bg-slate-50/40 border-slate-200 text-slate-400'
                }`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold flex items-center gap-1 text-[11px]">
                      <FileCode2 className="h-3 w-3 text-black" />
                      Direct Blog Page
                    </span>
                    {analysisResult.strategies_available.direct_page ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-black" />
                    ) : (
                      <XCircle className="h-3.5 w-3.5 text-slate-300" />
                    )}
                  </div>
                  <div className="text-[10px] truncate text-slate-400">
                    {analysisResult.blog_details?.blog_url || 'Root Page'}
                  </div>
                </div>
              </div>

              {/* Metadata support signals */}
              <div className="p-2.5 rounded-lg bg-slate-50/60 border border-slate-200 flex items-center justify-between text-[11px]">
                <span className="text-slate-400">Publication Metadata Signals:</span>
                <div className="flex gap-2 text-slate-300">
                  <span className={`px-1.5 py-0.5 rounded ${analysisResult.publication_metadata_support?.json_ld  ? 'text-black bg-slate-50' : 'text-slate-300'}`}>JSON-LD</span>
                  <span className={`px-1.5 py-0.5 rounded ${analysisResult.publication_metadata_support?.opengraph  ? 'text-black bg-slate-50' : 'text-slate-300'}`}>OpenGraph</span>
                  <span className={`px-1.5 py-0.5 rounded ${analysisResult.publication_metadata_support?.time_tags  ? 'text-black bg-slate-50' : 'text-slate-300'}`}>&lt;time&gt; tags</span>
                </div>
              </div>
            </div>
          )}

          {/* Competitor Name & Check Interval */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Competitor Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. AWS Blog"
                className="w-full px-3 py-2 bg-white/80 border border-slate-300 rounded-xl text-xs text-slate-900 placeholder-slate-500 focus:outline-none focus:border-slate-300"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                Monitoring Check Interval
              </label>
              <select
                value={interval}
                onChange={(e) => setInterval(Number(e.target.value))}
                className="w-full px-3 py-2 bg-white/80 border border-slate-300 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-slate-300"
              >
                <option value={30}>Every 30 seconds (High Frequency)</option>
                <option value={60}>Every 1 minute (Standard)</option>
                <option value={120}>Every 2 minutes</option>
                <option value={300}>Every 5 minutes</option>
              </select>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-4 border-t border-slate-200 bg-white/50 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleCreate}
            disabled={isSubmitting || !name || !url}
            className="flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-bold bg-black hover:bg-slate-800 text-white shadow-lg shadow-black/10 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Saving Competitor...</span>
              </>
            ) : (
              <>
                <span>Save & Start Monitoring</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
