'use client';

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

// 🌀 THE MAELSTROM - Money Black Hole
function MaelstromParticles({ count = 5000, intensity = 1 }) {
    const ref = useRef<THREE.Points>(null);

    const positions = useMemo(() => {
        const pos = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            // Spiral distribution
            const angle = Math.random() * Math.PI * 2;
            const radius = 0.5 + Math.random() * 3;
            const height = (Math.random() - 0.5) * 2;

            pos[i * 3] = Math.cos(angle) * radius;
            pos[i * 3 + 1] = height;
            pos[i * 3 + 2] = Math.sin(angle) * radius;
        }
        return pos;
    }, [count]);

    const colors = useMemo(() => {
        const cols = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
            // Mix of gold, red, and dark particles
            const colorType = Math.random();
            if (colorType < 0.4) {
                // Gold
                cols[i * 3] = 1.0;
                cols[i * 3 + 1] = 0.84;
                cols[i * 3 + 2] = 0.0;
            } else if (colorType < 0.6) {
                // Blood Red
                cols[i * 3] = 0.8;
                cols[i * 3 + 1] = 0.1;
                cols[i * 3 + 2] = 0.1;
            } else {
                // Dark Purple
                cols[i * 3] = 0.3;
                cols[i * 3 + 1] = 0.1;
                cols[i * 3 + 2] = 0.4;
            }
        }
        return cols;
    }, [count]);

    useFrame((state, delta) => {
        if (!ref.current) return;

        const positions = ref.current.geometry.attributes.position.array as Float32Array;

        for (let i = 0; i < count; i++) {
            const idx = i * 3;
            const x = positions[idx];
            const z = positions[idx + 2];
            const y = positions[idx + 1];

            // Calculate current radius and angle
            const radius = Math.sqrt(x * x + z * z);
            const angle = Math.atan2(z, x);

            // Spiral inward (being sucked into the void)
            const newRadius = radius - delta * 0.3 * intensity;
            const newAngle = angle + delta * (1 + 1 / (radius + 0.5)) * intensity;

            if (newRadius < 0.2) {
                // Respawn at edge
                const respawnAngle = Math.random() * Math.PI * 2;
                const respawnRadius = 2.5 + Math.random() * 1;
                positions[idx] = Math.cos(respawnAngle) * respawnRadius;
                positions[idx + 2] = Math.sin(respawnAngle) * respawnRadius;
                positions[idx + 1] = (Math.random() - 0.5) * 2;
            } else {
                positions[idx] = Math.cos(newAngle) * newRadius;
                positions[idx + 2] = Math.sin(newAngle) * newRadius;
                positions[idx + 1] = y * 0.99; // Slowly compress toward center
            }
        }

        ref.current.geometry.attributes.position.needsUpdate = true;
        ref.current.rotation.y += delta * 0.1;
    });

    return (
        <Points ref={ref} positions={positions} colors={colors}>
            <PointMaterial
                vertexColors
                size={0.05}
                sizeAttenuation
                transparent
                opacity={0.8}
                depthWrite={false}
            />
        </Points>
    );
}

// 💀 THE VOID CORE - Central black sphere
function VoidCore() {
    const ref = useRef<THREE.Mesh>(null);

    useFrame((state) => {
        if (ref.current) {
            ref.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 2) * 0.05);
        }
    });

    return (
        <mesh ref={ref}>
            <sphereGeometry args={[0.3, 32, 32]} />
            <meshBasicMaterial color="#000000" />
        </mesh>
    );
}

// 🔥 EXPORT: Full Maelstrom Scene
export function MaelstromScene({ intensity = 1, className = '' }: { intensity?: number; className?: string }) {
    return (
        <div className={`w-full h-full ${className}`}>
            <Canvas camera={{ position: [0, 2, 5], fov: 60 }}>
                <ambientLight intensity={0.2} />
                <pointLight position={[5, 5, 5]} color="#FFD700" intensity={1} />
                <pointLight position={[-5, -5, -5]} color="#FF0033" intensity={0.5} />

                <VoidCore />
                <MaelstromParticles count={6000} intensity={intensity} />

                {/* Subtle fog for depth */}
                <fog attach="fog" args={['#000000', 5, 15]} />
            </Canvas>
        </div>
    );
}
