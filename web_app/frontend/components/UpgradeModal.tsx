import React, { useState } from 'react';
import { X, CreditCard, Check, Loader2 } from 'lucide-react';
import { useUser } from '@/context/UserContext';
import confetti from 'canvas-confetti';

interface UpgradeModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const UpgradeModal: React.FC<UpgradeModalProps> = ({ isOpen, onClose }) => {
    const { upgradeToPro } = useUser();
    const [processing, setProcessing] = useState(false);

    if (!isOpen) return null;

    const handlePayment = async (e: React.FormEvent) => {
        e.preventDefault();
        setProcessing(true);

        await upgradeToPro();

        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 }
        });

        setProcessing(false);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md overflow-hidden relative shadow-2xl shadow-purple-500/20">
                <button onClick={onClose} className="absolute top-4 right-4 text-slate-400 hover:text-white">
                    <X size={20} />
                </button>

                <div className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg">
                            <CreditCard className="text-white" size={24} />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">Upgrade to Pro</h2>
                            <p className="text-xs text-slate-400">Unlock full Hive Mind capabilities.</p>
                        </div>
                    </div>

                    <form onSubmit={handlePayment} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-xs font-medium text-slate-300">Card Number</label>
                            <input type="text" placeholder="0000 0000 0000 0000" className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm font-mono placeholder-slate-600" />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <label className="text-xs font-medium text-slate-300">Expiry</label>
                                <input type="text" placeholder="MM/YY" className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm font-mono placeholder-slate-600" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-medium text-slate-300">CVC</label>
                                <input type="text" placeholder="123" className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm font-mono placeholder-slate-600" />
                            </div>
                        </div>

                        <div className="pt-4">
                            <button
                                type="submit"
                                disabled={processing}
                                className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold py-3 px-4 rounded-xl shadow-lg shadow-purple-900/40 transition-all transform hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2"
                            >
                                {processing ? (
                                    <>
                                        <Loader2 className="animate-spin" size={18} />
                                        Processing...
                                    </>
                                ) : (
                                    <>
                                        PAY $29/mo
                                    </>
                                )}
                            </button>
                            <p className="text-[10px] text-center text-slate-500 mt-3 flex items-center justify-center gap-1">
                                <Check size={10} className="text-green-500" /> Secure 256-bit SSL Encrypted
                            </p>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};
