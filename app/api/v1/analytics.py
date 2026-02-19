from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.sar import SAR, SARStatus, RiskLevel

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics"""
    
    # Total SARs
    total_sars = db.query(func.count(SAR.id)).scalar()
    
    # SARs by status
    status_counts = db.query(
        SAR.status,
        func.count(SAR.id)
    ).group_by(SAR.status).all()
    
    # SARs by risk level
    risk_counts = db.query(
        SAR.risk_level,
        func.count(SAR.id)
    ).group_by(SAR.risk_level).all()
    
    # Recent SARs (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_sars = db.query(func.count(SAR.id)).filter(
        SAR.created_at >= thirty_days_ago
    ).scalar()
    
    # Average risk score
    avg_risk_score = db.query(func.avg(SAR.risk_score)).scalar()
    
    # Approved SARs count
    approved_sars = db.query(func.count(SAR.id)).filter(
        SAR.status == SARStatus.APPROVED
    ).scalar()
    
    return {
        "total_sars": total_sars,
        "recent_sars": recent_sars,
        "approved_sars": approved_sars,
        "average_risk_score": float(avg_risk_score) if avg_risk_score else 0,
        "status_distribution": {status.value: count for status, count in status_counts},
        "risk_distribution": {risk.value: count for risk, count in risk_counts}
    }

@router.get("/trends")
async def get_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get SAR trends over time"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily SAR counts
    daily_counts = db.query(
        func.date(SAR.created_at).label('date'),
        func.count(SAR.id).label('count')
    ).filter(
        SAR.created_at >= start_date
    ).group_by(
        func.date(SAR.created_at)
    ).all()
    
    return {
        "period_days": days,
        "daily_counts": [
            {"date": str(date), "count": count}
            for date, count in daily_counts
        ]
    }
