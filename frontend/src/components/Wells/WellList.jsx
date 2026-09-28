import React, { useState } from "react";
import {
  Compass,
  ArrowUpDown,
  AlertTriangle,
  ShieldCheck,
  Search,
  ExternalLink,
  ChevronRight,
  Layers,
  Activity
} from "lucide-react";

export default function WellList({ offsetWells, radiusKm, onSelectWell, selectedWellId }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("similarity"); // similarity, distance, depth, hazards

  // Filter & sort
  const filtered = (offsetWells || []).filter((w) => {
    const term = searchTerm.toLowerCase();
    return (
      w.name.toLowerCase().includes(term) ||
      (w.uwi && w.uwi.toLowerCase().includes(term)) ||
      (w.target_formation && w.target_formation.toLowerCase().includes(term))
    );
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === "similarity") {
      const scoreA = a.composite_similarity_score ?? a.similarity_breakdown?.composite_score ?? 0;
      const scoreB = b.composite_similarity_score ?? b.similarity_breakdown?.composite_score ?? 0;
      return scoreB - scoreA;
    }
    if (sortBy === "distance") {
      return (a.distance_km || 0) - (b.distance_km || 0);
    }
    if (sortBy === "depth") {
      return (b.total_depth_tvd || 0) - (a.total_depth_tvd || 0);
    }
    if (sortBy === "hazards") {
      return (b.critical_hazards_count || 0) - (a.critical_hazards_count || 0);
    }
    return 0;
  });

  return (
    <div className="bg-slate-900 border border-slate-700/80 rounded-xl p-3 shadow-xl flex flex-col flex-1 min-h-[280px]">
      {/* Header with Title and Proximity Radius */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
        <div className="flex items-center space-x-2">
          <div className="w-6 h-6 rounded bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Compass className="w-3.5 h-3.5" />
          </div>
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Offset Wells ({sorted.length})
            </h3>
            <span className="text-[10px] text-slate-400 font-mono">
              Within {radiusKm} km PostGIS corridor
            </span>
          </div>
        </div>

        {/* Sort selector */}
        <div className="flex items-center space-x-1.5">
          <ArrowUpDown className="w-3 h-3 text-slate-400" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-[10px] rounded px-1.5 py-0.5 focus:outline-none focus:border-amber-500"
          >
            <option value="similarity">Rank: Similarity</option>
            <option value="distance">Rank: Distance</option>
            <option value="depth">Rank: Depth TVD</option>
            <option value="hazards">Rank: Hazards</option>
          </select>
        </div>
      </div>

      {/* Mini search input */}
      <div className="my-2 relative">
        <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-slate-500" />
        <input
          type="text"
          placeholder="Filter offsets by name, UWI, or formation..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-slate-950/80 border border-slate-800 rounded-lg pl-8 pr-2.5 py-1 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500/60"
        />
      </div>

      {/* Offset Well Cards / Table container */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 max-h-[290px]">
        {sorted.map((ow) => {
          const compPct = ow.similarity_breakdown?.composite_pct || Math.round((ow.composite_similarity_score || 0) * 100);
          const breakdown = ow.similarity_breakdown;
          const isSelected = selectedWellId === ow.id;

          return (
            <div
              key={ow.id}
              onClick={() => onSelectWell(ow)}
              className={`p-2.5 rounded-lg border transition-all cursor-pointer select-none ${
                isSelected
                  ? "bg-slate-800/90 border-amber-500/80 shadow-md shadow-amber-500/10"
                  : "bg-slate-800/50 hover:bg-slate-800 border-slate-700/60 hover:border-slate-600"
              }`}
            >
              {/* Row 1: Name, Status, and Composite Score */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      ow.critical_hazards_count > 0
                        ? "bg-red-400 animate-pulse"
                        : ow.status === "Drilling"
                        ? "bg-sky-400"
                        : "bg-emerald-400"
                    }`}
                  />
                  <span className="font-bold text-xs text-white tracking-wide">
                    {ow.name}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {ow.uwi}
                  </span>
                </div>

                <div className="flex items-center space-x-1.5">
                  <span
                    className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded border font-mono ${
                      compPct >= 85
                        ? "bg-emerald-500/15 text-emerald-400 border-emerald-500/30"
                        : compPct >= 65
                        ? "bg-amber-500/15 text-amber-400 border-amber-500/30"
                        : "bg-slate-800 text-slate-400 border-slate-700"
                    }`}
                  >
                    {compPct}% Match
                  </span>
                </div>
              </div>

              {/* Row 2: Distance, Formation, and TVD */}
              <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-300">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-amber-400 font-semibold">
                    {ow.distance_km} km
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="text-slate-300 truncate max-w-[110px]" title={ow.target_formation}>
                    {ow.target_formation || "Barail"}
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="font-mono text-slate-400">
                    {ow.total_depth_tvd}m TVD
                  </span>
                </div>

                {/* Hazards tag */}
                <div>
                  {ow.critical_hazards_count > 0 ? (
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                      {ow.critical_hazards_count} Critical
                    </span>
                  ) : ow.hazard_count > 0 ? (
                    <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                      {ow.hazard_count} Logged
                    </span>
                  ) : (
                    <span className="text-[9px] text-emerald-400">Clean</span>
                  )}
                </div>
              </div>

              {/* Row 3: 5-Factor Similarity Breakdown Pills */}
              {breakdown && (
                <div className="mt-2 pt-1.5 border-t border-slate-800/80 grid grid-cols-4 gap-1 text-[9px] font-mono text-slate-400">
                  <div className="bg-slate-900/80 px-1 py-0.5 rounded text-center" title="30% Stratigraphic Formation Match">
                    <span className="text-slate-500">Fm:</span>{" "}
                    <span className="text-emerald-400 font-bold">{Math.round(breakdown.formation_match * 100)}%</span>
                  </div>
                  <div className="bg-slate-900/80 px-1 py-0.5 rounded text-center" title="25% Total Depth Proximity">
                    <span className="text-slate-500">Dp:</span>{" "}
                    <span className="text-sky-400 font-bold">{Math.round(breakdown.depth_proximity * 100)}%</span>
                  </div>
                  <div className="bg-slate-900/80 px-1 py-0.5 rounded text-center" title="20% Spatial Radial Proximity">
                    <span className="text-slate-500">Sp:</span>{" "}
                    <span className="text-amber-400 font-bold">{Math.round(breakdown.spatial_proximity * 100)}%</span>
                  </div>
                  <div className="bg-slate-900/80 px-1 py-0.5 rounded text-center" title="15% Drilling Parameter Alignment">
                    <span className="text-slate-500">Pr:</span>{" "}
                    <span className="text-indigo-400 font-bold">{Math.round(breakdown.parameter_alignment * 100)}%</span>
                  </div>
                </div>
              )}
            </div>
          );
        })}

        {sorted.length === 0 && (
          <div className="p-6 text-center text-slate-500 text-xs flex flex-col items-center justify-center space-y-1">
            <Compass className="w-6 h-6 text-slate-600 mb-1" />
            <span>No offset wells found within {radiusKm} km corridor.</span>
            <span className="text-[10px] text-slate-600">Try expanding the buffer radius in the map above.</span>
          </div>
        )}
      </div>
    </div>
  );
}
