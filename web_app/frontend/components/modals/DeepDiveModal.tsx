import React, { useState, useEffect } from 'react';
import { X, Cpu, Database, ChevronRight, Loader2 } from 'lucide-react';

interface DeepDiveModalProps {
    isOpen: boolean;
    onClose: () => void;
    data: any;
}

export const DeepDiveModal: React.FC<DeepDiveModalProps> = ({ isOpen, onClose, data }) => {
    const [loading, setLoading] = useState(true);

    // Simulate loading state when modal opens with new data
    useEffect(() => {
        if (isOpen && data) {
            setLoading(true);
            // Quick delay to show loading state, then reveal content
            const timer = setTimeout(() => setLoading(false), 500);
            return () => clearTimeout(timer);
        }
    }, [isOpen, data?.id]);

    if (!isOpen) return null;

    // Show loading state
    if (loading || !data) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl p-12 flex flex-col items-center justify-center shadow-2xl">
                    <Loader2 size={48} className="text-blue-500 animate-spin mb-4" />
                    <div className="text-lg font-bold text-white mb-2">Analyzing Neural Pathways...</div>
                    <div className="text-xs text-slate-400 font-mono">Extracting AI reasoning from Vertex AI</div>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="p-4 border-b border-slate-700 flex justify-between items-center bg-slate-900/50">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
                            <Cpu size={20} />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-white tracking-tight">Proof of Intelligence</h3>
                            <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
                                <span>AGENT ID: {data.id}</span>
                                <ChevronRight size={10} />
                                <span className={data.signal === 'BUY' ? 'text-emerald-400' : data.signal === 'SELL' ? 'text-rose-400' : 'text-amber-400'}>{data.signal}</span>
                                <span className="text-slate-600">|</span>
                                <span className="text-slate-300">{data.confidence}% CONF</span>
                            </div>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-800 rounded-full text-slate-400 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6 space-y-6">

                    {/* Live Price Reference */}
                    {data.source_data?.price && (
                        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center gap-3">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                            <span className="text-xs text-emerald-400 font-mono">
                                LIVE ANALYSIS @ <span className="font-bold text-emerald-300">${data.source_data.price.toLocaleString()}</span>
                            </span>
                        </div>
                    )}

                    {/* Formatting the Reasoning */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
                            <Database size={12} className="text-purple-400" />
                            AI Reasoning Logic
                        </div>
                        <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-sm text-slate-300 leading-relaxed font-mono whitespace-pre-wrap">
                            {data.reasoning || "No reasoning data available."}
                        </div>
                    </div>

                    {/* Source Data (Inputs) */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
                            <Database size={12} className="text-blue-400" />
                            Source Data (Input)
                        </div>
                        <pre className="p-4 bg-black rounded-xl border border-slate-800 text-[10px] text-emerald-400 font-mono overflow-x-auto">
                            {JSON.stringify(data.source_data, null, 2)}
                        </pre>
                    </div>

                </div>

                {/* Footer */}
                <div className="p-4 border-t border-slate-800 bg-slate-900/50 text-right">
                    <button onClick={onClose} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded transition-colors">
                        CLOSE INSPECTOR
                    </button>
                </div>
            </div>
        </div>
    );
};
