'use client';
import React from 'react';

import {
    MousePointer2,
    TrendingUp,
    Minus,
    Type,
    PenTool,
    Trash2,
    Maximize2,
    Settings,
    MoreVertical,
    Activity,
    BarChart3,
    History
} from 'lucide-react';

export type DrawingTool = 'cursor' | 'trendline' | 'horizontal_line' | 'text' | 'brush' | null;

interface ChartToolbarProps {
    activeTool: DrawingTool;
    onToolChange: (tool: DrawingTool) => void;
    onClearAll: () => void;
    currentInterval: string;
    onIntervalChange: (interval: string) => void;
    isScriptingActive?: boolean;
    onToggleScripting?: () => void;
}

const INTERVALS = [
    { label: '1m', value: '1m' },
    { label: '5m', value: '5m' },
    { label: '15m', value: '15m' },
    { label: '1h', value: '1h' },
    { label: '4h', value: '4h' },
    { label: '1D', value: '1d' },
    { label: '1W', value: '1w' },
];

export function ChartToolbar({
    activeTool,
    onToolChange,
    onClearAll,
    currentInterval,
    onIntervalChange,
    isScriptingActive,
    onToggleScripting
}: ChartToolbarProps) {

    return (
        <div className="flex flex-col h-full bg-[#1e222d] border-r border-[#2a2e39] w-14 items-center py-4 gap-4 z-20">
            {/* Main Tools */}
            <TooltipButton
                active={activeTool === 'cursor'}
                onClick={() => onToolChange('cursor')}
                icon={<MousePointer2 size={18} />}
                label="Cursor"
            />

            <div className="w-8 h-[1px] bg-[#2a2e39]" />

            <TooltipButton
                active={activeTool === 'trendline'}
                onClick={() => onToolChange('trendline')}
                icon={<TrendingUp size={18} />}
                label="Trend Line"
            />
            <TooltipButton
                active={activeTool === 'horizontal_line'}
                onClick={() => onToolChange('horizontal_line')}
                icon={<Minus size={18} />}
                label="Horizontal Line"
            />
            <TooltipButton
                active={activeTool === 'brush'}
                onClick={() => onToolChange('brush')}
                icon={<PenTool size={18} />}
                label="Brush"
            />
            <TooltipButton
                active={activeTool === 'text'}
                onClick={() => onToolChange('text')}
                icon={<Type size={18} />}
                label="Text"
            />

            <div className="w-8 h-[1px] bg-[#2a2e39]" />

            <TooltipButton
                active={false}
                onClick={onClearAll}
                icon={<Trash2 size={18} className="text-red-400" />}
                label="Clear All"
            />
        </div>
    );
}

// Top Bar with Timeframes and Indicators
export function ChartTopBar({
    symbol,
    currentInterval,
    onIntervalChange,
    currentPrice,
    chartType,
    onChartTypeChange,
    indicators,
    onIndicatorChange,
    onToggleSettings,
    onToggleFullscreen
}: {
    symbol: string,
    currentInterval: string,
    onIntervalChange: (i: string) => void,
    currentPrice?: number | null,
    chartType: 'candle' | 'area',
    onChartTypeChange: (type: 'candle' | 'area') => void,
    indicators: { ma20: boolean; ma50: boolean; ma200: boolean; rsi: boolean },
    onIndicatorChange: (key: string, val: boolean) => void,
    onToggleSettings: () => void,
    onToggleFullscreen: () => void
}) {
    const [showIndicators, setShowIndicators] = React.useState(false);

    return (
        <div className="flex items-center justify-between h-[60px] bg-[#1e222d] border-b border-[#2a2e39] px-4 shrink-0">
            <div className="flex items-center gap-6">
                {/* Symbol Info */}
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <span className="text-white font-bold text-xl">{symbol}</span>
                        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-green-500/20 text-green-400 border border-green-500/30 animate-pulse">
                            LIVE
                        </span>
                    </div>
                </div>

                {/* Divider */}
                <div className="h-8 w-[1px] bg-[#2a2e39]" />

                {/* Chart Type Switcher - ENHANCED VISIBILITY */}
                <div className="flex bg-[#0b0e14] rounded-lg p-1 items-center border border-[#2a2e39]">
                    <button
                        onClick={() => onChartTypeChange('candle')}
                        className={`
                            flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all
                            ${chartType === 'candle' ? 'bg-[#2a2e39] text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'}
                        `}
                    >
                        <BarChart3 size={16} className="rotate-90" />
                        <span>Candles</span>
                    </button>
                    <button
                        onClick={() => onChartTypeChange('area')}
                        className={`
                            flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all
                            ${chartType === 'area' ? 'bg-[#2a2e39] text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'}
                        `}
                    >
                        <Activity size={16} />
                        <span>Mountain</span>
                    </button>
                </div>

                {/* Divider */}
                <div className="h-8 w-[1px] bg-[#2a2e39]" />

                {/* Timeframes */}
                <div className="flex items-center gap-1 bg-[#0b0e14] p-1 rounded-lg border border-[#2a2e39]">
                    {INTERVALS.map((tf) => (
                        <button
                            key={tf.value}
                            onClick={() => onIntervalChange(tf.value)}
                            className={`
                                px-2.5 py-1 text-xs font-medium rounded transition-colors
                                ${currentInterval === tf.value ? 'text-[#2962ff] bg-[#2962ff]/10' : 'text-gray-400 hover:text-white'}
                            `}
                        >
                            {tf.label}
                        </button>
                    ))}
                </div>

                {/* Divider */}
                <div className="h-8 w-[1px] bg-[#2a2e39]" />

                {/* Indicators Button with Dropdown */}
                <div className="relative">
                    <button
                        onClick={() => setShowIndicators(!showIndicators)}
                        className={`
                            flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-lg transition-colors border
                            ${showIndicators ? 'bg-[#2a2e39] text-white border-[#334155]' : 'text-gray-300 hover:text-white border-transparent hover:bg-[#2a2e39]'}
                        `}
                    >
                        <Activity size={18} />
                        <span>Indicators</span>
                    </button>

                    {/* DROPDOWN MENU - Positioned Absolute under the button */}
                    {showIndicators && (
                        <div className="absolute top-full left-0 mt-2 z-50 bg-[#1e222d] border border-[#2a2e39] rounded-lg shadow-xl w-48 p-2 flex flex-col gap-1">
                            <h4 className="text-[10px] uppercase text-gray-500 font-bold px-2 py-1 mb-1">Overlays</h4>

                            <IndicatorToggle
                                label="MA 20 (Yellow)"
                                active={indicators.ma20}
                                onClick={() => onIndicatorChange('ma20', !indicators.ma20)}
                            />
                            <IndicatorToggle
                                label="MA 50 (Blue)"
                                active={indicators.ma50}
                                onClick={() => onIndicatorChange('ma50', !indicators.ma50)}
                            />
                            <IndicatorToggle
                                label="MA 200 (Purple)"
                                active={indicators.ma200}
                                onClick={() => onIndicatorChange('ma200', !indicators.ma200)}
                            />

                            <div className="h-[1px] bg-[#2a2e39] my-1" />
                            <h4 className="text-[10px] uppercase text-gray-500 font-bold px-2 py-1 mb-1">Oscillators</h4>
                            <IndicatorToggle
                                label="RSI (14)"
                                active={indicators.rsi}
                                onClick={() => onIndicatorChange('rsi', !indicators.rsi)}
                            />
                        </div>
                    )}
                </div>
            </div>

            <div className="flex items-center gap-2">
                {/* Live Price Display */}
                {currentPrice && (
                    <div className="flex flex-col items-end mr-4">
                        <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Bitcoin Price</span>
                        <span className="text-lg font-mono font-black text-[#26a69a]">
                            ${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </span>
                    </div>
                )}
                <div className="h-8 w-[1px] bg-[#2a2e39] mr-2" />

                <button
                    onClick={onToggleSettings}
                    className="p-2 text-gray-400 hover:text-white hover:bg-[#2a2e39] rounded-lg transition-colors"
                >
                    <Settings size={20} />
                </button>
                <button
                    onClick={onToggleFullscreen}
                    className="p-2 text-gray-400 hover:text-white hover:bg-[#2a2e39] rounded-lg transition-colors"
                >
                    <Maximize2 size={20} />
                </button>
            </div>
        </div>
    )
}

function IndicatorToggle({ label, active, onClick }: { label: string, active: boolean, onClick: () => void }) {
    return (
        <button
            onClick={onClick}
            className={`
                flex items-center justify-between w-full px-2 py-1.5 rounded text-xs transition-colors
                ${active ? 'bg-[#2962ff]/10 text-[#2962ff]' : 'text-gray-400 hover:bg-[#2a2e39] hover:text-white'}
            `}
        >
            <span>{label}</span>
            <div className={`w-2 h-2 rounded-full ${active ? 'bg-[#2962ff]' : 'bg-gray-600'}`} />
        </button>
    )
}

function TooltipButton({ active, onClick, icon, label }: any) {
    return (
        <div className="group relative">
            <button
                onClick={onClick}
                className={`
                    p-2 rounded-lg transition-all duration-200
                    ${active ? 'bg-[#2962ff] text-white shadow-lg shadow-blue-900/50' : 'text-gray-400 hover:text-white hover:bg-[#2a2e39]'}
                `}
            >
                {icon}
            </button>
            {/* Tooltip */}
            <div className="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-2 py-1 bg-black border border-gray-800 rounded text-xs text-white opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
                {label}
            </div>
        </div>
    )
}
