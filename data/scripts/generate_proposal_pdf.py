"""
Generate sample proposal PDF for Acme Corp demo.
Uses reportlab to create a realistic-looking sales proposal.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

OUTPUT_DIR = "/app/data/documents"

def create_proposal():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    doc = SimpleDocTemplate(
        f"{OUTPUT_DIR}/Acme_Corp_Proposal_v3.pdf",
        pagesize=letter,
        rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1a365d')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#2c5282')
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        leading=16
    )
    
    story = []
    
    # Title
    story.append(Paragraph("Enterprise Software Proposal", title_style))
    story.append(Paragraph("Prepared for Acme Corp", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Meta info table
    meta_data = [
        ["Document:", "Proposal v3"],
        ["Date:", "March 15, 2026"],
        ["Prepared by:", "Sarah Chen, Account Executive"],
        ["Valid until:", "April 30, 2026"]
    ]
    meta_table = Table(meta_data, colWidths=[1.5*inch, 3*inch])
    meta_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 30))
    
    # Executive Summary
    story.append(Paragraph("1. Executive Summary", heading_style))
    story.append(Paragraph(
        "We are pleased to present this proposal for a 3-year Enterprise Software License "
        "to support Acme Corp's manufacturing operations. This solution will streamline "
        "your production workflows, improve compliance tracking, and reduce manual reporting "
        "by an estimated 40+ hours per month.",
        body_style
    ))
    story.append(Paragraph(
        "Based on our discovery sessions with your engineering and IT teams, we have tailored "
        "this proposal to address your specific requirements for SAP S/4HANA integration, "
        "US-only data residency, and enterprise-grade security compliance.",
        body_style
    ))
    
    # Pricing
    story.append(Paragraph("2. Investment Summary", heading_style))
    
    pricing_data = [
        ["Component", "Year 1", "Year 2", "Year 3", "Total"],
        ["Annual License Fee", "$120,000", "$120,000", "$120,000", "$360,000"],
        ["Implementation Services", "$45,000", "-", "-", "$45,000"],
        ["Training (40 hours)", "$15,000", "-", "-", "$15,000"],
        ["Premium Support (24/7)", "$30,000", "$30,000", "$30,000", "$90,000"],
        ["", "", "", "", ""],
        ["Annual Total", "$210,000", "$150,000", "$150,000", "$510,000"],
    ]
    
    pricing_table = Table(pricing_data, colWidths=[2*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch])
    pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.gray),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(pricing_table)
    story.append(Spacer(1, 20))
    
    # Discount note
    story.append(Paragraph(
        "<b>Special Pricing:</b> This proposal reflects a 10% volume discount from our standard "
        "enterprise rates, resulting in a total 3-year investment of <b>$450,000</b> "
        "(originally $510,000).",
        body_style
    ))
    
    # Terms
    story.append(Paragraph("3. Terms and Conditions", heading_style))
    
    terms = [
        "Payment Terms: Net 30 from invoice date",
        "Service Level Agreement: 99.9% uptime guarantee",
        "Data Residency: All data stored in US-East region (AWS us-east-1)",
        "Support: 24/7 premium support with 2-hour response time",
        "Implementation Timeline: 8-10 weeks from contract signing",
    ]
    
    for term in terms:
        story.append(Paragraph(f"<bullet>&bull;</bullet> {term}", body_style))
    
    story.append(PageBreak())
    
    # Implementation
    story.append(Paragraph("4. Implementation Plan", heading_style))
    
    impl_data = [
        ["Phase", "Duration", "Activities"],
        ["1. Discovery", "Week 1-2", "Requirements validation, technical review"],
        ["2. Configuration", "Week 3-4", "System setup, SAP integration"],
        ["3. Data Migration", "Week 5-6", "Historical data import, validation"],
        ["4. Training", "Week 7-8", "User training, admin certification"],
        ["5. Go-Live", "Week 9-10", "Pilot rollout, production deployment"],
    ]
    
    impl_table = Table(impl_data, colWidths=[1.5*inch, 1.2*inch, 3.5*inch])
    impl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(impl_table)
    
    # Next Steps
    story.append(Paragraph("5. Next Steps", heading_style))
    story.append(Paragraph(
        "To proceed with this engagement, please review and sign the attached Master Service "
        "Agreement. Upon receipt, we will schedule a kickoff call with your team and begin "
        "the implementation process.",
        body_style
    ))
    story.append(Paragraph(
        "We look forward to partnering with Acme Corp on this initiative. Please do not "
        "hesitate to reach out with any questions.",
        body_style
    ))
    
    story.append(Spacer(1, 40))
    story.append(Paragraph("Sarah Chen", body_style))
    story.append(Paragraph("Account Executive", body_style))
    story.append(Paragraph("sarah.chen@ourcompany.com | +1 555-0123", body_style))
    
    doc.build(story)
    print(f"Created: {OUTPUT_DIR}/Acme_Corp_Proposal_v3.pdf")


if __name__ == "__main__":
    create_proposal()
