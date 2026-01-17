/**
 * Loading Skeleton Components
 * Smooth placeholders for better UX
 */

'use client';

import { motion } from 'framer-motion';

// Pulse animation
const pulseAnimation = {
    animate: {
        opacity: [0.5, 0.8, 0.5],
    },
    transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut" as const
    }
};

// Chart Skeleton
export function ChartSkeleton() {
    return (
        <div className="flex-1 flex flex-col bg-[#0a0e27] p-4">
            {/* Header */}
            <motion.div
                className="h-12 bg-gray-800/50 rounded-lg mb-4"
                {...pulseAnimation}
            />

            {/* Main Chart Area */}
            <div className="flex-1 flex flex-col gap-2">
                {/* Price chart skeleton */}
                <div className="flex-[7] bg-gray-800/30 rounded-lg p-4">
                    <div className="h-full flex items-end justify-around gap-1">
                        {Array.from({ length: 20 }).map((_, i) => (
                            <motion.div
                                key={i}
                                className="flex-1 bg-cyan-500/20 rounded-t"
                                style={{ height: `${30 + Math.random() * 70}%` }}
                                animate={{ opacity: [0.3, 0.6, 0.3] }}
                                transition={{
                                    duration: 1.5,
                                    repeat: Infinity,
                                    delay: i * 0.05,
                                }}
                            />
                        ))}
                    </div>
                </div>

                {/* Volume chart skeleton */}
                <div className="flex-[3] bg-gray-800/30 rounded-lg p-4">
                    <div className="h-full flex items-end justify-around gap-1">
                        {Array.from({ length: 20 }).map((_, i) => (
                            <motion.div
                                key={i}
                                className="flex-1 bg-purple-500/20 rounded-t"
                                style={{ height: `${20 + Math.random() * 60}%` }}
                                animate={{ opacity: [0.3, 0.6, 0.3] }}
                                transition={{
                                    duration: 1.5,
                                    repeat: Infinity,
                                    delay: i * 0.05,
                                }}
                            />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Market List Skeleton
export function MarketListSkeleton() {
    return (
        <div className="space-y-2 p-3">
            {Array.from({ length: 8 }).map((_, i) => (
                <motion.div
                    key={i}
                    className="flex items-center justify-between p-3 bg-gray-800/30 rounded-lg"
                    animate={{ opacity: [0.3, 0.6, 0.3] }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.1,
                    }}
                >
                    {/* Symbol */}
                    <div className="flex flex-col gap-1">
                        <div className="h-4 w-16 bg-gray-700/50 rounded" />
                        <div className="h-3 w-12 bg-gray-700/30 rounded" />
                    </div>

                    {/* Price */}
                    <div className="flex flex-col gap-1 items-end">
                        <div className="h-4 w-20 bg-gray-700/50 rounded" />
                        <div className="h-3 w-16 bg-gray-700/30 rounded" />
                    </div>
                </motion.div>
            ))}
        </div>
    );
}

// AI Signals Skeleton
export function AISignalsSkeleton() {
    return (
        <div className="space-y-2 p-3">
            {Array.from({ length: 3 }).map((_, i) => (
                <motion.div
                    key={i}
                    className="p-3 bg-gray-800/30 rounded-lg border border-gray-700/30"
                    animate={{ opacity: [0.3, 0.6, 0.3] }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.2,
                    }}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between mb-2">
                        <div className="h-4 w-20 bg-gray-700/50 rounded" />
                        <div className="h-5 w-12 bg-green-500/20 rounded" />
                    </div>

                    {/* Confidence bar */}
                    <div className="h-2 bg-gray-700/30 rounded mb-2" />

                    {/* Details */}
                    <div className="grid grid-cols-2 gap-2">
                        <div className="h-3 bg-gray-700/30 rounded" />
                        <div className="h-3 bg-gray-700/30 rounded" />
                    </div>

                    {/* Reason */}
                    <div className="mt-2 space-y-1">
                        <div className="h-2 bg-gray-700/20 rounded w-full" />
                        <div className="h-2 bg-gray-700/20 rounded w-3/4" />
                    </div>
                </motion.div>
            ))}
        </div>
    );
}

// Trade Info Skeleton
export function TradeInfoSkeleton() {
    return (
        <div className="p-4 space-y-4">
            {/* Price */}
            <motion.div
                className="space-y-2"
                animate={{ opacity: [0.4, 0.7, 0.4] }}
                transition={{ duration: 1.5, repeat: Infinity }}
            >
                <div className="h-3 w-20 bg-gray-700/50 rounded" />
                <div className="h-10 w-40 bg-gray-700/50 rounded" />
                <div className="h-4 w-24 bg-green-500/20 rounded" />
            </motion.div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-3">
                {Array.from({ length: 4 }).map((_, i) => (
                    <motion.div
                        key={i}
                        className="space-y-1"
                        animate={{ opacity: [0.3, 0.6, 0.3] }}
                        transition={{
                            duration: 1.5,
                            repeat: Infinity,
                            delay: i * 0.1,
                        }}
                    >
                        <div className="h-3 w-16 bg-gray-700/30 rounded" />
                        <div className="h-4 w-full bg-gray-700/50 rounded" />
                    </motion.div>
                ))}
            </div>

            {/* Buttons */}
            <div className="space-y-2 pt-4 border-t border-gray-800">
                <div className="h-10 bg-cyan-500/20 rounded-lg" />
                <div className="h-10 bg-gray-800/50 rounded-lg" />
            </div>
        </div>
    );
}

// Order Book Skeleton
export function OrderBookSkeleton() {
    return (
        <div className="p-4">
            {/* Header */}
            <motion.div
                className="h-5 w-24 bg-gray-700/50 rounded mb-3"
                animate={{ opacity: [0.4, 0.7, 0.4] }}
                transition={{ duration: 1.5, repeat: Infinity }}
            />

            {/* Column Headers */}
            <div className="grid grid-cols-3 gap-2 mb-2 px-2">
                <div className="h-3 bg-gray-700/30 rounded" />
                <div className="h-3 bg-gray-700/30 rounded" />
                <div className="h-3 bg-gray-700/30 rounded" />
            </div>

            {/* Asks */}
            {Array.from({ length: 5 }).map((_, i) => (
                <motion.div
                    key={`ask-${i}`}
                    className="grid grid-cols-3 gap-2 px-2 py-1"
                    animate={{ opacity: [0.3, 0.6, 0.3] }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.05,
                    }}
                >
                    <div className="h-3 bg-red-500/20 rounded" />
                    <div className="h-3 bg-gray-700/30 rounded" />
                    <div className="h-3 bg-gray-700/30 rounded" />
                </motion.div>
            ))}

            {/* Spread */}
            <div className="h-8 bg-gray-800/50 rounded my-2" />

            {/* Bids */}
            {Array.from({ length: 5 }).map((_, i) => (
                <motion.div
                    key={`bid-${i}`}
                    className="grid grid-cols-3 gap-2 px-2 py-1"
                    animate={{ opacity: [0.3, 0.6, 0.3] }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.05,
                    }}
                >
                    <div className="h-3 bg-green-500/20 rounded" />
                    <div className="h-3 bg-gray-700/30 rounded" />
                    <div className="h-3 bg-gray-700/30 rounded" />
                </motion.div>
            ))}
        </div>
    );
}
