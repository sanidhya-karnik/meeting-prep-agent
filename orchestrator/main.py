"""
PreCall Briefing Orchestrator

Coordinates multiple agents to gather context and generate briefings.
Returns structured data with citations for card-based UI.
"""

import os
import asyncio
import time
from typing import Optional, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="PreCall Briefing Orchestrator")

# Configuration - defaults work for local development
LLM_URL = os.getenv("LLM_URL", "http://127.0.0.1:65354")
CRM_AGENT_URL = os.getenv("CRM_AGENT_URL", "http://127.0.0.1:8001")
COMMS_AGENT_URL = os.getenv("COMMS_AGENT_URL", "http://127.0.0.1:8002")
DOCS_AGENT_URL = os.getenv("DOCS_AGENT_URL", "http://127.0.0.1:8003")
ANALYTICS_AGENT_URL = os.getenv("ANALYTICS_AGENT_URL", "http://127.0.0.1:8004")

# System prompt for priority extraction
PRIORITY_PROMPT = """Based on the context, list the top 5 discussion topics for this call in order of urgency.
Consider: pending requests, unanswered questions, approaching deadlines, blockers, competitor mentions.
Return ONLY a numbered list, one item per line. Be specific and actionable.
Example format:
1. Address the ROI projections request from last call
2. Clarify timeline concerns before contract review
3. Discuss competitor pricing comparison"""


class BriefingRequest(BaseModel):
    client_name: str
    meeting_topic: Optional[str] = "General Check-in"
    meeting_time: Optional[str] = None


class BriefingResponse(BaseModel):
    briefing: str
    sources_used: list[str]
    generation_time_ms: int
    structured_data: dict


# ============================================================================
# Agent Clients
# ============================================================================

async def query_crm_agent(client_name: str) -> dict:
    """Query CRM agent for client data."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{CRM_AGENT_URL}/query",
                json={"client_name": client_name}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"CRM agent error: {e}")
        return {"error": str(e)}


async def query_comms_agent(client_name: str) -> dict:
    """Query Communications agent for Slack/email threads."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{COMMS_AGENT_URL}/query",
                json={"client_name": client_name, "days_back": 14}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Comms agent error: {e}")
        return {"error": str(e)}


async def query_docs_agent(client_name: str) -> dict:
    """Query Docs agent for relevant documents."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{DOCS_AGENT_URL}/query",
                json={"client_name": client_name}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Docs agent error: {e}")
        return {"error": str(e)}


async def query_analytics_agent(client_name: str) -> dict:
    """Query Analytics agent for charts and metrics."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ANALYTICS_AGENT_URL}/query",
                json={"client_name": client_name, "include_images": False}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Analytics agent error: {e}")
        return {"error": str(e)}


# ============================================================================
# LLM Client
# ============================================================================

async def call_llm(messages: list[dict], temperature: float = 0.3, max_tokens: int = 500) -> str:
    """Call local LLM."""
    try:
        print(f"Calling LLM at {LLM_URL}...")
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{LLM_URL}/v1/chat/completions",
                json={
                    "model": "ibm-granite/granite-4.0-micro-GGUF",
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            print(f"LLM response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"LLM call error: {type(e).__name__}: {e}")
        raise


# ============================================================================
# Structured Data Builder
# ============================================================================

def build_structured_data(
    client_name: str,
    crm_data: dict,
    comms_data: dict,
    docs_data: dict,
    analytics_data: dict
) -> dict:
    """Build structured data for card-based UI with citations."""
    
    structured = {
        "client_name": client_name,
        "deal": {},
        "health": {},
        "stakeholders": [],
        "priorities": [],
        "recent_context": [],
        "documents": [],
        "talking_points": [],
        "opening_script": []
    }
    
    # === Deal Info (from CRM) ===
    if "error" not in crm_data:
        if "deal" in crm_data and crm_data["deal"]:
            d = crm_data["deal"]
            structured["deal"] = {
                "stage": d.get("stage", "Unknown"),
                "value": d.get("value", "N/A"),
                "close_date": d.get("close_date", "N/A"),
                "probability": d.get("probability", "N/A"),
                "owner": d.get("owner", "N/A"),
                "competitor": d.get("competitor", "None")
            }
        
        # Stakeholders
        if "stakeholders" in crm_data:
            for s in crm_data["stakeholders"][:4]:
                structured["stakeholders"].append({
                    "name": s.get("name", ""),
                    "role": s.get("role", ""),
                    "sentiment": s.get("sentiment", "Neutral"),
                    "notes": s.get("notes", ""),
                    "source": "crm"
                })
        
        # Recent activity as context
        if "recent_activity" in crm_data:
            for a in crm_data["recent_activity"][:2]:
                structured["recent_context"].append({
                    "text": f"{a.get('type', 'Activity')}: {a.get('note', '')[:100]}",
                    "source": "crm",
                    "detail": a.get("next_steps", "")
                })
        
        # Health indicators
        if "health_indicators" in crm_data and crm_data["health_indicators"]:
            h = crm_data["health_indicators"]
            structured["health"] = {
                "score": h.get("engagement_score", "N/A"),
                "risk": h.get("risk_level", "Unknown"),
                "trend": h.get("usage_trend", "stable"),
                "tickets": h.get("support_tickets_open", 0)
            }
    
    # === Slack Context ===
    if "error" not in comms_data:
        # Recent messages
        if "threads" in comms_data:
            for t in comms_data["threads"][:1]:
                if "messages" in t:
                    for m in t["messages"][:2]:
                        sender = m.get('from', 'Unknown')
                        text = m.get('text', '')[:100]
                        structured["recent_context"].append({
                            "text": f"{sender}: {text}",
                            "source": "slack",
                            "detail": f"#{comms_data.get('channel', {}).get('name', 'channel')}"
                        })
        
        # Action items become priorities
        if "action_items" in comms_data:
            for item in comms_data["action_items"][:2]:
                structured["priorities"].append({
                    "topic": item,
                    "source": "slack",
                    "detail": "Pending from Slack"
                })
    
    # === Documents ===
    if "error" not in docs_data:
        if "documents" in docs_data:
            for d in docs_data["documents"][:3]:
                doc_entry = {
                    "title": d.get("title", "Document"),
                    "type": d.get("type", "unknown"),
                    "summary": d.get("summary", "")[:120],
                    "source": "docs"
                }
                structured["documents"].append(doc_entry)
                
                # Open items from docs become priorities
                if "open_items" in d:
                    for item in d["open_items"][:2]:
                        structured["priorities"].append({
                            "topic": f"{item.get('item', '')} (Owner: {item.get('owner', 'TBD')})",
                            "source": "docs",
                            "detail": d.get("title", "Document")
                        })
    
    # === Analytics ===
    if "error" not in analytics_data:
        if "charts" in analytics_data:
            for chart in analytics_data["charts"][:2]:
                # Add chart insights as talking points
                structured["talking_points"].append({
                    "point": chart.get("description", "")[:80],
                    "source": "analytics"
                })
    
    # === Build Priority List (dedupe and limit) ===
    # Move CRM next_steps to priorities
    if "error" not in crm_data and "recent_activity" in crm_data:
        for a in crm_data["recent_activity"][:2]:
            if a.get("next_steps"):
                structured["priorities"].insert(0, {
                    "topic": a.get("next_steps"),
                    "source": "crm",
                    "detail": f"From {a.get('type', 'activity')}"
                })
    
    # Limit priorities to top 5
    structured["priorities"] = structured["priorities"][:5]
    
    # === Add default talking points ===
    if structured["deal"].get("competitor"):
        structured["talking_points"].append({
            "point": f"Address competitive positioning vs {structured['deal']['competitor']}",
            "source": "crm"
        })
    
    if structured["health"].get("score") and structured["health"]["score"] != "N/A":
        score = structured["health"]["score"]
        if score >= 80:
            structured["talking_points"].append({
                "point": "Acknowledge strong engagement and explore expansion opportunities",
                "source": "analytics"
            })
        elif score < 60:
            structured["talking_points"].append({
                "point": "Address engagement concerns and identify blockers",
                "source": "analytics"
            })
    
    # Limit talking points
    structured["talking_points"] = structured["talking_points"][:4]
    
    # === Build Opening Script based on context ===
    # Get primary contact name
    primary_contact = structured["stakeholders"][0]["name"] if structured["stakeholders"] else "there"
    
    # Personalized openers based on recent context
    if structured["recent_context"]:
        recent = structured["recent_context"][0]["text"]
        if "pricing" in recent.lower() or "discount" in recent.lower():
            structured["opening_script"].append({
                "line": f"Hi {primary_contact}, thanks for making time today. I wanted to follow up on our pricing discussion and make sure we're aligned on the value we're bringing.",
                "source": "slack"
            })
        elif "proposal" in recent.lower():
            structured["opening_script"].append({
                "line": f"Hi {primary_contact}, great to connect again. I know you've had a chance to review the proposal - I'd love to hear your thoughts and address any questions.",
                "source": "docs"
            })
        else:
            structured["opening_script"].append({
                "line": f"Hi {primary_contact}, thanks for joining. Before we dive in, I wanted to check - how are things going on your end?",
                "source": "crm"
            })
    
    # Add context-aware follow-up
    if structured["priorities"]:
        top_priority = structured["priorities"][0]["topic"]
        structured["opening_script"].append({
            "line": f"I want to make sure we cover {top_priority[:50]}{'...' if len(top_priority) > 50 else ''} today - that seemed important from our last conversation.",
            "source": structured["priorities"][0].get("source", "crm")
        })
    
    # Add stakeholder-aware line if CFO or exec is involved
    for s in structured["stakeholders"]:
        if "cfo" in s.get("role", "").lower() or "ceo" in s.get("role", "").lower():
            if s.get("sentiment") == "Neutral":
                structured["opening_script"].append({
                    "line": f"I'm also keen to address any ROI or budget concerns {s['name']} might have - I've prepared some numbers to share.",
                    "source": "crm"
                })
            break
    
    return structured


def format_context_for_llm(structured: dict) -> str:
    """Format structured data as context for LLM."""
    lines = []
    
    # Deal info
    d = structured.get("deal", {})
    if d:
        lines.append(f"Deal: {d.get('stage')} stage, {d.get('value')}, closes {d.get('close_date')}")
        if d.get("competitor") and d["competitor"] != "None":
            lines.append(f"Competitor: {d['competitor']}")
    
    # Stakeholders
    for s in structured.get("stakeholders", [])[:3]:
        lines.append(f"Stakeholder: {s['name']} ({s['role']}) - {s['sentiment']}")
    
    # Recent context
    for c in structured.get("recent_context", [])[:3]:
        lines.append(f"Recent: {c['text']}")
    
    # Documents
    for doc in structured.get("documents", [])[:2]:
        lines.append(f"Document: {doc['title']} - {doc['summary'][:60]}")
    
    return "\n".join(lines)


# ============================================================================
# Briefing Generation
# ============================================================================

async def generate_briefing(client_name: str, meeting_topic: str) -> tuple[str, list[str], dict]:
    """Generate a pre-call briefing with structured data."""
    
    # Query all agents in parallel
    crm_task = query_crm_agent(client_name)
    comms_task = query_comms_agent(client_name)
    docs_task = query_docs_agent(client_name)
    analytics_task = query_analytics_agent(client_name)
    
    crm_data, comms_data, docs_data, analytics_data = await asyncio.gather(
        crm_task, comms_task, docs_task, analytics_task
    )
    
    # Track sources
    sources_used = []
    if "error" not in crm_data:
        sources_used.append("crm")
    if "error" not in comms_data:
        sources_used.append("slack")
    if "error" not in docs_data:
        sources_used.append("docs")
    if "error" not in analytics_data:
        sources_used.append("analytics")
    
    # Build structured data
    structured = build_structured_data(
        client_name, crm_data, comms_data, docs_data, analytics_data
    )
    
    # Generate LLM summary (brief)
    context = format_context_for_llm(structured)
    messages = [
        {"role": "system", "content": "Create a 2-3 sentence executive summary for this client meeting. Be specific and actionable."},
        {"role": "user", "content": f"Client: {client_name}\nTopic: {meeting_topic}\n\n{context}"}
    ]
    
    try:
        summary = await call_llm(messages, max_tokens=150)
    except:
        summary = "Unable to generate summary."
    
    # Build markdown briefing (for fallback/export)
    briefing = f"# PreCall Briefing: {client_name}\n\n"
    briefing += f"**Meeting:** {meeting_topic}\n\n"
    briefing += f"**Summary:** {summary}\n\n"
    briefing += "---\n\n"
    
    # Add sections
    d = structured.get("deal", {})
    briefing += "## At a Glance\n"
    briefing += f"- **Stage:** {d.get('stage', 'N/A')}\n"
    briefing += f"- **Value:** {d.get('value', 'N/A')}\n"
    briefing += f"- **Close Date:** {d.get('close_date', 'N/A')}\n"
    briefing += f"- **Health:** {structured.get('health', {}).get('score', 'N/A')}/100\n\n"
    
    briefing += "## Priority Discussion Topics\n"
    for i, p in enumerate(structured.get("priorities", [])[:5], 1):
        briefing += f"{i}. {p['topic']}\n"
    
    return briefing, sources_used, structured


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/briefing", response_model=BriefingResponse)
async def create_briefing(request: BriefingRequest):
    """Generate a pre-call briefing for a client."""
    start_time = time.time()
    
    try:
        briefing, sources, structured = await generate_briefing(
            request.client_name,
            request.meeting_topic
        )
        
        generation_time = int((time.time() - start_time) * 1000)
        
        return BriefingResponse(
            briefing=briefing,
            sources_used=sources,
            generation_time_ms=generation_time,
            structured_data=structured
        )
    except Exception as e:
        print(f"Briefing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
