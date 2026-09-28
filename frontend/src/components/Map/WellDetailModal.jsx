import React, { useState } from "react";
import { X, Layers, Activity, AlertTriangle, ShieldCheck, FileText, ChevronRight, Compass } from "lucide-react";

export default function WellDetailModal({ well, onClose }) {
  const [activeTab, setActiveTab] = useState("overview");

  if (!well) return null;

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-4xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 font-black">
              OIL
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold text-white">{well.name}</h2>
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {well.uwi}
                </span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                  {well.status}
                </span>
              </div>
              <p className="text-xs text-slate-400">
                {well.field_name} Field • Operator: {well.operator} • Lat: {well.latitude}°N, Lon: {well.longitude}°E
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-800 bg-slate-950/60 px-6">
          {[
            { id: "overview", label: "Overview & Specs", icon: Compass },
            { id: "formations", label: `Stratigraphy (${well.formations?.length || 0})`, icon: Layers },
            { id: "trajectory", label: `Trajectory (${well.trajectories?.length || 0})`, icon: Activity },
            { id: "hazards", label: `Hazards & NPT (${well.hazards?.length || 0})`, icon: AlertTriangle },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-3 px-4 text-xs font-semibold border-b-2 transition ${
                  activeTab === tab.id
                    ? "border-amber-500 text-amber-400 bg-amber-500/5"
                    : "border-transparent text-slate-400 hover:text-slate-200"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {activeTab === "overview" && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700">
                  <div className="text-[11px] text-slate-400 uppercase font-semibold">Total Depth (TVD)</div>
                  <div className="text-xl font-bold text-white mt-1">{well.total_depth_tvd} m</div>
                  <div className="text-xs text-slate-500">{(well.total_depth_tvd * 3.28084).toFixed(0)} ft</div>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700">
                  <div className="text-[11px] text-slate-400 uppercase font-semibold">Measured Depth (MD)</div>
                  <div className="text-xl font-bold text-white mt-1">{well.total_depth_md} m</div>
                  <div className="text-xs text-slate-500">{(well.total_depth_md * 3.28084).toFixed(0)} ft</div>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700">
                  <div className="text-[11px] text-slate-400 uppercase font-semibold">Target Formation</div>
                  <div className="text-base font-bold text-amber-400 mt-1">{well.target_formation || "Barail Sand"}</div>
                  <div className="text-xs text-slate-500">Assam Shelf Basin</div>
                </div>
                <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-700">
                  <div className="text-[11px] text-slate-400 uppercase font-semibold">KB Elevation</div>
                  <div className="text-xl font-bold text-white mt-1">{well.elevation_kb || 120} m</div>
                  <div className="text-xs text-slate-500">Above MSL</div>
                </div>
              </div>

              {/* Historical Hazards summary */}
              <div className="bg-slate-800/40 p-4 rounded-xl border border-slate-700/60">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  <span>Hazard Summary & Remediation Logs</span>
                </h3>
                {well.hazards && well.hazards.length > 0 ? (
                  <div className="space-y-2">
                    {well.hazards.map((h, i) => (
                      <div key={i} className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-start justify-between">
                        <div>
                          <div className="flex items-center space-x-2">
                            <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                              h.severity === "CRITICAL" ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                            }`}>
                              {h.severity}
                            </span>
                            <span className="font-semibold text-xs text-slate-200">{h.event_type}</span>
                            <span className="text-xs text-slate-500">@ {h.depth_md} m MD</span>
                          </div>
                          <p className="text-xs text-slate-300 mt-1.5">{h.description}</p>
                          {h.remediation_action && (
                            <p className="text-xs text-emerald-400 mt-1">
                              <strong>Remediation:</strong> {h.remediation_action}
                            </p>
                          )}
                        </div>
                        {h.npt_hours > 0 && (
                          <div className="text-right pl-3">
                            <div className="text-xs font-bold text-red-400">{h.npt_hours}h NPT</div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-xs text-slate-400 py-2 flex items-center gap-1.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <span>No critical drilling incidents or non-productive time recorded for this well.</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "formations" && (
            <div className="space-y-4">
              <p className="text-xs text-slate-400">
                Interpreted stratigraphic tops and pore pressure gradients for Upper Assam Basin sequence:
              </p>
              <div className="border border-slate-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-semibold">
                    <tr>
                      <th className="p-3">Formation Name</th>
                      <th className="p-3">Top MD (m)</th>
                      <th className="p-3">Top TVD (m)</th>
                      <th className="p-3">Base TVD (m)</th>
                      <th className="p-3">Est. Pore Press. (ppg)</th>
                      <th className="p-3">Lithology & Operational Notes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {well.formations && well.formations.map((f, i) => (
                      <tr key={i} className="hover:bg-slate-800/40">
                        <td className="p-3 font-bold text-amber-400">{f.formation_name}</td>
                        <td className="p-3 font-mono">{f.top_md} m</td>
                        <td className="p-3 font-mono">{f.top_tvd} m</td>
                        <td className="p-3 font-mono">{f.base_tvd ? `${f.base_tvd} m` : "—"}</td>
                        <td className="p-3">
                          {f.pore_pressure_gradient_ppg ? (
                            <span className="font-semibold text-sky-400">{f.pore_pressure_gradient_ppg} ppg</span>
                          ) : "—"}
                        </td>
                        <td className="p-3 text-slate-400">{f.lithology_description || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === "trajectory" && (
            <div className="space-y-4">
              <p className="text-xs text-slate-400">
                Directional directional survey points from Kelly Bushing to Total Depth:
              </p>
              <div className="border border-slate-800 rounded-xl overflow-hidden max-h-[400px] overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-semibold sticky top-0">
                    <tr>
                      <th className="p-3">MD (m)</th>
                      <th className="p-3">TVD (m)</th>
                      <th className="p-3">Inclination (°)</th>
                      <th className="p-3">Azimuth (°)</th>
                      <th className="p-3">Latitude</th>
                      <th className="p-3">Longitude</th>
                      <th className="p-3">DLS (°/30m)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-300">
                    {well.trajectories && well.trajectories.map((t, i) => (
                      <tr key={i} className="hover:bg-slate-800/40 font-mono">
                        <td className="p-3 font-semibold text-white">{t.md}</td>
                        <td className="p-3">{t.tvd}</td>
                        <td className="p-3 text-amber-400">{t.inclination}°</td>
                        <td className="p-3">{t.azimuth}°</td>
                        <td className="p-3 text-slate-400">{t.latitude.toFixed(6)}</td>
                        <td className="p-3 text-slate-400">{t.longitude.toFixed(6)}</td>
                        <td className="p-3">{t.dogleg_severity || 0.0}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === "hazards" && (
            <div className="space-y-3">
              {well.hazards && well.hazards.length > 0 ? (
                well.hazards.map((h, i) => (
                  <div key={i} className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${
                          h.severity === "CRITICAL" ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        }`}>
                          {h.severity}
                        </span>
                        <span className="font-bold text-sm text-white">{h.event_type}</span>
                        <span className="text-xs text-slate-400">@ {h.depth_md} m MD ({h.formation_name || "N/A"})</span>
                      </div>
                      {h.mud_weight_ppg && (
                        <div className="text-xs text-sky-400 font-semibold">
                          MW: {h.mud_weight_ppg} ppg
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{h.description}</p>
                    {h.remediation_action && (
                      <div className="p-2.5 rounded bg-emerald-950/30 border border-emerald-800/40 text-xs text-emerald-300">
                        <strong className="text-emerald-400">Remediation Action:</strong> {h.remediation_action}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-slate-400 text-xs">
                  No hazards logged for this well.
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-slate-950 px-6 py-3 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition"
          >
            Close Profile
          </button>
        </div>

      </div>
    </div>
  );
}
