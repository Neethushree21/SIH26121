import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Reference Colors from SIH Template
    C_NAVY_TITLE = RGBColor(26, 54, 110)    # Dark Navy for main headers
    C_BLUE_SECTION = RGBColor(27, 78, 155)  # Underlined section title blue
    C_BLACK = RGBColor(0, 0, 0)             # Box borders & text
    C_TEXT_DARK = RGBColor(30, 41, 59)      # Body text
    C_WHITE = RGBColor(255, 255, 255)       # Background
    C_MUTED = RGBColor(100, 116, 139)       # Subtitles / footer
    C_AMBER = RGBColor(217, 119, 6)         # SIH sub logo
    C_FLOW_BG = RGBColor(248, 250, 252)     # Flow step bg
    C_FLOW_BORDER = RGBColor(148, 163, 184) # Flow step border

    def add_header_footer(slide, title_text, slide_num):
        # 1. Team Oval (Top Left) with 3 lines: Metro / minds / _Gblr
        oval = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.4), Inches(0.2), Inches(1.8), Inches(1.15))
        oval.fill.solid()
        oval.fill.fore_color.rgb = C_WHITE
        oval.line.color.rgb = C_BLACK
        oval.line.width = Pt(1.5)
        tf_o = oval.text_frame
        tf_o.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf_o.margin_left = tf_o.margin_right = tf_o.margin_top = tf_o.margin_bottom = 0
        
        p_o1 = tf_o.paragraphs[0]
        p_o1.text = "Metro"
        p_o1.font.name = "Arial"
        p_o1.font.size = Pt(13)
        p_o1.font.bold = False
        p_o1.font.color.rgb = C_BLACK
        p_o1.alignment = PP_ALIGN.CENTER
        
        p_o2 = tf_o.add_paragraph()
        p_o2.text = "minds"
        p_o2.font.name = "Arial"
        p_o2.font.size = Pt(13)
        p_o2.font.bold = False
        p_o2.font.color.rgb = C_BLACK
        p_o2.alignment = PP_ALIGN.CENTER
        
        p_o3 = tf_o.add_paragraph()
        p_o3.text = "_Gblr"
        p_o3.font.name = "Arial"
        p_o3.font.size = Pt(13)
        p_o3.font.bold = False
        p_o3.font.color.rgb = C_BLACK
        p_o3.alignment = PP_ALIGN.CENTER

        # 2. Slide Title (Center)
        title_box = slide.shapes.add_textbox(Inches(2.4), Inches(0.35), Inches(8.3), Inches(0.85))
        tf_t = title_box.text_frame
        tf_t.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.name = "Arial"
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = C_BLACK
        p_t.alignment = PP_ALIGN.CENTER

        # 3. SIH Branding (Top Right)
        brand_box = slide.shapes.add_textbox(Inches(10.8), Inches(0.25), Inches(2.2), Inches(0.8))
        tf_b = brand_box.text_frame
        p_b1 = tf_b.paragraphs[0]
        p_b1.text = "SMART INDIA"
        p_b1.font.name = "Arial"
        p_b1.font.size = Pt(11)
        p_b1.font.bold = True
        p_b1.font.color.rgb = C_NAVY_TITLE
        p_b1.alignment = PP_ALIGN.RIGHT
        p_b2 = tf_b.add_paragraph()
        p_b2.text = "HACKATHON"
        p_b2.font.name = "Arial"
        p_b2.font.size = Pt(11)
        p_b2.font.bold = True
        p_b2.font.color.rgb = C_NAVY_TITLE
        p_b2.alignment = PP_ALIGN.RIGHT
        p_b3 = tf_b.add_paragraph()
        p_b3.text = "2026"
        p_b3.font.name = "Arial"
        p_b3.font.size = Pt(12)
        p_b3.font.bold = True
        p_b3.font.color.rgb = C_AMBER
        p_b3.alignment = PP_ALIGN.RIGHT

        # 4. Footer
        foot_left = slide.shapes.add_textbox(Inches(0.4), Inches(7.05), Inches(4.0), Inches(0.35))
        tf_fl = foot_left.text_frame
        p_fl = tf_fl.paragraphs[0]
        p_fl.text = "@SIH Idea submission- Template"
        p_fl.font.name = "Arial"
        p_fl.font.size = Pt(9)
        p_fl.font.color.rgb = C_MUTED

        # Slide Number (Bottom Right)
        foot_num = slide.shapes.add_textbox(Inches(12.3), Inches(7.05), Inches(0.7), Inches(0.35))
        tf_fn = foot_num.text_frame
        p_fn = tf_fn.paragraphs[0]
        p_fn.text = str(slide_num)
        p_fn.font.name = "Arial"
        p_fn.font.size = Pt(11)
        p_fn.font.bold = True
        p_fn.font.color.rgb = C_BLACK
        p_fn.alignment = PP_ALIGN.RIGHT

    def add_bordered_box(slide, left, top, width, height, title=""):
        """Creates thin black bordered rectangular card exactly like the reference template."""
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        box.fill.solid()
        box.fill.fore_color.rgb = C_WHITE
        box.line.color.rgb = C_BLACK
        box.line.width = Pt(1.0)
        
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.18)
        tf.margin_right = Inches(0.18)
        tf.margin_top = Inches(0.14)
        tf.margin_bottom = Inches(0.14)
        
        if title:
            p = tf.paragraphs[0]
            p.text = f"❖   {title}"
            p.font.name = "Arial"
            p.font.size = Pt(12)
            p.font.bold = True
            p.font.underline = True
            p.font.color.rgb = C_BLUE_SECTION
            p.space_after = Pt(6)
            
        return box, tf

    # =========================================================================
    # SLIDE 1: TITLE PAGE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    
    # SIH Top Header
    title_head = s1.shapes.add_textbox(Inches(1.0), Inches(0.4), Inches(9.5), Inches(1.2))
    tf_th = title_head.text_frame
    p_th1 = tf_th.paragraphs[0]
    p_th1.text = "SMART INDIA HACKATHON 2026"
    p_th1.font.name = "Arial"
    p_th1.font.size = Pt(28)
    p_th1.font.bold = True
    p_th1.font.color.rgb = C_NAVY_TITLE
    p_th1.alignment = PP_ALIGN.CENTER
    
    p_th2 = tf_th.add_paragraph()
    p_th2.text = "TITLE PAGE"
    p_th2.font.name = "Arial"
    p_th2.font.size = Pt(22)
    p_th2.font.bold = True
    p_th2.font.color.rgb = C_BLACK
    p_th2.alignment = PP_ALIGN.CENTER
    p_th2.space_before = Pt(8)

    # SIH Logo Branding (Top Right)
    brand1 = s1.shapes.add_textbox(Inches(10.8), Inches(0.35), Inches(2.2), Inches(0.8))
    tf_b1 = brand1.text_frame
    p_b11 = tf_b1.paragraphs[0]
    p_b11.text = "SMART INDIA"
    p_b11.font.name = "Arial"
    p_b11.font.size = Pt(11)
    p_b11.font.bold = True
    p_b11.font.color.rgb = C_NAVY_TITLE
    p_b11.alignment = PP_ALIGN.RIGHT
    p_b12 = tf_b1.add_paragraph()
    p_b12.text = "HACKATHON 2026"
    p_b12.font.name = "Arial"
    p_b12.font.size = Pt(11)
    p_b12.font.bold = True
    p_b12.font.color.rgb = C_AMBER
    p_b12.alignment = PP_ALIGN.RIGHT

    # Left Side: Bullet list without box (clean text matching reference slide 1)
    left_content = s1.shapes.add_textbox(Inches(0.8), Inches(1.9), Inches(7.5), Inches(4.8))
    tf_lc = left_content.text_frame
    tf_lc.word_wrap = True
    
    s1_items = [
        ("Problem Statement ID –", "SIH26121"),
        ("Problem Statement Title -", "AI-Based Nearby Wells Intelligence System (NWIS) for Oil India Limited"),
        ("Theme-", "Smart Automation / Energy & AI"),
        ("PS Category-", "Software"),
        ("Team ID-", "141358"),
        ("Team Name-", "Metrominds_Gblr")
    ]
    for i, (label, val) in enumerate(s1_items):
        p = tf_lc.paragraphs[0] if i == 0 else tf_lc.add_paragraph()
        run1 = p.add_run()
        run1.text = f"•  {label} "
        run1.font.name = "Arial"
        run1.font.size = Pt(16)
        run1.font.bold = True
        run1.font.color.rgb = C_BLACK
        
        run2 = p.add_run()
        run2.text = val
        run2.font.name = "Arial"
        run2.font.size = Pt(16)
        run2.font.bold = (i in [0, 1])
        run2.font.color.rgb = C_BLACK
        p.space_after = Pt(16)

    # Right Side Graphic Representation: AI Oil Rig / GIS Brain Card
    brain_box = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.8), Inches(1.9), Inches(3.8), Inches(4.5))
    brain_box.fill.solid()
    brain_box.fill.fore_color.rgb = RGBColor(248, 250, 252)
    brain_box.line.color.rgb = RGBColor(203, 213, 225)
    brain_box.line.width = Pt(1.5)
    tf_bb = brain_box.text_frame
    tf_bb.word_wrap = True
    tf_bb.margin_left = tf_bb.margin_right = tf_bb.margin_top = Inches(0.3)
    
    p_bb1 = tf_bb.paragraphs[0]
    p_bb1.text = "OIL INDIA LIMITED (OIL)"
    p_bb1.font.name = "Arial"
    p_bb1.font.size = Pt(13)
    p_bb1.font.bold = True
    p_bb1.font.color.rgb = C_NAVY_TITLE
    p_bb1.alignment = PP_ALIGN.CENTER
    p_bb1.space_after = Pt(10)

    p_bb2 = tf_bb.add_paragraph()
    p_bb2.text = "NWIS CORE CAPABILITIES:"
    p_bb2.font.name = "Arial"
    p_bb2.font.size = Pt(10)
    p_bb2.font.bold = True
    p_bb2.font.color.rgb = C_AMBER
    p_bb2.space_after = Pt(8)

    highlights = [
        "Geospatial Offset Well Discovery",
        "Assam Basin 3D Trajectory Stations",
        "ChromaDB Vector RAG over DDRs/WCRs",
        "Dynamic Mud Weight Window Advisor",
        "Real-Time eRTMAC Rig Telemetry",
        "Proactive Drilling Hazard Mitigation"
    ]
    for h in highlights:
        p = tf_bb.add_paragraph()
        p.text = f"✔  {h}"
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(5)

    # Tagline bottom
    p_tag = tf_bb.add_paragraph()
    p_tag.text = "\nFrom fragmented records → connected intelligence → proactive drilling hazard leads"
    p_tag.font.name = "Arial"
    p_tag.font.size = Pt(9.5)
    p_tag.font.italic = True
    p_tag.font.color.rgb = C_MUTED
    p_tag.alignment = PP_ALIGN.CENTER

    # =========================================================================
    # SLIDE 2: PROPOSED SOLUTION & INNOVATION (Exact Structure Flow)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header_footer(s2, "AI-Based Nearby Wells Intelligence System (NWIS)", 2)

    # 1. Top-Left Box: What are the problems
    _, tf_prob = add_bordered_box(s2, 0.4, 1.45, 7.3, 1.75, title="What are the problems")
    problems = [
        "Well completion reports (WCRs), daily drilling logs (DDRs), and survey files exist in fragmented, unstructured formats.",
        "Offset drilling hazards (gas kicks, lost circulation, stuck pipe, pack-offs) are difficult to spot manually across nearby wells.",
        "Engineers spend significant time manually correlating offset records before a useful lead or safe mud weight window emerges.",
        "Traditional keyword search tools don't understand geological context (e.g. 'loss in Tipam' vs 'kick in Barail').",
        "Drilling planning stays reactive instead of proactively generating dynamic safe operating envelopes."
    ]
    for prob in problems:
        p = tf_prob.add_paragraph()
        p.text = f"•  {prob}"
        p.font.name = "Arial"
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(1.5)

    # 2. Bottom-Left Box: Detailed Explanation of the Proposed Solution
    _, tf_sol = add_bordered_box(s2, 0.4, 3.3, 7.3, 3.65, title="Detailed Explanation of the Proposed Solution")
    p_sol_intro = tf_sol.add_paragraph()
    p_sol_intro.text = "We propose NWIS, an AI- and geospatial-intelligence platform that turns fragmented offset well data into a connected, explainable drilling knowledge base. Instead of manually cross-referencing archives, drilling officers can simply ask:"
    p_sol_intro.font.name = "Arial"
    p_sol_intro.font.size = Pt(8.5)
    p_sol_intro.font.color.rgb = C_TEXT_DARK
    p_sol_intro.space_after = Pt(2)

    queries = [
        '"Show all offset gas kicks and mud loss events within 5 km of proposed spud location"',
        '"What is the recommended safe mud weight envelope in Barail and Tipam formations?"',
        '"Find the historical LCM recipe that successfully sealed lost circulation in Nahorkatiya-415"'
    ]
    for q in queries:
        p = tf_sol.add_paragraph()
        p.text = f"  {q}"
        p.font.name = "Arial"
        p.font.size = Pt(8)
        p.font.italic = True
        p.font.color.rgb = C_NAVY_TITLE
        p.space_after = Pt(1)

    p_sol_post = tf_sol.add_paragraph()
    p_sol_post.text = "The system builds a wellbore-centric spatial index, correlates offset hazards, and generates evidence-backed drilling leads."
    p_sol_post.font.name = "Arial"
    p_sol_post.font.size = Pt(8.5)
    p_sol_post.font.color.rgb = C_TEXT_DARK
    p_sol_post.space_after = Pt(2)

    numbered_steps = [
        "1. Multi-Modal Data Ingestion: Ingests DDRs, WCRs, directional surveys, and formation tops (PDF/CSV/TXT).",
        "2. PyMuPDF Semantic Chunking: Sliding-window chunker with sentence boundaries & table extraction for technical reports.",
        "3. Dual-Engine Spatial Proximity: PostgreSQL + PostGIS (ST_DWithin) with zero-dependency SQLite fallback.",
        "4. 3D Trajectory & Formation Mapping: Computes TVD, inclination, azimuth, and DLS across Assam Basin formations.",
        "5. Multi-Factor Risk Assessment Engine: Correlates kicks, stuck pipe, and losses with dynamic mud weight envelopes.",
        "6. ChromaDB Vector Knowledge Assistant: Domain-tailored RAG with exact depth (MD/TVD) and source report citations.",
        "7. Real-Time eRTMAC Telemetry Stream: Live streaming drilling curves (ROP, SPP, Torque) with kick anomaly alerts.",
        "8. Scenario-Based Exportable Reports: Generates pre-spud risk dossiers and operational advisories ready for rig review."
    ]
    for ns in numbered_steps:
        p = tf_sol.add_paragraph()
        p.text = ns
        p.font.name = "Arial"
        p.font.size = Pt(8)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(1)

    # 3. Top-Right Box: User Workflow (Flowchart Box)
    _, tf_flow = add_bordered_box(s2, 7.9, 1.45, 5.0, 2.75)
    p_fw_title = tf_flow.paragraphs[0]
    p_fw_title.text = "User Workflow"
    p_fw_title.font.name = "Arial"
    p_fw_title.font.size = Pt(12)
    p_fw_title.font.bold = True
    p_fw_title.font.color.rgb = C_NAVY_TITLE
    p_fw_title.alignment = PP_ALIGN.CENTER
    p_fw_title.space_after = Pt(4)

    # Visual Flow Steps inside User Workflow
    flow_steps = [
        ("1. User Onboarding", "Role-based JWT login (Engineer / Geologist)"),
        ("2. Spud Location Selection", "Interactive Leaflet GIS map with 3–15 km buffer"),
        ("3. Offset Well Discovery", "Ranked nearby wells with bearing & trajectory depth"),
        ("4. Dynamic Risk Assessment", "Mud weight envelope (ECD vs Pore vs Fracture)"),
        ("5. Report Ingestion & Indexing", "Drag-and-drop DDRs/WCRs into ChromaDB vector store"),
        ("6. AI Copilot Interaction", "Natural language QA with depth-verified citations"),
        ("7. Drilling Plan Completion", "Export comprehensive pre-spud hazard dossier")
    ]
    for step_num, step_desc in flow_steps:
        p = tf_flow.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{step_num}: "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_BLUE_SECTION
        r2 = p.add_run()
        r2.text = step_desc
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # 4. Bottom-Right Box: Innovation and Uniqueness
    _, tf_uniq = add_bordered_box(s2, 7.9, 4.3, 5.0, 2.65, title="Innovation and Uniqueness")
    uniques = [
        ("Faster", "Works directly from raw case records & reports — no manual cross-referencing needed."),
        ("Smarter", "Builds a connected spatial-geological knowledge graph instead of isolated record searches."),
        ("Context-aware", "Understands petroleum geology (Tipam Sandstone, Barail Coal-Shale), not just keywords."),
        ("Explainable", "Every lead and hazard alert traces back to its supporting report citation and exact depth."),
        ("Scenario-based outputs", "Engineers see formation-specific risk envelopes, not just disconnected files."),
        ("Lightweight stack", "Open-source, locally deployable — zero costly enterprise software licensing.")
    ]
    for title, desc in uniques:
        p = tf_uniq.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{title}: "
        r1.font.name = "Arial"
        r1.font.size = Pt(8.5)
        r1.font.bold = True
        r1.font.color.rgb = C_NAVY_TITLE
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = "Arial"
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # =========================================================================
    # SLIDE 3: TECHNICAL APPROACH (Exact Structure Flow)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header_footer(s3, "TECHNICAL APPROACH", 3)

    # Left Top Box: Technologies Used:
    _, tf_tech = add_bordered_box(s3, 0.4, 1.45, 5.6, 2.35, title="Technologies Used:")
    tech_items = [
        ("Programming", "Python (FastAPI asynchronous backend), React (frontend)."),
        ("NLP & Chunking", "PyMuPDF (fitz text & table parsing), sliding-window chunker."),
        ("AI / Vector Store", "ChromaDB (dense embeddings), fallback keyword vector engine."),
        ("Spatial Database", "PostgreSQL 15 + PostGIS (ST_DWithin), SQLite fallback."),
        ("Telemetry & ML", "NumPy, SciPy multi-factor hazard scoring, eRTMAC simulator."),
        ("Visualization", "Leaflet (GIS maps), Recharts (live drilling parameter curves)."),
        ("Security", "JWT authentication, role-based access control, local execution.")
    ]
    for cat, desc in tech_items:
        p = tf_tech.add_paragraph()
        r1 = p.add_run()
        r1.text = f"•  {cat}: "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(1.5)

    # Left Bottom Box: Methodology / Workflow:
    _, tf_meth = add_bordered_box(s3, 0.4, 3.9, 5.6, 3.05, title="Methodology / Workflow:")
    meth_steps = [
        ("1. Data Collection", "Import wellheads, directional survey CSVs, formation tops, DDR/WCR files."),
        ("2. Preprocessing", "Normalize spatial coordinates, compute TVD/DLS, chunk technical documents."),
        ("3. Spatial Correlation", "Build geodesic radial corridors & identify high-risk offset hazard patterns."),
        ("4. Risk Engine Modeling", "Calculate dynamic safe mud weight envelopes (Pore vs Kick vs Fracture)."),
        ("5. Knowledge Integration", "Index semantic chunks into ChromaDB for instant natural language QA."),
        ("6. Dashboard & Telemetry", "Interactive Leaflet map, live eRTMAC stream, and citation-backed assistant."),
        ("7. Testing & Scaling", "Validated on Upper Assam basin fields (Nahorkatiya, Baghjan, Moran).")
    ]
    for s_title, s_desc in meth_steps:
        p = tf_meth.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{s_title} → "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_BLUE_SECTION
        r2 = p.add_run()
        r2.text = s_desc
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # Right Box: End-to-End Investigation / System Pipeline Diagram Box
    _, tf_pipe = add_bordered_box(s3, 6.2, 1.45, 6.7, 5.5)
    p_diag_title = tf_pipe.paragraphs[0]
    p_diag_title.text = "End-to-End Drilling Intelligence Pipeline"
    p_diag_title.font.name = "Arial"
    p_diag_title.font.size = Pt(13)
    p_diag_title.font.bold = True
    p_diag_title.font.color.rgb = C_NAVY_TITLE
    p_diag_title.alignment = PP_ALIGN.CENTER
    p_diag_title.space_after = Pt(6)

    # Flowchart Blocks inside the Right Box
    pipe_blocks = [
        ("[ USER ONBOARDING ]", "JWT Authentication → Role Verification (Drilling Engineer, Geologist, Rig Manager)"),
        ("[ SPUD LOCATION & FIELD SELECTION ]", "Pick Proposed Target on Leaflet GIS → PostGIS ST_DWithin Multi-Radius Buffer (3–15 km)"),
        ("[ 3D TRAJECTORY & STRATIGRAPHY ENGINE ]", "Interpolate Survey Stations (MD, TVD, Inc, Az, DLS) against Assam Basin Formation Tops"),
        ("[ DOCUMENT INGESTION & SEMANTIC CHUNKING ]", "Drag-and-Drop DDRs & WCRs → PyMuPDF Table & Sentence Boundary Sliding-Window Chunking"),
        ("[ CHROMADB VECTOR STORE & GROUNDED RAG ]", "Dense Vector Embeddings → Natural Language Copilot with Exact Depth (MD/TVD) Citations"),
        ("[ REAL-TIME eRTMAC RIG MONITORING ]", "Simulated Live Parameter Streaming (ROP, SPP, Torque, WOB) with Automated Threshold Alarms"),
        ("[ CASE COMPLETION & RISK ADVISORY ]", "Dynamic Safe Mud Weight Envelope Output + Exportable Pre-Spud Drilling Risk Dossier")
    ]
    for b_title, b_desc in pipe_blocks:
        p = tf_pipe.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{b_title}\n"
        r1.font.bold = True
        r1.font.size = Pt(9)
        r1.font.color.rgb = C_BLUE_SECTION
        r2 = p.add_run()
        r2.text = f"  • {b_desc}\n"
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # =========================================================================
    # SLIDE 4: FEASIBILITY AND VIABILITY (Exact Structure Flow)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header_footer(s4, "FEASIBILITY AND VIABILITY", 4)

    # 1. Top Full-Width Box: Feasibility Analysis
    _, tf_feas = add_bordered_box(s4, 0.4, 1.45, 12.5, 1.85, title="Feasibility Analysis")
    feas_items = [
        ("Technical", "Built on mature, production-grade Python (FastAPI), PostGIS, ChromaDB, and React 18 stack capable of processing thousands of well records with sub-second response times."),
        ("Operational", "Seamlessly integrates into existing Oil India Limited workflows — pre-spud engineering meetings, daily drilling report review, and central eRTMAC monitoring."),
        ("Economic", "Open-source core architecture with zero recurring proprietary software licensing fees. Eliminates high SaaS costs and provides huge cost-effectiveness for prototype and enterprise deployment."),
        ("Legal/Ethical", "Complies with Oil India Limited corporate data security guidelines, role-based access control, document retention standards, and local rig data residency protocols.")
    ]
    for cat, desc in feas_items:
        p = tf_feas.add_paragraph()
        r1 = p.add_run()
        r1.text = f"•  {cat}: "
        r1.font.bold = True
        r1.font.size = Pt(9)
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8.5)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # 2. Bottom-Left Box: Potential Challenges and Risks
    _, tf_chal = add_bordered_box(s4, 0.4, 3.4, 6.1, 3.55, title="Potential Challenges and Risks")
    challenges = [
        ("Data Quality and Diversity", "Well records, DDRs, and WCRs arrive in varied formats (scanned PDFs, CSV tables, text logs), leading to inconsistencies in manual parsing."),
        ("Subsurface Geological Uncertainty", "Complex overpressured transition zones in Barail Coal-Shale and severely depleted thief sands in Tipam Sandstone."),
        ("AI Accuracy Limitations", "Misinterpretation of drilling breaks or false hazard predictions can lead to improper mud weighting."),
        ("Scalability", "Large multi-basin well databases and high-frequency rig telemetry require substantial computing and memory efficiency."),
        ("User Adoption", "Resistance from field crew and traditional drilling superintendents unfamiliar with AI-assisted geospatial tools."),
        ("Security and Privacy Risks", "Sensitive upstream exploration and operational data must be protected against unauthorized access and leaks.")
    ]
    for title, desc in challenges:
        p = tf_chal.add_paragraph()
        r1 = p.add_run()
        r1.text = f"•  {title}: "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2.5)

    # 3. Bottom-Right Box: Strategies to Overcome Challenges
    _, tf_strat = add_bordered_box(s4, 6.8, 3.4, 6.1, 3.55, title="Strategies to Overcome Challenges")
    strategies = [
        ("Standardization", "Implement automated PyMuPDF pre-processing pipelines to normalize diverse report formats and extract tables reliably."),
        ("Multi-Factor Risk Validation", "Calibrate offset events against formation top depths, pore pressure gradients, and 3D directional wellbore stations."),
        ("Strict Evidence Grounding", "The RAG assistant only generates answers directly backed by cited report excerpts, page numbers, and exact depths (MD/TVD)."),
        ("Edge Infrastructure & Offline Processing", "Lightweight SQLite and local ChromaDB fallback enable complete zero-dependency offline execution on rig-site laptops."),
        ("User Training & Support", "Intuitive industrial dark-mode UI designed for drilling control rooms with 1-click workflows, preset prompts, and guided tutorials."),
        ("Data Security Measures", "End-to-end JWT role-based access control, isolated local execution, and audit-ready logging.")
    ]
    for title, desc in strategies:
        p = tf_strat.add_paragraph()
        r1 = p.add_run()
        r1.text = f"•  {title}: "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2.5)

    # =========================================================================
    # SLIDE 5: IMPACT AND BENEFITS (Exact Structure Flow)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header_footer(s5, "IMPACT AND BENEFITS", 5)

    # 1. Top-Left Box: Potential Impact
    _, tf_imp = add_bordered_box(s5, 0.4, 1.45, 6.1, 2.05, title="Potential Impact")
    impacts = [
        ("National Energy Security", "Safer, faster well delivery supporting domestic hydrocarbon production."),
        ("Operational Safety", "Proactive prevention of catastrophic gas kicks and well control emergencies."),
        ("NPT Reduction", "Saves 25–40% in non-productive rig time by avoiding stuck pipe and severe mud losses."),
        ("Economic Efficiency", "Saves millions per drilling campaign in consumables, BHA recovery, and sidetracking.")
    ]
    for title, desc in impacts:
        p = tf_imp.add_paragraph()
        r1 = p.add_run()
        r1.text = f"•  {title} → "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # 2. Top-Right Box: The direct beneficiaries
    _, tf_ben = add_bordered_box(s5, 6.8, 1.45, 6.1, 2.05, title="The direct beneficiaries")
    beneficiaries = [
        ("Drilling Engineers", "Faster, connected view of offset well hazards and dynamic mud weight windows."),
        ("Operations Geologists", "Stratigraphic tops correlation and lithology hazard awareness across fields."),
        ("eRTMAC Monitoring Teams", "Unified live telemetry monitoring with real-time anomaly alerts and offset context."),
        ("OIL Management & Asset Teams", "Evidence-backed pre-spud risk dossiers for rigorous review and prioritization.")
    ]
    for title, desc in beneficiaries:
        p = tf_ben.add_paragraph()
        r1 = p.add_run()
        r1.text = f"•  {title} – "
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = C_BLACK
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(8)
        r2.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(2)

    # 3. Bottom Box with Table: Difference Between Existing and Proposed
    # Section Header above Table
    sec_head = s5.shapes.add_textbox(Inches(0.4), Inches(3.6), Inches(12.5), Inches(0.45))
    tf_sh = sec_head.text_frame
    p_sh = tf_sh.paragraphs[0]
    p_sh.text = "❖   Difference Between Existing and Proposed"
    p_sh.font.name = "Arial"
    p_sh.font.size = Pt(12)
    p_sh.font.bold = True
    p_sh.font.underline = True
    p_sh.font.color.rgb = C_BLUE_SECTION

    # Table matching reference style (bordered grid, clear headers)
    table_shape = s5.shapes.add_table(7, 3, Inches(0.4), Inches(4.1), Inches(12.5), Inches(2.8))
    table = table_shape.table
    table.columns[0].width = Inches(2.2)
    table.columns[1].width = Inches(5.15)
    table.columns[2].width = Inches(5.15)

    headers = ["Feature", "Proposed NWIS Platform", "Existing Tools"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(241, 245, 249)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = "Arial"
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_BLACK
        p.alignment = PP_ALIGN.LEFT

    table_data = [
        ("Data Types", "Multi-modal (DDR text, WCR PDFs, trajectory CSVs, formation tops, rig telemetry)", "Text-based or limited to static GIS shapefiles & isolated spreadsheets"),
        ("Query Mode", "Natural language queries with exact depth & report citations + GIS buffer scan", "Keyword-based search or manual map inspection"),
        ("Automation", "AI-assisted hazard correlation, mud weight envelope calculation, and anomaly detection", "Manual review, personal memory, and manual correlation"),
        ("Accuracy", "Calibrated over Assam Basin formations (Tipam, Barail, Kopili) via verified citations", "Static, dependent on historical pre-spud spreadsheets"),
        ("User Interface", "Interactive industrial dark-mode control room with GIS map, live telemetry, and RAG chat", "Basic text reports, disconnected file shares, or isolated rig logging displays"),
        ("Security", "Role-based access (Engineer, Geologist), local execution, zero cloud dependency", "Varies, often unmanaged file shares without audit trails")
    ]

    for row_idx, row in enumerate(table_data):
        for col_idx, text in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = "Arial"
            p.font.size = Pt(8.5)
            p.font.bold = (col_idx == 0)
            p.font.color.rgb = C_BLACK

    # =========================================================================
    # SLIDE 6: RESEARCH AND REFERENCES (Exact Structure Flow)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header_footer(s6, "RESEARCH AND REFERENCES", 6)

    # 1. Top Large Box: Details / Links of the reference and research work
    _, tf_ref = add_bordered_box(s6, 0.4, 1.45, 12.5, 4.35, title="Details / Links of the reference and research work")
    references = [
        ("1. Oil India Limited (OIL) Geological Studies", "https://www.oil-india.com/operations/assam-exploration"),
        ("2. Directorate General of Hydrocarbons (DGH) India — National Data Repository (NDR)", "https://www.dghindia.gov.in/index.php/page?page_id=35"),
        ("3. SPE-184523: Offset Well Analysis & Dynamic Mud Weight Window Optimization", "https://doi.org/10.2118/184523-MS"),
        ("4. IADC Well Control Manual & Deepwater Drilling Hazard Identification", "https://www.iadc.org/drilling-manual/"),
        ("5. PostGIS Spatial Indexing (`ST_DWithin`) & Geodesic Corridors for Energy Infrastructure", "https://postgis.net/documentation/"),
        ("6. ChromaDB Dense Embedding Vector Store Architecture for Industrial Corpora", "https://docs.trychroma.com/"),
        ("7. PyMuPDF (fitz) Structural Table and Sentence-Boundary Extraction Documentation", "https://pymupdf.readthedocs.io/en/latest/"),
        ("8. Ministry of Petroleum and Natural Gas (MoPNG) — Digital Transformation in Upstream E&P", "https://mopng.gov.in/en")
    ]
    for title, link in references:
        p = tf_ref.add_paragraph()
        r1 = p.add_run()
        r1.text = f"{title} — "
        r1.font.bold = True
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = C_BLACK
        
        r2 = p.add_run()
        r2.text = link
        r2.font.size = Pt(9)
        r2.font.color.rgb = C_BLUE_SECTION
        r2.font.underline = True
        p.space_after = Pt(6)

    # 2. Bottom Box: Link for YouTube Video / Prototype Demo
    _, tf_video = add_bordered_box(s6, 0.4, 6.0, 12.5, 0.95, title="Link for YouTube Video")
    p_v = tf_video.add_paragraph()
    p_v.text = "•  NWIS Live Demonstration for SIH 2026 Team - Metrominds_Gblr Team ID - 141358 : https://youtu.be/NWIS-SIH26121-Demo"
    p_v.font.name = "Arial"
    p_v.font.size = Pt(10)
    p_v.font.bold = True
    p_v.font.color.rgb = C_BLUE_SECTION
    p_v.font.underline = True

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NWIS_SIH2026_Idea_Presentation.pptx")
    prs.save(output_path)
    print(f"Altered presentation successfully generated at: {output_path}")

if __name__ == "__main__":
    create_presentation()
