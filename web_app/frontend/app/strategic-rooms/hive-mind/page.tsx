"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Head from 'next/head';
import {
    Activity,
    BrainCircuit,
    FileDown,
    Zap,
    Shield,
    Brain,
    Eye,
    Globe,
    Lock
} from 'lucide-react';

// Components
import AgentSidebar from '@/components/dashboard/AgentSidebar';
import { AgentMatrixWidget } from '@/components/dashboard/widgets/AgentMatrixWidget';
import { SignalTableWidget } from '@/components/dashboard/widgets/SignalTableWidget';
import { ConsensusHero } from '@/components/dashboard/widgets/ConsensusHero';
// Modals
import { DeepDiveModal } from '@/components/modals/DeepDiveModal';
import { UpsellModal } from '@/components/modals/UpsellModal';
import { UpgradeModal } from '@/components/UpgradeModal';
import { useUser } from '@/context/UserContext';
import { Loader2 } from 'lucide-react';
import { Cpu } from 'lucide-react';

// API Configuration
// API Configuration
const AI_ENGINE_URL = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api/v1` : "http://localhost:8000/api/v1";

interface SwarmState {
    symbol: string;
    verdict: string;
    agents_active: number;
    swarm_breakdown: any[];
    global_consensus: string; // NEW FIELD
    collective_sentiment: number;
    risk_status: string;
    anomaly_threat: number;
    confidence_score: number;
    math_context: any;
    source_data: any;
    summary_data?: {
        price: number;
        high: number;
        low: number;
        volume: number;
        change_24h: string;
    };
    error?: string;
}

export default function HiveMindPage() {
    // ------------------------------------------------------------
    // 1. GLOBAL STATE (Single Source of Truth)
    // ------------------------------------------------------------
    const { plan, loading: userLoading } = useUser();
    const isPremium = plan === 'PRO';
    const [showUpgradeModal, setShowUpgradeModal] = useState(false);

    const [selectedAsset, setSelectedAsset] = useState("BTC/USDT");

    // Derived States
    const [swarm, setSwarm] = useState<SwarmState | null>(null);
    const [tickerData, setTickerData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [connectionError, setConnectionError] = useState<string | null>(null);

    // User & UI States
    // const [isPremium, setIsPremium] = useState(false); // REPLACED
    // const [upgrading, setUpgrading] = useState(false); // REMOVED
    const [deepDiveData, setDeepDiveData] = useState<any>(null);
    const [upsellFeature, setUpsellFeature] = useState<string | null>(null);
    const [generatingPdf, setGeneratingPdf] = useState(false);

    // Sidebar Config State
    const [agentConfig, setAgentConfig] = useState({
        scout: { active: true, weight: 1.0 },
        hunter: { active: true, weight: 1.0 },
        analyst: { active: true, weight: 1.0 },
        defender: { active: true, weight: 1.0 },
        strategist: { active: true, weight: 1.0 },
        sentinel: { active: true, weight: 1.0 },
    });

    // ------------------------------------------------------------
    // 2. DATA FETCHING
    // ------------------------------------------------------------
    const fetchTicker = useCallback(async () => {
        try {
            const cleanSymbol = selectedAsset.replace("/", "");
            const res = await fetch(`${AI_ENGINE_URL}/market/ticker/${cleanSymbol}`);
            if (!res.ok) throw new Error("Ticker Error");
            const data = await res.json();
            setTickerData(data);
            setConnectionError(null);
        } catch (err) {
            console.error(err);
        }
    }, [selectedAsset]);

    const fetchSwarm = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);
        try {
            const res = await fetch(`${AI_ENGINE_URL}/hive/swarm/${selectedAsset.replace("/", "-")}`);
            if (!res.ok) throw new Error("Backend Offline");
            const data = await res.json();
            if (data.error) throw new Error(data.error + (data.details ? ` (${data.details})` : ""));
            setSwarm(data);
            setConnectionError(null);
        } catch (err) {
            setConnectionError("AI CORE OFFLINE");
            console.error(err);
        } finally {
            if (!silent) setLoading(false);
        }
    }, [selectedAsset]);

    // Initial Load & Polling
    useEffect(() => {
        setSwarm(null); // Reset on asset change
        fetchSwarm(false);
        fetchTicker();

        const tickerInterval = setInterval(fetchTicker, 2000);
        // Swarm auto-refresh disabled per user request (static view only)

        return () => {
            clearInterval(tickerInterval);
        };
    }, [selectedAsset, fetchSwarm, fetchTicker]);


    // Removed manual plan fetch - using UserContext

    // ------------------------------------------------------------
    // 3. HANDLERS
    // ------------------------------------------------------------
    const handleConfigChange = (key: string, field: 'active' | 'weight', value: any) => {
        setAgentConfig(prev => ({
            ...prev,
            [key]: {
                // @ts-ignore
                ...prev[key],
                [field]: value
            }
        }));
    };

    const handleConfigCommit = async (key: string, field: 'active' | 'weight', value: any) => {
        console.log(`[SYNC] Committing config change: ${key}.${field} = ${value}`);
        try {
            const res = await fetch(`${AI_ENGINE_URL}/hive/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    role: key.toUpperCase(),
                    // If weight > 0 is being set, force active to true
                    active: (field === 'weight' && value > 0)
                        ? true
                        : (field === 'active' ? value : agentConfig[key as keyof typeof agentConfig].active),

                    // If active is being set to true, force weight to 1.0 (if it was 0)
                    weight: (field === 'active' && value === true)
                        ? 1.0
                        : (field === 'weight' ? value : agentConfig[key as keyof typeof agentConfig].weight)
                })
            });

            if (res.ok) {
                // Force immediate swarm refresh to reflect changes in Evidence Log
                setTimeout(() => fetchSwarm(), 500);
            }
        } catch (e) {
            console.error("Config Sync Failed", e);
        }
    };

    const handleDownloadReport = async () => {
        if (!isPremium) {
            setShowUpgradeModal(true);
            return;
        }
        if (!swarm) return;
        const price = tickerData?.last || 0;

        const payload = {
            symbol: selectedAsset,
            price: price,
            verdict: swarm.verdict,
            confidence: swarm.confidence_score,
            consensus_text: swarm.global_consensus || "Consensus pending...",
            agents: swarm.swarm_breakdown || [],
            timestamp: new Date().toISOString()
        };

        try {
            const res = await fetch(`${AI_ENGINE_URL}/reports/pdf_post`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("PDF Gen Failed");

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Tactical_Brief_${selectedAsset.replace('/', '_')}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (e) {
            console.error(e);
            alert("Failed to generate PDF Report.");
        }
    };

    // Old handleUpgrade removed - handled by UpgradeModal

    // Market Sentiment Logic
    const riskStatus = React.useMemo(() => {
        if (!tickerData) return { label: "ANALYZING...", color: "bg-slate-700" };
        const change = parseFloat(tickerData.change_24h || "0");
        return change < -1.0
            ? { label: "RISK OFF", color: "bg-rose-600 animate-pulse shadow-[0_0_10px_rgba(225,29,72,0.5)]" }
            : { label: "RISK ON", color: "bg-emerald-600 shadow-[0_0_10px_rgba(5,150,105,0.5)]" };
    }, [tickerData]);




    // Parse Global Consensus JSON safely
    const parsedConsensus = React.useMemo(() => {
        if (!swarm?.global_consensus) return null;

        // If it's already an object, return it
        if (typeof swarm.global_consensus === 'object') return swarm.global_consensus;

        const raw = String(swarm.global_consensus).trim();

        // Quick check: if it doesn't look like JSON, don't even try to parse
        if (!raw.startsWith('{') && !raw.startsWith('[')) {
            return {
                summary: raw,
                global_confidence: swarm.confidence_score || 0,
                verdict: swarm.verdict || "UNKNOWN"
            };
        }

        try {
            return JSON.parse(raw);
        } catch (e) {
            // Silently fallback to raw summary if parsing fails
            return {
                summary: raw,
                global_confidence: swarm.confidence_score || 0,
                verdict: swarm.verdict || "UNKNOWN"
            };
        }
    }, [swarm]);

    // FAILSAFE: Filter agents here based on local config to ensure immediate UI response
    // regardless of backend state consistency.
    // PREMIUM GATE: Also exclude Defender and Strategist for non-premium users.
    const filteredBreakdown = React.useMemo(() => {
        if (!swarm?.swarm_breakdown) return [];

        // Define which agents are premium-locked
        const premiumLockedAgents = ['defender', 'strategist'];

        return swarm.swarm_breakdown.filter(agent => {
            const roleKey = agent.role?.toLowerCase();

            // Premium Gate: If user is not premium and agent is premium-locked, exclude it
            if (!isPremium && premiumLockedAgents.includes(roleKey)) {
                return false;
            }

            // Default to true if not in config, otherwise check active status
            return agentConfig[roleKey as keyof typeof agentConfig]?.active ?? true;
        });
    }, [swarm?.swarm_breakdown, agentConfig, isPremium]);

    // Recalculate confidence based on FILTERED agents only (Frontend Truth)
    const effectiveConfidence = React.useMemo(() => {
        if (filteredBreakdown.length === 0) return 0;
        const totalConf = filteredBreakdown.reduce((acc, agent) => acc + (agent.confidence || 0), 0);
        return Math.round(totalConf / filteredBreakdown.length);
    }, [filteredBreakdown]);

    if (userLoading) {
        return (
            <div className="h-screen w-full flex items-center justify-center bg-[#0b1120] text-slate-400 gap-2">
                <Loader2 className="animate-spin" size={24} />
                <span className="text-sm font-mono tracking-widest">AUTHENTICATING ACCESS...</span>
            </div>
        );
    }

    return (
        <div className="flex flex-col min-h-screen bg-[#0b1120] text-slate-200 font-sans">
            <Head>
                <title>HIVE MIND | TURBO-PLAN X</title>
            </Head>

            {/* HEADER with Live Price */}
            <header className="h-16 border-b border-slate-700/50 flex items-center justify-between px-6 bg-slate-900/50 backdrop-blur-md z-20 sticky top-0">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <BrainCircuit className="text-blue-500" size={24} />
                        <h1 className="text-lg font-bold tracking-tight text-white">
                            HIVE MIND <span className="text-slate-500 font-normal">v2.1</span>
                        </h1>
                    </div>

                    {/* ASSET SELECTOR */}
                    <div className="h-8 w-[1px] bg-slate-700 mx-2"></div>
                    <select
                        value={selectedAsset}
                        onChange={(e) => setSelectedAsset(e.target.value)}
                        className="bg-slate-800 border border-slate-600 text-white text-sm rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 hover:bg-slate-700 transition-colors cursor-pointer"
                    >
                        <option value="BTC/USDT">BTC/USDT</option>
                        <option value="ETH/USDT">ETH/USDT</option>
                        <option value="SOL/USDT">SOL/USDT</option>
                    </select>
                    {/* Live Ticker Summary */}
                    <div className="flex flex-col items-end mr-4">
                        <span className="text-[10px] text-slate-400 font-bold tracking-widest">LIVE PRICE</span>
                        {tickerData ? (
                            <div className={`font-mono font-bold text-lg ${parseFloat(tickerData.change_24h) >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                                ${tickerData.last?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 text-slate-500">
                                <Activity size={14} className="animate-spin" />
                                <span className="text-sm font-mono">SCANNING...</span>
                            </div>
                        )}
                    </div>

                    <button
                        onClick={handleDownloadReport}
                        disabled={generatingPdf}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-md border text-xs font-bold transition-all ${isPremium
                            ? 'bg-slate-800 hover:bg-slate-700 text-slate-200 border-slate-600'
                            : 'bg-slate-900 border-slate-800 text-slate-600 cursor-not-allowed group'
                            }`}
                        title={isPremium ? "Download Deep Report" : "Upgrade to Pro to Download"}
                    >
                        {generatingPdf ? <Loader2 size={14} className="animate-spin" /> : (
                            isPremium ? <FileDown size={14} /> : <Lock size={14} className="text-slate-600 group-hover:text-slate-500" />
                        )}
                        DOWNLOAD REPORT
                    </button>
                    {!isPremium && (
                        <button
                            onClick={() => setUpsellFeature("PRO")}
                            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-4 py-1.5 rounded-md text-xs font-bold shadow-lg shadow-blue-900/20 transition-all hover:scale-105"
                        >
                            UPGRADE TO PRO
                        </button>
                    )}
                </div>
            </header>

            {/* MAIN CONTENT ROW */}
            <div className="flex flex-1">

                {/* LEFT SIDEBAR (Swarm Control) - Sticky and fluid */}
                <div className="w-80 flex-shrink-0 bg-slate-900/80 border-r border-slate-700/50 z-10 sticky top-16 h-fit max-h-[calc(100vh-64px)] overflow-y-auto scrollbar-hide">
                    <AgentSidebar
                        config={agentConfig}
                        onChange={handleConfigChange}
                        onCommit={handleConfigCommit}
                        isPremium={isPremium}
                        onUpgrade={() => setShowUpgradeModal(true)}
                    />
                </div>

                {/* CENTER CONTENT (Matrix & Evidence) */}
                <div className="flex-1 flex flex-col min-w-0 bg-[#0b1120] relative h-auto">
                    {/* Background Grid */}
                    <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-5 pointer-events-none"></div>

                    <div className="p-6 space-y-8 h-auto">

                        {/* REDESIGNED CONSENSUS HERO */}
                        <ConsensusHero
                            summary={parsedConsensus?.summary}
                            confidence={effectiveConfidence}
                            verdict={parsedConsensus?.verdict || swarm?.verdict}
                            loading={loading}
                        />

                        {/* 1. AGENT MATRIX (Grid) */}
                        <section>
                            <h2 className="text-xs font-bold text-slate-500 mb-4 flex items-center gap-2 uppercase tracking-widest">
                                <Activity size={12} />
                                Neural Grid Matrix
                            </h2>
                            {/* Removed fixed height container */}
                            <AgentMatrixWidget
                                data={filteredBreakdown}
                                config={agentConfig}
                                isPremium={isPremium}
                            />
                        </section>

                        {/* 2. EVIDENCE LOG (Table) */}
                        <section>
                            <div className="bg-slate-900/50 rounded-xl border border-slate-700/50 flex flex-col h-auto">
                                <div className="p-4 border-b border-slate-700/50 flex items-center justify-between">
                                    <h3 className="text-xs font-bold text-slate-400 flex items-center gap-2 uppercase tracking-widest">
                                        <FileDown size={12} />
                                        Evidence & Consensus Log
                                    </h3>
                                </div>
                                <div className="p-0">
                                    {swarm?.swarm_breakdown ? (
                                        <SignalTableWidget
                                            data={filteredBreakdown}
                                            onDeepDive={setDeepDiveData}
                                        />
                                    ) : (
                                        <div className="h-64 flex items-center justify-center text-slate-500 text-xs">
                                            {loading ? "ANALYZING BLOCKCHAIN DATA..." : "WAITING FOR CONNECTION..."}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </section>

                    </div>
                </div>
            </div>

            {/* MODALS */}
            {deepDiveData && (
                <DeepDiveModal
                    isOpen={!!deepDiveData}
                    onClose={() => setDeepDiveData(null)}
                    data={deepDiveData}
                />
            )}
            {upsellFeature && (
                <UpsellModal
                    isOpen={!!upsellFeature}
                    onClose={() => setUpsellFeature(null)}
                    onUpgrade={() => setShowUpgradeModal(true)}
                    feature={upsellFeature}
                    upgrading={false}
                />
            )}
            <UpgradeModal isOpen={showUpgradeModal} onClose={() => setShowUpgradeModal(false)} />

            {connectionError && (
                <div className="absolute bottom-6 right-6 bg-red-500/90 text-white px-4 py-2 rounded-lg shadow-lg text-xs font-bold animate-pulse z-50">
                    ⚠ {connectionError}
                </div>
            )}
        </div>
    );
}
