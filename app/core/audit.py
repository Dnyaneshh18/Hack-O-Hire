from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
import json
import logging

from app.models.audit import AuditLog

logger = logging.getLogger(__name__)

class AuditLogger:
    """Comprehensive audit logging system for SAR generation"""
    
    @staticmethod
    def log_event(
        db: Session,
        event_type: str,
        user_id: Optional[int],
        sar_id: Optional[int],
        action: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log an audit event"""
        try:
            audit_log = AuditLog(
                event_type=event_type,
                user_id=user_id,
                sar_id=sar_id,
                action=action,
                details=json.dumps(details),
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            db.commit()
            logger.info(f"Audit log created: {event_type} - {action}")
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            db.rollback()
    
    @staticmethod
    def log_sar_generation(
        db: Session,
        user_id: int,
        sar_id: int,
        input_data: Dict[str, Any],
        llm_response: str,
        reasoning_trace: Dict[str, Any]
    ):
        """Log SAR narrative generation with full reasoning trace"""
        AuditLogger.log_event(
            db=db,
            event_type="SAR_GENERATION",
            user_id=user_id,
            sar_id=sar_id,
            action="GENERATE_NARRATIVE",
            details={
                "input_data": input_data,
                "llm_response": llm_response,
                "reasoning_trace": reasoning_trace,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def log_data_access(
        db: Session,
        user_id: int,
        data_type: str,
        data_id: str,
        action: str
    ):
        """Log data access for compliance"""
        AuditLogger.log_event(
            db=db,
            event_type="DATA_ACCESS",
            user_id=user_id,
            sar_id=None,
            action=action,
            details={
                "data_type": data_type,
                "data_id": data_id,
                "access_time": datetime.utcnow().isoformat()
            }
        )
    
    @staticmethod
    def log_approval(
        db: Session,
        user_id: int,
        sar_id: int,
        approval_status: str,
        comments: Optional[str] = None
    ):
        """Log SAR approval/rejection"""
        AuditLogger.log_event(
            db=db,
            event_type="SAR_APPROVAL",
            user_id=user_id,
            sar_id=sar_id,
            action=approval_status,
            details={
                "status": approval_status,
                "comments": comments,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
