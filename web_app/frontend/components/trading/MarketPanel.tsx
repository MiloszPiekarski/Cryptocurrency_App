/**
 * Market Panel - Symbol List & Search
 */

'use client';

import { useState } from 'react';
import { useTicker, useScreener } from '@/lib/hooks';
import { Search } from 'lucide-react';
import { MarketListSkeleton } from '@/components/ui/LoadingSkeletons';

function SymbolRow({ data, isSelected, onClick }: {
    data: any;
    isSelected: boolean;
    onClick: () => void;
}) {
    if (!data) return null;

    const isPositive = (data.change_24h || 0) >= 0;

    return (
        <button
            onClick={onClick}
            className={`w-full px-4 py-2.5 flex items-center justify-between hover:bg-gray-800/50 transition-colors ${isSelected ? 'bg-cyan-500/10 border-l-2 border-cyan-500' : ''
                }`}
        >
            <div className="flex flex-col items-start">
                <span className="font-semibold text-white text-sm">
                    {data.symbol.replace('/USDT', '')}
                </span>
                <span className="text-xs text-gray-500">USDT</span>
            </div>
            <div className="flex flex-col items-end">
                <span className="font-mono text-white text-sm">
                    ${data.last.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <span className={`text-xs font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? '+' : ''}{(data.change_24h || 0).toFixed(2)}%
                </span>
            </div>
        </button>
    );
}

export function MarketPanel({ selectedSymbol, onSelectSymbol }: {
    selectedSymbol: string;
    onSelectSymbol: (symbol: string) => void;
}) {
    const [search, setSearch] = useState('');
    const [tab, setTab] = useState<'all' | 'favorites'>('all');

    // Use new Screener Hook (efficient batch fetch)
    const { data: screenerData, loading } = useScreener();

    const filteredData = (screenerData || []).filter(item =>
        item.symbol.toLowerCase().includes(search.toLowerCase())
    );

    if (loading && filteredData.length === 0) {
        return <MarketListSkeleton />;
    }

    return (
        <div className="flex flex-col h-1/2 border-b border-gray-800">
            {/* Header */}
            <div className="p-3 border-b border-gray-800">
                <div className="flex gap-2 mb-3">
                    <button
                        onClick={() => setTab('all')}
                        className={`flex-1 py-1.5 text-sm font-medium rounded transition-colors ${tab === 'all'
                            ? 'bg-cyan-500 text-white'
                            : 'bg-gray-800 text-gray-400 hover:text-white'
                            }`}
                    >
                        All Markets
                    </button>
                    <button
                        onClick={() => setTab('favorites')}
                        className={`flex-1 py-1.5 text-sm font-medium rounded transition-colors ${tab === 'favorites'
                            ? 'bg-cyan-500 text-white'
                            : 'bg-gray-800 text-gray-400 hover:text-white'
                            }`}
                    >
                        ⭐ Favorites
                    </button>
                </div>

                {/* Search */}
                <div className="relative mb-2">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                    <input
                        type="text"
                        placeholder="Search symbol..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                    />
                </div>

                {/* Headers */}
                <div className="flex justify-between text-xs text-gray-500 px-2 mt-2">
                    <span>Symbol</span>
                    <div className="flex gap-4">
                        <span>Price</span>
                        <span>24h %</span>
                    </div>
                </div>
            </div>

            {/* Symbol List */}
            <div className="flex-1 overflow-y-auto">
                {filteredData.map(item => (
                    <SymbolRow
                        key={item.symbol}
                        data={item}
                        isSelected={selectedSymbol === item.symbol}
                        onClick={() => onSelectSymbol(item.symbol)}
                    />
                ))}

                {filteredData.length === 0 && !loading && (
                    <div className="text-center p-4 text-gray-500 text-sm">
                        No symbols found.
                    </div>
                )}
            </div>
        </div>
    );
}
