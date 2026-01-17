/**
 * Order Book Panel - Live Bids & Asks
 */

'use client';

import { useEffect, useState } from 'react';
import { OrderBookSkeleton } from '@/components/ui/LoadingSkeletons';
import { MiniEmptyState } from '@/components/ui/EmptyStates';
import { Database } from 'lucide-react';

interface OrderBookProps {
    symbol: string;
}

export function OrderBookPanel({ symbol }: OrderBookProps) {
    const [loading, setLoading] = useState(true);
    const [orderBook, setOrderBook] = useState<{
        bids: { price: number; quantity: number }[];
        asks: { price: number; quantity: number }[];
    } | null>(null);

    useEffect(() => {
        // Fetch order book from API
        const fetchOrderBook = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/v1/market/orderbook/${symbol.replace('/', '')}`);
                if (res.ok) {
                    const data = await res.json();
                    setOrderBook({
                        bids: data.bids || [],
                        asks: data.asks || [],
                    });
                }
            } catch (error) {
                // Silent fail - orderbook is optional
            } finally {
                setLoading(false);
            }
        };

        fetchOrderBook();
        const interval = setInterval(fetchOrderBook, 2000);

        return () => clearInterval(interval);
    }, [symbol]);

    const maxBidVolume = orderBook ? Math.max(...orderBook.bids.map((b: any) => b.quantity)) : 1;
    const maxAskVolume = orderBook ? Math.max(...orderBook.asks.map((a: any) => a.quantity)) : 1;

    if (loading) {
        return <OrderBookSkeleton />;
    }

    return (
        <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 border-b border-gray-800">
                <h3 className="text-sm font-semibold text-white">Order Book</h3>
            </div>

            {/* Column Headers */}
            <div className="px-4 py-2 bg-[#0a0e27] border-b border-gray-800 grid grid-cols-3 gap-2 text-xs text-gray-500">
                <div className="text-left">Price (USDT)</div>
                <div className="text-right">Amount</div>
                <div className="text-right">Total</div>
            </div>

            {/* Order Book Data */}
            <div className="flex-1 overflow-y-auto">
                {/* Asks (Sell orders - Red) */}
                <div className="flex flex-col-reverse">
                    {orderBook?.asks.slice(0, 10).map((item: any, idx) => {
                        const price = item.price;
                        const amount = item.quantity;
                        const total = price * amount;
                        const percentage = (amount / maxAskVolume) * 100;

                        return (
                            <div key={`ask-${idx}`} className="relative px-4 py-1 hover:bg-red-500/5">
                                <div
                                    className="absolute left-0 top-0 h-full bg-red-500/10"
                                    style={{ width: `${percentage}%` }}
                                />
                                <div className="relative grid grid-cols-3 gap-2 text-xs font-mono">
                                    <span className="text-red-400">{price.toFixed(2)}</span>
                                    <span className="text-right text-gray-300">{amount.toFixed(4)}</span>
                                    <span className="text-right text-gray-400">{total.toFixed(2)}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Spread */}
                {orderBook && orderBook.bids.length > 0 && orderBook.asks.length > 0 && (
                    <div className="px-4 py-2 bg-gray-800/50 border-y border-gray-700">
                        <div className="flex justify-between items-center text-xs">
                            <span className="text-gray-400">Spread</span>
                            <span className="text-yellow-400 font-mono">
                                {((orderBook.asks[0] as any).price - (orderBook.bids[0] as any).price).toFixed(2)}
                            </span>
                        </div>
                    </div>
                )}

                {/* Bids (Buy orders - Green) */}
                <div>
                    {orderBook?.bids.slice(0, 10).map((item: any, idx) => {
                        const price = item.price;
                        const amount = item.quantity;
                        const total = price * amount;
                        const percentage = (amount / maxBidVolume) * 100;

                        return (
                            <div key={`bid-${idx}`} className="relative px-4 py-1 hover:bg-green-500/5">
                                <div
                                    className="absolute left-0 top-0 h-full bg-green-500/10"
                                    style={{ width: `${percentage}%` }}
                                />
                                <div className="relative grid grid-cols-3 gap-2 text-xs font-mono">
                                    <span className="text-green-400">{price.toFixed(2)}</span>
                                    <span className="text-right text-gray-300">{amount.toFixed(4)}</span>
                                    <span className="text-right text-gray-400">{total.toFixed(2)}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {!orderBook && !loading && (
                <MiniEmptyState
                    text="Order book not available"
                    icon={Database}
                />
            )}
        </div>
    );
}
