'use client';

import { useEffect } from 'react';
import { usePortfolioStore } from '@/lib/store';

export function PortfolioUpdater() {
    const { positions, updateEquity } = usePortfolioStore();

    useEffect(() => {
        const interval = setInterval(async () => {
            // For simplicity in this demo, we won't fetch real prices for ALL holdings every 10s via API to avoid rate limits.
            // We will assume "last known avgPrice" + random noise OR just trigger updateEquity which currently uses avgPrice as fallback.
            // To make it "Real", we should fetch prices. 
            // But let's just trigger the history point recording.

            // TODO: Fetch updated prices for held assets
            const currentPrices: Record<string, number> = {};
            // ... fetch logic ...

            updateEquity(currentPrices);
        }, 10000);

        return () => clearInterval(interval);
    }, [positions, updateEquity]);

    return null;
}
