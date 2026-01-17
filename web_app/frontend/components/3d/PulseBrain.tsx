'use client';

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

function BrainParticles({ count = 2000 }) {
    const points = useRef<THREE.Points>(null);

    // Generate particles in a spherical/brain-like shape
    const particles = useMemo(() => {
        const positions = new Float32Array(count * 3);
        const colors = new Float32Array(count * 3);

        for (let i = 0; i < count; i++) {
            // Hemisphere distribution (approximate brain shape)
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(Math.random() * 2 - 1);
            const r = 1.2 + Math.random() * 0.2; // Base radius with noise

            // Squash slightly to look more like a brain
            let x = r * Math.sin(phi) * Math.cos(theta);
            let y = r * Math.sin(phi) * Math.sin(theta) * 0.8;
            let z = r * Math.cos(phi) * 1.2;

            // Separate hemispheres
            if (x > 0) x += 0.1;
            if (x < 0) x -= 0.1;

            positions[i * 3] = x;
            positions[i * 3 + 1] = y;
            positions[i * 3 + 2] = z;

            // Electric Blue / Purple colors
            colors[i * 3] = 0.5 + Math.random() * 0.5; // R
            colors[i * 3 + 1] = 0.0; // G
            colors[i * 3 + 2] = 1.0; // B
        }
        return { positions, colors };
    }, [count]);

    useFrame((state) => {
        if (points.current) {
            points.current.rotation.y += 0.005;
            points.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.5) * 0.1;

            // Pulse size
            const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.05;
            points.current.scale.set(scale, scale, scale);
        }
    });

    return (
        <Points ref={points}>
            <bufferGeometry>
                <bufferAttribute
                    attach="attributes-position"
                    args={[particles.positions, 3]}
                />
                <bufferAttribute
                    attach="attributes-color"
                    args={[particles.colors, 3]}
                />
            </bufferGeometry>
            <PointMaterial
                vertexColors
                size={0.03}
                sizeAttenuation
                transparent
                depthWrite={false}
                opacity={0.8}
            />
        </Points>
    );
}

export function PulseBrain() {
    return (
        <div className="absolute inset-0 pointer-events-none opacity-50">
            <Canvas camera={{ position: [0, 0, 4] }}>
                <ambientLight intensity={0.5} />
                <BrainParticles />
            </Canvas>
        </div>
    );
}
