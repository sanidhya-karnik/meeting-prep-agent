"""
CRM Agent for PreCall Briefing

Fetches client info, deal stage, stakeholders, and recent activity from PostgreSQL.
Mimics Salesforce-like data structure.
"""

import os
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="CRM Agent")

# Database connection settings
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "crm")
DB_USER = os.getenv("DB_USER", "crm_user")
DB_PASS = os.getenv("DB_PASS", "crm_pass")


class QueryRequest(BaseModel):
    client_name: str


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


def fetch_client_data(client_name: str) -> dict:
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


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/query")
async def query(request: QueryRequest):
    """Query CRM for client information."""
    return fetch_client_data(request.client_name)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
