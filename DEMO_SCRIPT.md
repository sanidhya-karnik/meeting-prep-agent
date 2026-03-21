# Meeting Prep Agent - Demo Script
## 2-Minute Video Guide

---

### Pre-Recording Checklist

- [ ] Qwen3-4B running in Podman AI Lab (port 8080)
- [ ] All containers running (`podman-compose up`)
- [ ] UI open at http://localhost:8501
- [ ] Screen recording software ready (OBS, Loom, or QuickTime)
- [ ] Microphone tested
- [ ] Browser zoom at 100%, dark mode off for visibility

---

### Script

#### [0:00 - 0:15] Hook

**[Show: Empty briefing UI]**

> "You're a senior sales rep. You have a call with Acme Corp in 10 minutes. The CFO is joining for the first time. Quick - what's the deal status? What did you promise last time? Any red flags?"

**[Pause for effect]**

> "That scramble through CRM, Slack, and shared drives? It takes 20 minutes you don't have. Let me show you a better way."

---

#### [0:15 - 0:30] Introduction

**[Show: UI with inputs visible]**

> "This is Meeting Prep Agent - a multi-agent system that generates complete client briefings in seconds."

> "I enter the client name: Acme Corp. The meeting topic: Q1 Review."

**[Type "Acme Corp" and "Q1 Review"]**

> "And click Generate."

**[Click the button]**

---

#### [0:30 - 1:15] Live Demo - The Money Shot

**[Show: Progress indicators as they update]**

> "Watch what happens. Four agents are now querying four different data sources - in parallel."

**[Point to each status as it appears]**

> "CRM agent hits PostgreSQL for client info and deal status..."
> "Comms agent parses our Slack channel with the client..."
> "Docs agent reads the proposal PDF and meeting notes using Docling..."
> "Analytics agent pulls the usage charts and health score..."

**[Briefing appears]**

> "And here's the briefing. Let's look at what it found."

**[Scroll through briefing, highlighting key sections]**

> "At a Glance: $450K deal, Negotiation stage, 75% probability. Owner is Sarah Chen."

> "Stakeholders: John Smith is our Champion. Lisa Park, the CFO joining today? She's Neutral - focused on ROI."

**[Point to action items]**

> "Here's the critical insight: John requested ROI projections on March 20th - and they were never sent. Without this briefing, I would have walked into a CFO call without the numbers she's expecting."

**[Point to analytics section]**

> "Analytics shows health score 85, usage up 62% over 6 months. That's my proof point for the ROI conversation."

---

#### [1:15 - 1:40] Architecture + Tech

**[Show: Architecture diagram or terminal with containers]**

> "Under the hood: five containers running in Podman Compose."

**[Quick terminal shot of `podman ps` or compose logs]**

> "PostgreSQL for CRM data. FastAPI agents for each data source. Streamlit for the UI. And Qwen3 running locally in Podman AI Lab - no API costs, no data leaving your machine."

> "The orchestrator coordinates everything with LangChain, querying all agents in parallel, then synthesizing with the LLM."

> "Document parsing uses Docling - IBM's open-source library - so we can extract structure from PDFs and Word docs."

---

#### [1:40 - 2:00] Wrap + Call to Action

**[Return to briefing view]**

> "Meeting Prep Agent turns 20 minutes of scrambling into 5 seconds of reading."

> "The agents are modular - swap PostgreSQL for Salesforce API, Slack exports for real Slack integration. The architecture scales."

> "This is multi-agent orchestration solving a real enterprise problem. Thanks for watching."

**[End on briefing with sources visible: CRM, Slack, Docs, Analytics]**

---

### Recording Tips

1. **Pace:** Speak slightly slower than normal - viewers can speed up but not slow down
2. **Cursor:** Use a cursor highlighter tool to make clicks visible
3. **Pauses:** Brief pauses before key reveals (briefing appearing, highlighting the missed action item)
4. **Energy:** The "aha moment" is the unsent ROI projections - emphasize it
5. **B-roll:** If time allows, quick cuts to terminal showing containers running adds credibility

### Backup Plan

If the LLM is slow or something breaks during recording:
- Pre-record a successful run as backup footage
- Have a static briefing screenshot ready
- Script can be delivered over the backup footage

---

### Rubric Alignment

| Criterion | How We Address It |
|-----------|------------------|
| **Multi-agent orchestration** | 4 specialized agents + 1 orchestrator, parallel execution |
| **Practical use case** | Universal pain point (meeting prep), clear ROI |
| **Technical depth** | PostgreSQL, Docling, LangChain, Podman Compose |
| **Demo quality** | Live generation, visible progress, highlighted insight |
| **Red Hat/IBM alignment** | Podman ecosystem, Docling (IBM), local-first |
