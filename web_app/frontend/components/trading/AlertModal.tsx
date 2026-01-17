"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bell, X, ArrowUp, ArrowDown } from 'lucide-react';
import { useAlertStore } from '@/lib/alertStore';

interface AlertModalProps {
    isOpen: boolean;
    onClose: () => void;
    symbol: string;
    currentPrice: number;
}

export function AlertModal({ isOpen, onClose, symbol, currentPrice }: AlertModalProps) {
    const { registerPriceAlert } = useAlertStore();
    const [price, setPrice] = useState<string>(currentPrice.toString());
    const [condition, setCondition] = useState<'above' | 'below'>('above');

    const handleSave = () => {
        const targetPrice = parseFloat(price);
        if (!isNaN(targetPrice)) {
            registerPriceAlert(symbol, targetPrice, condition);
            onClose();
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center"
                    >
                        {/* Modal Content - Prevent click parsing */}
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            onClick={(e) => e.stopPropagation()}
                            className="bg-[#0f1729] border border-gray-800 p-6 rounded-xl w-full max-w-sm shadow-2xl relative"
                        >
                            <button onClick={onClose} className="absolute top-4 right-4 text-gray-500 hover:text-white">
                                <X className="w-5 h-5" />
                            </button>

                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400">
                                    <Bell className="w-6 h-6" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-white">Set Alert</h3>
                                    <p className="text-sm text-gray-400">for {symbol}</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <div>
                                    <label className="text-xs text-gray-500 mb-2 block">Condition</label>
                                    <div className="grid grid-cols-2 gap-2">
                                        <button
                                            onClick={() => setCondition('above')}
                                            className={`flex items-center justify-center gap-2 py-2 rounded-lg border ${condition === 'above' ? 'bg-green-500/20 border-green-500 text-green-400' : 'bg-[#0a0e27] border-gray-700 text-gray-400'}`}
                                        >
                                            <ArrowUp className="w-4 h-4" /> Crossing Up
                                        </button>
                                        <button
                                            onClick={() => setCondition('below')}
                                            className={`flex items-center justify-center gap-2 py-2 rounded-lg border ${condition === 'below' ? 'bg-red-500/20 border-red-500 text-red-400' : 'bg-[#0a0e27] border-gray-700 text-gray-400'}`}
                                        >
                                            <ArrowDown className="w-4 h-4" /> Crossing Down
                                        </button>
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs text-gray-500 mb-2 block">Price Target</label>
                                    <input
                                        type="number"
                                        value={price}
                                        onChange={(e) => setPrice(e.target.value)}
                                        className="w-full bg-[#0a0e27] border border-gray-700 rounded-lg p-3 text-white font-mono focus:border-blue-500 outline-none transition-colors"
                                    />
                                    <div className="text-xs text-right mt-1 text-gray-500">
                                        Current: ${currentPrice.toLocaleString()}
                                    </div>
                                </div>

                                <button
                                    onClick={handleSave}
                                    className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg transition-colors mt-2"
                                >
                                    Create Alert
                                </button>
                            </div>

                        </motion.div>
                    </motion.div>
                </>
            )}
        </AnimatePresence>
    );
}
