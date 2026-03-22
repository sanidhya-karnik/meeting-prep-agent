"""
Kairo - AI Meeting Prep Agent

Professional Streamlit interface with card-based layout and source citations.
"""

import os
import time
import streamlit as st
import requests

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://127.0.0.1:8000")

# Page config
st.set_page_config(
    page_title="Kairo - Meeting Prep Agent",
    page_icon="K",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional Light Theme CSS
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .main {
        padding: 2rem 3rem;
        background-color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
    }
    
    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 32px 40px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .app-title {
        font-size: 36px;
        font-weight: 700;
        color: white;
        margin: 0;
        font-family: 'Inter', sans-serif;
    }
    .app-subtitle {
        font-size: 18px;
        color: rgba(255,255,255,0.95);
        margin: 8px 0 0 0;
        font-weight: 500;
    }
    .app-description {
        font-size: 14px;
        color: rgba(255,255,255,0.75);
        margin: 12px 0 0 0;
        font-weight: 400;
        max-width: 700px;
        line-height: 1.6;
    }
    
    /* Card styles */
    .briefing-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        height: 100%;
        min-height: 180px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: box-shadow 0.2s ease;
        margin-bottom: 0;
    }
    .briefing-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Card grid layout */
    .card-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 16px;
    }
    
    .card-grid .briefing-card {
        height: 100%;
    }
    .card-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid #f1f5f9;
    }
    .card-icon {
        font-size: 22px;
    }
    .card-title {
        font-weight: 600;
        font-size: 15px;
        color: #1e293b;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .card-content {
        color: #475569;
        font-size: 14px;
        line-height: 1.7;
    }
    .card-content ul {
        margin: 0;
        padding-left: 18px;
    }
    .card-content li {
        margin-bottom: 10px;
    }
    .card-content strong {
        color: #1e293b;
    }
    
    /* Citation badges */
    .citation {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        margin-left: 8px;
        cursor: help;
    }
    .cite-crm { background: #dbeafe; color: #1e40af; }
    .cite-slack { background: #fef3c7; color: #92400e; }
    .cite-docs { background: #dcfce7; color: #166534; }
    .cite-analytics { background: #f3e8ff; color: #6b21a8; }
    
    /* Priority numbers */
    .priority-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        font-weight: 700;
        font-size: 12px;
        margin-right: 10px;
    }
    .priority-1 { background: #dc2626; color: white; }
    .priority-2 { background: #ea580c; color: white; }
    .priority-3 { background: #ca8a04; color: white; }
    .priority-4 { background: #16a34a; color: white; }
    .priority-5 { background: #64748b; color: white; }
    
    /* Deal journey */
    .deal-journey {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 20px 0;
        flex-wrap: wrap;
        padding: 16px 20px;
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    .stage-pill {
        padding: 10px 20px;
        border-radius: 24px;
        font-weight: 600;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .stage-completed { background: #22c55e; color: white; }
    .stage-current { background: #2563eb; color: white; box-shadow: 0 0 0 4px rgba(37,99,235,0.2); }
    .stage-pending { background: #e2e8f0; color: #94a3b8; }
    .stage-arrow { color: #cbd5e1; font-size: 20px; }
    
    /* Source legend */
    .source-legend {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        margin: 12px 0 20px 0;
        padding: 12px 16px;
        background: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        align-items: center;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #64748b;
    }
    
    /* Briefing header */
    .briefing-header {
        margin-bottom: 8px;
    }
    .client-name {
        font-size: 32px;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        font-family: 'Inter', sans-serif;
    }
    .meeting-topic {
        font-size: 16px;
        color: #64748b;
        margin: 6px 0 0 0;
        font-weight: 500;
    }
    
    .gen-time {
        color: #94a3b8;
        font-size: 13px;
        font-weight: 500;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 12px 16px;
        font-size: 15px;
        font-family: 'Inter', sans-serif;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 14px 28px;
        font-size: 15px;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: #94a3b8;
        font-size: 13px;
        padding: 24px 0;
        border-top: 1px solid #e2e8f0;
        margin-top: 40px;
    }
    
    /* Analytics chart card */
    .chart-insight {
        background: #f8fafc;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
        border-left: 3px solid #3b82f6;
    }
    .chart-insight-title {
        font-weight: 600;
        color: #1e293b;
        font-size: 13px;
        margin-bottom: 4px;
    }
    .chart-insight-text {
        color: #64748b;
        font-size: 12px;
        line-height: 1.5;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Pulse animation for active agent */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }
</style>
""", unsafe_allow_html=True)

# Source config for citations
SOURCE_CONFIG = {
    "crm": {"label": "CRM", "icon": "🗄️", "class": "cite-crm"},
    "slack": {"label": "Slack", "icon": "💬", "class": "cite-slack"},
    "docs": {"label": "Docs", "icon": "📄", "class": "cite-docs"},
    "analytics": {"label": "Analytics", "icon": "📊", "class": "cite-analytics"},
}


def render_citation(source: str, detail: str = "") -> str:
    """Render a small citation badge."""
    cfg = SOURCE_CONFIG.get(source, {"label": source, "icon": "📁", "class": "cite-crm"})
    title = f'title="{detail}"' if detail else ""
    return f'<span class="citation {cfg["class"]}" {title}>{cfg["icon"]} {cfg["label"]}</span>'


def render_deal_journey(stage: str) -> str:
    """Render visual deal journey with current stage highlighted."""
    stages = ["Discovery", "Proposal", "Negotiation", "Closed Won"]
    stage_map = {
        "discovery": 0, "qualification": 0,
        "proposal": 1, "demo": 1,
        "negotiation": 2, "contract": 2,
        "closed won": 3, "closed": 3, "won": 3
    }
    current_idx = stage_map.get(stage.lower(), 1)
    
    html = '<div class="deal-journey">'
    for i, s in enumerate(stages):
        if i < current_idx:
            css = "stage-completed"
            icon = "✓"
        elif i == current_idx:
            css = "stage-current"
            icon = "●"
        else:
            css = "stage-pending"
            icon = "○"
        
        html += f'<span class="stage-pill {css}">{icon} {s}</span>'
        if i < len(stages) - 1:
            html += '<span class="stage-arrow">→</span>'
    html += '</div>'
    return html


def render_card_html(icon: str, title: str, content: str) -> str:
    """Render a single briefing card HTML (for use in grid)."""
    return f'''
    <div class="briefing-card">
        <div class="card-header">
            <span class="card-icon">{icon}</span>
            <span class="card-title">{title}</span>
        </div>
        <div class="card-content">{content}</div>
    </div>
    '''


def render_card_row(card1: tuple, card2: tuple) -> str:
    """Render two cards side by side with equal heights."""
    icon1, title1, content1 = card1
    icon2, title2, content2 = card2
    
    return f'''
    <div class="card-grid">
        {render_card_html(icon1, title1, content1)}
        {render_card_html(icon2, title2, content2)}
    </div>
    '''


# === HEADER ===
st.markdown('''
<div class="app-header">
    <p class="app-title">Kairo</p>
    <p class="app-subtitle">Your AI Meeting Prep Agent</p>
    <p class="app-description">Stop scrambling through CRM, Slack, and docs before client calls. Kairo pulls context from all your data sources and delivers a complete briefing in seconds, so you can walk into every meeting prepared and confident.</p>
</div>
''', unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([2, 1])

with col1:
    client_name = st.text_input(
        "Client Name",
        placeholder="e.g., Acme Corp",
        help="Enter the client or company name"
    )

with col2:
    meeting_topic = st.text_input(
        "Meeting Topic",
        placeholder="e.g., Q1 Review",
        value="General Check-in",
        help="What's the meeting about?"
    )

# Agent status component
def render_agent_status(agents_status: dict) -> str:
    """Render visual agent status indicator."""
    html = '<div style="display:flex;gap:12px;flex-wrap:wrap;margin:16px 0;">'
    
    agent_config = {
        "crm": {"name": "CRM Agent", "color": "#3b82f6"},
        "comms": {"name": "Comms Agent", "color": "#f59e0b"},
        "docs": {"name": "Docs Agent", "color": "#10b981"},
        "analytics": {"name": "Analytics Agent", "color": "#8b5cf6"},
        "orchestrator": {"name": "Orchestrator", "color": "#052FAD"}
    }
    
    for agent_id, config in agent_config.items():
        status = agents_status.get(agent_id, "pending")
        if status == "active":
            bg = config["color"]
            border = config["color"]
            icon = '<span style="animation:pulse 1s infinite;">●</span>'
            opacity = "1"
        elif status == "done":
            bg = "#f0fdf4"
            border = "#22c55e"
            icon = "✓"
            opacity = "1"
        else:
            bg = "#f8fafc"
            border = "#e2e8f0"
            icon = "○"
            opacity = "0.6"
        
        html += f'''<div style="
            background:{bg};
            border:2px solid {border};
            border-radius:8px;
            padding:8px 14px;
            font-size:13px;
            font-weight:500;
            color:{'white' if status == 'active' else '#475569'};
            opacity:{opacity};
            display:flex;
            align-items:center;
            gap:6px;
        ">{icon} {config["name"]}</div>'''
    
    html += '</div>'
    return html


# Generate button
if st.button("Generate Briefing", type="primary", use_container_width=True):
    if not client_name.strip():
        st.error("Please enter a client name")
    else:
        # Progress container
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            agent_status_container = st.empty()
        
        try:
            # CRM Agent
            agent_status_container.markdown(render_agent_status({"crm": "active"}), unsafe_allow_html=True)
            status_text.markdown("**CRM Agent:** Querying client database for account info, stakeholders, and deal status...")
            progress_bar.progress(15)
            time.sleep(0.3)
            
            # Comms Agent
            agent_status_container.markdown(render_agent_status({"crm": "done", "comms": "active"}), unsafe_allow_html=True)
            status_text.markdown("**Comms Agent:** Analyzing Slack conversations for recent context and action items...")
            progress_bar.progress(35)
            time.sleep(0.3)
            
            # Docs Agent
            agent_status_container.markdown(render_agent_status({"crm": "done", "comms": "done", "docs": "active"}), unsafe_allow_html=True)
            status_text.markdown("**Docs Agent:** Parsing proposals and meeting notes with Docling...")
            progress_bar.progress(55)
            time.sleep(0.3)
            
            # Analytics Agent
            agent_status_container.markdown(render_agent_status({"crm": "done", "comms": "done", "docs": "done", "analytics": "active"}), unsafe_allow_html=True)
            status_text.markdown("**Analytics Agent:** Analyzing dashboards, charts, and health metrics...")
            progress_bar.progress(75)
            time.sleep(0.3)
            
            # Orchestrator
            agent_status_container.markdown(render_agent_status({"crm": "done", "comms": "done", "docs": "done", "analytics": "done", "orchestrator": "active"}), unsafe_allow_html=True)
            status_text.markdown("**Orchestrator:** Collating agent outputs and generating briefing with IBM Granite...")
            progress_bar.progress(90)
            
            # Call orchestrator
            response = requests.post(
                f"{ORCHESTRATOR_URL}/briefing",
                json={"client_name": client_name, "meeting_topic": meeting_topic},
                timeout=180
            )
            response.raise_for_status()
            result = response.json()
            
            # All done
            agent_status_container.markdown(render_agent_status({"crm": "done", "comms": "done", "docs": "done", "analytics": "done", "orchestrator": "done"}), unsafe_allow_html=True)
            progress_bar.progress(100)
            status_text.markdown("**Briefing ready!**")
            
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            agent_status_container.empty()
            
            # Get structured data
            data = result.get("structured_data", {})
            sources = result.get("sources_used", [])
            gen_time = result.get('generation_time_ms', 0) / 1000
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # === BRIEFING HEADER ===
            st.markdown(f'''
            <div class="briefing-header">
                <p class="client-name">{data.get("client_name", client_name)}</p>
                <p class="meeting-topic">Meeting Topic: {meeting_topic}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Deal Journey
            deal_stage = data.get("deal", {}).get("stage", "Proposal")
            st.markdown(render_deal_journey(deal_stage), unsafe_allow_html=True)
            
            # Source Legend
            legend_html = '<div class="source-legend">'
            legend_html += '<span style="color:#475569;font-weight:600;">Sources:</span>'
            for src in sources:
                cfg = SOURCE_CONFIG.get(src, {"label": src, "icon": "📁", "class": "cite-crm"})
                legend_html += f'<span class="legend-item"><span class="citation {cfg["class"]}">{cfg["icon"]} {cfg["label"]}</span></span>'
            legend_html += f'<span class="legend-item" style="margin-left:auto;"><span class="gen-time">Generated in {gen_time:.1f}s</span></span>'
            legend_html += '</div>'
            st.markdown(legend_html, unsafe_allow_html=True)
            
            # === CARDS ROW 1: At a Glance + Key Stakeholders ===
            deal = data.get("deal", {})
            health = data.get("health", {})
            glance_content = f'''
            <ul>
                <li><strong>Stage:</strong> {deal.get("stage", "N/A")} {render_citation("crm")}</li>
                <li><strong>Value:</strong> {deal.get("value", "N/A")} {render_citation("crm")}</li>
                <li><strong>Close Date:</strong> {deal.get("close_date", "N/A")} {render_citation("crm")}</li>
                <li><strong>Probability:</strong> {deal.get("probability", "N/A")}% {render_citation("crm")}</li>
                <li><strong>Health Score:</strong> {health.get("score", "N/A")}/100 {render_citation("analytics")}</li>
                <li><strong>Competitor:</strong> {deal.get("competitor", "None")} {render_citation("crm")}</li>
            </ul>
            '''
            
            stakeholders = data.get("stakeholders", [])
            stake_items = ""
            for s in stakeholders[:4]:
                sentiment_color = {"Champion": "#16a34a", "Supportive": "#2563eb", "Neutral": "#ca8a04", "Detractor": "#dc2626"}.get(s.get("sentiment"), "#64748b")
                notes = s.get("notes", "")
                notes_html = f'<br/><span style="color:#64748b;font-size:12px;margin-left:8px;">{notes[:80]}...</span>' if notes else ""
                stake_items += f'''<li style="margin-bottom:12px;"><strong>{s.get("name", "")}</strong>, {s.get("role", "")} 
                    <span style="color:{sentiment_color};font-weight:600;">({s.get("sentiment", "")})</span>
                    {render_citation("crm")}{notes_html}</li>'''
            stakeholders_content = f"<ul>{stake_items}</ul>"
            
            st.markdown(render_card_row(
                ("📊", "At a Glance", glance_content),
                ("👥", "Key Stakeholders", stakeholders_content)
            ), unsafe_allow_html=True)
            
            # === CARDS ROW 2: Priority Discussion + Recent Context ===
            priorities = data.get("priorities", [])
            priority_items = ""
            for i, p in enumerate(priorities[:5], 1):
                src = p.get("source", "crm")
                priority_items += f'''<li style="margin-bottom:10px;">
                    <span class="priority-num priority-{i}">{i}</span>
                    {p.get("topic", "")} {render_citation(src, p.get("detail", ""))}
                </li>'''
            priorities_content = f"<ul style='list-style:none;padding-left:0;'>{priority_items}</ul>"
            
            context_items = data.get("recent_context", [])
            context_html = ""
            for c in context_items[:3]:
                context_html += f'''<li style="margin-bottom:8px;">{c.get("text", "")} {render_citation(c.get("source", "crm"))}</li>'''
            context_content = f"<ul>{context_html}</ul>"
            
            st.markdown(render_card_row(
                ("🎯", "Priority Discussion Topics", priorities_content),
                ("💬", "Recent Context", context_content)
            ), unsafe_allow_html=True)
            
            # === CARDS ROW 3: Key Documents + Analytics Insights ===
            docs = data.get("documents", [])
            docs_html = ""
            for d in docs[:3]:
                docs_html += f'''<li style="margin-bottom:10px;"><strong>{d.get("title", "")}</strong><br/>
                    <span style="color:#64748b;font-size:12px;">{d.get("summary", "")[:80]}...</span>
                    {render_citation("docs", d.get("title", ""))}</li>'''
            docs_content = f"<ul>{docs_html}</ul>"
            
            talking = data.get("talking_points", [])
            charts = data.get("chart_insights", [])
            analytics_items = ""
            if charts:
                for chart in charts[:3]:
                    title = chart.get("title", "")
                    insight = chart.get("insight", "")
                    analytics_items += f'''<li style="margin-bottom:12px;">
                        <strong>{title}</strong><br/>
                        <span style="color:#64748b;font-size:13px;">{insight}</span>
                        {render_citation("analytics")}
                    </li>'''
            else:
                for t in talking[:3]:
                    analytics_items += f'''<li>{t.get("point", "")} {render_citation(t.get("source", "analytics"))}</li>'''
            analytics_content = f"<ul>{analytics_items}</ul>"
            
            st.markdown(render_card_row(
                ("📄", "Key Documents", docs_content),
                ("📈", "Analytics Insights", analytics_content)
            ), unsafe_allow_html=True)
            
            # === OPENING SCRIPT (Full Width) ===
            opening = data.get("opening_script", [])
            if opening:
                script_html = '<div style="color:#475569;">'
                for i, line in enumerate(opening[:3]):
                    script_html += f'''<p style="margin-bottom:14px;padding:12px 16px;background:#f8fafc;border-radius:8px;border-left:4px solid #2563eb;font-style:italic;">
                        "{line.get('line', '')}" {render_citation(line.get('source', 'crm'))}
                    </p>'''
                script_html += '</div>'
                st.markdown(render_card_html("🎬", "Suggested Opening Script", script_html), unsafe_allow_html=True)
            
            # === ACTION BUTTONS ===
            st.markdown("<br>", unsafe_allow_html=True)
            bcol1, bcol2, bcol3 = st.columns(3)
            
            with bcol1:
                if st.button("🔄 Regenerate"):
                    st.rerun()
            with bcol2:
                if st.button("📋 View Raw"):
                    with st.expander("Raw Briefing", expanded=True):
                        st.markdown(result.get("briefing", ""))
            with bcol3:
                if st.button("📤 Export"):
                    st.info("Export feature coming soon")
                    
        except requests.exceptions.ConnectionError:
            progress_bar.empty()
            status_text.empty()
            agent_status_container.empty()
            st.error("Could not connect to orchestrator. Make sure services are running with: python run_local.py")
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            agent_status_container.empty()
            st.error(f"Error: {e}")

# Footer
st.markdown('''
<div class="footer-text">
    Built for Pods, Prompts & Prototypes Hackathon | Red Hat + IBM | Powered by IBM Granite
</div>
''', unsafe_allow_html=True)
