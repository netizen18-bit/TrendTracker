import React from 'react';
import { Bell, Zap, Clock, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function LiveEventTicker({ events, onArticleClick }) {
  if (!events || events.length === 0) return null;

  return (
    <div className="mb-6 space-y-2">
      <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
        <Bell className="h-3.5 w-3.5 text-black animate-bounce" />
        <span>Live Real-Time Event Stream</span>
      </div>

      <div className="flex flex-col gap-2">
        {events.slice(0, 3).map((evt, idx) => {
          if (evt.event === 'NEW_ARTICLE_DETECTED') {
            const art = evt.data;
            const isFast = art.detection_delay_seconds !== null && art.detection_delay_seconds <= 300;
            return (
              <div
                key={idx}
                onClick={() => onArticleClick && onArticleClick(art)}
                className="glass-panel rounded-xl p-3 border border-slate-300 flex items-center justify-between gap-4 cursor-pointer hover:bg-slate-50/80 transition-all shadow-lg shadow-black/10 animate-in slide-in-from-top duration-300"
              >
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg bg-black/10 border border-slate-300 flex items-center justify-center text-black flex-shrink-0">
                    <Zap className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase text-black">{art.competitor_name}</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.2 rounded bg-slate-100 text-slate-300">{art.detection_method}</span>
                    </div>
                    <div className="text-xs font-semibold text-slate-900 line-clamp-1">{art.title}</div>
                  </div>
                </div>

                <div className="flex items-center gap-3 flex-shrink-0">
                  <div className="text-right">
                    <div className="text-[10px] text-slate-400 font-medium">Detection Delay</div>
                    <div className={`font-mono text-xs font-bold ${isFast  ? 'text-black' : 'text-slate-600'}`}>
                      {art.detection_delay_formatted || '0s'}
                    </div>
                  </div>
                  <div className={`p-1.5 rounded-lg text-xs ${isFast  ? 'bg-slate-200 text-black' : 'bg-slate-200 text-slate-600'}`}>
                    {isFast ? <ShieldCheck className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                  </div>
                </div>
              </div>
            );
          }
          return null;
        })}
      </div>
    </div>
  );
}
