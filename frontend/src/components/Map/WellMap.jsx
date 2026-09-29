import React, { useEffect, useState, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import { Navigation, Target, Layers, AlertTriangle, ShieldCheck, Crosshair, ArrowUpRight } from "lucide-react";

// Fix Leaflet standard marker icon paths in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// Custom SVG Icons for Oil Wells
const createWellIcon = (status, hasHazard) => {
  let color = "#10b981"; // green producing
  if (status === "Drilling") color = "#0284c7"; // blue drilling
  if (status === "Suspended") color = "#f59e0b"; // amber suspended
  if (hasHazard) color = "#ef4444"; // red hazard

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28">
      <circle cx="12" cy="12" r="10" fill="#111827" stroke="${color}" stroke-width="2.5"/>
      <circle cx="12" cy="12" r="4" fill="${color}"/>
      ${hasHazard ? '<circle cx="18" cy="6" r="4" fill="#ef4444" stroke="#ffffff" stroke-width="1.5"/>' : ''}
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: "custom-well-pin",
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14],
  });
};

const createSpudIcon = () => {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="36" height="36">
      <circle cx="16" cy="16" r="14" fill="#f59e0b" fill-opacity="0.3" stroke="#f59e0b" stroke-width="2"/>
      <circle cx="16" cy="16" r="7" fill="#f59e0b"/>
      <path d="M16 2 L16 30 M2 16 L30 16" stroke="#ffffff" stroke-width="1.5"/>
    </svg>
  `;
  return L.divIcon({
    html: svg,
    className: "spud-target-pin",
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
};

// Map click handler helper component
function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

// Controller to smoothly pan to selected well or spud
function MapViewController({ center, zoom }) {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, zoom || map.getZoom(), { animate: true });
    }
  }, [center, zoom, map]);
  return null;
}

export default function WellMap({
  wells,
  offsetWells,
  spudLocation,
  radiusKm,
  onRadiusChange,
  onSpudChange,
  onSelectWell,
  selectedWell
}) {
  const [mapCenter, setMapCenter] = useState([27.35, 95.35]); // Assam basin center
  const [mapStyle, setMapStyle] = useState("dark"); // "dark" or "satellite"

  const offsetWellIds = useMemo(() => {
    return new Set((offsetWells || []).map((w) => w.id));
  }, [offsetWells]);

  return (
    <div className="relative w-full h-[340px] xl:h-[360px] shrink-0 flex flex-col rounded-xl overflow-hidden border border-slate-700/80 bg-slate-950 shadow-xl">
      
      {/* Top Map Floating Control Toolbar */}
      <div className="absolute top-2.5 left-2.5 right-2.5 z-[1000] flex flex-wrap items-center justify-between gap-1.5 bg-slate-900/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/60 shadow-lg text-xs">
        <div className="flex items-center space-x-1.5 text-xs font-semibold text-amber-400">
          <Target className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span className="font-mono text-[11px] text-slate-200">
            {spudLocation.lat.toFixed(3)}°N, {spudLocation.lon.toFixed(3)}°E
          </span>
        </div>

        {/* Radius buffer selector & Layer Switcher */}
        <div className="flex items-center space-x-2">
          {/* Basemap Switcher (Free, No API Key Required) */}
          <div className="flex items-center space-x-0.5 bg-slate-800 p-0.5 rounded border border-slate-700 text-[10px]">
            <button
              onClick={() => setMapStyle("dark")}
              className={`px-1.5 py-0.5 rounded font-semibold transition ${
                mapStyle === "dark"
                  ? "bg-amber-500 text-black shadow-xs"
                  : "text-slate-300 hover:text-white"
              }`}
              title="Clean Industrial Dark Mode Basemap"
            >
              Dark
            </button>
            <button
              onClick={() => setMapStyle("satellite")}
              className={`px-1.5 py-0.5 rounded font-semibold transition ${
                mapStyle === "satellite"
                  ? "bg-amber-500 text-black shadow-xs"
                  : "text-slate-300 hover:text-white"
              }`}
              title="High-Resolution Satellite Terrain View"
            >
              Satellite
            </button>
          </div>

          <div className="flex items-center space-x-1">
            <span className="text-slate-400 text-[10px]">Buffer:</span>
            <div className="flex items-center space-x-0.5 bg-slate-800 p-0.5 rounded border border-slate-700">
              {[3, 5, 10, 15].map((r) => (
                <button
                  key={r}
                  onClick={() => onRadiusChange(r)}
                  className={`px-1.5 py-0.2 rounded text-[10px] font-bold transition ${
                    radiusKm === r
                      ? "bg-amber-500 text-black shadow-xs"
                      : "text-slate-300 hover:text-white"
                  }`}
                >
                  {r}k
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Offset Wells Count */}
        <div className="text-[10px] font-semibold text-emerald-400 flex items-center gap-1 font-mono">
          <ShieldCheck className="w-3 h-3" />
          <span>{offsetWells.length} Offsets</span>
        </div>
      </div>

      {/* Map Interactive Hint Bottom Left */}
      <div className="absolute bottom-2 left-2 z-[1000] hidden sm:flex items-center space-x-1 bg-slate-900/85 backdrop-blur-md px-2 py-1 rounded text-[10px] text-slate-400 border border-slate-800">
        <Crosshair className="w-3 h-3 text-amber-400" />
        <span>Click to reposition spud</span>
      </div>


      {/* Map Legend Floating Bottom Right */}
      <div className="absolute bottom-3 right-3 z-[1000] bg-slate-900/90 backdrop-blur-md p-2.5 rounded-xl border border-slate-700/60 shadow-xl text-xs space-y-1.5">
        <div className="font-bold text-slate-300 text-[11px] uppercase tracking-wider mb-1">Symbology</div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-emerald-500 border border-slate-900"></span>
          <span className="text-slate-300">Producing Well</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-sky-500 border border-slate-900"></span>
          <span className="text-slate-300">Drilling Active</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-red-500 border border-slate-900"></span>
          <span className="text-slate-300">Hazard / Kick Reported</span>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-3 h-3 rounded-full bg-amber-400 border border-slate-900 ring-2 ring-amber-400/30"></span>
          <span className="text-amber-400 font-semibold">Planned Spud Location</span>
        </div>
      </div>

      {/* Leaflet Map Canvas */}
      <MapContainer
        center={mapCenter}
        zoom={10}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        {/* Free, Open-Access Basemap (Zero API Key, No Watermark) */}
        {mapStyle === "dark" ? (
          <TileLayer
            key="esri-dark"
            attribution='Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ | Oil India Limited'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
            maxZoom={16}
          />
        ) : (
          <TileLayer
            key="esri-satellite"
            attribution='Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics | Oil India Limited'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            maxZoom={18}
          />
        )}

        <MapClickHandler
          onMapClick={(lat, lon) => {
            onSpudChange(lat, lon);
          }}
        />

        <MapViewController center={[spudLocation.lat, spudLocation.lon]} />

        {/* Dynamic Offset Buffer Circle (PostGIS Representation) */}
        <Circle
          center={[spudLocation.lat, spudLocation.lon]}
          radius={radiusKm * 1000}
          pathOptions={{
            color: "#f59e0b",
            fillColor: "#f59e0b",
            fillOpacity: 0.08,
            weight: 1.5,
            dashArray: "5, 5",
          }}
        />

        {/* Planned Spud Pin */}
        <Marker
          position={[spudLocation.lat, spudLocation.lon]}
          icon={createSpudIcon()}
        >
          <Popup className="oil-popup">
            <div className="p-1 text-slate-900">
              <div className="font-bold text-amber-700 text-sm">Target Spud Location</div>
              <div className="text-xs text-slate-700 mt-1">
                Lat: {spudLocation.lat.toFixed(4)}°N<br />
                Lon: {spudLocation.lon.toFixed(4)}°E
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                Radius: {radiusKm} km buffer active
              </div>
            </div>
          </Popup>
        </Marker>

        {/* Offset Lines connecting target to nearby wells */}
        {offsetWells.map((ow) => (
          <Polyline
            key={`line-${ow.id}`}
            positions={[
              [spudLocation.lat, spudLocation.lon],
              [ow.latitude, ow.longitude],
            ]}
            pathOptions={{
              color: ow.critical_hazards_count > 0 ? "#ef4444" : "#10b981",
              weight: 1.5,
              opacity: 0.5,
              dashArray: "4, 4",
            }}
          />
        ))}

        {/* All Oil India Wells */}
        {wells.map((well) => {
          const isOffset = offsetWellIds.has(well.id);
          const hasHazard = (well.hazard_count || 0) > 0;
          return (
            <Marker
              key={well.id}
              position={[well.latitude, well.longitude]}
              icon={createWellIcon(well.status, hasHazard)}
              eventHandlers={{
                click: () => onSelectWell(well),
              }}
            >
              <Popup>
                <div className="text-slate-900 min-w-[200px] p-1">
                  <div className="flex items-center justify-between border-b pb-1">
                    <span className="font-bold text-sm text-slate-950">{well.name}</span>
                    <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-200 text-slate-800">
                      {well.status}
                    </span>
                  </div>
                  <div className="text-xs text-slate-700 space-y-1 mt-2">
                    <div><span className="font-semibold">UWI:</span> {well.uwi}</div>
                    <div><span className="font-semibold">Field:</span> {well.field_name}</div>
                    <div><span className="font-semibold">Target:</span> {well.target_formation || "Barail Sand"}</div>
                    <div><span className="font-semibold">TVD:</span> {well.total_depth_tvd} m ({Math.round(well.total_depth_tvd * 3.28084)} ft)</div>
                    {hasHazard && (
                      <div className="text-red-700 font-bold flex items-center gap-1 mt-1">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        <span>{well.hazard_count} Historical Hazards</span>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => onSelectWell(well)}
                    className="w-full mt-2.5 py-1 px-2 rounded bg-slate-900 hover:bg-slate-800 text-amber-400 font-semibold text-xs flex items-center justify-center gap-1 transition"
                  >
                    <span>Inspect Well Profile</span>
                    <ArrowUpRight className="w-3 h-3" />
                  </button>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
