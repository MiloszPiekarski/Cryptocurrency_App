'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowUpRight, ArrowDownRight, Skull, Rocket, Activity, Eye, Zap, TrendingUp } from 'lucide-react';
import { Sparkline } from '@/components/ui/Sparkline';
import { HorrorTicker } from '@/components/ui/HorrorTicker';
import { PageHelper } from '@/components/ui/PageHelper';

// --- MOCK DATA FOR PROTOTYPE ---
const MARKET_DATA = [
    { name: 'Bitcoin', symbol: 'BTC', price: 94250.45, change: 5.2, color: '#10b981', history: Array(20).fill(0).map((_, i) => ({ value: 50000 + Math.random() * 5000 + i * 100 })) },
    { name: 'Ethereum', symbol: 'ETH', price: 3450.12, change: 2.1, color: '#10b981', history: Array(20).fill(0).map((_, i) => ({ value: 3000 + Math.random() * 200 + i * 10 })) },
    { name: 'Solana', symbol: 'SOL', price: 145.67, change: -1.4, color: '#ef4444', history: Array(20).fill(0).map((_, i) => ({ value: 150 + Math.random() * 10 - i })) },
];

const CHAD_COINS = [
    { symbol: 'PEPE', change: '+24%', desc: 'Frog bouncing' },
    { symbol: 'WIF', change: '+18%', desc: 'Hat stays on' },
    { symbol: 'BONK', change: '+12%', desc: 'Dog go bark' },
];

const REKT_COINS = [
    { symbol: 'LUNA', change: '-99%', desc: 'Still dead' },
    { symbol: 'FTT', change: '-15%', desc: 'Jail time' },
    { symbol: 'XRP', change: '-5%', desc: 'SEC woke up' },
];

const WHALE_ACTIVITY = [
    { time: '10:42', text: '🐋 5000 BTC moved to Binance', risk: 'HIGH' },
    { time: '10:38', text: '🧠 Hive Mind detected accumulation on SOL', risk: 'LOW' },
    { time: '10:30', text: '💀 $42M Longs liquidated in 1 min', risk: 'CRITICAL' },
];

// --- COMPONENTS ---

function MarketCard({ asset }: { asset: any }) {
    return (
        <div className="bg-gray-900/40 border border-gray-800 rounded-xl p-4 hover:border-cyan-500/50 transition-colors group">
            <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs ${asset.color === '#10b981' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                        {asset.symbol[0]}
                    </div>
                    <div>
                        <div className="font-bold text-sm">{asset.name}</div>
                        <div className="text-xs text-gray-500">{asset.symbol}</div>
                    </div>
                </div>
                <div className={`text-right ${asset.change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    <div className="font-mono font-bold">${asset.price.toLocaleString()}</div>
                    <div className="text-xs flex items-center justify-end">
                        {asset.change > 0 ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                        {asset.change}%
                    </div>
                </div>
            </div>
            <div className="h-12 w-full opacity-50 group-hover:opacity-100 transition-opacity">
                <Sparkline data={asset.history} color={asset.color} />
            </div>
        </div>
    );
}

function FeedItem({ item }: { item: any }) {
    return (
        <div className={`p-3 border-l-2 mb-2 bg-black/40 text-sm ${item.risk === 'CRITICAL' ? 'border-red-500 text-red-200' :
                item.risk === 'HIGH' ? 'border-orange-500 text-orange-200' : 'border-cyan-500 text-gray-300'
            }`}>
            <span className="text-xs font-mono opacity-50 mr-2">[{item.time}]</span>
            {item.text}
        </div>
    )
}

function Mascot({ mood }: { mood: string }) {
    return (
        <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ repeat: Infinity, duration: 3 }}
            className="fixed bottom-20 right-6 z-50 pointer-events-none hidden lg:block"
        >
            <div className="relative">
                <div className="text-8xl filter drop-shadow-2xl">
                    {mood === 'bull' ? '🐂' : '👻'}
                </div>
                <div className="absolute -top-12 -left-20 bg-white text-black p-3 rounded-xl rounded-br-none text-xs font-bold w-40 shadow-xl">
                    {mood === 'bull' ? "Market looking juicy! Time to eat?" : "I smell fear... delicious fear."}
                </div>
            </div>
        </motion.div>
    )
}

export default function DashboardPage() {
    return (
        <div className="min-h-screen bg-[#050505] text-white pb-32 bg-[url('/grid-texture.png')]">

            {/* --- HEADER SECTION --- */}
            <div className="max-w-7xl mx-auto p-6 pt-8">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 border-b border-gray-800 pb-6">
                    <div>
                        <h1 className="text-4xl font-black italic tracking-tighter mb-1">
                            OVERVIEW <span className="text-cyan-500">_V3</span>
                        </h1>
                        <p className="text-gray-400 text-sm">
                            Welcome back, Operator. The market is <span className="text-green-400 font-bold">ALIVE</span>.
                        </p>
                    </div>
                    <div className="mt-4 md:mt-0 flex gap-4">
                        <div className="text-right">
                            <div className="text-xs text-gray-500 uppercase">Fear & Greed</div>
                            <div className="text-xl font-black text-orange-500">79 <span className="text-xs">(Extreme Greed)</span></div>
                        </div>
                        <div className="text-right border-l border-gray-800 pl-4">
                            <div className="text-xs text-gray-500 uppercase">24h Vol</div>
                            <div className="text-xl font-black text-white">$142B</div>
                        </div>
                    </div>
                </div>

                {/* --- MAIN GRID LAYOUT --- */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

                    {/* 1. LEFT COLUMN: MARKET PULSE (Major Assets) */}
                    <div className="lg:col-span-1 space-y-4">
                        <div className="flex items-center gap-2 mb-2">
                            <Activity className="text-cyan-500 w-4 h-4" />
                            <h3 className="font-bold text-gray-400 text-sm uppercase">Market Pulse</h3>
                        </div>
                        {MARKET_DATA.map(asset => (
                            <MarketCard key={asset.symbol} asset={asset} />
                        ))}

                        {/* Status Box */}
                        <div className="bg-gradient-to-br from-purple-900/20 to-black border border-purple-500/20 p-4 rounded-xl mt-6">
                            <div className="flex items-center gap-2 text-purple-400 font-bold text-sm mb-2">
                                <Zap className="w-4 h-4" /> HIVE MIND STATUS
                            </div>
                            <div className="text-xs text-gray-400">
                                984,213 active agents scanning order books.
                            </div>
                            <div className="w-full bg-gray-800 h-1 mt-3 rounded-full overflow-hidden">
                                <div className="bg-purple-500 h-full w-[85%] animate-pulse"></div>
                            </div>
                            <div className="text-[10px] text-right text-purple-500 mt-1">OPTIMIZED</div>
                        </div>
                    </div>

                    {/* 2. CENTER COLUMN: THE FEED + CHART OF DAY */}
                    <div className="lg:col-span-2 space-y-6">

                        {/* Chart of the Day Area */}
                        <div className="bg-gray-900/20 border border-gray-800 rounded-2xl p-6 h-64 relative overflow-hidden group">
                            <div className="absolute inset-0 bg-gradient-to-t from-green-900/10 to-transparent"></div>
                            <div className="absolute top-4 left-4">
                                <div className="text-xs font-bold text-green-500 uppercase tracking-widest border border-green-500/30 px-2 py-1 rounded inline-block">
                                    CHART OF THE MOMENT
                                </div>
                                <h2 className="text-3xl font-black mt-2">BITCOIN BREAKOUT</h2>
                            </div>
                            {/* Fake Chart Line */}
                            <svg className="absolute bottom-0 left-0 right-0 h-32 w-full stroke-green-500 stroke-2 fill-green-500/20" preserveAspectRatio="none">
                                <path d="M0,100 Q200,50 400,80 T800,20 V120 H0 Z" />
                            </svg>
                            <div className="absolute bottom-4 right-4 text-xs text-gray-500 group-hover:text-white transition-colors cursor-pointer">
                                Click to analyze in Forge &rarr;
                            </div>
                        </div>

                        {/* Live Intel Feed */}
                        <div className="bg-black border border-gray-800 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-bold text-gray-200 text-sm flex items-center gap-2">
                                    <Eye className="w-4 h-4 text-cyan-500" /> LIVE INTEL
                                </h3>
                                <span className="text-[10px] text-green-500 animate-pulse">● LIVE</span>
                            </div>
                            <div className="space-y-1">
                                {WHALE_ACTIVITY.map((item, i) => (
                                    <FeedItem key={i} item={item} />
                                ))}
                            </div>
                        </div>

                    </div>

                    {/* 3. RIGHT COLUMN: GAINERS/LOSERS (The Fun Stuff) */}
                    <div className="lg:col-span-1 space-y-6">

                        {/* Chad Coins */}
                        <div className="bg-green-900/10 border border-green-900/30 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-3 text-green-400 font-bold text-sm uppercase">
                                <Rocket className="w-4 h-4" /> Chad Coins 🚀
                            </div>
                            <div className="space-y-3">
                                {CHAD_COINS.map(c => (
                                    <div key={c.symbol} className="flex justify-between items-center text-sm border-b border-green-500/10 pb-2 last:border-0 hover:pl-2 transition-all cursor-pointer">
                                        <div>
                                            <div className="font-bold text-white">{c.symbol}</div>
                                            <div className="text-[10px] text-gray-400">{c.desc}</div>
                                        </div>
                                        <div className="font-bold text-green-400">{c.change}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Rekt Coins */}
                        <div className="bg-red-900/10 border border-red-900/30 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-3 text-red-400 font-bold text-sm uppercase">
                                <Skull className="w-4 h-4" /> Rekt Coins 💀
                            </div>
                            <div className="space-y-3">
                                {REKT_COINS.map(c => (
                                    <div key={c.symbol} className="flex justify-between items-center text-sm border-b border-red-500/10 pb-2 last:border-0 hover:pl-2 transition-all cursor-pointer">
                                        <div>
                                            <div className="font-bold text-white">{c.symbol}</div>
                                            <div className="text-[10px] text-gray-400">{c.desc}</div>
                                        </div>
                                        <div className="font-bold text-red-400">{c.change}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                    </div>

                </div>

            </div>

            <Mascot mood="bull" />

            <div className="fixed bottom-0 left-0 right-0 z-40">
                <HorrorTicker />
            </div>

            <PageHelper
                title="DASHBOARD OVERVIEW"
                description="This is your daily briefing. Check Market Pulse for key levels. Read the Whale Activity feed to see what smart money is doing. Look at 'Rekt Coins' to see who is crying today."
            />

        </div>
    );
}
