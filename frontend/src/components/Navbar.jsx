import React from "react";
import {
  Compass,
  Flame,
  ShieldAlert,
  FileText,
  Database,
  Activity,
  Sparkles,
  MapPin
} from "lucide-react";

export default function Navbar({
  selectedField,
  onSelectField,
  activeWell,
  onSelectActiveWell,
  wells,
  onOpenIngest,
  totalWellsCount,
  activeAlertsCount
}) {
  const fields = [
    { id: "", label: "All Assam Fields" },
    { id: "Nahorkatiya", label: "Nahorkatiya Field" },
    { id: "Baghjan", label: "Baghjan Field" },
    { id: "Moran", label: "Moran Field" },
    { id: "Jorajan", label: "Jorajan Field" },
    { id: "Digboi", label: "Digboi Field" },
  ];

  return (
    <header className="bg-slate-950 border-b border-slate-800 sticky top-0 z-50 shadow-xl">
      <div className="max-w-[1920px] mx-auto px-4 sm:px-6 py-2.5 flex items-center justify-between">
        
        {/* Brand & Organization Title */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center shadow-md shadow-amber-500/20 shrink-0">
            <Flame className="w-5 h-5 text-black font-black" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] uppercase font-extrabold tracking-wider px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                OIL INDIA LIMITED
              </span>
              <span className="text-[10px] font-mono text-slate-400">SIH26121</span>
            </div>
            <h1 className="text-sm font-bold text-slate-100 flex items-center gap-1.5">
              <span>NWIS</span>
              <span className="text-xs font-normal text-slate-400 hidden xl:inline">
                | Nearby Wells Intelligence System
              </span>
            </h1>
          </div>
        </div>

        {/* Center Selectors: Active Wellhead & Field */}
        <div className="hidden md:flex items-center space-x-3">
          {/* Active Spud / Well Focus Selector */}
          <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-lg border border-slate-800">
            <MapPin className="w-3.5 h-3.5 text-amber-400 ml-1.5" />
            <span className="text-xs text-slate-400 font-medium">Focus Well:</span>
            <select
              value={activeWell ? activeWell.id : ""}
              onChange={(e) => {
                const w = (wells || []).find((item) => item.id === e.target.value);
                if (w) onSelectActiveWell(w);
              }}
              className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none pr-2 cursor-pointer max-w-[180px] truncate"
            >
              <option value="" className="bg-slate-900 text-slate-400">
                Select Wellhead...
              </option>
              {(wells || []).map((w) => (
                <option key={w.id} value={w.id} className="bg-slate-900 text-slate-200">
                  {w.name} ({w.field_name})
                </option>
              ))}
            </select>
          </div>

          {/* Operational Field Selector */}
          <div className="flex items-center space-x-2 bg-slate-900 p-1 rounded-lg border border-slate-800">
            <Compass className="w-3.5 h-3.5 text-amber-400 ml-1.5" />
            <span className="text-xs text-slate-400 font-medium">Field:</span>
            <select
              value={selectedField}
              onChange={(e) => onSelectField(e.target.value)}
              className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none pr-2 cursor-pointer"
            >
              {fields.map((f) => (
                <option key={f.id} value={f.id} className="bg-slate-900 text-slate-200">
                  {f.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Live System Status Badges & Action Buttons */}
        <div className="flex items-center space-x-2.5">
          {/* PostGIS Engine Ready */}
          <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-mono text-[11px]">PostGIS Engine</span>
          </div>

          {/* eRTMAC Stream Active */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs">
            <Activity className="w-3 h-3 text-sky-400" />
            <span className="font-mono text-[11px]">eRTMAC Live</span>
          </div>

          {/* Active Hazards Alert Count */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{activeAlertsCount} Hazards</span>
          </div>

          {/* Document Ingestion Trigger Modal */}
          <button
            onClick={onOpenIngest}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition duration-150 shadow-md shadow-amber-500/20"
          >
            <FileText className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Ingest Reports</span>
          </button>
        </div>

      </div>
    </header>
  );
}
