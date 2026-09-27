import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import StatCards from './components/StatCards';
import PerformanceCharts from './components/PerformanceCharts';
import CompetitorsView from './components/CompetitorsView';
import ArticlesView from './components/ArticlesView';
import DemoPublisherStudio from './components/DemoPublisherStudio';
import BenchmarkStudio from './components/BenchmarkStudio';
import CompetitorModal from './components/CompetitorModal';
import ArticleModal from './components/ArticleModal';
import LiveEventTicker from './components/LiveEventTicker';
import { api } from './services/api';
import { ShieldCheck, ArrowRight, Activity, Clock, Layers, Sparkles, ExternalLink, RefreshCw } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [competitors, setCompetitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isCheckingAll, setIsCheckingAll] = useState(false);
  
  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [inspectArticle, setInspectArticle] = useState(null);

  // Live WebSocket stream
  const [wsConnected, setWsConnected] = useState(false);
  const [liveEvents, setLiveEvents] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  // Fetch Core Data
  const fetchData = async () => {
    try {
      const [statsData, compsData] = await Promise.all([
        api.getDashboardStats(),
        api.getCompetitors()
      ]);
      setStats(statsData);
      setCompetitors(compsData);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Background polling interval every 15s to keep stats perfectly fresh
    const interval = setInterval(() => {
      fetchData();
    }, 15000);
    return () => clearInterval(interval);
  }, [refreshKey]);

  // WebSocket Connection
  useEffect(() => {
    let ws;
    const protocol = window.location.protocol === 'https:'  ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/live`;

    const connectWs = () => {
      try {
        ws = new WebSocket(wsUrl);
        ws.onopen = () => {
          setWsConnected(true);
        };
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setLiveEvents((prev) => [data, ...prev.slice(0, 9)]);
            if (data.event === 'NEW_ARTICLE_DETECTED') {
              fetchData();
              setRefreshKey((k) => k + 1);
            }
          } catch (e) {
            console.error('Error parsing WebSocket message:', e);
          }
        };
        ws.onclose = () => {
          setWsConnected(false);
          // Retry connect after 3s
          setTimeout(connectWs, 3000);
        };
        ws.onerror = () => {
          setWsConnected(false);
        };
      } catch (e) {
        console.error('WebSocket connection failed:', e);
      }
    };

    connectWs();
    return () => {
      if (ws) ws.close();
    };
  }, []);

  const handleGlobalCheck = async () => {
    setIsCheckingAll(true);
    try {
      await api.checkAllCompetitors();
      await fetchData();
      setRefreshKey((k) => k + 1);
    } catch (err) {
      console.error('Global check failed:', err);
    } finally {
      setIsCheckingAll(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-white flex flex-col selection:bg-black selection:text-white">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onAddCompetitor={() => setIsAddModalOpen(true)}
        onGlobalCheck={handleGlobalCheck}
        isCheckingAll={isCheckingAll}
        wsConnected={wsConnected}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Live Notification Ticker */}
        <LiveEventTicker
          events={liveEvents}
          onArticleClick={(art) => setInspectArticle(art)}
        />

        {/* Tab 1: Executive Dashboard */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* KPI Cards */}
            <StatCards stats={stats} />

            {/* Performance Charts */}
            <PerformanceCharts stats={stats} />

            {/* Bottom 2 Grid: Recent Detected Articles & Active Targets Snapshot */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Articles */}
              <div className="lg:col-span-2 glass-panel rounded-2xl p-5 border border-slate-200/80">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                      <Clock className="h-4 w-4 text-black" />
                      Latest Detected Articles
                    </h3>
                    <p className="text-xs text-slate-400">Live feed with calculated detection delays</p>
                  </div>
                  <button
                    onClick={() => setActiveTab('articles')}
                    className="text-xs font-semibold text-black hover:text-black flex items-center gap-1"
                  >
                    <span>View All</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                </div>

                <div className="space-y-2.5">
                  {stats?.recent_articles && stats.recent_articles.length > 0 ? (
                    stats.recent_articles.map((art) => (
                      <div
                        key={art.id}
                        onClick={() => setInspectArticle(art)}
                        className="p-3 rounded-xl bg-white/60 hover:bg-slate-50 border border-slate-200/80 hover:border-slate-300 transition-all flex items-center justify-between gap-3 cursor-pointer group"
                      >
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 text-[10px] font-bold uppercase text-black mb-0.5">
                            <span>{art.competitor_name}</span>
                            <span className="text-slate-300">•</span>
                            <span className="text-slate-400">{art.detection_method}</span>
                          </div>
                          <div className="text-xs font-semibold text-slate-900 group-hover:text-black transition-colors truncate">
                            {art.title}
                          </div>
                        </div>

                        <div className="flex items-center gap-3 flex-shrink-0">
                          <div className={`text-right px-2.5 py-1 rounded-lg border text-xs ${
                            art.is_within_sla
                               ? 'bg-slate-50 border-slate-300 text-black' : 'bg-slate-50 border-slate-300 text-slate-600'
                          }`}>
                            <div className="font-mono font-bold">{art.detection_delay_formatted || '0s'}</div>
                            <div className="text-[9px] uppercase font-semibold opacity-75">
                              {art.is_within_sla  ? '<5m SLA' : '>5m SLA'}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-slate-400 text-xs">
                      No articles detected yet. Click "Trigger Scan" or add a competitor target.
                    </div>
                  )}
                </div>
              </div>

              {/* Active Monitoring Sources */}
              <div className="glass-panel rounded-2xl p-5 border border-slate-200/80 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                        <Layers className="h-4 w-4 text-black" />
                        Monitored Targets
                      </h3>
                      <p className="text-xs text-slate-400">Status & Health</p>
                    </div>
                    <button
                      onClick={() => setActiveTab('competitors')}
                      className="text-xs font-semibold text-black hover:text-black"
                    >
                      Manage
                    </button>
                  </div>

                  <div className="space-y-2.5">
                    {competitors.slice(0, 5).map((c) => (
                      <div key={c.id} className="p-2.5 rounded-xl bg-white/60 border border-slate-200 flex items-center justify-between">
                        <div>
                          <div className="text-xs font-bold text-slate-900">{c.name}</div>
                          <div className="text-[10px] text-slate-400 font-mono truncate max-w-[150px]">
                            {c.website_url.replace('https://', '').replace('http://', '')}
                          </div>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <span className={`h-2 w-2 rounded-full ${c.monitoring_enabled  ? 'bg-black animate-pulse' : 'bg-slate-600'}`} />
                          <span className="text-[11px] font-mono text-slate-300 font-semibold">{c.articles_count} arts</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200 text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Continuous Engine Polling</span>
                  <span className="font-mono text-black font-semibold">Interval: 60s</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Competitors */}
        {activeTab === 'competitors' && (
          <CompetitorsView
            competitors={competitors}
            onRefresh={fetchData}
            onAddClick={() => setIsAddModalOpen(true)}
          />
        )}

        {/* Tab 3: Detected Articles */}
        {activeTab === 'articles' && (
          <ArticlesView
            competitors={competitors}
            refreshTrigger={refreshKey}
          />
        )}

        {/* Tab 4: Interactive Demo Publisher */}
        {activeTab === 'demo' && (
          <DemoPublisherStudio
            onArticleDetected={() => {
              fetchData();
              setRefreshKey((k) => k + 1);
            }}
          />
        )}

        {/* Tab 5: 100-Website Scale Benchmark */}
        {activeTab === 'benchmark' && (
          <BenchmarkStudio />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200/80 py-4 text-center text-xs text-slate-400 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span><strong>TrendTracker</strong> — Competitor Blog Spy & Real-Time Content Monitoring System</span>
          <span className="text-[11px] text-slate-400">Detection Intelligence • Timing SLA • Non-Blocking Concurrency</span>
        </div>
      </footer>

      {/* Add Competitor Modal */}
      <CompetitorModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onCreated={() => {
          fetchData();
          setRefreshKey((k) => k + 1);
        }}
      />

      {/* Article Detail Inspector Modal */}
      {inspectArticle && (
        <ArticleModal
          article={inspectArticle}
          onClose={() => setInspectArticle(null)}
        />
      )}
    </div>
  );
}
