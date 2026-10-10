import React from 'react';
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Layers,
  Sparkles,
  Info,
  CheckCircle2,
  Activity,
  Copy
} from 'lucide-react';
import { ReviewCredibilityResult } from '../../types/contracts';

interface ReviewClusterExplorerProps {
  credibility: ReviewCredibilityResult;
}

export default function ReviewClusterExplorer({ credibility }: ReviewClusterExplorerProps) {
  const {
    trust_score,
    anomaly_level,
    sample_size,
    total_ratings_available,
    duplicate_cluster_ratio,
    entropy_score,
    polarity_drift_ratio,
    estimated_genuine_pct,
    estimated_fake_pct,
    authenticity_status,
    authenticity_reason,
    signals,
    executive_summary,
    data_limitation_notice
  } = credibility;

  // Maximum entropy for a 5-star distribution is log2(5) ~ 2.322 bits
  const entropyPct = Math.round((entropy_score / 2.322) * 100);

  return (
    <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            <Shield className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Review Credibility & Linguistic Cluster Analysis
            </h3>
            <p className="text-xs text-slate-400">
              Deterministic NLP heuristic audit assessing text duplication, star polarity, and bot templating
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Audited Sample:</span>
          <span className="text-xs font-mono font-bold text-white bg-slate-800 px-2.5 py-0.5 rounded border border-slate-700">
            {sample_size} on-page reviews / {total_ratings_available || 'unknown'} catalog ratings
          </span>
        </div>
      </div>

      {/* Primary Authenticity Dual Progress Bar */}
      <div className="bg-slate-950/80 border border-slate-800/80 rounded-xl p-5 space-y-3.5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-200">Estimated Authenticity Distribution</span>
            <span className={`text-[10px] font-black uppercase px-2 py-0.5 rounded-full ${
              authenticity_status === 'LIKELY_AUTHENTIC'
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                : authenticity_status === 'MODERATE_SUSPICION'
                ? 'bg-amber-950 text-amber-400 border border-amber-800'
                : 'bg-rose-950 text-rose-400 border border-rose-800'
            }`}>
              {authenticity_status.replace(/_/g, ' ')}
            </span>
          </div>

          <div className="text-xs text-slate-400 font-mono">
            Trust Score: <strong className="text-white font-bold">{trust_score}</strong>/100 ({anomaly_level} Risk)
          </div>
        </div>

        {/* Dual Color Progress Bar */}
        <div className="w-full h-4 bg-rose-950/60 rounded-full overflow-hidden flex border border-slate-800 shadow-inner">
          <div
            className="h-full bg-emerald-500 transition-all duration-500 rounded-l-full flex items-center justify-end pr-2 text-[9px] font-black text-slate-950"
            style={{ width: `${estimated_genuine_pct}%` }}
          >
            {estimated_genuine_pct >= 20 ? `${estimated_genuine_pct.toFixed(0)}%` : ''}
          </div>
          <div
            className="h-full bg-rose-500 transition-all duration-500 rounded-r-full flex items-center justify-start pl-2 text-[9px] font-black text-white"
            style={{ width: `${estimated_fake_pct}%` }}
          >
            {estimated_fake_pct >= 15 ? `${estimated_fake_pct.toFixed(0)}%` : ''}
          </div>
        </div>

        <div className="flex items-center justify-between text-xs font-bold pt-0.5">
          <span className="text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            ~{estimated_genuine_pct?.toFixed(0)}% Organic Human Reviews
          </span>
          <span className="text-rose-400 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
            ~{estimated_fake_pct?.toFixed(0)}% Coordinated / Bot Reviews
          </span>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed italic bg-slate-900/50 p-3 rounded-lg border border-slate-800/60">
          "{authenticity_reason}"
        </p>
      </div>

      {/* Analytical Metrics Triad (Duplicate Ratio, Shannon Entropy, Polarity Drift) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Metric 1: Jaccard Duplicate Cluster Ratio */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold">Syntactic Overlap Ratio</span>
            <Copy className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="text-2xl font-black text-white">
            {(duplicate_cluster_ratio * 100).toFixed(1)}%
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                duplicate_cluster_ratio > 0.25 ? 'bg-rose-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, duplicate_cluster_ratio * 100 * 3)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 leading-normal">
            Proportion of reviews sharing high Jaccard character 3-shingle similarity (&ge;0.65).
          </p>
        </div>

        {/* Metric 2: Shannon Entropy Rating Spread */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold">Rating Entropy Spread</span>
            <Activity className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="text-2xl font-black text-white">
            {entropy_score.toFixed(2)} <span className="text-xs text-slate-500 font-normal">/ 2.32 bits</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                entropy_score < 0.6 ? 'bg-amber-500' : 'bg-indigo-500'
              }`}
              style={{ width: `${Math.min(100, entropyPct)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 leading-normal">
            Shannon entropy across 1-5 star distributions. Values &lt;0.6 indicate artificial rating skew.
          </p>
        </div>

        {/* Metric 3: Polarity Contradiction Drift */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold">Star-Text Polarity Drift</span>
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-2xl font-black text-white">
            {(polarity_drift_ratio * 100).toFixed(1)}%
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                polarity_drift_ratio > 0.1 ? 'bg-rose-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, polarity_drift_ratio * 100 * 5)}%` }}
            />
          </div>
          <p className="text-[11px] text-slate-500 leading-normal">
            Percentage of 4-5 star reviews whose textual contents express severe critical complaints.
          </p>
        </div>
      </div>

      {/* Cluster Signals Detail Grid */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-blue-400" />
          Detected Linguistic Cluster Signals ({signals.length})
        </h4>

        {signals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {signals.map((sig, idx) => (
              <div
                key={idx}
                className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-4 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                    {sig.signal_type.replace(/_/g, ' ')}
                  </span>
                  <span className={`text-[10px] font-black px-2 py-0.5 rounded uppercase ${
                    sig.severity === 'HIGH'
                      ? 'bg-rose-950 text-rose-400 border border-rose-800'
                      : 'bg-amber-950 text-amber-400 border border-amber-800'
                  }`}>
                    {sig.severity} Severity
                  </span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {sig.description}
                </p>
                {sig.affected_review_ids && sig.affected_review_ids.length > 0 && (
                  <div className="text-[10px] text-slate-500 font-mono">
                    Affects Review IDs: [{sig.affected_review_ids.join(', ')}]
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-emerald-950/20 border border-emerald-800/30 rounded-xl p-4 text-xs text-emerald-300 flex items-center gap-2.5">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
            <div>
              <strong>Organic Linguistic Variance Confirmed:</strong> No coordinated copy-paste clusters, generic hyperbole spam, or star-rating contradictions were identified in the audited sample.
            </div>
          </div>
        )}
      </div>

      {/* Transparency & Limitations Notice */}
      <div className="text-xs text-slate-400 border-t border-slate-800/80 pt-4 flex items-start gap-2 leading-relaxed">
        <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-300">Methodology & Mathematical Limits: </strong>
          {data_limitation_notice}
        </div>
      </div>
    </section>
  );
}
