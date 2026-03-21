"""
PreCall Briefing Orchestrator

Coordinates multiple agents to gather context and generate briefings.
Uses LangChain for orchestration and Qwen3 for synthesis.
"""

import os
import asyncio
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="PreCall Briefing Orchestrator")

# Configuration
LLM_URL = os.getenv("LLM_URL", "http://host.containers.internal:8080")
CRM_AGENT_URL = os.getenv("CRM_AGENT_URL", "http://crm-agent:8001")
COMMS_AGENT_URL = os.getenv("COMMS_AGENT_URL", "http://comms-agent:8002")
DOCS_AGENT_URL = os.getenv("DOCS_AGENT_URL", "http://docs-agent:8003")
ANALYTICS_AGENT_URL = os.getenv("ANALYTICS_AGENT_URL", "http://analytics-agent:8004")

# System prompt for briefing generation
BRIEFING_SYSTEM_PROMPT = """You are an expert at creating concise, actionable pre-call briefings for sales representatives.

Given context from multiple sources (CRM, Slack/email, documents, analytics), synthesize a briefing that helps the rep prepare for their call in under 60 seconds of reading.

Output format MUST be valid Markdown with these sections:
1. **At a Glance** - Key facts table (deal stage, value, close date, owner, health score)
2. **Key Stakeholders** - Who's who, their role, and sentiment (Champion/Neutral/Detractor)
3. **Recent Context** - What happened in the last interaction, any urgent items
4. **Open Action Items** - Checkbox list of things that need to be done
5. **Active Documents** - Relevant proposals, contracts, meeting notes
6. **Analytics Snapshot** - Key metrics, trends, and health indicators
7. **Talking Points** - 3-5 recommended topics for the call based on the context

Keep it scannable. Use bullet points. Bold important items. The rep has 2 minutes to read this before the call.

IMPORTANT: Do not make up information. Only include what's provided in the context."""


class BriefingRequest(BaseModel):
    client_name: str
    meeting_topic: Optional[str] = "General Check-in"
    meeting_time: Optional[str] = None


class BriefingResponse(BaseModel):
    briefing: str
    sources_used: list[str]
    generation_time_ms: int


# ============================================================================
# Agent Clients
# ============================================================================

async def query_crm_agent(client_name: str) -> dict:
    """Query CRM agent for client data from PostgreSQL."""
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

async def call_llm(messages: list[dict], temperature: float = 0.3) -> str:
    """Call Qwen3 for briefing generation."""
    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(
            f"{LLM_URL}/v1/chat/completions",
            json={
                "model": "qwen/Qwen3-4B-Thinking-2507-GGUF",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 2000
            }
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


# ============================================================================
# Briefing Generation
# ============================================================================

def format_context(crm_data: dict, comms_data: dict, docs_data: dict, analytics_data: dict) -> str:
    """Format all agent responses into a context string for the LLM."""
    sections = []
    
    # CRM Context
    if "error" not in crm_data:
        sections.append("## CRM DATA (PostgreSQL)")
        if "client" in crm_data:
            c = crm_data["client"]
            sections.append(f"Client: {c.get('name', 'Unknown')}")
            sections.append(f"Industry: {c.get('industry', 'Unknown')}")
        
        if "deal" in crm_data and crm_data["deal"]:
            d = crm_data["deal"]
            sections.append(f"Deal Stage: {d.get('stage', 'Unknown')}")
            sections.append(f"Deal Value: {d.get('value', 'Unknown')}")
            sections.append(f"Close Date: {d.get('close_date', 'Unknown')}")
            sections.append(f"Probability: {d.get('probability', 'Unknown')}%")
            sections.append(f"Owner: {d.get('owner', 'Unknown')}")
            if d.get('competitor'):
                sections.append(f"Competitor: {d.get('competitor')}")
        
        if "stakeholders" in crm_data:
            sections.append("\nStakeholders:")
            for s in crm_data["stakeholders"]:
                sections.append(f"- {s.get('name')}: {s.get('role')} ({s.get('sentiment')})")
                if s.get('notes'):
                    sections.append(f"  Notes: {s.get('notes')}")
        
        if "recent_activity" in crm_data:
            sections.append("\nRecent Activity:")
            for a in crm_data["recent_activity"][:5]:
                sections.append(f"- {a.get('date')} [{a.get('type')}]: {a.get('note')}")
                if a.get('next_steps'):
                    sections.append(f"  Next Steps: {a.get('next_steps')}")
        
        if "health_indicators" in crm_data and crm_data["health_indicators"]:
            h = crm_data["health_indicators"]
            sections.append(f"\nHealth Score: {h.get('engagement_score', 'N/A')}/100")
            sections.append(f"Risk Level: {h.get('risk_level', 'Unknown')}")
    
    # Communications Context (Slack)
    if "error" not in comms_data:
        sections.append("\n## SLACK CONVERSATIONS")
        if "channel" in comms_data:
            ch = comms_data["channel"]
            sections.append(f"Channel: #{ch.get('name', 'unknown')}")
        
        if "threads" in comms_data:
            for t in comms_data["threads"][:2]:
                sections.append(f"\nRecent Messages ({t.get('message_count', 0)} messages):")
                if "messages" in t:
                    for m in t["messages"][:5]:
                        sender = m.get('from', 'Unknown')
                        internal = "(internal)" if m.get('is_internal') else "(external)"
                        sections.append(f"- {sender} {internal}: {m.get('text', '')[:200]}")
        
        if "action_items" in comms_data:
            sections.append("\nPending Action Items from Slack:")
            for item in comms_data["action_items"]:
                sections.append(f"  - {item}")
        
        if "summary" in comms_data:
            s = comms_data["summary"]
            if s.get("key_topics"):
                sections.append(f"\nKey Topics: {', '.join(s.get('key_topics', []))}")
            sections.append(f"Sentiment: {s.get('sentiment', 'neutral')}")
    
    # Documents Context
    if "error" not in docs_data:
        sections.append("\n## DOCUMENTS (Docling)")
        if "documents" in docs_data:
            for d in docs_data["documents"][:4]:
                sections.append(f"\n{d.get('title')} ({d.get('type')})")
                sections.append(f"Last Modified: {d.get('last_modified')}")
                if d.get('summary'):
                    sections.append(f"Summary: {d.get('summary')}")
                if d.get("key_terms"):
                    sections.append(f"Key Terms: {', '.join(d.get('key_terms', [])[:5])}")
                if d.get("open_items"):
                    sections.append("Open Items:")
                    for item in d["open_items"]:
                        status = f" [{item.get('status')}]" if item.get('status') else ""
                        sections.append(f"  - {item.get('item')} (Owner: {item.get('owner')}){status}")
    
    # Analytics Context
    if "error" not in analytics_data:
        sections.append("\n## ANALYTICS (Charts)")
        if "charts" in analytics_data:
            for chart in analytics_data["charts"]:
                sections.append(f"\n{chart.get('chart_type', 'Chart').replace('_', ' ').title()}:")
                sections.append(f"{chart.get('description', 'No description')}")
        
        if "summary" in analytics_data and analytics_data["summary"]:
            sections.append(f"\nAnalytics Summary: {analytics_data['summary']}")
    
    return "\n".join(sections)


async def generate_briefing(client_name: str, meeting_topic: str) -> tuple[str, list[str]]:
    """Generate a pre-call briefing by querying all agents and synthesizing."""
    
    # Query all agents in parallel
    crm_task = query_crm_agent(client_name)
    comms_task = query_comms_agent(client_name)
    docs_task = query_docs_agent(client_name)
    analytics_task = query_analytics_agent(client_name)
    
    crm_data, comms_data, docs_data, analytics_data = await asyncio.gather(
        crm_task, comms_task, docs_task, analytics_task
    )
    
    # Track which sources returned data
    sources_used = []
    if "error" not in crm_data:
        sources_used.append("crm")
    if "error" not in comms_data:
        sources_used.append("slack")
    if "error" not in docs_data:
        sources_used.append("docs")
    if "error" not in analytics_data:
        sources_used.append("analytics")
    
    # Format context for LLM
    context = format_context(crm_data, comms_data, docs_data, analytics_data)
    
    # Generate briefing
    user_message = f"""Generate a pre-call briefing for the following meeting:

**Client:** {client_name}
**Meeting Topic:** {meeting_topic}

---

{context}

---

Generate the briefing now. Remember to include all sections: At a Glance, Key Stakeholders, Recent Context, Open Action Items, Active Documents, Analytics Snapshot, and Talking Points."""

    messages = [
        {"role": "system", "content": BRIEFING_SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    briefing = await call_llm(messages)
    
    # Add header
    header = f"# PreCall Briefing: {client_name}\n**Meeting:** {meeting_topic}\n\n---\n\n"
    
    return header + briefing, sources_used


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
        briefing, sources = await generate_briefing(
            request.client_name,
            request.meeting_topic
        )
        
        generation_time = int((time.time() - start_time) * 1000)
        
        # Add footer
        briefing += f"\n\n---\n*Generated in {generation_time/1000:.1f} seconds from {len(sources)} sources*"
        
        return BriefingResponse(
            briefing=briefing,
            sources_used=sources,
            generation_time_ms=generation_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
