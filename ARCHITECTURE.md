# PreCall Briefing: Technical Architecture

**Project:** Pods, Prompts & Prototypes Hackathon  
**Challenge Tier:** Advanced (Multi-Agent Orchestration)  
**Date:** Saturday, March 22, 2026

---

## The Problem

Senior reps get pulled into client calls at the last minute. They juggle multiple accounts and can't remember every detail. They scramble through CRM, email, Slack, shared drives, and dashboards trying to piece together:

- What's the deal stage? Who are the stakeholders?
- What did we discuss last time? Any open action items?
- How are their metrics trending? Any red flags?
- What proposals or documents are active?

This takes 15-30 minutes of context-gathering before a 30-minute call.

## The Solution

**PreCall Briefing** is a multi-agent system that automatically pulls context from multiple sources and generates a concise, scannable briefing document. Input: meeting invite (client name + topic). Output: everything you need to know in 60 seconds.

---

## Architecture Overview

```
                    ┌─────────────────────┐
                    │   Meeting Invite    │
                    │  (client + topic)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │    Orchestrator     │
                    │  LangChain + Qwen3  │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    ┌───────────┐        ┌───────────┐        ┌───────────┐
    │CRM Agent  │        │Email Agent│        │Docs Agent │
    │           │        │           │        │           │
    │Salesforce │        │Gmail/Slack│        │Drive/     │
    │mock data  │        │threads    │        │Docling    │
    └─────┬─────┘        └─────┬─────┘        └─────┬─────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Briefing Generator │
                    │   Synthesize all    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  PreCall Briefing   │
                    │  (Markdown output)  │
                    └─────────────────────┘
```

---

## Team Split (3 People)

| Person | Owns | Folders |
|--------|------|---------|
| **Sanidhya** | Orchestrator + Compose + Integration | `/orchestrator`, `podman-compose.yml` |
| **Person 2** | CRM Agent + Email Agent | `/agents/crm`, `/agents/email` |
| **Person 3** | Docs Agent + UI + Demo | `/agents/docs`, `/ui`, demo materials |

---

## Component Specifications

### 1. Orchestrator

**Port:** 8000  
**Framework:** FastAPI + LangChain  
**Responsibility:** Coordinate agents, aggregate results, generate briefing

**API Contract:**

```
POST /briefing
Content-Type: application/json

Request:
{
  "client_name": "Acme Corp",
  "meeting_topic": "Q1 Review",
  "meeting_time": "2026-03-22T14:00:00Z"
}

Response:
{
  "briefing": "# PreCall Briefing: Acme Corp\n\n## Quick Facts\n...",
  "sources_used": ["crm", "email", "docs"],
  "generation_time_ms": 3200
}
```

**Internal Flow:**
1. Parse meeting invite
2. Fan out to agents in parallel (CRM, Email, Docs, Analytics)
3. Collect responses
4. Call Qwen3 to synthesize into briefing
5. Return formatted markdown

---

### 2. CRM Agent

**Port:** 8001  
**Responsibility:** Fetch client info, deal stage, stakeholders, recent activity

**API Contract:**

```
POST /query
{
  "client_name": "Acme Corp"
}

Response:
{
  "client": {
    "name": "Acme Corp",
    "industry": "Manufacturing",
    "deal_stage": "Negotiation",
    "deal_value": "$450,000",
    "close_date": "2026-04-15",
    "owner": "Sarah Chen"
  },
  "stakeholders": [
    {"name": "John Smith", "role": "VP Engineering", "sentiment": "Champion"},
    {"name": "Lisa Park", "role": "CFO", "sentiment": "Neutral"}
  ],
  "recent_activity": [
    {"date": "2026-03-18", "type": "Call", "note": "Discussed pricing concerns"},
    {"date": "2026-03-10", "type": "Email", "note": "Sent revised proposal"}
  ]
}
```

---

### 3. Email Agent

**Port:** 8002  
**Responsibility:** Fetch recent email threads, extract key points and action items

**API Contract:**

```
POST /query
{
  "client_name": "Acme Corp",
  "days_back": 14
}

Response:
{
  "threads": [
    {
      "subject": "Re: Q1 Review Prep",
      "participants": ["john.smith@acme.com", "sarah.chen@ourcompany.com"],
      "last_message_date": "2026-03-20",
      "summary": "John requested updated ROI projections before the call",
      "action_items": ["Send ROI deck by Thursday"]
    }
  ],
  "sentiment": "Positive",
  "urgency": "Medium"
}
```

---

### 4. Docs Agent

**Port:** 8003  
**Responsibility:** Find and summarize relevant documents (proposals, SOWs, meeting notes)

**API Contract:**

```
POST /query
{
  "client_name": "Acme Corp",
  "doc_types": ["proposal", "meeting_notes", "sow"]
}

Response:
{
  "documents": [
    {
      "title": "Acme Corp - Proposal v3",
      "type": "proposal",
      "last_modified": "2026-03-15",
      "summary": "3-year enterprise license, $450K total, includes implementation",
      "key_terms": ["Net 30 payment", "99.9% SLA", "24/7 support"]
    },
    {
      "title": "Acme Meeting Notes - March 10",
      "type": "meeting_notes", 
      "summary": "Discussed timeline concerns. John wants go-live by Q2.",
      "open_items": ["Confirm implementation timeline", "Schedule technical deep-dive"]
    }
  ]
}
```

---

### 5. Analytics Agent (Optional/Stretch)

**Port:** 8004  
**Responsibility:** Fetch recent metrics, charts, trends for the client

**API Contract:**

```
POST /query
{
  "client_name": "Acme Corp"
}

Response:
{
  "metrics": {
    "usage_trend": "up_15_percent",
    "health_score": 85,
    "nps": 42
  },
  "chart_summary": "Usage increased 15% MoM. No support tickets in 30 days.",
  "alerts": []
}
```

---

### 6. UI

**Port:** 8501  
**Framework:** Streamlit  
**Responsibility:** Input meeting details, display generated briefing

**Features:**
- Text inputs for client name and meeting topic
- "Generate Briefing" button
- Rendered markdown output with sections
- Copy-to-clipboard button
- Generation time indicator

---

## Briefing Output Format

```markdown
# PreCall Briefing: Acme Corp
**Meeting:** Q1 Review | March 22, 2026 at 2:00 PM

---

## At a Glance
| Field | Value |
|-------|-------|
| Deal Stage | Negotiation |
| Deal Value | $450,000 |
| Expected Close | April 15, 2026 |
| Account Owner | Sarah Chen |
| Health Score | 85/100 |

---

## Key Stakeholders

**John Smith** - VP Engineering (Champion)
- Primary technical decision maker
- Wants go-live by Q2

**Lisa Park** - CFO (Neutral)  
- Concerned about ROI justification
- Hasn't been in recent calls

---

## Recent Context

### Last Interaction (March 18)
Call with John Smith. Discussed pricing concerns and implementation timeline.

### Open Action Items
- [ ] Send updated ROI projections (requested March 20)
- [ ] Confirm implementation timeline
- [ ] Schedule technical deep-dive with engineering team

---

## Active Documents
- **Proposal v3** (March 15): 3-year enterprise license, $450K
- **Meeting Notes** (March 10): Timeline concerns, Q2 go-live target

---

## Talking Points
1. Address ROI concerns with updated projections
2. Confirm Q2 go-live is achievable
3. Offer technical deep-dive to build engineering confidence
4. Gauge Lisa's concerns before negotiation phase

---

*Generated in 3.2 seconds from 4 sources*
```

---

## Folder Structure

```
/precall-briefing
├── podman-compose.yml
├── README.md
├── ARCHITECTURE.md
├── .env.example
│
├── orchestrator/
│   ├── Containerfile
│   ├── main.py
│   ├── chains.py          # LangChain orchestration
│   ├── prompts.py         # System prompts
│   └── requirements.txt
│
├── agents/
│   ├── crm/
│   │   ├── Containerfile
│   │   ├── agent.py
│   │   └── requirements.txt
│   ├── email/
│   │   ├── Containerfile
│   │   ├── agent.py
│   │   └── requirements.txt
│   └── docs/
│       ├── Containerfile
│       ├── agent.py
│       └── requirements.txt
│
├── ui/
│   ├── Containerfile
│   ├── app.py
│   └── requirements.txt
│
└── data/                   # Mock data for demo
    ├── crm/
    │   └── acme_corp.json
    ├── emails/
    │   └── acme_threads.json
    └── documents/
        ├── acme_proposal_v3.json
        └── acme_meeting_notes.json
```

---

## Podman Compose

```yaml
version: "3.8"

services:
  orchestrator:
    build: ./orchestrator
    ports:
      - "8000:8000"
    environment:
      - LLM_URL=http://host.containers.internal:8080
      - CRM_AGENT_URL=http://crm-agent:8001
      - EMAIL_AGENT_URL=http://email-agent:8002
      - DOCS_AGENT_URL=http://docs-agent:8003
    depends_on:
      - crm-agent
      - email-agent
      - docs-agent
    networks:
      - briefing-net

  crm-agent:
    build: ./agents/crm
    ports:
      - "8001:8001"
    volumes:
      - ./data/crm:/app/data:ro
    networks:
      - briefing-net

  email-agent:
    build: ./agents/email
    ports:
      - "8002:8002"
    volumes:
      - ./data/emails:/app/data:ro
    networks:
      - briefing-net

  docs-agent:
    build: ./agents/docs
    ports:
      - "8003:8003"
    volumes:
      - ./data/documents:/app/data:ro
    networks:
      - briefing-net

  ui:
    build: ./ui
    ports:
      - "8501:8501"
    environment:
      - ORCHESTRATOR_URL=http://orchestrator:8000
    depends_on:
      - orchestrator
    networks:
      - briefing-net

networks:
  briefing-net:
    driver: bridge
```

---

## Demo Scenario

**Setup:** Senior sales rep has a Q1 review call with Acme Corp in 10 minutes.

**Input:**
- Client: Acme Corp
- Meeting: Q1 Review

**Demo flow:**
1. Rep opens PreCall Briefing UI
2. Enters "Acme Corp" and "Q1 Review"
3. Clicks Generate
4. System shows progress (fetching from CRM... emails... docs...)
5. Briefing appears in ~3-5 seconds
6. Rep scans the "At a Glance" table, sees deal stage and value
7. Checks "Open Action Items" - realizes they never sent the ROI deck
8. Reviews "Talking Points" for the call

**Key demo moments:**
- Show the briefing populating in real-time
- Point out the action item that would have been missed
- Show the "Generated from 4 sources" footer

---

## Pre-Saturday Checklist

### Sanidhya
- [ ] Qwen3-4B running in Podman AI Lab on port 8080
- [ ] Create mock data files for Acme Corp
- [ ] Test orchestrator locally
- [ ] Note laptop IP for teammates

### Person 2
- [ ] Implement CRM agent with mock data lookup
- [ ] Implement Email agent with thread summarization

### Person 3
- [ ] Implement Docs agent with document summaries
- [ ] Build Streamlit UI
- [ ] Prepare demo script and concept brief
