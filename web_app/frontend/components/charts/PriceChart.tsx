/**
 * TURBO-PLAN X Professional Chart - TradingView Lightweight Charts v4
 * Same engine as Bybit/TradingView
 */

'use client';

import { useEffect, useRef, useState } from 'react';
import { useOHLCV } from '@/lib/hooks';

interface PriceChartProps {
    symbol: string;
    timeframe?: string;
    limit?: number;
    type?: 'candlestick' | 'area' | 'line';
    showHeader?: boolean;
    showVolume?: boolean;
}

export function PriceChart({
    symbol,
    timeframe = '1h',
    limit = 200,
    type = 'candlestick',
    showHeader = true,
    showVolume = true
}: PriceChartProps) {
    const { data, loading, error } = useOHLCV(symbol, timeframe, limit);
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<any>(null);
    const [isClient, setIsClient] = useState(false);

    // Check if we're on client side
    useEffect(() => {
        setIsClient(true);
    }, []);

    // DEBUG STATE
    const [chartInstance, setChartInstance] = useState<any>(null);

    // Initialize and update chart
    const seriesRef = useRef<any>(null);
    // const volumeSeriesRef = useRef<any>(null); // Removed as per new code

    useEffect(() => {
        console.log("[PriceChart] MOUNTED", { symbol, timeframe, container: chartContainerRef.current });

        if (!isClient || !chartContainerRef.current) {
            console.warn("[PriceChart] Container not ready or SSR");
            return;
        }

        let chart: any = null;
        let isMounted = true;

        import('lightweight-charts').then((LightweightCharts) => {
            if (!isMounted) return;
            console.log("[PriceChart] Lib Loaded");

            const { createChart, ColorType, CrosshairMode } = LightweightCharts;

            if (chartRef.current) {
                console.log("[PriceChart] Removing old chart");
                chartRef.current.remove();
            }

            const clientWidth = chartContainerRef.current?.clientWidth || 0;
            const clientHeight = chartContainerRef.current?.clientHeight || 400; // Fallback height
            console.log("[PriceChart] Creating chart with dims:", clientWidth, clientHeight);

            chart = createChart(chartContainerRef.current!, {
                layout: {
                    background: { type: ColorType.Solid, color: '#0f1729' },
                    textColor: '#9ca3af',
                },
                grid: {
                    vertLines: { color: '#1e293b' },
                    horzLines: { color: '#1e293b' },
                },
                crosshair: {
                    mode: CrosshairMode.Normal,
                    vertLine: {
                        color: '#6366f1',
                        width: 1,
                        style: 2,
                        labelBackgroundColor: '#6366f1',
                    },
                    horzLine: {
                        color: '#6366f1',
                        width: 1,
                        style: 2,
                        labelBackgroundColor: '#6366f1',
                    },
                },
                rightPriceScale: {
                    borderColor: '#1e293b',
                    scaleMargins: {
                        top: 0.1,
                        bottom: 0.1, // Adjusted as showVolume is no longer handled here
                    },
                },
                timeScale: {
                    borderColor: '#1e293b',
                    timeVisible: true,
                    secondsVisible: false,
                    rightOffset: 5,
                    barSpacing: 8,
                    minBarSpacing: 2,
                },
                width: clientWidth,
                height: clientHeight || 400, // Force height if 0
            });

            // Basic Series Init
            let series: any;
            if (type === 'candlestick') {
                series = chart.addCandlestickSeries({
                    upColor: '#10b981', downColor: '#ef4444',
                    borderUpColor: '#10b981', borderDownColor: '#ef4444',
                    wickUpColor: '#10b981', wickDownColor: '#ef4444',
                });
            } else if (type === 'area') { // Re-added area series logic
                series = chart.addAreaSeries({
                    topColor: 'rgba(16, 185, 129, 0.4)',
                    bottomColor: 'rgba(16, 185, 129, 0.0)',
                    lineColor: '#10b981',
                    lineWidth: 2,
                });
            } else {
                series = chart.addLineSeries({ color: '#10b981' });
            }
            seriesRef.current = series;
            chartRef.current = chart;

            // Volume series initialization removed as per new code, but keeping the original logic for now
            // if (showVolume) {
            //     const volumeSeries = chart.addHistogramSeries({
            //         color: '#26a69a',
            //         priceFormat: { type: 'volume' },
            //         priceScaleId: '',
            //     });
            //     chart.priceScale('').applyOptions({
            //         scaleMargins: { top: 0.85, bottom: 0 },
            //     });
            //     volumeSeriesRef.current = volumeSeries;
            // }


            if (isMounted) setChartInstance(chart);

            // Simple Resize Listener
            const handleResize = () => {
                if (chartContainerRef.current && chart) {
                    chart.applyOptions({
                        width: chartContainerRef.current.clientWidth,
                        height: chartContainerRef.current.clientHeight || 400
                    });
                }
            };
            window.addEventListener('resize', handleResize);

            // Force one resize trigger
            setTimeout(handleResize, 100);

            // Cleanup for listener
            return () => window.removeEventListener('resize', handleResize);
        });

        return () => {
            console.log("[PriceChart] UNMOUNT");
            isMounted = false;
            if (chartRef.current) {
                chartRef.current.remove();
                chartRef.current = null;
            }
            setChartInstance(null);
            seriesRef.current = null; // Added cleanup for seriesRef
            // volumeSeriesRef.current = null; // Removed as per new code
        };
    }, [isClient, type, loading, error, !!data]); // CRITICAL FIX: Re-run when DOM becomes available

    // Data Effect (No changes needed logic-wise, but keep it clean)
    useEffect(() => {
        if (!chartInstance || !seriesRef.current) return;

        if (!data || data.candles.length === 0) return;

        const rawCandles = data.candles.map(c => ({
            time: Math.floor(c.time / 1000) as any,
            open: c.open, high: c.high, low: c.low, close: c.close
        })).sort((a: any, b: any) => a.time - b.time);

        // Dedupe
        const unique = new Map();
        rawCandles.forEach(c => unique.set(c.time, c));
        const finalData = Array.from(unique.values());

        seriesRef.current.setData(finalData);

        // Volume logic restoration can be done here if needed

        // Fit content if newly initialized
        try {
            const logicalRange = chartInstance.timeScale().getVisibleLogicalRange();
            if (!logicalRange) {
                chartInstance.timeScale().fitContent();
            }
        } catch (e) { }

    }, [data, chartInstance]);

    // Loading state
    if (loading) {
        return (
            <div className="w-full h-[400px] flex items-center justify-center bg-[#0f1729] rounded-xl border border-cyan-500/20">
                <div className="flex flex-col items-center gap-3">
                    <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
                    <div className="text-cyan-400 text-sm">Loading {symbol}...</div>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="w-full h-[400px] flex items-center justify-center bg-[#0f1729] rounded-xl border border-red-500/20">
                <div className="text-center">
                    <div className="text-red-400 text-lg mb-2">⚠️ Error</div>
                    <div className="text-gray-400 text-sm">{error}</div>
                </div>
            </div>
        );
    }

    // No data state
    if (!data || data.candles.length === 0) {
        return (
            <div className="w-full h-[400px] flex items-center justify-center bg-[#0f1729] rounded-xl border border-yellow-500/20">
                <div className="text-center">
                    <div className="text-yellow-400 text-lg mb-2">📊 No Data</div>
                    <div className="text-gray-400 text-sm">No data for {symbol} ({timeframe})</div>
                </div>
            </div>
        );
    }

    // Calculate stats
    const lastCandle = data.candles[data.candles.length - 1];
    const firstCandle = data.candles[0];
    const lastPrice = lastCandle?.close || 0;
    const firstPrice = firstCandle?.close || 0;
    const priceChange = lastPrice - firstPrice;
    const priceChangePercent = firstPrice > 0 ? (priceChange / firstPrice) * 100 : 0;
    const isPositive = priceChange >= 0;
    const highPrice = Math.max(...data.candles.map(c => c.high));
    const lowPrice = Math.min(...data.candles.map(c => c.low));

    return (
        <div className="w-full">
            {showHeader && (
                <div className="mb-3 flex justify-between items-start">
                    <div>
                        <h3 className="text-lg font-bold text-white mb-1">{symbol}</h3>
                        <div className="flex items-baseline gap-2">
                            <span className="text-xl font-mono text-white">
                                ${lastPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                            <span className={`text-sm font-semibold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                                {isPositive ? '+' : ''}{priceChangePercent.toFixed(2)}%
                            </span>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-xs text-gray-500">{data.count} pts</div>
                    </div>
                </div>
            )}

            {/* TradingView Chart Container */}
            <div
                ref={chartContainerRef}
                className="w-full rounded-lg overflow-hidden"
                style={{ height: '400px' }}
            />

            {showHeader && (
                <div className="grid grid-cols-4 gap-3 mt-3 pt-3 border-t border-gray-700/50">
                    <div>
                        <div className="text-xs text-gray-500">High</div>
                        <div className="text-sm font-mono text-green-400">${highPrice.toFixed(2)}</div>
                    </div>
                    <div>
                        <div className="text-xs text-gray-500">Low</div>
                        <div className="text-sm font-mono text-red-400">${lowPrice.toFixed(2)}</div>
                    </div>
                    <div>
                        <div className="text-xs text-gray-500">Change</div>
                        <div className={`text-sm font-mono ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                            ${Math.abs(priceChange).toFixed(2)}
                        </div>
                    </div>
                    <div>
                        <div className="text-xs text-gray-500">Range</div>
                        <div className="text-sm font-mono text-cyan-400">${(highPrice - lowPrice).toFixed(2)}</div>
                    </div>
                </div>
            )}
        </div>
    );
}
