from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class AlertCreate(BaseModel):
    customer_id: str
    customer_name: str
    account_number: str
    alert_reason: str
    alert_type: Optional[str] = None
    priority: Optional[str] = "medium"
    transaction_data: List[Dict[str, Any]]
    kyc_data: Optional[Dict[str, Any]] = None
    customer_data: Optional[Dict[str, Any]] = None

class AlertUpdate(BaseModel):
    is_processed: Optional[bool] = None
    sar_id: Optional[int] = None

class AlertResponse(BaseModel):
    id: int
    alert_id: str
    customer_id: str
    customer_name: str
    account_number: str
    alert_reason: str
    alert_type: Optional[str]
    priority: str
    transaction_data: List[Dict[str, Any]]
    kyc_data: Optional[Dict[str, Any]]
    customer_data: Optional[Dict[str, Any]]
    is_processed: bool
    processed_at: Optional[datetime]
    sar_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True
