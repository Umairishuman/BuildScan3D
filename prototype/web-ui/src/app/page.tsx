"use client";

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
