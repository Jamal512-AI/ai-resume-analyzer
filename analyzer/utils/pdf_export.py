"""
PDF report generation using ReportLab.
Generates a styled PDF report from analysis results.
"""
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_report_pdf(analysis_data):
    """
    Generate a styled PDF report from analysis data.

    analysis_data should be a dict with keys like:
    - 'filename': original resume filename
    - 'summary': summary text
    - 'strength': strength text
    - 'weakness': weakness text
    - 'job_titles': job title suggestions text
    - 'skills': dict of skill scores
    - 'gap_analysis': gap analysis results dict
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25 * mm,
        leftMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1A237E'),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#4F6EF7'),
        spaceBefore=20,
        spaceAfter=10,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        leading=16,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=30,
    )

    elements = []

    # Title
    elements.append(Paragraph("Resume Analysis Report", title_style))
    elements.append(Paragraph("AI Resume Intelligence Platform", subtitle_style))

    if analysis_data.get('filename'):
        elements.append(Paragraph(f"File: {analysis_data['filename']}", subtitle_style))

    elements.append(HRFlowable(
        width="100%", thickness=2,
        color=colors.HexColor('#4F6EF7'),
        spaceAfter=20
    ))

    # Sections
    sections = [
        ('Summary', analysis_data.get('summary', '')),
        ('Strengths', analysis_data.get('strength', '')),
        ('Weaknesses & Suggestions', analysis_data.get('weakness', '')),
        ('Recommended Job Titles', analysis_data.get('job_titles', '')),
    ]

    for title, content in sections:
        if content:
            elements.append(Paragraph(title, heading_style))
            # Split content into paragraphs
            for para in content.split('\n'):
                para = para.strip()
                if para:
                    # Escape HTML special characters
                    para = para.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    # Convert markdown bold
                    para = para.replace('**', '<b>', 1).replace('**', '</b>', 1)
                    elements.append(Paragraph(para, body_style))
            elements.append(Spacer(1, 10))

    # Gap Analysis section
    gap = analysis_data.get('gap_analysis')
    if gap and isinstance(gap, dict):
        elements.append(Paragraph("Gap Analysis", heading_style))

        score = gap.get('match_score', 0)
        elements.append(Paragraph(f"Match Score: <b>{score}%</b>", body_style))
        elements.append(Spacer(1, 5))

        if gap.get('matching_skills'):
            elements.append(Paragraph("✅ Matching Skills:", body_style))
            for skill in gap['matching_skills']:
                elements.append(Paragraph(f"  • {skill}", body_style))

        if gap.get('missing_skills'):
            elements.append(Paragraph("❌ Missing Skills:", body_style))
            for skill in gap['missing_skills']:
                elements.append(Paragraph(f"  • {skill}", body_style))

        if gap.get('overall_assessment'):
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(gap['overall_assessment'], body_style))

    # Skills section
    skills = analysis_data.get('skills')
    if skills and isinstance(skills, dict):
        elements.append(Paragraph("Skills Assessment", heading_style))
        table_data = [['Skill Category', 'Score']]
        for skill, score in skills.items():
            table_data.append([skill, f"{score}/100"])

        table = Table(table_data, colWidths=[300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F6EF7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8F9FA'), colors.white]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CCCCCC')))
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER, spaceBefore=10,
    )
    elements.append(Paragraph("Generated by AI Resume Intelligence Platform | Powered by Google Gemini", footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
