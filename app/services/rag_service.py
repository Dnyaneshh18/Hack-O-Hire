from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import logging

from app.core.config import settings as app_settings

logger = logging.getLogger(__name__)

class RAGService:
    """Retrieval Augmented Generation service for SAR templates and guidelines"""
    
    def __init__(self):
        self.client = chromadb.Client(Settings(
            persist_directory=app_settings.CHROMA_PERSIST_DIRECTORY,
            anonymized_telemetry=False
        ))
        self.embedding_model = SentenceTransformer(app_settings.EMBEDDING_MODEL)
        self.collection_name = "sar_knowledge_base"
        self._initialize_collection()
    
    def _initialize_collection(self):
        """Initialize or get existing collection"""
        try:
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "SAR templates, guidelines, and regulatory requirements"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
            self._load_initial_knowledge()
    
    def _load_initial_knowledge(self):
        """Load initial SAR templates and guidelines"""
        
        knowledge_base = [
            {
                "id": "template_1",
                "content": """SAR Narrative Template - Structuring:
                
Subject Information: [Customer Name], [Customer ID], [Account Number]

Suspicious Activity: Between [start date] and [end date], the subject conducted [number] transactions totaling [amount] that appear designed to evade reporting requirements.

Transaction Pattern: The transactions were consistently structured in amounts just below the $10,000 reporting threshold, ranging from $[min] to $[max]. This pattern suggests deliberate structuring to avoid Currency Transaction Report (CTR) filing.

Why Suspicious: This activity is consistent with structuring under 31 USC 5324, where individuals break up large transactions to evade reporting requirements. The pattern, timing, and amounts indicate potential money laundering.

Supporting Facts: [Additional KYC inconsistencies, behavioral changes, or other red flags]""",
                "metadata": {"type": "template", "typology": "structuring"}
            },
            {
                "id": "template_2",
                "content": """SAR Narrative Template - Rapid Fund Movement:
                
Subject Information: [Customer Name], [Customer ID], [Account Number]

Suspicious Activity: The subject's account received [amount] from [number] different sources over [timeframe], followed by immediate outbound transfers to [destination].

Transaction Pattern: Funds were received in [number] deposits averaging [amount] each, then consolidated and transferred within [hours/days]. The rapid movement and lack of business purpose suggest layering activity.

Why Suspicious: This pattern is consistent with money laundering layering, where illicit funds are moved quickly through multiple accounts to obscure their origin. The velocity and complexity indicate potential criminal proceeds.

Supporting Facts: [Customer profile inconsistencies, unusual counterparties, geographic risk factors]""",
                "metadata": {"type": "template", "typology": "layering"}
            },
            {
                "id": "guideline_1",
                "content": """FinCEN SAR Narrative Guidelines:

1. Be Clear and Concise: Use plain language, avoid jargon
2. Be Specific: Include dates, amounts, account numbers
3. Be Objective: State facts, not opinions or speculation
4. Explain the Suspicious Nature: Link to known typologies
5. Include All Relevant Information: KYC data, transaction details, behavioral changes
6. Maintain Confidentiality: Protect customer information
7. Avoid Discrimination: Focus on behavior, not demographics""",
                "metadata": {"type": "guideline", "source": "FinCEN"}
            },
            {
                "id": "typology_1",
                "content": """Money Laundering Typology - Structuring:

Definition: Breaking up large transactions into smaller amounts to avoid reporting thresholds.

Red Flags:
- Multiple transactions just below $10,000
- Consistent patterns over time
- Use of multiple accounts or locations
- No apparent business purpose

Regulatory Reference: 31 USC 5324 - Structuring transactions to evade reporting""",
                "metadata": {"type": "typology", "category": "structuring"}
            },
            {
                "id": "typology_2",
                "content": """Money Laundering Typology - Funnel Account:

Definition: Account receives funds from multiple sources and quickly transfers to single destination.

Red Flags:
- High volume of incoming transfers from different sources
- Rapid outbound movement
- Minimal account balance retention
- Inconsistent with customer profile

Common in: Trade-based money laundering, fraud proceeds consolidation""",
                "metadata": {"type": "typology", "category": "funnel_account"}
            }
        ]
        
        # Add to collection
        for item in knowledge_base:
            embedding = self.embedding_model.encode(item["content"]).tolist()
            self.collection.add(
                ids=[item["id"]],
                embeddings=[embedding],
                documents=[item["content"]],
                metadatas=[item["metadata"]]
            )
        
        logger.info(f"Loaded {len(knowledge_base)} items into knowledge base")
    
    def get_relevant_context(self, query: str, n_results: int = 3) -> str:
        """Retrieve relevant context for SAR generation"""
        
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            if results and results["documents"]:
                context = "\n\n---\n\n".join(results["documents"][0])
                return context
            
            return "No specific templates found. Use general SAR guidelines."
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            return "Error retrieving templates. Use general SAR guidelines."
    
    def add_approved_sar(self, sar_id: str, narrative: str, metadata: Dict[str, Any]):
        """Add approved SAR to knowledge base for learning"""
        
        try:
            embedding = self.embedding_model.encode(narrative).tolist()
            self.collection.add(
                ids=[f"approved_sar_{sar_id}"],
                embeddings=[embedding],
                documents=[narrative],
                metadatas=[{**metadata, "type": "approved_sar"}]
            )
            logger.info(f"Added approved SAR {sar_id} to knowledge base")
        except Exception as e:
            logger.error(f"Error adding approved SAR: {str(e)}")
