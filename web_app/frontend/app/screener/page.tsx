'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { ScreenerTable } from '@/components/screener/ScreenerTable';
import { Search, Activity, Zap, TrendingUp } from 'lucide-react';

export default function ScreenerPage() {
    const [data, setData] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const isMounted = useRef(true);

    const fetchData = async (showLoading = false) => {
        if (!isMounted.current) return;

        if (showLoading) setIsLoading(true);

        try {
            // Note: In production this would be an env var
            const res = await fetch('http://localhost:8001/api/v1/market/screener');
            if (res.ok) {
                const json = await res.json();
                if (isMounted.current) {
                    setData(json);
                    setLastUpdated(new Date());
                }
            } else {
                console.error("Failed to fetch screener data");
            }
        } catch (error) {
            console.error(error);
        } finally {
            if (isMounted.current) {
                setIsLoading(false);
            }
        }
    };

    useEffect(() => {
        isMounted.current = true;

        const loop = async () => {
            await fetchData(true); // Initial load

            while (isMounted.current) {
                await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s (Live feel)
                if (!isMounted.current) break;
                await fetchData(false); // Background refresh
            }
        };

        loop();

        return () => {
            isMounted.current = false;
        };
    }, []);

    return (
        <div className="min-h-screen bg-[#050914] text-white p-4 md:p-8 font-sans selection:bg-cyan-500/30">

            {/* Header Area */}
            <div className="max-w-[1600px] mx-auto mb-8 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
                <div>
                    <Link href="/nexus" className="text-[10px] text-gray-500 hover:text-cyan-400 tracking-widest mb-1 block transition-colors">
                        &larr; TERMINAL NEXUS
                    </Link>
                    <h1 className="text-4xl md:text-5xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500">
                        MARKET SCREENER
                    </h1>
                    <div className="flex items-center gap-2 mt-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        <p className="text-xs text-gray-400 font-mono">
                            LIVE FEED // CONNECTION STABLE
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    {/* Controls Removed as per user request */}
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-[1600px] mx-auto">
                <div className="bg-[#0a0f1e] border border-gray-800 rounded-2xl overflow-hidden shadow-2xl shadow-black/50">
                    <div className="p-1 bg-gradient-to-r from-gray-800 to-gray-900 border-b border-gray-800 flex justify-between px-4 py-2">
                        <span className="text-[10px] uppercase text-gray-600 font-mono mt-1">
                            Top 20 USDT Pairs (Volume Sort)
                        </span>
                        <span className="text-[10px] uppercase text-gray-600 font-mono mt-1">
                            Last Upd: {lastUpdated ? lastUpdated.toLocaleTimeString() : '--:--:--'}
                        </span>
                    </div>

                    <ScreenerTable data={data} isLoading={isLoading} />
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6 opacity-60 hover:opacity-100 transition-opacity">
                    <div className="p-4 rounded-xl border border-dashed border-gray-800 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-emerald-900/20 flex items-center justify-center text-emerald-400">
                            <Activity size={20} />
                        </div>
                        <div>
                            <div className="text-xs text-gray-400">MARKET SENTIMENT</div>
                            <div className="font-bold text-emerald-400">GREED (74)</div>
                        </div>
                    </div>
                    <div className="p-4 rounded-xl border border-dashed border-gray-800 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-purple-900/20 flex items-center justify-center text-purple-400">
                            <Zap size={20} />
                        </div>
                        <div>
                            <div className="text-xs text-gray-400">AI SIGNAL STRENGTH</div>
                            <div className="font-bold text-purple-400">HIGH CONFIDENCE</div>
                        </div>
                    </div>
                    <div className="p-4 rounded-xl border border-dashed border-gray-800 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-blue-900/20 flex items-center justify-center text-blue-400">
                            <TrendingUp size={20} />
                        </div>
                        <div>
                            <div className="text-xs text-gray-400">24H VOLUME</div>
                            <div className="font-bold text-blue-400">$48.2B</div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    );
}
