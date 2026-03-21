"""
Meeting Prep Agent UI

Streamlit interface with card-based layout and source citations.
"""

import os
import streamlit as st
import requests

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://127.0.0.1:8000")

# Page config
st.set_page_config(
    page_title="Meeting Prep Agent",
    page_icon="📋",
    layout="wide"
)

# Custom CSS for cards and citations
st.markdown("""
<style>
    .main { padding: 1rem; }
    
    /* Card styles */
    .briefing-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        min-height: 180px;
    }
    .card-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #334155;
    }
    .card-icon {
        font-size: 20px;
    }
    .card-title {
        font-weight: 600;
        font-size: 16px;
        color: #f1f5f9;
        margin: 0;
    }
    .card-content {
        color: #cbd5e1;
        font-size: 14px;
        line-height: 1.6;
    }
    .card-content ul {
        margin: 0;
        padding-left: 20px;
    }
    .card-content li {
        margin-bottom: 6px;
    }
    
    /* Citation badges */
    .citation {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 10px;
        font-weight: 500;
        margin-left: 6px;
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
        width: 22px;
        height: 22px;
        border-radius: 50%;
        font-weight: 700;
        font-size: 12px;
        margin-right: 8px;
    }
    .priority-1 { background: #ef4444; color: white; }
    .priority-2 { background: #f97316; color: white; }
    .priority-3 { background: #eab308; color: #1e1e1e; }
    .priority-4 { background: #22c55e; color: white; }
    .priority-5 { background: #6b7280; color: white; }
    
    /* Deal journey */
    .deal-journey {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 16px 0;
        flex-wrap: wrap;
    }
    .stage-pill {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 13px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .stage-completed { background: #22c55e; color: white; }
    .stage-current { background: #3b82f6; color: white; box-shadow: 0 0 12px rgba(59,130,246,0.5); }
    .stage-pending { background: #4b5563; color: #9ca3af; }
    .stage-arrow { color: #6b7280; font-size: 18px; }
    
    /* Source legend */
    .source-legend {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin: 8px 0 16px 0;
        padding: 10px;
        background: #1e293b;
        border-radius: 8px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: #94a3b8;
    }
    
    /* Header section */
    .briefing-header {
        margin-bottom: 20px;
    }
    .client-name {
        font-size: 28px;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .meeting-topic {
        font-size: 16px;
        color: #94a3b8;
        margin: 4px 0 0 0;
    }
    
    .gen-time {
        color: #6b7280;
        font-size: 13px;
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


def render_card(icon: str, title: str, content: str) -> str:
    """Render a single briefing card."""
    return f'''
    <div class="briefing-card">
        <div class="card-header">
            <span class="card-icon">{icon}</span>
            <span class="card-title">{title}</span>
        </div>
        <div class="card-content">{content}</div>
    </div>
    '''


# Header
st.title("📋 Meeting Prep Agent")
st.markdown("*Get up to speed on any client in 60 seconds*")

st.markdown("---")

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

# Generate button
if st.button("🚀 Generate Briefing", type="primary", use_container_width=True):
    if not client_name.strip():
        st.error("Please enter a client name")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Querying CRM...")
        progress_bar.progress(20)
        
        try:
            status_text.text("💬 Fetching Slack conversations...")
            progress_bar.progress(40)
            
            status_text.text("📄 Parsing documents...")
            progress_bar.progress(60)
            
            status_text.text("🤖 Generating briefing with IBM Granite...")
            progress_bar.progress(80)
            
            # Call orchestrator
            response = requests.post(
                f"{ORCHESTRATOR_URL}/briefing",
                json={"client_name": client_name, "meeting_topic": meeting_topic},
                timeout=180
            )
            response.raise_for_status()
            result = response.json()
            
            progress_bar.progress(100)
            status_text.text("✅ Briefing ready!")
            
            import time
            time.sleep(0.3)
            progress_bar.empty()
            status_text.empty()
            
            # Get structured data
            data = result.get("structured_data", {})
            sources = result.get("sources_used", [])
            gen_time = result.get('generation_time_ms', 0) / 1000
            
            st.markdown("---")
            
            # === HEADER ===
            st.markdown(f'''
            <div class="briefing-header">
                <p class="client-name">{data.get("client_name", client_name)}</p>
                <p class="meeting-topic">Meeting: {meeting_topic}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Deal Journey
            deal_stage = data.get("deal", {}).get("stage", "Proposal")
            st.markdown(render_deal_journey(deal_stage), unsafe_allow_html=True)
            
            # Source Legend
            legend_html = '<div class="source-legend">'
            legend_html += '<span style="color:#64748b;font-weight:500;">Sources:</span>'
            for src in sources:
                cfg = SOURCE_CONFIG.get(src, {"label": src, "icon": "📁", "class": "cite-crm"})
                legend_html += f'<span class="legend-item"><span class="citation {cfg["class"]}">{cfg["icon"]} {cfg["label"]}</span></span>'
            legend_html += f'<span class="legend-item" style="margin-left:auto;">Generated in {gen_time:.1f}s</span>'
            legend_html += '</div>'
            st.markdown(legend_html, unsafe_allow_html=True)
            
            # === CARDS ROW 1 ===
            col1, col2 = st.columns(2)
            
            with col1:
                # At a Glance card
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
                st.markdown(render_card("📊", "At a Glance", glance_content), unsafe_allow_html=True)
            
            with col2:
                # Key Stakeholders card
                stakeholders = data.get("stakeholders", [])
                stake_items = ""
                for s in stakeholders[:4]:
                    sentiment_color = {"Champion": "#22c55e", "Supportive": "#3b82f6", "Neutral": "#eab308", "Detractor": "#ef4444"}.get(s.get("sentiment"), "#6b7280")
                    notes = s.get("notes", "")
                    notes_html = f'<br/><span style="color:#94a3b8;font-size:12px;margin-left:8px;">{notes[:80]}...</span>' if notes else ""
                    stake_items += f'''<li style="margin-bottom:10px;"><strong>{s.get("name", "")}</strong> - {s.get("role", "")} 
                        <span style="color:{sentiment_color};font-weight:600;">({s.get("sentiment", "")})</span>
                        {render_citation("crm")}{notes_html}</li>'''
                st.markdown(render_card("👥", "Key Stakeholders", f"<ul>{stake_items}</ul>"), unsafe_allow_html=True)
            
            # === CARDS ROW 2 ===
            col3, col4 = st.columns(2)
            
            with col3:
                # Priority Discussion Topics card
                priorities = data.get("priorities", [])
                priority_items = ""
                for i, p in enumerate(priorities[:5], 1):
                    src = p.get("source", "crm")
                    priority_items += f'''<li style="margin-bottom:8px;">
                        <span class="priority-num priority-{i}">{i}</span>
                        {p.get("topic", "")} {render_citation(src, p.get("detail", ""))}
                    </li>'''
                st.markdown(render_card("🎯", "Priority Discussion Topics", f"<ul style='list-style:none;padding-left:0;'>{priority_items}</ul>"), unsafe_allow_html=True)
            
            with col4:
                # Recent Context card
                context_items = data.get("recent_context", [])
                context_html = ""
                for c in context_items[:3]:
                    context_html += f'''<li>{c.get("text", "")} {render_citation(c.get("source", "crm"))}</li>'''
                st.markdown(render_card("💬", "Recent Context", f"<ul>{context_html}</ul>"), unsafe_allow_html=True)
            
            # === CARDS ROW 3 ===
            col5, col6 = st.columns(2)
            
            with col5:
                # Key Documents card
                docs = data.get("documents", [])
                docs_html = ""
                for d in docs[:3]:
                    docs_html += f'''<li><strong>{d.get("title", "")}</strong><br/>
                        <span style="color:#94a3b8;font-size:12px;">{d.get("summary", "")[:80]}...</span>
                        {render_citation("docs", d.get("title", ""))}</li>'''
                st.markdown(render_card("📄", "Key Documents", f"<ul>{docs_html}</ul>"), unsafe_allow_html=True)
            
            with col6:
                # Talking Points card
                talking = data.get("talking_points", [])
                talking_html = ""
                for t in talking[:3]:
                    talking_html += f'''<li>{t.get("point", "")} {render_citation(t.get("source", "crm"))}</li>'''
                st.markdown(render_card("💡", "Talking Points", f"<ul>{talking_html}</ul>"), unsafe_allow_html=True)
            
            # === OPENING SCRIPT (Full Width) ===
            opening = data.get("opening_script", [])
            if opening:
                script_html = '<div style="font-style:italic;color:#e2e8f0;">'
                for i, line in enumerate(opening[:3]):
                    script_html += f'''<p style="margin-bottom:12px;padding-left:12px;border-left:3px solid #3b82f6;">
                        "{line.get('line', '')}" {render_citation(line.get('source', 'crm'))}
                    </p>'''
                script_html += '</div>'
                st.markdown(render_card("🎬", "Opening Script", script_html), unsafe_allow_html=True)
            
            # === ACTION BUTTONS ===
            st.markdown("---")
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
            st.error("Could not connect to orchestrator. Make sure services are running.")
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption("Built for Pods, Prompts & Prototypes hackathon | Red Hat + IBM | All processing runs locally via Podman")
