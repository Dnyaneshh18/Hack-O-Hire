from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.audit import AuditLogger
from app.models.user import User
from app.models.sar import SAR, SARStatus, RiskLevel
from app.schemas.sar import SARCreate, SARResponse, SARUpdate, SARGenerate
from app.services.llm_service import LLMService
from app.services.export_service import ExportService
from app.services.email_service import EmailService
from pydantic import BaseModel, EmailStr

router = APIRouter()
llm_service = LLMService()
export_service = ExportService()
email_service = EmailService()

class DeleteSARsRequest(BaseModel):
    sar_ids: List[int]

class EmailExportRequest(BaseModel):
    recipient_email: EmailStr
    format: str  # pdf, xml, or csv

@router.post("/generate", response_model=SARResponse)
async def generate_sar(
    sar_data: SARGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate SAR narrative using LLM with comprehensive analysis"""
    
    try:
        # Generate narrative with comprehensive analysis
        narrative, comprehensive_analysis = llm_service.generate_sar_narrative(
            customer_data=sar_data.customer_data,
            transaction_data=sar_data.transaction_data,
            kyc_data=sar_data.kyc_data,
            alert_reason=sar_data.alert_reason
        )
        
        # Extract risk assessment
        risk_assessment = comprehensive_analysis.get("risk_analysis", {})
        
        # Create SAR record with all analysis data
        new_sar = SAR(
            case_id=f"SAR-{uuid.uuid4().hex[:8].upper()}",
            customer_id=sar_data.customer_data.get("customer_id"),
            customer_name=sar_data.customer_data.get("name"),
            narrative=narrative,
            risk_score=risk_assessment.get("risk_score", 0),
            risk_level=RiskLevel(risk_assessment.get("risk_level", "medium")),
            typology=comprehensive_analysis.get("typology", "unknown"),
            status=SARStatus.DRAFT,
            created_by=current_user.id,
            transaction_data=sar_data.transaction_data,
            kyc_data=sar_data.kyc_data,
            reasoning_trace=comprehensive_analysis,
            data_sources={
                "customer_data": sar_data.customer_data,
                "alert_reason": sar_data.alert_reason
            },
            # Store comprehensive analysis
            facts=comprehensive_analysis.get("facts", ""),
            red_flags=comprehensive_analysis.get("red_flags", ""),
            evidence_map=comprehensive_analysis.get("evidence_map", ""),
            quality_check=comprehensive_analysis.get("quality_check", ""),
            contradictions=comprehensive_analysis.get("contradictions", ""),
            timeline=comprehensive_analysis.get("timeline", ""),
            typology_confidence=comprehensive_analysis.get("typology_confidence", ""),
            regulatory_highlights=comprehensive_analysis.get("regulatory_highlights", ""),
            executive_summary=comprehensive_analysis.get("executive_summary", ""),
            pii_check=comprehensive_analysis.get("pii_check", ""),
            reasoning_trace_detailed=comprehensive_analysis.get("reasoning_trace", ""),
            next_actions=comprehensive_analysis.get("next_actions", ""),
            improvements=comprehensive_analysis.get("improvements", "")
        )
        
        db.add(new_sar)
        db.commit()
        db.refresh(new_sar)
        
        # Log audit trail
        AuditLogger.log_sar_generation(
            db=db,
            user_id=current_user.id,
            sar_id=new_sar.id,
            input_data=sar_data.dict(),
            llm_response=narrative,
            reasoning_trace=comprehensive_analysis
        )
        
        return new_sar
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating SAR: {str(e)}"
        )

@router.get("/", response_model=List[SARResponse])
async def list_sars(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all SARs"""
    
    query = db.query(SAR)
    
    # Filter by status if provided
    if status_filter:
        query = query.filter(SAR.status == status_filter)
    
    # Analysts can only see their own SARs
    if current_user.role == "analyst":
        query = query.filter(SAR.created_by == current_user.id)
    
    sars = query.offset(skip).limit(limit).all()
    return sars

@router.get("/{sar_id}", response_model=SARResponse)
async def get_sar(
    sar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific SAR"""
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    # Check permissions
    if current_user.role == "analyst" and sar.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this SAR"
        )
    
    # Log data access
    AuditLogger.log_data_access(
        db=db,
        user_id=current_user.id,
        data_type="SAR",
        data_id=str(sar_id),
        action="VIEW"
    )
    
    return sar

@router.put("/{sar_id}", response_model=SARResponse)
async def update_sar(
    sar_id: int,
    sar_update: SARUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update SAR narrative"""
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    # Check permissions
    if current_user.role == "analyst" and sar.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this SAR"
        )
    
    # Update fields
    if sar_update.narrative:
        sar.narrative = sar_update.narrative
    if sar_update.status:
        sar.status = sar_update.status
    
    db.commit()
    db.refresh(sar)
    
    # Log audit trail
    AuditLogger.log_event(
        db=db,
        event_type="SAR_UPDATE",
        user_id=current_user.id,
        sar_id=sar_id,
        action="UPDATE",
        details=sar_update.dict(exclude_unset=True)
    )
    
    return sar

@router.post("/{sar_id}/approve", response_model=SARResponse)
async def approve_sar(
    sar_id: int,
    comments: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve SAR (supervisor/admin only)"""
    
    if current_user.role not in ["supervisor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only supervisors and admins can approve SARs"
        )
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    sar.status = SARStatus.APPROVED
    sar.approved_by = current_user.id
    sar.approved_at = datetime.utcnow()
    
    db.commit()
    db.refresh(sar)
    
    # Log approval
    AuditLogger.log_approval(
        db=db,
        user_id=current_user.id,
        sar_id=sar_id,
        approval_status="APPROVED",
        comments=comments
    )
    
    # Add to knowledge base for learning
    llm_service.rag_service.add_approved_sar(
        sar_id=str(sar_id),
        narrative=sar.narrative,
        metadata={
            "typology": sar.typology,
            "risk_level": sar.risk_level.value
        }
    )
    
    return sar

@router.post("/{sar_id}/reject", response_model=SARResponse)
async def reject_sar(
    sar_id: int,
    comments: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject SAR (supervisor/admin only)"""
    
    if current_user.role not in ["supervisor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only supervisors and admins can reject SARs"
        )
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    sar.status = SARStatus.REJECTED
    sar.reviewed_by = current_user.id
    sar.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(sar)
    
    # Log rejection
    AuditLogger.log_approval(
        db=db,
        user_id=current_user.id,
        sar_id=sar_id,
        approval_status="REJECTED",
        comments=comments
    )
    
    return sar

@router.delete("/{sar_id}")
async def delete_sar(
    sar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a single SAR"""
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    # Check permissions: admin/supervisor can delete any, analyst can delete their own
    if current_user.role == "analyst" and sar.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this SAR"
        )
    
    # Log deletion before removing
    AuditLogger.log_event(
        db=db,
        event_type="SAR_DELETION",
        user_id=current_user.id,
        sar_id=sar_id,
        action="DELETE",
        details={
            "case_id": sar.case_id,
            "customer_name": sar.customer_name,
            "status": sar.status.value,
            "deleted_at": datetime.utcnow().isoformat()
        }
    )
    
    db.delete(sar)
    db.commit()
    
    return {"message": "SAR deleted successfully", "sar_id": sar_id}

@router.post("/delete-multiple")
async def delete_multiple_sars(
    request: DeleteSARsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete multiple SARs by IDs"""
    
    if not request.sar_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No SAR IDs provided"
        )
    
    deleted_count = 0
    failed_ids = []
    
    for sar_id in request.sar_ids:
        sar = db.query(SAR).filter(SAR.id == sar_id).first()
        
        if not sar:
            failed_ids.append({"id": sar_id, "reason": "Not found"})
            continue
        
        # Check permissions
        if current_user.role == "analyst" and sar.created_by != current_user.id:
            failed_ids.append({"id": sar_id, "reason": "Not authorized"})
            continue
        
        # Log deletion
        AuditLogger.log_event(
            db=db,
            event_type="SAR_DELETION",
            user_id=current_user.id,
            sar_id=sar_id,
            action="DELETE_MULTIPLE",
            details={
                "case_id": sar.case_id,
                "customer_name": sar.customer_name,
                "status": sar.status.value,
                "deleted_at": datetime.utcnow().isoformat()
            }
        )
        
        db.delete(sar)
        deleted_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully deleted {deleted_count} SAR(s)",
        "deleted_count": deleted_count,
        "failed": failed_ids
    }

@router.delete("/delete-all")
async def delete_all_sars(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete all SARs (admin/supervisor only, or analyst's own SARs)"""
    
    query = db.query(SAR)
    
    # Analysts can only delete their own SARs
    if current_user.role == "analyst":
        query = query.filter(SAR.created_by == current_user.id)
    elif current_user.role not in ["supervisor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete all SARs"
        )
    
    sars = query.all()
    deleted_count = len(sars)
    
    # Log bulk deletion
    AuditLogger.log_event(
        db=db,
        event_type="SAR_BULK_DELETION",
        user_id=current_user.id,
        sar_id=None,
        action="DELETE_ALL",
        details={
            "deleted_count": deleted_count,
            "user_role": current_user.role,
            "deleted_at": datetime.utcnow().isoformat()
        }
    )
    
    # Delete all
    for sar in sars:
        db.delete(sar)
    
    db.commit()
    
    return {
        "message": f"Successfully deleted {deleted_count} SAR(s)",
        "deleted_count": deleted_count
    }

@router.get("/{sar_id}/export/pdf")
async def export_sar_pdf(
    sar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export SAR as PDF"""
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    # Check permissions
    if current_user.role == "analyst" and sar.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export this SAR"
        )
    
    try:
        # Generate PDF
        pdf_buffer = export_service.generate_pdf_export(sar, db)
        
        # Log export
        AuditLogger.log_event(
            db=db,
            event_type="SAR_EXPORT",
            user_id=current_user.id,
            sar_id=sar_id,
            action="EXPORT_PDF",
            details={
                "case_id": sar.case_id,
                "exported_at": datetime.utcnow().isoformat()
            }
        )
        
        # Return PDF as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=SAR_{sar.case_id}.pdf"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )

@router.get("/{sar_id}/export/xml")
async def export_sar_xml(
    sar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export SAR as XML (FinCEN-compatible)"""
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    # Check permissions
    if current_user.role == "analyst" and sar.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export this SAR"
        )
    
    try:
        # Generate XML
        xml_content = export_service.generate_xml_export(sar, db)
        
        # Log export
        AuditLogger.log_event(
            db=db,
            event_type="SAR_EXPORT",
            user_id=current_user.id,
            sar_id=sar_id,
            action="EXPORT_XML",
            details={
                "case_id": sar.case_id,
                "exported_at": datetime.utcnow().isoformat()
            }
        )
        
        # Return XML as streaming response
        return StreamingResponse(
            iter([xml_content]),
            media_type="application/xml",
            headers={
                "Content-Disposition": f"attachment; filename=SAR_{sar.case_id}.xml"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating XML: {str(e)}"
        )

@router.get("/{sar_id}/export/csv")
async def export_sar_csv(
    sar_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export SAR as CSV"""
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    # Check permissions
    if current_user.role == "analyst" and sar.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export this SAR"
        )
    
    try:
        # Generate CSV
        csv_content = export_service.generate_csv_export(sar, db)
        
        # Log export
        AuditLogger.log_event(
            db=db,
            event_type="SAR_EXPORT",
            user_id=current_user.id,
            sar_id=sar_id,
            action="EXPORT_CSV",
            details={
                "case_id": sar.case_id,
                "exported_at": datetime.utcnow().isoformat()
            }
        )
        
        # Return CSV as streaming response
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=SAR_{sar.case_id}.csv"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating CSV: {str(e)}"
        )

@router.post("/{sar_id}/export/email")
async def email_sar_export(
    sar_id: int,
    request: EmailExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Email SAR export to recipient"""
    
    sar = db.query(SAR).filter(SAR.id == sar_id).first()
    
    if not sar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SAR not found"
        )
    
    # Check permissions
    if current_user.role == "analyst" and sar.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export this SAR"
        )
    
    # Validate format
    if request.format.lower() not in ['pdf', 'xml', 'csv']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid format. Must be pdf, xml, or csv"
        )
    
    try:
        # Generate export in requested format
        file_content = None
        if request.format.lower() == 'pdf':
            pdf_buffer = export_service.generate_pdf_export(sar, db)
            file_content = pdf_buffer.getvalue()
        elif request.format.lower() == 'xml':
            file_content = export_service.generate_xml_export(sar, db).encode('utf-8')
        elif request.format.lower() == 'csv':
            file_content = export_service.generate_csv_export(sar, db).encode('utf-8')
        
        # Send email
        result = email_service.send_sar_export(
            recipient_email=request.recipient_email,
            case_id=sar.case_id,
            file_content=file_content,
            file_format=request.format.lower()
        )
        
        # Log email export
        AuditLogger.log_event(
            db=db,
            event_type="SAR_EXPORT",
            user_id=current_user.id,
            sar_id=sar_id,
            action="EXPORT_EMAIL",
            details={
                "case_id": sar.case_id,
                "recipient": request.recipient_email,
                "format": request.format.lower(),
                "exported_at": datetime.utcnow().isoformat()
            }
        )
        
        if result.get("success"):
            return {
                "success": True,
                "message": f"SAR {sar.case_id} sent successfully to {request.recipient_email}",
                "case_id": sar.case_id,
                "recipient": request.recipient_email,
                "format": request.format.lower()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Failed to send email")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error sending email: {str(e)}"
        )

