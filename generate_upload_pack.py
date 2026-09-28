import os
import csv
import json
import pymupdf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PACK_DIR = os.path.join(BASE_DIR, "test_upload_pack")
os.makedirs(PACK_DIR, exist_ok=True)

print(f"Generating test upload pack in: {PACK_DIR}")

# -------------------------------------------------------------
# 1. PDF Report 1: Nahorkatiya-415 Severe Mud Loss in Tipam
# -------------------------------------------------------------
pdf1_path = os.path.join(PACK_DIR, "DDR_NHK_415_Severe_Mud_Loss_Tipam.pdf")
doc1 = pymupdf.open()

# Page 1: Executive Summary & Timeline
page1 = doc1.new_page(width=595, height=842) # A4
p1_text = """OIL INDIA LIMITED - DAILY DRILLING REPORT (DDR #19)
FIELD OPERATIONS HEADQUARTERS, DULIAJAN, ASSAM
SYNTHETIC OPERATIONAL AUDIT DOCUMENTATION (SIH26121 PROTOTYPE)

WELL IDENTIFICATION:
Well Name: Nahorkatiya-415 | UWI: OIL-NHK-415 | Rig: OIL Rig-08 (Assam Shelf)
Spud Date: 12-Nov-2023 | 24-Hr Reported Depth: 2,365 m MD (2,342 m TVD)
Active Stratigraphic Formation: Tipam Sandstone | Hole Size: 12-1/4 inch
Mud System: Potassium Chloride / Polymer WBM | Current Mud Weight: 10.6 ppg

24-HOUR OPERATIONAL LOG & CHRONOLOGY:
00:00 - 05:30: Rotary drilling 12-1/4" section from 2,310 m to 2,340 m MD. Parameters steady:
               ROP: 14.5 m/hr, WOB: 22 klbs, Surface Torque: 10.8 kft-lbs, SPP: 2,450 psi.
05:30 - 06:15: Drilled into highly porous fractured Tipam Sandstone interval at 2,340 m MD.
06:15 - 07:00: CRITICAL EVENT: Complete loss of returns observed in mud pits (Pit Level Drop: 45 bbl in 12 min).
               Standpipe pressure dropped sharply from 2,450 psi to 1,680 psi.
               Immediately stopped rotary table, picked up off bottom to 2,330 m MD, spaced out drillstring.
07:00 - 10:30: Mixed and pumped 50 bbl high-viscosity Loss Circulation Material (LCM) pill
               containing 25 ppb medium walnut shells, 15 ppb coarse mica flakes, and 10 ppb cellulosic fiber.
10:30 - 13:00: Squeezed LCM pill into fractured sand with hesitation pumping (annular pressure 280 psi).
               Observed gradual pressure stabilization. Fluid level in annulus held static.
13:00 - 17:00: Controlled circulation resumed at reduced pump rate 480 GPM (previously 650 GPM).
               Reduced active mud weight from 10.6 ppg to 10.2 ppg to stay within fracture gradient window.
17:00 - 24:00: Resumed washing and reaming 2,335 m - 2,365 m with full 100% returns restored.

DRILLING HAZARD SUMMARY:
- Event: Severe Lost Circulation / Porous Depleted Sand Influx
- Total Non-Productive Time (NPT): 10.5 Hours
- Recommended Mitigation: Pre-treat active system with 15-20 ppb fine calcium carbonate prior to crossing
  the upper Tipam Sandstone contact. Maintain ECD strictly below 10.8 ppg.
"""
page1.insert_textbox(pymupdf.Rect(40, 40, 555, 800), p1_text, fontsize=9.5, fontname="helv")

# Page 2: Mud Properties & BHA Configuration
page2 = doc1.new_page(width=595, height=842)
p2_text = """OIL INDIA LIMITED - DAILY DRILLING REPORT (DDR #19) [PAGE 2]
MUD PROPERTIES & BOTTOM HOLE ASSEMBLY (BHA) TECHNICAL REPORT

MUD PROPERTIES AT 2,365 m MD:
- Mud Type: KCl-Polymer Water Based Mud (Inhibitive Shale & Sand System)
- Density: 10.2 ppg (Reduced from 10.6 ppg following lost circulation remediation)
- Funnel Viscosity: 48 sec/qt
- Plastic Viscosity (PV): 18 cP
- Yield Point (YP): 22 lb/100 sq ft
- Gel Strength: 6 / 14 lb/100 sq ft (10 sec / 10 min)
- API Fluid Loss: 4.8 cc / 30 min
- pH: 9.4 | Chlorides: 38,000 mg/L | KCl Content: 6.5% wt

BOTTOM HOLE ASSEMBLY (BHA #4):
1. 12-1/4" PDC Bit (5 blades, 16mm cutters)
2. 8" Mud Motor (1.5 deg bent housing, 7/8 lobe)
3. Float Sub & Filter Sub (tested to 3,500 psi)
4. MWD / LWD Telemetry Collar (Directional, Gamma Ray, Resistivity)
5. 8" Non-Magnetic Drill Collars (2 joints)
6. 8" Spiral Drill Collars (6 joints)
7. Drilling Jar (Mechanical/Hydraulic double acting, placed at 2,180 m MD)
8. 5" Heavy Weight Drill Pipe (15 joints)
9. 5" Range 2 S-135 Drill Pipe to surface

REMARKS & SUPERINTENDENT RECOMMENDATION:
Offset data from Nahorkatiya-412 confirms porous thief zones at 2,335 - 2,350 m MD.
Always spot LCM pill before penetrating deeper Barail formations. Maintain standby LCM inventory on rig.
"""
page2.insert_textbox(pymupdf.Rect(40, 40, 555, 800), p2_text, fontsize=9.5, fontname="helv")
doc1.save(pdf1_path)
doc1.close()
print(f"Created: {pdf1_path}")


# -------------------------------------------------------------
# 2. PDF Report 2: Baghjan-07 High-Pressure Gas Kick in Barail
# -------------------------------------------------------------
pdf2_path = os.path.join(PACK_DIR, "DDR_BGH_07_High_Pressure_Gas_Kick_Barail.pdf")
doc2 = pymupdf.open()

page1 = doc2.new_page(width=595, height=842)
p2_text = """OIL INDIA LIMITED - DAILY DRILLING REPORT (DDR #34)
FIELD OPERATIONS HEADQUARTERS, DULIAJAN, ASSAM
SYNTHETIC OPERATIONAL AUDIT DOCUMENTATION (SIH26121 PROTOTYPE)

WELL IDENTIFICATION:
Well Name: Baghjan-07 | UWI: OIL-BGH-07 | Field: Baghjan
Spud Date: 05-Jan-2024 | Current Depth: 3,428 m MD (3,390 m TVD)
Target Stratigraphic Formation: Barail Coal-Shale Main Sand | Hole Size: 8-1/2 inch
Current Mud Weight: 10.3 ppg | Rig: OIL High-Pressure Deep Rig 03

CRITICAL WELL CONTROL EVENT LOG:
08:15 - Penetrated upper Barail Coal stringer at depth 3,420 m MD.
08:18 - DRILLING BREAK: Instantaneous ROP surged from 8.2 m/hr to 36.5 m/hr with zero increase in WOB.
08:22 - Mud logger reported background gas elevation jumping from 2.5% to 42.0% with strong C1-C4 chromatograph peaks.
08:25 - Flow show on trip tank: 14 bbl pit volume gain detected in 4 minutes.
08:26 - WELL SHUT-IN: Driller picked up kelly off bottom, shut down mud pumps, verified flow,
        and closed Annular Preventer followed by opening hydraulic choke HCR valve.
08:35 - Pressure stabilization recorded on choke panel:
        Shut-In Drill Pipe Pressure (SIDPP): 440 psi
        Shut-In Casing Pressure (SICP): 680 psi
        Total Pit Influx Volume: 16.5 bbl gas/condensate influx

WELL KILL EXECUTION (WAIT & WEIGHT METHOD):
- Initial Mud Weight: 10.3 ppg
- Calculated Required Kill Mud Density (KMD):
  KMD = 10.3 + (440 psi / (0.052 * 3,390 m * 3.28084 ft/m)) = 11.45 ppg (Mixed to 11.5 ppg).
- Weighed up active mud pits using barium sulfate (Barite) and circulated kill mud via drillstring.
- Maintained drillpipe pressure schedule using adjusted choke opening.
- Influx circulated out safely through Poor Boy degasser without venting to atmosphere.
- SIDPP and SICP dropped to 0 psi upon kill mud arrival at surface.
- Total NPT Incurred: 22.0 Hours.

AUDIT EVIDENCE & MITIGATION DIRECTIVES:
1. When crossing into Barail Coal stringers (>3,350 m MD), conduct pre-recorded slow circulating rates (SCR)
   every 100 meters or after bit change.
2. Maintain reserve barite inventory of minimum 80 metric tonnes on rig site.
3. Keep choke manifold and Annular BOP tested to 5,000 psi every 14 days.
"""
page1.insert_textbox(pymupdf.Rect(40, 40, 555, 800), p2_text, fontsize=9.5, fontname="helv")
doc2.save(pdf2_path)
doc2.close()
print(f"Created: {pdf2_path}")


# -------------------------------------------------------------
# 3. PDF Report 3: Moran-92 Differential Sticking Summary (WCR)
# -------------------------------------------------------------
pdf3_path = os.path.join(PACK_DIR, "WCR_MOR_92_Differential_Sticking_Summary.pdf")
doc3 = pymupdf.open()

page1 = doc3.new_page(width=595, height=842)
p3_text = """OIL INDIA LIMITED - WELL COMPLETION REPORT (WCR EXTRACT)
DRILLING ENGINEERING DEPARTMENT - MORAN ASSET
SYNTHETIC TECHNICAL CASE STUDY (SIH26121 PROTOTYPE)

WELL SUMMARY:
Well Name: Moran-92 | UWI: OIL-MOR-92 | Field: Moran
Total Depth Reached: 3,920 m MD (3,845 m TVD) | Rig: Moran Super-Rig 02
Spud Date: 14-Aug-2023 | Completion Date: 02-Dec-2023

POST-WELL DRILLING HAZARD CASE STUDY: DIFFERENTIAL PIPE STICKING
1. Incident Occurrence:
   At depth 2,890 m MD (Tipam Sandstone / Barail boundary), drillstring was left static for 50 minutes
   to conduct an MWD directional survey and gyroscopic check.
   Upon attempting to resume rotation and reciprocation, string was found differentially stuck against
   a permeable, depleted Tipam sandstone bed.
   Overbalance pressure across the sand was estimated at 620 psi (Mud weight: 10.7 ppg vs pore pressure 9.5 ppg).

2. Remedial Action & Pipe-Freeing Protocol:
   - Initial Jarring: Fired hydraulic drilling jar upward with 80,000 lbs overpull. String remained stuck.
   - Spotting Freeing Pill: Mixed 45 bbl of oil-based pipe-freeing soak pill containing surfactant wetting agents.
   - Displaced pill to bit and allowed 3 hours soaking time across the stuck interval (2,870 m - 2,900 m).
   - Re-applied upward jarring with 110,000 lbs overpull.
   - After 4.5 hours of jarring and chemical soaking, drillstring freed with sudden drop in drag.
   - Total NPT: 16.5 Hours.

3. Engineering Lessons & Recommendations for Offset Wells:
   - Limit stationary time in open-hole depleted sands to maximum 15 minutes.
   - Rotate drillpipe at 15-20 RPM during directional surveys if MWD tool permits.
   - Optimize mud cake lubricity with 2-3% liquid glycol or lubricant additive to lower friction coefficient.
"""
page1.insert_textbox(pymupdf.Rect(40, 40, 555, 800), p3_text, fontsize=9.5, fontname="helv")
doc3.save(pdf3_path)
doc3.close()
print(f"Created: {pdf3_path}")


# -------------------------------------------------------------
# 4. Text Report: Jorajan-18 Wellbore Instability in Kopili
# -------------------------------------------------------------
txt_path = os.path.join(PACK_DIR, "DDR_JRN_18_Wellbore_Instability_Kopili.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    f.write("""OIL INDIA LIMITED - DAILY DRILLING REPORT (DDR #42)
JORAJAN ASSET - SYNTHETIC DATA FOR SIH26121 PROTOTYPE

WELL IDENTIFICATION:
Well Name: Jorajan-18 | UWI: OIL-JRN-18 | Depth: 3,680 m MD (3,620 m TVD)
Formation: Kopili Shale | Hole Size: 8-1/2 inch | Mud Weight: 11.2 ppg

INCIDENT LOG:
- Encountered splintery cavings and high shaker volume while drilling through Kopili Shale at 3,650 - 3,680 m MD.
- Annular backpressure increased by 350 psi due to annular pack-off.
- Mud weight raised from 10.8 ppg to 11.2 ppg with added polymer encapsulator (PHPA 1.5 lb/bbl) to inhibit shale hydration and prevent hole collapse.
- Circulated high-viscosity sweep pill (40 bbl) to clean wellbore. Recovered 8 bbl of reactive shale cavings.
- Drag dropped from 45 klbs to normal baseline (12 klbs).

RECOMMENDATION:
For nearby spuds, maintain minimum 11.2 ppg mud density and KCl concentration > 7% when penetrating Kopili Shale interval.
""")
print(f"Created: {txt_path}")


# -------------------------------------------------------------
# 5. CSV Telemetry Log: Assam Basin Drilling Parameters Log
# -------------------------------------------------------------
csv_path = os.path.join(PACK_DIR, "Assam_Basin_Drilling_Parameters_Log.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "depth_md", "depth_tvd", "formation", "rop_m_hr", "wob_klbs", 
        "torque_kft_lbs", "standpipe_pressure_psi", "mud_weight_ppg", "flow_out_pct", "status"
    ])
    
    # 50 rows of synthetic drilling telemetry
    data_rows = [
        [2310.0, 2295.0, "Tipam Sandstone", 15.2, 21.0, 10.5, 2450, 10.5, 100.0, "Normal"],
        [2320.0, 2304.8, "Tipam Sandstone", 14.8, 21.5, 11.0, 2480, 10.5, 100.0, "Normal"],
        [2330.0, 2314.5, "Tipam Sandstone", 13.9, 22.0, 11.8, 2520, 10.6, 99.5, "Normal"],
        [2340.0, 2324.2, "Tipam Sandstone", 24.5, 18.0, 12.5, 1850, 10.6, 55.0, "Mud Loss Detected"],
        [2345.0, 2329.0, "Tipam Sandstone", 18.0, 16.0, 11.2, 1720, 10.2, 42.0, "Severe Lost Circulation"],
        [2350.0, 2334.0, "Tipam Sandstone", 5.0, 12.0, 8.5, 2200, 10.2, 85.0, "LCM Squeeze Remediation"],
        [2360.0, 2343.8, "Tipam Sandstone", 12.5, 20.0, 10.2, 2420, 10.2, 100.0, "Normal Drilling Resumed"],
        [2850.0, 2810.0, "Tipam Sandstone", 14.0, 22.0, 12.0, 2550, 10.6, 100.0, "Normal"],
        [2885.0, 2842.0, "Tipam Sandstone", 2.5, 29.0, 32.5, 2980, 10.7, 98.0, "Torque Spike / Tight Hole"],
        [2890.0, 2847.0, "Tipam Sandstone", 0.0, 35.0, 38.0, 3250, 10.7, 95.0, "Differentially Stuck"],
        [2895.0, 2851.5, "Tipam Sandstone", 8.0, 18.0, 11.5, 2500, 10.5, 100.0, "Freed with Soak Pill"],
        [3380.0, 3320.0, "Barail Coal-Shale", 11.0, 21.0, 12.2, 2600, 10.3, 100.0, "Normal"],
        [3410.0, 3350.0, "Barail Coal-Shale", 12.2, 20.5, 13.0, 2620, 10.3, 100.0, "Normal"],
        [3420.0, 3360.0, "Barail Coal-Shale", 38.5, 15.0, 14.8, 2150, 10.3, 145.0, "Gas Kick Influx (Drilling Break)"],
        [3425.0, 3365.0, "Barail Coal-Shale", 0.0, 0.0, 0.0, 0, 11.5, 0.0, "BOP Shut In (SIDPP 440 psi)"],
        [3430.0, 3370.0, "Barail Coal-Shale", 9.5, 19.0, 11.0, 2700, 11.5, 100.0, "Killed with 11.5 ppg mud"],
        [3650.0, 3590.0, "Kopili Shale", 8.5, 23.0, 16.5, 2850, 11.2, 98.0, "Shale Sloughing"],
        [3680.0, 3620.0, "Kopili Shale", 10.0, 22.0, 13.5, 2780, 11.2, 100.0, "Stabilized with PHPA Polymer"]
    ]
    writer.writerows(data_rows)

print(f"Created: {csv_path}")


# -------------------------------------------------------------
# 6. CSV Trajectory Plan: Offset Well Directional Survey
# -------------------------------------------------------------
traj_path = os.path.join(PACK_DIR, "Offset_Well_Trajectory_Survey.csv")
with open(traj_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["well_uwi", "well_name", "md_m", "tvd_m", "inclination_deg", "azimuth_deg", "dls_deg_30m", "latitude", "longitude"])
    traj_rows = [
        ["OIL-NHK-415", "Nahorkatiya-415", 0.0, 0.0, 0.0, 0.0, 0.0, 27.2950, 95.3580],
        ["OIL-NHK-415", "Nahorkatiya-415", 500.0, 500.0, 0.5, 45.0, 0.03, 27.2951, 95.3581],
        ["OIL-NHK-415", "Nahorkatiya-415", 1500.0, 1498.2, 8.2, 52.0, 0.25, 27.2965, 95.3602],
        ["OIL-NHK-415", "Nahorkatiya-415", 2340.0, 2320.5, 16.5, 55.4, 0.30, 27.2995, 95.3650],
        ["OIL-NHK-415", "Nahorkatiya-415", 3500.0, 3420.0, 22.0, 58.0, 0.15, 27.3045, 95.3725],
        ["OIL-BGH-07", "Baghjan-07", 0.0, 0.0, 0.0, 0.0, 0.0, 27.5920, 95.4850],
        ["OIL-BGH-07", "Baghjan-07", 1000.0, 999.5, 2.0, 110.0, 0.06, 27.5915, 95.4862],
        ["OIL-BGH-07", "Baghjan-07", 2500.0, 2485.0, 11.5, 115.0, 0.20, 27.5890, 95.4910],
        ["OIL-BGH-07", "Baghjan-07", 3420.0, 3380.0, 18.0, 118.0, 0.22, 27.5855, 95.4980]
    ]
    writer.writerows(traj_rows)

print(f"Created: {traj_path}")

# Also mirror into sample_data/demo_upload_pack
sample_mirror_dir = os.path.join(BASE_DIR, "sample_data", "demo_upload_pack")
os.makedirs(sample_mirror_dir, exist_ok=True)
import shutil
for f in os.listdir(PACK_DIR):
    shutil.copy2(os.path.join(PACK_DIR, f), os.path.join(sample_mirror_dir, f))

print(f"Mirrored test pack to: {sample_mirror_dir}")
print("ALL TEST UPLOAD FILES GENERATED SUCCESSFULLY!")
