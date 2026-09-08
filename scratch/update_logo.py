import os

base_dir = r"d:\FYP\prototype\web-ui"

# 1. page.tsx
page_tsx = """\"use client\";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Mail, Lock, Eye, EyeOff, ShieldCheck } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("pm.jenkins@buildscan3d.ai");
  const [password, setPassword] = useState("password123");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      router.push("/dashboard");
    }, 400);
  };

  return (
    <div className="min-h-screen w-full flex flex-col md:flex-row bg-white overflow-hidden">
      {/* LEFT COLUMN: Full-Bleed Architectural 3D Graphic Panel */}
      <div className="relative w-full md:w-[48%] lg:w-[46%] bg-[#eff6fd] min-h-[380px] md:min-h-screen flex flex-col justify-between overflow-hidden select-none border-r border-[#e2edf8]">
        {/* Full-bleed Background 3D BIM Graphic */}
        <div className="absolute inset-0 w-full h-full pointer-events-none">
          <Image
            src="/images/login-left-panel-new.png"
            alt="3D Spatial BIM Scan"
            fill
            className="object-cover object-center scale-105 md:scale-100"
            priority
            quality={100}
          />
          {/* Subtle top & bottom gradient overlays */}
          <div className="absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-[#eff6fd]/90 via-[#eff6fd]/40 to-transparent" />
          <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-[#eff6fd]/90 via-[#eff6fd]/40 to-transparent" />
        </div>

        {/* Top Text Overlay */}
        <div className="relative z-10 p-8 md:p-12 space-y-1">
          <h2 className="text-base md:text-lg font-bold text-[#1e293b] tracking-tight">
            Real sites. 3D truth.
          </h2>
          <p className="text-xs md:text-sm text-[#64748b] font-medium">
            Verify. Measure. Build better.
          </p>
        </div>

        {/* Bottom Text Overlay */}
        <div className="relative z-10 p-8 md:p-12">
          <p className="text-xs text-[#64748b] font-medium">
            Powered by spatial data. Built for construction.
          </p>
        </div>
      </div>

      {/* RIGHT COLUMN: Clean Enterprise Authentication Form */}
      <div className="flex-1 flex flex-col items-center justify-center p-6 sm:p-10 md:p-16 bg-white min-h-screen">
        <div className="w-full max-w-[380px] flex flex-col items-center">
          {/* Official New Brand Logo */}
          <div className="flex flex-col items-center text-center mb-8">
            <div className="relative w-48 h-16 mb-2">
              <Image
                src="/images/logo-new-removebg-preview.png"
                alt="BuildScan 3D"
                fill
                className="object-contain"
                priority
              />
            </div>
            <p className="text-xs text-[#64748b]">
              Construction Spatial Intelligence Platform
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSignIn} className="w-full space-y-4">
            {/* Email Field */}
            <div className="relative flex items-center border border-[#e2e8f0] rounded-xl px-3.5 py-3 bg-white focus-within:border-[#2563eb] focus-within:ring-2 focus-within:ring-[#2563eb]/10 transition-all shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <Mail className="w-4 h-4 text-[#64748b] mr-3 shrink-0" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full text-xs sm:text-sm text-[#0f172a] placeholder-[#94a3b8] bg-transparent focus:outline-none"
                required
              />
            </div>

            {/* Password Field */}
            <div className="relative flex items-center border border-[#e2e8f0] rounded-xl px-3.5 py-3 bg-white focus-within:border-[#2563eb] focus-within:ring-2 focus-within:ring-[#2563eb]/10 transition-all shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <Lock className="w-4 h-4 text-[#64748b] mr-3 shrink-0" />
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full text-xs sm:text-sm text-[#0f172a] placeholder-[#94a3b8] bg-transparent focus:outline-none font-mono"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-[#64748b] hover:text-[#0f172a] ml-2 shrink-0 transition-colors cursor-pointer"
                title={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 rounded-xl bg-[#2563eb] hover:bg-[#1d4ed8] active:bg-[#1e40af] text-white font-medium text-xs sm:text-sm shadow-sm transition-all flex items-center justify-center gap-2 cursor-pointer mt-5"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                "Sign In"
              )}
            </button>

            {/* Forgot password link */}
            <div className="text-center pt-1">
              <button
                type="button"
                onClick={() => alert("Password reset link sent to demo email")}
                className="text-xs text-[#2563eb] hover:text-[#1d4ed8] hover:underline font-medium transition-colors cursor-pointer"
              >
                Forgot password?
              </button>
            </div>
          </form>

          {/* Security & Compliance Badges */}
          <div className="w-full flex items-center justify-center gap-3 mt-12 pt-4">
            <div className="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-xl border border-[#e2e8f0] bg-white text-[11px] font-medium text-[#64748b] shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <Lock className="w-3.5 h-3.5 text-[#64748b]" />
              <span>256-bit encrypted</span>
            </div>
            <div className="flex-1 flex items-center justify-center gap-2 py-2 px-3 rounded-xl border border-[#e2e8f0] bg-white text-[11px] font-medium text-[#64748b] shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
              <ShieldCheck className="w-3.5 h-3.5 text-[#64748b]" />
              <span>SOC 2 compliant</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

with open(os.path.join(base_dir, "src", "app", "page.tsx"), "w", encoding="utf-8") as f:
    f.write(page_tsx)

# 2. Navbar.tsx
navbar_tsx = """\"use client\";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { Activity, HardHat, Search, ShieldCheck } from "lucide-react";

interface NavbarProps {
  onOpenJobStatus?: () => void;
  activeProcessingCount?: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  onOpenJobStatus,
  activeProcessingCount = 1,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#e2e8f0] bg-white/90 backdrop-blur-md text-[#0f172a]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand & System Tag */}
        <div className="flex items-center gap-8">
          <Link href="/dashboard" className="flex items-center gap-2 group">
            <div className="relative w-36 h-9">
              <Image
                src="/images/logo-new-removebg-preview.png"
                alt="BuildScan 3D"
                fill
                className="object-contain group-hover:scale-105 transition-transform"
                priority
              />
            </div>
            <span className="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-blue-50 text-[#2563eb] border border-blue-200">
              Enterprise
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-1 text-xs font-semibold text-[#64748b]">
            <Link
              href="/dashboard"
              className="px-3 py-1.5 rounded-lg text-[#2563eb] bg-blue-50 font-bold transition-colors"
            >
              Projects & Scans
            </Link>
            <Link
              href="/viewer/sector-4-mep"
              className="px-3 py-1.5 rounded-lg hover:text-[#0f172a] hover:bg-slate-100 transition-colors"
            >
              3D Workspace
            </Link>
          </nav>
        </div>

        {/* Global Search */}
        <div className="hidden lg:flex items-center flex-1 max-w-xs relative">
          <Search className="w-3.5 h-3.5 text-[#94a3b8] absolute left-3 pointer-events-none" />
          <input
            type="text"
            placeholder="Search scans, sectors, rooms..."
            className="w-full pl-8 pr-4 py-1.5 bg-[#f8fafc] border border-[#e2e8f0] rounded-xl text-xs text-[#0f172a] placeholder-[#94a3b8] focus:outline-none focus:border-[#2563eb] focus:bg-white transition-all"
          />
        </div>

        {/* Right Section: Status Indicator & Profile */}
        <div className="flex items-center gap-3">
          {/* Active Job Trigger Button */}
          {activeProcessingCount > 0 && onOpenJobStatus && (
            <button
              onClick={onOpenJobStatus}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-700 hover:bg-amber-100 text-xs font-semibold transition-all cursor-pointer"
              title="Click to view live 3DGS training queue"
            >
              <Activity className="w-3.5 h-3.5 text-amber-600 animate-spin" />
              <span>1 Pipeline Active (68%)</span>
            </button>
          )}

          {/* Defense Badge */}
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-xl">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span className="font-mono text-[11px] font-semibold">FAST-NUCES PoC</span>
          </div>

          <div className="h-5 w-[1px] bg-[#e2e8f0] hidden sm:block" />

          {/* User Profile Snippet */}
          <div className="flex items-center gap-2.5 pl-1">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white font-bold text-xs shadow-sm">
              SJ
            </div>
            <div className="hidden xl:block text-left">
              <div className="text-xs font-bold text-[#0f172a]">
                Sarah Jenkins
              </div>
              <div className="text-[10px] text-[#64748b] flex items-center gap-1">
                <HardHat className="w-2.5 h-2.5 text-amber-500" />
                <span>Lead MEP Manager</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
"""

with open(os.path.join(base_dir, "src", "components", "Navbar.tsx"), "w", encoding="utf-8") as f:
    f.write(navbar_tsx)

# 3. AGENTS.md
agents_md = """# BuildScan 3D — Agent Instructions & Design Guidelines

## 1. Brand Assets & Logo Rules
- **Official Logo**: Always use `/images/logo-new-removebg-preview.png` (transparent background) or `/images/logo-new.png` for all branding, login screens, headers, navbars, and exported reports.
- **Do NOT** replace the official logo with generic icons, raw SVG cubes, or placeholder text. Always render the brand asset from `/images/logo-new-removebg-preview.png`.
- **Hero Image (Login)**: Always use `/images/login-left-panel-new.png` for the left full-bleed architectural 3D blueprint panel on the login screen.

## 2. UI Theme & Design System
- **Theme**: Light Enterprise SaaS theme (`#f8fafc` background, crisp white cards `#ffffff`, subtle slate borders `#e2e8f0`, primary blue accents `#2563eb`).
- **Typography**: Clean modern sans-serif with high-contrast text (`#0f172a` headings, `#64748b` secondary text).

## 3. FYP Defense Architecture
- **Stage 1 (Mobile)**: CameraX / ARCore (Android) & ARKit (iOS) capturing 30 FPS video + 120Hz IMU telemetry (`poses.csv` and `points.csv`).
- **Stage 2 (Pose Prior)**: `build_transforms.py` quaternion to $3 \\times 3$ SO(3) matrix conversion + OpenGL to OpenCV/Nerfstudio coordinate alignment (`transforms.json` and `points3D.ply`).
- **Stage 3 (3DGS)**: Nerfstudio `splatfacto` 3D Gaussian Splatting trained in < 5 minutes on Cloud GPU (NVIDIA RTX 4090).
- **Stage 4 (Semantic AI)**: YOLOv8-Seg 2D segmentation masks projected to 3D point cloud for MEP systems (Pipes, Conduits, HVAC).
- **Stage 5 (Web Workspace)**: Three.js / WebGPU rendering with 1:1 metric measurements and semantic system toggles.
"""

with open(r"d:\FYP\AGENTS.md", "w", encoding="utf-8") as f:
    f.write(agents_md)

with open(r"d:\FYP\prototype\web-ui\AGENTS.md", "w", encoding="utf-8") as f:
    f.write(agents_md)

print("Updated page.tsx, Navbar.tsx, and created AGENTS.md in root and web-ui.")

