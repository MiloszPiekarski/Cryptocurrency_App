import React, { useState } from 'react';
import { Terminal, Shield, Eye, Activity, Brain, Lock, ExternalLink } from 'lucide-react';

interface AgentSignal {
    role: string;
    id: string;
    type?: string;
    signal: string;
    confidence: number;
    reasoning: string;
    source_data?: any;
    timestamp?: number;
}

interface EvidenceLogProps {
    signals: AgentSignal[];
    onInspect: (signal: AgentSignal) => void;
    isPremium: boolean;
}

const EvidenceLog: React.FC<EvidenceLogProps> = ({ signals, onInspect, isPremium }) => {
    return (
        <div className="bg-[#0f172a]/80 backdrop-blur-md rounded-xl border border-slate-700/50 flex flex-col h-auto shadow-2xl">
            {/* Header */}
            <div className="p-4 border-b border-slate-700/50 flex items-center justify-between bg-black/20">
                <h3 className="text-sm font-mono text-slate-300 flex items-center gap-2">
                    <Terminal size={14} className="text-emerald-400" />
                    SWARM_EVIDENCE_LOG_V2
                </h3>
                <div className="flex gap-2 text-xs">
                    <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">LIVE</span>
                    <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">{signals.length} SOURCES</span>
                </div>
            </div>

            {/* Table Header */}
            <div className="grid grid-cols-12 gap-2 p-3 text-xs font-mono text-slate-500 border-b border-slate-800 bg-slate-900/50">
                <div className="col-span-2">AGENT_ID</div>
                <div className="col-span-2">ROLE</div>
                <div className="col-span-2">SIGNAL</div>
                <div className="col-span-1">CONF</div>
                <div className="col-span-4">REASONING_PREVIEW</div>
                <div className="col-span-1 text-right">PROOF</div>
            </div>

            {/* Table Body */}
            <div className="p-2 space-y-1">
                {signals.length === 0 ? (
                    <div className="text-center py-20 text-slate-600 font-mono text-sm">
                        WAITING FOR SWARM UPLINK...
                    </div>
                ) : (
                    signals.map((sig, idx) => {
                        const isScout = sig.role === 'SCOUT';
                        const isHunter = sig.role === 'HUNTER';
                        const isAnalyst = sig.role === 'ANALYST';
                        const isDefender = sig.role === 'DEFENDER';
                        const isStrategist = sig.role === 'STRATEGIST';

                        // Premium Gate for Strategist
                        if (isStrategist && !isPremium) {
                            return (
                                <div key={idx} className="grid grid-cols-12 gap-2 p-3 rounded bg-slate-900/40 border border-slate-800/50 items-center opacity-75">
                                    <div className="col-span-2 font-mono text-xs text-purple-400 flex items-center gap-1">
                                        <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse"></span>
                                        {sig.id}
                                    </div>
                                    <div className="col-span-10 flex items-center gap-2 text-purple-300 text-xs font-mono">
                                        <Lock size={12} />
                                        <span>INSTITUTIONAL SIGNAL LOCKED. UPGRADE TO VIEW STRATEGIST REASONING.</span>
                                    </div>
                                </div>
                            )
                        }

                        return (
                            <div
                                key={idx}
                                onClick={() => onInspect(sig)}
                                className="grid grid-cols-12 gap-2 p-3 rounded hover:bg-white/5 transition-colors cursor-pointer border border-transparent hover:border-slate-600 group"
                            >
                                {/* Agent ID */}
                                <div className="col-span-2 flex items-center gap-2 font-mono text-xs text-slate-400">
                                    {isScout && <Activity size={12} className="text-cyan-400" />}
                                    {isHunter && <Eye size={12} className="text-amber-400" />}
                                    {isAnalyst && <Brain size={12} className="text-purple-400" />}
                                    {isDefender && <Shield size={12} className="text-red-400" />}
                                    {isStrategist && <div className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />}
                                    <span className="truncate">{sig.id}</span>
                                </div>

                                {/* Role */}
                                <div className="col-span-2 text-xs font-bold text-slate-300 tracking-wider">
                                    {sig.role}
                                </div>

                                {/* Signal Badge */}
                                <div className="col-span-2">
                                    <span className={`
                    text-[10px] px-2 py-0.5 rounded border font-mono font-bold
                    ${sig.signal === 'BUY' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : ''}
                    ${sig.signal === 'SELL' ? 'bg-rose-500/10 text-rose-400 border-rose-500/30' : ''}
                    ${sig.signal === 'HOLD' ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : ''}
                    ${sig.signal === 'SAFE' ? 'bg-blue-500/10 text-blue-400 border-blue-500/30' : ''}
                    ${sig.signal === 'CRITICAL' || sig.signal === 'LIQUIDATE_RISK' ? 'bg-red-600 text-white border-red-500 animate-pulse' : ''}
                  `}>
                                        {sig.signal}
                                    </span>
                                </div>

                                {/* Confidence */}
                                <div className="col-span-1 text-xs font-mono text-slate-400">
                                    {sig.confidence ? `${sig.confidence.toFixed(0)}%` : '-'}
                                </div>

                                {/* Reasoning Preview */}
                                <div className="col-span-4 text-xs text-slate-400 truncate font-mono">
                                    {sig.reasoning}
                                </div>

                                {/* Action */}
                                <div className="col-span-1 flex justify-end">
                                    <ExternalLink size={14} className="text-slate-600 group-hover:text-blue-400 transition-colors" />
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
        </div>
    );
};

export default EvidenceLog;
