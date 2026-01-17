import React, { useState } from 'react';
import { Sliders, Shield, Eye, Activity, Brain, Rocket, Lock, Globe } from 'lucide-react';

interface AgentConfig {
    active: boolean;
    weight: number;
}

interface AgentState {
    scout: AgentConfig;
    hunter: AgentConfig;
    analyst: AgentConfig;
    defender: AgentConfig;
    strategist: AgentConfig;
    sentinel: AgentConfig;
}

interface AgentSidebarProps {
    config: AgentState;
    onChange: (key: string, field: 'active' | 'weight', value: any) => void;
    onCommit: (key: string, field: 'active' | 'weight', value: any) => void;
    isPremium: boolean;
    onUpgrade: () => void;
}

const AgentSidebar: React.FC<AgentSidebarProps> = ({ config, onChange, onCommit, isPremium, onUpgrade }) => {

    const renderControl = (key: string, label: string, icon: React.ReactNode, color: string, description: string, locked = false) => {
        // @ts-ignore
        const state = config[key] as AgentConfig;

        return (
            <div className={`p-4 rounded-lg bg-slate-900/50 border ${state.active ? 'border-slate-700' : 'border-transparent opacity-50'} transition-all mb-4 relative overflow-hidden group`}>
                {locked && (
                    <div className="absolute inset-0 bg-black/60 z-10 flex items-center justify-center backdrop-blur-[1px]">
                        <button
                            onClick={onUpgrade}
                            className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold py-1 px-3 rounded flex items-center gap-1 transition-transform hover:scale-105"
                        >
                            <Lock size={10} /> UPGRADE
                        </button>
                    </div>
                )}

                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div className={`p-1.5 rounded bg-slate-800 ${color}`}>
                            {icon}
                        </div>
                        <div>
                            <div className="text-xs font-bold text-slate-200 uppercase tracking-wider">{label}</div>
                            <div className="text-[10px] text-slate-500">{description}</div>
                        </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                        <input
                            type="checkbox"
                            checked={state.active}
                            onChange={(e) => {
                                const isActive = e.target.checked;
                                // Update local state for immediate UI feedback
                                onChange(key, 'active', isActive);
                                onChange(key, 'weight', isActive ? 1.0 : 0.0);

                                // SINGLE network commit to prevent race conditions.
                                // page.tsx handler will ensure weight aligns with active status.
                                onCommit(key, 'active', isActive);
                            }}
                            className="sr-only peer"
                            disabled={locked}
                        />
                        <div className="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                </div>
            </div>
        );
    };

    return (
        <div className="h-auto bg-[#0b1120] border-r border-slate-700/50 p-4 flex flex-col">
            <div className="mb-6 pb-4 border-b border-slate-700/50">
                <h2 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
                    <Sliders size={16} className="text-blue-500" />
                    SWARM CONTROL
                </h2>
                <p className="text-xs text-slate-500">Configure neural weights & override agent authority.</p>
            </div>

            <div className="scrollbar-hide">
                {renderControl('scout', 'SCOUT AGENT', <Activity size={14} />, 'text-cyan-400', 'Math & Volatility (Z-Score)')}
                {renderControl('hunter', 'HUNTER AGENT', <Eye size={14} />, 'text-amber-400', 'Orderbook & liquidity hunting')}
                {renderControl('analyst', 'ANALYST AGENT', <Brain size={14} />, 'text-purple-400', 'Narrative & Sentiment (Vertex AI)')}
                {renderControl('sentinel', 'SENTINEL AGENT', <Globe size={14} />, 'text-pink-400', 'Global News & Social Sentiment')}

                <div className="pt-4 border-t border-slate-800 mt-4">
                    <div className="text-[10px] text-slate-500 font-bold mb-2 uppercase tracking-widest pl-1">PREMIUM AGENTS</div>
                    {renderControl('defender', 'DEFENDER AGENT', <Shield size={14} />, 'text-red-400', 'Risk Management & Veto Power', !isPremium)}
                    {renderControl('strategist', 'STRATEGIST', <Rocket size={14} />, 'text-indigo-400', 'Macro Trends (BigQuery)', !isPremium)}
                </div>
            </div>

            {!isPremium && (
                <div className="mt-4 p-4 rounded-xl bg-gradient-to-br from-indigo-900/50 to-purple-900/50 border border-indigo-500/30 text-center">
                    <h3 className="text-white font-bold text-sm mb-1">Scale to Institutional</h3>
                    <p className="text-[10px] text-indigo-200 mb-3">Unlock Strategist Agent, PDF Reports & API Access.</p>
                    <button onClick={onUpgrade} className="w-full py-2 bg-indigo-500 hover:bg-indigo-400 text-white text-xs font-bold rounded transition-colors shadow-lg shadow-indigo-500/20">
                        UPGRADE PLAN
                    </button>
                </div>
            )}
        </div>
    );
};

export default AgentSidebar;
