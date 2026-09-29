import os
import json
import logging
import math
import re
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class SimpleEmbeddingEngine:
    """Lightweight token & keyword-frequency vectorizer for fast fallback search."""
    @staticmethod
    def tokenize(text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())

    @staticmethod
    def text_to_vector(text: str, vocab: Dict[str, int]) -> List[float]:
        tokens = SimpleEmbeddingEngine.tokenize(text)
        vec = [0.0] * len(vocab)
        for token in tokens:
            if token in vocab:
                vec[vocab[token]] += 1.0
        # Normalize
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        return sum(a * b for a, b in zip(v1, v2))


class VectorStoreService:
    def __init__(self):
        self.client = None
        self.collection = None
        self.use_fallback = False
        self.fallback_docs: List[Dict[str, Any]] = []
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
            self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            self.collection = self.client.get_or_create_collection(
                name="oil_reports_rag",
                metadata={"description": "OIL WCRs and DDRs Drilling Intelligence"}
            )
            logger.info("ChromaDB vector store connected successfully.")
        except Exception as e:
            logger.warning(f"ChromaDB native initialization warning ({e}). Initializing high-speed persistent fallback vector index.")
            self.use_fallback = True
            self._load_fallback_index()

    def _get_fallback_file(self) -> str:
        return os.path.join(settings.CHROMA_PERSIST_DIR, "fallback_vectors.json")

    def _load_fallback_index(self):
        path = self._get_fallback_file()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.fallback_docs = json.load(f)
            except Exception:
                self.fallback_docs = []

    def _save_fallback_index(self):
        path = self._get_fallback_file()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.fallback_docs, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save fallback index: {e}")

    def add_documents(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Chunks is a list of dicts:
        {
          "id": str,
          "text": str,
          "metadata": {
             "document_name": str,
             "well_name": str,
             "formation": str,
             "depth_interval": str
          }
        }
        """
        if not chunks:
            return 0

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c.get("metadata", {}) for c in chunks]

        if not self.use_fallback and self.collection is not None:
            try:
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                return len(chunks)
            except Exception as e:
                logger.error(f"Chroma add error: {e}, falling back.")
                self.use_fallback = True

        # Fallback storage
        for c in chunks:
            self.fallback_docs.append({
                "id": c["id"],
                "text": c["text"],
                "metadata": c.get("metadata", {})
            })
        self._save_fallback_index()
        return len(chunks)

    def delete_document(self, filename: str) -> int:
        """Deletes all chunks associated with a given filename from ChromaDB and fallback index."""
        deleted_count = 0
        if not self.use_fallback and self.collection is not None:
            try:
                results = self.collection.get()
                matched_ids = []
                if results and "ids" in results and "metadatas" in results:
                    for cid, meta in zip(results["ids"], results["metadatas"]):
                        fname = meta.get("file_name") or meta.get("document_name")
                        if fname == filename:
                            matched_ids.append(cid)
                if matched_ids:
                    self.collection.delete(ids=matched_ids)
                    deleted_count += len(matched_ids)
            except Exception as e:
                logger.error(f"Error deleting document '{filename}' from ChromaDB: {e}")

        # Also remove from fallback_docs
        original_fallback_len = len(self.fallback_docs)
        self.fallback_docs = [
            d for d in self.fallback_docs
            if d.get("metadata", {}).get("document_name") != filename and d.get("metadata", {}).get("file_name") != filename
        ]
        if len(self.fallback_docs) < original_fallback_len:
            deleted_count += (original_fallback_len - len(self.fallback_docs))
            self._save_fallback_index()

        return deleted_count

    def search(
        self,
        query: str,
        top_k: int = 4,
        well_filter: Optional[str] = None,
        formation_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches vector index and returns top matching chunks with scores and metadata."""
        if not self.use_fallback and self.collection is not None:
            try:
                # Query top candidates from ChromaDB
                query_k = min(top_k * 4, 30)
                results = self.collection.query(
                    query_texts=[query],
                    n_results=query_k
                )

                citations = []
                if results and "documents" in results and results["documents"]:
                    docs = results["documents"][0]
                    metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
                    distances = results["distances"][0] if "distances" in results and results["distances"] else [0.2] * len(docs)

                    for doc, meta, dist in zip(docs, metas, distances):
                        w_meta = str(meta.get("well_name", "")).lower()
                        f_meta = str(meta.get("formation", "")).lower()

                        if well_filter and well_filter.lower() not in w_meta:
                            continue
                        if formation_filter and formation_filter.lower() not in f_meta:
                            continue

                        citations.append({
                            "snippet": doc,
                            "document_name": meta.get("document_name", "Oil Field Report"),
                            "well_name": meta.get("well_name", "General Offset"),
                            "formation": meta.get("formation", "N/A"),
                            "depth_interval": meta.get("depth_interval", "N/A"),
                            "page_number": meta.get("page_number", 1),
                            "score": round(max(0.1, 1.0 - (dist if dist is not None else 0.5)), 2)
                        })

                    # If strict filtering yielded fewer than needed, relax filter
                    if len(citations) < top_k:
                        for doc, meta, dist in zip(docs, metas, distances):
                            cand = {
                                "snippet": doc,
                                "document_name": meta.get("document_name", "Oil Field Report"),
                                "well_name": meta.get("well_name", "General Offset"),
                                "formation": meta.get("formation", "N/A"),
                                "depth_interval": meta.get("depth_interval", "N/A"),
                                "page_number": meta.get("page_number", 1),
                                "score": round(max(0.1, 1.0 - (dist if dist is not None else 0.5)), 2)
                            }
                            if not any(c["snippet"] == doc for c in citations):
                                citations.append(cand)
                            if len(citations) >= top_k:
                                break

                if citations:
                    return citations[:top_k]
            except Exception as e:
                logger.warning(f"Chroma search warning: {e}. Executing fallback vector search.")


        # Fallback search using token scoring
        query_tokens = set(SimpleEmbeddingEngine.tokenize(query))
        scored = []
        for item in self.fallback_docs:
            meta = item.get("metadata", {})
            if well_filter and well_filter.lower() not in meta.get("well_name", "").lower():
                continue
            if formation_filter and formation_filter.lower() not in meta.get("formation", "").lower():
                continue

            doc_tokens = set(SimpleEmbeddingEngine.tokenize(item["text"]))
            overlap = query_tokens.intersection(doc_tokens)
            score = len(overlap) / (len(query_tokens) + 1e-5)

            # Boost if exact phrase matches
            if any(q in item["text"].lower() for q in query.lower().split() if len(q) > 3):
                score += 0.3

            scored.append({
                "snippet": item["text"],
                "document_name": meta.get("document_name", "OIL Report"),
                "well_name": meta.get("well_name", "Assam Basin Well"),
                "formation": meta.get("formation", "Upper Assam"),
                "depth_interval": meta.get("depth_interval", "Variable"),
                "score": round(min(0.99, max(0.35, score)), 2)
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def synthesize_answer(self, question: str, citations: List[Dict[str, Any]]) -> str:
        """Domain-tailored synthesis for Oil India drilling intelligence queries."""
        if not citations:
            return (
                "Based on the currently indexed Well Completion Reports (WCRs) and Daily Drilling Reports (DDRs), "
                "no direct offset incident match was found for this specific query. Consider expanding your offset radius "
                "or querying adjacent fields (Nahorkatiya, Moran, Baghjan, Digboi)."
            )

        key_points = []
        for c in citations:
            key_points.append(f"• In **{c['well_name']}** ({c['formation']}, {c['depth_interval']}): {c['snippet'][:160]}...")

        citations_summary = "\n".join(key_points)

        answer = (
            f"**Offset Well Intelligence Summary for Oil India Engineers:**\n\n"
            f"Based on historical offset records from {len(citations)} relevant document sections:\n\n"
            f"{citations_summary}\n\n"
            f"**Key Engineering Precautions:**\n"
            f"1. **Mud Weight Window:** Maintain tight hydrostatic control when penetrating Barail and Tipam sections to prevent pore pressure underbalance or micro-fracturing weak sandstone intervals.\n"
            f"2. **Lost Circulation Mitigation:** Keep 30-50 bbl of medium-to-coarse LCM (Lost Circulation Material) pills pre-mixed in active pit.\n"
            f"3. **Wellbore Stability:** Monitor shaker returns for splintery shale cavings indicative of Girujan / Kopili overpressured shale spalling."
        )
        return answer

vector_store_service = VectorStoreService()
