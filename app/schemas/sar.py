from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class SARGenerate(BaseModel):
    customer_data: Dict[str, Any]
    transaction_data: List[Dict[str, Any]]
    kyc_data: Dict[str, Any]
    alert_reason: str

class SARCreate(BaseModel):
    customer_id: str
    customer_name: str
    narrative: str
    transaction_data: Dict[str, Any]
    kyc_data: Dict[str, Any]

class SARUpdate(BaseModel):
    narrative: Optional[str] = None
    status: Optional[str] = None

class SARResponse(BaseModel):
    id: int
    case_id: str
    customer_id: str
    customer_name: str
    narrative: str
    risk_score: Optional[float]
    risk_level: Optional[str]
    typology: Optional[str]
    status: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime]
    reasoning_trace: Optional[Dict[str, Any]]
    
    # New comprehensive analysis fields
    facts: Optional[str] = None
    red_flags: Optional[str] = None
    evidence_map: Optional[str] = None
    quality_check: Optional[str] = None
    contradictions: Optional[str] = None
    timeline: Optional[str] = None
    typology_confidence: Optional[str] = None
    regulatory_highlights: Optional[str] = None
    executive_summary: Optional[str] = None
    pii_check: Optional[str] = None
    reasoning_trace_detailed: Optional[str] = None
    next_actions: Optional[str] = None
    improvements: Optional[str] = None
    
    class Config:
        from_attributes = True
