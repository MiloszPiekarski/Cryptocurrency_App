import React from 'react';
import { Activity, Shield, Eye, Brain, Rocket, Zap, Globe, Lock } from 'lucide-react';

interface AgentMatrixProps {
    data: any[];
    config?: any;
    isPremium?: boolean;
    loading?: boolean;
}

const getIcon = (role: string) => {
    switch (role?.toUpperCase()) {
        case 'SCOUT': return <Activity size={16} />;
        case 'HUNTER': return <Eye size={16} />;
        case 'ANALYST': return <Brain size={16} />;
        case 'DEFENDER': return <Shield size={16} />;
        case 'STRATEGIST': return <Rocket size={16} />;
        case 'SENTINEL': return <Globe size={16} />;
        default: return <Zap size={16} />;
    }
};

export const AgentMatrixWidget: React.FC<AgentMatrixProps> = ({ data, config, isPremium = false, loading = false }) => {
    // Expected Roles order for consistent grid
    const roles = ['SCOUT', 'HUNTER', 'ANALYST', 'DEFENDER', 'SENTINEL', 'STRATEGIST'];

    if (loading) {
        return (
            <div className="h-auto bg-slate-900/50 rounded-xl border border-slate-700/50 p-4 flex flex-col">
                <div className="mb-3 flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                    <span className="text-xs font-bold text-slate-400 font-mono tracking-wider">NEURAL LINKING...</span>
                </div>
                <div className="grid grid-cols-2 gap-3">
                    {[...Array(6)].map((_, i) => (
                        <div key={i} className="h-24 bg-slate-800/50 rounded-lg animate-pulse border border-slate-700/50"></div>
                    ))}
                </div>
            </div>
        )
    }

    return (
        <div className="h-auto bg-slate-900/50 rounded-xl border border-slate-700/50 p-4 flex flex-col">
            <div className="mb-3 flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                <span className="text-xs font-bold text-slate-400 font-mono tracking-wider">AGENT MATRIX</span>
            </div>

            <div className="grid grid-cols-2 gap-3">
                {roles.map(role => {
                    // Premium-locked agents: DEFENDER and STRATEGIST
                    const isPremiumLockedAgent = role === 'STRATEGIST' || role === 'DEFENDER';
                    const isLocked = isPremiumLockedAgent && !isPremium;

                    const agent = data?.find((a: any) => a.role === role);
                    const isActive = !!agent;
                    const isConfigActive = config ? config[role.toLowerCase()]?.active : true;

                    const isBullish = agent?.signal === 'BUY';
                    const isBearish = agent?.signal === 'SELL';

                    // Opacity Logic
                    let opacityClass = !isConfigActive ? 'opacity-30 grayscale' : !isActive ? 'opacity-50' : 'opacity-100';
                    if (isLocked) opacityClass = 'opacity-40 blur-[2px] pointer-events-none select-none';

                    // Real AI Confidence
                    let dynamicConfidence = agent?.confidence || 0;

                    return (
                        <div key={role} className={`relative rounded-lg border p-3 flex flex-col items-center justify-center gap-2 transition-all ${opacityClass} ${isActive && !isLocked
                            ? isBullish ? 'bg-emerald-900/20 border-emerald-500/30 shadow-[0_0_10px_rgba(16,185,129,0.1)]'
                                : isBearish ? 'bg-rose-900/20 border-rose-500/30 shadow-[0_0_10px_rgba(244,63,94,0.1)]'
                                    : 'bg-slate-800/50 border-slate-700'
                            : 'bg-slate-900/30 border-slate-800'}`}>

                            {isLocked && (
                                <div className="absolute inset-0 z-10 flex flex-col items-center justify-center text-slate-400">
                                    <Lock size={16} className="mb-1" />
                                    <span className="text-[8px] font-bold uppercase tracking-widest text-slate-500 animate-pulse">PREMIUM ONLY</span>
                                </div>
                            )}

                            <div className={`${isActive && !isLocked
                                ? isBullish ? 'text-emerald-400'
                                    : isBearish ? 'text-rose-400'
                                        : 'text-slate-200'
                                : 'text-slate-600'}`}>
                                {getIcon(role)}
                            </div>
                            <div className="text-[10px] font-bold text-slate-400 tracking-wide">{role}</div>
                            {isActive && !isLocked && (
                                <>
                                    <div className={`text-[9px] font-mono px-2 py-0.5 rounded-full ${isBullish ? 'text-emerald-400 bg-emerald-500/10' : isBearish ? 'text-rose-400 bg-rose-500/10' : 'text-amber-400 bg-amber-500/10'}`}>
                                        {agent.signal}
                                    </div>
                                    {/* Confidence Bar */}
                                    <div className="w-full h-1 bg-slate-700 rounded-full mt-1 overflow-hidden">
                                        <div
                                            className={`h-full rounded-full transition-all duration-500 ${isBullish ? 'bg-emerald-500' : isBearish ? 'bg-rose-500' : 'bg-amber-500'}`}
                                            style={{ width: `${dynamicConfidence}%` }}
                                        ></div>
                                    </div>
                                    <div className="text-[8px] text-slate-500 font-mono mt-0.5">{dynamicConfidence}% CF</div>
                                </>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
