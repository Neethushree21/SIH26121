import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import WellMap from "./components/Map/WellMap";
import WellDetailModal from "./components/Map/WellDetailModal";
import RAGChat from "./components/Chat/RAGChat";
import RiskFeed from "./components/Alerts/RiskFeed";
import DocumentIngestModal from "./components/Ingest/DocumentIngestModal";
import { fetchWells, queryNearbyWells, fetchWellDetail, fetchHazardFeed } from "./utils/api";
import { Compass, AlertTriangle, ShieldCheck, ArrowRight, Table, Layers, Sparkles, Activity } from "lucide-react";

export default function App() {
  const [wells, setWells] = useState([]);
  const [offsetWells, setOffsetWells] = useState([]);
  const [selectedField, setSelectedField] = useState("");
  const [spudLocation, setSpudLocation] = useState({ lat: 27.2891, lon: 95.3524 }); // Centered near Nahorkatiya
  const [radiusKm, setRadiusKm] = useState(5.0);
  const [selectedWellDetail, setSelectedWellDetail] = useState(null);
  const [ingestModalOpen, setIngestModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("risks"); // "risks" or "chat"
  const [hazardCount, setHazardCount] = useState(0);
  const [loading, setLoading] = useState(false);

  // Load all wells on initial render or when field filter changes
  useEffect(() => {
    loadWells();
    loadHazardCount();
  }, [selectedField]);

  // Update offset proximity query when spud coordinates or radius changes
  useEffect(() => {
    loadOffsetWells();
  }, [spudLocation, radiusKm, wells]);

  const loadWells = async () => {
    try {
      const data = await fetchWells(selectedField);
      setWells(data);
    } catch (err) {
      console.error("Failed to load wells", err);
    }
  };

  const loadHazardCount = async () => {
    try {
      const data = await fetchHazardFeed();
      setHazardCount(data.length);
    } catch (err) {
      console.error("Failed to load hazards", err);
    }
  };

  const loadOffsetWells = async () => {
    if (!spudLocation.lat || !spudLocation.lon) return;
    try {
      const res = await queryNearbyWells(spudLocation.lat, spudLocation.lon, radiusKm);
      setOffsetWells(res.offset_wells || []);
    } catch (err) {
      console.error("Failed to query nearby wells", err);
    }
  };

  const handleSelectWell = async (well) => {
    try {
      const detail = await fetchWellDetail(well.id);
      setSelectedWellDetail(detail);
    } catch (err) {
      console.error("Failed to fetch well details", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      
      {/* Top Navbar */}
      <Navbar
        selectedField={selectedField}
        onSelectField={setSelectedField}
        onOpenIngest={() => setIngestModalOpen(true)}
        totalWellsCount={wells.length}
        activeAlertsCount={hazardCount}
      />

      {/* Main Workspace Layout */}
      <main className="flex-1 max-w-[1920px] w-full mx-auto p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left & Center Geospatial Column (7 or 8 columns on desktop) */}
        <div className="lg:col-span-7 xl:col-span-8 flex flex-col space-y-6">
          
          {/* Map Section */}
          <div className="h-[520px] xl:h-[580px] w-full">
            <WellMap
              wells={wells}
              offsetWells={offsetWells}
              spudLocation={spudLocation}
              radiusKm={radiusKm}
              onRadiusChange={setRadiusKm}
              onSpudChange={(lat, lon) => setSpudLocation({ lat, lon })}
              onSelectWell={handleSelectWell}
              selectedWell={selectedWellDetail}
            />
          </div>

          {/* Offset Wells Proximity Table */}
          <div className="bg-slate-900 border border-oil-border rounded-xl p-4 shadow-xl space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Compass className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Offset Wells Correlated within {radiusKm} km Corridor ({offsetWells.length})
                </h3>
              </div>
              <span className="text-[11px] text-slate-400 font-mono">
                PostGIS Radial Query (`ST_DWithin`)
              </span>
            </div>

            <div className="border border-slate-800 rounded-xl overflow-hidden max-h-[220px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 uppercase font-semibold sticky top-0">
                  <tr>
                    <th className="p-2.5">Offset Well</th>
                    <th className="p-2.5">Offset Similarity</th>
                    <th className="p-2.5">Distance</th>
                    <th className="p-2.5">Azimuth</th>
                    <th className="p-2.5">Target Formation</th>
                    <th className="p-2.5">Total Depth</th>
                    <th className="p-2.5">Hazards</th>
                    <th className="p-2.5 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300">
                  {offsetWells.map((ow) => {
                    const compPct = ow.similarity_breakdown?.composite_pct || Math.round((ow.composite_similarity_score || 0) * 100);
                    const breakdown = ow.similarity_breakdown;
                    return (
                      <tr key={ow.id} className="hover:bg-slate-800/40">
                        <td className="p-2.5 font-bold text-white flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                          <span>{ow.name}</span>
                        </td>
                        <td className="p-2.5">
                          <div className="flex flex-col space-y-1">
                            <div className="flex items-center space-x-1.5">
                              <span className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded border ${
                                compPct >= 85
                                  ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                                  : compPct >= 65
                                  ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
                                  : "bg-slate-800 text-slate-400 border-slate-700"
                              }`}>
                                {compPct}% Match
                              </span>
                            </div>
                            {breakdown && (
                              <div className="text-[9px] text-slate-500 font-mono flex items-center space-x-1">
                                <span title="30% Formation Match">Fm:{Math.round(breakdown.formation_match * 100)}%</span>
                                <span>•</span>
                                <span title="25% Depth Proximity">Dp:{Math.round(breakdown.depth_proximity * 100)}%</span>
                                <span>•</span>
                                <span title="20% Spatial Proximity">Sp:{Math.round(breakdown.spatial_proximity * 100)}%</span>
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="p-2.5 font-mono text-amber-400 font-semibold">
                          {ow.distance_km} km
                        </td>
                        <td className="p-2.5 font-mono text-slate-400">
                          {ow.bearing_degrees}°
                        </td>
                        <td className="p-2.5 text-slate-300">{ow.target_formation || "Barail"}</td>
                        <td className="p-2.5 font-mono">{ow.total_depth_tvd} m</td>
                        <td className="p-2.5">
                          {ow.critical_hazards_count > 0 ? (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                              {ow.critical_hazards_count} Critical
                            </span>
                          ) : ow.hazard_count > 0 ? (
                            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                              {ow.hazard_count} Logged
                            </span>
                          ) : (
                            <span className="text-[10px] text-emerald-400">Clean</span>
                          )}
                        </td>
                        <td className="p-2.5 text-right">
                          <button
                            onClick={() => handleSelectWell(ow)}
                            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-amber-400 font-semibold text-[11px] transition"
                          >
                            View Profile
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                  {offsetWells.length === 0 && (
                    <tr>
                      <td colSpan="8" className="p-6 text-center text-slate-500 text-xs">
                        No offset wells found within {radiusKm} km. Increase search radius in the map toolbar.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        {/* Right Intelligence Column (5 or 4 columns on desktop) */}
        <div className="lg:col-span-5 xl:col-span-4 flex flex-col space-y-4">
          
          {/* Tab Switcher between Risk Engine and RAG Assistant */}
          <div className="flex bg-slate-900 p-1 rounded-xl border border-oil-border shadow-md">
            <button
              onClick={() => setActiveTab("risks")}
              className={`flex-1 py-2 rounded-lg text-xs font-bold flex items-center justify-center space-x-2 transition ${
                activeTab === "risks"
                  ? "bg-amber-500 text-black shadow-md shadow-amber-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Offset Risk Advisor</span>
            </button>
            <button
              onClick={() => setActiveTab("chat")}
              className={`flex-1 py-2 rounded-lg text-xs font-bold flex items-center justify-center space-x-2 transition ${
                activeTab === "chat"
                  ? "bg-amber-500 text-black shadow-md shadow-amber-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>RAG Knowledge Chat</span>
            </button>
          </div>

          {/* Active Tab Panel */}
          <div className="flex-1 min-h-[500px]">
            {activeTab === "risks" ? (
              <RiskFeed
                spudLocation={spudLocation}
                radiusKm={radiusKm}
                offsetWells={offsetWells}
                onSelectWell={handleSelectWell}
              />
            ) : (
              <RAGChat selectedWell={selectedWellDetail} />
            )}
          </div>

        </div>

      </main>

      {/* Well Deep Dive Modal */}
      {selectedWellDetail && (
        <WellDetailModal
          well={selectedWellDetail}
          onClose={() => setSelectedWellDetail(null)}
        />
      )}

      {/* Document Ingestion Pipeline Modal */}
      {ingestModalOpen && (
        <DocumentIngestModal
          onClose={() => setIngestModalOpen(false)}
        />
      )}

    </div>
  );
}
