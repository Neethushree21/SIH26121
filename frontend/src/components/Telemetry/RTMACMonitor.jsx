import React, { useState, useEffect, useRef } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  AreaChart,
  Area
} from "recharts";
import {
  Activity,
  Play,
  Pause,
  RotateCcw,
  Zap,
  Gauge,
  AlertTriangle,
  Flame,
  Droplets,
  Layers,
  ChevronRight
} from "lucide-react";
import { fetchTelemetryTick, resetTelemetrySimulation } from "../../utils/api";

export default function RTMACMonitor({ onHazardAlert }) {
  const [isStreaming, setIsStreaming] = useState(true);
  const [telemetryState, setTelemetryState] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeMetricTab, setActiveMetricTab] = useState("drilling"); // "drilling" (ROP/Torque) or "hydraulics" (Pressure/Mud)
  const isStreamingRef = useRef(isStreaming);
  isStreamingRef.current = isStreaming;

  // Polling loop for streaming telemetry ticks
  useEffect(() => {
    let intervalId = null;

    const pullTick = async () => {
      try {
        const tickRes = await fetchTelemetryTick();
        setTelemetryState(tickRes);

        const t = tickRes.telemetry;
        if (t) {
          setHistory((prev) => {
            const next = [
              ...prev,
              {
                time: `T+${t.tick_index}`,
                tick: t.tick_index,
                depth_md: t.depth_md,
                rop_m_hr: t.rop_m_hr,
                torque_kft_lbs: t.torque_kft_lbs,
                standpipe_pressure_psi: t.standpipe_pressure_psi,
                mud_weight_in_ppg: t.mud_weight_in_ppg,
                wob_klbs: t.wob_klbs,
                flow_out_pct: t.flow_out_pct
              }
            ];
            // Keep last 25 ticks in time-series
            return next.slice(-25);
          });
        }
      } catch (err) {
        console.error("eRTMAC telemetry pull error:", err);
      }
    };

    // Initial pull
    pullTick();

    // Stream interval
    intervalId = setInterval(() => {
      if (isStreamingRef.current) {
        pullTick();
      }
    }, 1800);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  const handleResetTo = async (depthMd, mudWeight) => {
    try {
      await resetTelemetrySimulation(depthMd, mudWeight);
      setHistory([]);
      const tickRes = await fetchTelemetryTick();
      setTelemetryState(tickRes);
    } catch (err) {
      console.error("Failed to reset telemetry:", err);
    }
  };

  const curr = telemetryState?.telemetry || {
    depth_md: 2320.0,
    depth_tvd: 2314.5,
    rop_m_hr: 14.5,
    wob_klbs: 21.0,
    torque_kft_lbs: 11.2,
    standpipe_pressure_psi: 2550.0,
    mud_weight_in_ppg: 10.4,
    flow_out_pct: 100.0,
    active_formation: "Tipam Sandstone"
  };

  const probs = telemetryState?.ml_hazard_probabilities || {
    gas_kick_prob: 0.05,
    loss_circulation_prob: 0.08,
    stuck_pipe_prob: 0.02,
    normal_prob: 0.85
  };

  const riskTier = telemetryState?.hybrid_risk_tier || "LOW";

  const getTierColor = (tier) => {
    switch (tier) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/40";
      case "HIGH":
        return "bg-orange-500/20 text-orange-400 border-orange-500/40";
      case "MEDIUM":
        return "bg-amber-500/20 text-amber-400 border-amber-500/40";
      default:
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/40";
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-700/80 rounded-xl p-3.5 shadow-xl flex flex-col space-y-3">
      {/* Header with Live Status & Streaming Controls */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 shadow-sm">
            <Activity className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-100">
                eRTMAC Real-Time Telemetry Stream
              </h2>
              <span
                className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded border uppercase font-mono ${getTierColor(
                  riskTier
                )}`}
              >
                ML Risk: {riskTier}
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono">
              Live MWD/LWD rig feed correlated with Assam Basin offset hazards
            </p>
          </div>
        </div>

        {/* Play/Pause & Reset Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsStreaming(!isStreaming)}
            className={`px-2.5 py-1 rounded text-[11px] font-bold flex items-center space-x-1.5 transition ${
              isStreaming
                ? "bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 border border-amber-500/40"
                : "bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 border border-emerald-500/40"
            }`}
          >
            {isStreaming ? (
              <>
                <Pause className="w-3 h-3" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-3 h-3" />
                <span>Stream</span>
              </>
            )}
          </button>

          <button
            onClick={() => handleResetTo(2320.0, 10.4)}
            title="Reset telemetry drillstring"
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Primary Telemetry Metric Ribbons */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-2 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 font-medium uppercase">Bit Depth (MD)</span>
          <div className="flex items-baseline space-x-1 mt-1">
            <span className="text-base font-extrabold text-amber-400 font-mono">
              {curr.depth_md.toFixed(1)}
            </span>
            <span className="text-[10px] text-slate-500">m</span>
          </div>
          <span className="text-[9px] text-slate-500 font-mono">TVD: {curr.depth_tvd?.toFixed(1)}m</span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-2 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 font-medium uppercase">Penetration (ROP)</span>
          <div className="flex items-baseline space-x-1 mt-1">
            <span className="text-base font-extrabold text-emerald-400 font-mono">
              {curr.rop_m_hr}
            </span>
            <span className="text-[10px] text-slate-500">m/hr</span>
          </div>
          <span className="text-[9px] text-slate-500 font-mono">WOB: {curr.wob_klbs} klbs</span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-2 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 font-medium uppercase">Surface Torque</span>
          <div className="flex items-baseline space-x-1 mt-1">
            <span className={`text-base font-extrabold font-mono ${curr.torque_kft_lbs > 25 ? "text-red-400 animate-pulse" : "text-sky-400"}`}>
              {curr.torque_kft_lbs}
            </span>
            <span className="text-[10px] text-slate-500">kft·lbs</span>
          </div>
          <span className="text-[9px] text-slate-500 font-mono">SPP: {curr.standpipe_pressure_psi} psi</span>
        </div>

        <div className="bg-slate-950/70 border border-slate-800 rounded-lg p-2 flex flex-col justify-between">
          <span className="text-[10px] text-slate-400 font-medium uppercase">Mud Weight</span>
          <div className="flex items-baseline space-x-1 mt-1">
            <span className="text-base font-extrabold text-indigo-400 font-mono">
              {curr.mud_weight_in_ppg}
            </span>
            <span className="text-[10px] text-slate-500">ppg</span>
          </div>
          <span className="text-[9px] text-slate-400 font-mono truncate" title={curr.active_formation}>
            {curr.active_formation || "Tipam"}
          </span>
        </div>
      </div>

      {/* Real-Time Recharts Stacked Streaming Curves */}
      <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-bold text-slate-300 uppercase tracking-wide">
              Telemetry Dynamics Stream
            </span>
            <span className="text-[10px] text-slate-500 font-mono">
              (Rolling 25 ticks)
            </span>
          </div>

          {/* Toggle metric visualization */}
          <div className="flex items-center space-x-1 bg-slate-900 p-0.5 rounded-lg border border-slate-800 text-[10px]">
            <button
              onClick={() => setActiveMetricTab("drilling")}
              className={`px-2 py-0.5 rounded font-bold transition ${
                activeMetricTab === "drilling"
                  ? "bg-slate-800 text-amber-400 shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              ROP & Torque
            </button>
            <button
              onClick={() => setActiveMetricTab("hydraulics")}
              className={`px-2 py-0.5 rounded font-bold transition ${
                activeMetricTab === "hydraulics"
                  ? "bg-slate-800 text-sky-400 shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              SPP & Mud Wt
            </button>
          </div>
        </div>

        {/* Recharts Container with fixed aspect ratio */}
        <div className="h-44 w-full">
          <ResponsiveContainer width="100%" height="100%">
            {activeMetricTab === "drilling" ? (
              <AreaChart data={history} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="ropGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="torqueGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 9 }} />
                <YAxis stroke="#475569" tick={{ fontSize: 9 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    fontSize: "11px",
                    borderRadius: "8px"
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="rop_m_hr"
                  name="ROP (m/hr)"
                  stroke="#10b981"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#ropGrad)"
                />
                <Area
                  type="monotone"
                  dataKey="torque_kft_lbs"
                  name="Torque (kft·lbs)"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#torqueGrad)"
                />
              </AreaChart>
            ) : (
              <LineChart data={history} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#475569" tick={{ fontSize: 9 }} />
                <YAxis stroke="#475569" tick={{ fontSize: 9 }} domain={["auto", "auto"]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#0f172a",
                    borderColor: "#334155",
                    fontSize: "11px",
                    borderRadius: "8px"
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="standpipe_pressure_psi"
                  name="SPP (psi)"
                  stroke="#38bdf8"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="mud_weight_in_ppg"
                  name="Mud Weight (ppg)"
                  stroke="#a855f7"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>

      {/* ML Hazard Probability Gauges */}
      <div className="bg-slate-950/60 border border-slate-800 rounded-lg p-2.5">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] font-bold uppercase text-slate-400 flex items-center gap-1">
            <Zap className="w-3 h-3 text-amber-400" />
            <span>Hybrid ML Hazard Probabilities</span>
          </span>
          <span className="text-[9px] text-slate-500 font-mono">
            RandomForestClassifier Inference
          </span>
        </div>

        <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
          {/* Gas Kick */}
          <div className="bg-slate-900 border border-slate-800 p-1.5 rounded">
            <div className="text-slate-400 text-[9px]">Gas Kick</div>
            <div
              className={`font-bold font-mono text-xs ${
                probs.gas_kick_prob > 0.4 ? "text-red-400" : "text-slate-200"
              }`}
            >
              {(probs.gas_kick_prob * 100).toFixed(1)}%
            </div>
            <div className="w-full bg-slate-800 h-1 rounded-full mt-1 overflow-hidden">
              <div
                className="bg-red-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${Math.min(probs.gas_kick_prob * 100, 100)}%` }}
              />
            </div>
          </div>

          {/* Mud Loss */}
          <div className="bg-slate-900 border border-slate-800 p-1.5 rounded">
            <div className="text-slate-400 text-[9px]">Mud Loss</div>
            <div
              className={`font-bold font-mono text-xs ${
                probs.loss_circulation_prob > 0.4 ? "text-amber-400" : "text-slate-200"
              }`}
            >
              {(probs.loss_circulation_prob * 100).toFixed(1)}%
            </div>
            <div className="w-full bg-slate-800 h-1 rounded-full mt-1 overflow-hidden">
              <div
                className="bg-amber-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${Math.min(probs.loss_circulation_prob * 100, 100)}%` }}
              />
            </div>
          </div>

          {/* Stuck Pipe */}
          <div className="bg-slate-900 border border-slate-800 p-1.5 rounded">
            <div className="text-slate-400 text-[9px]">Stuck Pipe</div>
            <div
              className={`font-bold font-mono text-xs ${
                probs.stuck_pipe_prob > 0.4 ? "text-orange-400" : "text-slate-200"
              }`}
            >
              {(probs.stuck_pipe_prob * 100).toFixed(1)}%
            </div>
            <div className="w-full bg-slate-800 h-1 rounded-full mt-1 overflow-hidden">
              <div
                className="bg-orange-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${Math.min(probs.stuck_pipe_prob * 100, 100)}%` }}
              />
            </div>
          </div>

          {/* Normal Drilling */}
          <div className="bg-slate-900 border border-slate-800 p-1.5 rounded">
            <div className="text-slate-400 text-[9px]">Normal Status</div>
            <div className="font-bold font-mono text-xs text-emerald-400">
              {(probs.normal_prob * 100).toFixed(1)}%
            </div>
            <div className="w-full bg-slate-800 h-1 rounded-full mt-1 overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-300"
                style={{ width: `${Math.min(probs.normal_prob * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Active Warning Notification banner if any */}
        {telemetryState?.active_warning && (
          <div className="mt-2 p-2 rounded bg-amber-500/10 border border-amber-500/30 flex items-center space-x-2 text-[11px] text-amber-300">
            <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
            <span className="font-medium">{telemetryState.active_warning}</span>
          </div>
        )}
      </div>

      {/* Quick Simulation Jump corridor buttons */}
      <div className="flex items-center space-x-1.5 text-[10px] pt-1 border-t border-slate-800">
        <span className="text-slate-500 font-semibold uppercase">Hazard Scenarios:</span>
        <button
          onClick={() => handleResetTo(2335.0, 10.6)}
          className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-amber-400 border border-slate-700 transition"
        >
          Tipam Mud Loss (2,335m)
        </button>
        <button
          onClick={() => handleResetTo(3410.0, 10.2)}
          className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-red-400 border border-slate-700 transition"
        >
          Barail Gas Kick (3,410m)
        </button>
        <button
          onClick={() => handleResetTo(2880.0, 10.4)}
          className="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-orange-400 border border-slate-700 transition"
        >
          Torque Stall (2,880m)
        </button>
      </div>
    </div>
  );
}
