/**
 * TURBO-PLAN X - Recent Trades Widget
 * Live feed of market trades
 */

'use client';

import { useEffect, useState } from 'react';
import { api, TradeData } from '@/lib/api';

interface RecentTradesProps {
    symbol: string;
    limit?: number;
}

export function RecentTrades({ symbol, limit = 30 }: RecentTradesProps) {
    const [trades, setTrades] = useState<TradeData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let mounted = true;

        const fetchTrades = async () => {
            try {
                const data = await api.getTrades(symbol, limit);
                if (mounted) {
                    if (data.length > 0) {
                        // Sort by timestamp desc (newest first)
                        const sorted = data.sort((a: TradeData, b: TradeData) => b.timestamp - a.timestamp);
                        setTrades(prev => sorted);
                    }
                    setLoading(false);
                }
            } catch (err) {
                console.error(err);
                if (mounted) setLoading(false);
            }
        };

        fetchTrades();
        const interval = setInterval(fetchTrades, 2000);

        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, [symbol, limit]);

    if (loading) {
        return (
            <div className="w-full h-full bg-[#0f1729] rounded-xl border border-gray-700 p-4">
                <div className="animate-pulse flex flex-col gap-2">
                    <div className="h-4 bg-gray-800 rounded w-1/3"></div>
                    <div className="h-32 bg-gray-800/50 rounded"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full bg-[#0f1729] rounded-xl border border-gray-700 h-full flex flex-col">
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-700 shrink-0">
                <h3 className="text-sm font-semibold text-white">Recent Trades</h3>
            </div>

            {/* Column Headers */}
            <div className="grid grid-cols-3 gap-2 px-4 py-2 text-xs text-gray-500 font-mono border-b border-gray-800 shrink-0">
                <div className="text-left">Price (USDT)</div>
                <div className="text-right">Amount</div>
                <div className="text-right">Time</div>
            </div>

            {/* Trades List (Scrollable) */}
            <div className="overflow-y-auto flex-1 custom-scrollbar min-h-0">
                <div className="px-4 py-1">
                    {trades.map((trade) => (
                        <div
                            key={trade.id}
                            className="grid grid-cols-3 gap-2 py-1 text-xs font-mono border-b border-gray-800/30 last:border-0 hover:bg-gray-800/30 transition-colors"
                        >
                            <div className={`${trade.side === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                                {trade.price.toLocaleString('en-US', { minimumFractionDigits: 1 })}
                            </div>
                            <div className="text-right text-gray-300">
                                {trade.amount.toFixed(4)}
                            </div>
                            <div className="text-right text-gray-500">
                                {new Date(trade.timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
