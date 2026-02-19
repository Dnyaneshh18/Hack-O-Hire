from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base

class SARStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FILED = "filed"

class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SAR(Base):
    __tablename__ = "sars"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, index=True, nullable=False)
    customer_name = Column(String, nullable=False)
    
    # SAR Details
    narrative = Column(Text, nullable=False)
    risk_score = Column(Float)
    risk_level = Column(Enum(RiskLevel))
    typology = Column(String)  # Money laundering typology
    
    # Status
    status = Column(Enum(SARStatus), default=SARStatus.DRAFT)
    
    # Metadata
    created_by = Column(Integer, ForeignKey("users.id"))
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    filed_at = Column(DateTime(timezone=True))
    
    # Transaction data (stored as JSON)
    transaction_data = Column(JSON)
    kyc_data = Column(JSON)
    
    # Reasoning and audit
    reasoning_trace = Column(JSON)  # Complete LLM reasoning
    data_sources = Column(JSON)  # Sources used for generation
    
    # Comprehensive analysis fields (new)
    facts = Column(Text)  # Extracted facts
    red_flags = Column(Text)  # Detected red flags
    evidence_map = Column(Text)  # Evidence mapping
    quality_check = Column(Text)  # Quality assessment
    contradictions = Column(Text)  # Contradiction detection
    timeline = Column(Text)  # Event timeline
    typology_confidence = Column(Text)  # Typology confidence score
    regulatory_highlights = Column(Text)  # Key regulatory points
    executive_summary = Column(Text)  # Executive summary
    pii_check = Column(Text)  # PII leakage check
    reasoning_trace_detailed = Column(Text)  # Detailed reasoning
    next_actions = Column(Text)  # Suggested next actions
    improvements = Column(Text)  # Suggested improvements
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
