'use client';
import Link from 'next/link';

export default function GlobalPulsePage() {
    return (
        <div className="min-h-screen bg-black text-white p-8">
            <Link href="/nexus" className="text-cyan-500 text-sm">&larr; NEXUS</Link>
            <h1 className="text-4xl font-bold mt-4">GLOBAL CONSCIOUSNESS</h1>
            <p className="text-gray-400 mt-2">Macro & Satellite Data Correlation - Coming Soon</p>
        </div>
    );
}
