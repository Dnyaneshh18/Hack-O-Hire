from typing import Dict, Any, List, Tuple
import logging
from langchain_community.llms import Ollama
import json

from app.core.config import settings
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM-based SAR narrative generation with multi-stage analysis"""
    
    def __init__(self):
        self.llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
        self.rag_service = RAGService()
        
    def generate_sar_narrative(
        self,
        customer_data: Dict[str, Any],
        transaction_data: List[Dict[str, Any]],
        kyc_data: Dict[str, Any],
        alert_reason: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate SAR narrative with comprehensive analysis (OPTIMIZED - 3 LLM calls instead of 16)
        
        Returns:
            Tuple of (narrative, comprehensive_analysis)
        """
        try:
            logger.info("Starting OPTIMIZED SAR generation pipeline...")
            
            # Prepare case text
            case_text = self._prepare_case_text(customer_data, transaction_data, kyc_data, alert_reason)
            
            # Get regulatory context from RAG
            rules = self.rag_service.get_relevant_context(alert_reason)
            
            # OPTIMIZED STAGE 1: Combined Analysis (Facts + Red Flags + Typology + Timeline)
            logger.info("Stage 1: Running combined analysis...")
            combined_analysis = self._run_combined_analysis(case_text)
            
            # OPTIMIZED STAGE 2: Generate SAR with Quality Checks
            logger.info("Stage 2: Generating SAR narrative with quality checks...")
            sar_result = self._generate_sar_optimized(rules, combined_analysis, case_text)
            
            # OPTIMIZED STAGE 3: Post-Generation Analysis (Evidence + Actions + Improvements)
            logger.info("Stage 3: Running post-generation analysis...")
            post_analysis = self._run_post_analysis(sar_result["narrative"], combined_analysis)
            
            # Calculate risk score (fast, no LLM call)
            logger.info("Calculating risk score...")
            risk_analysis = self._assess_risk_factors(customer_data, transaction_data, kyc_data)
            
            # Compile comprehensive analysis
            comprehensive_analysis = {
                "facts": combined_analysis.get("facts", ""),
                "red_flags": combined_analysis.get("red_flags", ""),
                "typology": combined_analysis.get("typology", "unknown"),
                "typology_confidence": combined_analysis.get("confidence", ""),
                "timeline": combined_analysis.get("timeline", ""),
                "evidence_map": post_analysis.get("evidence_map", ""),
                "quality_check": sar_result.get("quality_check", ""),
                "contradictions": post_analysis.get("contradictions", ""),
                "regulatory_highlights": sar_result.get("regulatory_highlights", ""),
                "executive_summary": sar_result.get("executive_summary", ""),
                "pii_check": post_analysis.get("pii_check", ""),
                "reasoning_trace": combined_analysis.get("reasoning", ""),
                "next_actions": post_analysis.get("next_actions", ""),
                "improvements": post_analysis.get("improvements", ""),
                "risk_analysis": risk_analysis,
                "llm_model": settings.LLM_MODEL,
                "temperature": settings.LLM_TEMPERATURE
            }
            
            logger.info("SAR generation completed successfully (3 LLM calls)")
            return sar_result["narrative"], comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Error in SAR generation pipeline: {str(e)}")
            raise
    
    def _prepare_case_text(
        self,
        customer_data: Dict[str, Any],
        transaction_data: List[Dict[str, Any]],
        kyc_data: Dict[str, Any],
        alert_reason: str
    ) -> str:
        """Prepare comprehensive case text for analysis"""
        return f"""
CUSTOMER INFORMATION:
{json.dumps(customer_data, indent=2)}

KYC DATA:
{json.dumps(kyc_data, indent=2)}

TRANSACTION DATA:
{json.dumps(transaction_data, indent=2)}

ALERT REASON:
{alert_reason}
"""
    
    # ===================== OPTIMIZED STAGE 1: COMBINED ANALYSIS =====================
    def _run_combined_analysis(self, case_text: str) -> Dict[str, str]:
        """Run combined analysis in ONE LLM call (Facts + Red Flags + Typology + Timeline)"""
        prompt = f"""You are a senior AML compliance analyst at Barclays Bank with 15+ years of experience in financial crime detection. Analyze this suspicious activity case with precision and regulatory expertise.

CRITICAL INSTRUCTIONS:
- Be SPECIFIC with numbers, dates, and amounts (use exact figures)
- Focus on OBJECTIVE facts only (no speculation or assumptions)
- Identify CONCRETE red flags based on FinCEN guidelines
- Use PROFESSIONAL regulatory language
- Be THOROUGH but CONCISE
- DO NOT use asterisks (*) for emphasis or formatting - use plain text only
- DO NOT use markdown formatting - write in plain professional text

ANALYSIS REQUIRED:

1. FACTS - Extract objective, verifiable facts:
   • Customer identification (name, ID, account)
   • Transaction specifics (exact dates, amounts, counterparties)
   • Behavioral patterns (frequency, timing, amounts)
   • Geographic factors (locations, jurisdictions)

2. RED FLAGS - Identify suspicious indicators:
   • Structuring patterns (transactions near $10,000 threshold)
   • Rapid fund movement (velocity and timing)
   • Unusual patterns (inconsistent with customer profile)
   • High-risk jurisdictions or counterparties
   • Lack of economic purpose

3. TYPOLOGY - Classify money laundering pattern:
   Common typologies: Structuring, Layering, Trade-Based ML, Funnel Account, Smurfing
   • Name the typology
   • Explain WHY this pattern matches
   • Reference specific transactions as evidence

4. CONFIDENCE - Rate your confidence (0-100%):
   • Provide percentage
   • Explain reasoning (what evidence supports this?)
   • Note any uncertainties or gaps

5. TIMELINE - Create chronological sequence:
   • List events in date order
   • Show progression of suspicious activity
   • Highlight key moments

6. REASONING - Step-by-step logic:
   • How did you identify the pattern?
   • What facts led to the typology conclusion?
   • Why is this suspicious (not just unusual)?

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

=== FACTS ===
• [Specific, numbered facts with exact amounts and dates]

=== RED FLAGS ===
• [Concrete suspicious indicators with regulatory basis]

=== TYPOLOGY ===
[Typology Name]: [Detailed explanation with transaction references]

=== CONFIDENCE ===
[XX%]: [Reasoning based on evidence strength]

=== TIMELINE ===
[Date-ordered sequence of events]

=== REASONING ===
[Step-by-step analytical process]

Case Details:
{case_text}"""
        
        response = self.llm.invoke(prompt)
        
        # Parse the response
        sections = {
            "facts": self._extract_section(response, "FACTS"),
            "red_flags": self._extract_section(response, "RED FLAGS"),
            "typology": self._extract_section(response, "TYPOLOGY"),
            "confidence": self._extract_section(response, "CONFIDENCE"),
            "timeline": self._extract_section(response, "TIMELINE"),
            "reasoning": self._extract_section(response, "REASONING")
        }
        
        return sections
    
    # ===================== OPTIMIZED STAGE 2: SAR GENERATION =====================
    def _generate_sar_optimized(self, rules: str, analysis: Dict[str, str], case_text: str) -> Dict[str, str]:
        """Generate SAR with quality checks and summaries in ONE LLM call"""
        prompt = f"""You are a senior compliance officer at Barclays Bank with expertise in SAR narrative writing. Your narratives are consistently approved by FinCEN and praised for clarity and completeness.

CRITICAL FORMATTING RULES:
- DO NOT use asterisks (*) anywhere in your response
- DO NOT use markdown formatting (no **, *, _, etc.)
- Write in plain professional text only
- Use bullet points with • or - symbols only
- Use checkmarks ✅ and ❌ for quality checks only

REGULATORY GUIDELINES TO FOLLOW:
{rules}

CASE ANALYSIS PROVIDED:
Facts: {analysis.get('facts', '')}
Red Flags: {analysis.get('red_flags', '')}
Typology: {analysis.get('typology', '')}

CASE DETAILS:
{case_text}

YOUR TASK: Generate a complete, regulator-ready SAR package

REQUIREMENTS FOR SAR NARRATIVE:
1. STRUCTURE: Follow FinCEN SAR narrative format
   • Subject Information (who)
   • Suspicious Activity Description (what happened)
   • Transaction Pattern Analysis (amounts, timing, frequency)
   • Why This Is Suspicious (link to ML typologies)
   • Supporting Evidence (KYC inconsistencies, behavioral changes)

2. LANGUAGE: Professional, objective, fact-based
   • Use specific amounts and dates
   • Avoid speculation or assumptions
   • Use regulatory terminology correctly
   • Be clear and concise (1000-2000 characters)
   • NO asterisks or markdown formatting

3. CONTENT: Must include
   • Customer identification
   • Transaction specifics (dates, amounts, counterparties)
   • Suspicious pattern explanation
   • Typology classification
   • Why it warrants SAR filing

4. COMPLIANCE: Ensure
   • No discrimination or bias
   • Focus on behavior, not demographics
   • Objective tone throughout
   • Evidence-backed statements only

DELIVERABLES:

1. SAR NARRATIVE - Complete, professional narrative (1000-2000 chars) in plain text
2. QUALITY CHECK - Validate against checklist:
   ✅ Clear customer description
   ✅ Logical narrative flow
   ✅ All statements evidence-backed
   ✅ Proper FinCEN structure
   ✅ Professional regulatory language
   ✅ No speculation or bias
   ✅ Specific dates and amounts included

3. REGULATORY HIGHLIGHTS - Key points for examiner review:
   • Most critical red flags
   • Strongest evidence of suspicious activity
   • Typology classification justification

4. EXECUTIVE SUMMARY - 5-line summary for senior management:
   • Who (customer)
   • What (activity)
   • Why suspicious (pattern)
   • Risk level
   • Recommended action

FORMAT EXACTLY LIKE THIS:

=== SAR NARRATIVE ===
[Complete professional narrative in plain text, 1000-2000 characters, NO asterisks]

=== QUALITY CHECK ===
✅/❌ [Checklist items]

=== REGULATORY HIGHLIGHTS ===
• [Key points]

=== EXECUTIVE SUMMARY ===
[5-line summary]"""
        
        response = self.llm.invoke(prompt)
        
        return {
            "narrative": self._extract_section(response, "SAR NARRATIVE"),
            "quality_check": self._extract_section(response, "QUALITY CHECK"),
            "regulatory_highlights": self._extract_section(response, "REGULATORY HIGHLIGHTS"),
            "executive_summary": self._extract_section(response, "EXECUTIVE SUMMARY")
        }
    
    # ===================== OPTIMIZED STAGE 3: POST-ANALYSIS =====================
    def _run_post_analysis(self, narrative: str, analysis: Dict[str, str]) -> Dict[str, str]:
        """Run post-generation analysis in ONE LLM call"""
        prompt = f"""Review this SAR and provide:

CRITICAL: DO NOT use asterisks (*) or markdown formatting in your response. Use plain professional text only.

1. EVIDENCE MAP: Map key narrative sentences to supporting facts
2. CONTRADICTIONS: Check for inconsistencies (or say "No contradictions found")
3. PII CHECK: Verify no unnecessary personal information exposed
4. NEXT ACTIONS: Suggest 3-5 follow-up actions (monitoring, investigation, etc.)
5. IMPROVEMENTS: Suggest 2-3 ways to improve the narrative

SAR NARRATIVE:
{narrative}

FACTS:
{analysis.get('facts', '')}

Format EXACTLY like this (NO asterisks):

=== EVIDENCE MAP ===
[Sentence → Fact mappings]

=== CONTRADICTIONS ===
[List or "No contradictions found"]

=== PII CHECK ===
[Assessment and suggestions]

=== NEXT ACTIONS ===
• [Action items]

=== IMPROVEMENTS ===
• [Suggestions]"""
        
        response = self.llm.invoke(prompt)
        
        return {
            "evidence_map": self._extract_section(response, "EVIDENCE MAP"),
            "contradictions": self._extract_section(response, "CONTRADICTIONS"),
            "pii_check": self._extract_section(response, "PII CHECK"),
            "next_actions": self._extract_section(response, "NEXT ACTIONS"),
            "improvements": self._extract_section(response, "IMPROVEMENTS")
        }
    
    def _extract_section(self, text: str, section_name: str) -> str:
        """Extract a section from formatted response"""
        try:
            marker = f"=== {section_name} ==="
            if marker in text:
                start = text.index(marker) + len(marker)
                # Find next section or end
                next_marker = text.find("===", start)
                if next_marker != -1:
                    return text[start:next_marker].strip()
                return text[start:].strip()
            return ""
        except:
            return ""
    
    # ===================== LEGACY METHODS (kept for compatibility) =====================
    def _extract_facts(self, case_text: str) -> str:
        """Extract objective, verifiable facts from case details"""
        prompt = f"""You are a banking AML analyst.
From the case details below, extract only objective, verifiable facts.

Extract:
- Customer name
- Total amount involved
- Number of accounts involved
- Source of funds
- Destination of funds
- Time pattern
- Geographic pattern
- Transaction behavior

Return the facts in clear bullet points.

Case Details:
{case_text}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 2: RED FLAG DETECTOR =====================
    def _detect_red_flags(self, case_text: str) -> str:
        """Identify immediate suspicious indicators"""
        prompt = f"""You are an AML red flag detection engine.
Identify immediate suspicious indicators from the case.

Look for:
- Multiple accounts
- Cash deposits
- Foreign transfers
- Rapid movement of funds
- Structuring patterns
- Dormant account activity

Return only a bullet list of red flags.

Case Details:
{case_text}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 3: TYPOLOGY DETECTOR =====================
    def _identify_typology(self, facts: str) -> str:
        """Determine money laundering typology"""
        prompt = f"""You are an AML typology expert.
Based on these facts, determine which money laundering typology is present.

Possible typologies:
- Structuring
- Layering
- Mule account
- Overseas transfer
- Shell account
- Rapid fund movement

Explain the typology and why it matches.

Facts:
{facts}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 4: SAR GENERATOR =====================
    def _generate_sar(self, rules: str, typology: str, facts: str) -> str:
        """Generate professional SAR narrative"""
        prompt = f"""You are a senior banking compliance officer.
Follow these SAR writing rules strictly:
{rules}

Case Typology:
{typology}

Use these extracted facts as evidence:
{facts}

Write a professional, regulator-ready SAR narrative.
The SAR must clearly explain why the activity is suspicious and reference the facts."""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 5: EVIDENCE MAPPER =====================
    def _map_evidence(self, sar_text: str, facts: str) -> str:
        """Map each SAR sentence to supporting facts"""
        prompt = f"""Map each sentence of the SAR narrative to the exact fact it came from.

For every sentence in the SAR, show:
Sentence → Supporting Fact

SAR:
{sar_text}

Facts:
{facts}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 6: QUALITY CHECKER =====================
    def _check_quality(self, sar_text: str) -> str:
        """Check if SAR meets regulatory standards"""
        prompt = f"""You are a SAR quality reviewer.
Check if this SAR meets regulatory standards:

Checklist:
- Clear customer description
- Logical flow
- Evidence-backed statements
- Proper SAR structure
- Professional AML language

Return a checklist with ✅ or ❌ and explanations.

SAR:
{sar_text}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 7: RISK SCORER =====================
    def _score_risk(
        self,
        facts: str,
        transaction_data: List[Dict[str, Any]],
        customer_data: Dict[str, Any],
        kyc_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk score"""
        # Use existing risk assessment logic
        risk_factors = self._assess_risk_factors(customer_data, transaction_data, kyc_data)
        
        # Add AI explanation
        prompt = f"""You are an AML risk scoring engine.
Based on these facts, assign a suspicion score from 0 to 100.
Explain why the score is high or low.

Facts:
{facts}"""
        
        ai_explanation = self.llm.invoke(prompt)
        
        return {
            **risk_factors,
            "ai_explanation": ai_explanation
        }
    
    # ===================== STAGE 8: CONTRADICTION DETECTOR =====================
    def _detect_contradictions(self, sar_text: str, facts: str) -> str:
        """Detect contradictions between SAR and facts"""
        prompt = f"""Compare the SAR narrative with the extracted facts.

Identify:
- Any mismatched numbers
- Dates/timelines that don't match
- Claims in SAR not supported by facts
- Logical contradictions

Return a bullet list or say 'No contradictions found'.

SAR:
{sar_text}

Facts:
{facts}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 9: TIMELINE BUILDER =====================
    def _build_timeline(self, facts: str) -> str:
        """Create chronological timeline of events"""
        prompt = f"""Create a clear chronological timeline of events from the facts.

Show sequence of:
- Deposits
- Transfers
- Geographic movement
- Behavior change

Facts:
{facts}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 10: TYPOLOGY CONFIDENCE =====================
    def _assess_typology_confidence(self, typology: str, facts: str) -> str:
        """Assign confidence percentage to typology"""
        prompt = f"""Given the detected typology and facts, assign a confidence percentage (0-100%).
Explain which facts support this typology.

Typology:
{typology}

Facts:
{facts}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 11: REGULATORY RISK HIGHLIGHT =====================
    def _highlight_regulatory_risks(self, sar_text: str) -> str:
        """Highlight critical sentences for regulatory review"""
        prompt = f"""Highlight the sentences in the SAR that are most critical for regulatory review.
Explain why each is important.

SAR:
{sar_text}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 12: SAR SIMPLIFIER =====================
    def _simplify_sar(self, sar_text: str) -> str:
        """Create executive summary"""
        prompt = f"""Summarize this SAR in 5 simple lines for a non-technical manager.

SAR:
{sar_text}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 13: PII LEAKAGE CHECK =====================
    def _check_pii(self, sar_text: str) -> str:
        """Check for unnecessary PII exposure"""
        prompt = f"""Check if this SAR exposes unnecessary personal information.
Suggest any redactions needed.

SAR:
{sar_text}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 14: REASONING TRACE =====================
    def _build_reasoning_trace(self, typology: str, facts: str) -> str:
        """Explain step-by-step reasoning"""
        prompt = f"""Explain step-by-step why this typology was chosen from the facts.

Typology:
{typology}

Facts:
{facts}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 15: NEXT BEST ACTION =====================
    def _suggest_next_actions(self, sar_text: str) -> str:
        """Suggest next best actions"""
        prompt = f"""Based on this SAR and facts, suggest next best actions.

Examples:
- Enhanced monitoring
- Account freeze
- Further investigation
- Report to authorities

SAR:
{sar_text}"""
        
        return self.llm.invoke(prompt)
    
    # ===================== STAGE 16: SAR REVIEWER =====================
    def _suggest_improvements(self, sar_text: str, facts: str) -> str:
        """Suggest improvements to SAR"""
        prompt = f"""You are a senior SAR reviewer.
Suggest improvements to make this SAR clearer, more professional, and regulator-ready.

SAR:
{sar_text}

Facts:
{facts}"""
        
        return self.llm.invoke(prompt)
    
    def _build_prompt(
        self,
        customer_data: Dict[str, Any],
        transaction_data: List[Dict[str, Any]],
        kyc_data: Dict[str, Any],
        alert_reason: str,
        context: str
    ) -> str:
        """Build comprehensive prompt for SAR generation (legacy method, kept for compatibility)"""
        
        template = """You are an expert financial crime compliance analyst at Barclays Bank tasked with writing a Suspicious Activity Report (SAR) narrative.

CRITICAL INSTRUCTIONS:
- Be objective and fact-based. Do NOT discriminate based on race, religion, nationality, or any protected characteristic.
- Focus ONLY on transaction patterns, amounts, timing, and behavioral anomalies.
- Use clear, professional language suitable for regulatory review.
- Follow FinCEN SAR narrative guidelines.
- Explain WHY the activity is suspicious based on financial crime typologies.

REGULATORY CONTEXT AND TEMPLATES:
{context}

CUSTOMER INFORMATION:
{customer_info}

KYC DATA:
{kyc_info}

TRANSACTION DATA:
{transaction_info}

ALERT REASON:
{alert_reason}

TASK:
Write a comprehensive SAR narrative that includes:
1. Subject Information (customer details)
2. Suspicious Activity Description (what happened)
3. Transaction Pattern Analysis (amounts, timing, frequency)
4. Why This Is Suspicious (link to money laundering typologies)
5. Supporting Facts (KYC inconsistencies, behavioral changes)

Write the narrative now:"""

        return template.format(
            context=context,
            customer_info=json.dumps(customer_data, indent=2),
            kyc_info=json.dumps(kyc_data, indent=2),
            transaction_info=json.dumps(transaction_data, indent=2),
            alert_reason=alert_reason
        )
    
    def _extract_reasoning(
        self,
        customer_data: Dict[str, Any],
        transaction_data: List[Dict[str, Any]],
        kyc_data: Dict[str, Any],
        alert_reason: str,
        response: str
    ) -> Dict[str, Any]:
        """Extract reasoning trace for audit trail (legacy method)"""
        
        # Calculate transaction statistics
        total_amount = sum(t.get("amount", 0) for t in transaction_data)
        transaction_count = len(transaction_data)
        unique_counterparties = len(set(t.get("counterparty", "") for t in transaction_data))
        
        return {
            "input_summary": {
                "customer_id": customer_data.get("customer_id"),
                "customer_name": customer_data.get("name"),
                "alert_reason": alert_reason,
                "transaction_count": transaction_count,
                "total_amount": total_amount,
                "unique_counterparties": unique_counterparties
            },
            "data_sources": {
                "customer_data": list(customer_data.keys()),
                "kyc_data": list(kyc_data.keys()),
                "transaction_fields": list(transaction_data[0].keys()) if transaction_data else []
            },
            "key_indicators": self._identify_key_indicators(transaction_data, kyc_data),
            "typology_match": self._match_typology(alert_reason, transaction_data),
            "risk_factors": self._assess_risk_factors(customer_data, transaction_data, kyc_data),
            "llm_model": settings.LLM_MODEL,
            "temperature": settings.LLM_TEMPERATURE
        }
    
    def _identify_key_indicators(
        self,
        transaction_data: List[Dict[str, Any]],
        kyc_data: Dict[str, Any]
    ) -> List[str]:
        """Identify key suspicious indicators"""
        indicators = []
        
        if len(transaction_data) > 20:
            indicators.append("High transaction volume")
        
        amounts = [t.get("amount", 0) for t in transaction_data]
        if amounts and max(amounts) > 50000:
            indicators.append("Large transaction amounts")
        
        # Check for structuring (amounts just below reporting threshold)
        structuring_count = sum(1 for amt in amounts if 9000 <= amt <= 10000)
        if structuring_count >= 3:
            indicators.append("Possible structuring pattern")
        
        # Check for rapid movement
        if len(transaction_data) > 10:
            time_span = "short"  # Simplified
            if time_span == "short":
                indicators.append("Rapid fund movement")
        
        return indicators
    
    def _match_typology(
        self,
        alert_reason: str,
        transaction_data: List[Dict[str, Any]]
    ) -> str:
        """Match to money laundering typology"""
        
        typologies = {
            "structuring": ["multiple", "below threshold", "structured"],
            "layering": ["rapid", "multiple transfers", "complex"],
            "trade_based": ["trade", "import", "export"],
            "cash_intensive": ["cash", "deposit"],
            "funnel_account": ["multiple sources", "single destination"]
        }
        
        alert_lower = alert_reason.lower()
        for typology, keywords in typologies.items():
            if any(kw in alert_lower for kw in keywords):
                return typology
        
        return "unknown"
    
    def _assess_risk_factors(
        self,
        customer_data: Dict[str, Any],
        transaction_data: List[Dict[str, Any]],
        kyc_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess risk factors for scoring"""
        
        risk_score = 0
        factors = []
        
        # Get transaction amounts
        amounts = [t.get("amount", 0) for t in transaction_data]
        total_amount = sum(amounts)
        transaction_count = len(transaction_data)
        
        # 1. Transaction volume risk (0-25 points)
        if transaction_count > 50:
            risk_score += 25
            factors.append("Very high transaction volume (50+ transactions)")
        elif transaction_count > 20:
            risk_score += 20
            factors.append("High transaction volume (20+ transactions)")
        elif transaction_count > 10:
            risk_score += 15
            factors.append("Elevated transaction volume (10+ transactions)")
        elif transaction_count >= 5:
            risk_score += 10
            factors.append("Multiple transactions detected")
        
        # 2. Total amount risk (0-30 points)
        if total_amount > 1000000:
            risk_score += 30
            factors.append(f"Very large total amount (${total_amount:,.0f})")
        elif total_amount > 500000:
            risk_score += 25
            factors.append(f"Large total amount (${total_amount:,.0f})")
        elif total_amount > 100000:
            risk_score += 20
            factors.append(f"Significant total amount (${total_amount:,.0f})")
        elif total_amount > 50000:
            risk_score += 15
            factors.append(f"Notable total amount (${total_amount:,.0f})")
        elif total_amount > 25000:
            risk_score += 10
            factors.append(f"Moderate total amount (${total_amount:,.0f})")
        
        # 3. Structuring pattern detection (0-30 points)
        structuring_count = sum(1 for amt in amounts if 9000 <= amt <= 10000)
        if structuring_count >= 5:
            risk_score += 30
            factors.append(f"Strong structuring pattern ({structuring_count} transactions near $10K threshold)")
        elif structuring_count >= 3:
            risk_score += 25
            factors.append(f"Likely structuring pattern ({structuring_count} transactions near $10K threshold)")
        elif structuring_count >= 2:
            risk_score += 15
            factors.append(f"Possible structuring pattern ({structuring_count} transactions near $10K threshold)")
        
        # 4. Individual transaction size risk (0-15 points)
        if amounts:
            max_amount = max(amounts)
            if max_amount > 100000:
                risk_score += 15
                factors.append(f"Very large individual transaction (${max_amount:,.0f})")
            elif max_amount > 50000:
                risk_score += 10
                factors.append(f"Large individual transaction (${max_amount:,.0f})")
            elif max_amount > 25000:
                risk_score += 5
                factors.append(f"Significant individual transaction (${max_amount:,.0f})")
        
        # 5. Velocity risk (0-10 points)
        if transaction_count > 10:
            risk_score += 10
            factors.append("High transaction velocity")
        elif transaction_count >= 5:
            risk_score += 5
            factors.append("Elevated transaction velocity")
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "factors": factors
        }
