"use client";

import React, { useRef, useMemo, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Instances, Instance } from '@react-three/drei';
import * as THREE from 'three';
import { EffectComposer, Bloom } from '@react-three/postprocessing';

// A single animated agent connection line
function ConnectionLine({ start, end, color }: { start: THREE.Vector3, end: THREE.Vector3, color: string }) {
    // Explicitly casting ref to any to bypass SVG line element type conflict in React
    const ref = useRef<any>(null);

    // Animate opacity or width for 'transmission' effect
    useFrame((state) => {
        if (ref.current && ref.current.material) {
            // Cast material to LineBasicMaterial to access opacity
            (ref.current.material as THREE.LineBasicMaterial).opacity = 0.2 + Math.sin(state.clock.elapsedTime * 5 + start.x) * 0.2;
        }
    })

    return (
        <line ref={ref}>
            <bufferGeometry>
                <bufferAttribute
                    attach="attributes-position"
                    args={[new Float32Array([...start.toArray(), ...end.toArray()]), 3]}
                />
            </bufferGeometry>
            <lineBasicMaterial color={color} transparent opacity={0.3} blending={THREE.AdditiveBlending} />
        </line>
    )
}

function NeuralNetwork({ count = 100 }) {
    const group = useRef<THREE.Group>(null);

    // Generate nodes (Agents)
    const nodes = useMemo(() => {
        const temp: { position: THREE.Vector3, type: string }[] = [];
        for (let i = 0; i < count; i++) {
            const r = 4;
            const theta = THREE.MathUtils.randFloatSpread(360);
            const phi = THREE.MathUtils.randFloatSpread(360);
            const x = r * Math.sin(theta) * Math.cos(phi);
            const y = r * Math.sin(theta) * Math.sin(phi);
            const z = r * Math.cos(theta);
            const type = Math.random() > 0.8 ? 'hunter' : (Math.random() > 0.5 ? 'analyst' : 'scout');
            temp.push({ position: new THREE.Vector3(x, y, z), type });
        }
        return temp;
    }, [count]);

    // Generate connections
    const connections = useMemo(() => {
        const conns: { start: THREE.Vector3, end: THREE.Vector3 }[] = [];
        nodes.forEach((node, i) => {
            const target1 = nodes[Math.floor(Math.random() * count)];
            const target2 = nodes[Math.floor(Math.random() * count)];
            if (node !== target1) conns.push({ start: node.position, end: target1.position });
            if (node !== target2) conns.push({ start: node.position, end: target2.position });
        });
        return conns;
    }, [nodes, count]);

    useFrame((state) => {
        if (group.current) {
            group.current.rotation.y += 0.002;
            group.current.rotation.x += 0.001;
        }
    });

    return (
        <group ref={group}>
            {/* Nodes */}
            <Instances range={count}>
                <sphereGeometry args={[0.08, 16, 16]} />
                <meshBasicMaterial />
                {nodes.map((node, i) => (
                    <Instance
                        key={i}
                        position={node.position}
                        color={node.type === 'hunter' ? "#ef4444" : (node.type === 'analyst' ? "#06b6d4" : "#10b981")}
                    />
                ))}
            </Instances>

            {/* Connections */}
            {connections.slice(0, 150).map((conn, i) => (
                <ConnectionLine key={i} start={conn.start} end={conn.end} color="#1e3a8a" />
            ))}
        </group>
    );
}

interface HiveMindWidgetProps {
    data: any;
}

export default function HiveMindWidget({ data }: HiveMindWidgetProps) {
    // Agents online simulation derived from data or default
    const agentsOnline = data ? (data.agents_active || 5) : 0;
    const scanData = data;

    return (
        <div className="w-full h-full relative">
            <div className="absolute top-4 left-4 z-10 flex flex-col gap-1 pointer-events-none">
                <div className="text-blue-400 font-mono text-xs">HIVE MIND STATUS</div>
                <div className="text-white text-xl font-bold flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    {scanData ? scanData.swarm_status : "CONNECTING..."}
                </div>
                <div className="text-slate-400 text-xs mt-2">
                    AGENTS ACTIVE: <span className="text-white font-mono">{agentsOnline} / 1M (Sim)</span>
                </div>
                {scanData && (
                    <div className="mt-4 bg-black/50 p-3 rounded border border-white/10 backdrop-blur-md">
                        <div className="text-xs text-slate-400">VERDICT</div>
                        <div className={`text-2xl font-bold ${scanData.verdict === 'BUY' ? 'text-green-400' : (scanData.verdict === 'SELL' ? 'text-red-400' : 'text-yellow-400')}`}>
                            {scanData.verdict}
                        </div>
                        <div className="text-xs text-slate-400 mt-2">SENTIMENT</div>
                        <div className="text-sm font-mono text-blue-300">
                            {scanData.collective_sentiment > 0 ? "+" : ""}{scanData.collective_sentiment}
                        </div>

                        {/* BigQuery Insight */}
                        {scanData.macro_strategy && (
                            <div className="mt-3 pt-3 border-t border-white/10">
                                <div className="text-[10px] text-purple-400 uppercase tracking-wider">Strategic Outlook</div>
                                <div className="text-sm font-bold text-white">
                                    {scanData.macro_strategy}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <Canvas camera={{ position: [0, 0, 8], fov: 60 }} gl={{ antialias: false, alpha: true }}>
                <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#06b6d4" />

                <NeuralNetwork count={50} />

                <EffectComposer>
                    <Bloom luminanceThreshold={0} luminanceSmoothing={0.9} height={300} intensity={0.5} />
                </EffectComposer>
            </Canvas>
        </div>
    );
}
