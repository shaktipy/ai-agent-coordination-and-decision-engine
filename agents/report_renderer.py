"""
agents/report_renderer.py — PDF Report Renderer
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from models.schemas import FinalReviewReport


def render_report_to_pdf(report: FinalReviewReport, output_path: str) -> None:
    """Render a FinalReviewReport to a styled PDF file."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36, leftMargin=36,
        topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontName='Helvetica-Bold', fontSize=22, leading=26,
        textColor=colors.HexColor('#1F2937'), spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Heading2'],
        fontName='Helvetica-Bold', fontSize=15, leading=18,
        textColor=colors.HexColor('#2563EB'), spaceBefore=14, spaceAfter=8
    )
    h3_style = ParagraphStyle(
        'AgentH3', parent=styles['Heading3'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#1E293B'), spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=13,
        textColor=colors.HexColor('#374151')
    )
    score_color = (
        colors.HexColor('#10B981') if report.overall_score >= 80
        else colors.HexColor('#F59E0B') if report.overall_score >= 50
        else colors.HexColor('#EF4444')
    )
    score_style = ParagraphStyle(
        'Score', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18,
        textColor=score_color
    )
    th_style = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=9,
        textColor=colors.white
    )

    story = []
    story.append(Paragraph("Multi-Agent Code Review Report", title_style))
    story.append(Paragraph(
        f"<b>Generated:</b> {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')} &nbsp; "
        f"<b>ID:</b> {report.report_id}",
        body_style
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Overall Code Health Score: {report.overall_score}/100", score_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Executive Summary", h2_style))
    story.append(Paragraph(report.executive_summary, body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Detailed Agent Reports", h2_style))
    for agent_rep in report.reports:
        story.append(Paragraph(f"{agent_rep.agent_name}", h3_style))
        story.append(Paragraph(f"<b>Summary:</b> {agent_rep.summary}", body_style))
        story.append(Spacer(1, 5))

        if agent_rep.findings:
            data = [[
                Paragraph("<b>Severity</b>", th_style),
                Paragraph("<b>Line</b>", th_style),
                Paragraph("<b>Title &amp; Description</b>", th_style),
                Paragraph("<b>Suggestion</b>", th_style),
            ]]
            for f in agent_rep.findings:
                ln = str(f.line_number) if f.line_number else "Snippet"
                sev_c = (
                    "#EF4444" if f.severity == "critical"
                    else "#F59E0B" if f.severity in ("high", "medium")
                    else "#3B82F6"
                )
                data.append([
                    Paragraph(f"<font color='{sev_c}'><b>{f.severity.upper()}</b></font>", body_style),
                    Paragraph(ln, body_style),
                    Paragraph(f"<b>{f.title}</b><br/>{f.description}", body_style),
                    Paragraph(f.suggestion, body_style),
                ])
            t = Table(data, colWidths=[60, 45, 230, 205], repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(t)
        else:
            story.append(Paragraph("<i>No issues reported by this agent.</i>", body_style))
        story.append(Spacer(1, 14))

    doc.build(story)
