'use client';
import { useEffect, useState, useRef } from 'react';
import { Terminal } from 'lucide-react';

export function LiveLogTerminal() {
    const [logs, setLogs] = useState<string[]>(["[SYSTEM] Initializing Neural Uplink...", "[SYSTEM] Connecting to Ray Cluster..."]);
    const endRef = useRef<HTMLDivElement>(null);

    const addLog = (msg: string) => {
        const time = new Date().toISOString().split('T')[1].slice(0, 12);
        setLogs(prev => [...prev.slice(-20), `[${time}] ${msg}`]);
    };

    useEffect(() => {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

        const fetchRealLogs = async () => {
            // 1. Ping Agents
            try {
                const t1 = Date.now();
                const res = await fetch(`${API_URL}/api/v1/agents/scan/BTCUSDT`);
                const data = await res.json();
                const lat = Date.now() - t1;

                if (data.hive_scan && data.hive_scan.swarm_breakdown) {
                    // Log the composite verdict
                    addLog(`[HIVE] Swarm Verdict: ${data.hive_scan.verdict} (Confidence: ${(data.hive_scan.collective_sentiment * 100).toFixed(0)}%). Agents: ${data.hive_scan.agents_active}`);

                    // Randomly log 1-2 specific agent actions to look "busy" but not flood
                    const specific = data.hive_scan.swarm_breakdown[Math.floor(Math.random() * data.hive_scan.swarm_breakdown.length)];
                    if (specific) {
                        if (specific.role === 'SCOUT') {
                            addLog(`[SCOUT] ${specific.id} report: ${specific.message} (Score: ${specific.anomaly_score})`);
                        } else if (specific.role === 'HUNTER') {
                            addLog(`[HUNTER] ${specific.id} testing ${specific.strategy}: Signal ${specific.signal} (${specific.confidence}%)`);
                        } else if (specific.role === 'ANALYST') {
                            addLog(`[ANALYST] ${specific.id} news scan: Impact ${specific.news_impact}`);
                        }
                    }

                } else {
                    addLog(`[HIVE] Swarm Status: ${data.swarm_status}`);
                }
            } catch (e) {
                addLog("[ERROR] Ray Cluster silent. Retrying...");
            }
        };

        const fetchQuantum = async () => {
            try {
                const res = await fetch(`${API_URL}/api/v1/quantum/optimize`);
                const data = await res.json();
                if (data.algo) {
                    addLog(`[QUANTUM] ${data.algo} finished. States: ${data.quantum_states_explored}`);
                    if (data.signals) {
                        addLog(`[QUANTUM] RECOMMENDS: BTC:${data.signals.BTC} ETH:${data.signals.ETH}`);
                    }
                }
            } catch (e) { }
        };

        const fetchWhales = async () => {
            try {
                const res = await fetch(`${API_URL}/api/v1/onchain/whales`);
                const data = await res.json();
                if (data.whale_transactions && data.whale_transactions.length > 0) {
                    data.whale_transactions.forEach((tx: any) => {
                        addLog(`[WHALE] ALERT: ${tx.value.toFixed(1)} ETH moved. Hash: ${tx.hash.substring(0, 8)}...`);
                    });
                } else {
                    addLog(`[CHAIN] Mempool scan complete. No whales > 50 ETH.`);
                }
            } catch (e) { }
        };

        // Schedule real pings
        const i1 = setInterval(fetchRealLogs, 2500); // Fast agent pings
        const i2 = setInterval(fetchQuantum, 8000);  // Slower quantum
        const i3 = setInterval(fetchWhales, 12000); // Whale scan

        return () => { clearInterval(i1); clearInterval(i2); clearInterval(i3); };
    }, []);

    // Auto-scroll
    useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [logs]);

    return (
        <div className="bg-black font-mono text-xs p-4 rounded-xl border border-green-500/30 h-[300px] overflow-hidden flex flex-col shadow-[0_0_15px_rgba(0,255,0,0.1)]">
            <div className="flex items-center gap-2 text-green-500 mb-2 border-b border-green-900 pb-2">
                <Terminal size={14} />
                <span className="font-bold">AI KERNEL OUPUT (L1 LOGS)</span>
                <div className="ml-auto flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse delay-75" />
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse delay-150" />
                </div>
            </div>
            <div className="flex-1 overflow-y-auto space-y-1">
                {logs.map((log, i) => (
                    <div key={i} className="text-green-400/90 break-all font-mono">
                        <span className="text-green-600 mr-2 opacity-50">{'>'}</span>
                        {log}
                    </div>
                ))}
                <div ref={endRef} />
            </div>
        </div>
    );
}
