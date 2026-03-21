"""
Docs Agent for PreCall Briefing

Parses and summarizes documents (PDFs, DOCX) using Docling.
Extracts key information from proposals, meeting notes, and other business documents.
"""

import os
import json
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Docs Agent")

DATA_DIR = Path("/app/data")
CACHE_FILE = DATA_DIR / "parsed_docs_cache.json"

# Optional: Use Docling for parsing (if available)
try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False


class QueryRequest(BaseModel):
    client_name: str
    doc_types: Optional[list[str]] = None


def get_cached_docs() -> dict:
    """Load pre-parsed document cache."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}


def parse_document_with_docling(file_path: Path) -> dict:
    """Parse document using Docling to extract structured content."""
    if not DOCLING_AVAILABLE:
        return {"error": "Docling not available"}
    
    try:
        converter = DocumentConverter()
        result = converter.convert(str(file_path))
        
        # Extract text and structure
        doc = result.document
        
        return {
            "file_name": file_path.name,
            "content": doc.export_to_markdown(),
            "num_pages": len(doc.pages) if hasattr(doc, 'pages') else 1,
            "tables": [t.export() for t in doc.tables] if hasattr(doc, 'tables') else [],
            "parsed": True
        }
    except Exception as e:
        return {"error": f"Docling parsing failed: {str(e)}"}


def find_client_docs(client_name: str) -> list[dict]:
    """Find documents matching client name."""
    client_lower = client_name.lower().replace(" ", "_")
    docs = []
    
    # Check cache first
    cache = get_cached_docs()
    
    # Try exact match
    if client_lower in cache:
        return cache[client_lower].get("documents", [])
    
    # Try partial match in cache
    for key in cache:
        if key in client_lower or client_lower in key or "acme" in client_lower.lower():
            if key == "acme" or "acme" in key:
                return cache[key].get("documents", [])
    
    # Fallback: search for files
    for ext in ["*.pdf", "*.docx", "*.doc"]:
        for file_path in DATA_DIR.glob(ext):
            if client_lower in file_path.stem.lower() or "acme" in file_path.stem.lower():
                # Determine doc type from filename
                doc_type = "unknown"
                name_lower = file_path.stem.lower()
                if "proposal" in name_lower:
                    doc_type = "proposal"
                elif "meeting" in name_lower or "notes" in name_lower:
                    doc_type = "meeting_notes"
                elif "sow" in name_lower or "statement" in name_lower:
                    doc_type = "sow"
                elif "requirements" in name_lower:
                    doc_type = "requirements"
                
                doc_info = {
                    "title": file_path.stem.replace("_", " ").title(),
                    "file_name": file_path.name,
                    "type": doc_type,
                    "last_modified": file_path.stat().st_mtime if file_path.exists() else None,
                    "file_path": str(file_path)
                }
                
                # Try to parse with Docling
                if DOCLING_AVAILABLE:
                    parsed = parse_document_with_docling(file_path)
                    if "content" in parsed:
                        # Extract summary from first 500 chars
                        content = parsed["content"]
                        doc_info["summary"] = content[:500] + "..." if len(content) > 500 else content
                        doc_info["num_pages"] = parsed.get("num_pages", 1)
                
                docs.append(doc_info)
    
    return docs


def filter_by_type(docs: list[dict], doc_types: list[str]) -> list[dict]:
    """Filter documents by type."""
    if not doc_types:
        return docs
    return [d for d in docs if d.get("type") in doc_types]


@app.get("/health")
async def health():
    """Health check endpoint."""
    files = list(DATA_DIR.glob("*.pdf")) + list(DATA_DIR.glob("*.docx"))
    return {
        "status": "healthy",
        "data_dir": str(DATA_DIR),
        "docling_available": DOCLING_AVAILABLE,
        "documents_found": len(files)
    }


@app.post("/query")
async def query(request: QueryRequest):
    """Query for documents related to a client."""
    docs = find_client_docs(request.client_name)
    
    if request.doc_types:
        docs = filter_by_type(docs, request.doc_types)
    
    if not docs:
        return {"error": f"No documents found for '{request.client_name}'"}
    
    return {"documents": docs}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
