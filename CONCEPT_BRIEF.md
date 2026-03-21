# Meeting Prep Agent
## One-Page Concept Brief

**Team:** [Your Team Name]  
**Challenge Tier:** Advanced (Multi-Agent Orchestration)  
**Hackathon:** Pods, Prompts & Prototypes (Red Hat + IBM)

---

### The Problem

Senior sales reps manage dozens of accounts. When pulled into a call at the last minute, they scramble through CRM, Slack history, shared drives, and dashboards to piece together context. This takes 15-30 minutes - time they don't have.

**The real cost:** Reps walk into calls unprepared, miss critical context, and forget follow-up items. Deals slip.

---

### The Solution

**Meeting Prep Agent** generates a complete client briefing in seconds.

Enter client name → System queries 4 data sources in parallel → LLM synthesizes a scannable briefing.

**What the briefing includes:**
- Deal status, value, close date, probability
- Key stakeholders with sentiment (Champion/Neutral/Detractor)
- Recent interactions and open action items
- Active proposals and meeting notes
- Usage trends and health score
- Recommended talking points

---

### How It Works

```
User Input: "Acme Corp" + "Q1 Review"
                    │
                    ▼
        ┌─────────────────────┐
        │    Orchestrator     │
        │  (LangChain + Qwen3)│
        └──────────┬──────────┘
                   │ parallel queries
    ┌──────┬───────┼───────┬──────┐
    ▼      ▼       ▼       ▼      
  CRM    Slack    Docs   Charts   
(Postgres) (JSON) (Docling) (PNG)  
    │      │       │       │      
    └──────┴───────┴───────┴──────┘
                   │
                   ▼
           Synthesized Briefing
```

**4 specialized agents** run in parallel:
1. **CRM Agent** - SQL queries against PostgreSQL (client, contacts, deals, activities)
2. **Comms Agent** - Parses Slack export JSON for recent conversations
3. **Docs Agent** - Reads PDF/DOCX with Docling, extracts summaries and action items
4. **Analytics Agent** - Loads chart images with pre-computed descriptions

---

### Design Decisions

| Choice | Rationale |
|--------|-----------|
| **Docling for doc parsing** | IBM open-source, preserves document structure, enables citations |
| **PostgreSQL for CRM** | Real database queries, demonstrates production-ready architecture |
| **Parallel agent execution** | Reduces latency from ~12s (serial) to ~4s |
| **Local LLM (Qwen3-4B)** | No API costs, runs in Podman AI Lab, fast inference |
| **Podman Compose** | Rootless containers, Red Hat ecosystem alignment |

---

### Tech Stack

- **LLM:** Qwen3-4B-Thinking (Podman AI Lab, port 8080)
- **Orchestration:** LangChain + FastAPI (Python)
- **Database:** PostgreSQL 15
- **Document Parsing:** Docling (IBM)
- **Containers:** Podman Compose
- **UI:** Streamlit

---

### Demo Scenario

**Setup:** Sarah has a Q1 review call with Acme Corp in 10 minutes. The CFO is joining for the first time.

**What the system surfaces:**
- $450K deal in Negotiation stage, 75% close probability
- John Smith is the Champion; Lisa Park (CFO) is Neutral - needs ROI justification
- **Critical:** ROI projections John requested were never sent (action item from Slack)
- Competitor TechRival submitted a lower quote - need TCO comparison ready
- Health score is 85/100, usage up 62% - strong engagement to reference

**The insight:** Without Meeting Prep Agent, Sarah would have walked into the call without the ROI deck Lisa is expecting.

---

### Why It Matters

This isn't about generating text. It's about **grounding every recommendation in your organization's actual data**.

The system retrieves, synthesizes, and cites - it doesn't hallucinate. Every talking point traces back to a CRM record, a Slack message, or a document section.

**For the judges:** This demonstrates true multi-agent orchestration with heterogeneous data sources, multimodal inputs (documents + charts), and practical enterprise value.

---

### Links

- **GitHub:** [your-repo-url]
- **Demo Video:** [youtube-url]
