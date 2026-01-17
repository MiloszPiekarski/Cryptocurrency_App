"use client";

import React, { useRef, useMemo, Suspense } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import {
    Stars,
    Float,
    Sparkles,
    ScrollControls,
    Scroll,
    useScroll,
    Line,
    Icosahedron,
    MeshDistortMaterial,
    Points,
    PointMaterial,
    Ring
} from "@react-three/drei";
import {
    EffectComposer,
    Bloom,
    Noise,
    Vignette,
    ChromaticAberration
} from "@react-three/postprocessing";
import * as THREE from "three";
import { Cpu, Shield, Zap, Globe, Activity, BarChart3, BrainCircuit, Users } from "lucide-react";

// --- PROFESSIONAL ASSETS ---

// 1. The "Hive Mind" - Organized Network of Agents
function AgentNetwork({ count = 800 }) {
    const points = useMemo(() => {
        const p = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            // Create a structured shell, not random chaos
            const theta = THREE.MathUtils.randFloatSpread(360);
            const phi = THREE.MathUtils.randFloatSpread(360);
            const r = 3.5;
            const x = r * Math.sin(theta) * Math.cos(phi);
            const y = r * Math.sin(theta) * Math.sin(phi);
            const z = r * Math.cos(theta);
            p[i * 3] = x;
            p[i * 3 + 1] = y;
            p[i * 3 + 2] = z;
        }
        return p;
    }, [count]);

    const ref = useRef<THREE.Points>(null);
    useFrame((state, delta) => {
        if (ref.current) {
            ref.current.rotation.y += delta * 0.05;
        }
    })

    return (
        <points ref={ref}>
            <bufferGeometry>
                <bufferAttribute attach="attributes-position" args={[points, 3]} />
            </bufferGeometry>
            <PointMaterial transparent color="#00f0ff" size={0.03} sizeAttenuation={true} depthWrite={false} opacity={0.6} />
        </points>
    )
}

// 2. The "Digital Twin" - Wireframe Globe
function DigitalTwinGlobe() {
    return (
        <group>
            {/* Main Grid */}
            <mesh>
                <sphereGeometry args={[2.5, 32, 32]} />
                <meshBasicMaterial color="#3b82f6" wireframe transparent opacity={0.15} />
            </mesh>
            {/* Inner Core */}
            <mesh>
                <sphereGeometry args={[2.3, 32, 32]} />
                <meshBasicMaterial color="#000000" />
            </mesh>
            {/* Scanning Line */}
            <Ring args={[2.6, 2.65, 64]} rotation={[1.5, 0, 0]}>
                <meshBasicMaterial color="#a855f7" transparent opacity={0.5} side={THREE.DoubleSide} />
            </Ring>
        </group>
    )
}

// 3. The "Central Intelligence" - The Main Crystal
function CentralIntelligence() {
    return (
        <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
            <mesh>
                <octahedronGeometry args={[1, 0]} />
                <meshStandardMaterial
                    color="#ffffff"
                    roughness={0.1}
                    metalness={0.9}
                    emissive="#00f0ff"
                    emissiveIntensity={0.2}
                />
            </mesh>
            <mesh scale={[1.05, 1.05, 1.05]}>
                <octahedronGeometry args={[1, 0]} />
                <meshBasicMaterial color="#00f0ff" wireframe transparent opacity={0.2} />
            </mesh>
        </Float>
    )
}

// --- SCENE ORCHESTRATOR ---
function SceneDirector() {
    const scroll = useScroll();
    const groupRef = useRef<THREE.Group>(null);

    useFrame((state, delta) => {
        // Adjusted for 6 pages (5 scroll segments)
        // r1..r5 not strictly needed if we just map offset directly to z-position

        if (groupRef.current) {
            // Smooth rotation for the whole system
            groupRef.current.rotation.y = -scroll.offset * Math.PI * 2.5;

            // Z-axis movement: User flies through the system
            // Extended depth for 6 pages
            groupRef.current.position.z = scroll.offset * 2.5;
        }
    });

    return (
        <group ref={groupRef}>
            <CentralIntelligence />
            <group scale={1.5}>
                <AgentNetwork />
            </group>
            <group scale={1.2}>
                <DigitalTwinGlobe />
            </group>
        </group>
    )
}

export default function LandingScene() {
    return (
        <div className="w-full h-screen absolute inset-0 -z-10 bg-[#050505]">
            <Canvas camera={{ position: [0, 0, 7], fov: 40 }} gl={{ antialias: true, toneMapping: THREE.ReinhardToneMapping, toneMappingExposure: 1.5 }}>
                <Suspense fallback={null}>
                    <ScrollControls pages={6} damping={0.3}>

                        <SceneDirector />

                        {/* STUDIO LIGHTING - Clean & Professional */}
                        <ambientLight intensity={0.5} color="#ffffff" />
                        <directionalLight position={[5, 5, 5]} intensity={2} color="#ffffff" />
                        <directionalLight position={[-5, -5, -5]} intensity={1} color="#3b82f6" />
                        <Sparkles count={200} size={2} scale={10} color="#ffffff" opacity={0.2} speed={0.2} />

                        {/* SUBTLE POST PROCESSING - "Apple" Quality */}
                        <EffectComposer>
                            <Bloom luminanceThreshold={0.8} luminanceSmoothing={0.5} height={300} intensity={0.5} />
                            <Noise opacity={0.02} />
                            <Vignette eskil={false} offset={0.1} darkness={0.8} />
                        </EffectComposer>

                        {/* HTML CONTENT - THE NARRATIVE */}
                        <Scroll html style={{ width: '100%', height: '100%' }}>

                            {/* 1. HERO: The Promise */}
                            <div className="w-screen h-screen flex flex-col items-center justify-center p-8 text-center pointer-events-none">
                                <div className="glass-panel px-6 py-2 rounded-full mb-8 border border-white/10 bg-white/5 backdrop-blur-md">
                                    <span className="text-cyan-400 font-mono text-xs tracking-[0.2em] font-bold">EUROPE'S FIRST AI HEDGE FUND</span>
                                </div>
                                <h1 className="text-5xl md:text-8xl font-bold tracking-tight text-white mb-6 drop-shadow-2xl">
                                    TURBO-PLAN <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">X</span>
                                </h1>
                                <p className="text-slate-400 max-w-2xl text-lg md:text-xl font-light leading-relaxed mb-10">
                                    Autonomous Investment System. <br />
                                    Analyzing <strong>100,000 simulations</strong> per second, predicting trends, and securing your capital.
                                    Operates 24/7. Without emotion.
                                </p>
                                <div className="animate-bounce mt-10 text-slate-600 text-[10px] uppercase tracking-widest">
                                    Scroll to Explore System Architecture
                                </div>
                            </div>

                            {/* 2. HIVE MIND */}
                            <div className="w-screen h-screen flex items-center justify-end px-10 md:px-32 pointer-events-none">
                                <div className="max-w-xl text-right">
                                    <div className="flex items-center justify-end gap-4 mb-6 text-cyan-400">
                                        <Users size={32} />
                                        <h2 className="text-4xl font-bold tracking-tight">HIVE-MIND</h2>
                                    </div>
                                    <h3 className="text-2xl text-white mb-4 font-light">10,000+ Autonomous Agents</h3>
                                    <p className="text-slate-400 text-lg leading-relaxed glass-panel p-8 rounded-2xl border-r-4 border-cyan-500 bg-black/40 backdrop-blur-xl">
                                        This is not just an algorithm. It is a <strong>Superorganism</strong>.
                                        <br /><br />
                                        Thousands of micro-agents (Scouts, Analysts, Hunters) constantly scan market niches, fight for survival, and adapt strategies to market conditions (Bull/Bear/Crab).
                                    </p>
                                </div>
                            </div>

                            {/* 3. DIGITAL TWIN */}
                            <div className="w-screen h-screen flex items-center justify-start px-10 md:px-32 pointer-events-none">
                                <div className="max-w-xl text-left">
                                    <div className="flex items-center gap-4 mb-6 text-blue-500">
                                        <Globe size={32} />
                                        <h2 className="text-4xl font-bold tracking-tight">DIGITAL TWIN</h2>
                                    </div>
                                    <h3 className="text-2xl text-white mb-4 font-light">Future Simulation</h3>
                                    <p className="text-slate-400 text-lg leading-relaxed glass-panel p-8 rounded-2xl border-l-4 border-blue-500 bg-black/40 backdrop-blur-xl">
                                        We create a <strong>Market Digital Twin</strong>.
                                        <br /><br />
                                        The system analyzes orderbooks, whale movements, and liquidity, performing <strong>domino effect</strong> simulations before taking any position. We don't guess. We simulate.
                                    </p>
                                </div>
                            </div>

                            {/* 4. GLOBAL CONSCIOUSNESS */}
                            <div className="w-screen h-screen flex items-center justify-center px-10 pointer-events-none">
                                <div className="max-w-4xl text-center">
                                    <div className="flex flex-col items-center gap-4 mb-8 text-purple-400">
                                        <Activity size={48} />
                                        <h2 className="text-5xl font-bold tracking-tight">GLOBAL CONSCIOUSNESS</h2>
                                    </div>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-left">
                                        <div className="glass-panel p-6 rounded-xl border-t-4 border-purple-500 bg-black/50">
                                            <h4 className="text-white font-bold mb-2 flex items-center gap-2"><BrainCircuit size={16} /> AI Sentiment</h4>
                                            <p className="text-slate-400 text-sm">24/7 analysis of Twitter, Reddit, and News. Real-time FOMO/FUD detection.</p>
                                        </div>
                                        <div className="glass-panel p-6 rounded-xl border-t-4 border-purple-500 bg-black/50">
                                            <h4 className="text-white font-bold mb-2 flex items-center gap-2"><BarChart3 size={16} /> Alternative Data</h4>
                                            <p className="text-slate-400 text-sm">Satellite imagery, air traffic, energy costs. Macroeconomics impacting crypto.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* 5. FAIR PRICING MODEL - PDF REQUIREMENT */}
                            <div className="w-screen h-screen flex flex-row items-center justify-center pointer-events-none px-4">
                                <div className="max-w-4xl text-center glass-panel p-8 md:p-12 rounded-3xl border border-white/10 bg-gradient-to-tr from-emerald-900/40 to-black/80 backdrop-blur-xl">
                                    <div className="flex justify-center mb-6">
                                        <Zap size={48} className="text-yellow-400" />
                                    </div>
                                    <h2 className="text-3xl md:text-5xl font-bold text-white mb-8 tracking-tight">ZERO MANAGEMENT FEES</h2>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center divide-y md:divide-y-0 md:divide-x divide-white/10">
                                        <div className="p-4">
                                            <div className="text-4xl font-bold text-white mb-2">0 PLN</div>
                                            <div className="text-xs text-slate-400 tracking-[0.2em] font-bold">STARTING COST</div>
                                        </div>
                                        <div className="p-4">
                                            <div className="text-4xl font-bold text-white mb-2">0 PLN</div>
                                            <div className="text-xs text-slate-400 tracking-[0.2em] font-bold">MONTHLY FEE</div>
                                        </div>
                                        <div className="p-4">
                                            <div className="text-4xl font-bold text-emerald-400 mb-2">20%</div>
                                            <div className="text-xs text-emerald-600/80 tracking-[0.2em] font-bold">SUCCESS FEE ONLY</div>
                                        </div>
                                    </div>
                                    <p className="mt-8 text-slate-400 font-light italic border-t border-white/5 pt-6">"We only make money when the AI makes money for you."</p>
                                </div>
                            </div>

                            {/* 6. RISK ENGINE & CTA */}
                            <div className="w-screen h-screen flex flex-col items-center justify-center pointer-events-none">
                                <div className="mb-12 text-center">
                                    <Shield size={64} className="text-emerald-500 mx-auto mb-6" />
                                    <h2 className="text-5xl font-bold text-white mb-4">ELITE RISK ENGINEERING</h2>
                                    <p className="text-slate-400">Capital protection at hedge fund levels.</p>
                                </div>

                                <div className="glass-panel p-10 rounded-3xl border border-white/10 bg-gradient-to-b from-white/10 to-transparent backdrop-blur-2xl text-center">
                                    <p className="text-white font-mono mb-6 tracking-widest">READY TO JOIN THE ELITE?</p>
                                    {/* Button handled by overlay */}
                                    <div className="text-sm text-cyan-400 animate-pulse">
                                        INITIALIZE SYSTEM ABOVE
                                    </div>
                                </div>
                            </div>

                        </Scroll>
                    </ScrollControls>
                </Suspense>
            </Canvas>
        </div>
    );
}
