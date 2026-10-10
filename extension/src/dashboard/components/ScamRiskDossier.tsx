import React, { useState } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertOctagon,
  AlertTriangle,
  CheckCircle2,
  PackageCheck,
  Info,
  Lock,
  ChevronRight
} from 'lucide-react';
import { ScamRiskAssessment } from '../../types/contracts';

interface ScamRiskDossierProps {
  scamRisk?: ScamRiskAssessment;
}

export default function ScamRiskDossier({ scamRisk }: ScamRiskDossierProps) {
  if (!scamRisk) {
    return (
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 text-center text-xs text-slate-400">
        Scam risk assessment unavailable for this listing.
      </div>
    );
  }

  const {
    risk_score,
    risk_level,
    verdict_title,
    verdict_summary,
    positive_safety_signals,
    warning_flags,
    safety_checklist
  } = scamRisk;

  const [completedSteps, setCompletedSteps] = useState<number[]>([]);

  const toggleStep = (idx: number) => {
    setCompletedSteps((prev) =>
      prev.includes(idx) ? prev.filter((i) => i !== idx) : [...prev, idx]
    );
  };

  const isLowRisk = risk_level === 'LOW';
  const isModerateRisk = risk_level === 'MODERATE';

  return (
    <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            {isLowRisk ? (
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            ) : isModerateRisk ? (
              <ShieldAlert className="w-4 h-4 text-amber-400" />
            ) : (
              <AlertOctagon className="w-4 h-4 text-rose-400" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Scam & Counterfeit Fraud Risk Dossier
            </h3>
            <p className="text-xs text-slate-400">
              Multi-factor assessment evaluating pricing deviations, merchant reputation, and return shields
            </p>
          </div>
        </div>

        <span className={`px-3 py-1 text-xs font-black rounded-full self-start sm:self-auto ${
          isLowRisk
            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
            : isModerateRisk
            ? 'bg-amber-950 text-amber-400 border border-amber-800'
            : 'bg-rose-950 text-rose-400 border border-rose-800'
        }`}>
          {risk_level} SCAM RISK ({risk_score}%)
        </span>
      </div>

      {/* Primary Verdict Card */}
      <div className={`rounded-xl p-5 border space-y-2 ${
        isLowRisk
          ? 'bg-emerald-950/20 border-emerald-800/40'
          : isModerateRisk
          ? 'bg-amber-950/20 border-amber-800/40'
          : 'bg-rose-950/20 border-rose-800/40'
      }`}>
        <div className="flex items-center gap-2">
          {isLowRisk ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0" />
          )}
          <h4 className="text-sm font-black text-white">{verdict_title}</h4>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed pl-7">
          {verdict_summary}
        </p>
      </div>

      {/* 2-Column Factors Grid (Positive Safety Signals vs Warnings) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Verified Positive Signals */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 space-y-2.5">
          <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" />
            <span>Verified Buyer Protection Factors ({positive_safety_signals.length})</span>
          </div>
          <div className="space-y-2 pt-1">
            {positive_safety_signals.map((sig, idx) => (
              <div key={idx} className="flex items-start gap-2 text-xs text-emerald-300/90 leading-relaxed">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>{sig}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Warning Flags */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 space-y-2.5">
          <div className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4" />
            <span>Detected Red Flags & Vulnerabilities ({warning_flags.length})</span>
          </div>
          <div className="space-y-2 pt-1">
            {warning_flags.length > 0 ? (
              warning_flags.map((flag, idx) => (
                <div key={idx} className="flex items-start gap-2 text-xs text-rose-300/90 leading-relaxed">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                  <span>{flag}</span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 italic">No abnormal discounts, unrated merchants, or bot red flags detected.</p>
            )}
          </div>
        </div>
      </div>

      {/* Interactive Buyer Safety Delivery Checklist */}
      <div className="bg-slate-950/80 border border-slate-800/90 rounded-xl p-5 space-y-3.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-white uppercase tracking-wider">
            <PackageCheck className="w-4 h-4 text-blue-400" />
            <span>Interactive Buyer Delivery & Unboxing Checklist</span>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            {completedSteps.length} of {safety_checklist.length} verified
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1">
          {safety_checklist.map((step, idx) => {
            const isDone = completedSteps.includes(idx);

            return (
              <button
                key={idx}
                onClick={() => toggleStep(idx)}
                className={`text-left p-3 rounded-xl border transition-all flex items-start gap-2.5 cursor-pointer ${
                  isDone
                    ? 'bg-blue-950/40 border-blue-600/50 text-blue-200'
                    : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <div className={`w-4 h-4 rounded-md border flex items-center justify-center shrink-0 mt-0.5 transition-colors ${
                  isDone ? 'bg-blue-600 border-blue-500 text-white' : 'border-slate-600 bg-slate-800'
                }`}>
                  {isDone && <CheckCircle2 className="w-3 h-3 text-white" />}
                </div>
                <span className="text-xs leading-normal">{step}</span>
              </button>
            );
          })}
        </div>
      </div>
    </section>
  );
}
