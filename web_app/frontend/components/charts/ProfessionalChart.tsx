"use client";

import React, { useEffect, useRef, useState, useCallback } from 'react';
import {
    createChart,
    ColorType,
    CrosshairMode,
    IChartApi,
    ISeriesApi,
    UTCTimestamp,
    LineStyle,
    IPriceLine
} from 'lightweight-charts';
import { ChartToolbar, ChartTopBar, DrawingTool } from './ChartToolbar';
import { Activity, X } from 'lucide-react';

// --- Interfaces ---
interface OHLC {
    time: UTCTimestamp | number;
    open: number;
    high: number;
    low: number;
    close: number;
    volume?: number;
}

interface Drawing {
    id: string;
    type: DrawingTool;
    price: number;
    time?: UTCTimestamp;
}

// --- Helper: Indicators Calculation ---
const calculateSMA = (data: OHLC[], count: number) => {
    const avg = (data: OHLC[]) => data.reduce((a, b) => a + b.close, 0) / data.length;
    const result = [];
    for (let i = count - 1; i < data.length; i++) {
        const val = avg(data.slice(i - count + 1, i + 1));
        result.push({ time: data[i].time, value: val });
    }
    return result;
};

const calculateRSI = (data: OHLC[], count: number = 14) => {
    // Basic RSI implementation
    if (data.length < count) return [];
    let gains = 0;
    let losses = 0;

    // First run
    for (let i = 1; i <= count; i++) {
        const change = data[i].close - data[i - 1].close;
        if (change > 0) gains += change;
        else losses += Math.abs(change);
    }

    let avgGain = gains / count;
    let avgLoss = losses / count;

    const result = [];

    for (let i = count + 1; i < data.length; i++) {
        const change = data[i].close - data[i - 1].close;
        let gain = change > 0 ? change : 0;
        let loss = change < 0 ? Math.abs(change) : 0;

        avgGain = (avgGain * (count - 1) + gain) / count;
        avgLoss = (avgLoss * (count - 1) + loss) / count;

        const rs = avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));

        result.push({ time: data[i].time, value: rsi });
    }
    return result;
};

export const ProfessionalChart: React.FC<any> = ({
    symbol = 'BTC/USDT',
    theme = 'dark'
}) => {
    // --- Refs ---
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);

    // Series Refs
    const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
    const areaSeriesRef = useRef<ISeriesApi<"Area"> | null>(null);
    const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);

    // Indicators Refs
    const ma20SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
    const ma50SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
    const ma200SeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
    const rsiSeriesRef = useRef<ISeriesApi<"Line"> | null>(null); // Ideally creates separate pane, but simplifying

    const wsRef = useRef<WebSocket | null>(null);
    const chartDataRef = useRef<OHLC[]>([]);

    // --- State ---
    const [interval, setInterval] = useState('1h');
    const [currentPrice, setCurrentPrice] = useState<number | null>(null);
    const [chartType, setChartType] = useState<'candle' | 'area'>('candle');
    const [isLoading, setIsLoading] = useState(true);

    // UI State
    const [activeTool, setActiveTool] = useState<DrawingTool>('cursor');
    const activeToolRef = useRef<DrawingTool>('cursor'); // Ref to avoid closure staleness
    const priceLinesRef = useRef<IPriceLine[]>([]);

    useEffect(() => {
        activeToolRef.current = activeTool;
    }, [activeTool]);


    const [showIndicatorsMenu, setShowIndicatorsMenu] = useState(false);
    const [showSettingsModal, setShowSettingsModal] = useState(false);

    const [indicators, setIndicators] = useState({
        ma20: true,
        ma50: true,
        ma200: true,
        rsi: false
    });

    const [chartColors, setChartColors] = useState({
        upColor: '#26a69a',
        downColor: '#ef5350',
        bg: '#0a0a0a',
        grid: '#1e222d'
    });

    // --- Helper: Parse Interval ---
    const parseInterval = (intv: string): number => {
        const num = parseInt(intv);
        if (intv.includes('m')) return num * 60;
        if (intv.includes('h')) return num * 3600;
        if (intv.includes('d')) return num * 86400;
        if (intv.includes('w')) return num * 604800;
        return 3600;
    };

    // --- 1. Chart Initialization ---
    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Cleanup
        if (chartRef.current) {
            chartRef.current.remove();
            chartRef.current = null;
        }

        // Create Chart
        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: chartColors.bg },
                textColor: '#94a3b8',
            },
            grid: {
                vertLines: { color: chartColors.grid },
                horzLines: { color: chartColors.grid },
            },
            crosshair: { mode: CrosshairMode.Normal },
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
                borderColor: '#334155',
            },
            rightPriceScale: {
                borderColor: '#334155',
                autoScale: true,
                scaleMargins: {
                    top: 0.1,
                    bottom: 0.25, // Reserved for Volume
                },
            },
            width: chartContainerRef.current.clientWidth,
            height: chartContainerRef.current.clientHeight,
        });

        // --- 2. Volume Series (Separated) ---
        // Setting priceScaleId to empty string '' makes it an overlay.
        // Then we configure that overlay's scale margins to keep it at the bottom 20%.
        const volumeSeries = chart.addHistogramSeries({
            color: '#26a69a',
            priceFormat: { type: 'volume' },
            priceScaleId: '', // Overlay
        });

        volumeSeries.priceScale().applyOptions({
            scaleMargins: {
                top: 0.8, // Top 80% is free for price
                bottom: 0,
            },
        });
        volumeSeriesRef.current = volumeSeries;

        // --- 3. Indicators (MA) ---
        // We add them first so they stay behind candles? Or after? Usually behind.
        const ma20 = chart.addLineSeries({ color: '#fbbf24', lineWidth: 1, crosshairMarkerVisible: false, visible: indicators.ma20 });
        const ma50 = chart.addLineSeries({ color: '#3b82f6', lineWidth: 2, crosshairMarkerVisible: false, visible: indicators.ma50 });
        const ma200 = chart.addLineSeries({ color: '#a855f7', lineWidth: 2, crosshairMarkerVisible: false, visible: indicators.ma200 });

        ma20SeriesRef.current = ma20;
        ma50SeriesRef.current = ma50;
        ma200SeriesRef.current = ma200;

        chartRef.current = chart;

        // Re-Apply Resize Logic
        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                    height: chartContainerRef.current.clientHeight
                });
            }
        };
        window.addEventListener('resize', handleResize);

        // Click Handler (Drawing) - Uses Ref to get latest tool
        chart.subscribeClick((param: any) => {
            const currentTool = activeToolRef.current;

            if (currentTool !== 'cursor' && param.point && param.time) {
                const targetSeries = candlestickSeriesRef.current || areaSeriesRef.current;
                if (targetSeries) {
                    const price = targetSeries.coordinateToPrice(param.point.y);
                    if (price) {
                        if (currentTool === 'horizontal_line') {
                            const line = targetSeries.createPriceLine({
                                price: price,
                                color: '#2962ff',
                                lineWidth: 2,
                                lineStyle: LineStyle.Solid,
                                axisLabelVisible: true,
                                title: 'H-Line',
                            });
                            priceLinesRef.current.push(line);
                            setActiveTool('cursor'); // Reset tool
                        }
                        // Add other tools here logic if needed
                    }
                }
            }
        });

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, []);

    // --- 2. Chart Type Management (Switch Logic) ---
    useEffect(() => {
        if (!chartRef.current) return;

        // Remove existing main series
        if (candlestickSeriesRef.current) {
            chartRef.current.removeSeries(candlestickSeriesRef.current);
            candlestickSeriesRef.current = null;
        }
        if (areaSeriesRef.current) {
            chartRef.current.removeSeries(areaSeriesRef.current);
            areaSeriesRef.current = null;
        }

        // Add new series type
        if (chartType === 'candle') {
            const series = chartRef.current.addCandlestickSeries({
                upColor: chartColors.upColor,
                downColor: chartColors.downColor,
                borderVisible: false,
                wickUpColor: chartColors.upColor,
                wickDownColor: chartColors.downColor,
            });
            candlestickSeriesRef.current = series;
        } else {
            const series = chartRef.current.addAreaSeries({
                lineColor: '#26a69a',
                topColor: 'rgba(38, 166, 154, 0.4)',
                bottomColor: 'rgba(38, 166, 154, 0.0)',
                lineWidth: 2,
            });
            areaSeriesRef.current = series;
        }

        // Re-populate data if available
        if (chartDataRef.current.length > 0) {
            refreshChartData(chartDataRef.current);
        }

    }, [chartType, chartColors]); // Re-run if type or colors change

    // --- 3. Indicators Visibility Management ---
    useEffect(() => {
        ma20SeriesRef.current?.applyOptions({ visible: indicators.ma20 });
        ma50SeriesRef.current?.applyOptions({ visible: indicators.ma50 });
        ma200SeriesRef.current?.applyOptions({ visible: indicators.ma200 });
        // RSI Logic would require separate pane or removal/addition, skipped for brevity
    }, [indicators]);

    // --- 4. Data Fetching ---
    const fetchData = useCallback(async () => {
        setIsLoading(true);
        try {
            const t = Date.now();
            const res = await fetch(`/api/v1/market/ohlcv/${symbol.replace('/', '')}?timeframe=${interval}&limit=1000&_t=${t}`);
            const data = await res.json();

            if (data.candles && Array.isArray(data.candles)) {
                // Parse & Sort
                let cleanData = data.candles
                    .map((c: any) => ({
                        time: (c.time / 1000) as UTCTimestamp,
                        open: c.open,
                        high: c.high,
                        low: c.low,
                        close: c.close,
                        volume: c.volume
                    }))
                    .sort((a: any, b: any) => (a.time as number) - (b.time as number));

                // Deduplicate
                const uniqueData: OHLC[] = [];
                const seen = new Set();
                cleanData.forEach((c: OHLC) => {
                    if (!seen.has(c.time)) {
                        seen.add(c.time);
                        uniqueData.push(c);
                    }
                });

                chartDataRef.current = uniqueData;
                refreshChartData(uniqueData);
            }
        } catch (e) {
            console.error("Fetch failed", e);
        } finally {
            setIsLoading(false);
        }
    }, [symbol, interval]);

    useEffect(() => { fetchData(); }, [fetchData]);

    const refreshChartData = (data: OHLC[]) => {
        if (!data || data.length === 0) return;

        // Set Main Series
        if (candlestickSeriesRef.current) {
            candlestickSeriesRef.current.setData(data as any);
        } else if (areaSeriesRef.current) {
            areaSeriesRef.current.setData(data.map(d => ({ time: d.time, value: d.close })) as any);
        }

        // Set Volume
        volumeSeriesRef.current?.setData(data.map(c => ({
            time: c.time,
            value: c.volume || 0,
            color: c.close >= c.open ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'
        })) as any);

        // Update Indicators
        const ma20Data = calculateSMA(data, 20);
        const ma50Data = calculateSMA(data, 50);
        const ma200Data = calculateSMA(data, 200);

        ma20SeriesRef.current?.setData(ma20Data as any);
        ma50SeriesRef.current?.setData(ma50Data as any);
        ma200SeriesRef.current?.setData(ma200Data as any);
    };

    // --- 5. WebSocket Updates ---
    const updateCurrentInRef = (price: number, timestamp: number) => {
        if (chartDataRef.current.length === 0) return;

        const intervalSeconds = parseInterval(interval);
        const incomingSeconds = Math.floor(timestamp / 1000);
        const bucketStart = incomingSeconds - (incomingSeconds % intervalSeconds);

        const lastCandle = chartDataRef.current[chartDataRef.current.length - 1];
        const lastTime = lastCandle.time as number;

        let updatedCandle: OHLC;

        if (bucketStart > lastTime) {
            // New Candle
            const smoothOpen = lastCandle.close;
            updatedCandle = {
                time: bucketStart as UTCTimestamp,
                open: smoothOpen,
                high: Math.max(smoothOpen, price),
                low: Math.min(smoothOpen, price),
                close: price,
                volume: 0
            };
            chartDataRef.current.push(updatedCandle);
        } else {
            // Update Existing
            updatedCandle = {
                ...lastCandle,
                high: Math.max(lastCandle.high, price),
                low: Math.min(lastCandle.low, price),
                close: price,
                volume: (lastCandle.volume || 0)
            };
            chartDataRef.current[chartDataRef.current.length - 1] = updatedCandle;
        }

        // Update active series
        if (candlestickSeriesRef.current) {
            candlestickSeriesRef.current.update(updatedCandle as any);
        } else if (areaSeriesRef.current) {
            areaSeriesRef.current.update({ time: updatedCandle.time, value: updatedCandle.close } as any);
        }
    };

    useEffect(() => {
        if (wsRef.current) wsRef.current.close();
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.hostname;
        const wsUrl = `${protocol}//${host}:8000/api/v1/ws/market/${symbol.replace('/', '')}`;

        const socket = new WebSocket(wsUrl);
        socket.onmessage = (event) => {
            try {
                let msg = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                if (msg && msg.type === 'update' && msg.data) {
                    let tickerData = msg.data;
                    if (typeof tickerData === 'string') tickerData = JSON.parse(tickerData);

                    const price = tickerData.last || tickerData.price;
                    const ts = tickerData.timestamp;

                    if (price && ts) {
                        setCurrentPrice(price);
                        if (chartDataRef.current.length > 0) updateCurrentInRef(price, ts);
                    }
                }
            } catch (e) {
                console.error("WS Error", e);
            }
        };
        wsRef.current = socket;
        return () => { if (socket.readyState === WebSocket.OPEN) socket.close(); };
    }, [symbol, interval, chartType]);
    // ^ Added chartType dep to ensure WS keeps updating correct series if we reconnect or if updateRef checks refs

    // --- 6. Interaction Handlers ---

    const toggleFullscreen = () => {
        if (!chartContainerRef.current) return;
        if (!document.fullscreenElement) {
            chartContainerRef.current.requestFullscreen().catch(err => console.error(err));
        } else {
            document.exitFullscreen();
        }
    };

    return (
        <div className="flex flex-col w-full h-[calc(100vh-120px)] bg-[#0b0e14] text-gray-300 relative">
            {/* Top Bar */}
            <ChartTopBar
                symbol={symbol}
                currentInterval={interval}
                onIntervalChange={setInterval}
                currentPrice={currentPrice}
                chartType={chartType}
                onChartTypeChange={setChartType}
                indicators={indicators}
                onIndicatorChange={(key, val) => setIndicators(prev => ({ ...prev, [key]: val }))}
                onToggleSettings={() => setShowSettingsModal(true)}
                onToggleFullscreen={toggleFullscreen}
            />

            {/* Settings Sidebar Overlay */}
            {showSettingsModal && (
                <div className="absolute top-0 right-0 h-full w-[320px] z-50 bg-[#1e222d] border-l border-[#2a2e39] shadow-2xl transform transition-transform duration-300 ease-in-out">
                    <div className="flex justify-between items-center p-4 border-b border-[#2a2e39]">
                        <h3 className="text-white font-bold text-sm uppercase tracking-wider">Chart Configuration</h3>
                        <button
                            onClick={() => setShowSettingsModal(false)}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            <X size={20} />
                        </button>
                    </div>

                    <div className="p-6 space-y-6">
                        {/* Appearance Section */}
                        <div>
                            <h4 className="text-xs font-bold text-gray-500 uppercase mb-3">Appearance</h4>
                            <div className="space-y-4">
                                <div className="flex items-center justify-between">
                                    <label className="text-sm text-gray-300">Bullish Candle</label>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="color"
                                            value={chartColors.upColor}
                                            onChange={e => setChartColors({ ...chartColors, upColor: e.target.value })}
                                            className="w-8 h-8 rounded cursor-pointer bg-transparent border-none"
                                        />
                                        <span className="text-xs font-mono text-gray-500">{chartColors.upColor}</span>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <label className="text-sm text-gray-300">Bearish Candle</label>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="color"
                                            value={chartColors.downColor}
                                            onChange={e => setChartColors({ ...chartColors, downColor: e.target.value })}
                                            className="w-8 h-8 rounded cursor-pointer bg-transparent border-none"
                                        />
                                        <span className="text-xs font-mono text-gray-500">{chartColors.downColor}</span>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <label className="text-sm text-gray-300">Grid Lines</label>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="color"
                                            value={chartColors.grid}
                                            onChange={e => setChartColors({ ...chartColors, grid: e.target.value })}
                                            className="w-8 h-8 rounded cursor-pointer bg-transparent border-none"
                                        />
                                        <span className="text-xs font-mono text-gray-500">{chartColors.grid}</span>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <label className="text-sm text-gray-300">Background</label>
                                    <div className="flex items-center gap-2">
                                        <input
                                            type="color"
                                            value={chartColors.bg}
                                            onChange={e => setChartColors({ ...chartColors, bg: e.target.value })}
                                            className="w-8 h-8 rounded cursor-pointer bg-transparent border-none"
                                        />
                                        <span className="text-xs font-mono text-gray-500">{chartColors.bg}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Info */}
                        <div className="p-4 bg-[#2a2e39]/50 rounded text-xs text-gray-400 border border-[#2a2e39]">
                            <p>Customize your viewing experience. Changes are applied immediately to the local chart instance.</p>
                        </div>
                    </div>
                </div>
            )}

            <div className="flex flex-1 overflow-hidden relative">
                {/* Tools */}
                <ChartToolbar
                    activeTool={activeTool}
                    onToolChange={setActiveTool}
                    onClearAll={() => {
                        priceLinesRef.current.forEach(line => {
                            candlestickSeriesRef.current?.removePriceLine(line);
                            areaSeriesRef.current?.removePriceLine(line);
                        });
                        priceLinesRef.current = [];
                        setActiveTool('cursor');
                    }}
                    currentInterval={interval}
                    onIntervalChange={setInterval}
                />

                {/* Chart Area */}
                <div className="flex-1 relative bg-[#0a0a0a]" ref={chartContainerRef}>
                    {isLoading && (
                        <div className="absolute inset-0 flex items-center justify-center bg-black/60 z-50 backdrop-blur-sm pointer-events-none">
                            <div className="flex items-center gap-3">
                                <Activity className="w-6 h-6 text-[#26a69a] animate-spin" />
                                <span className="text-sm font-mono text-[#26a69a] tracking-widest">LOADING MARKET DATA...</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
