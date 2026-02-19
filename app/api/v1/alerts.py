from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertResponse, AlertUpdate

router = APIRouter()

@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new alert"""
    
    new_alert = Alert(
        alert_id=f"ALERT-{uuid.uuid4().hex[:8].upper()}",
        customer_id=alert_data.customer_id,
        customer_name=alert_data.customer_name,
        account_number=alert_data.account_number,
        alert_reason=alert_data.alert_reason,
        alert_type=alert_data.alert_type,
        priority=alert_data.priority,
        transaction_data=alert_data.transaction_data,
        kyc_data=alert_data.kyc_data,
        customer_data=alert_data.customer_data,
        is_processed=False
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    return new_alert

@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    show_processed: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all alerts"""
    
    query = db.query(Alert)
    
    # Filter by processed status
    if not show_processed:
        query = query.filter(Alert.is_processed == False)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return alerts

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific alert"""
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update alert status"""
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    if alert_update.is_processed is not None:
        alert.is_processed = alert_update.is_processed
        if alert_update.is_processed:
            alert.processed_at = datetime.utcnow()
    
    if alert_update.sar_id is not None:
        alert.sar_id = alert_update.sar_id
    
    db.commit()
    db.refresh(alert)
    
    return alert

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete alert"""
    
    # Only admins can delete
    if current_user.role not in ["admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and supervisors can delete alerts"
        )
    
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
    
    return {"message": "Alert deleted successfully"}

@router.post("/bulk-process")
async def bulk_process_alerts(
    alert_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark multiple alerts as processed"""
    
    alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()
    
    for alert in alerts:
        alert.is_processed = True
        alert.processed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"{len(alerts)} alerts marked as processed"}
