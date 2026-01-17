'use client';
import { Line, LineChart, ResponsiveContainer, YAxis } from 'recharts';

export function Sparkline({ data, color }: { data: any[]; color: string }) {
    if (!data || data.length === 0) return <div className="h-full w-full bg-gray-900/50 animate-pulse rounded" />;

    return (
        <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
                <Line
                    type="monotone"
                    dataKey="value"
                    stroke={color}
                    strokeWidth={2}
                    dot={false}
                    isAnimationActive={false}
                />
            </LineChart>
        </ResponsiveContainer>
    );
}
