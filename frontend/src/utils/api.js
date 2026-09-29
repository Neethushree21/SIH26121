import { getToken } from "./auth";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

function getAuthHeaders(extra = {}) {
  const token = getToken();
  const headers = { ...extra };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

// -------------------------------------------------------------
// Authentication Endpoints
// -------------------------------------------------------------
export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Authentication failed. Invalid email or password.");
  }
  return res.json();
}

export async function registerUser(userData) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Registration failed. Please check your details.");
  }
  return res.json();
}

export async function fetchCurrentUser() {
  const res = await fetch(`${API_BASE}/auth/me`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error("Failed to fetch user profile");
  return res.json();
}

// -------------------------------------------------------------
// Wells & Geospatial Endpoints
// -------------------------------------------------------------
export async function fetchWells(fieldName = "", status = "") {
  let url = `${API_BASE}/wells`;
  const params = new URLSearchParams();
  if (fieldName) params.append("field_name", fieldName);
  if (status) params.append("status", status);
  if (params.toString()) url += `?${params.toString()}`;

  const res = await fetch(url, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error("Failed to fetch wells");
  return res.json();
}

export async function fetchWellsGeoJSON() {
  const res = await fetch(`${API_BASE}/wells/geojson`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error("Failed to fetch GeoJSON");
  return res.json();
}

export async function fetchWellDetail(wellId) {
  const res = await fetch(`${API_BASE}/wells/${wellId}`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error(`Failed to fetch well detail for ${wellId}`);
  return res.json();
}

export async function queryNearbyWells(lat, lon, radiusKm = 10.0, formation = "", targetDepth = null, plannedMudWeight = null) {
  const params = new URLSearchParams({
    latitude: parseFloat(lat),
    longitude: parseFloat(lon),
    radius_km: parseFloat(radiusKm)
  });
  if (formation) params.append("formation", formation);
  if (targetDepth) params.append("target_depth_md", parseFloat(targetDepth));
  if (plannedMudWeight) params.append("planned_mud_weight", parseFloat(plannedMudWeight));

  const res = await fetch(`${API_BASE}/wells/nearby?${params.toString()}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error("Failed to query nearby wells with multi-factor similarity");
  return res.json();
}

export async function triggerFolderIngestion(folderPath) {
  const res = await fetch(`${API_BASE}/ingest/folder`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ folder_path: folderPath })
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Folder ingestion failed");
  }
  return res.json();
}

export async function fetchIngestionTaskStatus(taskId) {
  const res = await fetch(`${API_BASE}/ingest/status/${taskId}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error(`Failed to fetch status for task ${taskId}`);
  return res.json();
}

export async function queryRAGChat(question, wellFilter = null, formationFilter = null) {
  const res = await fetch(`${API_BASE}/search/query`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      question,
      well_filter: wellFilter || null,
      formation_filter: formationFilter || null,
      top_k: 4
    })
  });
  if (!res.ok) throw new Error("Knowledge search query failed");
  return res.json();
}

export async function fetchHazardFeed(severity = "") {
  let url = `${API_BASE}/alerts/feed`;
  if (severity) url += `?severity=${severity}`;
  const res = await fetch(url, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error("Failed to fetch hazard feed");
  return res.json();
}

export async function assessSpudLocation(lat, lon, plannedTvd, radiusKm = 5.0, targetFormation = null) {
  const res = await fetch(`${API_BASE}/alerts/assess`, {
    method: "POST",
    headers: getAuthHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({
      latitude: parseFloat(lat),
      longitude: parseFloat(lon),
      planned_tvd: parseFloat(plannedTvd),
      radius_km: parseFloat(radiusKm),
      target_formation: targetFormation || null
    })
  });
  if (!res.ok) throw new Error("Risk assessment failed");
  return res.json();
}

export async function uploadReportFile(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/ingest/upload`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: formData
  });
  if (!res.ok) throw new Error("File upload failed");
  return res.json();
}

export async function fetchIngestionStatus() {
  const res = await fetch(`${API_BASE}/ingest/status`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error("Failed to fetch ingestion status");
  return res.json();
}

export async function deleteIngestedDocument(documentId) {
  const res = await fetch(`${API_BASE}/ingest/${documentId}`, {
    method: "DELETE",
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to delete document");
  }
  return res.json();
}

export async function purgeAllIngestedDocuments() {
  const res = await fetch(`${API_BASE}/ingest/purge/all`, {
    method: "DELETE",
    headers: getAuthHeaders()
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to purge documents");
  }
  return res.json();
}

export async function fetchExplainableOffsetRisks(lat, lon, plannedDepth = 3700.0, radiusKm = 10.0, formation = "") {
  const params = new URLSearchParams({
    latitude: parseFloat(lat),
    longitude: parseFloat(lon),
    planned_depth_md: parseFloat(plannedDepth),
    radius_km: parseFloat(radiusKm)
  });
  if (formation) params.append("formation", formation);

  const res = await fetch(`${API_BASE}/alerts/offset-risks?${params.toString()}`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error("Failed to fetch explainable offset risks");
  return res.json();
}

export async function fetchTelemetryTick() {
  const res = await fetch(`${API_BASE}/rtmac/tick`, {
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error("Failed to fetch eRTMAC telemetry tick");
  return res.json();
}

export async function resetTelemetrySimulation(depthMd = 2320.0, mudWeight = 10.4) {
  const res = await fetch(`${API_BASE}/rtmac/reset?depth_md=${depthMd}&mud_weight=${mudWeight}`, {
    method: "POST",
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error("Failed to reset telemetry simulation");
  return res.json();
}
