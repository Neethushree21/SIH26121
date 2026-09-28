import React from "react";
import { Compass, Flame, ShieldAlert, FileText, Database, Activity, Sparkles } from "lucide-react";

export default function Navbar({
  selectedField,
  onSelectField,
  onOpenIngest,
  totalWellsCount,
  activeAlertsCount,
  onOpenHelp
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
    <header className="bg-oil-panel border-b border-oil-border sticky top-0 z-50 shadow-lg">
      <div className="max-w-[1920px] mx-auto px-4 sm:px-6 py-2.5 flex items-center justify-between">
        
        {/* Brand & Client Identification */}
        <div className="flex items-center space-x-3.5">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500 to-amber-700 flex items-center justify-center shadow-md shadow-amber-500/20">
            <Flame className="w-6 h-6 text-black font-black" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs uppercase font-extrabold tracking-wider px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                OIL INDIA LIMITED
              </span>
              <span className="text-xs font-mono text-slate-400">SIH26121</span>
            </div>
            <h1 className="text-base font-bold text-slate-100 flex items-center gap-1.5">
              NWIS <span className="text-xs font-normal text-slate-400 hidden md:inline">| Nearby Wells Intelligence System</span>
            </h1>
          </div>
        </div>

        {/* Operational Field Selector */}
        <div className="hidden lg:flex items-center space-x-2 bg-slate-900/80 p-1 rounded-lg border border-slate-800">
          <Compass className="w-4 h-4 text-amber-400 ml-2" />
          <span className="text-xs text-slate-400 font-medium">Field:</span>
          <select
            value={selectedField}
            onChange={(e) => onSelectField(e.target.value)}
            className="bg-transparent text-xs font-semibold text-slate-200 focus:outline-none pr-3 cursor-pointer"
          >
            {fields.map((f) => (
              <option key={f.id} value={f.id} className="bg-slate-900 text-slate-200">
                {f.label}
              </option>
            ))}
          </select>
        </div>

        {/* Live System Status Badges & Action Buttons */}
        <div className="flex items-center space-x-3">
          {/* PostGIS & Database Indicator */}
          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-mono">PostGIS / GeoSpatial Ready</span>
          </div>

          {/* Active Hazards Alert Count */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>{activeAlertsCount} Offset Hazards</span>
          </div>

          {/* Document Ingestion Trigger */}
          <button
            onClick={onOpenIngest}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs transition duration-150 shadow-md shadow-amber-500/20"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Ingest Reports</span>
          </button>
        </div>

      </div>
    </header>
  );
}
