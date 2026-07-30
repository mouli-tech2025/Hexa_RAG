import type { Metadata } from "next";
import { Inter, Playfair_Display, Caveat } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
});

const caveat = Caveat({
  variable: "--font-script",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "SafeRAG — Private Offline Document Intelligence",
  description: "Evidence-first document investigation powered by local AI. No data leaves your device.",
  icons: {
    icon: "/favicon.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable} ${caveat.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-background text-foreground relative overflow-x-hidden">
        {/* Background Atmosphere: Star Particles (purely decorative, fixed behind content across full site) */}
        <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden" aria-hidden>
          <div className="animate-star-slow absolute top-12 left-[15%] h-1 w-1 rounded-full bg-cyan-300 opacity-30 shadow-[0_0_8px_#06b6d4]" />
          <div className="animate-star-mid absolute top-28 right-[20%] h-1.5 w-1.5 rounded-full bg-amber-200 opacity-40 shadow-[0_0_10px_#f59e0b]" />
          <div className="animate-star-fast absolute top-60 left-[35%] h-1 w-1 rounded-full bg-slate-100 opacity-25" />
          <div className="animate-star-slow absolute top-96 right-[12%] h-1 w-1 rounded-full bg-cyan-200 opacity-35 shadow-[0_0_6px_#06b6d4]" />
          <div className="animate-star-mid absolute top-[60%] left-[8%] h-1.5 w-1.5 rounded-full bg-amber-300 opacity-30 shadow-[0_0_8px_#f59e0b]" />
          <div className="animate-star-fast absolute top-[75%] right-[25%] h-1 w-1 rounded-full bg-cyan-300 opacity-20" />
          <div className="animate-star-slow absolute top-[90%] left-[45%] h-1.5 w-1.5 rounded-full bg-amber-200 opacity-25 shadow-[0_0_8px_#f59e0b]" />
        </div>

        {/* Decorative Wavy Line directly under top navbar/header zone */}
        <div className="pointer-events-none absolute top-0 left-0 right-0 z-10 overflow-hidden opacity-40" aria-hidden>
          <svg className="w-full h-4" viewBox="0 0 1200 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M0 8 Q 150 16, 300 8 T 600 8 T 900 8 T 1200 8"
              stroke="#06b6d4"
              strokeWidth="1.5"
              className="animate-wavy-divider"
            />
          </svg>
        </div>

        {/* Main Content Layer */}
        <div className="relative z-10 flex min-h-full flex-col font-sans">
          {children}
        </div>
      </body>
    </html>
  );
}
