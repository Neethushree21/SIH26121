import os
import re
import uuid
import glob
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.document import IngestedDocument
from app.models.well import Well
from app.services.vector_store import vector_store_service

logger = logging.getLogger(__name__)

# Global in-memory task status tracker for asynchronous folder ingestion
INGESTION_TASKS: Dict[str, Dict[str, Any]] = {}

class SemanticChunker:
    """
    Sentence-boundary aware sliding-window text chunker.
    Extracts text chunks with overlap without breaking mid-sentence.
    """
    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        # Regex to split text at sentence boundaries while preserving ending punctuation
        sentence_endings = re.compile(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\n])')
        sentences = sentence_endings.split(text.strip())
        return [s.strip() for s in sentences if s.strip()]

    @classmethod
    def sliding_window_chunk(
        cls,
        text: str,
        target_chunk_chars: int = 750,
        overlap_sentences: int = 1
    ) -> List[str]:
        sentences = cls.split_into_sentences(text)
        if not sentences:
            return []

        chunks = []
        current_chunk: List[str] = []
        current_length = 0

        for sentence in sentences:
            sent_len = len(sentence)
            if current_length + sent_len > target_chunk_chars and current_chunk:
                chunks.append(" ".join(current_chunk))
                # Retain overlap sentences for sliding window
                current_chunk = current_chunk[-overlap_sentences:] if overlap_sentences > 0 else []
                current_length = sum(len(s) for s in current_chunk) + len(current_chunk)

            current_chunk.append(sentence)
            current_length += sent_len + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


class IngestionService:
    @staticmethod
    def parse_pdf_pymupdf(file_path: str) -> List[Dict[str, Any]]:
        """
        Extracts text and tables page-by-page using PyMuPDF.
        Returns a list of dicts: [{"page_number": int, "text": str}]
        """
        pages_content = []
        try:
            import pymupdf
            doc = pymupdf.open(file_path)
            for page_idx, page in enumerate(doc):
                text = page.get_text("text") or ""
                # Attempt to extract table data if available in PyMuPDF
                try:
                    tables = page.find_tables()
                    if tables and tables.tables:
                        for tbl in tables.tables:
                            text += "\n[Extracted Table Data]:\n" + str(tbl.extract())
                except Exception:
                    pass

                if text.strip():
                    pages_content.append({
                        "page_number": page_idx + 1,
                        "text": text.strip()
                    })
            doc.close()
        except Exception as e:
            logger.error(f"PyMuPDF error parsing {file_path}: {e}")
            # Fallback to simple read if pdf failed
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    t = page.extract_text()
                    if t:
                        pages_content.append({"page_number": i + 1, "text": t.strip()})
            except Exception as e2:
                logger.error(f"Fallback PDF parsing failed for {file_path}: {e2}")
        return pages_content

    @staticmethod
    def parse_tabular_file(file_path: str) -> List[Dict[str, Any]]:
        """Parses CSV or Excel (.xlsx) files into markdown table formatted text."""
        import pandas as pd
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            text_chunks = []
            # Split dataframe into slices of 15 rows for readable text chunks
            chunk_size = 15
            for i in range(0, len(df), chunk_size):
                sub_df = df.iloc[i:i + chunk_size]
                chunk_str = f"Tabular Data ({os.path.basename(file_path)}, rows {i+1} to {min(i+chunk_size, len(df))}):\n"
                chunk_str += sub_df.to_string(index=False)
                text_chunks.append({"page_number": (i // chunk_size) + 1, "text": chunk_str})
            return text_chunks
        except Exception as e:
            logger.error(f"Failed to parse tabular file {file_path}: {e}")
            return []

    @staticmethod
    def extract_hierarchy_metadata(file_path: str) -> Dict[str, str]:
        """
        Preserves folder hierarchy like /Field/Well/Reports.
        Derives field_name, well_name, formation_tag, and event_type.
        """
        norm_path = os.path.normpath(file_path).replace("\\", "/")
        parts = [p for p in norm_path.split("/") if p]
        
        field_name = "Assam Shelf"
        well_name = "General OIL Well"
        formation_tag = "Barail / Tipam"
        event_type = "Routine Drilling Operation"
        depth_range = "Variable Depth"

        # Check path elements for known fields
        for part in parts:
            p_up = part.upper()
            if "NAHORKATIYA" in p_up or "NHK" in p_up:
                field_name = "Nahorkatiya"
                well_name = "Nahorkatiya-412" if "412" in p_up else "Nahorkatiya Field Well"
            elif "BAGHJAN" in p_up or "BGH" in p_up:
                field_name = "Baghjan"
                well_name = "Baghjan-03" if "03" in p_up or "3" in p_up else "Baghjan Field Well"
            elif "MORAN" in p_up or "MOR" in p_up:
                field_name = "Moran"
                well_name = "Moran-88" if "88" in p_up else "Moran Field Well"
            elif "JORAJAN" in p_up or "JRN" in p_up:
                field_name = "Jorajan"
                well_name = "Jorajan-15" if "15" in p_up else "Jorajan Field Well"
            elif "DIGBOI" in p_up or "DGB" in p_up:
                field_name = "Digboi"
                well_name = "Digboi-101" if "101" in p_up else "Digboi Field Well"

        return {
            "field_name": field_name,
            "well_name": well_name,
            "formation_tag": formation_tag,
            "event_type": event_type,
            "depth_range": depth_range
        }

    @staticmethod
    def detect_formation_and_events(text: str) -> Dict[str, str]:
        """Scans chunk text for formation tops and drilling event categories."""
        upper = text.upper()
        formation = "Barail / Tipam Sequence"
        if "BARAIL COAL" in upper or "COAL-SHALE" in upper:
            formation = "Barail Coal-Shale"
        elif "BARAIL MAIN" in upper or "BMS" in upper or "FIRST SAND" in upper:
            formation = "Barail Main Sand"
        elif "TIPAM" in upper:
            formation = "Tipam Sandstone"
        elif "GIRUJAN" in upper:
            formation = "Girujan Clay"
        elif "KOPILI" in upper:
            formation = "Kopili Formation"

        event = "Routine Drilling Operation"
        if "KICK" in upper or "SIDPP" in upper or "SICP" in upper or "INFLUX" in upper:
            event = "Gas Kick / Influx"
        elif "LOSS" in upper or "LCM" in upper or "LOST CIRCULATION" in upper:
            event = "Loss of Circulation"
        elif "STUCK" in upper or "OVERPULL" in upper or "JARRING" in upper or "DIFFERENTIAL" in upper:
            event = "Stuck Pipe Incident"
        elif "COLLAPSE" in upper or "CAVING" in upper or "PACK-OFF" in upper or "PACK OFF" in upper:
            event = "Wellbore Collapse / Tight Hole"

        # Depth range detection
        depth_match = re.search(r'(\d{1,2}[,\.]\d{3}\s*m|\b\d{3,4}\s*m\b)', text, re.IGNORECASE)
        depth_range = depth_match.group(0) if depth_match else "Interval Profile"

        return {
            "formation_tag": formation,
            "event_type": event,
            "depth_range": depth_range
        }

    @classmethod
    def ingest_single_file(cls, db: Session, file_path: str) -> Dict[str, Any]:
        """
        Parses a single file (.pdf, .csv, .xlsx, .txt), performs semantic sliding-window chunking,
        attaches rich metadata, and upserts into ChromaDB.
        """
        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        path_meta = cls.extract_hierarchy_metadata(file_path)

        pages_data = []
        if ext == ".pdf":
            pages_data = cls.parse_pdf_pymupdf(file_path)
        elif ext in [".csv", ".xlsx", ".xls"]:
            pages_data = cls.parse_tabular_file(file_path)
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                pages_data = [{"page_number": 1, "text": content}]
            except Exception as e:
                logger.error(f"Error reading text file {file_path}: {e}")

        if not pages_data:
            pages_data = [{"page_number": 1, "text": f"Technical operational drilling report: {filename}"}]

        # Match well in database to get well_id
        well = db.query(Well).filter(Well.name.ilike(f"%{path_meta['well_name']}%")).first()
        well_id = well.id if well else "OIL-GEN-WELL"

        vector_chunks = []
        total_chunks = 0

        for p in pages_data:
            page_no = p["page_number"]
            page_text = p["text"]
            # Apply semantic sliding-window chunker
            chunks = SemanticChunker.sliding_window_chunk(page_text, target_chunk_chars=800, overlap_sentences=1)
            
            for chunk_idx, chunk in enumerate(chunks):
                text_meta = cls.detect_formation_and_events(chunk)
                chunk_id = f"{filename}_p{page_no}_c{chunk_idx}_{uuid.uuid4().hex[:6]}"
                
                vector_chunks.append({
                    "id": chunk_id,
                    "text": chunk,
                    "metadata": {
                        "well_id": str(well_id),
                        "file_name": filename,
                        "page_number": page_no,
                        "depth_range": text_meta["depth_range"],
                        "formation_tag": text_meta["formation_tag"],
                        "event_type": text_meta["event_type"],
                        "field_name": path_meta["field_name"],
                        "well_name": path_meta["well_name"]
                    }
                })
                total_chunks += 1

        # Bulk upsert into vector store
        if vector_chunks:
            vector_store_service.add_documents(vector_chunks)

        # Record in database
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        doc_record = IngestedDocument(
            filename=filename,
            file_type=ext.replace(".", "").upper() or "TXT",
            file_size_bytes=file_size,
            well_name=path_meta["well_name"],
            chunk_count=total_chunks,
            status="INDEXED"
        )
        db.add(doc_record)
        db.commit()
        db.refresh(doc_record)

        return {
            "document_id": doc_record.id,
            "filename": filename,
            "chunks_count": total_chunks,
            "well_name": path_meta["well_name"],
            "field_name": path_meta["field_name"]
        }

    @classmethod
    def process_folder_batch_async(cls, task_id: str, folder_path: str, db_session_factory):
        """
        Background task: recursively scans directory for .pdf, .csv, .xlsx, .txt
        and processes files in batches of 10.
        """
        task = INGESTION_TASKS.get(task_id)
        if not task:
            return

        task["status"] = "SCANNING"
        supported_extensions = ["*.pdf", "*.csv", "*.xlsx", "*.xls", "*.txt"]
        all_files = []

        for ext in supported_extensions:
            pattern = os.path.join(folder_path, "**", ext)
            all_files.extend(glob.glob(pattern, recursive=True))

        all_files = list(set(all_files))
        task["total_files"] = len(all_files)
        task["status"] = "PROCESSING"
        task["total_batches"] = (len(all_files) + 9) // 10 if all_files else 0

        batch_size = 10
        total_indexed_chunks = 0

        db = db_session_factory()
        try:
            for b_idx in range(0, len(all_files), batch_size):
                batch_files = all_files[b_idx:b_idx + batch_size]
                task["current_batch"] = (b_idx // batch_size) + 1

                for file_path in batch_files:
                    try:
                        res = cls.ingest_single_file(db, file_path)
                        total_indexed_chunks += res["chunks_count"]
                        task["processed_files"] += 1
                        task["processed_file_names"].append(res["filename"])
                        task["indexed_chunks"] = total_indexed_chunks
                    except Exception as err:
                        logger.error(f"Error processing {file_path} in batch {task['current_batch']}: {err}")
                        task["errors"].append({"file": os.path.basename(file_path), "error": str(err)})

            task["status"] = "COMPLETED"
            task["completion_time"] = datetime.utcnow().isoformat()
        except Exception as e:
            task["status"] = "FAILED"
            task["error_message"] = str(e)
            logger.error(f"Folder ingestion task {task_id} failed: {e}")
        finally:
            db.close()

ingestion_service = IngestionService()
