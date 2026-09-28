import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import WellMap from "./components/Map/WellMap";
import WellList from "./components/Wells/WellList";
import WellDetailModal from "./components/Map/WellDetailModal";
import RTMACMonitor from "./components/Telemetry/RTMACMonitor";
import RiskFeed from "./components/Alerts/RiskFeed";
import RAGChat from "./components/Chat/RAGChat";
import DocumentIngestModal from "./components/Ingest/DocumentIngestModal";
import ProtectedRoute from "./components/Auth/ProtectedRoute";
import { fetchWells, queryNearbyWells, fetchWellDetail, fetchHazardFeed } from "./utils/api";

function DashboardContent({ onLogout, currentUser }) {
  const [wells, setWells] = useState([]);
  const [offsetWells, setOffsetWells] = useState([]);
  const [selectedField, setSelectedField] = useState("");
  const [activeWell, setActiveWell] = useState(null);
  const [spudLocation, setSpudLocation] = useState({ lat: 27.2891, lon: 95.3524 }); // Centered near Nahorkatiya
  const [radiusKm, setRadiusKm] = useState(5.0);
  const [selectedWellDetail, setSelectedWellDetail] = useState(null);
  const [ingestModalOpen, setIngestModalOpen] = useState(false);
  const [hazardCount, setHazardCount] = useState(0);

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
      if (data.length > 0 && !activeWell) {
        // Default active well to Nahorkatiya-412 if present
        const defaultWell = data.find((w) => w.uwi === "OIL-NHK-412") || data[0];
        setActiveWell(defaultWell);
        setSpudLocation({ lat: defaultWell.latitude, lon: defaultWell.longitude });
      }
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

  const handleSelectActiveWell = (well) => {
    setActiveWell(well);
    setSpudLocation({ lat: well.latitude, lon: well.longitude });
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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-amber-500 selection:text-black">
      
      {/* 1. Global Navigation Bar with System Badges, Active User, and Operational Controls */}
      <Navbar
        selectedField={selectedField}
        onSelectField={setSelectedField}
        activeWell={activeWell}
        onSelectActiveWell={handleSelectActiveWell}
        wells={wells}
        onOpenIngest={() => setIngestModalOpen(true)}
        totalWellsCount={wells.length}
        activeAlertsCount={hazardCount}
        currentUser={currentUser}
        onLogout={onLogout}
      />

      {/* 2. Enterprise 3-Column Industrial Dark-Mode Control Room Dashboard */}
      <main className="flex-1 w-full max-w-[1920px] mx-auto p-3 sm:p-4 lg:p-5 grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-5">
        
        {/* ========================================================
            COLUMN 1 (LEFT ~25%): Interactive Map & Offset Well Table
           ======================================================== */}
        <section className="lg:col-span-3 flex flex-col space-y-4">
          {/* Interactive Leaflet Map */}
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

          {/* Offset Well Comparison Table */}
          <WellList
            offsetWells={offsetWells}
            radiusKm={radiusKm}
            onSelectWell={handleSelectWell}
            selectedWellId={selectedWellDetail?.id}
          />
        </section>

        {/* ========================================================
            COLUMN 2 (CENTER ~45%): eRTMAC Stream & Evidence Risk Feed
           ======================================================== */}
        <section className="lg:col-span-5 flex flex-col space-y-4">
          {/* Real-Time eRTMAC Telemetry Monitoring Panel (Recharts Curves) */}
          <RTMACMonitor
            onHazardAlert={(alert) => {
              console.log("Telemetry hazard alert triggered:", alert);
            }}
          />

          {/* Live Evidence-Backed Risk Alert Feed */}
          <RiskFeed
            spudLocation={spudLocation}
            radiusKm={radiusKm}
            offsetWells={offsetWells}
            onSelectWell={handleSelectWell}
          />
        </section>

        {/* ========================================================
            COLUMN 3 (RIGHT ~30%): AI Knowledge Repository RAG Chat
           ======================================================== */}
        <section className="lg:col-span-4 flex flex-col h-[750px] lg:h-auto lg:min-h-full">
          <RAGChat
            selectedWell={activeWell}
            onClearWellFilter={() => setActiveWell(null)}
          />
        </section>

      </main>

      {/* Deep Dive Profile Modal */}
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

export default function App() {
  return (
    <ProtectedRoute>
      {({ onLogout, currentUser }) => (
        <DashboardContent onLogout={onLogout} currentUser={currentUser} />
      )}
    </ProtectedRoute>
  );
}
