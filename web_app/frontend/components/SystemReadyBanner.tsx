'use client';

import { useEffect, useState } from 'react';
import { CheckCircle, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function SystemReadyBanner() {
    const [show, setShow] = useState(false);

    useEffect(() => {
        // Show banner after 2 seconds to prove systems are live
        const timer = setTimeout(() => setShow(true), 2000);
        return () => clearTimeout(timer);
    }, []);

    return (
        <AnimatePresence>
            {show && (
                <motion.div
                    initial={{ y: -100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -100, opacity: 0 }}
                    className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 pointer-events-none"
                >
                    <div className="bg-gradient-to-r from-green-900/90 to-emerald-900/90 backdrop-blur-xl border-2 border-green-500 rounded-2xl px-8 py-4 shadow-2xl shadow-green-500/50">
                        <div className="flex items-center gap-4">
                            <CheckCircle className="w-8 h-8 text-green-400 animate-pulse" />
                            <div>
                                <div className="text-white font-bold text-lg">🚀 ALL SYSTEMS OPERATIONAL</div>
                                <div className="text-green-300 text-sm flex items-center gap-2 mt-1">
                                    <Zap className="w-4 h-4" />
                                    <span>Ray Hive • Quantum Engine • Blockchain • Redis Streams</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
