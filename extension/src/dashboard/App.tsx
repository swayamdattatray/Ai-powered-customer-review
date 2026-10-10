import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertOctagon,
  TrendingDown,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  ShoppingBag,
  Sparkles,
  Info,
  Calendar,
  MessageSquare,
  CheckCircle2,
  PackageCheck,
  Shield,
  Layers,
  ChevronRight,
  HelpCircle,
  Sliders,
  LayoutDashboard
} from 'lucide-react';
import {
  ExtractedProductPayload,
  ProductIntelligenceResponse,
  AspectSentiment
} from '../types/contracts';

import DecisionAssistant from './components/DecisionAssistant';
import ReviewClusterExplorer from './components/ReviewClusterExplorer';
import AspectExplorer from './components/AspectExplorer';
import PriceMatrixTable from './components/PriceMatrixTable';
import ScamRiskDossier from './components/ScamRiskDossier';
import SettingsAndTransparency from './components/SettingsAndTransparency';

const API_BASE = 'http://127.0.0.1:8000/api/v1';

type DashboardTab = 'overview' | 'reviews' | 'aspects' | 'prices' | 'scam' | 'settings';

export default function DashboardApp() {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [productPayload, setProductPayload] = useState<ExtractedProductPayload | null>(null);
  const [intelligence, setIntelligence] = useState<ProductIntelligenceResponse | null>(null);
  const [activeTab, setActiveTab] = useState<DashboardTab>('overview');

  // 1. Deterministic State Handoff from chrome.storage.local & URL Query Parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const targetId = urlParams.get('id');
    const targetSku = urlParams.get('sku');
    const targetPlatform = urlParams.get('platform');

    const resolveProductPayload = async () => {
      setLoading(true);
      setError(null);

      // Attempt reading cached payload from chrome.storage.local
      if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
        const storageKeys = targetId
          ? [`product_${targetId}`, 'latest_dashboard_product']
          : ['latest_dashboard_product'];

        chrome.storage.local.get(storageKeys, (items) => {
          let foundPayload: ExtractedProductPayload | null = null;
          if (targetId && items[`product_${targetId}`]) {
            foundPayload = items[`product_${targetId}`];
          } else if (items.latest_dashboard_product) {
            foundPayload = items.latest_dashboard_product;
          }

          if (foundPayload) {
            setProductPayload(foundPayload);
            fetchDeepIntelligence(foundPayload);
          } else if (targetSku) {
            // Construct baseline payload from query params
            const fallbackPayload: ExtractedProductPayload = {
              url: window.location.href,
              platform: (targetPlatform as any) || 'AMAZON_IN',
              sku: targetSku,
              title: `Product Listing (${targetSku})`,
              currency: 'INR',
              availability: true,
              attributes: {},
              reviews: []
            };
            setProductPayload(fallbackPayload);
            fetchDeepIntelligence(fallbackPayload);
          } else {
            setLoading(false);
          }
        });
      } else {
        // Fallback for standalone preview
        setLoading(false);
      }
    };

    resolveProductPayload();
  }, []);

  const fetchDeepIntelligence = async (payload: ExtractedProductPayload) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${API_BASE}/intelligence/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) {
        throw new Error(`Intelligence API returned HTTP ${resp.status}`);
      }
      const data: ProductIntelligenceResponse = await resp.json();
      setIntelligence(data);
    } catch (err: any) {
      setError(err.message || 'Unable to communicate with local shopping intelligence service.');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    if (productPayload) {
      fetchDeepIntelligence(productPayload);
    }
  };

  // ---------------------------------------------------------------------------
  // Empty State: No product detected
  // ---------------------------------------------------------------------------
  if (!loading && !productPayload && !intelligence) {
    return (
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-20 h-20 bg-blue-900/40 text-blue-400 border border-blue-700/50 rounded-3xl flex items-center justify-center mb-6 shadow-2xl">
          <ShoppingBag className="w-10 h-10" />
        </div>
        <h1 className="text-2xl font-black text-white tracking-tight">No Active Product Handoff</h1>
        <p className="text-sm text-slate-400 mt-3 max-w-md leading-relaxed">
          Open a product page on <strong>Amazon.in</strong> or <strong>Flipkart.com</strong> and click the floating 
          <span className="text-blue-400 font-semibold"> "Deep Dashboard ↗"</span> badge to launch real-time multi-platform intelligence.
        </p>
        <button
          onClick={() => window.close()}
          className="mt-8 px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl transition-all shadow-md cursor-pointer"
        >
          Close Dashboard Tab
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col antialiased">
      {/* --------------------------------------------------------------------- */}
      {/* 1. Master Top Navigation Bar with View Switcher                       */}
      {/* --------------------------------------------------------------------- */}
      <header className="border-b border-slate-800/80 bg-slate-900/90 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-9 h-9 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center font-black text-white shadow-lg shadow-blue-900/30">
            AI
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-sm font-black tracking-tight text-white uppercase">
                Shopping Intelligence
              </h1>
              <span className="text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded-full">
                Workspace
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Cross-Platform Arbitrage, Review Authenticity & Fraud Risk Dossier
            </p>
          </div>
        </div>

        {/* Tab Switcher Controls */}
        <nav className="flex items-center gap-1.5 overflow-x-auto pb-1 lg:pb-0">
          {[
            { id: 'overview', label: 'Overview', icon: LayoutDashboard },
            { id: 'reviews', label: 'Review NLP & Clusters', icon: Shield },
            { id: 'aspects', label: 'Aspect Sentiment', icon: MessageSquare },
            { id: 'prices', label: 'Price Matrix', icon: TrendingDown },
            { id: 'scam', label: 'Scam Risk', icon: ShieldCheck },
            { id: 'settings', label: 'Settings', icon: Sliders }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as DashboardTab)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold whitespace-nowrap transition-all flex items-center gap-1.5 cursor-pointer border ${
                  isActive
                    ? 'bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-900/30'
                    : 'bg-slate-950/70 text-slate-400 border-slate-800 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5 self-end lg:self-auto">
          {productPayload?.url && (
            <a
              href={productPayload.url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold rounded-lg border border-slate-700/60 transition-colors"
            >
              <span>Original Listing</span>
              <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
            </a>
          )}
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white text-xs font-bold rounded-lg shadow-sm transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Analyzing...' : 'Re-Analyze'}</span>
          </button>
        </div>
      </header>

      {/* --------------------------------------------------------------------- */}
      {/* 2. Main Workspace Layout                                              */}
      {/* --------------------------------------------------------------------- */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Error Alert */}
        {error && (
          <div className="bg-amber-950/40 border border-amber-600/50 rounded-2xl p-4 text-xs text-amber-200 flex items-start gap-3 shadow-lg">
            <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <strong className="font-bold text-amber-300">Service Communication Warning:</strong> {error}
            </div>
          </div>
        )}

        {/* Product Identity Master Banner */}
        {productPayload && (
          <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />

            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
              <div className="space-y-2 max-w-3xl">
                <div className="flex items-center gap-2.5 flex-wrap">
                  <span className="px-2.5 py-0.5 text-[10px] font-black rounded-md uppercase tracking-wider bg-blue-950 text-blue-400 border border-blue-800/60">
                    {productPayload.platform.replace('_', ' ')}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">
                    SKU: {productPayload.sku}
                  </span>
                  {productPayload.seller_name && (
                    <span className="text-xs text-slate-300 bg-slate-800/60 px-2 py-0.5 rounded border border-slate-700/50">
                      Merchant: <strong className="text-white">{productPayload.seller_name}</strong>
                    </span>
                  )}
                  {productPayload.is_fulfilled_by_platform && (
                    <span className="text-[11px] font-semibold text-emerald-400 bg-emerald-950/40 border border-emerald-800/50 px-2 py-0.5 rounded flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3 text-emerald-400" /> Platform Fulfilled
                    </span>
                  )}
                  {productPayload.return_policy && (
                    <span className="text-[11px] font-medium text-slate-300 bg-slate-800 px-2 py-0.5 rounded">
                      🛡️ {productPayload.return_policy}
                    </span>
                  )}
                </div>
                <h2 className="text-base lg:text-lg font-bold text-white tracking-tight leading-snug">
                  {productPayload.title}
                </h2>
              </div>

              {/* Price & Timestamp Block */}
              <div className="lg:text-right shrink-0">
                {productPayload.listed_price ? (
                  <div className="text-2xl lg:text-3xl font-black text-white tracking-tight">
                    ₹{productPayload.listed_price.toLocaleString('en-IN')}
                  </div>
                ) : (
                  <div className="text-sm font-semibold text-slate-400">Price Pending</div>
                )}
                <div className="text-[11px] text-slate-400 mt-1">
                  Last Checked: {intelligence?.generated_at || 'Just now'}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Executive KPI Summary Strip (Always visible for glanceable context) */}
        {intelligence && (
          <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3.5">
            {/* KPI 1 */}
            <div
              onClick={() => setActiveTab('reviews')}
              className="bg-slate-900/80 hover:bg-slate-900 border border-slate-800/90 rounded-2xl p-4 space-y-1.5 shadow-md cursor-pointer transition-colors"
            >
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
                <span>Trust Index</span>
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-black text-white">{intelligence.credibility.trust_score}</span>
                <span className="text-xs text-slate-500">/ 100</span>
              </div>
              <div className="text-[11px] font-bold text-emerald-400 uppercase tracking-wide">
                {intelligence.credibility.anomaly_level} Anomaly Risk
              </div>
            </div>

            {/* KPI 2 */}
            <div
              onClick={() => setActiveTab('reviews')}
              className="bg-slate-900/80 hover:bg-slate-900 border border-slate-800/90 rounded-2xl p-4 space-y-1.5 shadow-md cursor-pointer transition-colors"
            >
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
                <span>Authenticity</span>
                <Sparkles className="w-4 h-4 text-blue-400" />
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-black text-emerald-400">
                  ~{intelligence.credibility.estimated_genuine_pct?.toFixed(0)}%
                </span>
                <span className="text-xs text-slate-400">Genuine</span>
              </div>
              <div className="text-[11px] text-slate-400">
                ~{intelligence.credibility.estimated_fake_pct?.toFixed(0)}% Bot / Suspicious
              </div>
            </div>

            {/* KPI 3 */}
            <div
              onClick={() => setActiveTab('scam')}
              className="bg-slate-900/80 hover:bg-slate-900 border border-slate-800/90 rounded-2xl p-4 space-y-1.5 shadow-md cursor-pointer transition-colors"
            >
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
                <span>Scam Risk</span>
                {intelligence.scam_risk?.risk_level === 'LOW' ? (
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                ) : (
                  <AlertOctagon className="w-4 h-4 text-amber-400" />
                )}
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-black text-white">{intelligence.scam_risk?.risk_score}%</span>
                <span className={`text-xs font-bold ${
                  intelligence.scam_risk?.risk_level === 'LOW' ? 'text-emerald-400' : 'text-amber-400'
                }`}>
                  {intelligence.scam_risk?.risk_level}
                </span>
              </div>
              <div className="text-[11px] text-slate-400 truncate">
                {intelligence.scam_risk?.verdict_title}
              </div>
            </div>

            {/* KPI 4 */}
            <div
              onClick={() => setActiveTab('prices')}
              className="bg-slate-900/80 hover:bg-slate-900 border border-slate-800/90 rounded-2xl p-4 space-y-1.5 shadow-md cursor-pointer transition-colors"
            >
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
                <span>Price Arbitrage</span>
                <TrendingDown className="w-4 h-4 text-blue-400" />
              </div>
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-black text-white">
                  ₹{intelligence.arbitrage.potential_savings ? intelligence.arbitrage.potential_savings.toLocaleString('en-IN') : '0'}
                </span>
              </div>
              <div className="text-[11px] text-slate-400">
                {intelligence.arbitrage.cheapest_platform ? `Best on ${intelligence.arbitrage.cheapest_platform}` : '1 Platform Analyzed'}
              </div>
            </div>

            {/* KPI 5 */}
            <div
              onClick={() => setActiveTab('prices')}
              className="bg-slate-900/80 hover:bg-slate-900 border border-slate-800/90 rounded-2xl p-4 space-y-1.5 shadow-md cursor-pointer transition-colors"
            >
              <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
                <span>Purchase Timing</span>
                <Calendar className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-sm font-black text-white uppercase tracking-wide truncate">
                {intelligence.history?.recommendation.replace(/_/g, ' ') || 'FAIR PRICE'}
              </div>
              <div className="text-[11px] text-slate-400 truncate">
                30-Day Low: ₹{intelligence.history?.lowest_recorded?.toLocaleString('en-IN') || 'N/A'}
              </div>
            </div>
          </section>
        )}

        {/* ------------------------------------------------------------------- */}
        {/* 3. Tab-Routed High-Density Analytical Views                         */}
        {/* ------------------------------------------------------------------- */}
        {intelligence && (
          <>
            {/* View: Overview (Decision Assistant & Core Synthesis) */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <DecisionAssistant intelligence={intelligence} />
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <ReviewClusterExplorer credibility={intelligence.credibility} />
                  <ScamRiskDossier scamRisk={intelligence.scam_risk} />
                </div>
                <PriceMatrixTable
                  prices={intelligence.prices}
                  arbitrage={intelligence.arbitrage}
                  history={intelligence.history}
                />
              </div>
            )}

            {/* View: Review NLP & Linguistic Clusters */}
            {activeTab === 'reviews' && (
              <div className="space-y-6">
                <ReviewClusterExplorer credibility={intelligence.credibility} />
                <AspectExplorer aspects={intelligence.credibility.aspects} />
              </div>
            )}

            {/* View: Aspect Sentiment Explorer */}
            {activeTab === 'aspects' && (
              <div className="space-y-6">
                <AspectExplorer aspects={intelligence.credibility.aspects} />
              </div>
            )}

            {/* View: Cross-Platform Price Matrix */}
            {activeTab === 'prices' && (
              <div className="space-y-6">
                <PriceMatrixTable
                  prices={intelligence.prices}
                  arbitrage={intelligence.arbitrage}
                  history={intelligence.history}
                />
              </div>
            )}

            {/* View: Scam & Fraud Risk Dossier */}
            {activeTab === 'scam' && (
              <div className="space-y-6">
                <ScamRiskDossier scamRisk={intelligence.scam_risk} />
              </div>
            )}

            {/* View: Settings & Transparency */}
            {activeTab === 'settings' && (
              <div className="space-y-6">
                <SettingsAndTransparency />
              </div>
            )}
          </>
        )}
      </main>

      {/* --------------------------------------------------------------------- */}
      {/* 4. Footer & Compliance Disclaimer                                     */}
      {/* --------------------------------------------------------------------- */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 py-6 px-6 mt-12 text-center text-xs text-slate-500 space-y-2">
        <p>
          AI Shopping Intelligence Platform • Chrome Manifest V3 Production Architecture • Powered by Local NLP & Heuristic Engines
        </p>
        <p className="max-w-2xl mx-auto text-[11px] text-slate-600">
          Disclaimer: Analysis results represent algorithmic credibility scores and statistical estimates, not definitive legal claims. Prices reflect live on-page observations and verified public catalog matches. DPDP Act compliance: Personal buyer identifiers are strictly stripped.
        </p>
      </footer>
    </div>
  );
}
