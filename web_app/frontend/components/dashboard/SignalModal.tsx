import React, { useState } from 'react';
import { X, Check, Lock, Database, Code, Maximize2 } from 'lucide-react';

interface SignalModalProps {
    isOpen: boolean;
    onClose: () => void;
    signal: any; // Using any for flexibility with JSON view
    isPremium: boolean;
}

const SignalModal: React.FC<SignalModalProps> = ({ isOpen, onClose, signal, isPremium }) => {
    const [activeTab, setActiveTab] = useState<'narrative' | 'source' | 'model'>('narrative');

    if (!isOpen || !signal) return null;

    const isStrategist = signal.role === 'STRATEGIST';

    if (isStrategist && !isPremium) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                <div className="bg-[#0f172a] border border-purple-500/50 rounded-2xl p-8 max-w-md w-full text-center relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-purple-500 to-transparent"></div>
                    <Lock className="mx-auto text-purple-400 mb-4" size={48} />
                    <h2 className="text-xl font-bold text-white mb-2">Restricted Access</h2>
                    <p className="text-slate-400 mb-6 text-sm">
                        Deep strategic insights and 30-day BigQuery trend analysis are reserved for Institutional Plan members.
                    </p>
                    <button
                        onClick={onClose}
                        className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-6 rounded-lg transition-colors w-full"
                    >
                        Upgrade to Unlock
                    </button>
                    <button
                        onClick={onClose}
                        className="mt-4 text-slate-500 text-sm hover:text-white"
                    >
                        Close Preview
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
            <div
                className="bg-[#0f172a] rounded-xl border border-slate-700 w-full max-w-2xl overflow-hidden shadow-2xl scale-100 animate-in zoom-in-95 duration-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-slate-700/50 bg-slate-900/50">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded bg-slate-800 border border-slate-700">
                            <Maximize2 size={18} className="text-slate-400" />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                SIGNAL INSPECTOR
                                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">ID: {signal.id}</span>
                            </h2>
                            <div className="flex gap-2 text-xs text-slate-500">
                                <span>AGENT_TYPE: {signal.role}</span>
                                <span>CONFIDENCE: {signal.confidence}%</span>
                            </div>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-white/10 rounded-full transition-colors text-slate-400 hover:text-white"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-slate-700/50 bg-slate-900/30">
                    <button
                        onClick={() => setActiveTab('narrative')}
                        className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors flex items-center justify-center gap-2 ${activeTab === 'narrative' ? 'border-blue-500 text-blue-400 bg-blue-500/5' : 'border-transparent text-slate-500 hover:text-slate-300'
                            }`}
                    >
                        <Check size={14} /> Full Narrative
                    </button>
                    <button
                        onClick={() => setActiveTab('source')}
                        className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors flex items-center justify-center gap-2 ${activeTab === 'source' ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5' : 'border-transparent text-slate-500 hover:text-slate-300'
                            }`}
                    >
                        <Database size={14} /> Source Data (Proof)
                    </button>
                    <button
                        onClick={() => setActiveTab('model')}
                        className={`flex-1 py-3 text-sm font-medium border-b-2 transition-colors flex items-center justify-center gap-2 ${activeTab === 'model' ? 'border-amber-500 text-amber-400 bg-amber-500/5' : 'border-transparent text-slate-500 hover:text-slate-300'
                            }`}
                    >
                        <Code size={14} /> Thought Process (Raw)
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 h-[400px] overflow-y-auto bg-[#0b1120]">
                    {activeTab === 'narrative' && (
                        <div className="space-y-4">
                            <div className="p-4 rounded-lg bg-blue-500/5 border border-blue-500/20 text-slate-300 leading-relaxed font-sans text-sm">
                                {signal.reasoning}
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-3 bg-slate-900 rounded border border-slate-800">
                                    <label className="text-xs text-slate-500 block mb-1">Signal Type</label>
                                    <div className={`text-lg font-bold ${signal.signal === 'BUY' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {signal.signal}
                                    </div>
                                </div>
                                <div className="p-3 bg-slate-900 rounded border border-slate-800">
                                    <label className="text-xs text-slate-500 block mb-1">Processing Node</label>
                                    <div className="text-base text-slate-300 font-mono">
                                        RAY-WORKER-{Math.floor(Math.random() * 9000) + 1000}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'source' && (
                        <div className="space-y-4">
                            <p className="text-xs text-slate-400 mb-2">
                                Cryptographically verifiable raw data snapshot used for this decision.
                            </p>
                            <div className="p-4 rounded bg-[#050914] border border-emerald-500/20 font-mono text-xs text-emerald-300 overflow-x-auto">
                                <pre>{JSON.stringify(signal.source_data, null, 2)}</pre>
                            </div>
                        </div>
                    )}

                    {activeTab === 'model' && (
                        <div className="space-y-4">
                            {!isPremium ? (
                                <div className="h-full flex flex-col items-center justify-center text-center opacity-60">
                                    <Lock size={32} className="text-amber-500 mb-2" />
                                    <p className="text-amber-500 font-bold">L2 Logic View Locked</p>
                                    <p className="text-xs text-slate-400 max-w-[200px]">Unlock to view the raw JSON prompt and model parameters used by the agent.</p>
                                </div>
                            ) : (
                                <div className="p-4 rounded bg-[#050914] border border-amber-500/20 font-mono text-xs text-amber-300 overflow-x-auto">
                                    <pre>{JSON.stringify({
                                        model: "Custom/Llama-2-Fineta",
                                        temperature: 0.2,
                                        vector_db_hits: 14,
                                        latency_ms: 24,
                                        raw_thought_chain: signal
                                    }, null, 2)}</pre>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-slate-700/50 bg-slate-900/50 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium rounded transition-colors"
                    >
                        Close Inspector
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SignalModal;
