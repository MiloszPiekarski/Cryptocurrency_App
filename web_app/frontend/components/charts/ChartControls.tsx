/**
 * TURBO-PLAN X Chart Controls - FIXED VERSION
 * Fixed compact mode layout and styling
 */

'use client';

import { useRef, useEffect, useState } from 'react';

export type Timeframe = '1m' | '5m' | '15m' | '30m' | '1h' | '4h' | '1d' | '1w' | '1M';
export type ChartTypeOption = 'candlestick' | 'area' | 'line';

interface ChartControlsProps {
    symbol: string;
    timeframe: Timeframe;
    chartType: ChartTypeOption;
    onSymbolChange: (symbol: string) => void;
    onTimeframeChange: (timeframe: Timeframe) => void;
    onChartTypeChange: (type: ChartTypeOption) => void;
    availableSymbols?: Array<{ symbol: string; name: string }>;
    compact?: boolean;
}

const ALL_TIMEFRAMES: Array<{ value: Timeframe; label: string }> = [
    { value: '1m', label: '1m' },
    { value: '5m', label: '5m' },
    { value: '15m', label: '15m' },
    { value: '30m', label: '30m' },
    { value: '1h', label: '1h' },
    { value: '4h', label: '4h' },
    { value: '1d', label: '1D' },
    { value: '1w', label: '1W' },
    { value: '1M', label: '1M' },
];

const CHART_TYPES: Array<{ value: ChartTypeOption; label: string; icon: string }> = [
    { value: 'candlestick', label: 'Candles', icon: '🕯️' },
    { value: 'area', label: 'Area', icon: '📈' },
    { value: 'line', label: 'Line', icon: '📉' },
];

export function ChartControls({
    symbol,
    timeframe,
    chartType,
    onSymbolChange,
    onTimeframeChange,
    onChartTypeChange,
    availableSymbols = [],
    compact = false
}: ChartControlsProps) {
    const [showSymbolPicker, setShowSymbolPicker] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowSymbolPicker(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const filteredSymbols = availableSymbols.filter(s =>
        s.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className={`flex ${compact ? 'flex-col gap-2' : 'flex-wrap gap-3'} mb-4`}>
            {/* Symbol Selector */}
            <div className="relative" ref={dropdownRef}>
                <button
                    onClick={() => setShowSymbolPicker(!showSymbolPicker)}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white font-semibold transition-colors flex items-center gap-2 text-sm"
                >
                    <span>{symbol.replace('/USDT', '')}</span>
                    <span className="text-xs text-gray-400">▼</span>
                </button>

                {showSymbolPicker && availableSymbols.length > 0 && (
                    <div className="absolute top-full left-0 mt-2 w-64 bg-gray-900 border border-gray-700 rounded-lg shadow-2xl z-50 max-h-96 overflow-hidden flex flex-col">
                        <div className="p-3 border-b border-gray-700">
                            <input
                                type="text"
                                placeholder="Search symbol..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:outline-none focus:border-cyan-500"
                                autoFocus
                            />
                        </div>
                        <div className="overflow-y-auto">
                            {filteredSymbols.map((s) => (
                                <button
                                    key={s.symbol}
                                    onClick={() => {
                                        onSymbolChange(s.symbol);
                                        setShowSymbolPicker(false);
                                        setSearchTerm('');
                                    }}
                                    className="w-full px-4 py-2 text-left hover:bg-gray-800 transition-colors text-white text-sm flex justify-between items-center"
                                >
                                    <span className="font-semibold">{s.symbol.replace('/USDT', '')}</span>
                                    <span className="text-xs text-gray-400">{s.name}</span>
                                </button>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Timeframe Selector */}
            <div className="flex gap-1 bg-gray-900 rounded-lg p-1 flex-wrap">
                {ALL_TIMEFRAMES.map(tf => (
                    <button
                        key={tf.value}
                        onClick={() => onTimeframeChange(tf.value)}
                        className={`px-2 py-1 rounded text-xs font-semibold transition-all ${timeframe === tf.value
                                ? 'bg-cyan-500 text-white'
                                : 'text-gray-400 hover:text-white hover:bg-gray-800'
                            }`}
                    >
                        {tf.label}
                    </button>
                ))}
            </div>

            {/* Chart Type Selector - FIXED for compact mode */}
            <div className="flex gap-1 bg-gray-900 rounded-lg p-1">
                {CHART_TYPES.map(ct => (
                    <button
                        key={ct.value}
                        onClick={() => onChartTypeChange(ct.value)}
                        className={`px-2 py-1 rounded text-xs font-medium transition-all flex items-center gap-1 whitespace-nowrap ${chartType === ct.value
                                ? 'bg-purple-500 text-white'
                                : 'text-gray-400 hover:text-white hover:bg-gray-800'
                            }`}
                        title={ct.label}
                    >
                        <span className="text-sm">{ct.icon}</span>
                        {!compact && <span>{ct.label}</span>}
                    </button>
                ))}
            </div>
        </div>
    );
}
