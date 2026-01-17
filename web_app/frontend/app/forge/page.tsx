'use client';

import { useState } from 'react';
import { ProfessionalChart } from '@/components/charts/ProfessionalChart';

const SYMBOLS = [
    { symbol: 'BTC/USDT', name: 'Bitcoin' },
    { symbol: 'ETH/USDT', name: 'Ethereum' },
    { symbol: 'SOL/USDT', name: 'Solana' },
    { symbol: 'BNB/USDT', name: 'BNB' },
    { symbol: 'XRP/USDT', name: 'XRP' },
    // Simplified list for now, easy to extend
];

export default function ForgePage() {
    const [symbol, setSymbol] = useState('BTC/USDT');

    return (
        <div className="h-screen w-screen bg-[#0f1729] flex flex-col overflow-hidden">
            {/* Minimal App Header (Optional, or integrate into chart) */}
            <header className="h-12 bg-[#1e222d] border-b border-[#2a2e39] flex items-center px-4 justify-between shrink-0 z-30">
                <div className="flex items-center gap-4">
                    <span className="font-bold text-gray-100 tracking-wider">MAELSTROM <span className="text-cyan-500">FORGE</span></span>
                    <div className="h-4 w-[1px] bg-gray-700"></div>
                    <select
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value)}
                        className="bg-[#2a2e39] text-gray-200 text-xs px-2 py-1 rounded border border-gray-700 focus:outline-none focus:border-cyan-500"
                    >
                        {SYMBOLS.map(s => (
                            <option key={s.symbol} value={s.symbol}>{s.name} ({s.symbol})</option>
                        ))}
                    </select>
                </div>
                <div className="text-xs text-gray-500">
                    Pro Mode Active
                </div>
            </header>

            <div className="flex-1 w-full relative">
                <ProfessionalChart symbol={symbol} />
            </div>
        </div>
    );
}
