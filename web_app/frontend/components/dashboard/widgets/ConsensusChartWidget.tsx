import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { Zap } from 'lucide-react';

interface ConsensusChartProps {
    data: any;
}

export const ConsensusChartWidget: React.FC<ConsensusChartProps> = ({ data }) => {
    if (!data) return null;

    const confidence = data.confidence_score || 0;
    const verdict = data.verdict || "HOLD";

    // Gauge Data
    const chartData = [
        { name: 'Confidence', value: confidence },
        { name: 'Remaining', value: 100 - confidence },
    ];

    const COLORS = verdict === 'BUY' ? ['#10b981', '#1e293b'] :
        verdict === 'SELL' ? ['#f43f5e', '#1e293b'] :
            ['#f59e0b', '#1e293b']; // Amber for HOLD

    return (
        <div className="h-full flex flex-col p-4 bg-slate-900/50 rounded-xl border border-slate-700/50">
            <div className="flex items-center gap-2 mb-2">
                <Zap size={14} className={verdict === 'BUY' ? 'text-emerald-400' : verdict === 'SELL' ? 'text-rose-400' : 'text-amber-400'} />
                <span className="text-xs font-bold text-slate-400 font-mono tracking-wider">SWARM CONSENSUS</span>
            </div>

            <div className="flex-1 flex items-center justify-center relative">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={35}
                            outerRadius={45}
                            startAngle={90}
                            endAngle={-270}
                            dataKey="value"
                            stroke="none"
                        >
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                    </PieChart>
                </ResponsiveContainer>

                {/* Center Text */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <div className={`text-xl font-black ${verdict === 'BUY' ? 'text-emerald-400' : verdict === 'SELL' ? 'text-rose-400' : 'text-amber-400'}`}>
                        {verdict}
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">
                        {confidence.toFixed(0)}%
                    </div>
                </div>
            </div>
        </div>
    );
};
