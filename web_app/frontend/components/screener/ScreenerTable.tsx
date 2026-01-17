'use client';

import React from 'react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { ArrowUpRight, ArrowDownRight, Activity, Zap, TrendingUp, TrendingDown } from 'lucide-react';

// --- Types ---
interface ScreenerAsset {
    symbol: string;
    name: string;
    price: number;
    change_24h: number;
    low_24h: number;
    high_24h: number;
    volume_usdt: number;
    sparkline_7d: number[];
    quant_score: number;
    signal: string;
}

interface ScreenerTableProps {
    data: ScreenerAsset[];
    isLoading: boolean;
}

// --- Helper Components ---

const Sparkline = ({ data, color }: { data: number[], color: string }) => {
    const chartData = data.map((val, i) => ({ i, val }));
    return (
        <div className="h-10 w-24">
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                    <Line
                        type="monotone"
                        dataKey="val"
                        stroke={color}
                        strokeWidth={2}
                        dot={false}
                        isAnimationActive={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

const RangeBar = ({ low, high, current }: { low: number, high: number, current: number }) => {
    // Avoid division by zero
    const range = high - low || 1;
    const positionPct = Math.min(Math.max(((current - low) / range) * 100, 0), 100);

    return (
        <div className="w-32 flex items-center gap-2">
            <span className="text-[10px] text-gray-500 font-mono">${low.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
            <div className="flex-1 h-1.5 bg-gray-800 rounded-full relative">
                <div
                    className="absolute top-1/2 -translate-y-1/2 w-2 h-2 bg-white rounded-full shadow-[0_0_8px_white]"
                    style={{ left: `${positionPct}%` }}
                />
            </div>
            <span className="text-[10px] text-gray-500 font-mono">${high.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
        </div>
    );
};

const ConfidenceMeter = ({ score }: { score: number }) => {
    const getGradient = (s: number) => {
        if (s >= 80) return 'bg-gradient-to-r from-emerald-600 to-green-400';
        if (s >= 50) return 'bg-gradient-to-r from-yellow-600 to-yellow-400';
        return 'bg-gradient-to-r from-red-900 to-red-600';
    };

    return (
        <div className="flex items-center gap-3">
            <div className="flex-1 h-3 bg-gray-800 rounded sm:w-24 overflow-hidden">
                <div
                    className={`h-full ${getGradient(score)}`}
                    style={{ width: `${score}%` }}
                />
            </div>
            <span className={`text-xs font-bold font-mono ${score >= 80 ? 'text-green-400' : score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                {score}%
            </span>
        </div>
    );
};

// --- Main Component ---

export function ScreenerTable({ data, isLoading }: ScreenerTableProps) {

    if (isLoading) {
        return (
            <div className="space-y-4 animate-pulse">
                {[...Array(10)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-900/50 rounded-xl border border-gray-800" />
                ))}
            </div>
        );
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full border-collapse">
                <thead>
                    <tr className="text-left text-xs uppercase text-gray-500 border-b border-gray-800">
                        <th className="py-4 px-4 font-medium tracking-wider">Asset</th>
                        <th className="py-4 px-4 font-medium tracking-wider">Price / 24h</th>
                        <th className="py-4 px-4 font-medium tracking-wider">24h Range</th>
                        <th className="py-4 px-4 font-medium tracking-wider">Market Trend (7d)</th>
                        <th className="py-4 px-4 font-medium tracking-wider text-right">Volume</th>
                        <th className="py-4 px-4 font-medium tracking-wider text-right">Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((asset, index) => {
                        const isPositive = asset.change_24h >= 0;
                        const trendColor = asset.sparkline_7d[asset.sparkline_7d.length - 1] >= asset.sparkline_7d[0]
                            ? '#34d399' // emerald-400
                            : '#f87171'; // red-400

                        return (
                            <tr
                                key={asset.symbol}
                                className="group border-b border-gray-800/50 hover:bg-gray-800/30 transition-all"
                            >
                                {/* ASSET */}
                                <td className="py-4 px-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center font-bold text-[10px] text-gray-400 border border-gray-700">
                                            {asset.symbol[0]}
                                        </div>
                                        <div>
                                            <div className="font-bold text-white group-hover:text-cyan-400 transition-colors">
                                                {asset.symbol}
                                            </div>
                                            <div className="text-[10px] text-gray-500 font-medium">
                                                {asset.name}
                                            </div>
                                        </div>
                                    </div>
                                </td>

                                {/* PRICE */}
                                <td className="py-4 px-4">
                                    <div className="font-mono text-base font-medium text-white">
                                        ${asset.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                    </div>
                                    <div className={`flex items-center text-xs font-bold mt-1 ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                                        {isPositive ? <ArrowUpRight size={12} className="mr-1" /> : <ArrowDownRight size={12} className="mr-1" />}
                                        {Math.abs(asset.change_24h).toFixed(2)}%
                                    </div>
                                </td>

                                {/* RANGE */}
                                <td className="py-4 px-4">
                                    <RangeBar low={asset.low_24h} high={asset.high_24h} current={asset.price} />
                                </td>

                                {/* TREND */}
                                <td className="py-4 px-4">
                                    <Sparkline data={asset.sparkline_7d} color={trendColor} />
                                </td>

                                {/* VOLUME */}
                                <td className="py-4 px-4 text-right">
                                    <div className="text-sm font-mono text-gray-300">
                                        ${(asset.volume_usdt / 1_000_000).toFixed(1)}M
                                    </div>
                                </td>

                                {/* AI CONFIDENCE */}
                                <td className="py-4 px-4 text-right">
                                    <div className="flex justify-end">
                                        <ConfidenceMeter score={asset.quant_score} />
                                    </div>
                                    <div className="text-[10px] text-gray-500 mt-1 uppercase tracking-widest ">
                                        {asset.signal}
                                    </div>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}
