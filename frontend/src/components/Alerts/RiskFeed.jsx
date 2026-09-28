import React, { useState, useEffect } from "react";
import {
  AlertOctagon,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  FileText,
  Sparkles,
  Layers,
  ArrowRight,
  ExternalLink,
  Flame,
  Droplets,
  HelpCircle,
  Clock
} from "lucide-react";
import {
  fetchHazardFeed,
  fetchExplainableOffsetRisks,
  assessSpudLocation
} from "../../utils/api";
import CitationCard from "../Chat/CitationCard";

export default function RiskFeed({ spudLocation, radiusKm, offsetWells, onSelectWell }) {
  const [activeTab, setActiveTab] = useState("evidence"); // "evidence" or "historical"
  const [evidenceReport, setEvidenceReport] = useState(null);
  const [historicalHazards, setHistoricalHazards] = useState([]);
  const [expandedAlerts, setExpandedAlerts] = useState({});
  const [loading, setLoading] = useState(false);
  const [severityFilter, setSeverityFilter] = useState("");

  useEffect(() => {
    if (spudLocation?.lat && spudLocation?.lon) {
      loadEvidenceReport();
    }
  }, [spudLocation, radiusKm]);

  useEffect(() => {
    loadHistoricalFeed();
  }, [severityFilter]);

  const loadEvidenceReport = async () => {
    setLoading(true);
    try {
      const report = await fetchExplainableOffsetRisks(
        spudLocation.lat,
        spudLocation.lon,
        3700.0,
        radiusKm
      );
      setEvidenceReport(report);
      // Auto-expand all alerts by default
      if (report?.alerts) {
        const exp = {};
        report.alerts.forEach((a) => {
          exp[a.id] = true;
        });
        setExpandedAlerts(exp);
      }
    } catch (err) {
      console.error("Failed to load evidence report:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadHistoricalFeed = async () => {
    try {
      const data = await fetchHazardFeed(severityFilter);
      setHistoricalHazards(data);
    } catch (err) {
      console.error("Failed to load historical hazards:", err);
    }
  };

  const toggleAlertExpand = (id) => {
    setExpandedAlerts((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const getSeverityBadge = (severity) => {
    switch (severity?.toUpperCase()) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/40 ring-1 ring-red-500/30";
      case "HIGH":
        return "bg-orange-500/20 text-orange-400 border-orange-500/40";
      case "MEDIUM":
        return "bg-amber-500/20 text-amber-400 border-amber-500/40";
      default:
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
    }
  };

  const alerts = evidenceReport?.alerts || [];

  return (
    <div className="bg-slate-900 border border-slate-700/80 rounded-xl p-3.5 shadow-xl flex flex-col flex-1">
      {/* Header and Sub-Tab Switcher */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5 mb-3">
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
            <AlertOctagon className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-100">
                Live Evidence-Backed Risk Alerts
              </h2>
              {evidenceReport?.overall_risk_tier && (
                <span
                  className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded border uppercase font-mono ${getSeverityBadge(
                    evidenceReport.overall_risk_tier
                  )}`}
                >
                  {evidenceReport.overall_risk_tier} RISK
                </span>
              )}
            </div>
            <p className="text-[10px] text-slate-400 font-mono">
              Audit-ready explainable evidence chain & mitigation recommendations
            </p>
          </div>
        </div>

        {/* View switcher */}
        <div className="flex items-center space-x-1 bg-slate-950 p-0.5 rounded-lg border border-slate-800 text-[10px]">
          <button
            onClick={() => setActiveTab("evidence")}
            className={`px-2 py-0.5 rounded font-bold transition ${
              activeTab === "evidence"
                ? "bg-slate-800 text-amber-400 shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Evidence Chain ({alerts.length})
          </button>
          <button
            onClick={() => setActiveTab("historical")}
            className={`px-2 py-0.5 rounded font-bold transition ${
              activeTab === "historical"
                ? "bg-slate-800 text-slate-200 shadow-sm"
                : "text-slate-400 hover:text-white"
            }`}
          >
            Field Feed ({historicalHazards.length})
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1 max-h-[420px]">
        {activeTab === "evidence" ? (
          <>
            {alerts.map((alert) => {
              const isExpanded = expandedAlerts[alert.id] !== false;
              const prob = alert.probability_pct ?? 80;
              const conf = Math.round((alert.confidence_score || 0.9) * 100);

              return (
                <div
                  key={alert.id}
                  className="bg-slate-950/90 border border-slate-700/80 rounded-xl overflow-hidden shadow-md transition-all hover:border-slate-600"
                >
                  {/* Alert Header Banner */}
                  <div
                    onClick={() => toggleAlertExpand(alert.id)}
                    className="p-3 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border-b border-slate-800/80 flex items-center justify-between cursor-pointer select-none"
                  >
                    <div className="flex items-center space-x-2.5">
                      <span
                        className={`w-2.5 h-2.5 rounded-full ${
                          alert.severity === "CRITICAL"
                            ? "bg-red-500 animate-ping"
                            : "bg-orange-500"
                        }`}
                      />
                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="text-xs font-bold text-white tracking-wide">
                            {alert.risk_type}
                          </h3>
                          <span
                            className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded border uppercase font-mono ${getSeverityBadge(
                              alert.severity
                            )}`}
                          >
                            {alert.severity} [{prob}%]
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono mt-0.5">
                          Hybrid ML Risk Score: {prob}% • Confidence: {conf}%
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      className="text-slate-400 hover:text-slate-200 p-1"
                      aria-label={isExpanded ? "Collapse alert card" : "Expand alert card"}
                    >
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>
                  </div>

                  {/* Expanded Alert Body */}
                  {isExpanded && (
                    <div className="p-3 space-y-3 text-xs bg-slate-950/60">
                      
                      {/* Section 1: The "Why?" Evidence Chain */}
                      <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-2.5">
                        <div className="flex items-center space-x-1.5 text-amber-400 font-bold text-[11px] uppercase tracking-wider mb-2">
                          <HelpCircle className="w-3.5 h-3.5" />
                          <span>The "Why?" Evidence Chain</span>
                        </div>

                        <div className="space-y-2">
                          {(alert.why_evidence_chain || []).map((ev, i) => (
                            <div
                              key={i}
                              className="bg-slate-950/80 border border-slate-800 rounded p-2 text-[11px] text-slate-300"
                            >
                              <div className="flex items-center justify-between text-slate-200 font-semibold mb-1">
                                <span className="text-amber-400 flex items-center gap-1">
                                  <span>Offset Well: {ev.offset_well_name}</span>
                                  <span className="text-[10px] text-slate-500 font-mono">({ev.offset_well_uwi})</span>
                                </span>
                                <span className="font-mono text-emerald-400 text-[10px]">
                                  {ev.distance_km} km away
                                </span>
                              </div>

                              <div className="grid grid-cols-2 gap-1 text-[10px] text-slate-400 font-mono mb-1.5">
                                <div>Depth: <span className="text-slate-200">{ev.depth_md}m MD</span></div>
                                <div>Formation: <span className="text-slate-200">{ev.formation_name}</span></div>
                                <div>Historical Event: <span className="text-red-400 font-semibold">{ev.historical_event}</span></div>
                                {ev.npt_hours > 0 && (
                                  <div>NPT Impact: <span className="text-amber-400 font-semibold">{ev.npt_hours} hrs</span></div>
                                )}
                              </div>

                              {ev.incident_description && (
                                <p className="text-[10px] text-slate-400 italic bg-slate-900 p-1.5 rounded border border-slate-800/80">
                                  "{ev.incident_description}"
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Section 2: Recommended Mitigation Actions */}
                      <div className="bg-slate-900/90 border border-slate-800 rounded-lg p-2.5">
                        <div className="flex items-center space-x-1.5 text-emerald-400 font-bold text-[11px] uppercase tracking-wider mb-2">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>Recommended Engineering Mitigations</span>
                        </div>

                        <ul className="space-y-1.5">
                          {(alert.recommended_mitigations || []).map((mitigation, i) => (
                            <li
                              key={i}
                              className="flex items-start space-x-2 text-[11px] text-slate-200"
                            >
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                              <span>{mitigation}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Section 3: Exact Document Citations */}
                      {(alert.document_citations || []).length > 0 && (
                        <div className="space-y-1.5">
                          <div className="flex items-center space-x-1.5 text-sky-400 font-bold text-[11px] uppercase tracking-wider">
                            <FileText className="w-3.5 h-3.5" />
                            <span>Document Evidence Citations (ChromaDB)</span>
                          </div>

                          <div className="space-y-1.5">
                            {alert.document_citations.map((citation, citIdx) => (
                              <CitationCard key={citIdx} citation={citation} index={citIdx} />
                            ))}
                          </div>
                        </div>
                      )}

                    </div>
                  )}
                </div>
              );
            })}

            {alerts.length === 0 && !loading && (
              <div className="p-8 text-center text-slate-500 text-xs flex flex-col items-center justify-center space-y-1">
                <ShieldCheck className="w-8 h-8 text-emerald-500/60 mb-1" />
                <span className="font-bold text-slate-300">Clean Offset Corridor</span>
                <span className="text-[11px] text-slate-500">
                  No critical drilling hazards logged within {radiusKm} km of this target spud location.
                </span>
              </div>
            )}
          </>
        ) : (
          /* Historical Field Feed */
          <div className="space-y-2">
            {/* Filter buttons */}
            <div className="flex items-center space-x-1 text-[10px] pb-1">
              <span className="text-slate-500 uppercase font-semibold">Filter:</span>
              {["", "CRITICAL", "HIGH", "MEDIUM"].map((sev) => (
                <button
                  key={sev}
                  onClick={() => setSeverityFilter(sev)}
                  className={`px-2 py-0.5 rounded transition ${
                    severityFilter === sev
                      ? "bg-slate-800 text-amber-400 font-bold border border-slate-700"
                      : "text-slate-400 hover:text-white"
                  }`}
                >
                  {sev || "All"}
                </button>
              ))}
            </div>

            {historicalHazards.map((h) => (
              <div
                key={h.id}
                className="bg-slate-950/80 border border-slate-800 rounded-lg p-2.5 text-xs hover:border-slate-700 transition"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-white">{h.well_name}</span>
                    <span className="text-[10px] text-slate-400 font-mono">{h.uwi}</span>
                  </div>
                  <span
                    className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded border uppercase font-mono ${getSeverityBadge(
                      h.severity
                    )}`}
                  >
                    {h.severity}
                  </span>
                </div>

                <div className="text-[11px] text-slate-300 font-medium mb-1">
                  {h.event_type} at {h.depth_md}m MD ({h.formation_name || "Tipam"})
                </div>

                <p className="text-[10px] text-slate-400 italic mb-1.5">
                  "{h.description}"
                </p>

                {h.remediation_action && (
                  <div className="text-[10px] text-emerald-400/90 font-mono bg-slate-900 p-1.5 rounded border border-slate-800">
                    Fix: {h.remediation_action}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
