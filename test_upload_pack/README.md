# NWIS Prototype Test Upload Pack (Oil India Limited - SIH26121)

This folder contains realistic, synthetic technical drilling files formatted specifically to test the **Nearby Wells Intelligence System (NWIS)** ingestion pipeline, multi-factor correlation engine, and Vector RAG search.

---

## 📁 Included Test Files

| File Name | Format | Primary Event / Scenario | Assam Formation |
|---|---|---|---|
| **`DDR_NHK_415_Severe_Mud_Loss_Tipam.pdf`** | 2-Page PDF | 45 bbl mud loss, standpipe pressure drop to 1680 psi, 50 bbl walnut/mica/fiber LCM pill squeeze, ECD management | **Tipam Sandstone** (2,340 m MD) |
| **`DDR_BGH_07_High_Pressure_Gas_Kick_Barail.pdf`** | PDF Report | 36.5 m/hr drilling break, gas jump to 42%, 16.5 bbl pit gain, SIDPP 440 psi, SICP 680 psi, Wait & Weight kill to 11.5 ppg | **Barail Coal-Shale** (3,420 m MD) |
| **`WCR_MOR_92_Differential_Sticking_Summary.pdf`** | PDF Summary | Differential sticking across depleted sand after 50-min survey, 45 bbl oil-based pipe-freeing soak pill, 110,000 lbs overpull | **Tipam Sandstone / Barail** (2,890 m MD) |
| **`DDR_JRN_18_Wellbore_Instability_Kopili.txt`** | Text Report | Splintery shale cavings, 350 psi backpressure increase, 11.2 ppg mud weighting + PHPA polymer encapsulation | **Kopili Shale** (3,680 m MD) |
| **`Assam_Basin_Drilling_Parameters_Log.csv`** | CSV Telemetry | 18 depth intervals tracking Depth MD/TVD, ROP, WOB, Torque, SPP, Mud Weight, Flow Out % across all 4 hazard scenarios | **Tipam, Barail, Kopili** |
| **`Offset_Well_Trajectory_Survey.csv`** | CSV Trajectory | Multi-station directional survey data (MD, TVD, Inclination, Azimuth, DLS, Lat, Lon) for offset wells | **Assam Shelf Corridor** |

---

## 🚀 How to Test in the Prototype

### Method 1: Single File Upload via Browser Modal
1. Open the NWIS dashboard in your browser (`http://127.0.0.1:5173`).
2. Click the yellow **`Ingest Reports`** button in the top navigation bar.
3. Switch to the **`Single File Upload`** tab.
4. Drag-and-drop or select any file from `test_upload_pack/` (e.g., `DDR_NHK_415_Severe_Mud_Loss_Tipam.pdf`).
5. Click **`Upload & Index Document`**.
6. The file will be parsed with PyMuPDF sliding-window chunking, vectorized, and stored in ChromaDB in real time!

### Method 2: Server-Side Batch Folder Ingestion
1. In the **`Ingest Reports`** modal, stay on the default **`Server Folder Ingestion`** tab.
2. In the folder path box, enter:
   ```
   test_upload_pack
   ```
3. Click **`Scan & Ingest Folder`**.
4. The backend will recursively scan all `.pdf`, `.csv`, `.xlsx`, and `.txt` files and ingest them asynchronously in batches of 10 with live progress tracking!

---

## 💬 Sample RAG Prompts to Test in the AI Assistant (Right Column)

Once you upload the files, test asking the following questions in the **WCR / DDR RAG Assistant** panel:

1. *"What caused the severe mud loss at 2,340m in Nahorkatiya-415 and what LCM pill was pumped?"*
   - **Expected Answer:** Details the 45 bbl loss in fractured Tipam Sandstone, pressure drop to 1,680 psi, and the 50 bbl pill containing walnut shells, coarse mica, and cellulosic fiber.
2. *"How was the high pressure gas kick killed in Baghjan-07?"*
   - **Expected Answer:** Explains the drilling break at 3,420m Barail Coal, SIDPP of 440 psi, SICP of 680 psi, and the Wait & Weight kill mud weighted up to 11.5 ppg barite.
3. *"What freeing pill recipe was used for differential sticking in Moran-92?"*
   - **Expected Answer:** Details the 45 bbl surfactant soak pill displaced across 2,870 - 2,900m and 110,000 lbs upward jarring.
4. *"What mud weight and polymer additives are recommended for Kopili Shale instability in Jorajan-18?"*
   - **Expected Answer:** Recommends raising mud density to 11.2 ppg with 1.5 lb/bbl PHPA polymer and >7% KCl.

---

> [!NOTE]
> All files in this folder are synthetic operational records modeled on Assam Basin stratigraphic and drilling patterns (Tipam Sandstone, Barail Coal-Shale, Kopili Shale) per SIH26121 guidelines. Actual Oil India operational data is not included.
