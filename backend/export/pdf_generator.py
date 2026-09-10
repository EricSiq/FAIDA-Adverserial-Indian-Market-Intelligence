import io
import html
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def _esc(val: Any) -> str:
    """Escapes XML/HTML entities for ReportLab Paragraph parser."""
    if val is None:
        return ""
    return html.escape(str(val))

class PreMortemPDFGenerator:
    """Generates clean, institutional-grade Pre-Mortem Audit One-Pager PDFs with zero emojis."""

    @classmethod
    def generate(cls, record: Dict[str, Any]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=12 * mm,
            rightMargin=12 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm
        )

        styles = getSampleStyleSheet()
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=19,
            textColor=colors.HexColor('#0F172A')
        )
        meta_style = ParagraphStyle(
            'DocMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#64748B')
        )
        header_right_style = ParagraphStyle(
            'HeaderRight',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            alignment=2,
            textColor=colors.HexColor('#1E293B')
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=13,
            textColor=colors.HexColor('#0F172A'),
            spaceBefore=8,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#334155')
        )
        body_bold = ParagraphStyle(
            'BodyBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor('#0F172A')
        )
        verdict_title_style = ParagraphStyle(
            'VerdictTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#991B1B')
        )
        verdict_meta_style = ParagraphStyle(
            'VerdictMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor('#475569')
        )
        score_num_style = ParagraphStyle(
            'ScoreNum',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=20,
            alignment=1,
            textColor=colors.HexColor('#DC2626')
        )
        score_label_style = ParagraphStyle(
            'ScoreLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=7,
            leading=9,
            alignment=1,
            textColor=colors.HexColor('#64748B')
        )
        link_style = ParagraphStyle(
            'TableLink',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            leading=10,
            textColor=colors.HexColor('#0284C7')
        )
        footer_style = ParagraphStyle(
            'FooterNotice',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7,
            leading=9,
            textColor=colors.HexColor('#64748B')
        )

        pm = record.get("pre_mortem") or {}
        lkb = record.get("lkb_packet") or {}
        facts = lkb.get("facts", [])
        biases = pm.get("detected_biases", [])
        inval = pm.get("invalidation_levels", {})

        symbol = _esc(record.get("symbol", "UNKNOWN")).upper()
        exchange = _esc(record.get("exchange", "NSE")).upper()
        action = _esc(record.get("action", "BUY")).upper()
        cmp_val = _esc(record.get("current_price") or "N/A")
        target_val = _esc(record.get("target_price") or "Market")
        created_at = _esc(str(record.get("created_at", "")).split("T")[0] or "Current")
        friction_score = int(record.get("friction_score", 50))
        session_id = _esc(record.get("id", "N/A"))
        verdict_headline = _esc(pm.get("headline_verdict", "Pre-Mortem Adversarial Invalidation Audit"))

        story = []

        # 1. Header Section
        header_left = [
            Paragraph("FAIDA Institutional Pre-Mortem Audit", title_style),
            Paragraph(f"Red-Team Invalidation Report | Indian Capital Markets | Date: {created_at}", meta_style)
        ]
        header_right = [
            Paragraph(f"<b>{symbol} ({exchange})</b> | <b>ACTION: {action}</b>", header_right_style),
            Paragraph(f"CMP: <b>INR {cmp_val}</b> | Target: <b>INR {target_val}</b>", header_right_style)
        ]
        header_table = Table(
            [[header_left, header_right]],
            colWidths=[105 * mm, 81 * mm]
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor('#0F172A'))
        ]))
        story.append(header_table)
        story.append(Spacer(1, 3 * mm))

        # 2. Friction Score & Headline Verdict Banner
        score_cell = [
            Paragraph(f"{friction_score}", score_num_style),
            Paragraph("FRICTION SCORE", score_label_style)
        ]
        verdict_cell = [
            Paragraph(verdict_headline, verdict_title_style),
            Spacer(1, 1 * mm),
            Paragraph(f"Session: <code>{session_id}</code> | Stance: Adversarial Red-Team Continuum Level 4", verdict_meta_style)
        ]
        verdict_table = Table(
            [[verdict_cell, score_cell]],
            colWidths=[155 * mm, 31 * mm]
        )
        verdict_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('LINEBEFORE', (0,0), (0,0), 3.5, colors.HexColor('#DC2626')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8)
        ]))
        story.append(verdict_table)
        story.append(Spacer(1, 2 * mm))

        # 3. Grounded Local Knowledge Base (Evidence Snapshot) Table
        story.append(Paragraph("1. Grounded Local Knowledge Base (Evidence Snapshot)", section_style))
        
        evidence_data = [[
            Paragraph("<b>Fact ID</b>", body_bold),
            Paragraph("<b>Category</b>", body_bold),
            Paragraph("<b>Metric</b>", body_bold),
            Paragraph("<b>Ground Value</b>", body_bold),
            Paragraph("<b>Data Source</b>", body_bold)
        ]]

        if facts:
            for f in facts:
                evidence_data.append([
                    Paragraph(f"<code>{_esc(f.get('id', ''))}</code>", body_style),
                    Paragraph(_esc(f.get('category', '')), body_style),
                    Paragraph(_esc(f.get('metric', '')), body_bold),
                    Paragraph(f"{_esc(f.get('value', ''))} {_esc(f.get('unit', ''))}", body_style),
                    Paragraph(_esc(f.get('source', '')), body_style)
                ])
        else:
            evidence_data.append([
                Paragraph("LKB-01", body_style),
                Paragraph("PRICE", body_style),
                Paragraph("Current Market Price", body_bold),
                Paragraph(f"INR {cmp_val}", body_style),
                Paragraph("NSE Real-time", body_style)
            ])


        evidence_table = Table(
            evidence_data,
            colWidths=[20 * mm, 28 * mm, 58 * mm, 42 * mm, 38 * mm]
        )
        evidence_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5)
        ]))
        story.append(evidence_table)
        story.append(Spacer(1, 2 * mm))

        # 4. Cognitive Biases & Behavioral Traps
        story.append(Paragraph("2. Cognitive Biases & Behavioral Traps Detected", section_style))
        if biases:
            for b in biases:
                b_name = _esc(b.get("bias_name", "Cognitive Bias"))
                b_sev = _esc(b.get("severity", "HIGH"))
                b_trap = _esc(b.get("psychological_trap", ""))
                b_reframe = _esc(b.get("reframing_advice", ""))

                bias_content = [
                    Paragraph(f"<b>[ALERT: {b_name.upper()}] ({b_sev} Severity)</b>", ParagraphStyle(
                        'BiasTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#B45309')
                    )),
                    Paragraph(f"<b>Trap:</b> {b_trap}", body_style),
                    Paragraph(f"<b>Reframing Check:</b> {b_reframe}", body_style)
                ]
                b_table = Table([[bias_content]], colWidths=[186 * mm])
                b_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFFBEB')),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#FDE68A')),
                    ('LINEBEFORE', (0,0), (0,0), 3, colors.HexColor('#D97706')),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6)
                ]))
                story.append(b_table)
                story.append(Spacer(1, 1.5 * mm))
        else:
            no_bias_msg = Paragraph("No prominent cognitive biases detected in hypothesis. Trade rationale appears disciplined.", body_style)
            story.append(no_bias_msg)
            story.append(Spacer(1, 1.5 * mm))

        # 5. Invalidation Discipline & Stop-Loss Levels
        story.append(Paragraph("3. Invalidation Discipline & Risk Levels", section_style))
        inval_price = _esc(inval.get("invalidation_price") or "Market Support Level")
        target_res = _esc(inval.get("take_profit_target") or "Resistance Level")

        inval_rows = [
            [
                Paragraph("<b>Thesis Invalidation Stop-Loss:</b>", body_bold),
                Paragraph(f"INR {inval_price} (Immediate exit discipline upon structural support breach to protect capital).", body_style)
            ],
            [
                Paragraph("<b>Resistance Invalidation Target:</b>", body_bold),
                Paragraph(f"INR {target_res} (Prior supply zone and descending technical resistance).", body_style)
            ]
        ]

        inval_table = Table(inval_rows, colWidths=[55 * mm, 131 * mm])
        inval_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6)
        ]))
        story.append(inval_table)
        story.append(Spacer(1, 2 * mm))

        # 6. References & Scraped Verification Links
        story.append(Paragraph("4. Grounded Evidence Sources & Scraped Verification Links", section_style))
        sources_data = [
            [
                Paragraph("<b>Source Entity</b>", body_bold),
                Paragraph("<b>Verification URL / Portal</b>", body_bold),
                Paragraph("<b>Extracted Metrics</b>", body_bold),
                Paragraph("<b>Data Cadence</b>", body_bold)
            ],
            [
                Paragraph("National Stock Exchange (NSE)", body_style),
                Paragraph(f'<a href="https://www.nseindia.com/get-quotes/equity?symbol={symbol}">nseindia.com/get-quotes/equity?symbol={symbol}</a>', link_style),
                Paragraph("Security Deliverables (Delivery %), 5D Volume, Real-time CMP", body_style),
                Paragraph("Live / T+0 Close", body_style)
            ],
            [
                Paragraph("Screener.in Financials", body_style),
                Paragraph(f'<a href="https://www.screener.in/company/{symbol}/consolidated/">screener.in/company/{symbol}/consolidated/</a>', link_style),
                Paragraph("10Y Median P/E, Operating Profit Margin (OPM), Promoter Pledging %", body_style),
                Paragraph("Quarterly Audited", body_style)
            ],
            [
                Paragraph("Clearing Corp of India (CCIL)", body_style),
                Paragraph('<a href="https://www.ccilindia.com/">ccilindia.com (Sovereign G-Sec Market)</a>', link_style),
                Paragraph("10-Year Benchmark Sovereign Yield (7.08%), Risk-free Baseline", body_style),
                Paragraph("Daily Yield Curve", body_style)
            ],
            [
                Paragraph("NSE Indices (India VIX)", body_style),
                Paragraph('<a href="https://www.nseindia.com/market-data/live-equity-market">nseindia.com/market-data/live-equity-market</a>', link_style),
                Paragraph("Implied Volatility Index, Market Regime Classification", body_style),
                Paragraph("Real-time Nifty Options", body_style)
            ]
        ]
        sources_table = Table(sources_data, colWidths=[40 * mm, 68 * mm, 56 * mm, 22 * mm])
        sources_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5)
        ]))
        story.append(sources_table)
        story.append(Spacer(1, 3 * mm))

        # 7. Regulatory Disclaimer Footer
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceBefore=2, spaceAfter=2))
        story.append(Paragraph(
            "<b>Regulatory Notice (SEBI Compliance):</b> FAIDA (Financial Adversarial Indian Data Agents) is strictly an educational research and adversarial pre-mortem risk-awareness tool powered by public Indian market data. It does NOT provide buy/sell recommendations or SEBI-registered financial advisory services. All investments in Indian capital markets are subject to market risks.",
            footer_style
        ))

        doc.build(story)
        return buffer.getvalue()
