/**
 * AI Signals Panel - KILLER FEATURE!
 * Shows AI predictions & confidence
 */

'use client';

import { Brain, TrendingUp, TrendingDown, Activity } from 'lucide-react';

export function AISignalsPanel() {
    // Mock AI signals - will be replaced with real API
    const signals = [
        {
            symbol: 'BTC/USDT',
            signal: 'BUY',
            confidence: 0.92,
            target: 92500,
            stopLoss: 88200,
            timeframe: '4h',
            reason: 'Volume spike + RSI oversold + Whale accumulation',
        },
        {
            symbol: 'ETH/USDT',
            signal: 'SELL',
            confidence: 0.78,
            target: 2950,
            stopLoss: 3100,
            timeframe: '1h',
            reason: 'Bearish divergence + Resistance level',
        },
        {
            symbol: 'SOL/USDT',
            signal: 'HOLD',
            confidence: 0.65,
            target: null,
            stopLoss: null,
            timeframe: '4h',
            reason: 'Consolidation phase, wait for breakout',
        },
    ];

    return (
        <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-800 flex items-center gap-2">
                <Brain className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-semibold text-white">AI Signals</h3>
                <div className="ml-auto px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs font-bold rounded">
                    LIVE
                </div>
            </div>

            {/* Signals List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {signals.map((signal, idx) => (
                    <div
                        key={idx}
                        className={`p-3 rounded-lg border ${signal.signal === 'BUY'
                                ? 'bg-green-500/5 border-green-500/30'
                                : signal.signal === 'SELL'
                                    ? 'bg-red-500/5 border-red-500/30'
                                    : 'bg-yellow-500/5 border-yellow-500/30'
                            }`}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                {signal.signal === 'BUY' ? (
                                    <TrendingUp className="w-4 h-4 text-green-400" />
                                ) : signal.signal === 'SELL' ? (
                                    <TrendingDown className="w-4 h-4 text-red-400" />
                                ) : (
                                    <Activity className="w-4 h-4 text-yellow-400" />
                                )}
                                <span className="font-semibold text-white text-sm">
                                    {signal.symbol.replace('/USDT', '')}
                                </span>
                            </div>
                            <div className={`px-2 py-0.5 rounded text-xs font-bold ${signal.signal === 'BUY'
                                    ? 'bg-green-500/20 text-green-400'
                                    : signal.signal === 'SELL'
                                        ? 'bg-red-500/20 text-red-400'
                                        : 'bg-yellow-500/20 text-yellow-400'
                                }`}>
                                {signal.signal}
                            </div>
                        </div>

                        {/* Confidence */}
                        <div className="mb-2">
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="text-gray-400">Confidence</span>
                                <span className="text-white font-mono font-semibold">
                                    {(signal.confidence * 100).toFixed(0)}%
                                </span>
                            </div>
                            <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${signal.confidence >= 0.8
                                            ? 'bg-green-500'
                                            : signal.confidence >= 0.6
                                                ? 'bg-yellow-500'
                                                : 'bg-red-500'
                                        }`}
                                    style={{ width: `${signal.confidence * 100}%` }}
                                />
                            </div>
                        </div>

                        {/* Details */}
                        {signal.target && (
                            <div className="grid grid-cols-2 gap-2 mb-2 text-xs">
                                <div>
                                    <div className="text-gray-400">Target</div>
                                    <div className="text-green-400 font-mono font-semibold">
                                        ${signal.target.toLocaleString()}
                                    </div>
                                </div>
                                {signal.stopLoss && (
                                    <div>
                                        <div className="text-gray-400">Stop Loss</div>
                                        <div className="text-red-400 font-mono font-semibold">
                                            ${signal.stopLoss.toLocaleString()}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Reason */}
                        <div className="text-xs text-gray-400 italic">
                            {signal.reason}
                        </div>

                        {/* Timeframe */}
                        <div className="mt-2 pt-2 border-t border-gray-700 flex items-center justify-between text-xs">
                            <span className="text-gray-500">Timeframe: {signal.timeframe}</span>
                            <span className="text-purple-400">Updated 2m ago</span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Pro Upgrade CTA */}
            <div className="p-3 border-t border-gray-800 bg-gradient-to-r from-purple-500/10 to-cyan-500/10">
                <div className="text-xs text-gray-400 mb-1">Free tier: 3 signals per day</div>
                <button className="w-full py-2 bg-gradient-to-r from-purple-500 to-cyan-500 text-white text-sm font-semibold rounded hover:opacity-90 transition-opacity">
                    Upgrade to Pro - Unlimited Signals
                </button>
            </div>
        </div>
    );
}
