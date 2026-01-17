"use client";

import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Stars } from '@react-three/drei';
import * as random from 'maath/random/dist/maath-random.esm';

function Swarm(props: any) {
    const ref = useRef<any>(null);
    const sphere = useMemo(() => {
        // Generate random points in a sphere. 
        // Must be divisible by 3 (x,y,z) to avoid BufferGeometry errors.
        const data = random.inSphere(new Float32Array(9000), { radius: 2.0 });
        // Scale check to ensure no NaNs (fallback)
        for (let i = 0; i < data.length; i++) {
            if (isNaN(data[i])) data[i] = 0;
        }
        return data;
    }, []);

    useFrame((state, delta) => {
        if (ref.current) {
            ref.current.rotation.x -= delta / 10;
            ref.current.rotation.y -= delta / 15;
        }
    });

    return (
        <group rotation={[0, 0, Math.PI / 4]}>
            <Points ref={ref} positions={sphere} stride={3} frustumCulled={false} {...props}>
                <PointMaterial
                    transparent
                    color="#8b7cf5"
                    size={0.025}
                    sizeAttenuation={true}
                    depthWrite={false}
                />
            </Points>
        </group>
    )
}

function Core(props: any) {
    const mesh = useRef<any>(null);

    useFrame((state, delta) => {
        if (mesh.current) {
            mesh.current.rotation.y += delta * 0.2;
        }
    });

    return (
        <mesh ref={mesh} {...props}>
            <sphereGeometry args={[1.2, 48, 48]} />
            <meshStandardMaterial
                color="#0a1628"
                emissive="#4c1d95"
                emissiveIntensity={0.6}
                wireframe
                transparent
                opacity={0.6}
            />
        </mesh>
    );
}

function InnerGlow(props: any) {
    return (
        <mesh {...props}>
            <sphereGeometry args={[0.8, 32, 32]} />
            <meshBasicMaterial
                color="#6366f1"
                transparent
                opacity={0.12}
            />
        </mesh>
    );
}

export default function GlobalAwarenessGlobe() {
    return (
        <div className="absolute inset-0 z-0 pointer-events-none">
            <Canvas camera={{ position: [0, 0, 4] }}>
                <ambientLight intensity={0.7} />
                <pointLight position={[0, 0, 0]} intensity={1.5} color="#6366f1" />
                <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
                <Swarm />
                <InnerGlow />
                <Core />
            </Canvas>
        </div>
    );
}

