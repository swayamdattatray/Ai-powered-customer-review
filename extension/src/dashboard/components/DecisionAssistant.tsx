import React from 'react';
import {
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  TrendingDown,
  AlertTriangle,
  HelpCircle,
  ThumbsUp,
  ThumbsDown,
  CheckCircle2,
  Info
} from 'lucide-react';
import { ProductIntelligenceResponse } from '../../types/contracts';

interface DecisionAssistantProps {
  intelligence: ProductIntelligenceResponse;
}

export default function DecisionAssistant({ intelligence }: DecisionAssistantProps) {
  const { credibility, arbitrage, history, scam_risk, prices, current_price } = intelligence;

  // 1. Credibility Evaluation
  const credibilityVerdict =
    credibility.trust_score >= 75
      ? 'High Credibility'
      : credibility.trust_score >= 50
      ? 'Moderate Credibility'
      : 'Low Credibility (High Bot Anomaly)';

  // 2. Pros and Cons extraction from aspects
  const topPros = credibility.aspects
    .filter((a) => a.score >= 3.5)
    .slice(0, 3);
  const topCons = credibility.aspects
    .filter((a) => a.score <= 3.0)
    .slice(0, 3);

  // 3. Price Arbitrage Status
  const priceComparisonVerdict = arbitrage.has_arbitrage && arbitrage.potential_savings
    ? `Available for ₹${arbitrage.potential_savings.toLocaleString('en-IN')} less on ${arbitrage.cheapest_platform}`
    : arbitrage.sources_compared > 1
    ? 'Prices are competitive across verified platforms'
    : 'Single retailer live price checked';

  // 4. Cheaper Alternatives / Best Merchant
  const cheaperAlternative =
    arbitrage.has_arbitrage && arbitrage.cheapest_platform
      ? `${arbitrage.cheapest_platform} offers the lowest verified landed price of ₹${arbitrage.lowest_price?.toLocaleString('en-IN')}`
      : 'Current listed price is currently the lowest verified tier among tracked retailers';

  // 5. Limitations to consider
  const limitations: string[] = [];
  if (credibility.duplicate_cluster_ratio > 0.15) {
    limitations.push(`${Math.round(credibility.duplicate_cluster_ratio * 100)}% of accessible reviews share syntactically repetitive phrasing.`);
  }
  if (scam_risk?.warning_flags && scam_risk.warning_flags.length > 0) {
    limitations.push(...scam_risk.warning_flags);
  }
  if (limitations.length === 0) {
    limitations.push('Always confirm model variant and storage capacity match before checkout.');
  }

  return (
    <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Shopping Decision Assistant
            </h3>
            <p className="text-xs text-slate-400">
              Evidence-based evaluation answering the 5 critical pre-purchase questions
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Evidence Confidence:</span>
          <span className="text-xs font-black text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-0.5 rounded-full">
            {credibility.sample_size >= 10 ? 'HIGH (Multi-Signal)' : 'ESTIMATED (Sample Bound)'}
          </span>
        </div>
      </div>

      {/* 5 Critical Questions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Q1: Review Credibility */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4.5 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[11px] font-black">
              1
            </span>
            <span>How credible are reviews?</span>
          </div>
          <div className="text-sm font-black text-white flex items-center gap-1.5">
            {credibility.trust_score >= 70 ? (
              <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
            )}
            <span>{credibilityVerdict} ({credibility.trust_score}/100)</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            ~{credibility.estimated_genuine_pct?.toFixed(0)}% genuine reviews. {credibility.authenticity_reason}
          </p>
        </div>

        {/* Q2: Customer Feedback (Likes & Dislikes) */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4.5 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[11px] font-black">
              2
            </span>
            <span>What do customers like/dislike?</span>
          </div>
          <div className="space-y-1.5 text-xs">
            {topPros.length > 0 && (
              <div className="text-emerald-400 flex items-start gap-1.5">
                <ThumbsUp className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                <span className="truncate">Praised: {topPros.map((p) => p.aspect).join(', ')}</span>
              </div>
            )}
            {topCons.length > 0 ? (
              <div className="text-rose-400 flex items-start gap-1.5">
                <ThumbsDown className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                <span className="truncate">Critiqued: {topCons.map((c) => c.aspect).join(', ')}</span>
              </div>
            ) : (
              <div className="text-slate-400 flex items-start gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                <span>No recurring hardware complaints.</span>
              </div>
            )}
          </div>
        </div>

        {/* Q3: Price Comparison */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4.5 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[11px] font-black">
              3
            </span>
            <span>How does the price compare?</span>
          </div>
          <div className="text-sm font-black text-white flex items-center gap-1.5">
            <TrendingDown className="w-4 h-4 text-blue-400 shrink-0" />
            <span className="truncate">{priceComparisonVerdict}</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            {arbitrage.status_notice}
          </p>
        </div>

        {/* Q4: Cheaper Alternatives */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4.5 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[11px] font-black">
              4
            </span>
            <span>Are there cheaper alternatives?</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed">
            {cheaperAlternative}
          </p>
          <div className="text-[11px] text-slate-500">
            Tracked across 4 verified retailers (Amazon, Flipkart, Croma, Reliance Digital).
          </div>
        </div>

        {/* Q5: Limitations to Consider */}
        <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4.5 space-y-2 md:col-span-2">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300">
            <span className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[11px] font-black">
              5
            </span>
            <span>What limitations should I consider before buying?</span>
          </div>
          <div className="space-y-1">
            {limitations.map((lim, idx) => (
              <div key={idx} className="flex items-start gap-1.5 text-xs text-amber-300/90">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                <span>{lim}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
