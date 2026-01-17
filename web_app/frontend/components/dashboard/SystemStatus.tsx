'use client';

import { useEffect, useState } from 'react';
import { Brain, Zap, Activity, Database, Cpu } from 'lucide-react';

interface SystemHealth {
    hiveMind: boolean;
    quantum: boolean;
    blockchain: boolean;
    redis: boolean;
    agents?: number;
}

export function SystemStatus() {
    const [health, setHealth] = useState<SystemHealth>({
        hiveMind: false,
        quantum: false,
        blockchain: false,
        redis: false
    });

    useEffect(() => {
        const checkSystems = async () => {
            try {
                // Check Hive Mind
                const hiveRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/agents/scan/BTCUSDT`);
                const hiveData = await hiveRes.json();

                // Check Quantum
                const quantumRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/quantum/optimize`);
                const quantumData = await quantumRes.json();

                // Check Blockchain
                const whaleRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/onchain/whales`);
                const whaleData = await whaleRes.json();

                setHealth({
                    hiveMind: !hiveData.error,
                    quantum: !quantumData.error,
                    blockchain: !whaleData.error,
                    redis: true,
                    agents: hiveData.agents_online || 0
                });
            } catch (e) {
                console.error('System check failed', e);
            }
        };

        checkSystems();
        const interval = setInterval(checkSystems, 10000);
        return () => clearInterval(interval);
    }, []);

    const systems = [
        { name: 'Ray Hive Mind', status: health.hiveMind, icon: Brain, detail: `${health.agents || 0} Agents` },
        { name: 'Quantum Engine', status: health.quantum, icon: Cpu, detail: 'Cirq Ready' },
        { name: 'Blockchain Node', status: health.blockchain, icon: Database, detail: 'Ethereum' },
        { name: 'Redis Streams', status: health.redis, icon: Zap, detail: 'WebSocket' }
    ];

    return (
        <div className="bg-gradient-to-br from-purple-900/20 to-blue-900/20 rounded-xl border border-purple-500/30 p-6">
            <div className="flex items-center gap-2 mb-4">
                <Activity className="w-5 h-5 text-purple-400" />
                <h3 className="font-bold text-white">DEEP TECH SYSTEMS</h3>
            </div>

            <div className="grid grid-cols-2 gap-3">
                {systems.map((sys) => (
                    <div key={sys.name} className="bg-black/40 rounded-lg p-3 border border-gray-700">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                                <sys.icon className="w-4 h-4 text-purple-400" />
                                <span className="text-sm font-medium text-gray-300">{sys.name}</span>
                            </div>
                            <div className={`w-2 h-2 rounded-full ${sys.status ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                        </div>
                        <p className="text-xs text-gray-500">{sys.detail}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
