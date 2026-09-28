# NWIS: Nearby Wells Intelligence System
### Tailored for Oil India Limited (Problem Statement SIH26121)

> [!IMPORTANT]
> **DISCLAIMER & DATA NOTICE:**  
> The prototype uses synthetic data modeled on the types of datasets described in the PS (Assam basin formations like Tipam and Barail). Actual Oil India Limited operational data is not available to the student team.

NWIS is an enterprise-grade full-stack spatial and knowledge intelligence platform built for drilling engineers, geologists, and operations managers at **Oil India Limited (OIL)**. It enables proactive drilling hazard prevention by correlating planned well trajectories against historical offset wells, formation boundaries, and unstructured technical reports (Daily Drilling Reports & Well Completion Reports).

---

## 🌟 Key Features

1. **Geospatial Proximity & Offset Well Discovery**
   - Radial and corridor spatial search around proposed spud locations (`ST_DWithin`).
   - Dynamic buffer radii (3 km, 5 km, 8 km, 15 km) with bearing angle and offset distance calculations.
   - Dual-engine architecture: Native **PostgreSQL + PostGIS** for enterprise deployment with automated SQLite/Haversine fallback for zero-dependency local runs.

2. **3D Directional Trajectories & Stratigraphy**
   - Visual inspection of well directional survey points (MD, TVD, Inclination, Azimuth, Dogleg Severity).
   - Stratigraphic tops mapping for Upper Assam Basin formations (Girujan Clay, Tipam Sandstone, Barail Coal-Shale, Barail Main Sand).

3. **Live Drilling Risk & Mud Weight Window Advisor**
   - Automated offset hazard correlation (Gas Kicks, Lost Circulation, Stuck Pipe, Wellbore Collapse).
   - Dynamic mud weight envelope advisor (Min Kick Margin, Max Fracture Loss, Surge Allowance).
   - Severity filtering (CRITICAL, HIGH, MEDIUM, LOW) with field remediation recommendations.

4. **Technical Knowledge Assistant (Vector RAG)**
   - ChromaDB vector store indexing historical DDRs and WCRs.
   - Domain-aware AI assistant with cited source excerpts, formation depths, and similarity matching.

5. **Folder & Report Ingestion Pipeline**
   - Drag-and-drop or folder scanning for technical PDFs and text reports.
   - Automated semantic chunking and vector embedding.

---

## 🏗️ Architecture

```
SIH26121/
├── docker-compose.yml              # PostgreSQL + PostGIS, ChromaDB, FastAPI
├── README.md                       # Documentation & setup guide
├── backend/                        # FastAPI Application
│   ├── app/
│   │   ├── core/                   # Settings, DB session, PostGIS connection
│   │   ├── models/                 # SQLAlchemy ORM (Well, Trajectory, Formation, Hazard, IngestedDoc)
│   │   ├── schemas/                # Pydantic schemas (GeoJSON, Chat, Alert, Query)
│   │   ├── services/               # Geospatial, ChromaDB vector store, Ingestion, Risk engine
│   │   └── api/v1/                 # Endpoints (/wells, /search, /alerts, /ingest)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                       # React 18 + Vite + Tailwind CSS Dashboard
│   ├── src/
│   │   ├── components/             # Navbar, Leaflet WellMap, RAGChat, RiskFeed, IngestModal
│   │   ├── utils/api.js            # Unified backend API client
│   │   └── App.jsx
└── sample_data/                    # Authentic Upper Assam Basin Synthetic Dataset
    ├── reports/                    # Sample DDRs & WCRs with realistic incidents
    └── seed_db.py                  # Seed script populating wells, trajectories & vector index
```

---

## 🚀 Quick Start Guide

### Option A: Local Development (Fastest, No Docker Required)

#### 1. Setup Backend & Seed Database
```bash
# In SIH26121/
pip install -r backend/requirements.txt

# Populate database with Oil India sample wells & vectorize reports
python sample_data/seed_db.py

# Launch FastAPI backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend API docs will be live at `http://localhost:8000/docs`.*

#### 2. Setup Frontend
```bash
# In SIH26121/frontend/
npm install
npm run dev
```
*Frontend will be running at `http://localhost:5173`.*

---

### Option B: Docker Compose (PostgreSQL + PostGIS + Backend)

If Docker Desktop is running:
```bash
docker compose up -d --build
```
This spins up:
- **PostGIS 15 Container** on port `5432` with automatic database initialization.
- **FastAPI Backend** on port `8000`.

Then run frontend locally:
```bash
cd frontend && npm run dev
```

---

## 📡 API Overview

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/wells` | `GET` | List all wells filtered by field and operational status |
| `/api/v1/wells/geojson` | `GET` | GeoJSON FeatureCollection of wellheads for GIS mapping |
| `/api/v1/wells/nearby` | `POST` | Spatial proximity query by Lat, Lon, and Radius (`km`) |
| `/api/v1/wells/{id}` | `GET` | Complete well profile with trajectories and formations |
| `/api/v1/alerts/feed` | `GET` | Live feed of drilling hazards sorted by severity and date |
| `/api/v1/alerts/assess`| `POST` | Spud location risk matrix and recommended mud weight window |
| `/api/v1/search/query` | `POST` | RAG semantic vector search over DDRs/WCRs with citations |
| `/api/v1/ingest/upload`| `POST` | Upload and vectorize a technical drilling document |
| `/api/v1/ingest/status`| `GET` | View list of indexed technical reports and chunk counts |

---

## 🛢️ Sample Oil India Operational Fields Included
- **Nahorkatiya Field** (Discovered 1953, Barail Sandstone reservoir, Tipam loss zones)
- **Baghjan Field** (High pressure gas kick history in Barail Coal-Shale)
- **Moran Field** (Differential sticking tendencies across depleted Tipam sands)
- **Jorajan Field** (Porous Tipam gas sandstones)
- **Digboi Field** (Historic shallow oil sands)
