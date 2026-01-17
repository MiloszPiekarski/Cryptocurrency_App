/**
 * TURBO-PLAN X - Markets List Widget
 * Screener and Symbol Selector
 */

'use client';

import { useEffect, useState } from 'react';
import { api, MarketScreenerItem } from '@/lib/api';

interface MarketsListProps {
    onSelect: (symbol: string) => void;
    selectedSymbol: string;
}

export function MarketsList({ onSelect, selectedSymbol }: MarketsListProps) {
    const [data, setData] = useState<MarketScreenerItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [sortBy, setSortBy] = useState<'volume' | 'change' | 'symbol'>('volume');

    useEffect(() => {
        let mounted = true;
        const fetchData = async () => {
            try {
                const items = await api.getScreener();
                if (mounted) {
                    if (items.length > 0) {
                        setData(items);
                    }
                    setLoading(false);
                }
            } catch (err) {
                console.error(err);
                if (mounted) setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 10000); // 10s refresh

        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, []);

    const filteredData = data
        .filter(item => item.symbol.toLowerCase().includes(search.toLowerCase()))
        .sort((a, b) => {
            if (sortBy === 'volume') return b.volume - a.volume;
            if (sortBy === 'change') return b.change_24h - a.change_24h;
            return a.symbol.localeCompare(b.symbol);
        });

    return (
        <div className="w-full h-full bg-[#0f1729] rounded-xl border border-gray-700 flex flex-col overflow-hidden">
            {/* Header & Search */}
            <div className="p-3 border-b border-gray-700 shrink-0 space-y-2">
                <h3 className="text-sm font-semibold text-white">Markets</h3>
                <input
                    type="text"
                    placeholder="Search..."
                    className="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1 text-xs text-white focus:outline-none focus:border-cyan-500"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
                <div className="flex gap-1 text-[10px] text-gray-400">
                    <button onClick={() => setSortBy('volume')} className={`px-2 py-0.5 rounded ${sortBy === 'volume' ? 'bg-gray-700 text-white' : 'hover:bg-gray-800'}`}>Vol</button>
                    <button onClick={() => setSortBy('change')} className={`px-2 py-0.5 rounded ${sortBy === 'change' ? 'bg-gray-700 text-white' : 'hover:bg-gray-800'}`}>24h%</button>
                    <button onClick={() => setSortBy('symbol')} className={`px-2 py-0.5 rounded ${sortBy === 'symbol' ? 'bg-gray-700 text-white' : 'hover:bg-gray-800'}`}>Name</button>
                </div>
            </div>

            {/* List */}
            <div className="overflow-y-auto flex-1 custom-scrollbar">
                {loading ? (
                    <div className="p-4 space-y-2">
                        {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-8 bg-gray-800/50 rounded animate-pulse"></div>)}
                    </div>
                ) : (
                    <div>
                        {filteredData.map(item => {
                            const simpleSymbol = item.symbol.replace('/USDT', '');
                            const isSelected = selectedSymbol.includes(simpleSymbol);
                            const isPositive = item.change_24h >= 0;

                            return (
                                <div
                                    key={item.symbol}
                                    onClick={() => onSelect(item.symbol)} // Item symbol already contains /USDT from API
                                    className={`px-3 py-2 cursor-pointer border-l-2 transition-colors flex justify-between items-center
                      ${isSelected ? 'bg-cyan-900/20 border-cyan-500' : 'border-transparent hover:bg-gray-800/50'}
                   `}
                                >
                                    <div>
                                        <div className={`text-xs font-bold ${isSelected ? 'text-cyan-400' : 'text-gray-300'}`}>{simpleSymbol}</div>
                                        <div className="text-[10px] text-gray-500">{(item.volume / 1000000).toFixed(1)}M Vol</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-xs text-white font-mono">{item.last.toLocaleString()}</div>
                                        <div className={`text-[10px] ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                                            {isPositive ? '+' : ''}{item.change_24h.toFixed(2)}%
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
