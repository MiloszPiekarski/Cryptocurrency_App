"use client";

import React from 'react';
import { Brain, ArrowRight, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { NeuralCore3D } from './NeuralCore3D';

interface ConsensusHeroProps {
    summary: string;
    confidence: number;
    verdict: string;
    loading?: boolean;
}

export const ConsensusHero: React.FC<ConsensusHeroProps> = ({ summary, confidence, verdict, loading }) => {
    // Determine status & colors
    const isBullish = verdict?.includes("BUY");
    const isBearish = verdict?.includes("SELL");

    const accentColor = isBullish ? "#10b981" : isBearish ? "#f43f5e" : "#f59e0b";
    const verdictLabel = verdict || "AWAITING CONSENSUS...";

    // SVG Circular Progress logic
    const radius = 54;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (confidence / 100) * circumference;

    if (loading) {
        return (
            <div className="w-full bg-[#1a1f2e] border border-slate-800 rounded-3xl p-10 animate-pulse flex items-center justify-between shadow-2xl">
                <div className="flex-[3] flex flex-col items-center">
                    <div className="w-32 h-32 bg-slate-800 rounded-full"></div>
                </div>
                <div className="flex-[7] space-y-4 ml-10">
                    <div className="h-4 w-32 bg-slate-800 rounded"></div>
                    <div className="h-24 w-full bg-slate-800 rounded"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full bg-[#0f172a] bg-gradient-to-br from-[#1e293b]/50 to-[#0f172a] border border-slate-800/80 rounded-[2rem] p-1 shadow-[0_20px_50px_rgba(0,0,0,0.5)] relative overflow-hidden group">
            <div className="bg-[#111827] rounded-[1.9rem] p-10 flex flex-col md:flex-row items-center gap-12 relative z-10 transition-all duration-700 hover:bg-[#0f172a]">

                {/* 1. LEFT SIDE: SWARM AGREEMENT (Gauge) */}
                <div className="flex-[3] flex flex-col items-center shrink-0">
                    <div className="relative flex items-center justify-center transition-transform duration-700 hover:scale-110">
                        {/* 3D CORE ANIMATION (Small & Centered) */}
                        <div className="absolute inset-0 flex items-center justify-center z-0 opacity-40">
                            <NeuralCore3D color={accentColor} />
                        </div>

                        {/* RING GAUGE */}
                        <svg className="w-44 h-44 rotate-[-90deg] z-10">
                            <circle
                                cx="88" cy="88" r={radius}
                                fill="transparent"
                                stroke="#1e293b"
                                strokeWidth="8"
                            />
                            <circle
                                cx="88" cy="88" r={radius}
                                fill="transparent"
                                stroke={accentColor}
                                strokeWidth="12"
                                strokeDasharray={circumference}
                                strokeDashoffset={offset}
                                strokeLinecap="round"
                                className="transition-all duration-1000 ease-out drop-shadow-[0_0_8px_var(--tw-shadow-color)]"
                                style={{ stroke: accentColor } as any}
                            />
                        </svg>

                        {/* Percentage in center */}
                        <div className="absolute inset-0 flex flex-col items-center justify-center z-20">
                            <span className="text-4xl font-black text-white tracking-tighter">{confidence.toFixed(0)}%</span>
                            <span className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em] mt-1">AGREEMENT</span>
                        </div>
                    </div>

                    <div className="mt-6 flex flex-col items-center">
                        <div className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.3em] mb-2">FINAL VERDICT</div>
                        <div className={`px-6 py-2 rounded-full border border-white/5 bg-white/5 backdrop-blur-md flex items-center gap-3 transition-colors duration-500`}>
                            {isBullish ? <TrendingUp size={20} className="text-emerald-400" /> : isBearish ? <TrendingDown size={20} className="text-rose-400" /> : <Minus size={20} className="text-amber-400" />}
                            <span className={`text-lg font-black tracking-widest ${isBullish ? 'text-emerald-400' : isBearish ? 'text-rose-400' : 'text-amber-400'}`}>
                                {verdictLabel}
                            </span>
                        </div>
                    </div>
                </div>

                {/* 2. PRAWA STRONA: EXECUTIVE SUMMARY */}
                <div className="flex-[7] self-start">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                            <Brain size={20} className="text-blue-400" />
                        </div>
                        <h2 className="text-sm font-bold text-slate-400 uppercase tracking-[0.4em]">
                            EXECUTIVE SUMMARY <span className="text-slate-700 ml-2">// HIVE MIND ANALYSIS</span>
                        </h2>
                    </div>

                    <div className="relative">
                        <div className="absolute -left-6 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500/50 to-transparent rounded-full shadow-[0_0_10px_rgba(59,130,246,0.5)]"></div>
                        <p className="text-xl md:text-2xl font-light text-white leading-relaxed tracking-wide italic">
                            "{summary || "Aggregating swarm reports to establish a unified market direction..."}"
                        </p>
                    </div>

                    <div className="mt-10 flex items-center gap-4 text-xs font-bold text-slate-500 tracking-widest">
                        <span className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                            LIVE NEURAL LINK ACTIVE
                        </span>
                        <ArrowRight size={14} className="text-slate-800" />
                        <span>CONSENSUS V.2.1-BETA</span>
                    </div>
                </div>
            </div>

            {/* Ambient background decoration */}
            <div className={`absolute top-0 right-0 w-96 h-96 bg-${isBullish ? 'emerald' : isBearish ? 'rose' : 'amber'}-500/10 blur-[150px] -z-0 rounded-full`}></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/5 blur-[120px] -z-0 rounded-full"></div>
        </div>
    );
};
