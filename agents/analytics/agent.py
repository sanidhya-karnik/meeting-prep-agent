"""
Analytics Agent for PreCall Briefing

Finds and describes analytics charts, dashboards, and KPIs for clients.
Simulates Docling-based analysis of dashboard screenshots.
"""

import os
import json
import base64
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Analytics Agent")

DATA_DIR = Path(os.getenv("ANALYTICS_DATA_PATH", "./data/analytics"))
DESCRIPTIONS_FILE = DATA_DIR / "chart_descriptions.json"


class QueryRequest(BaseModel):
    client_name: str
    include_images: Optional[bool] = False


def normalize_name(value: str) -> str:
    """Normalize names for robust matching across datasets."""
    return "".join(ch for ch in value.lower() if ch.isalnum())


def load_analytics_data() -> dict:
    """Load analytics data including dashboards and KPIs."""
    if DESCRIPTIONS_FILE.exists():
        with open(DESCRIPTIONS_FILE) as f:
            return json.load(f)
    return {}


def find_client_data(client_name: str, data: dict) -> Optional[dict]:
    """Find analytics data matching client name."""
    client_norm = normalize_name(client_name)
    search_words = client_name.lower().split()
    
    for key, value in data.items():
        key_norm = normalize_name(key)
        if client_norm in key_norm or key_norm in client_norm:
            return value
        
        # Also check account_name field if present
        if isinstance(value, dict) and "account_name" in value:
            if client_norm in normalize_name(value["account_name"]):
                return value
        
        # Partial word match
        if any(word in key.lower() for word in search_words if len(word) > 2):
            return value
    
    return None


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "data_dir": str(DATA_DIR),
        "descriptions_available": DESCRIPTIONS_FILE.exists()
    }


@app.post("/query")
async def query(request: QueryRequest):
    """Query for analytics data related to a client."""
    all_data = load_analytics_data()
    client_data = find_client_data(request.client_name, all_data)
    
    if not client_data:
        return {"error": f"No analytics data found for '{request.client_name}'"}
    
    # Build response with charts and insights
    result = {
        "account_name": client_data.get("account_name", request.client_name),
        "dashboards": [],
        "charts": [],
        "chart_insights": [],
        "kpi_summary": client_data.get("kpi_summary", {}),
        "summary": ""
    }
    
    # Process dashboards and extract chart information
    for dashboard in client_data.get("dashboards", []):
        dashboard_info = {
            "name": dashboard.get("name"),
            "file": dashboard.get("file"),
            "last_updated": dashboard.get("last_updated")
        }
        result["dashboards"].append(dashboard_info)
        
        # Process charts within dashboard
        for chart in dashboard.get("charts", []):
            chart_info = {
                "chart_type": chart.get("chart_type"),
                "title": chart.get("title"),
                "description": chart.get("description"),
                "insight": chart.get("insight"),
                "data_summary": chart.get("data_summary", ""),
                "value": chart.get("value"),
                "status": chart.get("status")
            }
            result["charts"].append(chart_info)
            
            # Extract key insights for UI display
            if chart.get("insight"):
                result["chart_insights"].append({
                    "title": chart.get("title"),
                    "insight": chart.get("insight"),
                    "chart_type": chart.get("chart_type")
                })
    
    # Build summary from KPI data
    kpi = client_data.get("kpi_summary", {})
    if kpi:
        result["summary"] = kpi.get("key_insight", "")
        
        # Also include health metrics for backward compatibility
        result["health_metrics"] = {
            "engagement_score": kpi.get("engagement_score"),
            "nps_score": kpi.get("nps_score"),
            "support_tickets_open": kpi.get("support_tickets_open"),
            "usage_trend": kpi.get("usage_trend"),
            "risk_level": kpi.get("risk_level")
        }
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
