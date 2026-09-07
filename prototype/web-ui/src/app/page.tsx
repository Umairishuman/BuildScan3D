"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Box, Lock, Mail, ArrowRight, ShieldCheck, HardHat, Sparkles } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("pm.jenkins@buildscan3d.ai");
  const [password, setPassword] = useState("••••••••••••");
  const [isLoading, setIsLoading] = useState(false);

  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      router.push("/dashboard");
    }, 450);
  };

  return (
    <div className="min-h-screen w-full bg-slate-950 text-slate-100 flex flex-col justify-between relative overflow-hidden">
      {/* Background Gradients & Grid */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_10%,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-950 to-slate-950 pointer-events-none" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:32px_32px] opacity-20 pointer-events-none" />

      {/* Top Banner */}
      <header className="relative z-10 w-full p-6 flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 p-[1px] shadow-lg shadow-blue-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center">
              <Box className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <span className="font-bold text-lg text-white">
              BuildScan<span className="text-cyan-400">3D</span>
            </span>
            <span className="ml-2 text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Enterprise
            </span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-lg">
          <ShieldCheck className="w-4 h-4" />
          <span className="font-mono">FAST-NUCES FYP Defense Build</span>
        </div>
      </header>

      {/* Main Login Card */}
      <main className="relative z-10 flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-slate-900/90 backdrop-blur-xl border border-slate-800/80 rounded-2xl shadow-2xl p-8 space-y-6">
          {/* Logo & Headline */}
          <div className="text-center space-y-2">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 p-[1px] shadow-xl shadow-blue-500/20 mb-2">
              <div className="w-full h-full bg-slate-950 rounded-[15px] flex items-center justify-center">
                <HardHat className="w-7 h-7 text-cyan-400" />
              </div>
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">
              Construction Intelligence Portal
            </h1>
            <p className="text-xs text-slate-400">
              Sign in to inspect millimeter-accurate 3D scans & telemetry
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSignIn} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">
                Enterprise Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label className="text-xs font-semibold text-slate-300">
                  Password
                </label>
                <span className="text-[11px] text-cyan-400 font-mono">
                  [Demo Pass]
                </span>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-9 pr-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors font-mono"
                  required
                />
              </div>
            </div>

            {/* Quick Demo Pre-filled Callout */}
            <div className="p-3 rounded-xl bg-blue-500/5 border border-blue-500/20 text-xs text-slate-300 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                <span className="text-[11px]">Logged as: <strong>Sarah Jenkins (Lead MEP)</strong></span>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs tracking-wide shadow-lg shadow-blue-500/25 transition-all flex items-center justify-center gap-2 group"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign In as Project Manager</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          {/* Defense Context Badge */}
          <div className="pt-2 border-t border-slate-800/80 text-center">
            <p className="text-[11px] text-slate-400">
              Architecture: <strong className="text-slate-300">ARCore 120Hz VIO + 3DGS + YOLOv8-Seg</strong>
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 w-full p-6 text-center text-xs text-slate-400">
        BuildScan 3D • Final Year Project • FAST National University of Computer and Emerging Sciences
      </footer>
    </div>
  );
}
