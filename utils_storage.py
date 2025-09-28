"""
Storage helpers: local JSON storage and optional Azure Blob Storage upload.

Local:
 - Saves anonymized candidate JSON to ./data/candidates/<timestamp>.json

Azure Blob (optional):
 - If AZURE_BLOB_CONN_STR and AZURE_BLOB_CONTAINER are set in env, attempts upload.
 - This file intentionally keeps Azure usage optional so local-only runs without Azure SDK are possible.

Security:
 - Do NOT store raw emails/phones in cloud unless required. We mask by default in app.py before saving.
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Optional azure import; wrapped to avoid hard dependency for local runs
try:
    from azure.storage.blob import BlobServiceClient
    AZURE_SDK_AVAILABLE = True
except Exception:
    AZURE_SDK_AVAILABLE = False

DATA_DIR = Path("./data/candidates")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def save_local_candidate(candidate: dict) -> str:
    """
    Save a candidate JSON locally. Returns filepath.
    """
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = DATA_DIR / f"candidate_{ts}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(candidate, f, indent=2)
    print(f"Saved candidate locally: {fname}")
    return str(fname)

def try_upload_to_azure(candidate: dict) -> bool:
    """
    Attempt to upload candidate JSON to Azure Blob Storage if configured.
    Returns True if uploaded, False otherwise.
    """
    conn_str = os.getenv("AZURE_BLOB_CONN_STR")
    container = os.getenv("AZURE_BLOB_CONTAINER")
    if not conn_str or not container:
        print("Azure Blob not configured (AZURE_BLOB_CONN_STR or AZURE_BLOB_CONTAINER missing). Skipping upload.")
        return False
    if not AZURE_SDK_AVAILABLE:
        print("azure-storage-blob SDK not installed. Install with 'pip install azure-storage-blob' to enable uploads.")
        return False
    try:
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        blob_client = blob_service_client.get_blob_client(container=container, blob=f"candidate_{datetime.utcnow().isoformat()}.json")
        blob_client.upload_blob(json.dumps(candidate, ensure_ascii=False), overwrite=True)
        print("Uploaded candidate to Azure Blob Storage.")
        return True
    except Exception as e:
        print("Failed to upload to Azure Blob Storage:", e)
        return False
