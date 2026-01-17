'use client';

import { motion } from 'framer-motion';

const HORROR_NEWS = [
    "💀 LIQUIDITY GHOST detected in the order book...",
    "🩸 BLEEDING EDGE: Solana vampires sucking liquidity...",
    "🧟 ZOMBIE BULLS are waking up from the grave...",
    "👻 A phantom wallet just moved 10,000 BTC...",
    "🕸️ The Spider Algorithm is weaving a trap...",
    "🌑 ECLIPSE MODE: Dark Pools aim for total darkness...",
    "🗡️ SHORT SQUEEZE: The bears are being hunted...",
    "🧠 BRAIINSSS... The Hive Mind demands compute...",
    "🔮 The Oracle sees only GREEN candles... and blood...",
];

export function HorrorTicker() {
    return (
        <div className="w-full bg-black border-t border-b border-red-900/30 overflow-hidden py-2 relative">
            <div className="absolute inset-0 bg-red-900/5 pointer-events-none animate-pulse"></div>
            <motion.div
                className="whitespace-nowrap flex gap-16 text-sm font-mono text-red-500/80"
                animate={{ x: [0, -1000] }}
                transition={{
                    repeat: Infinity,
                    duration: 20,
                    ease: "linear"
                }}
            >
                {/* Repeat list to ensure smooth infinite scroll */}
                {[...HORROR_NEWS, ...HORROR_NEWS, ...HORROR_NEWS].map((news, i) => (
                    <span key={i} className="flex items-center gap-2">
                        <span className="text-xl">⚡</span>
                        {news}
                    </span>
                ))}
            </motion.div>
        </div>
    );
}
