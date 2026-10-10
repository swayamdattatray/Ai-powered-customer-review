import React, { useState } from 'react';
import {
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  Search,
  ChevronRight,
  Quote,
  Filter
} from 'lucide-react';
import { AspectSentiment } from '../../types/contracts';

interface AspectExplorerProps {
  aspects: AspectSentiment[];
}

export default function AspectExplorer({ aspects }: AspectExplorerProps) {
  const [selectedAspectName, setSelectedAspectName] = useState<string>(aspects[0]?.aspect || '');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const currentAspect = aspects.find((a) => a.aspect === selectedAspectName) || aspects[0];

  // Frequently praised features (score >= 3.6)
  const praisedAspects = aspects.filter((a) => a.score >= 3.6);
  // Frequently criticized problems (score <= 3.0)
  const criticizedAspects = aspects.filter((a) => a.score <= 3.0);

  // Filter quotes based on search term
  const filteredQuotes = currentAspect
    ? currentAspect.grounded_snippets.filter((q) =>
        q.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : [];

  return (
    <section className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center">
            <MessageSquare className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Aspect-Based Customer Sentiment & Citations Explorer
            </h3>
            <p className="text-xs text-slate-400">
              Grounded feedback analysis across hardware dimensions with authentic review citations
            </p>
          </div>
        </div>

        <div className="text-xs text-slate-400">
          Tracking <strong className="text-white font-bold">{aspects.length}</strong> Product Dimensions
        </div>
      </div>

      {/* Frequently Praised vs Frequently Criticized Summary Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Frequently Praised */}
        <div className="bg-emerald-950/20 border border-emerald-800/40 rounded-xl p-4 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-wider">
            <ThumbsUp className="w-4 h-4" />
            <span>Frequently Praised Attributes</span>
          </div>
          {praisedAspects.length > 0 ? (
            <div className="flex flex-wrap gap-2 pt-1">
              {praisedAspects.map((asp, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedAspectName(asp.aspect)}
                  className={`px-3 py-1 text-xs font-semibold rounded-lg border transition-all cursor-pointer ${
                    selectedAspectName === asp.aspect
                      ? 'bg-emerald-600 text-white border-emerald-500 shadow-md'
                      : 'bg-emerald-950/60 text-emerald-300 border-emerald-800/60 hover:bg-emerald-900/40'
                  }`}
                >
                  {asp.aspect} ({asp.score}/5.0)
                </button>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No single aspect exceeds 3.6/5.0 satisfaction threshold.</p>
          )}
        </div>

        {/* Frequently Criticized */}
        <div className="bg-rose-950/20 border border-rose-800/40 rounded-xl p-4 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-rose-400 uppercase tracking-wider">
            <ThumbsDown className="w-4 h-4" />
            <span>Frequently Reported Complaints</span>
          </div>
          {criticizedAspects.length > 0 ? (
            <div className="flex flex-wrap gap-2 pt-1">
              {criticizedAspects.map((asp, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedAspectName(asp.aspect)}
                  className={`px-3 py-1 text-xs font-semibold rounded-lg border transition-all cursor-pointer ${
                    selectedAspectName === asp.aspect
                      ? 'bg-rose-600 text-white border-rose-500 shadow-md'
                      : 'bg-rose-950/60 text-rose-300 border-rose-800/60 hover:bg-rose-900/40'
                  }`}
                >
                  {asp.aspect} ({asp.score}/5.0)
                </button>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 italic">No recurring critical complaints detected in review sample.</p>
          )}
        </div>
      </div>

      {/* Aspect Dimension Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-800/80">
        {aspects.map((asp, idx) => {
          const isSelected = asp.aspect === selectedAspectName;
          const scoreColor =
            asp.score >= 3.6 ? 'text-emerald-400' : asp.score <= 2.8 ? 'text-rose-400' : 'text-slate-300';

          return (
            <button
              key={idx}
              onClick={() => setSelectedAspectName(asp.aspect)}
              className={`px-3.5 py-2 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-2 cursor-pointer border ${
                isSelected
                  ? 'bg-blue-600 text-white border-blue-500 shadow-lg shadow-blue-900/30'
                  : 'bg-slate-950/70 text-slate-400 border-slate-800 hover:text-white hover:bg-slate-800'
              }`}
            >
              <span>{asp.aspect}</span>
              <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono font-black ${isSelected ? 'bg-blue-800 text-white' : scoreColor}`}>
                {asp.score}
              </span>
            </button>
          );
        })}
      </div>

      {/* Selected Aspect Detail Panel */}
      {currentAspect && (
        <div className="bg-slate-950/80 border border-slate-800/90 rounded-2xl p-5 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
            <div>
              <div className="flex items-center gap-2.5">
                <h4 className="text-base font-black text-white tracking-tight">
                  {currentAspect.aspect} Satisfaction Breakdown
                </h4>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                  currentAspect.score >= 3.6
                    ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                    : currentAspect.score <= 2.8
                    ? 'bg-rose-950 text-rose-400 border border-rose-800'
                    : 'bg-slate-800 text-slate-300 border border-slate-700'
                }`}>
                  {currentAspect.sentiment} ({currentAspect.score}/5.0)
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Referenced across {currentAspect.mentions} customer reviews in the analyzed sample
              </p>
            </div>

            {/* Quote Search Filter */}
            <div className="relative w-full sm:w-64">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search quotes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-700 text-xs text-white rounded-lg placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Sentiment Proportion Bar */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="text-emerald-400">
                Positive Sentiment: {Math.round(currentAspect.positive_ratio * 100)}%
              </span>
              <span className="text-rose-400">
                Negative Sentiment: {Math.round(currentAspect.negative_ratio * 100)}%
              </span>
            </div>
            <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden flex border border-slate-700/50">
              <div
                className="h-full bg-emerald-500 transition-all duration-500 rounded-l-full"
                style={{ width: `${Math.round(currentAspect.positive_ratio * 100)}%` }}
              />
              <div
                className="h-full bg-rose-500 transition-all duration-500 rounded-r-full"
                style={{ width: `${Math.round(currentAspect.negative_ratio * 100)}%` }}
              />
            </div>
          </div>

          {/* Grounded Verbatim Citations Grid */}
          <div className="space-y-3 pt-2">
            <div className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Quote className="w-4 h-4 text-blue-400" />
              <span>Grounded Customer Review Citations ({filteredQuotes.length})</span>
            </div>

            {filteredQuotes.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {filteredQuotes.map((snippet, sIdx) => (
                  <div
                    key={sIdx}
                    className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3.5 text-xs text-slate-300 leading-relaxed italic border-l-3 border-l-blue-500 relative shadow-sm"
                  >
                    "{snippet}"
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-slate-900 p-4 rounded-xl text-center text-xs text-slate-400">
                {searchTerm ? 'No citations matching your search term.' : 'No direct text snippets captured for this attribute.'}
              </div>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
