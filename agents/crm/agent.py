"""
CRM Agent for Meeting Prep Agent

Fetches client info, deal stage, stakeholders, and recent activity.
Supports both PostgreSQL (container) and JSON (local dev) data sources.
"""

import os
import json
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="CRM Agent")

# Data source configuration
# If CRM_DATA_PATH is set, use JSON file; otherwise try PostgreSQL
CRM_DATA_PATH = os.getenv("CRM_DATA_PATH")
USE_JSON = CRM_DATA_PATH is not None

if not USE_JSON:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        DB_HOST = os.getenv("DB_HOST", "postgres")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "crm")
        DB_USER = os.getenv("DB_USER", "crm_user")
        DB_PASS = os.getenv("DB_PASS", "crm_pass")
    except ImportError:
        USE_JSON = True
        CRM_DATA_PATH = "./data/crm/clients.json"


class QueryRequest(BaseModel):
    client_name: str


def normalize_name(value: str) -> str:
    """Normalize names for robust matching across datasets."""
    return "".join(ch for ch in value.lower() if ch.isalnum())


# ============================================================================
# JSON Data Source (Local Development)
# ============================================================================

def load_client_data_json(client_name: str) -> dict:
    """Load client data from JSON file."""
    data_path = Path(CRM_DATA_PATH)
    if not data_path.exists():
        return {"error": f"CRM data file not found at {data_path}"}
    
    with open(data_path) as f:
        data = json.load(f)
    
    # Normalize client name for lookup
    client_norm = normalize_name(client_name)
    
    # Try exact key match first
    key = client_name.lower().strip()
    if key in data:
        return data[key]
    
    # Try normalized match
    for k, v in data.items():
        if normalize_name(k) == client_norm or client_norm in normalize_name(k):
            return v
    
    return {"error": f"Client '{client_name}' not found in CRM"}


# ============================================================================
# PostgreSQL Data Source (Container)
# ============================================================================

def get_db_connection():
    """Create database connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=RealDictCursor
    )


def load_client_data_postgres(client_name: str) -> dict:
    """Fetch all client data from PostgreSQL."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Find client by name (case-insensitive, partial match)
        cur.execute("""
            SELECT * FROM clients 
            WHERE LOWER(name) LIKE LOWER(%s)
            LIMIT 1
        """, (f"%{client_name}%",))
        client = cur.fetchone()
        
        if not client:
            conn.close()
            return {"error": f"Client '{client_name}' not found in CRM"}
        
        client_id = client['id']
        
        # Fetch contacts
        cur.execute("""
            SELECT name, role, email, phone, sentiment, notes, is_primary
            FROM contacts WHERE client_id = %s
            ORDER BY is_primary DESC, name
        """, (client_id,))
        contacts = cur.fetchall()
        
        # Fetch deal info
        cur.execute("""
            SELECT name, stage, deal_type, value, currency, close_date, 
                   probability, owner, competitor
            FROM deals WHERE client_id = %s
            ORDER BY created_at DESC LIMIT 1
        """, (client_id,))
        deal = cur.fetchone()
        
        # Fetch recent activities
        cur.execute("""
            SELECT activity_type, subject, description, participants,
                   duration_minutes, activity_date, next_steps
            FROM activities WHERE client_id = %s
            ORDER BY activity_date DESC LIMIT 5
        """, (client_id,))
        activities = cur.fetchall()
        
        # Fetch health metrics
        cur.execute("""
            SELECT engagement_score, nps_score, support_tickets_open,
                   last_login, usage_trend, risk_level
            FROM health_metrics WHERE client_id = %s
            ORDER BY recorded_at DESC LIMIT 1
        """, (client_id,))
        health = cur.fetchone()
        
        conn.close()
        
        # Format response
        result = {
            "client": {
                "name": client['name'],
                "industry": client['industry'],
                "company_size": client['company_size'],
                "headquarters": client['headquarters']
            },
            "stakeholders": [
                {
                    "name": c['name'],
                    "role": c['role'],
                    "email": c['email'],
                    "sentiment": c['sentiment'],
                    "notes": c['notes']
                }
                for c in contacts
            ],
            "deal": {
                "name": deal['name'],
                "stage": deal['stage'],
                "value": f"${deal['value']:,.0f}",
                "close_date": str(deal['close_date']),
                "probability": deal['probability'],
                "owner": deal['owner'],
                "competitor": deal['competitor']
            } if deal else None,
            "recent_activity": [
                {
                    "date": str(a['activity_date'].date()) if a['activity_date'] else None,
                    "type": a['activity_type'],
                    "subject": a['subject'],
                    "note": a['description'],
                    "next_steps": a['next_steps']
                }
                for a in activities
            ],
            "health_indicators": {
                "engagement_score": health['engagement_score'],
                "nps_score": health['nps_score'],
                "support_tickets_open": health['support_tickets_open'],
                "usage_trend": health['usage_trend'],
                "risk_level": health['risk_level']
            } if health else None
        }
        
        return result
        
    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    if USE_JSON:
        data_path = Path(CRM_DATA_PATH)
        return {
            "status": "healthy",
            "data_source": "json",
            "data_path": str(data_path),
            "exists": data_path.exists()
        }
    else:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT 1")
            conn.close()
            return {"status": "healthy", "data_source": "postgres", "database": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "data_source": "postgres", "error": str(e)}


@app.post("/query")
async def query(request: QueryRequest):
    """Query CRM for client information."""
    if USE_JSON:
        return load_client_data_json(request.client_name)
    else:
        return load_client_data_postgres(request.client_name)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
