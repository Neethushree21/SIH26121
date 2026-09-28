import React, { useState } from "react";
import { FileText, ChevronDown, ChevronUp, ExternalLink, Bookmark, CheckCircle2 } from "lucide-react";

export default function CitationCard({ citation, index }) {
  const [expanded, setExpanded] = useState(false);

  if (!citation) return null;

  const scorePct = Math.round((citation.score || 0.85) * 100);
  const docName = citation.document_name || citation.source_file || "Drilling Report";
  const isPdf = docName.toLowerCase().endsWith(".pdf");

  return (
    <div className="bg-slate-900/90 border border-slate-700/70 hover:border-amber-500/50 rounded-lg p-2.5 transition-all text-xs shadow-sm">
      {/* Citation Header */}
      <div 
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between cursor-pointer select-none gap-2"
      >
        <div className="flex items-center space-x-2 min-w-0">
          <div className="w-6 h-6 rounded bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
            <FileText className="w-3.5 h-3.5" />
          </div>
          <div className="truncate">
            <div className="font-semibold text-slate-200 truncate flex items-center gap-1.5">
              <span className="truncate">{docName}</span>
              {isPdf && (
                <span className="text-[9px] px-1 py-0.2 rounded bg-red-500/20 text-red-400 font-mono font-bold shrink-0">
                  PDF
                </span>
              )}
            </div>
            <div className="text-[10px] text-slate-400 flex items-center space-x-2 font-mono">
              <span>p. {citation.page_number || 1}</span>
              {citation.well_name && (
                <>
                  <span>•</span>
                  <span className="text-amber-400/90">{citation.well_name}</span>
                </>
              )}
              {citation.formation && citation.formation !== "N/A" && (
                <>
                  <span>•</span>
                  <span className="text-slate-300">{citation.formation}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-1.5 shrink-0">
          <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${
            scorePct >= 80 
              ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" 
              : "bg-slate-800 text-slate-300 border-slate-700"
          }`}>
            {scorePct}% match
          </span>
          <button 
            type="button" 
            className="text-slate-400 hover:text-slate-200 p-0.5"
            aria-label={expanded ? "Collapse citation snippet" : "Expand citation snippet"}
          >
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Expandable Snippet Excerpt */}
      {expanded && (
        <div className="mt-2 pt-2 border-t border-slate-800/80 text-[11px] text-slate-300 leading-relaxed font-sans bg-slate-950/60 p-2 rounded border border-slate-800">
          <div className="text-[10px] font-mono text-amber-400 uppercase tracking-wider mb-1 flex items-center gap-1">
            <Bookmark className="w-3 h-3" />
            <span>Extracted Report Excerpt:</span>
          </div>
          <p className="italic text-slate-200 whitespace-pre-wrap">
            "{citation.snippet}"
          </p>
          {citation.depth_interval && citation.depth_interval !== "N/A" && (
            <div className="mt-1 text-[10px] font-mono text-slate-400">
              Depth Interval: {citation.depth_interval}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
