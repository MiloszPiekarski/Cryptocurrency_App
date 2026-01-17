import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Navigation } from "@/components/Navigation";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const mono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CASH MAELSTROM | Quantum Market Research Institute",
  description: "Institutional-grade market analysis powered by 1M AI agents.",
};

import { Providers } from "./providers";
import { MainContentWrapper } from "@/components/MainContentWrapper";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${mono.variable} antialiased font-sans bg-black`}
      >
        <Providers>
          <Navigation />
          <MainContentWrapper>
            {children}
          </MainContentWrapper>
        </Providers>
      </body>
    </html>
  );
}
