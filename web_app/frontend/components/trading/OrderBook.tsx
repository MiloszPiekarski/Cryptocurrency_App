/**
 * TURBO-PLAN X - Order Book Widget
 * Professional order book display with market depth visualization
 */

'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface OrderBookLevel {
    price: number;
    quantity: number;
}

interface OrderBookData {
    symbol: string;
    bids: OrderBookLevel[];
    asks: OrderBookLevel[];
    timestamp: number;
}

interface OrderBookProps {
    symbol: string;
    refreshInterval?: number;
    levels?: number;
}

export function OrderBook({
    symbol,
    refreshInterval = 1000,
    levels = 15
}: OrderBookProps) {
    const [data, setData] = useState<OrderBookData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [lastPrice, setLastPrice] = useState<number | null>(null);

    // Fetch order book
    useEffect(() => {
        let mounted = true;

        const fetchOrderBook = async () => {
            try {
                const response = await api.getOrderBook(symbol);
                if (mounted) {
                    setData(response);
                    setLoading(false);
                    setError(null);
                }
            } catch (err) {
                if (mounted) {
                    setError(err instanceof Error ? err.message : 'Failed to fetch order book');
                    setLoading(false);
                }
            }
        };

        fetchOrderBook();
        const interval = setInterval(fetchOrderBook, refreshInterval);

        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, [symbol, refreshInterval]);

    // Fetch current price for mid-price
    useEffect(() => {
        let mounted = true;

        const fetchPrice = async () => {
            try {
                const ticker = await api.getTicker(symbol);
                if (mounted) {
                    setLastPrice(ticker.last);
                }
            } catch (err) {
                // Silently fail - not critical
            }
        };

        fetchPrice();
        const interval = setInterval(fetchPrice, 2000);

        return () => {
            mounted = false;
            clearInterval(interval);
        };
    }, [symbol]);

    if (loading) {
        return (
            <div className="w-full h-[500px] bg-[#0f1729] rounded-xl border border-gray-700 p-4">
                <div className="flex items-center justify-center h-full">
                    <div className="text-gray-500">Loading order book...</div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="w-full h-[500px] bg-[#0f1729] rounded-xl border border-gray-700 p-4">
                <div className="flex items-center justify-center h-full">
                    <div className="text-red-400">Error: {error}</div>
                </div>
            </div>
        );
    }

    if (!data) return null;

    // Calculate max volume for depth bar scaling
    const allLevels = [...data.bids, ...data.asks];
    const maxVolume = Math.max(...allLevels.map(l => l.quantity));

    // Take top N levels
    const displayAsks = data.asks.slice(0, levels).reverse();
    const displayBids = data.bids.slice(0, levels);

    // Calculate spread
    const bestBid = data.bids[0]?.price || 0;
    const bestAsk = data.asks[0]?.price || 0;
    const spread = bestAsk - bestBid;
    const spreadPercent = bestBid > 0 ? (spread / bestBid) * 100 : 0;

    return (
        <div className="w-full bg-[#0f1729] rounded-xl border border-gray-700">
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-700">
                <h3 className="text-sm font-semibold text-white">Order Book</h3>
                <div className="text-xs text-gray-500 mt-1">{symbol.replace('USDT', '/USDT')}</div>
            </div>

            {/* Column Headers */}
            <div className="grid grid-cols-3 gap-2 px-4 py-2 text-xs text-gray-500 font-mono border-b border-gray-800">
                <div className="text-left">Price (USDT)</div>
                <div className="text-right">Amount</div>
                <div className="text-right">Total</div>
            </div>

            {/* Order Book Content */}
            <div className="relative">
                {/* Asks (Sell Orders - Red) */}
                <div className="px-4 py-1">
                    {displayAsks.map((ask, idx) => {
                        const depthPercent = (ask.quantity / maxVolume) * 100;
                        const total = ask.price * ask.quantity;

                        return (
                            <div
                                key={`ask-${idx}`}
                                className="relative grid grid-cols-3 gap-2 py-1 text-xs font-mono group hover:bg-red-500/5 transition-colors"
                            >
                                {/* Depth Bar (Red) */}
                                <div
                                    className="absolute right-0 top-0 bottom-0 bg-red-500/10"
                                    style={{ width: `${depthPercent}%` }}
                                />

                                <div className="relative text-red-400">{ask.price.toFixed(1)}</div>
                                <div className="relative text-right text-gray-300">{ask.quantity.toFixed(4)}</div>
                                <div className="relative text-right text-gray-500">{total.toLocaleString('en-US', { maximumFractionDigits: 0 })}</div>
                            </div>
                        );
                    })}
                </div>

                {/* Spread / Last Price */}
                <div className="px-4 py-3 bg-gray-900/50 border-y border-gray-800">
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="text-lg font-bold font-mono text-white">
                                {lastPrice ? `$${lastPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '—'}
                            </div>
                            <div className="text-xs text-gray-500">Last Price</div>
                        </div>
                        <div className="text-right">
                            <div className="text-sm font-mono text-yellow-400">
                                ${spread.toFixed(2)}
                            </div>
                            <div className="text-xs text-gray-500">
                                Spread ({spreadPercent.toFixed(3)}%)
                            </div>
                        </div>
                    </div>
                </div>

                {/* Bids (Buy Orders - Green) */}
                <div className="px-4 py-1">
                    {displayBids.map((bid, idx) => {
                        const depthPercent = (bid.quantity / maxVolume) * 100;
                        const total = bid.price * bid.quantity;

                        return (
                            <div
                                key={`bid-${idx}`}
                                className="relative grid grid-cols-3 gap-2 py-1 text-xs font-mono group hover:bg-green-500/5 transition-colors"
                            >
                                {/* Depth Bar (Green) */}
                                <div
                                    className="absolute right-0 top-0 bottom-0 bg-green-500/10"
                                    style={{ width: `${depthPercent}%` }}
                                />

                                <div className="relative text-green-400">{bid.price.toFixed(1)}</div>
                                <div className="relative text-right text-gray-300">{bid.quantity.toFixed(4)}</div>
                                <div className="relative text-right text-gray-500">{total.toLocaleString('en-US', { maximumFractionDigits: 0 })}</div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Footer Info */}
            <div className="px-4 py-2 border-t border-gray-700 text-xs text-gray-500">
                <div className="flex justify-between">
                    <span>Updated: {new Date(data.timestamp).toLocaleTimeString()}</span>
                    <span className="text-cyan-400">Live</span>
                </div>
            </div>
        </div>
    );
}
