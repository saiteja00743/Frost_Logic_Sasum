import io
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

class ReportService:
    @classmethod
    def generate_pdf_report(cls, analysis_data: Dict[str, Any]) -> bytes:
        """
        Generates a comprehensive, styled executive PDF report using ReportLab.
        Returns bytes of the generated PDF.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        primary_color = colors.HexColor("#0F172A")  # Deep Navy
        secondary_color = colors.HexColor("#0D9488")  # Teal
        text_dark = colors.HexColor("#1E293B")
        bg_light = colors.HexColor("#F8FAFC")
        border_color = colors.HexColor("#E2E8F0")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=primary_color,
        )

        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#64748B"),
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=primary_color,
            spaceBefore=14,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13.5,
            textColor=text_dark,
        )

        quote_style = ParagraphStyle(
            "QuoteStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#334155"),
        )

        badge_style = ParagraphStyle(
            "BadgeStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            alignment=1,
        )

        elements = []

        # Header Title
        elements.append(Paragraph("<b>CLAUSEGUARD AI</b>", title_style))
        elements.append(Paragraph("Automated Legal Document Intelligence & Traceable Risk Audit", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=2, color=secondary_color, spaceBefore=0, spaceAfter=12))

        # Meta summary card table
        risk_score = analysis_data.get("risk_score", 50)
        risk_color = colors.HexColor("#DC2626") if risk_score >= 65 else (colors.HexColor("#D97706") if risk_score >= 40 else colors.HexColor("#16A34A"))
        verif_summary = analysis_data.get("verification_summary", {})
        verif_rate = verif_summary.get("verification_rate_percent", 100)

        meta_data = [
            [
                Paragraph(f"<b>Document:</b> {analysis_data.get('document_name', 'Agreement')}", body_style),
                Paragraph(f"<b>Contract Type:</b> {analysis_data.get('contract_type', 'Commercial')}", body_style),
            ],
            [
                Paragraph(f"<b>Pages / Words:</b> {analysis_data.get('total_pages', 1)} pages | {analysis_data.get('word_count', 0):,} words", body_style),
                Paragraph(f"<b>Risk Score:</b> <font color='{risk_color.hexval()}'><b>{risk_score} / 100</b></font>", body_style),
            ],
            [
                Paragraph(f"<b>Audit Evidence Match:</b> {verif_rate}% verified", body_style),
                Paragraph(f"<b>Analysis Engine:</b> {analysis_data.get('engine_used', 'Intelligent AI')}", body_style),
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 260])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_light),
            ("BOX", (0, 0), (-1, -1), 1, border_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # Executive Summary
        elements.append(Paragraph("1. Executive Summary", heading_style))
        elements.append(Paragraph(analysis_data.get("document_summary", "No summary provided."), body_style))
        elements.append(Spacer(1, 12))

        # Contracting Parties
        parties = analysis_data.get("parties", [])
        if parties:
            elements.append(Paragraph("2. Contracting Parties", heading_style))
            p_rows = [[Paragraph("<b>Party Name</b>", body_style), Paragraph("<b>Contractual Role</b>", body_style), Paragraph("<b>Obligations Count</b>", body_style)]]
            for p in parties:
                p_rows.append([
                    Paragraph(p.get("name", "Unknown"), body_style),
                    Paragraph(p.get("role", "Party"), body_style),
                    Paragraph(str(p.get("obligations_count", 0)), body_style),
                ])
            p_table = Table(p_rows, colWidths=[200, 230, 100])
            p_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(p_table)
            elements.append(Spacer(1, 14))

        # Risk Analysis Findings
        risks = analysis_data.get("risks", [])
        if risks:
            elements.append(Paragraph("3. Evidence-Linked Risk Findings", heading_style))
            r_rows = [[
                Paragraph("<b>Risk & Category</b>", body_style),
                Paragraph("<b>Severity</b>", body_style),
                Paragraph("<b>Supporting Evidence & Source</b>", body_style),
                Paragraph("<b>Recommended Action</b>", body_style)
            ]]
            for r in risks:
                sev = r.get("severity", "medium").upper()
                sev_hex = "#DC2626" if sev == "HIGH" else ("#D97706" if sev == "MEDIUM" else "#16A34A")
                ev = r.get("evidence", {})
                quote = ev.get("quote", "N/A")
                pg = ev.get("page", 1)
                status = r.get("verification_status", "verified").upper()

                r_rows.append([
                    Paragraph(f"<b>{r.get('title', 'Risk')}</b><br/><font color='#64748B'>{r.get('category', '')}</font>", body_style),
                    Paragraph(f"<font color='{sev_hex}'><b>{sev}</b></font>", badge_style),
                    Paragraph(f'"{quote[:140]}..."<br/><b>Page: {pg}</b> | <i>Status: {status}</i>', quote_style),
                    Paragraph(r.get("recommended_action", "Review term"), body_style),
                ])
            r_table = Table(r_rows, colWidths=[130, 60, 200, 140])
            r_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(r_table)
            elements.append(Spacer(1, 14))

        # Obligations & Deadlines
        obligations = analysis_data.get("obligations", [])
        if obligations:
            elements.append(Paragraph("4. Contractual Obligations Tracker", heading_style))
            ob_rows = [[
                Paragraph("<b>Responsible Party</b>", body_style),
                Paragraph("<b>Obligation & Evidence</b>", body_style),
                Paragraph("<b>Deadline</b>", body_style),
                Paragraph("<b>Verification</b>", body_style)
            ]]
            for ob in obligations[:6]:  # Keep to top 6 in PDF
                ev = ob.get("evidence", {})
                pg = ev.get("page", 1)
                ob_rows.append([
                    Paragraph(f"<b>{ob.get('responsible_party', 'Party')}</b>", body_style),
                    Paragraph(f"{ob.get('obligation', '')}<br/><font color='#475569'><i>Page {pg}: \"{ev.get('quote', '')[:90]}...\"</i></font>", body_style),
                    Paragraph(ob.get("deadline", "Needs verification"), body_style),
                    Paragraph(f"<b>{ob.get('verification_status', 'verified').title()}</b>", badge_style),
                ])
            ob_table = Table(ob_rows, colWidths=[120, 250, 90, 70])
            ob_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(ob_table)
            elements.append(Spacer(1, 14))

        # Key Clauses
        clauses = analysis_data.get("key_clauses", [])
        if clauses:
            elements.append(Paragraph("5. Key Clauses & Commercial Impact", heading_style))
            c_rows = [[
                Paragraph("<b>Clause</b>", body_style),
                Paragraph("<b>Summary & Commercial Impact</b>", body_style),
                Paragraph("<b>Source Page</b>", body_style)
            ]]
            for c in clauses[:5]:
                ev = c.get("evidence", {})
                pg = ev.get("page", 1)
                c_rows.append([
                    Paragraph(f"<b>{c.get('title', '')}</b><br/><font color='#64748B'>{c.get('category', '')}</font>", body_style),
                    Paragraph(f"{c.get('summary', '')}<br/><b>Impact:</b> {c.get('impact', '')}", body_style),
                    Paragraph(f"Page {pg}", body_style),
                ])
            c_table = Table(c_rows, colWidths=[140, 330, 60])
            c_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, border_color),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(c_table)
            elements.append(Spacer(1, 16))

        # Legal Disclaimer
        disclaimer_text = (
            "<b>NOTICE & LEGAL DISCLAIMER:</b> This report was automatically generated by ClauseGuard AI to assist "
            "qualified human legal and business review. Automated extraction, risk scoring, and evidence verification "
            "do not constitute formal legal advice or a binding legal opinion. Always consult a qualified attorney for "
            "jurisdiction-specific contract execution and disputes."
        )
        disclaimer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10.5,
            textColor=colors.HexColor("#64748B"),
        )
        elements.append(HRFlowable(width="100%", thickness=0.5, color=border_color, spaceBefore=8, spaceAfter=8))
        elements.append(Paragraph(disclaimer_text, disclaimer_style))

        # Build document
        doc.build(elements)
        return buffer.getvalue()
