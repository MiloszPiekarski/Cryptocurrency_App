import React from 'react';
import { Activity, TrendingUp, TrendingDown, DollarSign, BarChart2, WifiOff } from 'lucide-react';

interface LiveTickerProps {
    data: any;
    loading: boolean;
}

export const LiveTickerWidget: React.FC<LiveTickerProps> = ({ data, loading }) => {
    // LOADING STATE
    if (loading) {
        return (
            <div className="h-full w-full flex items-center justify-center bg-slate-900/50 rounded-xl border border-slate-800 animate-pulse">
                <div className="text-slate-500 text-xs font-mono">CONNECTING TO DATA FEED...</div>
            </div>
        );
    }

    // OFFLINE STATE - No fallback data allowed
    if (!data || !data.summary_data || typeof data.summary_data.price !== 'number') {
        return (
            <div className="h-full w-full flex flex-col items-center justify-center bg-slate-900/50 rounded-xl border border-rose-500/30">
                <WifiOff size={32} className="text-rose-500 mb-2" />
                <div className="text-rose-400 text-xs font-mono font-bold">FEED OFFLINE</div>
                <div className="text-slate-500 text-[10px] font-mono mt-1">Backend not responding</div>
            </div>
        );
    }

    // REAL DATA ONLY - extracted directly from API response
    // Price comes from: GET /api/v1/hive/swarm/BTC/USDT → response.summary_data.price
    const price = data.summary_data.price;  // LINE 31 - REAL API DATA
    const high = data.summary_data.high;
    const low = data.summary_data.low;
    const volume = data.summary_data.volume;
    const change = data.summary_data.change_24h;
    const isPositive = change >= 0;

    return (
        <div className="h-full flex flex-col justify-between p-4 bg-slate-900/50 rounded-xl border border-slate-700/50 relative overflow-hidden">
            {/* Background Element */}
            <div className="absolute -right-4 -bottom-4 opacity-5">
                <Activity size={100} />
            </div>

            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded bg-blue-500/10 text-blue-400">
                        <DollarSign size={16} />
                    </div>
                    <span className="text-xs font-bold text-slate-400 font-mono tracking-wider">LIVE TICKER</span>
                </div>
                <div className={`flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded ${isPositive ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                    {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {change > 0 ? '+' : ''}{change.toFixed(2)}%
                </div>
            </div>

            <div className="mt-2">
                <div className="text-3xl font-black text-white font-mono tracking-tight">
                    ${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className="flex items-center gap-4 mt-2 text-[10px] text-slate-500 font-mono">
                    <div className="flex items-center gap-1">
                        <span className="text-slate-600">H:</span>
                        <span>{high?.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <span className="text-slate-600">L:</span>
                        <span>{low?.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <BarChart2 size={10} />
                        <span>VOL: {volume?.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
