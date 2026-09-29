import React, { useState, useEffect } from "react";
import { X, UploadCloud, FolderSearch, FileText, CheckCircle, AlertCircle, RefreshCw, HardDrive, Play, Layers, Trash2 } from "lucide-react";
import { uploadReportFile, fetchIngestionStatus, triggerFolderIngestion, fetchIngestionTaskStatus, deleteIngestedDocument, purgeAllIngestedDocuments } from "../../utils/api";

export default function DocumentIngestModal({ onClose }) {
  const [activeTab, setActiveTab] = useState("folder"); // "folder" or "upload"
  const [documents, setDocuments] = useState([]);
  
  // Single File Upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState("");
  const [uploadError, setUploadError] = useState("");

  // Server Folder Batch Ingestion state
  const [folderPath, setFolderPath] = useState("sample_data/reports");
  const [batchTaskId, setBatchTaskId] = useState(null);
  const [batchTaskStatus, setBatchTaskStatus] = useState(null);
  const [folderScanning, setFolderScanning] = useState(false);
  const [folderError, setFolderError] = useState("");

  // Document deletion state
  const [deletingId, setDeletingId] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [confirmPurge, setConfirmPurge] = useState(false);
  const [purgingAll, setPurgingAll] = useState(false);
  const [actionFeedback, setActionFeedback] = useState("");
  const [actionError, setActionError] = useState("");

  useEffect(() => {
    loadStatus();
  }, []);

  // Poll task status if active
  useEffect(() => {
    let interval = null;
    if (batchTaskId && (!batchTaskStatus || (batchTaskStatus.status !== "COMPLETED" && batchTaskStatus.status !== "FAILED"))) {
      interval = setInterval(async () => {
        try {
          const status = await fetchIngestionTaskStatus(batchTaskId);
          setBatchTaskStatus(status);
          if (status.status === "COMPLETED" || status.status === "FAILED") {
            setFolderScanning(false);
            loadStatus();
          }
        } catch (err) {
          console.error(err);
        }
      }, 1500);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [batchTaskId, batchTaskStatus]);

  const loadStatus = async () => {
    try {
      const data = await fetchIngestionStatus();
      setDocuments(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadSuccess("");
      setUploadError("");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || uploading) return;
    setUploading(true);
    setUploadSuccess("");
    setUploadError("");

    try {
      const res = await uploadReportFile(selectedFile);
      setUploadSuccess(`Indexed "${selectedFile.name}" into ${res.chunks_indexed} vector embeddings!`);
      setSelectedFile(null);
      await loadStatus();
    } catch (err) {
      setUploadError(err.message || "Failed to upload and index document.");
    } finally {
      setUploading(false);
    }
  };

  const handleTriggerFolderScan = async () => {
    if (!folderPath.trim() || folderScanning) return;
    setFolderScanning(true);
    setFolderError("");
    setBatchTaskStatus(null);

    try {
      const res = await triggerFolderIngestion(folderPath);
      setBatchTaskId(res.task_id);
    } catch (err) {
      setFolderError(err.message || "Failed to initiate folder ingestion.");
      setFolderScanning(false);
    }
  };

  const executeDelete = async (id, filename) => {
    setDeletingId(id);
    setActionFeedback("");
    setActionError("");
    try {
      const res = await deleteIngestedDocument(id);
      setActionFeedback(res.message || `Deleted "${filename}" and purged its vector embeddings.`);
      setConfirmDeleteId(null);
      await loadStatus();
    } catch (err) {
      console.error("Delete failed:", err);
      setActionError(err.message || `Failed to delete ${filename}`);
    } finally {
      setDeletingId(null);
    }
  };

  const executePurgeAll = async () => {
    setPurgingAll(true);
    setActionFeedback("");
    setActionError("");
    try {
      const res = await purgeAllIngestedDocuments();
      setActionFeedback(res.message || "All indexed documents and vector chunks purged successfully.");
      setConfirmPurge(false);
      await loadStatus();
    } catch (err) {
      console.error("Purge failed:", err);
      setActionError(err.message || "Failed to purge documents");
    } finally {
      setPurgingAll(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[2000] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-3xl max-h-[88vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="bg-slate-950 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <UploadCloud className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">
                Technical Report Ingestion Pipeline
              </h2>
              <p className="text-xs text-slate-400">
                PyMuPDF Semantic Sliding-Window Chunking & Batch ChromaDB Vector Ingestion
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-slate-800 bg-slate-950/60 px-6">
          <button
            onClick={() => setActiveTab("folder")}
            className={`flex items-center space-x-2 py-3 px-4 text-xs font-semibold border-b-2 transition ${
              activeTab === "folder"
                ? "border-amber-500 text-amber-400 bg-amber-500/5"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <FolderSearch className="w-4 h-4" />
            <span>Server Directory Batch Ingestion (Batches of 10)</span>
          </button>
          <button
            onClick={() => setActiveTab("upload")}
            className={`flex items-center space-x-2 py-3 px-4 text-xs font-semibold border-b-2 transition ${
              activeTab === "upload"
                ? "border-amber-500 text-amber-400 bg-amber-500/5"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <UploadCloud className="w-4 h-4" />
            <span>Single File Upload</span>
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          
          {/* Tab 1: Server Directory Batch Ingestion */}
          {activeTab === "folder" && (
            <div className="space-y-4">
              <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-3">
                <div className="text-xs text-slate-300 font-medium">
                  Recursively scans directories for <code className="text-amber-400 bg-slate-900 px-1 py-0.5 rounded">.pdf</code>, <code className="text-amber-400 bg-slate-900 px-1 py-0.5 rounded">.csv</code>, <code className="text-amber-400 bg-slate-900 px-1 py-0.5 rounded">.xlsx</code>, and <code className="text-amber-400 bg-slate-900 px-1 py-0.5 rounded">.txt</code> while preserving folder hierarchy metadata.
                </div>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={folderPath}
                    onChange={(e) => setFolderPath(e.target.value)}
                    placeholder="Enter directory path (e.g. sample_data/reports)"
                    className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500 font-mono"
                  />
                  <button
                    onClick={handleTriggerFolderScan}
                    disabled={folderScanning}
                    className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-black font-bold text-xs flex items-center gap-1.5 transition shadow-md shadow-amber-500/20"
                  >
                    {folderScanning ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        <span>Processing...</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 fill-current" />
                        <span>Start Batch Ingestion</span>
                      </>
                    )}
                  </button>
                </div>

                {folderError && (
                  <div className="text-xs text-red-400 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    <span>{folderError}</span>
                  </div>
                )}
              </div>

              {/* Progress Card */}
              {batchTaskStatus && (
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200 flex items-center gap-2">
                      <span className={`w-2.5 h-2.5 rounded-full ${
                        batchTaskStatus.status === "COMPLETED" ? "bg-emerald-400" : "bg-amber-400 animate-ping"
                      }`}></span>
                      <span>Task: {batchTaskStatus.task_id.slice(0, 8)}...</span>
                    </span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                      batchTaskStatus.status === "COMPLETED"
                        ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                        : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                    }`}>
                      {batchTaskStatus.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400">Files Processed</div>
                      <div className="font-bold text-white mt-0.5 font-mono">
                        {batchTaskStatus.processed_files} / {batchTaskStatus.total_files}
                      </div>
                    </div>
                    <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400">Current Batch (Size 10)</div>
                      <div className="font-bold text-amber-400 mt-0.5 font-mono">
                        {batchTaskStatus.current_batch} / {batchTaskStatus.total_batches || 1}
                      </div>
                    </div>
                    <div className="bg-slate-900 p-2 rounded-lg border border-slate-800">
                      <div className="text-[10px] text-slate-400">Indexed Chunks</div>
                      <div className="font-bold text-emerald-400 mt-0.5 font-mono">
                        {batchTaskStatus.indexed_chunks}
                      </div>
                    </div>
                  </div>

                  {batchTaskStatus.processed_file_names && batchTaskStatus.processed_file_names.length > 0 && (
                    <div className="text-[11px] text-slate-400">
                      <strong>Recently Indexed:</strong> {batchTaskStatus.processed_file_names.slice(-3).join(", ")}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Tab 2: Single File Upload */}
          {activeTab === "upload" && (
            <div className="border-2 border-dashed border-slate-700 hover:border-amber-500/60 rounded-2xl p-6 text-center bg-slate-950/40 transition">
              <input
                type="file"
                id="file-upload"
                onChange={handleFileChange}
                accept=".pdf,.txt,.csv,.xlsx,.xls"
                className="hidden"
              />
              <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center text-amber-400 mb-2">
                  <FileText className="w-6 h-6" />
                </div>
                <span className="text-sm font-semibold text-slate-200">
                  {selectedFile ? selectedFile.name : "Click to select or drop technical report"}
                </span>
                <span className="text-xs text-slate-500 mt-1">
                  Supports PDF, CSV, XLSX, TXT (DDRs, WCRs, Mud Logs)
                </span>
              </label>

              {selectedFile && (
                <div className="mt-4 flex items-center justify-center space-x-3">
                  <span className="text-xs text-slate-400 font-mono">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </span>
                  <button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-black font-bold text-xs flex items-center gap-1.5 transition"
                  >
                    {uploading ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Semantic Chunking...</span>
                      </>
                    ) : (
                      <>
                        <UploadCloud className="w-3.5 h-3.5" />
                        <span>Ingest into ChromaDB</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {uploadSuccess && (
                <div className="mt-3 text-xs text-emerald-400 font-medium flex items-center justify-center gap-1.5">
                  <CheckCircle className="w-4 h-4" />
                  <span>{uploadSuccess}</span>
                </div>
              )}
              {uploadError && (
                <div className="mt-3 text-xs text-red-400 font-medium flex items-center justify-center gap-1.5">
                  <AlertCircle className="w-4 h-4" />
                  <span>{uploadError}</span>
                </div>
              )}
            </div>
          )}

          {/* Currently Indexed Documents */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-amber-400" />
                <span>Indexed Technical Reports in Vector Store ({documents.length})</span>
              </h3>
              <div className="flex items-center space-x-2">
                {documents.length > 0 && (
                  confirmPurge ? (
                    <div className="flex items-center space-x-1">
                      <button
                        type="button"
                        onClick={executePurgeAll}
                        disabled={purgingAll}
                        className="text-[11px] bg-red-600 hover:bg-red-500 text-white font-bold px-2 py-1 rounded flex items-center gap-1 transition shadow"
                      >
                        {purgingAll ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Trash2 className="w-3 h-3" />}
                        <span>Confirm Purge All?</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setConfirmPurge(false)}
                        className="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-1.5 py-1 rounded transition"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setConfirmPurge(true)}
                      disabled={purgingAll}
                      className="text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 px-2 py-1 rounded flex items-center gap-1 transition disabled:opacity-50"
                      title="Purge all indexed documents"
                    >
                      <Trash2 className="w-3 h-3" />
                      <span>Purge All</span>
                    </button>
                  )
                )}
                <button
                  type="button"
                  onClick={loadStatus}
                  className="text-xs text-slate-400 hover:text-white flex items-center gap-1 px-2 py-1 rounded hover:bg-slate-800 transition"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Refresh</span>
                </button>
              </div>
            </div>

            {actionFeedback && (
              <div className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-2 rounded-lg flex items-center gap-2">
                <CheckCircle className="w-4 h-4 flex-shrink-0" />
                <span>{actionFeedback}</span>
              </div>
            )}
            {actionError && (
              <div className="text-xs text-red-400 bg-red-500/10 border border-red-500/20 px-3 py-2 rounded-lg flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{actionError}</span>
              </div>
            )}

            <div className="border border-slate-800 rounded-xl overflow-hidden max-h-[220px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-semibold sticky top-0">
                  <tr>
                    <th className="p-3">File Name</th>
                    <th className="p-3">Well / Field</th>
                    <th className="p-3">Format</th>
                    <th className="p-3">Chunks</th>
                    <th className="p-3">Status</th>
                    <th className="p-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800 text-slate-300">
                  {documents.map((d) => (
                    <tr key={d.id} className="hover:bg-slate-800/40">
                      <td className="p-3 font-semibold text-white flex items-center gap-2">
                        <FileText className="w-3.5 h-3.5 text-amber-400" />
                        <span>{d.filename}</span>
                      </td>
                      <td className="p-3 text-slate-400">{d.well_name || "General OIL"}</td>
                      <td className="p-3 font-mono text-[11px] text-slate-400">{d.file_type}</td>
                      <td className="p-3 font-mono text-emerald-400 font-bold">{d.chunk_count}</td>
                      <td className="p-3">
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {d.status}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        {confirmDeleteId === d.id ? (
                          <div className="flex items-center justify-end space-x-1">
                            <button
                              type="button"
                              onClick={() => executeDelete(d.id, d.filename)}
                              disabled={deletingId === d.id}
                              className="px-2 py-0.5 rounded bg-red-600 hover:bg-red-500 text-white font-bold text-[10px] transition shadow flex items-center gap-1"
                            >
                              {deletingId === d.id ? (
                                <RefreshCw className="w-2.5 h-2.5 animate-spin" />
                              ) : (
                                <Trash2 className="w-2.5 h-2.5" />
                              )}
                              <span>Delete?</span>
                            </button>
                            <button
                              type="button"
                              onClick={() => setConfirmDeleteId(null)}
                              disabled={deletingId === d.id}
                              className="px-1.5 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] transition"
                            >
                              ✕
                            </button>
                          </div>
                        ) : (
                          <button
                            type="button"
                            onClick={() => setConfirmDeleteId(d.id)}
                            disabled={deletingId === d.id}
                            className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition disabled:opacity-50"
                            title={`Delete ${d.filename}`}
                          >
                            {deletingId === d.id ? (
                              <RefreshCw className="w-3.5 h-3.5 animate-spin text-red-400" />
                            ) : (
                              <Trash2 className="w-3.5 h-3.5" />
                            )}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {documents.length === 0 && (
                    <tr>
                      <td colSpan="6" className="p-6 text-center text-slate-500 text-xs">
                        No technical reports indexed yet. Trigger batch ingestion above.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="bg-slate-950 px-6 py-3 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold transition"
          >
            Done
          </button>
        </div>

      </div>
    </div>
  );
}
