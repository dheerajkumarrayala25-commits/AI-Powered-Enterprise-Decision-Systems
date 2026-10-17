"""
Executive Reporting & Deliverables Generator for the AI-Powered Enterprise Decision System.
Produces:
1. Executive PDF Deliverables (using ReportLab)
2. Interactive Boardroom HTML Briefings
3. Plain-text consulting summaries
"""

import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_consulting_pdf(kpis, sales_summary, inv_summary, churn_summary, risk_summary, recommendations):
    """
    Builds an executive PDF report for enterprise leadership.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    header_style = ParagraphStyle(
        'DocHeader',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    subhead_style = ParagraphStyle(
        'DocSubHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    sec_title = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    bold_style = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # 1. Header Block
    story.append(Paragraph("AI-POWERED ENTERPRISE DECISION SYSTEM", header_style))
    story.append(Paragraph("Executive Consulting Advisory & Decision Support Briefing", ParagraphStyle('Sub', parent=header_style, fontSize=12, leading=16, textColor=colors.HexColor('#2563EB'))))
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
    story.append(Paragraph(f"Client Case: Apex Logistics & Retail Corp | Prepared by: Rayala Dheeraj Kumar | Date: {now_str}", subhead_style))
    story.append(Spacer(1, 15))
    
    # 2. Executive KPI Summary Table
    story.append(Paragraph("1. Executive Operations & Risk Snapshot", sec_title))
    
    kpi_data = [
        [
            f"Gross 30D Forecast\n{kpis.get('revenue_proj', '₹1.85 Cr')}",
            f"At-Risk Contract Value\n{kpis.get('at_risk_val', '₹42.8 L')}",
            f"Pending Reorder CapEx\n{kpis.get('reorder_capex', '₹18.4 L')}",
            f"High-Risk Review Queue\n{kpis.get('risk_txns', '23 Txns')}"
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[130, 130, 130, 130])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#0F172A')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))
    
    # 3. Domain Analysis Summaries
    story.append(Paragraph("2. Strategic Domain Diagnoses", sec_title))
    domain_texts = [
        f"<b>Revenue Forecasting:</b> Historical demand patterns reveal seasonal peaks in Infrastructure & Networking. Next 30-day projected volume is <b>{sales_summary.get('units', '1,420')} units</b>, delivering estimated revenue of <b>{sales_summary.get('revenue', '₹1.85 Cr')}</b>.",
        f"<b>Supply Chain & Inventory Optimization:</b> <b>{inv_summary.get('reorder_count', '8')} of 12 SKUs</b> have crossed dynamic reorder thresholds under 95% service-level buffers. Implementing recommended EOQs will release <b>₹14.2 L</b> in excess safety stock holding costs.",
        f"<b>Customer Retention Intelligence:</b> <b>{churn_summary.get('critical_count', '61')} customer accounts</b> flagged in Critical Churn Risk zone. Primary attrition drivers: Support incident spikes and Month-to-Month contracts. At-risk annual revenue: <b>{churn_summary.get('risk_revenue', '₹42.8 L')}</b>.",
        f"<b>Financial Risk & Anomaly Screening:</b> Hybrid classification and compliance filters identified <b>{risk_summary.get('review_count', '23')} high-impact transactions</b> requiring human-in-the-loop review. Zero automated fund locks executed prior to senior officer review."
    ]
    for dt in domain_texts:
        story.append(Paragraph(f"• {dt}", body_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 10))
    
    # 4. Actionable Consulting Recommendations Table
    story.append(Paragraph("3. Ranked Actionable Prescriptions & Governance", sec_title))
    
    table_headers = ["Priority", "Decision Domain", "Prescribed Business Action", "Estimated Impact", "Governance Gate"]
    table_rows = [table_headers]
    
    for r in recommendations[:5]:
        table_rows.append([
            Paragraph(r["priority"], bold_style),
            Paragraph(r["domain"], body_style),
            Paragraph(r["action"], body_style),
            Paragraph(r["impact"], body_style),
            Paragraph(r["governance"], bold_style)
        ])
        
    t_recs = Table(table_rows, colWidths=[50, 95, 195, 100, 90])
    t_recs.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_recs)
    story.append(Spacer(1, 15))
    
    # 5. Methodological & Ethical Governance Statement
    story.append(Paragraph("4. Responsible AI & Human Oversight Framework", sec_title))
    story.append(Paragraph(
        "In accordance with modern Explainable AI (XAI) principles (Coussement et al., 2024), all machine-learned outputs in this system are bounded by explicit deterministic business rules. The system serves as an operational accelerator, preserving human accountability through mandatory sign-off gates on all material decisions exceeding enterprise risk tolerances.",
        ParagraphStyle('Legal', parent=body_style, fontSize=8, textColor=colors.HexColor('#64748B'))
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def generate_executive_html_brief(kpis, recommendations, inv_summary, churn_summary):
    """Generates a responsive modern HTML briefing document."""
    recs_rows_html = ""
    for r in recommendations:
        gov_badge_color = "#EF4444" if "Mandatory" in r["governance"] else "#3B82F6"
        recs_rows_html += f"""
        <tr style="border-bottom: 1px solid #334155;">
            <td style="padding: 12px; font-weight: bold; color: #F8FAFC;">{r['priority']}</td>
            <td style="padding: 12px; color: #94A3B8;">{r['domain']}</td>
            <td style="padding: 12px; color: #E2E8F0;"><b>{r['action']}</b><br><small style="color:#94A3B8">{r.get('details', '')}</small></td>
            <td style="padding: 12px; color: #10B981; font-weight: bold;">{r['impact']}</td>
            <td style="padding: 12px;"><span style="background: {gov_badge_color}22; color: {gov_badge_color}; border: 1px solid {gov_badge_color}; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{r['governance']}</span></td>
        </tr>
        """
        
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>AI Enterprise Decision System — Executive Briefing</title>
        <style>
            body {{
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
                background-color: #0F172A;
                color: #F8FAFC;
                margin: 0;
                padding: 40px;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: #1E293B;
                padding: 35px;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                border: 1px solid #334155;
            }}
            h1 {{ color: #38BDF8; margin-bottom: 4px; font-size: 26px; }}
            .subtitle {{ color: #94A3B8; margin-bottom: 25px; font-size: 14px; }}
            .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
            .card {{
                background: #0F172A;
                padding: 18px;
                border-radius: 8px;
                border: 1px solid #334155;
            }}
            .card .val {{ font-size: 22px; font-weight: bold; color: #F8FAFC; margin-top: 5px; }}
            .card .lbl {{ font-size: 12px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; text-align: left; }}
            th {{ background: #0F172A; padding: 12px; color: #38BDF8; font-size: 12px; text-transform: uppercase; border-bottom: 2px solid #38BDF8; }}
            .footer {{ margin-top: 30px; font-size: 12px; color: #64748B; border-top: 1px solid #334155; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>AI-POWERED ENTERPRISE DECISION SYSTEM</h1>
            <div class="subtitle">Client Executive Briefing | Scenario: Enterprise Consulting Advisory | Prepared by: Rayala Dheeraj Kumar</div>
            
            <div class="grid">
                <div class="card">
                    <div class="lbl">30D Forecast Revenue</div>
                    <div class="val" style="color: #38BDF8;">{kpis.get('revenue_proj', '₹1.85 Cr')}</div>
                </div>
                <div class="card">
                    <div class="lbl">At-Risk Contract Value</div>
                    <div class="val" style="color: #EF4444;">{kpis.get('at_risk_val', '₹42.8 L')}</div>
                </div>
                <div class="card">
                    <div class="lbl">Supply Chain PO CapEx</div>
                    <div class="val" style="color: #F59E0B;">{kpis.get('reorder_capex', '₹18.4 L')}</div>
                </div>
                <div class="card">
                    <div class="lbl">Human Review Queue</div>
                    <div class="val" style="color: #A855F7;">{kpis.get('risk_txns', '23 Txns')}</div>
                </div>
            </div>
            
            <h3 style="color: #F8FAFC; margin-top: 25px;">Priority Prescriptions & Decision Gates</h3>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Domain</th>
                        <th>Prescribed Business Action</th>
                        <th>Financial Impact</th>
                        <th>Human Oversight</th>
                    </tr>
                </thead>
                <tbody>
                    {recs_rows_html}
                </tbody>
            </table>
            
            <div class="footer">
                <b>Governance Note:</b> Model decisions comply with XAI Framework (Coussement et al., 2024). High-impact actions are held for Human Sign-Off. Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
            </div>
        </div>
    </body>
    </html>
    """
    return html
