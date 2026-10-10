import React from 'react';
import {
  TrendingDown,
  ExternalLink,
  Calendar,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  Info,
  CheckCircle2,
  DollarSign
} from 'lucide-react';
import {
  PlatformPriceItem,
  PriceArbitrageSummary,
  PriceHistoryAnalytics
} from '../../types/contracts';

interface PriceMatrixTableProps {
  prices: PlatformPriceItem[];
  arbitrage: PriceArbitrageSummary;
  history?: PriceHistoryAnalytics;
}

export default function PriceMatrixTable({
  prices,
  arbitrage,
  history
}: PriceMatrixTableProps) {
  const maxPrice = Math.max(
    ...prices.map((p) => p.final_landed_price || 0),
    1
  );

  return (
    <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            <TrendingDown className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Cross-Platform Landed Price Comparison Matrix
            </h3>
            <p className="text-xs text-slate-400">
              Normalized comparison across Indian e-commerce platforms with variant matching verification
            </p>
          </div>
        </div>

        {arbitrage.has_arbitrage && arbitrage.potential_savings && (
          <div className="text-xs font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-3 py-1 rounded-full flex items-center gap-1.5 self-start">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Save up to ₹{arbitrage.potential_savings.toLocaleString('en-IN')} on {arbitrage.cheapest_platform}</span>
          </div>
        )}
      </div>

      {/* Formula Explanation Banner */}
      <div className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-400">
        <div className="flex items-center gap-2 font-mono text-[11px] text-slate-300">
          <span className="text-blue-400 font-bold">Calculation:</span>
          <span>Final Landed Price = Listed Price + Shipping Charges - Verified Discounts</span>
        </div>
        <div className="text-[11px] text-slate-500 italic">
          *Bank offers, personal coupons, and payment cashbacks excluded until checkout.
        </div>
      </div>

      {/* 4-Retailer Comparison Table Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {prices.map((item, idx) => {
          const isCheapest =
            item.platform === arbitrage.cheapest_platform &&
            arbitrage.sources_compared > 1 &&
            item.status === 'SUCCESS';
          const pct = item.final_landed_price
            ? Math.round((item.final_landed_price / maxPrice) * 100)
            : 0;

          return (
            <div
              key={idx}
              className={`rounded-2xl p-5 flex flex-col justify-between border transition-all ${
                isCheapest
                  ? 'bg-slate-950 border-emerald-500/70 shadow-xl shadow-emerald-950/40 ring-1 ring-emerald-500/30'
                  : 'bg-slate-950/80 border-slate-800/90 hover:border-slate-700'
              }`}
            >
              <div className="space-y-3.5">
                {/* Platform Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-black text-white">{item.platform}</span>
                    {item.status === 'SUCCESS' && (
                      <span className="w-2 h-2 rounded-full bg-emerald-500" title="Live Price Verified" />
                    )}
                  </div>
                  {isCheapest && (
                    <span className="bg-emerald-500 text-slate-950 text-[10px] font-black px-2 py-0.5 rounded uppercase">
                      Lowest Price
                    </span>
                  )}
                </div>

                {/* Price Breakdown */}
                <div>
                  {item.final_landed_price ? (
                    <div>
                      <div className="text-2xl font-black text-white">
                        ₹{item.final_landed_price.toLocaleString('en-IN')}
                      </div>
                      <div className="text-[10px] text-slate-400 mt-0.5">
                        Listed: ₹{item.listed_price?.toLocaleString('en-IN')} | Shipping: ₹{item.shipping_charge}
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="text-sm font-bold text-slate-400">Direct Verified Link</div>
                      <div className="text-[10px] text-slate-500 mt-0.5">
                        Click below to verify live pricing
                      </div>
                    </div>
                  )}
                </div>

                {/* Match Confidence & Variant Audit */}
                <div className="space-y-1 pt-1">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-400">Match Confidence:</span>
                    <span className={`font-bold font-mono ${
                      item.match_confidence === 'EXACT'
                        ? 'text-emerald-400'
                        : item.match_confidence === 'HIGH'
                        ? 'text-blue-400'
                        : 'text-amber-400'
                    }`}>
                      {item.match_confidence}
                    </span>
                  </div>

                  {item.spec_deltas && item.spec_deltas.length > 0 && (
                    <div className="text-[10px] text-amber-300 bg-amber-950/40 border border-amber-800/50 rounded-lg p-2 leading-relaxed">
                      ⚠️ {item.spec_deltas.join(', ')}
                    </div>
                  )}
                </div>

                {/* Provenance & Last Checked */}
                <div className="text-[10px] text-slate-500 border-t border-slate-800/80 pt-2 flex items-center justify-between">
                  <span>Source: {item.data_provenance}</span>
                  <span>{item.last_checked.split(',')[1] || 'Today'}</span>
                </div>
              </div>

              {/* Purchase / Compare Button */}
              <div className="pt-4 mt-4 border-t border-slate-800/80">
                {item.product_url ? (
                  <a
                    href={item.product_url}
                    target="_blank"
                    rel="noreferrer"
                    className={`w-full inline-flex items-center justify-center gap-1.5 py-2 px-3 text-xs font-bold rounded-xl transition-all ${
                      isCheapest
                        ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-md'
                        : 'bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700/60'
                    }`}
                  >
                    <span>View on {item.platform}</span>
                    <ExternalLink className="w-3.5 h-3.5 opacity-70" />
                  </a>
                ) : (
                  <span className="text-xs text-slate-500 text-center block">Listing Unavailable</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* 30-Day Historical Price Trendline Section */}
      {history && history.has_history && (
        <div className="bg-slate-950/80 border border-slate-800/90 rounded-2xl p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-400" />
              <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                30-Day Historical Price Range & Timing Evaluation
              </h4>
            </div>

            <span className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full ${
              history.recommendation === 'GOOD_TIME_TO_BUY'
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                : history.recommendation === 'WAIT_FOR_SALE'
                ? 'bg-amber-950 text-amber-400 border border-amber-800'
                : 'bg-blue-950 text-blue-400 border border-blue-800'
            }`}>
              {history.recommendation.replace(/_/g, ' ')}
            </span>
          </div>

          {/* 3-Column Range Stats */}
          <div className="grid grid-cols-3 gap-3 text-center bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase">30-Day Lowest</div>
              <div className="text-sm font-black text-emerald-400">
                ₹{history.lowest_recorded?.toLocaleString('en-IN')}
              </div>
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase">Historical Average</div>
              <div className="text-sm font-black text-slate-300">
                ₹{history.average_recorded?.toLocaleString('en-IN')}
              </div>
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase">30-Day Highest</div>
              <div className="text-sm font-black text-slate-400">
                ₹{history.highest_recorded?.toLocaleString('en-IN')}
              </div>
            </div>
          </div>

          {/* Interactive Bar Trendline */}
          {history.history_points.length > 0 && (
            <div className="h-24 bg-slate-900/40 border border-slate-800/80 rounded-xl p-3 flex items-end justify-between gap-2">
              {history.history_points.map((pt, idx) => {
                const min = history.lowest_recorded || 1;
                const max = history.highest_recorded || 1;
                const range = Math.max(max - min, 1);
                const heightPct = Math.round(((pt.price - min) / range) * 55) + 35;

                return (
                  <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                    <div
                      className="w-full max-w-[28px] bg-indigo-500/80 group-hover:bg-indigo-400 rounded-t-sm transition-all"
                      style={{ height: `${heightPct}%` }}
                    />
                    <span className="text-[9px] text-slate-400 mt-1">{pt.date}</span>
                    <div className="absolute -top-7 hidden group-hover:flex bg-slate-900 border border-slate-700 text-white text-[10px] px-2 py-0.5 rounded shadow-lg pointer-events-none whitespace-nowrap z-20">
                      ₹{pt.price.toLocaleString('en-IN')}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          <div className="text-xs text-slate-300 leading-relaxed italic bg-indigo-950/20 border border-indigo-800/30 p-3 rounded-xl flex items-start gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <span>{history.recommendation_reason}</span>
          </div>
        </div>
      )}
    </section>
  );
}
