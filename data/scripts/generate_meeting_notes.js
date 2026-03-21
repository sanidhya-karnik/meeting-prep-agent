// Generate sample meeting notes DOCX for Acme Corp demo
// Run with: node generate_meeting_notes.js

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, 
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType } = require('docx');
const fs = require('fs');

const OUTPUT_DIR = '/app/data/documents';

async function createMeetingNotes() {
    const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
    const borders = { top: border, bottom: border, left: border, right: border };

    const doc = new Document({
        styles: {
            default: { document: { run: { font: "Arial", size: 22 } } },
            paragraphStyles: [
                { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal",
                  run: { size: 32, bold: true, color: "1a365d" },
                  paragraph: { spacing: { before: 240, after: 120 } } },
                { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal",
                  run: { size: 26, bold: true, color: "2c5282" },
                  paragraph: { spacing: { before: 200, after: 100 } } },
            ]
        },
        sections: [{
            properties: {
                page: {
                    size: { width: 12240, height: 15840 },
                    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
                }
            },
            children: [
                // Title
                new Paragraph({
                    heading: HeadingLevel.HEADING_1,
                    children: [new TextRun("Meeting Notes: Technical Deep-Dive")]
                }),
                
                // Meta info
                new Paragraph({
                    children: [
                        new TextRun({ text: "Date: ", bold: true }),
                        new TextRun("March 10, 2026 | 10:00 AM - 11:00 AM CST")
                    ],
                    spacing: { after: 100 }
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "Location: ", bold: true }),
                        new TextRun("Zoom Meeting")
                    ],
                    spacing: { after: 100 }
                }),
                new Paragraph({
                    children: [
                        new TextRun({ text: "Attendees: ", bold: true }),
                        new TextRun("John Smith (Acme, VP Eng), Mike Chen (Acme, IT Director), Sarah Chen, Tom Wilson")
                    ],
                    spacing: { after: 200 }
                }),

                // Meeting Purpose
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("Meeting Purpose")]
                }),
                new Paragraph({
                    children: [new TextRun(
                        "Technical deep-dive session to review integration architecture, address security requirements, " +
                        "and align on implementation timeline for Q2 go-live target."
                    )],
                    spacing: { after: 200 }
                }),

                // Discussion Topics
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("Discussion Topics")]
                }),

                // Topic 1
                new Paragraph({
                    children: [new TextRun({ text: "1. SAP S/4HANA Integration", bold: true })],
                    spacing: { before: 150, after: 100 }
                }),
                new Paragraph({
                    children: [new TextRun(
                        "Tom presented the integration architecture using REST APIs. Mike confirmed this approach " +
                        "aligns with Acme's existing integration patterns. Key points:"
                    )],
                    spacing: { after: 100 }
                }),
                new Paragraph({
                    bullet: { level: 0 },
                    children: [new TextRun("Real-time sync for inventory and order data")]
                }),
                new Paragraph({
                    bullet: { level: 0 },
                    children: [new TextRun("Batch processing for historical data migration")]
                }),
                new Paragraph({
                    bullet: { level: 0 },
                    children: [new TextRun("OAuth 2.0 authentication with Okta SSO")],
                    spacing: { after: 150 }
                }),

                // Topic 2
                new Paragraph({
                    children: [new TextRun({ text: "2. Security and Compliance", bold: true })],
                    spacing: { before: 150, after: 100 }
                }),
                new Paragraph({
                    children: [new TextRun(
                        "Mike reviewed our SOC 2 Type II certification and security documentation. All requirements met. " +
                        "Confirmed US-only data residency (AWS us-east-1). Mike will share with legal team."
                    )],
                    spacing: { after: 150 }
                }),

                // Topic 3
                new Paragraph({
                    children: [new TextRun({ text: "3. Implementation Timeline", bold: true })],
                    spacing: { before: 150, after: 100 }
                }),
                new Paragraph({
                    children: [new TextRun(
                        "John emphasized the Q2 go-live target (end of June). Tom estimated 8-10 weeks from contract signing. " +
                        "If contract signed by April 1, go-live by mid-June is achievable. Phased rollout recommended: " +
                        "pilot with engineering team first, then expand to full organization."
                    )],
                    spacing: { after: 200 }
                }),

                // Decisions
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("Decisions Made")]
                }),
                new Paragraph({
                    bullet: { level: 0 },
                    children: [new TextRun("Will use REST API for ERP integration (not file-based)")]
                }),
                new Paragraph({
                    bullet: { level: 0 },
                    children: [new TextRun("Phased rollout: pilot with engineering team first")]
                }),
                new Paragraph({
                    bullet: { level: 0 },
                    children: [new TextRun("Weekly check-ins during implementation phase")],
                    spacing: { after: 200 }
                }),

                // Action Items
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("Action Items")]
                }),
                
                new Table({
                    width: { size: 9360, type: WidthType.DXA },
                    columnWidths: [4500, 2000, 1500, 1360],
                    rows: [
                        new TableRow({
                            children: [
                                new TableCell({
                                    borders,
                                    width: { size: 4500, type: WidthType.DXA },
                                    shading: { fill: "2c5282", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ 
                                        children: [new TextRun({ text: "Action Item", bold: true, color: "FFFFFF" })] 
                                    })]
                                }),
                                new TableCell({
                                    borders,
                                    width: { size: 2000, type: WidthType.DXA },
                                    shading: { fill: "2c5282", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ 
                                        children: [new TextRun({ text: "Owner", bold: true, color: "FFFFFF" })] 
                                    })]
                                }),
                                new TableCell({
                                    borders,
                                    width: { size: 1500, type: WidthType.DXA },
                                    shading: { fill: "2c5282", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ 
                                        children: [new TextRun({ text: "Due", bold: true, color: "FFFFFF" })] 
                                    })]
                                }),
                                new TableCell({
                                    borders,
                                    width: { size: 1360, type: WidthType.DXA },
                                    shading: { fill: "2c5282", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ 
                                        children: [new TextRun({ text: "Status", bold: true, color: "FFFFFF" })] 
                                    })]
                                }),
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({ borders, width: { size: 4500, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Confirm implementation timeline with delivery team")] })] }),
                                new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Sarah Chen")] })] }),
                                new TableCell({ borders, width: { size: 1500, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Mar 18")] })] }),
                                new TableCell({ borders, width: { size: 1360, type: WidthType.DXA },
                                    shading: { fill: "FEF3C7", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ children: [new TextRun("Pending")] })] }),
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({ borders, width: { size: 4500, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Share API documentation with Mike")] })] }),
                                new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Tom Wilson")] })] }),
                                new TableCell({ borders, width: { size: 1500, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Mar 12")] })] }),
                                new TableCell({ borders, width: { size: 1360, type: WidthType.DXA },
                                    shading: { fill: "D1FAE5", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ children: [new TextRun("Done")] })] }),
                            ]
                        }),
                        new TableRow({
                            children: [
                                new TableCell({ borders, width: { size: 4500, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Schedule security review call with legal")] })] }),
                                new TableCell({ borders, width: { size: 2000, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Mike Chen")] })] }),
                                new TableCell({ borders, width: { size: 1500, type: WidthType.DXA },
                                    children: [new Paragraph({ children: [new TextRun("Mar 20")] })] }),
                                new TableCell({ borders, width: { size: 1360, type: WidthType.DXA },
                                    shading: { fill: "FEF3C7", type: ShadingType.CLEAR },
                                    children: [new Paragraph({ children: [new TextRun("Pending")] })] }),
                            ]
                        }),
                    ]
                }),

                new Paragraph({ children: [], spacing: { after: 200 } }),

                // Next Meeting
                new Paragraph({
                    heading: HeadingLevel.HEADING_2,
                    children: [new TextRun("Next Meeting")]
                }),
                new Paragraph({
                    children: [new TextRun({ text: "Q1 Review Call", bold: true })],
                    spacing: { after: 50 }
                }),
                new Paragraph({
                    children: [new TextRun("Date: March 22, 2026 at 2:00 PM CST")]
                }),
                new Paragraph({
                    children: [new TextRun("Attendees: John Smith, Lisa Park (CFO), Mike Chen, Sarah Chen")]
                }),
                new Paragraph({
                    children: [new TextRun("Agenda: Q1 progress review, ROI discussion, contract finalization")],
                    spacing: { after: 200 }
                }),

                // Notes by
                new Paragraph({
                    children: [
                        new TextRun({ text: "Notes prepared by: ", italics: true }),
                        new TextRun({ text: "Sarah Chen", italics: true })
                    ]
                }),
            ]
        }]
    });

    const buffer = await Packer.toBuffer(doc);
    
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }
    
    fs.writeFileSync(`${OUTPUT_DIR}/Acme_Meeting_Notes_2026-03-10.docx`, buffer);
    console.log(`Created: ${OUTPUT_DIR}/Acme_Meeting_Notes_2026-03-10.docx`);
}

createMeetingNotes().catch(console.error);
