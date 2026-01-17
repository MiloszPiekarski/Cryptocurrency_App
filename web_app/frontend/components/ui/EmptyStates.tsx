/**
 * Empty State Components
 * Beautiful "no data" screens
 */

'use client';

import { motion } from 'framer-motion';
import { TrendingUp, AlertCircle, Inbox, WifiOff, Database } from 'lucide-react';

interface EmptyStateProps {
    icon?: 'chart' | 'alert' | 'inbox' | 'offline' | 'database';
    title: string;
    description?: string;
    action?: {
        label: string;
        onClick: () => void;
    };
}

const icons = {
    chart: TrendingUp,
    alert: AlertCircle,
    inbox: Inbox,
    offline: WifiOff,
    database: Database,
};

export function EmptyState({
    icon = 'inbox',
    title,
    description,
    action
}: EmptyStateProps) {
    const Icon = icons[icon];

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="flex flex-col items-center justify-center p-8 text-center"
        >
            {/* Icon */}
            <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.1, type: 'spring' }}
                className="mb-4 p-4 rounded-full bg-gray-800/50 border border-gray-700/50"
            >
                <Icon className="w-8 h-8 text-gray-400" />
            </motion.div>

            {/* Title */}
            <h3 className="text-lg font-semibold text-white mb-2">
                {title}
            </h3>

            {/* Description */}
            {description && (
                <p className="text-sm text-gray-400 max-w-md mb-4">
                    {description}
                </p>
            )}

            {/* Action Button */}
            {action && (
                <button
                    onClick={action.onClick}
                    className="mt-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg text-sm font-medium transition-colors"
                >
                    {action.label}
                </button>
            )}
        </motion.div>
    );
}

// Chart Empty State
export function ChartEmptyState() {
    return (
        <EmptyState
            icon="chart"
            title="No Chart Data Available"
            description="Select a different symbol or timeframe to view chart data."
        />
    );
}

// Order Book Empty State
export function OrderBookEmptyState() {
    return (
        <EmptyState
            icon="database"
            title="Order Book Unavailable"
            description="Order book data is not available for this symbol at the moment."
        />
    );
}

// Error State
export function ErrorState({
    title = "Something went wrong",
    description = "An error occurred while loading data. Please try again.",
    onRetry
}: {
    title?: string;
    description?: string;
    onRetry?: () => void;
}) {
    return (
        <EmptyState
            icon="alert"
            title={title}
            description={description}
            action={onRetry ? {
                label: 'Try Again',
                onClick: onRetry
            } : undefined}
        />
    );
}

// Offline State
export function OfflineState() {
    return (
        <EmptyState
            icon="offline"
            title="No Connection"
            description="Unable to connect to the server. Please check your internet connection."
            action={{
                label: 'Reload',
                onClick: () => window.location.reload()
            }}
        />
    );
}

// Mini Empty State (for smaller panels)
export function MiniEmptyState({
    text = "No data available",
    icon: Icon = Inbox
}: {
    text?: string;
    icon?: React.ComponentType<{ className?: string }>;
}) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center p-6 text-center"
        >
            <Icon className="w-6 h-6 text-gray-500 mb-2" />
            <p className="text-sm text-gray-500">{text}</p>
        </motion.div>
    );
}
