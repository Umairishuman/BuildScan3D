content = """import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "BuildScan 3D — Construction Spatial Intelligence Platform",
  description: "Enterprise 3D Gaussian Splatting and AR Spatial Telemetry for Construction Verification",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#f8fafc] text-[#0f172a]">{children}</body>
    </html>
  );
}
"""

with open(r"d:\FYP\prototype\web-ui\src\app\layout.tsx", "w", encoding="utf-8") as f:
    f.write(content)

print("layout.tsx written cleanly.")

