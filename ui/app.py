"""
PreCall Briefing UI

Streamlit interface for generating pre-call briefings.
"""

import os
import streamlit as st
import requests

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8000")

# Page config
st.set_page_config(
    page_title="Meeting Prep Agent",
    page_icon="📋",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stMarkdown {
        max-width: 100%;
    }
    .source-badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
    }
    .source-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 500;
    }
    .source-crm {
        background-color: #dbeafe;
        color: #1e40af;
    }
    .source-slack {
        background-color: #fef3c7;
        color: #92400e;
    }
    .source-docs {
        background-color: #dcfce7;
        color: #166534;
    }
    .source-analytics {
        background-color: #f3e8ff;
        color: #6b21a8;
    }
    .gen-time {
        color: #6b7280;
        font-size: 13px;
    }
    .briefing-header {
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

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
        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🔍 Querying CRM (PostgreSQL)...")
        progress_bar.progress(15)
        
        try:
            status_text.text("💬 Fetching Slack conversations...")
            progress_bar.progress(35)
            
            status_text.text("📄 Parsing documents (Docling)...")
            progress_bar.progress(55)
            
            status_text.text("📊 Loading analytics charts...")
            progress_bar.progress(70)
            
            status_text.text("🤖 Generating briefing with Qwen3...")
            progress_bar.progress(85)
            
            # Call orchestrator
            response = requests.post(
                f"{ORCHESTRATOR_URL}/briefing",
                json={
                    "client_name": client_name,
                    "meeting_topic": meeting_topic
                },
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            
            progress_bar.progress(100)
            status_text.text("✅ Briefing ready!")
            
            # Clear progress after a moment
            import time
            time.sleep(0.5)
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.markdown("---")
            
            # Sources used with icons
            sources = result.get("sources_used", [])
            source_config = {
                "crm": {"label": "CRM", "icon": "🗄️", "class": "source-crm"},
                "slack": {"label": "Slack", "icon": "💬", "class": "source-slack"},
                "docs": {"label": "Documents", "icon": "📄", "class": "source-docs"},
                "analytics": {"label": "Analytics", "icon": "📊", "class": "source-analytics"},
            }
            
            badges_html = '<div class="source-badges">'
            for s in sources:
                cfg = source_config.get(s, {"label": s, "icon": "📁", "class": "source-crm"})
                badges_html += f'<span class="source-badge {cfg["class"]}">{cfg["icon"]} {cfg["label"]}</span>'
            badges_html += '</div>'
            
            st.markdown(badges_html, unsafe_allow_html=True)
            
            gen_time = result.get('generation_time_ms', 0) / 1000
            st.markdown(f'<p class="gen-time">Generated in {gen_time:.1f} seconds from {len(sources)} sources</p>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # The briefing
            st.markdown(result.get("briefing", "No briefing generated"))
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📋 Copy Markdown"):
                    st.code(result.get("briefing", ""), language="markdown")
                    st.info("Select and copy from the box above")
            
            with col2:
                if st.button("🔄 Regenerate"):
                    st.rerun()
            
            with col3:
                if st.button("📤 Export"):
                    st.info("Export feature coming soon")
                
        except requests.exceptions.ConnectionError:
            progress_bar.empty()
            status_text.empty()
            st.error("Could not connect to the orchestrator. Make sure all services are running.")
        except requests.exceptions.RequestException as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Failed to generate briefing: {e}")
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"Error: {e}")

# Demo hint
st.markdown("---")
with st.expander("💡 Demo Instructions", expanded=False):
    st.markdown("""
    **Try this demo scenario:**
    
    1. Enter client name: `Acme Corp`
    2. Enter meeting topic: `Q1 Review`
    3. Click "Generate Briefing"
    
    **What happens:**
    - CRM Agent queries PostgreSQL for client info, contacts, deal stage, recent activities
    - Comms Agent parses Slack channel export for recent conversations
    - Docs Agent reads proposal PDF and meeting notes DOCX via Docling
    - Analytics Agent loads usage charts and health score visualizations
    - Orchestrator sends all context to Qwen3 to generate the briefing
    
    **Data sources in this demo:**
    - PostgreSQL: Client profile, $450K deal in Negotiation, 3 stakeholders
    - Slack: 13 messages discussing ROI, timeline, competitor pricing
    - Documents: Proposal v3 (PDF), Meeting notes from March 10 (DOCX)
    - Analytics: Usage trend (+62% growth), Health score (85/100), Support metrics
    """)

# Footer
st.markdown("---")
st.caption("Built for Pods, Prompts & Prototypes hackathon | Red Hat + IBM | All processing runs locally via Podman")
