from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.sql import func

from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True, nullable=False)
    
    # Customer Information
    customer_id = Column(String, nullable=False, index=True)
    customer_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    
    # Alert Details
    alert_reason = Column(Text, nullable=False)
    alert_type = Column(String)  # e.g., "Structuring", "Layering", "Unusual Activity"
    priority = Column(String, default="medium")  # low, medium, high, critical
    
    # Transaction Data
    transaction_data = Column(JSON, nullable=False)
    
    # KYC Data
    kyc_data = Column(JSON)
    
    # Additional Customer Data
    customer_data = Column(JSON)
    
    # Status
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True))
    sar_id = Column(Integer)  # Link to generated SAR
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
