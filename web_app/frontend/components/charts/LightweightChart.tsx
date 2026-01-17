/**
 * TradingView Lightweight Charts Adapter for TURBO-PLAN X
 * v5.x API compatible
 */

'use client';

import { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

export type ChartType = 'candlestick' | 'area' | 'line' | 'baseline';

export interface OHLCVData {
    time: number; // Unix timestamp in milliseconds
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}

interface LightweightChartProps {
    data: OHLCVData[];
    chartType?: ChartType;
    height?: number;
    showVolume?: boolean;
    autoSize?: boolean;
}

export function LightweightChart({
    data,
    chartType = 'candlestick',
    height = 400,
    showVolume = true,
    autoSize = true
}: LightweightChartProps) {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<any>(null);
    const seriesRef = useRef<any>(null);
    const volumeSeriesRef = useRef<any>(null);

    useEffect(() => {
        if (!chartContainerRef.current || data.length === 0) return;

        // Create chart with dark theme
        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { color: '#0f1729' },
                textColor: '#d1d4dc',
            },
            grid: {
                vertLines: { color: '#334155' },
                horzLines: { color: '#334155' },
            },
            width: chartContainerRef.current.clientWidth,
            height: height,
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
                borderColor: '#475569',
            },
            rightPriceScale: {
                borderColor: '#475569',
            },
            crosshair: {
                mode: 1,
                vertLine: { color: '#6366f1', width: 1, style: 3 },
                horzLine: { color: '#6366f1', width: 1, style: 3 },
            },
        });

        chartRef.current = chart;

        const firstPrice = data[0]?.close || 0;
        const lastPrice = data[data.length - 1]?.close || 0;
        const isBullish = lastPrice >= firstPrice;

        // Create series (v5.x API uses addSeries)
        let series: any;

        switch (chartType) {
            case 'candlestick':
                series = chart.addCandlestickSeries({
                    upColor: '#10b981',
                    downColor: '#ef4444',
                    borderUpColor: '#10b981',
                    borderDownColor: '#ef4444',
                    wickUpColor: '#10b981',
                    wickDownColor: '#ef4444',
                });
                series.setData(data.map(d => ({
                    time: Math.floor(d.time / 1000),
                    open: d.open,
                    high: d.high,
                    low: d.low,
                    close: d.close,
                })));
                break;

            case 'area':
                series = chart.addAreaSeries({
                    topColor: isBullish ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)',
                    bottomColor: isBullish ? 'rgba(16, 185, 129, 0.0)' : 'rgba(239, 68, 68, 0.0)',
                    lineColor: isBullish ? '#10b981' : '#ef4444',
                    lineWidth: 2,
                });
                series.setData(data.map(d => ({
                    time: Math.floor(d.time / 1000),
                    value: d.close,
                })));
                break;

            case 'line':
                series = chart.addLineSeries({
                    color: isBullish ? '#10b981' : '#ef4444',
                    lineWidth: 2,
                });
                series.setData(data.map(d => ({
                    time: Math.floor(d.time / 1000),
                    value: d.close,
                })));
                break;

            case 'baseline':
                series = chart.addBaselineSeries({
                    topLineColor: '#10b981',
                    bottomLineColor: '#ef4444',
                    topFillColor1: 'rgba(16, 185, 129, 0.28)',
                    topFillColor2: 'rgba(16, 185, 129, 0.05)',
                    bottomFillColor1: 'rgba(239, 68, 68, 0.05)',
                    bottomFillColor2: 'rgba(239, 68, 68, 0.28)',
                    baseValue: { type: 'price', price: firstPrice },
                });
                series.setData(data.map(d => ({
                    time: Math.floor(d.time / 1000),
                    value: d.close,
                })));
                break;
        }

        seriesRef.current = series;

        // Add volume histogram
        if (showVolume) {
            const volumeSeries = chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: { type: 'volume' },
                priceScaleId: '',
            });

            volumeSeries.setData(data.map(d => ({
                time: Math.floor(d.time / 1000) as any,
                value: d.volume,
                color: d.close >= d.open ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)',
            })));

            volumeSeriesRef.current = volumeSeries;

            chart.priceScale('').applyOptions({
                scaleMargins: { top: 0.8, bottom: 0 },
            });
        }

        chart.timeScale().fitContent();

        const handleResize = () => {
            if (chartContainerRef.current && chartRef.current) {
                chartRef.current.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                });
            }
        };

        if (autoSize) {
            window.addEventListener('resize', handleResize);
        }

        return () => {
            if (autoSize) {
                window.removeEventListener('resize', handleResize);
            }
            if (chartRef.current) {
                chartRef.current.remove();
            }
        };
    }, [data, chartType, height, showVolume, autoSize]);

    return (
        <div
            ref={chartContainerRef}
            className="relative w-full"
            style={{ height: `${height}px` }}
        />
    );
}
