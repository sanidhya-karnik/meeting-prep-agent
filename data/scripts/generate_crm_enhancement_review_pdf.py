"""
Generate a PDF review pack for CRM dataset enhancement.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from pathlib import Path


ROOT = Path("/Users/angella/Desktop/meeting-prep-agent")
OUTPUT = ROOT / "data" / "documents" / "CRM_Dataset_Enhancement_Review.pdf"


def bullet_list(items, style):
    flow = []
    for item in items:
        flow.append(ListItem(Paragraph(item, style), leftIndent=14))
    return ListFlowable(flow, bulletType="bullet", start="circle", leftIndent=14)


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1f3a5f"),
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2c5282"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10.5,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6,
    )

    story = []
    story.append(Paragraph("CRM Dataset Enhancement Review Pack", title_style))
    story.append(
        Paragraph(
            "Prepared for review before applying any schema/data changes to the current mimicked Salesforce dataset.",
            body_style,
        )
    )
    story.append(Spacer(1, 8))

    story.append(Paragraph("1) Objective", heading_style))
    story.append(
        Paragraph(
            "Make the current CRM dataset more detailed, cohesive, and standardized for pre-call briefing generation.",
            body_style,
        )
    )

    story.append(Paragraph("2) Source Data Assessed", heading_style))
    story.append(
        bullet_list(
            [
                "accounts.csv: firmographics and parent-company relationships",
                "products.csv: product catalog and list pricing",
                "sales_teams.csv: rep-manager-region hierarchy",
                "sales_pipeline.csv: stage lifecycle, engage/close dates, and close value",
            ],
            body_style,
        )
    )

    story.append(Paragraph("3) Profiling Highlights", heading_style))
    story.append(
        bullet_list(
            [
                "8,800 opportunities; 6,711 closed; 2,089 open",
                "Closed win rate: 63.15%",
                "Data quality findings: 1,425 blank account values",
                "Product mismatch: 'GTXPro' should be normalized to 'GTX Pro' (1,480 rows)",
                "Industry typo normalization required: 'technolgy' -> 'technology'",
            ],
            body_style,
        )
    )

    story.append(Paragraph("4) Proposed Enhancements", heading_style))
    story.append(
        bullet_list(
            [
                "Enrich clients with year_established, annual_revenue_musd, employee_count, parent_company, data_quality_flag",
                "Add sales_reps table for normalized ownership (rep, manager, region)",
                "Add products table and link deals to products",
                "Enhance deals with external_opportunity_id, owner_id, product_id, engage_date, list_price_snapshot",
                "Add deal_stage_history for stage transition analytics",
                "Extend health_metrics with win_rate_90d, avg_cycle_days_90d, avg_closed_value_90d, open_pipeline_value",
            ],
            body_style,
        )
    )

    story.append(Paragraph("5) Standardization Rules", heading_style))
    story.append(
        bullet_list(
            [
                "Canonical product names (GTXPro -> GTX Pro)",
                "Canonical industries (technolgy -> technology)",
                "Handle blank account rows via Unknown Account or quality flags",
                "Treat revenue as millions USD in transformed schema",
                "Maintain canonical stage vocabulary: Prospecting, Engaging, Won, Lost",
            ],
            body_style,
        )
    )

    story.append(Paragraph("6) Before vs After Deliverables", heading_style))
    story.append(
        Paragraph(
            "Detailed dictionaries are provided as CSVs in the repository:",
            body_style,
        )
    )
    story.append(
        bullet_list(
            [
                "data/documents/crm_dataset_before_current.csv",
                "data/documents/crm_dataset_after_proposed.csv",
            ],
            body_style,
        )
    )

    story.append(Paragraph("7) Implementation Status", heading_style))
    story.append(
        Paragraph(
            "No changes have been applied to data/postgres/init.sql in this review step. This pack is ready for approval.",
            body_style,
        )
    )

    doc.build(story)
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
