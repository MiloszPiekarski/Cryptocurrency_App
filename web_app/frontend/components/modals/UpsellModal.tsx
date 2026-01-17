import React from 'react';
import { X, Lock, CheckCircle, Zap, Loader2 } from 'lucide-react';

interface UpsellModalProps {
    isOpen: boolean;
    onClose: () => void;
    feature: string;
    onUpgrade?: () => void;
    upgrading?: boolean;
}

export const UpsellModal: React.FC<UpsellModalProps> = ({
    isOpen,
    onClose,
    feature,
    onUpgrade,
    upgrading = false
}) => {
    if (!isOpen) return null;

    const handleUpgrade = () => {
        if (onUpgrade) {
            onUpgrade();
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm">
            <div className="bg-[#0f172a] border border-indigo-500/30 rounded-2xl w-full max-w-md shadow-[0_0_50px_rgba(99,102,241,0.2)] overflow-hidden relative">

                {/* Decorative Gradient */}
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>

                <div className="p-8 text-center relative z-10">
                    <button onClick={onClose} className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors">
                        <X size={20} />
                    </button>

                    <div className="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mx-auto mb-6 ring-1 ring-indigo-500/50">
                        <Lock size={32} className="text-indigo-400" />
                    </div>

                    <h2 className="text-xl font-bold text-white mb-2">Unlock Institutional Grade</h2>
                    <p className="text-sm text-slate-400 mb-6 px-4">
                        The <span className="text-indigo-400 font-bold">{feature}</span> feature is locked in the Free Tier. Upgrade to access real-time macro strategies and institutional PDF reports.
                    </p>

                    <div className="space-y-3 mb-8 text-left bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                        <li className="flex items-center gap-3 text-sm text-slate-300">
                            <CheckCircle size={16} className="text-emerald-400" />
                            <span>Strategist Agent (BigQuery Macro Trends)</span>
                        </li>
                        <li className="flex items-center gap-3 text-sm text-slate-300">
                            <CheckCircle size={16} className="text-emerald-400" />
                            <span>Professional PDF Briefings</span>
                        </li>
                        <li className="flex items-center gap-3 text-sm text-slate-300">
                            <CheckCircle size={16} className="text-emerald-400" />
                            <span>API Access Keys</span>
                        </li>
                    </div>

                    <button
                        onClick={handleUpgrade}
                        disabled={upgrading}
                        className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold rounded-lg shadow-lg shadow-indigo-500/25 transition-all transform hover:scale-[1.02] flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                    >
                        {upgrading ? (
                            <>
                                <Loader2 size={18} className="animate-spin" />
                                UPGRADING...
                            </>
                        ) : (
                            <>
                                <Zap size={18} fill="currentColor" />
                                UPGRADE NOW
                            </>
                        )}
                    </button>

                    <button onClick={onClose} className="mt-4 text-xs text-slate-500 hover:text-white transition-colors">
                        Maybe Later
                    </button>
                </div>
            </div>
        </div>
    );
};
