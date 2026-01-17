/**
 * Trade Info Panel - Price Stats & Quick Actions
 */

'use client';
import { useState, useEffect } from 'react';
import { useTicker } from '@/lib/hooks';
import { ExternalLink, Bell } from 'lucide-react';
import { TradeInfoSkeleton } from '@/components/ui/LoadingSkeletons';
import { AlertModal } from './AlertModal';

export function TradeInfoPanel({ symbol }: { symbol: string }) {
    const { data, loading } = useTicker(symbol, 5000);
    const [isAlertOpen, setIsAlertOpen] = useState(false);

    if (loading) {
        return <TradeInfoSkeleton />;
    }

    if (!data) {
        return (
            <div className="p-4 border-b border-gray-800">
                <div className="text-sm text-gray-400">No data available</div>
            </div>
        );
    }

    const isPositive = (data.change_24h || 0) >= 0;

    return (
        <div className="border-b border-gray-800 relative">
            {/* Price Info */}
            <div className="p-4 flex justify-between items-start">
                <div>
                    <div className="text-xs text-gray-400 mb-1">Last Price</div>
                    <div className="text-3xl font-bold text-white font-mono mb-1">
                        ${data.last.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </div>
                    <div className={`text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                        {isPositive ? '+' : ''}{(data.change_24h || 0).toFixed(2)}% (24h)
                    </div>
                    {/* Data Source Indicator */}
                    {(data as any).source && (
                        <div className="mt-2">
                            <span className={`text-xs px-2 py-0.5 rounded border ${(data as any).source === 'redis-stream'
                                    ? 'bg-purple-500/20 text-purple-300 border-purple-500/30'
                                    : 'bg-blue-500/20 text-blue-300 border-blue-500/30'
                                }`}>
                                {(data as any).source === 'redis-stream' ? '⚡ Redis Stream' : '🌐 REST API'}
                            </span>
                        </div>
                    )}
                </div>
                <button
                    onClick={() => setIsAlertOpen(true)}
                    className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-gray-400 hover:text-white transition-colors"
                >
                    <Bell className="w-5 h-5" />
                </button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-3 p-4 border-t border-gray-800">
                <div>
                    <div className="text-xs text-gray-400 mb-1">24h High</div>
                    <div className="text-sm font-mono text-white">
                        ${(data.high || data.last).toLocaleString()}
                    </div>
                </div>
                <div>
                    <div className="text-xs text-gray-400 mb-1">24h Low</div>
                    <div className="text-sm font-mono text-white">
                        ${(data.low || data.last).toLocaleString()}
                    </div>
                </div>
                <div>
                    <div className="text-xs text-gray-400 mb-1">24h Volume</div>
                    <div className="text-sm font-mono text-white">
                        ${(data.volume || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </div>
                </div>
                <div>
                    <div className="text-xs text-gray-400 mb-1">Last Update</div>
                    <div className="text-sm text-white">
                        {new Date(data.timestamp).toLocaleTimeString()}
                    </div>
                </div>
            </div>

            {/* Paper Trading Actions */}
            <div className="p-4 border-t border-gray-800 bg-gray-900/50">
                <TradingActions symbol={symbol} price={data.last} />
            </div>

            <AlertModal
                isOpen={isAlertOpen}
                onClose={() => setIsAlertOpen(false)}
                symbol={symbol}
                currentPrice={data.last}
            />
        </div>
    );
}

import { usePortfolioStore } from '@/lib/store';
import { useAlertStore } from '@/lib/alertStore';
import { Wallet, Info } from 'lucide-react';

function TradingActions({ symbol, price }: { symbol: string, price: number }) {
    const { balance, positions, buy, sell } = usePortfolioStore();
    const { addAlert } = useAlertStore();
    const position = positions.find(p => p.symbol === symbol);

    // Auto-Trade State
    const [autoTrade, setAutoTrade] = useState(false);
    const [isBotRunning, setIsBotRunning] = useState(false);

    // Mock trade size: 10% of balance or $1000 min
    const tradeAmountUSD = Math.max(1000, balance * 0.1);
    const quantity = tradeAmountUSD / price;

    const handleBuy = () => {
        if (balance < tradeAmountUSD) {
            addAlert('error', 'Insufficient Funds', 'You do not have enough cash to execute this trade.');
            return;
        }
        buy(symbol, quantity, price);
        addAlert('success', 'Order Executed', `Bought ${quantity.toFixed(4)} ${symbol} @ $${price}`);
    };

    const handleSell = () => {
        if (!position || position.amount <= 0) {
            addAlert('error', 'No Position', 'You do not have any assets to sell.');
            return;
        }
        const sellQty = Math.min(position.amount, quantity);
        sell(symbol, sellQty, price);
        addAlert('success', 'Order Executed', `Sold ${sellQty.toFixed(4)} ${symbol} @ $${price}`);
    };

    // AI AUTO-TRADER BOT LOGIC
    useEffect(() => {
        const interval = setInterval(async () => {
            if (!autoTrade) return;

            setIsBotRunning(true);
            try {
                // Remove /USDT suffix for API call if needed, but our API handles it
                const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/ai/prediction/${encodeURIComponent(symbol)}`);
                const data = await res.json();

                if (data.prediction === 'BUY' && data.confidence > 75 && balance > tradeAmountUSD) {
                    buy(symbol, quantity, price);
                    addAlert('success', '🤖 AI Auto-Trade', `Bot Bought ${symbol} (Conf: ${data.confidence}%)`);
                } else if (data.prediction === 'SELL' && data.confidence > 75 && position && position.amount > 0) {
                    const sellQty = Math.min(position.amount, quantity);
                    sell(symbol, sellQty, price);
                    addAlert('success', '🤖 AI Auto-Trade', `Bot Sold ${symbol} (Conf: ${data.confidence}%)`);
                }
            } catch (e) {
                console.error("Bot Error", e);
            }
            setIsBotRunning(false);
        }, 10000); // Check every 10s

        return () => clearInterval(interval);
    }, [autoTrade, symbol, balance, position, price]); // Re-bind on state change (simplified for MVP)

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-gray-400">
                <div className="flex items-center gap-1">
                    <Wallet className="w-3 h-3" />
                    <span>Balance:</span>
                </div>
                <span className="font-mono text-white">${balance.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
            </div>

            {position && (
                <div className="flex items-center justify-between text-xs text-gray-400">
                    <span>Holding:</span>
                    <span className="font-mono text-cyan-400">
                        {position.amount.toFixed(4)} {symbol.split('/')[0]}
                    </span>
                </div>
            )}

            {/* Bot Toggle */}
            <div className="flex items-center justify-between bg-blue-900/20 p-2 rounded border border-blue-500/30">
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${autoTrade ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
                    <span className="text-xs font-bold text-blue-400">AI Auto-Pilot</span>
                </div>
                <button
                    onClick={() => setAutoTrade(!autoTrade)}
                    className={`text-[10px] px-2 py-1 rounded transition-colors ${autoTrade ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}
                >
                    {autoTrade ? 'ON' : 'OFF'}
                </button>
            </div>

            <div className="grid grid-cols-2 gap-2">
                <button
                    onClick={handleBuy}
                    className="py-3 bg-green-500/20 text-green-400 font-bold rounded border border-green-500/50 hover:bg-green-500 hover:text-white transition-all active:scale-95"
                >
                    BUY
                </button>
                <button
                    onClick={handleSell}
                    className="py-3 bg-red-500/20 text-red-400 font-bold rounded border border-red-500/50 hover:bg-red-500 hover:text-white transition-all active:scale-95"
                    disabled={!position || position.amount <= 0}
                >
                    SELL
                </button>
            </div>

            <div className="text-[10px] text-center text-gray-600 flex items-center justify-center gap-1">
                <Info className="w-3 h-3" />
                <span>Paper Trading Mode (Simulated)</span>
            </div>
        </div>
    );
}
