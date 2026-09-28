import React, { useState, useEffect } from "react";
import { AlertOctagon, AlertTriangle, ShieldCheck, Gauge, CheckCircle2, ChevronRight, SlidersHorizontal, Flame } from "lucide-react";
import { fetchHazardFeed, assessSpudLocation } from "../../utils/api";

export default function RiskFeed({ spudLocation, radiusKm, offsetWells, onSelectWell }) {
  const [hazards, setHazards] = useState([]);
  const [severityFilter, setSeverityFilter] = useState("");
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHazards();
  }, [severityFilter]);

  useEffect(() => {
    if (spudLocation?.lat && spudLocation?.lon) {
      loadAssessment();
    }
  }, [spudLocation, radiusKm]);

  const loadHazards = async () => {
    try {
      const data = await fetchHazardFeed(severityFilter);
      setHazards(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadAssessment = async () => {
    setLoading(true);
    try {
      const assessment = await assessSpudLocation(
        spudLocation.lat,
        spudLocation.lon,
        3700.0, // Default planned TVD
        radiusKm
      );
      setRiskAssessment(assessment);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/40 ring-1 ring-red-500/20";
      case "HIGH":
        return "bg-orange-500/20 text-orange-400 border-orange-500/30";
      case "MEDIUM":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      default:
        return "bg-slate-700 text-slate-300 border-slate-600";
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-oil-border rounded-xl shadow-xl overflow-hidden">
      
      {/* Header */}
      <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center justify-center text-red-400">
            <AlertOctagon className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Offset Drilling Hazards & Risk Advisor
            </h3>
            <p className="text-[11px] text-slate-400">
              Live offset kicks, losses, and safe mud weight envelope
            </p>
          </div>
        </div>

        {riskAssessment && (
          <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded border ${
            riskAssessment.overall_risk_score === "CRITICAL"
              ? "bg-red-500/20 text-red-400 border-red-500/40 animate-pulse"
              : riskAssessment.overall_risk_score === "ELEVATED"
              ? "bg-orange-500/20 text-orange-400 border-orange-500/30"
              : "bg-amber-500/20 text-amber-400 border-amber-500/30"
          }`}>
            Risk: {riskAssessment.overall_risk_score}
          </span>
        )}
      </div>

      <div className="p-4 space-y-4 overflow-y-auto flex-1">
        
        {/* Recommended Mud Weight Window Banner */}
        {riskAssessment && (
          <div className="bg-gradient-to-br from-slate-950 to-slate-900 border border-amber-500/30 rounded-xl p-3.5 space-y-3 shadow-lg">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-amber-400 flex items-center gap-1.5 uppercase tracking-wider">
                <Gauge className="w-4 h-4 text-amber-400" />
                <span>Recommended Mud Weight Window</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono">
                {radiusKm}km offset radius
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center">
              <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-400 font-medium">Min Kick Margin</div>
                <div className="text-base font-bold text-emerald-400 mt-0.5">
                  {riskAssessment.mud_weight_recommended_ppg.min_ppg} ppg
                </div>
              </div>
              <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-400 font-medium">Max Loss Fracture</div>
                <div className="text-base font-bold text-red-400 mt-0.5">
                  {riskAssessment.mud_weight_recommended_ppg.max_ppg} ppg
                </div>
              </div>
              <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
                <div className="text-[10px] text-slate-400 font-medium">Surge Allowance</div>
                <div className="text-base font-bold text-amber-400 mt-0.5">
                  ±{riskAssessment.mud_weight_recommended_ppg.surge_margin_ppg} ppg
                </div>
              </div>
            </div>

            {/* Key Precautions Checklist */}
            <div className="space-y-1.5 pt-1">
              <div className="text-[11px] font-semibold text-slate-300">Operational Precautions:</div>
              {riskAssessment.drilling_recommendations.slice(0, 2).map((rec, i) => (
                <div key={i} className="flex items-start space-x-1.5 text-[11px] text-slate-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Severity Filters */}
        <div className="flex items-center justify-between pt-1">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
            <SlidersHorizontal className="w-3 h-3 text-slate-400" />
            <span>Hazard Log Feed</span>
          </span>
          <div className="flex space-x-1">
            {["", "CRITICAL", "HIGH", "MEDIUM"].map((s) => (
              <button
                key={s}
                onClick={() => setSeverityFilter(s)}
                className={`px-2 py-0.5 rounded text-[10px] font-bold transition ${
                  severityFilter === s
                    ? "bg-slate-700 text-white"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {s || "ALL"}
              </button>
            ))}
          </div>
        </div>

        {/* Hazard Incident Cards */}
        <div className="space-y-2.5">
          {hazards.map((h) => (
            <div
              key={h.id}
              className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition space-y-2"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded border ${getSeverityBadge(h.severity)}`}>
                    {h.severity}
                  </span>
                  <span className="text-xs font-bold text-slate-200">{h.event_type}</span>
                </div>
                <div className="text-[11px] font-mono text-amber-400 font-semibold">
                  {h.well_name}
                </div>
              </div>

              <div className="flex items-center space-x-3 text-[11px] text-slate-400">
                <span>Depth: <strong className="text-slate-200">{h.depth_md} m</strong></span>
                {h.formation_name && <span>Fm: <strong className="text-slate-200">{h.formation_name}</strong></span>}
                {h.mud_weight_ppg && <span>MW: <strong className="text-sky-400">{h.mud_weight_ppg} ppg</strong></span>}
              </div>

              <p className="text-xs text-slate-300 leading-snug">
                {h.description}
              </p>

              {h.remediation_action && (
                <div className="p-2 rounded bg-slate-900 border border-slate-800 text-[11px] text-emerald-400">
                  <strong className="text-slate-300">Remediation:</strong> {h.remediation_action}
                </div>
              )}
            </div>
          ))}
        </div>

      </div>

    </div>
  );
}
