"use client";

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sigma, X, Database } from 'lucide-react';

interface MathRevealProps {
    label: string;
    value: React.ReactNode;
    math: string; // LaTeX or math string
    source: string; // Data source
    children: React.ReactNode;
}

export function MathReveal({ label, value, math, source, children }: MathRevealProps) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="relative group">
            <div
                className="cursor-pointer"
                onClick={() => setIsOpen(true)}
            >
                {children}
            </div>

            <AnimatePresence>
                {isOpen && (
                    <>
                        {/* Backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsOpen(false)}
                            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40"
                        />

                        {/* Modal */}
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9, y: 20 }}
                            className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg p-6 bg-[#050505] border border-cyan-900/50 rounded-xl shadow-[0_0_50px_rgba(0,255,255,0.1)]"
                        >
                            <div className="flex justify-between items-start mb-6">
                                <div className="flex items-center gap-2">
                                    <div className="p-2 bg-cyan-900/20 rounded border border-cyan-500/20">
                                        <Sigma className="w-5 h-5 text-cyan-400" />
                                    </div>
                                    <h3 className="text-xl font-bold text-white tracking-tight">RAW DATA REVEAL</h3>
                                </div>
                                <button onClick={() => setIsOpen(false)} className="text-gray-500 hover:text-white">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-xs uppercase text-gray-500 tracking-widest mb-1">METRIC</h4>
                                    <div className="text-2xl font-mono text-white">{label}: {value}</div>
                                </div>

                                <div className="p-4 bg-black border border-gray-800 rounded-lg font-mono text-sm text-yellow-500 overflow-x-auto">
                                    <div className="text-[10px] text-gray-500 mb-1">// FORMULA</div>
                                    {math}
                                </div>

                                <div>
                                    <h4 className="text-xs uppercase text-gray-500 tracking-widest mb-2 flex items-center gap-2">
                                        <Database className="w-3 h-3" /> SOURCE OF TRUTH
                                    </h4>
                                    <div className="text-xs font-mono text-cyan-300 break-all bg-cyan-950/20 p-2 rounded border border-cyan-900/30">
                                        {source}
                                    </div>
                                </div>
                            </div>

                            <div className="mt-6 pt-4 border-t border-gray-800 text-center">
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="text-xs text-gray-500 hover:text-white font-mono uppercase tracking-widest"
                                >
                                    [ CLOSE DEBUGGER ]
                                </button>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}
