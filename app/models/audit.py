from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    sar_id = Column(Integer, ForeignKey("sars.id", ondelete="SET NULL"))  # Allow SAR deletion
    action = Column(String, nullable=False)
    details = Column(Text)  # JSON string
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User")
    sar = relationship("SAR")
