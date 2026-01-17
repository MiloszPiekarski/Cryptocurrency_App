/**
 * Indicators Panel - Display Technical Indicators
 * Shows RSI, MACD, MA with signals
 */

'use client';

import { TrendingUp, TrendingDown, Activity, Circle } from 'lucide-react';
import { motion } from 'framer-motion';

interface IndicatorsPanelProps {
    indicators: {
        rsi: number | null;
        macd: {
            macd: number;
            signal: number;
            histogram: number;
        } | null;
        sma20: number | null;
        sma50: number | null;
        ema12: number | null;
        ema26: number | null;
    };
    currentPrice: number;
}

export function IndicatorsPanel({ indicators, currentPrice }: IndicatorsPanelProps) {
    // RSI Signal
    const getRSISignal = (rsi: number | null) => {
        if (!rsi) return 'NEUTRAL';
        if (rsi < 30) return 'OVERSOLD';
        if (rsi > 70) return 'OVERBOUGHT';
        return 'NEUTRAL';
    };

    const rsiSignal = getRSISignal(indicators.rsi);
    const rsiColor =
        rsiSignal === 'OVERSOLD' ? 'text-green-400' :
            rsiSignal === 'OVERBOUGHT' ? 'text-red-400' :
                'text-gray-400';

    // MACD Signal
    const macdSignal = indicators.macd && indicators.macd.histogram > 0 ? 'BULLISH' : 'BEARISH';
    const macdColor = macdSignal === 'BULLISH' ? 'text-green-400' : 'text-red-400';

    // Moving Average Signal
    const maSignal =
        indicators.sma20 && currentPrice > indicators.sma20 ? 'ABOVE' : 'BELOW';
    const maColor = maSignal === 'ABOVE' ? 'text-green-400' : 'text-red-400';

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-[#0f1729] border border-gray-800 rounded-lg p-4 space-y-4"
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <Activity className="w-4 h-4 text-purple-400" />
                    Technical Indicators
                </h3>
                <div className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded">
                    Live
                </div>
            </div>

            {/* RSI */}
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">RSI (14)</span>
                    <span className={`text-sm font-semibold ${rsiColor}`}>
                        {indicators.rsi?.toFixed(2) || '--'}
                    </span>
                </div>
                <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                    {indicators.rsi && (
                        <div
                            className={`h-full ${rsiSignal === 'OVERSOLD' ? 'bg-green-500' :
                                    rsiSignal === 'OVERBOUGHT' ? 'bg-red-500' :
                                        'bg-gray-500'
                                }`}
                            style={{ width: `${Math.min(indicators.rsi, 100)}%` }}
                        />
                    )}
                </div>
                <div className="text-xs flex justify-between text-gray-600">
                    <span>0</span>
                    <span className={rsiColor}>{rsiSignal}</span>
                    <span>100</span>
                </div>
            </div>

            {/* MACD */}
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">MACD</span>
                    <span className={`text-sm font-semibold ${macdColor}`}>
                        {macdSignal}
                    </span>
                </div>
                {indicators.macd && (
                    <div className="text-xs space-y-1">
                        <div className="flex justify-between">
                            <span className="text-gray-500">MACD:</span>
                            <span className="text-white font-mono">
                                {indicators.macd.macd.toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-500">Signal:</span>
                            <span className="text-white font-mono">
                                {indicators.macd.signal.toFixed(2)}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-500">Histogram:</span>
                            <span className={`font-mono font-semibold ${macdColor}`}>
                                {indicators.macd.histogram.toFixed(2)}
                            </span>
                        </div>
                    </div>
                )}
            </div>

            {/* Moving Averages */}
            <div className="space-y-2">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Moving Averages</span>
                    <span className={`text-sm font-semibold ${maColor}`}>
                        {maSignal} SMA20
                    </span>
                </div>
                <div className="text-xs space-y-1">
                    <div className="flex justify-between">
                        <span className="text-gray-500">SMA (20):</span>
                        <span className="text-white font-mono">
                            ${indicators.sma20?.toFixed(2) || '--'}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">SMA (50):</span>
                        <span className="text-white font-mono">
                            ${indicators.sma50?.toFixed(2) || '--'}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">EMA (12):</span>
                        <span className="text-cyan-400 font-mono">
                            ${indicators.ema12?.toFixed(2) || '--'}
                        </span>
                    </div>
                    <div className="flex justify-between">
                        <span className="text-gray-500">EMA (26):</span>
                        <span className="text-cyan-400 font-mono">
                            ${indicators.ema26?.toFixed(2) || '--'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Overall Signal */}
            <div className="pt-3 border-t border-gray-800">
                <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-white">Overall Signal</span>
                    <div className="flex items-center gap-2">
                        {macdSignal === 'BULLISH' && rsiSignal !== 'OVERBOUGHT' ? (
                            <>
                                <TrendingUp className="w-4 h-4 text-green-400" />
                                <span className="text-green-400 font-semibold">BUY</span>
                            </>
                        ) : macdSignal === 'BEARISH' && rsiSignal !== 'OVERSOLD' ? (
                            <>
                                <TrendingDown className="w-4 h-4 text-red-400" />
                                <span className="text-red-400 font-semibold">SELL</span>
                            </>
                        ) : (
                            <>
                                <Circle className="w-4 h-4 text-gray-400" />
                                <span className="text-gray-400">NEUTRAL</span>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
