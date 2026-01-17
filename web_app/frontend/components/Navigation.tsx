'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Atom, Brain, Binary, Microscope, Hammer, Globe } from 'lucide-react';

export function Navigation() {
    const pathname = usePathname();

    if (pathname === '/' || pathname === '/nexus') return null;

    const links = [
        { href: '/nexus', label: 'NEXUS', icon: Atom, desc: 'Command Center' },
        { href: '/screener', label: 'SCREENER', icon: Globe, desc: 'Market Discovery' },
        { href: '/strategic-rooms/hive-mind', label: 'HIVE MIND', icon: Brain, desc: 'Swarm Intelligence' },
        { href: '/strategic-rooms/digital-twin', label: 'DIGITAL TWIN', icon: Binary, desc: 'Simulation' },
        { href: '/lab', label: 'THE LAB', icon: Microscope, desc: 'Atomic Verdict' },
        { href: '/forge', label: 'THE FORGE', icon: Hammer, desc: 'No-AI Zone' },
    ];

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-gray-800/50">
            <div className="max-w-7xl mx-auto px-4">
                <div className="flex items-center justify-between h-14">

                    {/* Logo */}
                    <Link href="/nexus" className="flex items-center gap-2 group">
                        <div className="w-8 h-8 rounded bg-gradient-to-br from-purple-600 to-cyan-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <Atom className="w-4 h-4 text-white" />
                        </div>
                        <span className="text-sm font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
                            CASH MAELSTROM
                        </span>
                    </Link>

                    {/* Links */}
                    <div className="hidden md:flex items-center gap-1">
                        {links.map(link => {
                            const isActive = pathname === link.href;
                            return (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    className={`
                                        relative px-3 py-2 rounded-lg text-xs font-bold uppercase tracking-wider
                                        transition-all duration-200 flex items-center gap-2
                                        ${isActive
                                            ? 'text-cyan-400 bg-cyan-500/10'
                                            : 'text-gray-500 hover:text-white hover:bg-white/5'
                                        }
                                    `}
                                >
                                    <link.icon className="w-3.5 h-3.5" />
                                    {link.label}
                                    {isActive && (
                                        <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1 h-1 bg-cyan-400 rounded-full" />
                                    )}
                                </Link>
                            );
                        })}
                    </div>

                    {/* Status Indicator */}
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                        <span className="hidden sm:inline">SYSTEM ONLINE</span>
                    </div>

                </div>
            </div>
        </nav>
    );
}
