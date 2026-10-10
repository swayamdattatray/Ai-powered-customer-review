import React, { useState } from 'react';
import {
  Shield,
  Sliders,
  Database,
  Lock,
  RefreshCw,
  ExternalLink,
  CheckCircle2,
  Info
} from 'lucide-react';

export default function SettingsAndTransparency() {
  const [enabledRetailers, setEnabledRetailers] = useState<{ [key: string]: boolean }>({
    amazon: true,
    flipkart: true,
    croma: true,
    reliance: true
  });
  const [cacheTTL, setCacheTTL] = useState<number>(30);

  const toggleRetailer = (key: string) => {
    setEnabledRetailers((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Extension Settings & Data Transparency
            </h3>
            <p className="text-xs text-slate-400">
              Configure supported comparison retailers, cache durations, and review privacy guarantees
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Retailer Coverage Configuration */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
            <Database className="w-4 h-4 text-blue-400" />
            <span>Supported E-Commerce Retailers</span>
          </div>

          <div className="space-y-2.5">
            {[
              { id: 'amazon', name: 'Amazon India (Amazon.in)', desc: 'DOM Extraction + Official PA-API Fallback' },
              { id: 'flipkart', name: 'Flipkart (Flipkart.com)', desc: 'DOM Extraction + Affiliate Search Discovery' },
              { id: 'croma', name: 'Croma Retail', desc: 'Direct Verified Catalog Search Deep-Link' },
              { id: 'reliance', name: 'Reliance Digital', desc: 'Direct Verified Catalog Search Deep-Link' }
            ].map((r) => (
              <label
                key={r.id}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-slate-700 cursor-pointer"
              >
                <div>
                  <div className="text-xs font-bold text-white">{r.name}</div>
                  <div className="text-[10px] text-slate-400">{r.desc}</div>
                </div>
                <input
                  type="checkbox"
                  checked={enabledRetailers[r.id]}
                  onChange={() => toggleRetailer(r.id)}
                  className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 border-slate-700 bg-slate-800"
                />
              </label>
            ))}
          </div>
        </div>

        {/* Privacy & DPDP Compliance Dossier */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
            <Lock className="w-4 h-4 text-emerald-400" />
            <span>Security & Privacy Architecture</span>
          </div>

          <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
            <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-white">Author PII Stripping: </strong>
                Customer reviewer names, profiles, and avatar URIs are stripped on the client side prior to NLP transmission.
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-white">DPDP Act (India) Compliance: </strong>
                No personal browsing history or unrelated website navigation is tracked or recorded.
              </div>
            </div>

            <div className="flex items-start gap-2.5 p-3 rounded-lg bg-slate-900/60 border border-slate-800">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-white">Deterministic Heuristics: </strong>
                Review trust scores and scam evaluations are mathematically verifiable and reproducible.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
