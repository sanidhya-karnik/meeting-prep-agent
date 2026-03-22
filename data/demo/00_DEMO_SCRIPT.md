# Kairo Demo Script (2 Minutes)

## Setup Before Recording
- Have these windows ready:
  1. VS Code with `data/demo/` folder open (formatted markdown files)
  2. Browser with Kairo UI at http://localhost:8501
  3. Terminal showing services running (optional)

- Files to show in order:
  - `01_CRM_Data.md`
  - `02_Slack_Threads.md`
  - `03_Documents.md`
  - `04_Analytics_Dashboards.md`

---

## INTRO (0:00 - 0:20)

**[Screen: Architecture diagram or title slide]**

> "Meet Kairo, an AI-powered meeting prep agent built for the Pods, Prompts and Prototypes hackathon.
>
> Sales reps juggle dozens of accounts. Before a client call, they scramble through CRM, Slack, shared docs, and dashboards trying to piece together context. This takes 15 to 30 minutes.
>
> Kairo solves this. Enter a client name, get a complete briefing in seconds."

---

## SHOW THE DATA (0:20 - 0:50)

**[Screen: VS Code - data/demo folder]**

> "Let me show you the data sources Kairo pulls from."

**[Open `01_CRM_Data.md` - scroll through]**
> "First, CRM data. Here's Acme Corp: a $450,000 deal in negotiation stage. Three stakeholders with different sentiments. John is our champion, Lisa the CFO is neutral, and there's active competitor pressure from TechRival."

**[Open `02_Slack_Threads.md` - scroll to pending items]**
> "Next, Slack conversations. Notice John requested ROI projections by Thursday, and asked for a TCO comparison to justify us over the competitor. These are still pending."

**[Open `03_Documents.md` - scroll to open items]**
> "Documents: the proposal with pricing terms, and meeting notes with open action items."

**[Open `04_Analytics_Dashboards.md` - scroll through]**
> "And analytics dashboards showing usage trends, health scores, and support metrics. The customer has 85/100 health score, 62% user growth, and zero support tickets. These insights will be analyzed by Docling and surfaced in the briefing."

---

## GENERATE BRIEFING (0:50 - 1:20)

**[Screen: Browser - Kairo UI]**

> "Now let's see Kairo in action."

**[Type "Acme Corp" in client field, "Q1 Review" in topic]**

> "I'll enter Acme Corp and Q1 Review as the meeting topic."

**[Click Generate Briefing button]**

> "Kairo now queries four specialized agents in parallel: CRM, Communications, Documents, and Analytics. Each agent extracts relevant information, and IBM Granite synthesizes it into a structured briefing."

**[Wait for results to load]**

---

## EXPLAIN THE OUTPUT (1:20 - 1:55)

**[Screen: Generated briefing with cards]**

> "Here's the output. Notice the card-based layout with everything visible at a glance."

**[Point to Deal Journey]**
> "The deal journey shows we're in Negotiation stage."

**[Point to At a Glance card]**
> "At a Glance gives me the key numbers: $450K deal, 75% probability, health score of 85."

**[Point to citation badges]**
> "These citation badges show exactly where each piece of information came from, whether it's CRM, Slack, or Documents."

**[Point to Priority Discussion Topics]**
> "Priority Discussion Topics tells me what to cover. Number one: send those ROI projections John requested. This is something I would have missed without Kairo."

**[Point to Suggested Opening Script]**
> "And the Suggested Opening Script gives me personalized conversation starters based on context."

---

## CLOSING (1:55 - 2:00)

> "That's Kairo. From scattered data to meeting-ready in 20 seconds. Built with IBM Granite, FastAPI, Streamlit, and Podman."

**[End]**

---

## Key Points to Hit
- **Problem**: Reps waste 15-30 min prepping for calls
- **Solution**: Multi-agent system that synthesizes CRM + Slack + Docs + Analytics
- **Tech**: IBM Granite LLM, FastAPI orchestration, Podman containers
- **"Aha" moment**: ROI projections were requested but never sent (shows up in Slack AND Docs)
- **Citations**: Every piece of info traceable to its source

## Demo Files in This Folder
```
data/demo/
├── 00_DEMO_SCRIPT.md          # This script
├── 01_CRM_Data.md             # Company, deal, stakeholders, health
├── 02_Slack_Threads.md        # Conversations with pending items
├── 03_Documents.md            # Proposal terms, meeting notes, open items
└── 04_Analytics_Dashboards.md # Usage trends, health scores, support metrics
```

## Tips
- Use VS Code Preview mode (Ctrl+Shift+V) to show formatted markdown
- Speak at a steady pace
- Pause briefly when switching screens
- Keep mouse movements smooth
- Emphasize the "aha" moment: ROI projections requested but not sent
