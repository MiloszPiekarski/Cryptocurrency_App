"use client";
import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Activity, Globe, ShieldCheck, Zap } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { LoginModal } from "@/components/auth/LoginModal";

// Dynamically import the 3D globe to avoid SSR issues with Three.js
const GlobalAwarenessGlobe = dynamic(
  () => import('@/components/landing/GlobalAwarenessGlobe'),
  { ssr: false }
);

function FeatureCard({ icon: Icon, title, desc, delay }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="p-6 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-sm hover:border-cyan-500/30 hover:bg-white/10 transition-all group"
    >
      <div className="mb-4 p-3 rounded-full bg-cyan-900/20 w-fit group-hover:scale-110 transition-transform">
        <Icon className="w-6 h-6 text-cyan-400 group-hover:text-cyan-200" />
      </div>
      <h3 className="text-xl font-bold mb-2 text-white group-hover:text-cyan-400">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
    </motion.div>
  )
}

export default function Home() {
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  return (
    <>
      <main className={`relative min-h-screen flex flex-col items-center justify-start overflow-hidden transition-all duration-300 ${isLoginOpen ? 'blur-sm scale-[0.99] opacity-50 pointer-events-none' : ''}`}>

        {/* 3D Background */}
        <div className="fixed inset-0 z-0">
          <GlobalAwarenessGlobe />
          <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-transparent to-[#050505]/50 z-[1]" />
          <div className="absolute inset-0 grid-bg z-[0] opacity-30" />
        </div>

        {/* Navbar */}
        <nav className="w-full z-10 p-6 flex justify-between items-center max-w-7xl mx-auto glass rounded-b-2xl mt-4 mx-4">
          <div className="text-2xl font-black tracking-widest bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-600">
            CASH MAELSTROM
          </div>
          <div className="flex gap-4">
            <Button
              onClick={() => setIsLoginOpen(true)}
              className="bg-cyan-600 hover:bg-cyan-500 text-white border-0 glow-text"
            >
              Login <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative z-10 w-full max-w-5xl mx-auto pt-32 px-4 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-6xl md:text-8xl font-black mb-6 leading-tight tracking-tight">
              <span className="block text-transparent bg-clip-text bg-gradient-to-b from-white to-gray-500">
                DIGITAL
              </span>
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600 animate-pulse">
                SOVEREIGNTY
              </span>
            </h1>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-xl md:text-2xl text-gray-400 max-w-2xl mx-auto mb-12"
          >
            The world's first Autonomous Hedge Fund simulation powered by <span className="text-cyan-400 font-bold">1,000,000 AI Agents</span>.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="flex flex-col md:flex-row gap-4 justify-center items-center"
          >
            <div className="relative group cursor-pointer" onClick={() => setIsLoginOpen(true)}>
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-lg blur opacity-40 group-hover:opacity-100 transition duration-200"></div>
              <button className="relative px-8 py-4 bg-black rounded-lg leading-none flex items-center divide-x divide-gray-600">
                <span className="flex items-center space-x-5">
                  <Zap className="text-cyan-400 w-6 h-6" />
                  <span className="pr-6 text-gray-100 font-bold text-lg">Access Terminal</span>
                </span>
                <span className="pl-6 text-cyan-400 group-hover:text-white transition duration-200">
                  v.2.0.4 &rarr;
                </span>
              </button>
            </div>
          </motion.div>
        </section>

        {/* Features Grid */}
        <section className="relative z-10 w-full max-w-7xl mx-auto py-32 px-4 grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard
            icon={Globe}
            title="Global Awareness"
            desc="Real-time ingestion of on-chain data, satellite imagery, and social sentiment from every corner of the digital sphere."
            delay={0.8}
          />
          <FeatureCard
            icon={Activity}
            title="Swarm Intelligence"
            desc="A decentralized hive-mind of specialized micro-agents (Scouts, Hunters, Analysts) collaborating to find alpha."
            delay={1.0}
          />
          <FeatureCard
            icon={ShieldCheck}
            title="Risk Citadel"
            desc="Institutional-grade risk management protocols protecting capital with mili-second reaction times."
            delay={1.2}
          />
        </section>

        {/* Footer */}
        <footer className="relative z-10 w-full border-t border-white/5 bg-black/50 backdrop-blur-md py-12 text-center text-gray-600">
          <p>© 2026 CASH MAELSTROM. Autonomous System. All Rights Reserved.</p>
        </footer>
      </main>

      <LoginModal isOpen={isLoginOpen} onClose={() => setIsLoginOpen(false)} />
    </>
  );
}
