import React, { useState } from 'react';
import { PlaySquare, Send, Sparkles, Clock, Globe, Radio, Compass, RefreshCw, CheckCircle2, AlertCircle, ArrowUpRight } from 'lucide-react';
import { api } from '../services/api';

const PRESET_ARTICLES = [
  {
    title: "Breakthrough: Sub-Second Vector Search Engine Released for Production Clouds",
    category: "Cloud Architecture",
    author: "Elena Rostova, Principal Architect",
    minutes_ago: 2,
    content: "Today we are open-sourcing our next-generation vector retrieval engine. By leveraging SIMD vectorization and lock-free in-memory index structures, latency drops from 45ms to under 800 microseconds at 100M vector scale."
  },
  {
    title: "Critical Security Advisory: Zero-Day Memory Isolation Patch Deployed",
    category: "Security & Reliability",
    author: "Marcus Vance, CISO",
    minutes_ago: 8,
    content: "Our automated telemetry detected an edge-case memory isolation anomaly in hypervisor ring 0. A hotpatch was verified and rolled out across 14 global regions within 18 minutes. No customer data was exposed."
  },
  {
    title: "Autonomous Agent Orchestration: Designing Fault-Tolerant Feedback Loops",
    category: "Artificial Intelligence",
    author: "Dr. Maya Vance",
    minutes_ago: 0,
    content: "Managing fleets of autonomous coding agents requires robust error boundaries, structured scratchpad persistence, and proactive health checks. This deep-dive explores multi-agent scheduling patterns."
  }
];

export default function DemoPublisherStudio({ onArticleDetected }) {
  const [title, setTitle] = useState(PRESET_ARTICLES[0].title);
  const [content, setContent] = useState(PRESET_ARTICLES[0].content);
  const [author, setAuthor] = useState(PRESET_ARTICLES[0].author);
  const [category, setCategory] = useState(PRESET_ARTICLES[0].category);
  const [minutesAgo, setMinutesAgo] = useState(2);
  
  const [isPublishing, setIsPublishing] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [error, setError] = useState(null);

  const applyPreset = (preset) => {
    setTitle(preset.title);
    setContent(preset.content);
    setAuthor(preset.author);
    setCategory(preset.category);
    setMinutesAgo(preset.minutes_ago);
    setLastResult(null);
  };

  const handlePublishAndScan = async (e) => {
    e.preventDefault();
    setIsPublishing(true);
    setError(null);
    setLastResult(null);

    try {
      // 1. Publish to controlled demo blog
      const publishRes = await api.publishDemoArticle({
        title,
        content,
        author,
        category,
        minutes_ago: minutesAgo
      });

      // 2. Trigger instant monitoring scan across all sources
      const scanRes = await api.checkAllCompetitors();

      setLastResult({
        published: publishRes,
        scan: scanRes
      });

      if (onArticleDetected) onArticleDetected();
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to publish and monitor article.');
    } finally {
      setIsPublishing(false);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset the demo blog to default seed articles?')) return;
    setIsResetting(true);
    try {
      await api.resetDemoBlog();
      await api.checkAllCompetitors();
      setLastResult(null);
      if (onArticleDetected) onArticleDetected();
    } catch (err) {
      alert('Reset failed: ' + err.message);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel-glow rounded-2xl p-6 relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full bg-slate-200 text-black border border-slate-300 text-[10px] font-bold uppercase tracking-wider">
                Controlled Testbed Environment
              </span>
            </div>
            <h2 className="text-xl font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
              <PlaySquare className="h-5 w-5 text-black" />
              Interactive Publisher & Detection Delay Testbed
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-2xl">
              Simulate competitor publishing in real-time. Publish an article with customized publication timestamps (e.g. 0s, 3m, 10m ago), trigger continuous monitoring, and verify the exact Detection Delay calculation live!
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <a
              href="/demo/blog"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white hover:bg-slate-100 border border-slate-300 text-xs font-semibold text-black"
            >
              <span>View /demo/blog</span>
              <ArrowUpRight className="h-3.5 w-3.5 text-black" />
            </a>
            <a
              href="/demo/rss.xml"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-black hover:bg-slate-800 border border-black text-xs font-semibold text-white"
            >
              <span>/demo/rss.xml</span>
              <Radio className="h-3.5 w-3.5 text-black" />
            </a>
            <button
              onClick={handleReset}
              disabled={isResetting}
              className="px-3 py-1.5 rounded-xl bg-white hover:bg-slate-100 border border-slate-300 text-xs font-semibold text-slate-400 hover:text-black"
            >
              {isResetting  ? 'Resetting...' : 'Reset Seeds'}
            </button>
          </div>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Form & Presets */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-slate-200/80 space-y-5">
          {/* Quick Presets */}
          <div>
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Quick Test Presets:
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              {PRESET_ARTICLES.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => applyPreset(p)}
                  className={`p-3 rounded-xl text-left border transition-all text-xs ${
                    title === p.title
                       ? 'bg-slate-200 border-slate-300 text-slate-900 shadow-md' : 'bg-white/60 border-slate-200 hover:border-slate-300 text-slate-300'
                  }`}
                >
                  <div className="text-[10px] font-bold text-black uppercase mb-1">{p.category}</div>
                  <div className="font-semibold line-clamp-2">{p.title}</div>
                  <div className="text-[10px] text-slate-400 mt-2">Simulate {p.minutes_ago}m ago</div>
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handlePublishAndScan} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Article Headline</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full px-3.5 py-2 bg-white/90 border border-slate-300 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-slate-300 font-medium"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Author</label>
                <input
                  type="text"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="w-full px-3.5 py-2 bg-white/90 border border-slate-300 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-slate-300"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3.5 py-2 bg-white/90 border border-slate-300 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-slate-300"
                />
              </div>
            </div>

            {/* Timing Simulator Slider */}
            <div className="p-4 rounded-xl bg-white/80 border border-slate-200 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-900 flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5 text-black" />
                  Simulate Publication Timestamp
                </span>
                <span className="font-mono font-bold text-black px-2 py-0.5 rounded bg-slate-200 border border-slate-300">
                  {minutesAgo === 0 ? 'Published Right Now (0m)' : `Published ${minutesAgo} minute(s) ago`}
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={15}
                step={1}
                value={minutesAgo}
                onChange={(e) => setMinutesAgo(Number(e.target.value))}
                className="w-full accent-black cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>0m (Instant target)</span>
                <span>3m (Normal SLA)</span>
                <span>5m (SLA Boundary)</span>
                <span>15m (Over SLA Test)</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Article Body Content</label>
              <textarea
                rows={4}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                required
                className="w-full px-3.5 py-2 bg-white/90 border border-slate-300 rounded-xl text-xs text-slate-900 focus:outline-none focus:border-slate-300"
              />
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-slate-200 border border-slate-300 text-black text-xs">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isPublishing}
              className="w-full py-3 rounded-xl text-xs font-bold bg-black hover:bg-slate-800 text-white shadow-xl shadow-black/10 transition-all flex items-center justify-center gap-2"
            >
              {isPublishing ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Publishing & Triggering Instant Detection Scan...</span>
                </>
              ) : (
                <>
                  <Send className="h-4 w-4" />
                  <span>Publish to Demo Blog & Trigger Live Detection Scan</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Col: Live Live Detection Proof & Flow */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-200/80 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2 mb-3">
              <Sparkles className="h-4 w-4 text-black" />
              Live Detection Flow Proof
            </h3>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-white/70 border border-slate-200 space-y-1.5">
                <div className="text-[10px] font-bold text-slate-400 uppercase">1. Publication Event</div>
                <p className="text-slate-300">
                  Article is injected into <code className="text-black">/demo/blog</code>, <code className="text-black">/demo/rss.xml</code>, and <code className="text-black">/demo/sitemap.xml</code> with UTC timestamp.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-white/70 border border-slate-200 space-y-1.5">
                <div className="text-[10px] font-bold text-slate-400 uppercase">2. Monitoring Cycle</div>
                <p className="text-slate-300">
                  Async workers query feed & sitemap, diff discovered canonical URLs, and detect new candidate article.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-white/70 border border-slate-200 space-y-1.5">
                <div className="text-[10px] font-bold text-slate-400 uppercase">3. Timing & Delay Calculation</div>
                <div className="font-mono text-[11px] text-black bg-slate-50 p-2 rounded-lg border border-slate-200">
                  Delay = Detected(UTC) - Published(UTC)
                </div>
              </div>
            </div>
          </div>

          {/* Last Result Showcase */}
          {lastResult && (
            <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-300 animate-in fade-in">
              <div className="flex items-center gap-1.5 text-xs font-bold text-black mb-2">
                <CheckCircle2 className="h-4 w-4" />
                <span>Detection Event Succeeded!</span>
              </div>
              <div className="space-y-1 text-[11px] font-mono text-slate-300">
                <div>Published: {new Date(lastResult.published.published_at).toLocaleTimeString()}</div>
                <div>Simulated Offset: {lastResult.published.minutes_ago}m ago</div>
                <div>New Articles Found: +{lastResult.scan.newly_detected}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
