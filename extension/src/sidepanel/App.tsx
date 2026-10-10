import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  TrendingDown,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  ShoppingBag,
  Sparkles,
  Info,
  Calendar,
  ChevronRight,
  X,
  MessageSquare,
  CheckCircle2,
  AlertOctagon,
  PackageCheck
} from 'lucide-react';
import {
  ExtractedProductPayload,
  ProductIntelligenceResponse,
  AspectSentiment
} from '../types/contracts';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

export default function App() {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentProduct, setCurrentProduct] = useState<ExtractedProductPayload | null>(null);
  const [intelligence, setIntelligence] = useState<ProductIntelligenceResponse | null>(null);
  const [selectedAspect, setSelectedAspect] = useState<AspectSentiment | null>(null);
  const [showSafetyChecklist, setShowSafetyChecklist] = useState<boolean>(false);

  const fetchIntelligence = async (payload: ExtractedProductPayload) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/intelligence/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) {
        throw new Error(`Backend API returned HTTP ${resp.status}`);
      }
      const data: ProductIntelligenceResponse = await resp.json();
      setIntelligence(data);
    } catch (err: any) {
      setError(err.message || 'Unable to communicate with local shopping intelligence service.');
    } finally {
      setLoading(false);
    }
  };

  const loadActiveProduct = () => {
    setLoading(true);
    chrome.runtime.sendMessage({ type: 'GET_ACTIVE_TAB_PRODUCT' }, (response) => {
      const payload: ExtractedProductPayload | null = response?.payload;
      if (payload && payload.title) {
        setCurrentProduct(payload);
        fetchIntelligence(payload);
      } else {
        setCurrentProduct(null);
        setIntelligence(null);
        setLoading(false);
      }
    });
  };

  useEffect(() => {
    loadActiveProduct();

    const listener = (msg: any) => {
      if (msg.type === 'BROADCAST_PRODUCT_UPDATE' && msg.payload) {
        setCurrentProduct(msg.payload);
        fetchIntelligence(msg.payload);
      }
    };
    chrome.runtime.onMessage.addListener(listener);
    return () => chrome.runtime.onMessage.removeListener(listener);
  }, []);

  // 1. Idle State: User is browsing non-product page
  if (!loading && !currentProduct) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[480px] p-6 text-center">
        <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl flex items-center justify-center mb-4 shadow-sm">
          <ShoppingBag className="w-8 h-8" />
        </div>
        <h2 className="text-lg font-bold text-slate-800">No Product Detected</h2>
        <p className="text-xs text-slate-500 mt-2 max-w-[260px] leading-relaxed">
          Navigate to an Amazon.in or Flipkart product page to view real-time credibility scores, price trends, and cross-platform arbitrage.
        </p>
        <button
          onClick={loadActiveProduct}
          className="mt-6 inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Scan Active Tab
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 pb-8 relative">
      {/* Top Navigation */}
      <header className="bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-10 flex items-center justify-between shadow-xs">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-blue-600 text-white rounded-lg flex items-center justify-center font-black text-sm">
            AI
          </div>
          <div>
            <h1 className="text-xs font-bold text-slate-900 tracking-tight">Shopping Intelligence</h1>
            <p className="text-[10px] text-slate-500">4-Platform Arbitrage & Trust Index</p>
          </div>
        </div>
        <button
          onClick={loadActiveProduct}
          disabled={loading}
          className="p-1.5 text-slate-400 hover:text-blue-600 rounded-md hover:bg-blue-50 transition-colors"
          title="Refresh intelligence"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-600' : ''}`} />
        </button>
      </header>

      {/* Main Container */}
      <main className="p-4 space-y-4">
        {/* Product Identity Banner */}
        {currentProduct && (
          <div className="bg-white border border-slate-200 rounded-xl p-3.5 shadow-2xs">
            <div className="flex items-start justify-between gap-2">
              <span className="inline-block px-2 py-0.5 text-[10px] font-bold rounded-md uppercase tracking-wider bg-blue-50 text-blue-700 border border-blue-200">
                {currentProduct.platform.replace('_', ' ')}
              </span>
              {currentProduct.listed_price && (
                <div className="text-sm font-black text-slate-900">
                  ₹{currentProduct.listed_price.toLocaleString('en-IN')}
                </div>
              )}
            </div>
            <h2 className="text-xs font-semibold text-slate-800 mt-2 line-clamp-2 leading-snug">
              {currentProduct.title}
            </h2>
            {(currentProduct.seller_name || currentProduct.is_fulfilled_by_platform) && (
              <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-500">
                {currentProduct.seller_name ? (
                  <span>Merchant: <strong className="text-slate-800">{currentProduct.seller_name}</strong></span>
                ) : <span />}
                {currentProduct.is_fulfilled_by_platform && (
                  <span className="text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded font-semibold border border-emerald-200">
                    ✓ Platform Fulfilled
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white border border-slate-200 rounded-xl p-6 text-center space-y-3">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mx-auto" />
            <p className="text-xs font-medium text-slate-600">Analyzing credibility, price trends & 4 retailers...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 text-xs text-amber-800 flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-bold">Service Notice:</strong> {error}
            </div>
          </div>
        )}

        {/* Render Intelligence Components */}
        {intelligence && !loading && (
          <>
            {/* OPTION A: Historical Price Tracking & Good-Time-To-Buy Recommendation */}
            {intelligence.history && intelligence.history.has_history && (
              <section className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-4 h-4 text-indigo-600" />
                    <h3 className="text-xs font-bold text-slate-900">Price History & Timing</h3>
                  </div>
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                    intelligence.history.recommendation === 'GOOD_TIME_TO_BUY'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : intelligence.history.recommendation === 'WAIT_FOR_SALE'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}>
                    {intelligence.history.recommendation.replace(/_/g, ' ')}
                  </span>
                </div>

                {/* 30-Day Range Stats */}
                <div className="grid grid-cols-3 gap-2 text-center bg-slate-50 border border-slate-100 rounded-lg p-2.5">
                  <div>
                    <div className="text-[10px] font-bold text-slate-400 uppercase">Lowest</div>
                    <div className="text-xs font-black text-emerald-700">₹{intelligence.history.lowest_recorded?.toLocaleString('en-IN')}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-bold text-slate-400 uppercase">Average</div>
                    <div className="text-xs font-black text-slate-700">₹{intelligence.history.average_recorded?.toLocaleString('en-IN')}</div>
                  </div>
                  <div>
                    <div className="text-[10px] font-bold text-slate-400 uppercase">Highest</div>
                    <div className="text-xs font-black text-slate-700">₹{intelligence.history.highest_recorded?.toLocaleString('en-IN')}</div>
                  </div>
                </div>

                {/* Recommendation Reason */}
                <div className="text-[11px] text-slate-600 leading-relaxed bg-indigo-50/50 border border-indigo-100 rounded-lg p-2.5 flex items-start gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-600 shrink-0 mt-0.5" />
                  <span>{intelligence.history.recommendation_reason}</span>
                </div>

                {/* Mini Historical Trend Points */}
                {intelligence.history.history_points.length > 0 && (
                  <div className="pt-1">
                    <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">30-Day Trendline</div>
                    <div className="flex items-end justify-between gap-1 h-16 pt-2 px-1 bg-slate-50 rounded-lg border border-slate-100">
                      {intelligence.history.history_points.map((pt, idx) => {
                        const min = intelligence.history?.lowest_recorded || 1;
                        const max = intelligence.history?.highest_recorded || 1;
                        const range = Math.max(max - min, 1);
                        const heightPct = Math.round(((pt.price - min) / range) * 60) + 30;

                        return (
                          <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                            <div
                              className="w-full max-w-[18px] bg-indigo-500 rounded-t-sm transition-all group-hover:bg-indigo-600"
                              style={{ height: `${heightPct}%` }}
                            />
                            <span className="text-[8px] text-slate-400 mt-1">{pt.date}</span>
                            {/* Hover tooltip */}
                            <div className="absolute -top-7 hidden group-hover:flex bg-slate-900 text-white text-[9px] px-1.5 py-0.5 rounded shadow pointer-events-none whitespace-nowrap z-20">
                              ₹{pt.price.toLocaleString('en-IN')}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </section>
            )}

            {/* 1. Review Credibility Index */}
            <section className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  {intelligence.credibility.trust_score >= 75 ? (
                    <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <ShieldAlert className="w-4 h-4 text-amber-600" />
                  )}
                  <h3 className="text-xs font-bold text-slate-900">Review Trust Index</h3>
                </div>
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                  intelligence.credibility.anomaly_level === 'LOW'
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : intelligence.credibility.anomaly_level === 'ELEVATED'
                    ? 'bg-amber-50 text-amber-700 border border-amber-200'
                    : 'bg-rose-50 text-rose-700 border border-rose-200'
                }`}>
                  {intelligence.credibility.anomaly_level} RISK
                </span>
              </div>

              {/* Trust Score Bar */}
              <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
                <div className="flex items-baseline justify-between mb-1">
                  <span className="text-[11px] font-semibold text-slate-600">Statistical Credibility</span>
                  <span className="text-base font-black text-slate-900">{intelligence.credibility.trust_score}<span className="text-xs font-normal text-slate-400">/100</span></span>
                </div>
                <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 rounded-full ${
                      intelligence.credibility.trust_score >= 75
                        ? 'bg-emerald-500'
                        : intelligence.credibility.trust_score >= 50
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                    }`}
                    style={{ width: `${intelligence.credibility.trust_score}%` }}
                  />
                </div>
                <div className="text-[10px] text-slate-500 mt-2 leading-relaxed">
                  {intelligence.credibility.executive_summary}
                </div>
              </div>

              {/* Real vs Fake Review Breakdown Gauge */}
              <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="text-[11px] font-bold text-slate-700">Review Authenticity (Real vs Fake)</div>
                  <span className={`px-2 py-0.5 text-[9px] font-bold rounded-full ${
                    intelligence.credibility.authenticity_status === 'LIKELY_AUTHENTIC'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : intelligence.credibility.authenticity_status === 'MODERATE_SUSPICION'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}>
                    {intelligence.credibility.authenticity_status.replace(/_/g, ' ')}
                  </span>
                </div>

                <div className="space-y-1">
                  <div className="flex items-center justify-between text-[10px] font-bold">
                    <span className="text-emerald-700">~{intelligence.credibility.estimated_genuine_pct?.toFixed(0)}% Genuine</span>
                    <span className="text-rose-700">~{intelligence.credibility.estimated_fake_pct?.toFixed(0)}% Suspicious / Bots</span>
                  </div>
                  <div className="w-full h-2.5 bg-rose-200 rounded-full overflow-hidden flex">
                    <div
                      className="h-full bg-emerald-500 transition-all duration-500 rounded-l-full"
                      style={{ width: `${intelligence.credibility.estimated_genuine_pct || 85}%` }}
                    />
                    <div
                      className="h-full bg-rose-500 transition-all duration-500 rounded-r-full"
                      style={{ width: `${intelligence.credibility.estimated_fake_pct || 15}%` }}
                    />
                  </div>
                </div>

                <p className="text-[10px] text-slate-600 leading-relaxed italic">
                  {intelligence.credibility.authenticity_reason}
                </p>
              </div>

              {/* Signals */}
              {intelligence.credibility.signals.length > 0 && (
                <div className="space-y-1.5 pt-1">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Detected Patterns</span>
                  {intelligence.credibility.signals.map((sig, i) => (
                    <div key={i} className="bg-amber-50 border border-amber-100 rounded-lg p-2 text-[11px] text-amber-900 flex items-start gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                      <span>{sig.description}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* Data Limitation Notice */}
              <div className="text-[10px] text-slate-400 flex items-start gap-1 pt-1 border-t border-slate-100">
                <Info className="w-3 h-3 text-slate-400 shrink-0 mt-0.5" />
                <span>{intelligence.credibility.data_limitation_notice}</span>
              </div>
            </section>

            {/* Scam Risk & Buyer Protection Shield */}
            {intelligence.scam_risk && (
              <section className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5">
                    {intelligence.scam_risk.risk_level === 'LOW' ? (
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                    ) : intelligence.scam_risk.risk_level === 'MODERATE' ? (
                      <ShieldAlert className="w-4 h-4 text-amber-600" />
                    ) : (
                      <AlertOctagon className="w-4 h-4 text-rose-600" />
                    )}
                    <h3 className="text-xs font-bold text-slate-900">Scam & Fraud Risk</h3>
                  </div>
                  <span className={`px-2 py-0.5 text-[10px] font-bold rounded-full ${
                    intelligence.scam_risk.risk_level === 'LOW'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : intelligence.scam_risk.risk_level === 'MODERATE'
                      ? 'bg-amber-50 text-amber-700 border border-amber-200'
                      : 'bg-rose-50 text-rose-700 border border-rose-200'
                  }`}>
                    {intelligence.scam_risk.risk_level} RISK ({intelligence.scam_risk.risk_score}%)
                  </span>
                </div>

                {/* Verdict Card */}
                <div className={`rounded-lg p-3 border ${
                  intelligence.scam_risk.risk_level === 'LOW'
                    ? 'bg-emerald-50/50 border-emerald-100 text-emerald-950'
                    : intelligence.scam_risk.risk_level === 'MODERATE'
                    ? 'bg-amber-50/50 border-amber-100 text-amber-950'
                    : 'bg-rose-50/50 border-rose-100 text-rose-950'
                }`}>
                  <div className="text-xs font-bold mb-1">
                    {intelligence.scam_risk.verdict_title}
                  </div>
                  <p className="text-[11px] text-slate-600 leading-relaxed">
                    {intelligence.scam_risk.verdict_summary}
                  </p>
                </div>

                {/* Detected Signals & Flags */}
                <div className="space-y-1.5">
                  {intelligence.scam_risk.positive_safety_signals.map((sig, i) => (
                    <div key={`pos-${i}`} className="bg-emerald-50/60 border border-emerald-100 rounded-lg p-2 text-[11px] text-emerald-900 flex items-start gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span>{sig}</span>
                    </div>
                  ))}
                  {intelligence.scam_risk.warning_flags.map((flag, i) => (
                    <div key={`warn-${i}`} className="bg-rose-50/60 border border-rose-100 rounded-lg p-2 text-[11px] text-rose-900 flex items-start gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                      <span>{flag}</span>
                    </div>
                  ))}
                </div>

                {/* Buyer Protection Checklist Accordion */}
                <div className="pt-1 border-t border-slate-100">
                  <button
                    onClick={() => setShowSafetyChecklist(!showSafetyChecklist)}
                    className="w-full flex items-center justify-between text-[11px] font-bold text-slate-700 hover:text-blue-600 py-1 transition-colors cursor-pointer"
                  >
                    <span className="flex items-center gap-1.5">
                      <PackageCheck className="w-3.5 h-3.5 text-blue-600" /> Buyer Safety Checklist ({intelligence.scam_risk.safety_checklist.length})
                    </span>
                    <ChevronRight className={`w-3.5 h-3.5 text-slate-400 transition-transform ${showSafetyChecklist ? 'rotate-90' : ''}`} />
                  </button>

                  {showSafetyChecklist && (
                    <div className="mt-2 space-y-1.5 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                      {intelligence.scam_risk.safety_checklist.map((tip, idx) => (
                        <div key={idx} className="flex items-start gap-1.5 text-[10px] text-slate-600 leading-normal">
                          <span className="text-blue-600 font-bold shrink-0">{idx + 1}.</span>
                          <span>{tip}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* OPTION D: Cross-Platform Price Comparison (4 Platforms: Amazon, Flipkart, Croma, Reliance Digital) */}
            <section className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <TrendingDown className="w-4 h-4 text-blue-600" />
                  <h3 className="text-xs font-bold text-slate-900">Retailer Price Arbitrage</h3>
                </div>
                {intelligence.arbitrage.has_arbitrage && (
                  <span className="bg-emerald-50 text-emerald-700 border border-emerald-200 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                    <Sparkles className="w-3 h-3" /> Save ₹{intelligence.arbitrage.potential_savings?.toLocaleString('en-IN')}
                  </span>
                )}
              </div>

              {/* Price Items */}
              <div className="space-y-2 pt-1">
                {intelligence.prices.map((item, idx) => {
                  const maxPrice = Math.max(...intelligence.prices.map(p => p.final_landed_price || 0), 1);
                  const pct = item.final_landed_price ? (item.final_landed_price / maxPrice) * 100 : 0;
                  const isLowest = item.platform === intelligence.arbitrage.cheapest_platform && intelligence.arbitrage.sources_compared > 1;

                  return (
                    <div key={idx} className="bg-slate-50 border border-slate-100 rounded-lg p-2.5 space-y-1.5">
                      <div className="flex items-center justify-between text-xs font-bold">
                        <div className="flex items-center gap-1.5">
                          <span className="text-slate-900">{item.platform}</span>
                          {isLowest && (
                            <span className="bg-emerald-600 text-white text-[9px] font-bold px-1.5 py-0.2 rounded-sm">
                              BEST
                            </span>
                          )}
                        </div>
                        {item.final_landed_price ? (
                          <span className="text-slate-900 font-black">
                            ₹{item.final_landed_price.toLocaleString('en-IN')}
                          </span>
                        ) : (
                          <span className="text-slate-400 font-normal text-[11px]">Compare Link</span>
                        )}
                      </div>

                      {item.final_landed_price ? (
                        <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-500 ${
                              isLowest ? 'bg-emerald-500' : 'bg-blue-600'
                            }`}
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      ) : (
                        <div className="text-[10px] text-slate-500 italic">
                          {item.error_reason || 'Click below to verify live listing.'}
                        </div>
                      )}

                      {item.spec_deltas.length > 0 && (
                        <div className="text-[10px] text-amber-700 bg-amber-50 rounded px-1.5 py-0.5 border border-amber-200">
                          ⚠️ {item.spec_deltas.join(', ')}
                        </div>
                      )}

                      {item.product_url && (
                        <a
                          href={item.product_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-[10px] font-semibold text-blue-600 hover:text-blue-800 pt-0.5"
                        >
                          View on {item.platform} <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>

              <div className="text-[10px] text-slate-500 italic">
                {intelligence.arbitrage.status_notice}
              </div>
            </section>

            {/* OPTION B: Interactive Aspect Explorer with Grounded Quotes Modal */}
            {intelligence.credibility.aspects.length > 0 && (
              <section className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-900">Feature Performance</h3>
                  <span className="text-[10px] text-slate-400">Click to read quotes</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {intelligence.credibility.aspects.map((asp, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedAspect(asp)}
                      className="bg-slate-50 hover:bg-blue-50/50 border border-slate-100 hover:border-blue-200 rounded-lg p-2.5 text-left transition-colors cursor-pointer group"
                    >
                      <div className="flex items-center justify-between text-[11px] font-bold">
                        <span className="text-slate-800 group-hover:text-blue-600">{asp.aspect}</span>
                        <span className={asp.score >= 3.6 ? 'text-emerald-600' : (asp.score <= 2.8 ? 'text-rose-600' : 'text-slate-600')}>
                          {asp.score}/5
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-[10px] text-slate-500 mt-1">
                        <span>{asp.mentions} mentions</span>
                        <ChevronRight className="w-3 h-3 text-slate-300 group-hover:text-blue-500" />
                      </div>
                    </button>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>

      {/* OPTION B: Aspect Explorer Quote Citations Modal */}
      {selectedAspect && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-end sm:items-center justify-center p-3 animate-in fade-in">
          <div className="bg-white w-full max-w-sm rounded-2xl p-4 shadow-xl border border-slate-200 space-y-3 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-blue-600" />
                <h4 className="text-sm font-bold text-slate-900">{selectedAspect.aspect} Analysis</h4>
              </div>
              <button
                onClick={() => setSelectedAspect(null)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="flex items-center justify-between bg-slate-50 p-2.5 rounded-lg border border-slate-100">
              <div>
                <span className="text-xs font-semibold text-slate-600">Satisfaction Score</span>
                <div className="text-lg font-black text-slate-900">{selectedAspect.score} <span className="text-xs text-slate-400 font-normal">/ 5.0</span></div>
              </div>
              <span className={`px-2 py-0.5 text-xs font-bold rounded-md ${
                selectedAspect.score >= 3.6 ? 'bg-emerald-50 text-emerald-700' : 'bg-rose-50 text-rose-700'
              }`}>
                {selectedAspect.sentiment}
              </span>
            </div>

            <div>
              <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                Grounded Customer Citations ({selectedAspect.grounded_snippets.length})
              </div>
              {selectedAspect.grounded_snippets.length > 0 ? (
                <div className="space-y-2">
                  {selectedAspect.grounded_snippets.map((snippet, i) => (
                    <div key={i} className="bg-slate-50 border-l-2 border-blue-500 rounded-r-lg p-2.5 text-xs text-slate-700 italic leading-relaxed">
                      "{snippet}"
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-slate-400 italic">No direct text snippets captured for this feature.</p>
              )}
            </div>

            <button
              onClick={() => setSelectedAspect(null)}
              className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold rounded-lg transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
