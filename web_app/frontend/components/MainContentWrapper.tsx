"use client";

import { usePathname } from 'next/navigation';

export function MainContentWrapper({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const isHome = pathname === '/';

    return (
        <div className={isHome ? "" : "pt-14"}>
            {children}
        </div>
    );
}
