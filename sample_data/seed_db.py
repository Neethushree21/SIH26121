import os
import sys
import glob
import json
import csv
from datetime import datetime

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "backend"))

from app.core.database import SessionLocal, init_db, engine, is_sqlite
from app.models.well import Well, TrajectoryPoint, FormationTop
from app.models.drilling_event import DrillingHazard
from app.models.document import IngestedDocument
from app.services.ingestion import ingestion_service

def generate_sample_pdfs():
    """Generates authentic synthetic PDF technical reports using PyMuPDF."""
    reports_dir = os.path.join(BASE_DIR, "sample_data", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        import fitz  # PyMuPDF
        
        pdf_samples = [
            {
                "filename": "WCR_NHK_412.pdf",
                "title": "OIL INDIA LIMITED - WELL COMPLETION REPORT",
                "content": (
                    "WELL: Nahorkatiya-412 (UWI: OIL-NHK-412)\n"
                    "FIELD: Nahorkatiya, Upper Assam Basin | OPERATOR: Oil India Limited\n"
                    "TOTAL DEPTH: 3,780 m MD / 3,695 m TVD | KB ELEVATION: 122.0 m\n\n"
                    "GEOLOGICAL STRATIGRAPHY & FORMATION TOPS:\n"
                    "- Girujan Clay: 380 m to 1,840 m TVD (Plastocene swelling shale)\n"
                    "- Tipam Sandstone: 1,840 m to 2,790 m TVD (Highly porous reservoir sand, loss zone)\n"
                    "- Barail Coal-Shale: 2,790 m to 3,380 m TVD (Overpressure transition zone, gas kicks)\n"
                    "- Barail Main Sand: 3,380 m to 3,580 m TVD (Primary oil discovery, 34 API)\n"
                    "- Kopili Formation: 3,580 m to 3,695 m TVD (Base seal calcareous shale)\n\n"
                    "CASING PROGRAM & LOGGED HAZARDS:\n"
                    "13-3/8' Surface Casing @ 1,180 m | 9-5/8' Intermediate @ 2,780 m\n"
                    "Encountered severe partial loss of circulation (45 bbl/hr) at 2,340 m MD in Tipam Sand.\n"
                    "Successfully controlled with 50 bbl nut plug / mica LCM pill and 250 psi squeeze.\n"
                )
            },
            {
                "filename": "DDR_BGH_03_Day28.pdf",
                "title": "OIL INDIA LIMITED - DAILY DRILLING REPORT (DDR #28)",
                "content": (
                    "WELL: Baghjan-03 (UWI: OIL-BGH-03)\n"
                    "CURRENT DEPTH: 3,425 m MD / 3,410 m TVD | HOLE SIZE: 8-1/2'\n"
                    "FORMATION: Barail Coal-Shale Sequence | MUD WEIGHT: 10.3 ppg\n\n"
                    "CRITICAL INCIDENT: HIGH-PRESSURE GAS KICK AT 3,420 m MD\n"
                    "During drilling break (ROP 6 to 32 m/hr), flow sensors registered 18 bbl pit gain.\n"
                    "Rig crew executed immediate hard shut-in on annular BOP.\n"
                    "Stabilized Pressures: SIDPP = 440 psi, SICP = 680 psi.\n\n"
                    "KILL OPERATION SUMMARY:\n"
                    "Calculated Kill Mud Weight: 11.4 ppg.\n"
                    "Executed Wait and Weight (Engineer's) Method. Displaced kick volume through\n"
                    "choke manifold with zero surface casing damage.\n"
                    "Recommendation: Maintain minimum 11.2 - 11.5 ppg mud weight when drilling offset\n"
                    "wells through Barail Coal-Shale in the Baghjan structure.\n"
                )
            }
        ]

        for pdata in pdf_samples:
            pdf_path = os.path.join(reports_dir, pdata["filename"])
            doc = fitz.open()
            page = doc.new_page(width=595, height=842) # A4
            
            # Draw header line
            page.draw_rect(fitz.Rect(40, 40, 555, 42), color=(0.96, 0.62, 0.07), fill=(0.96, 0.62, 0.07))
            page.insert_text((45, 65), pdata["title"], fontsize=13, fontname="helv", color=(0.1, 0.1, 0.1))
            page.insert_text((45, 95), "SYNTHETIC OPERATIONAL DOCUMENT - OIL INDIA LIMITED (SIH26121)", fontsize=8, fontname="helv", color=(0.4, 0.4, 0.4))
            
            # Content
            page.insert_textbox(fitz.Rect(45, 120, 550, 750), pdata["content"], fontsize=10, fontname="helv", color=(0.15, 0.15, 0.15))
            
            doc.save(pdf_path)
            doc.close()
            print(f"Generated PDF: {pdata['filename']} using PyMuPDF.")
            
    except Exception as e:
        print(f"Note on PDF generation: {e}")

def seed_database():
    print("Initializing Database Schemas...")
    init_db()
    db = SessionLocal()

    # Generate synthetic PDFs first
    generate_sample_pdfs()

    try:
        print("Clearing existing data for clean seed...")
        db.query(TrajectoryPoint).delete()
        db.query(FormationTop).delete()
        db.query(DrillingHazard).delete()
        db.query(Well).delete()
        db.query(IngestedDocument).delete()
        db.commit()

        print("Seeding Oil India Limited (Upper Assam Basin) Wells...")

        wells_data = [
            {
                "uwi": "OIL-NHK-412",
                "name": "Nahorkatiya-412",
                "field_name": "Nahorkatiya",
                "operator": "Oil India Limited",
                "status": "Producing",
                "target_formation": "Barail Sandstone",
                "total_depth_tvd": 3695.0,
                "total_depth_md": 3780.0,
                "latitude": 27.2891,
                "longitude": 95.3524,
                "elevation_kb": 122.0,
                "spud_date": datetime(2024, 1, 12),
                "completion_date": datetime(2024, 4, 24),
                "hazards": [
                    {
                        "event_type": "Loss of Circulation",
                        "severity": "HIGH",
                        "depth_md": 2340.0,
                        "formation_name": "Tipam Sandstone",
                        "mud_weight_ppg": 10.4,
                        "description": "Sudden loss of returns (45 bbl in 12 min) during 12-1/4' rotary drilling.",
                        "remediation_action": "Spotted 50 bbl mica/nut-plug LCM pill with 250 psi squeeze.",
                        "npt_hours": 14.0
                    },
                    {
                        "event_type": "Tight Hole",
                        "severity": "LOW",
                        "depth_md": 1420.0,
                        "formation_name": "Girujan Clay",
                        "mud_weight_ppg": 9.6,
                        "description": "Overpull of 45 klbs while tripping out drill collars.",
                        "remediation_action": "Reamed section and conditioned mud with glycol inhibitor.",
                        "npt_hours": 4.5
                    }
                ]
            },
            {
                "uwi": "OIL-NHK-420",
                "name": "Nahorkatiya-420",
                "field_name": "Nahorkatiya",
                "operator": "Oil India Limited",
                "status": "Drilling",
                "target_formation": "Barail Main Sand",
                "total_depth_tvd": 3550.0,
                "total_depth_md": 3610.0,
                "latitude": 27.2945,
                "longitude": 95.3610,
                "elevation_kb": 121.5,
                "spud_date": datetime(2024, 7, 10),
                "hazards": [
                    {
                        "event_type": "Gas Kick",
                        "severity": "HIGH",
                        "depth_md": 3120.0,
                        "formation_name": "Barail Coal-Shale",
                        "mud_weight_ppg": 10.6,
                        "description": "Pit gain of 12 bbl observed with background gas jumping to 35%.",
                        "remediation_action": "Weighted mud from 10.6 to 11.2 ppg using barite.",
                        "npt_hours": 8.0
                    }
                ]
            },
            {
                "uwi": "OIL-BGH-03",
                "name": "Baghjan-03",
                "field_name": "Baghjan",
                "operator": "Oil India Limited",
                "status": "Producing",
                "target_formation": "Barail Main Sand",
                "total_depth_tvd": 3950.0,
                "total_depth_md": 4020.0,
                "latitude": 27.6012,
                "longitude": 95.3945,
                "elevation_kb": 114.0,
                "spud_date": datetime(2024, 2, 5),
                "completion_date": datetime(2024, 5, 30),
                "hazards": [
                    {
                        "event_type": "Gas Kick",
                        "severity": "CRITICAL",
                        "depth_md": 3420.0,
                        "formation_name": "Barail Coal-Shale",
                        "mud_weight_ppg": 10.3,
                        "description": "Rapid pit gain 18 bbl in 4 minutes. SIDPP: 440 psi, SICP: 680 psi.",
                        "remediation_action": "Executed Wait & Weight method, weighted mud system up to 11.4 ppg.",
                        "npt_hours": 26.0
                    },
                    {
                        "event_type": "Wellbore Collapse",
                        "severity": "HIGH",
                        "depth_md": 3580.0,
                        "formation_name": "Barail Coal-Shale",
                        "mud_weight_ppg": 11.4,
                        "description": "Splintery cavings pack off annulus causing pump pressure spike of 900 psi.",
                        "remediation_action": "Circulated high-viscosity pill and adjusted pH and polymer filtration control.",
                        "npt_hours": 12.0
                    }
                ]
            },
            {
                "uwi": "OIL-MOR-88",
                "name": "Moran-88",
                "field_name": "Moran",
                "operator": "Oil India Limited",
                "status": "Producing",
                "target_formation": "Barail Main Sand",
                "total_depth_tvd": 3845.0,
                "total_depth_md": 3920.0,
                "latitude": 27.1842,
                "longitude": 94.9214,
                "elevation_kb": 118.5,
                "spud_date": datetime(2023, 8, 2),
                "completion_date": datetime(2023, 11, 18),
                "hazards": [
                    {
                        "event_type": "Stuck Pipe",
                        "severity": "CRITICAL",
                        "depth_md": 2890.0,
                        "formation_name": "Tipam Sandstone",
                        "mud_weight_ppg": 10.5,
                        "description": "Differential sticking across depleted Tipam sand during 45 min directional survey.",
                        "remediation_action": "Spotted 45 bbl ester-based freeing pill. Freed string after 4.5 hrs jarring.",
                        "npt_hours": 16.5
                    }
                ]
            },
            {
                "uwi": "OIL-JRN-15",
                "name": "Jorajan-15",
                "field_name": "Jorajan",
                "operator": "Oil India Limited",
                "status": "Suspended",
                "target_formation": "Tipam Sandstone",
                "total_depth_tvd": 3100.0,
                "total_depth_md": 3150.0,
                "latitude": 27.2415,
                "longitude": 95.4210,
                "elevation_kb": 125.0,
                "spud_date": datetime(2023, 10, 1),
                "completion_date": datetime(2024, 1, 15),
                "hazards": [
                    {
                        "event_type": "Loss of Circulation",
                        "severity": "MEDIUM",
                        "depth_md": 2150.0,
                        "formation_name": "Tipam Sandstone",
                        "mud_weight_ppg": 10.2,
                        "description": "Seepage losses of 18 bbl/hr in porous sand.",
                        "remediation_action": "Added 12 ppb calcium carbonate blend to active system.",
                        "npt_hours": 5.0
                    }
                ]
            },
            {
                "uwi": "OIL-DGB-101",
                "name": "Digboi-101",
                "field_name": "Digboi",
                "operator": "Oil India Limited",
                "status": "Producing",
                "target_formation": "Tipam Sandstone",
                "total_depth_tvd": 1850.0,
                "total_depth_md": 1890.0,
                "latitude": 27.3820,
                "longitude": 95.6215,
                "elevation_kb": 160.0,
                "spud_date": datetime(2023, 3, 14),
                "completion_date": datetime(2023, 6, 20),
                "hazards": []
            }
        ]

        well_orm_map = {}

        for wdata in wells_data:
            wkt_geom = f"POINT({wdata['longitude']} {wdata['latitude']})"
            well = Well(
                uwi=wdata["uwi"],
                name=wdata["name"],
                field_name=wdata["field_name"],
                operator=wdata["operator"],
                status=wdata["status"],
                target_formation=wdata["target_formation"],
                total_depth_tvd=wdata["total_depth_tvd"],
                total_depth_md=wdata["total_depth_md"],
                latitude=wdata["latitude"],
                longitude=wdata["longitude"],
                geom=wkt_geom,
                elevation_kb=wdata["elevation_kb"],
                spud_date=wdata.get("spud_date"),
                completion_date=wdata.get("completion_date")
            )
            db.add(well)
            db.flush()
            well_orm_map[wdata["uwi"]] = well

            # Insert hazards
            for h in wdata.get("hazards", []):
                hazard = DrillingHazard(
                    well_id=well.id,
                    event_type=h["event_type"],
                    severity=h["severity"],
                    depth_md=h["depth_md"],
                    formation_name=h.get("formation_name"),
                    mud_weight_ppg=h.get("mud_weight_ppg"),
                    description=h["description"],
                    remediation_action=h.get("remediation_action"),
                    npt_hours=h.get("npt_hours", 0.0)
                )
                db.add(hazard)

        # Ingest formations from sample_data/formations.json
        formations_path = os.path.join(BASE_DIR, "sample_data", "formations.json")
        if os.path.exists(formations_path):
            with open(formations_path, "r", encoding="utf-8") as f:
                formations_list = json.load(f)
                for fitem in formations_list:
                    uwi = fitem.get("well_uwi")
                    if uwi in well_orm_map:
                        w_obj = well_orm_map[uwi]
                        form_top = FormationTop(
                            well_id=w_obj.id,
                            formation_name=fitem["formation_name"],
                            top_md=fitem["top_md"],
                            top_tvd=fitem["top_tvd"],
                            base_tvd=fitem.get("base_tvd"),
                            pore_pressure_gradient_ppg=fitem.get("pore_pressure_gradient_ppg"),
                            lithology_description=fitem.get("lithology_description")
                        )
                        db.add(form_top)

        # Ingest trajectories from sample_data/trajectories.csv
        trajectories_path = os.path.join(BASE_DIR, "sample_data", "trajectories.csv")
        if os.path.exists(trajectories_path):
            with open(trajectories_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    uwi = row.get("well_uwi")
                    if uwi in well_orm_map:
                        w_obj = well_orm_map[uwi]
                        traj = TrajectoryPoint(
                            well_id=w_obj.id,
                            md=float(row["md"]),
                            tvd=float(row["tvd"]),
                            inclination=float(row["inclination"]),
                            azimuth=float(row["azimuth"]),
                            latitude=float(row["latitude"]),
                            longitude=float(row["longitude"]),
                            dogleg_severity=float(row.get("dogleg_severity", 0.0))
                        )
                        db.add(traj)

        db.commit()
        print(f"Database seeded with {len(wells_data)} wells, trajectories, formations, and hazards.")

        # Ingest sample technical reports into vector store (both .txt and .pdf)
        reports_dir = os.path.join(BASE_DIR, "sample_data", "reports")
        report_files = glob.glob(os.path.join(reports_dir, "*.*"))
        print(f"Indexing {len(report_files)} technical reports into Vector Store...")

        for rf in report_files:
            fname = os.path.basename(rf)
            ingested = ingestion_service.ingest_file(db=db, file_path=rf, filename=fname)
            print(f"  Indexed: {fname} ({ingested.file_type}) -> {ingested.chunk_count} chunks")

        print("Phase 1 Seed Pipeline completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
