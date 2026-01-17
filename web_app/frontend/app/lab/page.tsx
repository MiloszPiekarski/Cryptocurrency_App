'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function LabPage() {
    const [selectedAsset, setSelectedAsset] = useState('BTC/USDT');
    const [swarmData, setSwarmData] = useState<any>(null);

    useEffect(() => {
        // Fetch from Hive Mind API
        fetch(`http://localhost:8000/api/v1/hive/swarm/${selectedAsset}`)
            .then(res => res.json())
            .then(data => setSwarmData(data))
            .catch(e => console.error(e));
    }, [selectedAsset]);

    return (
        <div className="min-h-screen bg-gradient-to-b from-black via-gray-900 to-black text-white p-6">

            {/* Header */}
            <div className="mb-6 flex justify-between items-center">
                <div>
                    <Link href="/nexus" className="text-xs text-gray-500 hover:text-cyan-400 transition-colors">
                        &larr; RETURN TO NEXUS
                    </Link>
                    <h1 className="text-4xl font-black mt-2 tracking-tight">
                        THE LAB <span className="text-cyan-500 text-lg font-normal">// Atomic Analysis</span>
                    </h1>
                    <p className="text-gray-400 text-sm mt-1">
                        Convergence of all intelligence systems for: <span className="text-white font-bold">{selectedAsset}</span>
                    </p>
                </div>

                {/* Asset Selector */}
                <div className="flex gap-2">
                    {['BTC/USDT', 'ETH/USDT', 'SOL/USDT'].map(symbol => (
                        <button
                            key={symbol}
                            onClick={() => setSelectedAsset(symbol)}
                            className={`px-4 py-2 rounded-lg text-sm font-mono transition-all ${selectedAsset === symbol
                                    ? 'bg-cyan-600 text-white'
                                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                                }`}
                        >
                            {symbol.replace('/USDT', '')}
                        </button>
                    ))}
                </div>
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">

                {/* Swarm Consensus */}
                <div className="bg-gray-900/40 border border-gray-800 rounded-xl p-6">
                    <h3 className="text-xs font-bold text-purple-400 uppercase mb-4 flex items-center gap-2">
                        <span className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></span>
                        Swarm Consensus
                    </h3>
                    {swarmData ? (
                        <>
                            <div className="text-3xl font-bold mb-2">
                                {swarmData.active_agents?.toLocaleString()} Agents
                            </div>
                            <div className="text-sm text-gray-400 mb-4">
                                Focus: {swarmData.focus_topic}
                            </div>
                            <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-purple-500 to-cyan-500"
                                    style={{ width: `${swarmData.consensus_score * 100}%` }}
                                ></div>
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                                Consensus: {Math.round(swarmData.consensus_score * 100)}%
                            </div>
                        </>
                    ) : (
                        <div className="text-gray-600">Loading swarm data...</div>
                    )}
                </div>

                {/* Digital Twin Projection */}
                <div className="bg-gray-900/40 border border-gray-800 rounded-xl p-6">
                    <h3 className="text-xs font-bold text-cyan-400 uppercase mb-4">Simulation Futures</h3>
                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-400">Bull Case (24h)</span>
                            <span className="text-green-400 font-bold">+12.3%</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-400">Base Case</span>
                            <span className="text-gray-400 font-bold">+3.1%</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-400">Bear Case</span>
                            <span className="text-red-400 font-bold">-8.7%</span>
                        </div>
                    </div>
                </div>

                {/* Risk Metrics */}
                <div className="bg-gray-900/40 border border-gray-800 rounded-xl p-6">
                    <h3 className="text-xs font-bold text-red-400 uppercase mb-4">Risk Assessment</h3>
                    <div className="space-y-3 text-sm">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Volatility</span>
                            <span className="text-yellow-400">MODERATE</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Liquidity</span>
                            <span className="text-green-400">HIGH</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Smart Money</span>
                            <span className="text-cyan-400">ACCUMULATING</span>
                        </div>
                    </div>
                </div>

            </div>

            {/* THE VERDICT */}
            <div className="bg-gradient-to-r from-purple-900/20 via-cyan-900/20 to-blue-900/20 border border-cyan-500/30 rounded-xl p-6">
                <h2 className="text-2xl font-black mb-3 text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
                    THE VERDICT
                </h2>
                <div className="text-gray-300 leading-relaxed">
                    <p className="mb-3">
                        <span className="text-cyan-400 font-bold">Convergence Analysis:</span> All systems indicate a{' '}
                        <span className="text-green-400 font-bold">
                            {swarmData?.consensus_score > 0.6 ? 'bullish accumulation pattern' : 'neutral market structure'}
                        </span>{' '}
                        for {selectedAsset}.
                    </p>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-400 ml-4">
                        <li>Hive Mind Consensus: <span className="text-purple-400">{swarmData ? Math.round(swarmData.consensus_score * 100) : '--'}% Confidence</span></li>
                        <li>Digital Twin Projections: <span className="text-cyan-400">+3-12% upside (24h)</span></li>
                        <li>Risk Level: <span className="text-yellow-400">Moderate</span></li>
                    </ul>
                    <p className="mt-4 text-xs text-gray-500 italic border-t border-gray-800 pt-3">
                        ⚠️ This is an analytical verdict based on quantitative models. Not financial advice. CASH MAELSTROM is a research tool.
                    </p>
                </div>
            </div>

        </div>
    );
}
