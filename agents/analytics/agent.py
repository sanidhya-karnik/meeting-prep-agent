"""
Analytics Agent for PreCall Briefing

Finds and describes analytics charts and dashboards for clients.
Returns chart images and metadata for multimodal processing.
"""

import os
import json
import base64
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Analytics Agent")

DATA_DIR = Path("/app/data")
DESCRIPTIONS_FILE = DATA_DIR / "chart_descriptions.json"


class QueryRequest(BaseModel):
    client_name: str
    include_images: Optional[bool] = False  # Whether to return base64 images


def load_chart_descriptions() -> dict:
    """Load pre-computed chart descriptions."""
    if DESCRIPTIONS_FILE.exists():
        with open(DESCRIPTIONS_FILE) as f:
            return json.load(f)
    return {}


def find_client_charts(client_name: str) -> list[dict]:
    """Find chart images matching client name."""
    client_lower = client_name.lower().replace(" ", "_")
    charts = []
    
    # First check: actual image files
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        for file_path in DATA_DIR.glob(ext):
            if client_lower in file_path.stem.lower() or "acme" in file_path.stem.lower():
                charts.append({
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "chart_type": infer_chart_type(file_path.stem)
                })
    
    # Fallback: use descriptions file as source of truth (for demo without actual images)
    if not charts:
        descriptions = load_chart_descriptions()
        for file_name in descriptions.keys():
            if "acme" in file_name.lower() or client_lower in file_name.lower():
                charts.append({
                    "file_name": file_name,
                    "file_path": str(DATA_DIR / file_name),
                    "chart_type": infer_chart_type(file_name)
                })
    
    return charts


def infer_chart_type(filename: str) -> str:
    """Infer chart type from filename."""
    name_lower = filename.lower()
    if "usage" in name_lower or "trend" in name_lower:
        return "usage_trend"
    elif "health" in name_lower:
        return "health_score"
    elif "engagement" in name_lower or "heatmap" in name_lower:
        return "engagement_heatmap"
    elif "support" in name_lower or "ticket" in name_lower:
        return "support_metrics"
    return "general"


def get_chart_image_base64(file_path: str) -> Optional[str]:
    """Read chart image and return as base64."""
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def get_chart_description(file_name: str, descriptions: dict) -> str:
    """Get pre-computed description for a chart."""
    # Try exact match first
    if file_name in descriptions:
        return descriptions[file_name]
    
    # Try without extension
    stem = Path(file_name).stem
    if stem in descriptions:
        return descriptions[stem]
    
    return "No description available for this chart."


@app.get("/health")
async def health():
    """Health check endpoint."""
    charts = list(DATA_DIR.glob("*.png")) + list(DATA_DIR.glob("*.jpg"))
    return {
        "status": "healthy",
        "data_dir": str(DATA_DIR),
        "charts_found": len(charts),
        "descriptions_available": DESCRIPTIONS_FILE.exists()
    }


@app.post("/query")
async def query(request: QueryRequest):
    """Query for analytics charts related to a client."""
    charts = find_client_charts(request.client_name)
    
    if not charts:
        return {"error": f"No analytics charts found for '{request.client_name}'"}
    
    # Load descriptions
    descriptions = load_chart_descriptions()
    
    # Build response
    result = {
        "charts": [],
        "summary": ""
    }
    
    summaries = []
    
    for chart in charts:
        chart_info = {
            "file_name": chart["file_name"],
            "chart_type": chart["chart_type"],
            "description": get_chart_description(chart["file_name"], descriptions)
        }
        
        # Optionally include base64 image for multimodal processing
        if request.include_images:
            img_base64 = get_chart_image_base64(chart["file_path"])
            if img_base64:
                chart_info["image_base64"] = img_base64
                chart_info["mime_type"] = "image/png"
        
        result["charts"].append(chart_info)
        summaries.append(chart_info["description"])
    
    # Create overall summary
    result["summary"] = " ".join(summaries[:3])  # First 3 descriptions
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
