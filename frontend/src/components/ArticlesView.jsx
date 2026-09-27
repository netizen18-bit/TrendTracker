import React, { useState, useEffect } from 'react';
import { Newspaper, Search, Filter, Clock, ExternalLink, ShieldCheck, AlertTriangle, Eye, ArrowUpDown } from 'lucide-react';
import { api } from '../services/api';
import ArticleModal from './ArticleModal';

export default function ArticlesView({ competitors, refreshTrigger }) {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState(null);
  
  // Filters
  const [search, setSearch] = useState('');
  const [selectedCompetitor, setSelectedCompetitor] = useState('');
  const [selectedMethod, setSelectedMethod] = useState('');
  const [selectedSla, setSelectedSla] = useState('');

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const data = await api.getArticles({
        competitor_id: selectedCompetitor || undefined,
        detection_method: selectedMethod || undefined,
        sla_filter: selectedSla || undefined,
        search: search || undefined,
        limit: 100
      });
      setArticles(data.articles || []);
    } catch (err) {
      console.error('Failed to load articles:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, [selectedCompetitor, selectedMethod, selectedSla, refreshTrigger]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchArticles();
  };

  return (
    <div className="space-y-4">
      {/* Header & Filter Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Newspaper className="h-4 w-4 text-black" />
            Detected Competitor Articles ({articles.length})
          </h2>
          <p className="text-xs text-slate-400">
            Real-time feed with verified publication timestamps and exact detection delays
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search Form */}
          <form onSubmit={handleSearchSubmit} className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search articles..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8 pr-3 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 placeholder-slate-500 focus:outline-none focus:border-slate-300 w-44"
            />
          </form>

          {/* Competitor Select */}
          <select
            value={selectedCompetitor}
            onChange={(e) => setSelectedCompetitor(e.target.value)}
            className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-slate-300"
          >
            <option value="">All Competitors</option>
            {competitors.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>

          {/* Method Select */}
          <select
            value={selectedMethod}
            onChange={(e) => setSelectedMethod(e.target.value)}
            className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-slate-300"
          >
            <option value="">All Methods</option>
            <option value="RSS">RSS / Atom</option>
            <option value="SITEMAP">XML Sitemap</option>
            <option value="DIRECT_PAGE">Direct Blog Page</option>
          </select>

          {/* SLA Filter */}
          <select
            value={selectedSla}
            onChange={(e) => setSelectedSla(e.target.value)}
            className="px-2.5 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-slate-300 font-medium"
          >
            <option value="">All SLA Statuses</option>
            <option value="within_5min">Within 5m Target (Fast)</option>
            <option value="over_5min">Over 5m Target</option>
          </select>
        </div>
      </div>

      {/* Articles Table */}
      <div className="glass-panel rounded-2xl border border-slate-200/80 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-white/80 border-b border-slate-200 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="px-5 py-3.5">Article Title & Source</th>
                <th className="px-4 py-3.5">Published Time</th>
                <th className="px-4 py-3.5">Detected Time</th>
                <th className="px-4 py-3.5 text-center">Detection Delay</th>
                <th className="px-4 py-3.5 text-center">Method</th>
                <th className="px-4 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/60">
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-12 text-slate-400">
                    Loading detected articles feed...
                  </td>
                </tr>
              ) : articles.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-12 text-slate-400">
                    No articles detected matching your current filters.
                  </td>
                </tr>
              ) : (
                articles.map((art) => (
                  <tr
                    key={art.id}
                    className="hover:bg-slate-50/40 transition-colors group cursor-pointer"
                    onClick={() => setSelectedArticle(art)}
                  >
                    {/* Title & Competitor */}
                    <td className="px-5 py-4 max-w-md">
                      <div className="flex items-center gap-1.5 text-[11px] font-bold text-black mb-0.5 uppercase tracking-wider">
                        {art.competitor_name}
                      </div>
                      <div className="font-semibold text-slate-800 group-hover:text-black transition-colors line-clamp-2">
                        {art.title}
                      </div>
                      {art.author && (
                        <div className="text-[11px] text-slate-400 mt-1">
                          By {art.author}
                        </div>
                      )}
                    </td>

                    {/* Published Time */}
                    <td className="px-4 py-4 whitespace-nowrap font-mono text-slate-400">
                      {art.published_at ? (
                        <>
                          <div className="text-slate-300 font-medium">{new Date(art.published_at).toLocaleDateString()}</div>
                          <div className="text-[11px] text-slate-400">{new Date(art.published_at).toLocaleTimeString()}</div>
                        </>
                      ) : (
                        <span className="text-slate-300">Unspecified</span>
                      )}
                    </td>

                    {/* Detected Time */}
                    <td className="px-4 py-4 whitespace-nowrap font-mono text-slate-400">
                      <div className="text-slate-300 font-medium">{new Date(art.detected_at).toLocaleDateString()}</div>
                      <div className="text-[11px] text-slate-400">{new Date(art.detected_at).toLocaleTimeString()}</div>
                    </td>

                    {/* Detection Delay */}
                    <td className="px-4 py-4 text-center whitespace-nowrap">
                      <div className={`inline-flex flex-col items-center px-3 py-1 rounded-xl border ${
                        art.is_within_sla
                           ? 'bg-slate-50 border-slate-300 text-black' : 'bg-slate-50 border-slate-300 text-slate-600'
                      }`}>
                        <span className="font-mono font-extrabold text-sm leading-tight">
                          {art.detection_delay_formatted || '0s'}
                        </span>
                        <span className="text-[9px] uppercase font-bold tracking-wider opacity-80 flex items-center gap-0.5">
                          {art.is_within_sla ? <ShieldCheck className="h-2.5 w-2.5" /> : <AlertTriangle className="h-2.5 w-2.5" />}
                          {art.is_within_sla  ? '< 5m SLA' : '> 5m SLA'}
                        </span>
                      </div>
                    </td>

                    {/* Method */}
                    <td className="px-4 py-4 text-center whitespace-nowrap">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                        art.detection_method === 'RSS'
                          ? 'bg-black text-white border border-black'
                          : art.detection_method === 'SITEMAP'
                           ? 'bg-black text-white border border-black' : 'bg-slate-200 text-black border border-slate-300'
                      }`}>
                        {art.detection_method}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="px-4 py-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => setSelectedArticle(art)}
                          className="p-1.5 rounded-lg text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
                          title="View Extracted Content"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                        <a
                          href={art.url}
                          target="_blank"
                          rel="noreferrer"
                          className="p-1.5 rounded-lg text-slate-400 hover:text-black hover:bg-slate-100 transition-colors"
                          title="Open Original URL"
                        >
                          <ExternalLink className="h-4 w-4" />
                        </a>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Inspector Modal */}
      {selectedArticle && (
        <ArticleModal
          article={selectedArticle}
          onClose={() => setSelectedArticle(null)}
        />
      )}
    </div>
  );
}
