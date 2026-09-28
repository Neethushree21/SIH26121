import React, { useState, useEffect } from "react";
import {
  AlertOctagon,
  AlertTriangle,
  ShieldCheck,
  Gauge,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Activity,
  FileText,
  Play,
  Pause,
  RotateCcw,
  Sparkles,
  Layers,
  ArrowRight,
  ExternalLink
} from "lucide-react";
import {
  fetchHazardFeed,
  assessSpudLocation,
  fetchExplainableOffsetRisks,
  fetchTelemetryTick,
  resetTelemetrySimulation
} from "../../utils/api";

export default function RiskFeed({ spudLocation, radiusKm, offsetWells, onSelectWell }) {
  const [activeTab, setActiveTab] = useState("evidence"); // "evidence", "telemetry", "feed"
  
  // Historical feed & basic assessment
  const [hazards, setHazards] = useState([]);
  const [severityFilter, setSeverityFilter] = useState("");
  const [riskAssessment, setRiskAssessment] = useState(null);

  // Phase 3: Explainable Evidence-Chain
  const [evidenceReport, setEvidenceReport] = useState(null);
  const [expandedAlerts, setExpandedAlerts] = useState({});

  // Phase 3: Live eRTMAC Telemetry
  const [telemetryState, setTelemetryState] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    loadHazards();
  }, [severityFilter]);

  useEffect(() => {
    if (spudLocation?.lat && spudLocation?.lon) {
      loadAssessment();
      loadEvidenceReport();
    }
  }, [spudLocation, radiusKm]);

  // Telemetry polling loop when streaming is active
  useEffect(() => {
    let timer = null;
    if (isStreaming) {
      timer = setInterval(async () => {
        try {
          const tickRes = await fetchTelemetryTick();
          setTelemetryState(tickRes);
        } catch (err) {
          console.error("Telemetry tick error:", err);
        }
      }, 1500);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isStreaming]);

  const loadHazards = async () => {
    try {
      const data = await fetchHazardFeed(severityFilter);
      setHazards(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadAssessment = async () => {
    try {
      const assessment = await assessSpudLocation(
        spudLocation.lat,
        spudLocation.lon,
        3700.0,
        radiusKm
      );
      setRiskAssessment(assessment);
    } catch (err) {
      console.error(err);
    }
  };

  const loadEvidenceReport = async () => {
    try {
      const report = await fetchExplainableOffsetRisks(
        spudLocation.lat,
        spudLocation.lon,
        3700.0,
        radiusKm
      );
      setEvidenceReport(report);
      // Auto-expand first alert
      if (report.alerts && report.alerts.length > 0) {
        setExpandedAlerts({ [report.alerts[0].id]: true });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleJumpToHazard = async (depth, mw) => {
    try {
      await resetTelemetrySimulation(depth, mw);
      const tickRes = await fetchTelemetryTick();
      setTelemetryState(tickRes);
    } catch (err) {
      console.error(err);
    }
  };

  const toggleAlertExpanded = (alertId) => {
    setExpandedAlerts((prev) => ({ ...prev, [alertId]: !prev[alertId] }));
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-oil-border rounded-xl shadow-xl overflow-hidden">
      
      {/* Top Header */}
      <div className="bg-slate-950 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center justify-center text-red-400">
            <AlertOctagon className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <span>Offset Risk Advisor</span>
              <span className="text-[10px] bg-amber-500/20 text-amber-400 px-1.5 py-0.2 rounded font-mono">
                Hybrid ML
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Explainable Evidence Chains & Real-Time eRTMAC Stream
            </p>
          </div>
        </div>

        {evidenceReport && (
          <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
            evidenceReport.overall_risk_tier === "CRITICAL"
              ? "bg-red-500/20 text-red-400 border-red-500/40 animate-pulse"
              : evidenceReport.overall_risk_tier === "HIGH"
              ? "bg-orange-500/20 text-orange-400 border-orange-500/30"
              : "bg-amber-500/20 text-amber-400 border-amber-500/30"
          }`}>
            Risk: {evidenceReport.overall_risk_tier}
          </span>
        )}
      </div>

      {/* Sub-tab Navigation */}
      <div className="flex bg-slate-950/60 border-b border-slate-800 px-2 text-xs">
        <button
          onClick={() => setActiveTab("evidence")}
          className={`py-2 px-3 font-semibold border-b-2 transition flex items-center gap-1.5 ${
            activeTab === "evidence"
              ? "border-amber-500 text-amber-400 bg-amber-500/5"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Evidence Chain ({evidenceReport?.alerts?.length || 0})</span>
        </button>
        <button
          onClick={() => setActiveTab("telemetry")}
          className={`py-2 px-3 font-semibold border-b-2 transition flex items-center gap-1.5 ${
            activeTab === "telemetry"
              ? "border-amber-500 text-amber-400 bg-amber-500/5"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <Activity className="w-3.5 h-3.5 text-sky-400" />
          <span>eRTMAC Telemetry ML</span>
        </button>
        <button
          onClick={() => setActiveTab("feed")}
          className={`py-2 px-3 font-semibold border-b-2 transition flex items-center gap-1.5 ${
            activeTab === "feed"
              ? "border-amber-500 text-amber-400 bg-amber-500/5"
              : "border-transparent text-slate-400 hover:text-slate-200"
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Hazard Logs ({hazards.length})</span>
        </button>
      </div>

      {/* Tab Contents */}
      <div className="p-4 space-y-4 overflow-y-auto flex-1">
        
        {/* TAB 1: EXPLAINABLE EVIDENCE-CHAIN ALERTS */}
        {activeTab === "evidence" && (
          <div className="space-y-4">
            
            {/* Safe Mud Weight Window Banner */}
            {riskAssessment && (
              <div className="bg-gradient-to-br from-slate-950 to-slate-900 border border-amber-500/30 rounded-xl p-3 space-y-2 shadow-lg">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-bold text-amber-400 flex items-center gap-1 uppercase">
                    <Gauge className="w-3.5 h-3.5" />
                    <span>Safe Mud Weight Envelope</span>
                  </span>
                  <span className="text-slate-400 font-mono">{radiusKm}km radius</span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">Min Kick Margin</div>
                    <div className="text-sm font-bold text-emerald-400">{riskAssessment.mud_weight_recommended_ppg.min_ppg} ppg</div>
                  </div>
                  <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">Max Loss Margin</div>
                    <div className="text-sm font-bold text-red-400">{riskAssessment.mud_weight_recommended_ppg.max_ppg} ppg</div>
                  </div>
                  <div className="bg-slate-900 p-1.5 rounded border border-slate-800">
                    <div className="text-[10px] text-slate-400">Surge Allowance</div>
                    <div className="text-sm font-bold text-amber-400">±{riskAssessment.mud_weight_recommended_ppg.surge_margin_ppg} ppg</div>
                  </div>
                </div>
              </div>
            )}

            {/* Audit-Ready Evidence Cards */}
            <div className="space-y-3">
              {evidenceReport?.alerts && evidenceReport.alerts.map((alert) => {
                const isExpanded = !!expandedAlerts[alert.id];
                return (
                  <div
                    key={alert.id}
                    className="rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 transition overflow-hidden shadow-md"
                  >
                    {/* Alert Card Header */}
                    <div
                      onClick={() => toggleAlertExpanded(alert.id)}
                      className="p-3.5 cursor-pointer flex items-center justify-between bg-slate-950/80 hover:bg-slate-900/60"
                    >
                      <div className="flex items-center space-x-2.5">
                        <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded border ${
                          alert.severity === "CRITICAL"
                            ? "bg-red-500/20 text-red-400 border-red-500/30 ring-1 ring-red-500/20"
                            : "bg-amber-500/20 text-amber-400 border-amber-500/30"
                        }`}>
                          {alert.severity}
                        </span>
                        <div>
                          <div className="text-xs font-bold text-white flex items-center gap-1.5">
                            <span>{alert.risk_type}</span>
                            <span className="text-amber-400 font-mono text-[11px]">
                              [{alert.probability_pct}% ML Prob]
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-400">
                            Confidence: {Math.round(alert.confidence_score * 100)}% • {alert.why_evidence_chain.length} Correlated Offset Wells
                          </div>
                        </div>
                      </div>
                      {isExpanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                    </div>

                    {/* Expandable Evidence Chain & Citations */}
                    {isExpanded && (
                      <div className="p-3.5 pt-1 border-t border-slate-800/80 space-y-3 text-xs">
                        
                        {/* The "Why?" Evidence Chain */}
                        <div className="space-y-1.5">
                          <span className="text-[11px] font-bold text-amber-400 uppercase tracking-wider flex items-center gap-1">
                            <span>The "Why?" Evidence Chain:</span>
                          </span>
                          <div className="space-y-1">
                            {alert.why_evidence_chain.map((item, idx) => (
                              <div
                                key={idx}
                                className="bg-slate-900/90 p-2 rounded-lg border border-slate-800 text-[11px] space-y-1"
                              >
                                <div className="flex items-center justify-between font-semibold">
                                  <span className="text-white flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                    <span>{item.offset_well_name}</span>
                                    <span className="text-slate-500">({item.offset_well_uwi})</span>
                                  </span>
                                  <span className="text-amber-400 font-mono">{item.distance_km} km away</span>
                                </div>
                                <div className="text-slate-400">
                                  Logged <strong>{item.historical_event}</strong> at <strong>{item.depth_md} m</strong> in <em>{item.formation_name}</em> ({item.npt_hours}h NPT).
                                </div>
                                <div className="text-slate-300 italic text-[10px]">
                                  "{item.incident_description}"
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Recommended Mitigations */}
                        <div className="space-y-1.5">
                          <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider">
                            Recommended Mitigation Checklist:
                          </span>
                          <div className="space-y-1">
                            {alert.recommended_mitigations.map((mit, idx) => (
                              <div key={idx} className="flex items-start space-x-1.5 text-[11px] text-slate-300">
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                                <span>{mit}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Exact Document Citations from ChromaDB */}
                        {alert.document_citations && alert.document_citations.length > 0 && (
                          <div className="space-y-1.5 pt-1">
                            <span className="text-[11px] font-bold text-sky-400 uppercase tracking-wider flex items-center gap-1">
                              <FileText className="w-3 h-3" />
                              <span>Exact Technical Citations (ChromaDB):</span>
                            </span>
                            <div className="space-y-1.5">
                              {alert.document_citations.map((c, idx) => (
                                <div
                                  key={idx}
                                  className="bg-slate-900 border border-sky-500/20 p-2 rounded-lg text-[10px] space-y-1"
                                >
                                  <div className="flex items-center justify-between font-mono text-sky-400">
                                    <span>{c.document_name} (Page {c.page_number})</span>
                                    <span className="text-slate-400">{c.depth_interval}</span>
                                  </div>
                                  <p className="text-slate-300 italic">
                                    "{c.snippet}"
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 2: LIVE eRTMAC TELEMETRY STREAM & ML GAUGE */}
        {activeTab === "telemetry" && (
          <div className="space-y-4">
            
            {/* Stream Controller Bar */}
            <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setIsStreaming(!isStreaming)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition ${
                    isStreaming
                      ? "bg-red-500 hover:bg-red-400 text-white animate-pulse"
                      : "bg-emerald-500 hover:bg-emerald-400 text-black shadow-md shadow-emerald-500/20"
                  }`}
                >
                  {isStreaming ? (
                    <>
                      <Pause className="w-3.5 h-3.5" />
                      <span>Pause Stream</span>
                    </>
                  ) : (
                    <>
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Start Live eRTMAC Stream</span>
                    </>
                  )}
                </button>
                <button
                  onClick={async () => {
                    const tickRes = await fetchTelemetryTick();
                    setTelemetryState(tickRes);
                  }}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium transition"
                >
                  Single Tick
                </button>
              </div>

              {telemetryState && (
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  telemetryState.hybrid_risk_tier === "CRITICAL"
                    ? "bg-red-500/20 text-red-400 border-red-500/30"
                    : telemetryState.hybrid_risk_tier === "HIGH"
                    ? "bg-orange-500/20 text-orange-400 border-orange-500/30"
                    : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                }`}>
                  {telemetryState.hybrid_risk_tier} RISK
                </span>
              )}
            </div>

            {/* Quick Test Hazard Zone Jump Buttons */}
            <div className="space-y-1">
              <div className="text-[10px] uppercase font-bold text-slate-400">
                Simulate Drillstring Hazard Encounters:
              </div>
              <div className="grid grid-cols-3 gap-1.5">
                <button
                  onClick={() => handleJumpToHazard(2338.0, 10.4)}
                  className="p-1.5 bg-slate-950 hover:bg-slate-800 text-[10px] text-amber-400 font-semibold rounded border border-slate-800 text-center"
                >
                  Tipam Loss (2,340m)
                </button>
                <button
                  onClick={() => handleJumpToHazard(3418.0, 10.3)}
                  className="p-1.5 bg-slate-950 hover:bg-slate-800 text-[10px] text-red-400 font-semibold rounded border border-slate-800 text-center"
                >
                  Barail Kick (3,420m)
                </button>
                <button
                  onClick={() => handleJumpToHazard(2888.0, 10.6)}
                  className="p-1.5 bg-slate-950 hover:bg-slate-800 text-[10px] text-orange-400 font-semibold rounded border border-slate-800 text-center"
                >
                  Tight Hole (2,890m)
                </button>
              </div>
            </div>

            {/* Telemetry Readouts Grid */}
            {telemetryState ? (
              <div className="space-y-3">
                <div className="grid grid-cols-3 sm:grid-cols-4 gap-2 text-center text-xs">
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-400">Measured Depth</div>
                    <div className="text-sm font-bold text-white font-mono mt-0.5">
                      {telemetryState.telemetry.depth_md} m
                    </div>
                  </div>
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-400">ROP (Rate of Penetration)</div>
                    <div className="text-sm font-bold text-sky-400 font-mono mt-0.5">
                      {telemetryState.telemetry.rop_m_hr} m/hr
                    </div>
                  </div>
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-400">Torque</div>
                    <div className="text-sm font-bold text-amber-400 font-mono mt-0.5">
                      {telemetryState.telemetry.torque_kft_lbs} kft-lbs
                    </div>
                  </div>
                  <div className="bg-slate-950 p-2 rounded-xl border border-slate-800">
                    <div className="text-[10px] text-slate-400">Standpipe Pressure</div>
                    <div className="text-sm font-bold text-white font-mono mt-0.5">
                      {telemetryState.telemetry.standpipe_pressure_psi} psi
                    </div>
                  </div>
                </div>

                {/* Scikit-Learn Hybrid ML Hazard Probabilities */}
                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-2.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-slate-200 flex items-center gap-1.5 uppercase">
                      <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                      <span>Hybrid ML Hazard Probabilities</span>
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      Fm: {telemetryState.telemetry.active_formation}
                    </span>
                  </div>

                  <div className="space-y-2 text-xs">
                    <div>
                      <div className="flex justify-between text-[11px] mb-0.5">
                        <span className="text-red-400 font-semibold">Gas Kick Influx Risk</span>
                        <span className="font-mono text-red-400">
                          {Math.round(telemetryState.ml_hazard_probabilities.gas_kick_prob * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-red-500 h-full transition-all duration-300"
                          style={{ width: `${Math.round(telemetryState.ml_hazard_probabilities.gas_kick_prob * 100)}%` }}
                        ></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-[11px] mb-0.5">
                        <span className="text-amber-400 font-semibold">Lost Circulation Risk</span>
                        <span className="font-mono text-amber-400">
                          {Math.round(telemetryState.ml_hazard_probabilities.loss_circulation_prob * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-amber-500 h-full transition-all duration-300"
                          style={{ width: `${Math.round(telemetryState.ml_hazard_probabilities.loss_circulation_prob * 100)}%` }}
                        ></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-[11px] mb-0.5">
                        <span className="text-orange-400 font-semibold">Stuck Pipe / Pack-Off</span>
                        <span className="font-mono text-orange-400">
                          {Math.round(telemetryState.ml_hazard_probabilities.stuck_pipe_prob * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-orange-500 h-full transition-all duration-300"
                          style={{ width: `${Math.round(telemetryState.ml_hazard_probabilities.stuck_pipe_prob * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  {telemetryState.active_warning && (
                    <div className="mt-2 p-2 rounded bg-red-950/40 border border-red-800/40 text-[11px] text-red-300">
                      <strong>ALERT:</strong> {telemetryState.active_warning}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-slate-500 text-xs">
                Click "Start Live eRTMAC Stream" or "Single Tick" to begin telemetry simulation.
              </div>
            )}

          </div>
        )}

        {/* TAB 3: HISTORICAL HAZARDS FEED */}
        {activeTab === "feed" && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Historical Drilling Incidents
              </span>
              <div className="flex space-x-1">
                {["", "CRITICAL", "HIGH", "MEDIUM"].map((s) => (
                  <button
                    key={s}
                    onClick={() => setSeverityFilter(s)}
                    className={`px-2 py-0.5 rounded text-[10px] font-bold transition ${
                      severityFilter === s ? "bg-slate-700 text-white" : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {s || "ALL"}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2.5">
              {hazards.map((h) => (
                <div
                  key={h.id}
                  className="p-3 rounded-xl bg-slate-950/70 border border-slate-800 space-y-1.5 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded border ${
                        h.severity === "CRITICAL"
                          ? "bg-red-500/20 text-red-400 border-red-500/30"
                          : "bg-amber-500/20 text-amber-400 border-amber-500/30"
                      }`}>
                        {h.severity}
                      </span>
                      <span className="font-bold text-white">{h.event_type}</span>
                    </div>
                    <span className="text-amber-400 font-mono text-[11px]">{h.well_name}</span>
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Depth: {h.depth_md}m • Fm: {h.formation_name || "N/A"} • MW: {h.mud_weight_ppg || 10.4} ppg
                  </div>
                  <p className="text-slate-300 leading-snug">{h.description}</p>
                  {h.remediation_action && (
                    <div className="text-emerald-400 text-[11px]">
                      <strong>Remediation:</strong> {h.remediation_action}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

      </div>

    </div>
  );
}
