'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function DigitalTwinPage() {
    const [symbol, setSymbol] = useState('BTC/USDT');

    return (
        <div className="min-h-screen bg-black text-white p-6">

            <div className="mb-6">
                <Link href="/nexus" className="text-xs text-gray-500 hover:text-cyan-400">&larr; NEXUS</Link>
                <h1 className="text-4xl font-bold mt-2 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">
                    DIGITAL TWIN
                </h1>
                <p className="text-gray-400 mt-1">Monte Carlo Simulation Studio</p>
            </div>

            <div className="bg-gray-900/40 border border-cyan-500/30 rounded-xl p-8 text-center">
                <div className="text-6xl mb-4">🔮</div>
                <h2 className="text-2xl font-bold mb-2">Simulation Engine</h2>
                <p className="text-gray-400 mb-6">
                    Monte Carlo algorithms analyze 10,000 potential futures for {symbol}
                </p>
                <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto">
                    <div className="bg-black/40 p-4 rounded border border-gray-800">
                        <div className="text-xs text-gray-500 mb-1">BULL SCENARIO</div>
                        <div className="text-green-400 text-2xl font-bold">+23.4%</div>
                        <div className="text-xs text-gray-600">Probability: 34%</div>
                    </div>
                    <div className="bg-black/40 p-4 rounded border border-gray-800">
                        <div className="text-xs text-gray-500 mb-1">NEUTRAL</div>
                        <div className="text-gray-400 text-2xl font-bold">±5%</div>
                        <div className="text-xs text-gray-600">Probability: 45%</div>
                    </div>
                    <div className="bg-black/40 p-4 rounded border border-gray-800">
                        <div className="text-xs text-gray-500 mb-1">BEAR SCENARIO</div>
                        <div className="text-red-400 text-2xl font-bold">-18.2%</div>
                        <div className="text-xs text-gray-600">Probability: 21%</div>
                    </div>
                </div>
                <p className="text-xs text-gray-600 mt-6 italic">
                    Full implementation coming soon - connect to backend Monte Carlo engine
                </p>
            </div>

        </div>
    );
}
