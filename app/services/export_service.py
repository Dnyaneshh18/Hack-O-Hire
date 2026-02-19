"""
Export Service for SAR PDF and XML Generation
Generates regulatory-compliant exports of SAR reports
"""

from typing import Dict, Any
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import xml.etree.ElementTree as ET
from xml.dom import minidom

from app.models.sar import SAR
from sqlalchemy.orm import Session


class ExportService:
    """Service for exporting SARs to PDF and XML formats"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for PDF"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00AEEF'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0088BD'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Risk level style
        self.styles.add(ParagraphStyle(
            name='RiskLevel',
            parent=self.styles['Normal'],
            fontSize=16,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        ))
    
    def generate_pdf_export(self, sar: SAR, db: Session) -> BytesIO:
        """
        Generate PDF export of SAR
        
        Args:
            sar: SAR object to export
            db: Database session
            
        Returns:
            BytesIO: PDF file buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Container for PDF elements
        story = []
        
        # Add cover page
        story.extend(self._create_cover_page(sar))
        story.append(Spacer(1, 0.3*inch))
        
        # Add executive summary (if exists)
        if sar.executive_summary:
            story.extend(self._create_executive_summary(sar))
            story.append(Spacer(1, 0.2*inch))
        
        # Add customer information
        story.extend(self._create_customer_section(sar))
        story.append(Spacer(1, 0.2*inch))
        
        # Add transaction analysis (narrative)
        story.extend(self._create_transaction_section(sar))
        story.append(Spacer(1, 0.2*inch))
        
        # Add key analysis sections (most important ones)
        story.extend(self._create_key_analysis_section(sar))
        story.append(Spacer(1, 0.2*inch))
        
        # Add audit trail (moved up for better space usage)
        story.extend(self._create_audit_section(sar))
        story.append(Spacer(1, 0.2*inch))
        
        # Add detailed analysis sections (remaining ones)
        story.extend(self._create_detailed_analysis_section(sar))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        
        buffer.seek(0)
        return buffer
    
    def _create_cover_page(self, sar: SAR) -> list:
        """Create PDF cover page"""
        elements = []
        
        # Title
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph("SUSPICIOUS ACTIVITY REPORT", self.styles['CustomTitle']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Style for table content
        table_style = ParagraphStyle(
            'CoverTableContent',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=16,
        )
        
        # Case information table - wrap all content in Paragraph objects
        case_info = [
            [Paragraph("<b>Case ID:</b>", table_style), Paragraph(sar.case_id or "N/A", table_style)],
            [Paragraph("<b>Filing Date:</b>", table_style), Paragraph(sar.created_at.strftime("%Y-%m-%d"), table_style)],
            [Paragraph("<b>Institution:</b>", table_style), Paragraph("Barclays Bank", table_style)],
            [Paragraph("<b>Status:</b>", table_style), Paragraph(sar.status.value.upper(), table_style)],
        ]
        
        case_table = Table(case_info, colWidths=[2*inch, 4*inch])
        case_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0088BD')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(case_table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Risk level box with better contrast
        risk_level = sar.risk_level.value.upper() if sar.risk_level else 'MEDIUM'
        risk_color = self._get_risk_color(risk_level)
        
        # Create risk level as a table for better control
        risk_data = [[f"RISK LEVEL: {risk_level}"]]
        risk_table = Table(risk_data, colWidths=[6*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(risk_color)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 18),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ]))
        
        elements.append(risk_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Risk score
        if sar.risk_score:
            score_data = [[f"Risk Score: {sar.risk_score}/100"]]
            score_table = Table(score_data, colWidths=[6*inch])
            score_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(score_table)
        
        return elements
    
    def _create_executive_summary(self, sar: SAR) -> list:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.08*inch))
        
        if sar.executive_summary:
            # Compact summary style
            summary_style = ParagraphStyle(
                'SummaryText',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=14,
                leftIndent=10,
                rightIndent=10,
            )
            
            summary_para = Paragraph(sar.executive_summary, summary_style)
            summary_table = Table([[summary_para]], colWidths=[6.5*inch])
            summary_table.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0088BD')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E3F2FD')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(summary_table)
        
        return elements
    
    def _create_customer_section(self, sar: SAR) -> list:
        """Create customer information section"""
        elements = []
        
        elements.append(Paragraph("SUBJECT INFORMATION", self.styles['SectionHeader']))
        
        # Style for table content
        table_style = ParagraphStyle(
            'TableContent',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
        )
        
        # Wrap all content in Paragraph objects for proper text wrapping
        customer_data = [
            [Paragraph("Subject Name:", table_style), Paragraph(sar.customer_name or "N/A", table_style)],
            [Paragraph("Subject ID:", table_style), Paragraph(sar.customer_id or "N/A", table_style)],
            [Paragraph("Risk Classification:", table_style), Paragraph((sar.risk_level.value.upper() if sar.risk_level else "N/A"), table_style)],
            [Paragraph("Risk Score:", table_style), Paragraph(f"{sar.risk_score}/100" if sar.risk_score else "N/A", table_style)],
            [Paragraph("Typology:", table_style), Paragraph((sar.typology.upper() if sar.typology else "N/A"), table_style)],
        ]
        
        customer_table = Table(customer_data, colWidths=[2.5*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E3F2FD')),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(customer_table)
        
        return elements
    
    def _create_transaction_section(self, sar: SAR) -> list:
        """Create transaction analysis section"""
        elements = []
        
        elements.append(Paragraph("SUSPICIOUS ACTIVITY NARRATIVE", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.08*inch))
        
        # Add narrative using Paragraph for proper text wrapping
        if sar.narrative:
            # Compact narrative style
            narrative_style = ParagraphStyle(
                'NarrativeText',
                parent=self.styles['Normal'],
                fontSize=10,
                leading=14,
                alignment=0,
                leftIndent=12,
                rightIndent=12,
            )
            
            # Wrap the narrative in a Paragraph for proper text flow
            narrative_para = Paragraph(sar.narrative, narrative_style)
            
            # Put it in a table for the border and background
            narrative_table = Table([[narrative_para]], colWidths=[6.5*inch])
            narrative_table.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#0088BD')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(narrative_table)
        
        return elements
    
    def _create_key_analysis_section(self, sar: SAR) -> list:
        """Create key analysis section with most important information"""
        elements = []
        
        elements.append(Paragraph("KEY ANALYSIS", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Key sections in a compact format
        key_sections = [
            ("TYPOLOGY CLASSIFICATION", sar.typology),
            ("RED FLAGS IDENTIFIED", sar.red_flags),
            ("EXTRACTED FACTS", sar.facts),
        ]
        
        # Compact style
        section_style = ParagraphStyle(
            'KeySection',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0088BD'),
            spaceAfter=6,
            spaceBefore=8,
        )
        
        content_style = ParagraphStyle(
            'KeyContent',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=13,
            leftIndent=10,
            rightIndent=10,
        )
        
        for section_name, section_content in key_sections:
            if section_content:
                elements.append(Paragraph(section_name, section_style))
                
                # Compact box
                content_para = Paragraph(str(section_content), content_style)
                content_table = Table([[content_para]], colWidths=[6.5*inch])
                content_table.setStyle(TableStyle([
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(content_table)
                elements.append(Spacer(1, 0.08*inch))
        
        return elements
    
    def _create_detailed_analysis_section(self, sar: SAR) -> list:
        """Create detailed analysis section with remaining information"""
        elements = []
        
        # No header - just continue with sections for cleaner look
        
        # Remaining sections
        detailed_sections = [
            ("EVIDENCE MAPPING", sar.evidence_map),
            ("QUALITY ASSESSMENT", sar.quality_check),
            ("TRANSACTION TIMELINE", sar.timeline),
            ("TYPOLOGY CONFIDENCE", sar.typology_confidence),
            ("REGULATORY HIGHLIGHTS", sar.regulatory_highlights),
            ("CONTRADICTION ANALYSIS", sar.contradictions),
            ("PII COMPLIANCE CHECK", sar.pii_check),
            ("REASONING TRACE", sar.reasoning_trace_detailed),
            ("RECOMMENDED ACTIONS", sar.next_actions),
            ("IMPROVEMENT SUGGESTIONS", sar.improvements),
        ]
        
        # Compact style
        section_style = ParagraphStyle(
            'DetailSection',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0088BD'),
            spaceAfter=5,
            spaceBefore=8,
        )
        
        content_style = ParagraphStyle(
            'DetailContent',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
            leftIndent=8,
            rightIndent=8,
        )
        
        for section_name, section_content in detailed_sections:
            if section_content:
                elements.append(Paragraph(section_name, section_style))
                
                # Compact box
                content_para = Paragraph(str(section_content), content_style)
                content_table = Table([[content_para]], colWidths=[6.5*inch])
                content_table.setStyle(TableStyle([
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(content_table)
                elements.append(Spacer(1, 0.06*inch))
        
        return elements
        """Create 16-stage analysis section"""
        elements = []
        
        elements.append(Paragraph("COMPREHENSIVE ANALYSIS & SUPPORTING DOCUMENTATION", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Add note
        note_style = ParagraphStyle(
            'Note',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            italic=True
        )
        elements.append(Paragraph(
            "The following sections provide detailed analysis supporting the suspicious activity determination:",
            note_style
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Define all 16 stages with better formatting
        stages = [
            ("1. EXTRACTED FACTS", sar.facts),
            ("2. RED FLAGS IDENTIFIED", sar.red_flags),
            ("3. TYPOLOGY CLASSIFICATION", sar.typology),
            ("4. EVIDENCE MAPPING", sar.evidence_map),
            ("5. QUALITY ASSESSMENT", sar.quality_check),
            ("6. TRANSACTION TIMELINE", sar.timeline),
            ("7. TYPOLOGY CONFIDENCE", sar.typology_confidence),
            ("8. REGULATORY HIGHLIGHTS", sar.regulatory_highlights),
            ("9. EXECUTIVE SUMMARY", sar.executive_summary),
            ("10. CONTRADICTION ANALYSIS", sar.contradictions),
            ("11. PII COMPLIANCE CHECK", sar.pii_check),
            ("12. REASONING TRACE", sar.reasoning_trace_detailed),
            ("13. RECOMMENDED ACTIONS", sar.next_actions),
            ("14. IMPROVEMENT SUGGESTIONS", sar.improvements),
        ]
        
        # Section header style
        section_style = ParagraphStyle(
            'AnalysisSection',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#0088BD'),
            spaceAfter=8,
            spaceBefore=12,
        )
        
        # Content style with proper wrapping
        content_style = ParagraphStyle(
            'AnalysisContent',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
            leftIndent=12,
            rightIndent=12,
            alignment=0,  # Left align
        )
        
        for stage_name, stage_content in stages:
            if stage_content:
                elements.append(Paragraph(stage_name, section_style))
                
                # Use Paragraph for proper text wrapping
                content_para = Paragraph(str(stage_content), content_style)
                
                # Put content in a light grey box
                content_table = Table([[content_para]], colWidths=[6.5*inch])
                content_table.setStyle(TableStyle([
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAFA')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(content_table)
                elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_audit_section(self, sar: SAR) -> list:
        """Create audit trail section"""
        elements = []
        
        elements.append(Paragraph("FILING INFORMATION & AUDIT TRAIL", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.08*inch))
        
        # Style for audit table content
        audit_style = ParagraphStyle(
            'AuditContent',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
        )
        
        # Compact audit table - wrap all content in Paragraph objects
        audit_data = [
            [Paragraph("<b>Case ID:</b>", audit_style), Paragraph(sar.case_id or "N/A", audit_style), 
             Paragraph("<b>Status:</b>", audit_style), Paragraph(sar.status.value.upper(), audit_style)],
            [Paragraph("<b>Filed By:</b>", audit_style), Paragraph(f"User ID: {sar.created_by}", audit_style), 
             Paragraph("<b>Filing Date:</b>", audit_style), Paragraph(sar.created_at.strftime("%Y-%m-%d %H:%M UTC"), audit_style)],
            [Paragraph("<b>Institution:</b>", audit_style), Paragraph("Barclays Bank", audit_style), 
             Paragraph("<b>Last Modified:</b>", audit_style), Paragraph(sar.updated_at.strftime("%Y-%m-%d %H:%M UTC") if sar.updated_at else "N/A", audit_style)],
        ]
        
        # Two-column layout for compact display
        audit_table = Table(audit_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        audit_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FFF3E0')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#FFF3E0')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(audit_table)
        
        return elements
    
    def _add_footer(self, canvas, doc):
        """Add footer to each page"""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.grey)
        
        # Confidential notice
        canvas.drawCentredString(letter[0]/2, 0.5*inch, 
                                "CONFIDENTIAL - For Official Use Only")
        
        # Page number
        page_num = canvas.getPageNumber()
        canvas.drawRightString(letter[0] - 0.5*inch, 0.5*inch, 
                              f"Page {page_num}")
        
        canvas.restoreState()
    
    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level"""
        colors_map = {
            'LOW': '#4CAF50',
            'MEDIUM': '#FF9800',
            'HIGH': '#FF5722',
            'CRITICAL': '#F44336'
        }
        return colors_map.get(risk_level, '#FF9800')
    
    def generate_xml_export(self, sar: SAR, db: Session) -> str:
        """
        Generate XML export of SAR (FinCEN-compatible format)
        
        Args:
            sar: SAR object to export
            db: Database session
            
        Returns:
            str: XML string
        """
        # Create root element
        root = ET.Element("SuspiciousActivityReport")
        root.set("version", "1.0")
        root.set("xmlns", "http://www.fincen.gov/sar")
        
        # Case information
        case_info = ET.SubElement(root, "CaseInformation")
        ET.SubElement(case_info, "CaseID").text = sar.case_id
        ET.SubElement(case_info, "FilingDate").text = sar.created_at.strftime("%Y-%m-%d")
        ET.SubElement(case_info, "Institution").text = "Barclays Bank"
        ET.SubElement(case_info, "Status").text = sar.status.value
        
        # Customer information
        customer_info = ET.SubElement(root, "CustomerInformation")
        ET.SubElement(customer_info, "Name").text = sar.customer_name or ""
        ET.SubElement(customer_info, "CustomerID").text = sar.customer_id or ""
        ET.SubElement(customer_info, "RiskLevel").text = sar.risk_level.value if sar.risk_level else "MEDIUM"
        
        # Analysis results
        analysis = ET.SubElement(root, "AnalysisResults")
        ET.SubElement(analysis, "RiskScore").text = str(sar.risk_score) if sar.risk_score else "0"
        ET.SubElement(analysis, "Typology").text = sar.typology or ""
        ET.SubElement(analysis, "Narrative").text = sar.narrative or ""
        
        # 16-stage analysis
        stages = ET.SubElement(analysis, "ComprehensiveAnalysis")
        
        stage_data = {
            "Facts": sar.facts,
            "RedFlags": sar.red_flags,
            "EvidenceMap": sar.evidence_map,
            "QualityCheck": sar.quality_check,
            "Timeline": sar.timeline,
            "TypologyConfidence": sar.typology_confidence,
            "RegulatoryHighlights": sar.regulatory_highlights,
            "ExecutiveSummary": sar.executive_summary,
            "Contradictions": sar.contradictions,
            "PIICheck": sar.pii_check,
            "ReasoningTrace": sar.reasoning_trace_detailed,
            "NextActions": sar.next_actions,
            "Improvements": sar.improvements,
        }
        
        for stage_name, stage_content in stage_data.items():
            if stage_content:
                ET.SubElement(stages, stage_name).text = str(stage_content)
        
        # Audit trail
        audit = ET.SubElement(root, "AuditTrail")
        ET.SubElement(audit, "CreatedBy").text = str(sar.created_by)
        ET.SubElement(audit, "CreatedDate").text = sar.created_at.isoformat()
        if sar.updated_at:
            ET.SubElement(audit, "LastUpdated").text = sar.updated_at.isoformat()
        
        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
        
        return xml_str
    
    def generate_csv_export(self, sar: SAR, db: Session) -> str:
        """
        Generate CSV export of SAR
        
        Args:
            sar: SAR object to export
            db: Database session
            
        Returns:
            str: CSV string
        """
        import csv
        from io import StringIO
        
        output = StringIO()
        # Use QUOTE_ALL to properly escape all fields
        writer = csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator='\n')
        
        # Header
        writer.writerow(['Field', 'Value'])
        
        # Basic Information
        writer.writerow(['Case ID', sar.case_id or ''])
        writer.writerow(['Customer Name', sar.customer_name or ''])
        writer.writerow(['Customer ID', sar.customer_id or ''])
        writer.writerow(['Status', sar.status.value if sar.status else ''])
        writer.writerow(['Risk Level', sar.risk_level.value.upper() if sar.risk_level else ''])
        writer.writerow(['Risk Score', str(sar.risk_score) if sar.risk_score else ''])
        writer.writerow(['Typology', sar.typology.upper() if sar.typology else ''])
        writer.writerow(['Created Date', sar.created_at.strftime("%Y-%m-%d %H:%M:%S") if sar.created_at else ''])
        writer.writerow(['Created By', f'User ID: {sar.created_by}' if sar.created_by else ''])
        writer.writerow(['Institution', 'Barclays Bank'])
        
        # Add separator
        writer.writerow([])
        
        # Narrative
        writer.writerow(['SAR Narrative', ''])
        if sar.narrative:
            # Clean and escape narrative text
            narrative_clean = str(sar.narrative).replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            writer.writerow(['', narrative_clean])
        
        # Analysis Sections
        analysis_sections = [
            ('Executive Summary', sar.executive_summary),
            ('Extracted Facts', sar.facts),
            ('Red Flags Identified', sar.red_flags),
            ('Typology Classification', sar.typology),
            ('Transaction Timeline', sar.timeline),
            ('Typology Confidence', sar.typology_confidence),
            ('Evidence Mapping', sar.evidence_map),
            ('Quality Assessment', sar.quality_check),
            ('Contradiction Analysis', sar.contradictions),
            ('Regulatory Highlights', sar.regulatory_highlights),
            ('PII Compliance Check', sar.pii_check),
            ('Reasoning Trace', sar.reasoning_trace_detailed),
            ('Recommended Actions', sar.next_actions),
            ('Improvement Suggestions', sar.improvements),
        ]
        
        for section_name, section_content in analysis_sections:
            if section_content:
                writer.writerow([])
                writer.writerow([section_name, ''])
                # Clean and escape content
                content_clean = str(section_content).replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
                writer.writerow(['', content_clean])
        
        # Add separator
        writer.writerow([])
        
        # Audit Information
        writer.writerow(['Audit Trail', ''])
        writer.writerow(['Filed By', f'User ID: {sar.created_by}' if sar.created_by else ''])
        writer.writerow(['Filing Date', sar.created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if sar.created_at else ''])
        writer.writerow(['Last Modified', sar.updated_at.strftime("%Y-%m-%d %H:%M:%S UTC") if sar.updated_at else 'N/A'])
        writer.writerow(['Current Status', sar.status.value.upper() if sar.status else ''])
        
        return output.getvalue()
