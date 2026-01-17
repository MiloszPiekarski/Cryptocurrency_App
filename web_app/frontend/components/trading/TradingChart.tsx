/**
 * Simplified Candlestick Chart 
 * Using simpler approach - stable and working!
 */

'use client';

import { useOHLCV } from '@/lib/hooks';
import { ChartSkeleton } from '@/components/ui/LoadingSkeletons';
import {
    ComposedChart,
    Line,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
    Area
} from 'recharts';

interface TradingChartProps {
    symbol: string;
    timeframe: '1m' | '5m' | '15m' | '1h' | '4h' | '1d';
}

// Enhanced Tooltip
const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload[0]) {
        const data = payload[0].payload;
        const isGreen = data.close >= data.open;
        const change = ((data.close - data.open) / data.open * 100).toFixed(2);

        return (
            <div className="bg-gray-900/95 border border-gray-700 rounded-lg p-3 shadow-xl backdrop-blur-sm">
                <div className="text-xs text-gray-400 mb-2 font-semibold">{data.time}</div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                    <div className="text-gray-400">Open:</div>
                    <div className="text-white font-mono tabular-nums">${data.open?.toFixed(2)}</div>

                    <div className="text-gray-400">High:</div>
                    <div className="text-green-400 font-mono tabular-nums">${data.high?.toFixed(2)}</div>

                    <div className="text-gray-400">Low:</div>
                    <div className="text-red-400 font-mono tabular-nums">${data.low?.toFixed(2)}</div>

                    <div className="text-gray-400">Close:</div>
                    <div className={`font-mono font-bold tabular-nums ${isGreen ? 'text-green-400' : 'text-red-400'}`}>
                        ${data.close?.toFixed(2)}
                    </div>

                    <div className="text-gray-400">Change:</div>
                    <div className={`font-mono font-semibold tabular-nums ${parseFloat(change) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {parseFloat(change) >= 0 ? '+' : ''}{change}%
                    </div>

                    <div className="text-gray-400 mt-1 col-span-2 border-t border-gray-700 pt-1.5">
                        Volume: <span className="text-cyan-400 font-mono tabular-nums">
                            ${(data.volume || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                        </span>
                    </div>
                </div>
            </div>
        );
    }
    return null;
};

export function TradingChart({ symbol, timeframe }: TradingChartProps) {
    const limit = timeframe === '1m' ? 500 : timeframe === '1h' ? 168 : 180;
    const { data, loading, error } = useOHLCV(symbol, timeframe, limit);

    const chartData = data?.candles.map((candle, idx) => {
        const date = new Date(candle.time);

        let timeLabel = '';
        if (timeframe === '1m' || timeframe === '5m') {
            timeLabel = date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
        } else if (timeframe === '1h') {
            timeLabel = date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
            }) + ' ' + date.getHours() + 'h';
        } else {
            timeLabel = date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
            });
        }

        const isGreen = candle.close >= candle.open;

        return {
            index: idx,
            time: timeLabel,
            open: candle.open,
            high: candle.high,
            low: candle.low,
            close: candle.close,
            volume: candle.volume,
            isGreen,
            // For area chart
            price: candle.close,
        };
    }) || [];

    // Calculate price range
    const prices = chartData.flatMap(d => [d.high, d.low]).filter(p => p > 0);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const priceRange = maxPrice - minPrice;
    const priceDomain = [
        Math.max(0, minPrice - priceRange * 0.05),
        maxPrice + priceRange * 0.05
    ];

    // Get current price change color
    const currentCandle = chartData[chartData.length - 1];
    const isCurrentGreen = currentCandle?.close >= currentCandle?.open;

    return (
        <div className="flex-1 flex flex-col bg-[#0a0e27]">
            {/* Chart Header */}
            <div className="h-12 bg-[#0f1729] border-b border-gray-800 flex items-center justify-between px-4">
                <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-400">Price Chart</span>
                    {data && data.candles.length > 0 && (
                        <div className="flex items-center gap-3 text-sm">
                            <span className="text-gray-500">O</span>
                            <span className="text-white tabular-nums">{data.candles[data.candles.length - 1]?.open.toFixed(2)}</span>
                            <span className="text-gray-500">H</span>
                            <span className="text-green-400 tabular-nums">{data.candles[data.candles.length - 1]?.high.toFixed(2)}</span>
                            <span className="text-gray-500">L</span>
                            <span className="text-red-400 tabular-nums">{data.candles[data.candles.length - 1]?.low.toFixed(2)}</span>
                            <span className="text-gray-500">C</span>
                            <span className={`font-bold tabular-nums ${isCurrentGreen ? 'text-green-400' : 'text-red-400'}`}>
                                {data.candles[data.candles.length - 1]?.close.toFixed(2)}
                            </span>
                        </div>
                    )}
                </div>
                <div className="flex items-center gap-2 text-xs">
                    <div className="px-2 py-1 bg-cyan-500/20 text-cyan-400 rounded font-semibold">
                        📈 Live Chart
                    </div>
                    <div className="px-2 py-1 bg-purple-500/20 text-purple-400 rounded tabular-nums">
                        {data?.candles.length || 0} bars
                    </div>
                </div>
            </div>

            {/* Main Chart Area */}
            <div className="flex-1 flex flex-col p-2">
                {loading && <ChartSkeleton />}

                {error && (
                    <div className="flex-1 flex items-center justify-center">
                        <div className="text-center">
                            <div className="text-red-400 mb-2 text-lg font-semibold">⚠️ Error Loading Chart</div>
                            <div className="text-sm text-gray-400 mb-4">{error}</div>
                            <div className="text-xs text-gray-600 space-y-1">
                                <div>Symbol: <span className="text-white">{symbol}</span></div>
                                <div>Timeframe: <span className="text-white">{timeframe}</span></div>
                            </div>
                            <button
                                onClick={() => window.location.reload()}
                                className="mt-4 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 text-sm transition-colors"
                            >
                                Reload Page
                            </button>
                        </div>
                    </div>
                )}

                {!loading && !error && chartData.length > 0 && (
                    <div className="flex-1 flex flex-col gap-2">
                        {/* Price Chart (70% height) */}
                        <div className="flex-[7]">
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                    <defs>
                                        <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.3} />
                                            <stop offset="100%" stopColor="#06b6d4" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>

                                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                                    <XAxis
                                        dataKey="time"
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 10 }}
                                        interval={Math.floor(chartData.length / 8)}
                                    />
                                    <YAxis
                                        domain={priceDomain}
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 10 }}
                                        width={70}
                                        tickFormatter={(value) => `$${value.toFixed(0)}`}
                                    />
                                    <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#4b5563', strokeWidth: 1, strokeDasharray: '3 3' }} />

                                    {/* Area fill */}
                                    <Area
                                        type="monotone"
                                        dataKey="price"
                                        stroke="none"
                                        fill="url(#priceGradient)"
                                    />

                                    {/* Main price line */}
                                    <Line
                                        type="monotone"
                                        dataKey="price"
                                        stroke="#06b6d4"
                                        strokeWidth={2}
                                        dot={false}
                                        activeDot={{ r: 5, fill: '#06b6d4', stroke: '#0a0e27', strokeWidth: 2 }}
                                    />
                                </ComposedChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Volume Chart (30% height) */}
                        <div className="flex-[3] border-t border-gray-800 pt-2">
                            <div className="text-xs text-gray-500 mb-1 px-2">Volume</div>
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={chartData} margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                                    <XAxis
                                        dataKey="time"
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 10 }}
                                        interval={Math.floor(chartData.length / 8)}
                                    />
                                    <YAxis
                                        stroke="#6b7280"
                                        tick={{ fill: '#6b7280', fontSize: 10 }}
                                        width={70}
                                        tickFormatter={(value) => {
                                            if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
                                            if (value >= 1e6) return `$${(value / 1e6).toFixed(0)}M`;
                                            if (value >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
                                            return `$${value.toFixed(0)}`;
                                        }}
                                    />
                                    <Bar dataKey="volume" radius={[3, 3, 0, 0]}>
                                        {chartData.map((entry, index) => (
                                            <Cell
                                                key={`vol-${index}`}
                                                fill={entry.isGreen ? '#10b981' : '#ef4444'}
                                                fillOpacity={0.6}
                                            />
                                        ))}
                                    </Bar>
                                </ComposedChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
