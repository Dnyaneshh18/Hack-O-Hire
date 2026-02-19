"""
Alert Priority Calculator Service
Automatically calculates alert priority based on multiple risk factors
"""

from typing import Dict, List, Any


class PriorityCalculator:
    """
    Calculates alert priority using a scoring system based on:
    - Transaction amounts
    - Transaction frequency
    - Alert type risk level
    - Customer risk profile
    - Red flag indicators
    """
    
    # Alert type risk weights
    ALERT_TYPE_SCORES = {
        "Structuring/Smurfing": 20,
        "Layering": 25,
        "PEP Activity": 22,
        "Shell Company": 23,
        "Trade-Based ML": 25,
        "Cryptocurrency": 18,
        "Suspicious Wires": 20,
        "Unusual Activity": 15,
        "New Account Activity": 17,
        "Check Cashing": 12,
        "Unknown": 10
    }
    
    @staticmethod
    def calculate_priority(
        transaction_data: List[Dict[str, Any]],
        alert_type: str,
        kyc_data: Dict[str, Any],
        alert_reason: str
    ) -> str:
        """
        Calculate priority based on multiple factors
        
        Returns: "low", "medium", "high", or "critical"
        """
        
        total_score = 0
        
        # 1. Transaction Amount Score (0-30 points)
        amount_score = PriorityCalculator._calculate_amount_score(transaction_data)
        total_score += amount_score
        
        # 2. Transaction Frequency Score (0-20 points)
        frequency_score = PriorityCalculator._calculate_frequency_score(transaction_data)
        total_score += frequency_score
        
        # 3. Alert Type Risk Score (0-25 points)
        type_score = PriorityCalculator.ALERT_TYPE_SCORES.get(alert_type, 10)
        total_score += type_score
        
        # 4. Customer Risk Profile Score (0-15 points)
        customer_score = PriorityCalculator._calculate_customer_risk_score(kyc_data)
        total_score += customer_score
        
        # 5. Red Flag Keywords Score (0-10 points)
        red_flag_score = PriorityCalculator._calculate_red_flag_score(alert_reason)
        total_score += red_flag_score
        
        # Convert score to priority level
        if total_score >= 75:
            return "critical"
        elif total_score >= 55:
            return "high"
        elif total_score >= 35:
            return "medium"
        else:
            return "low"
    
    @staticmethod
    def _calculate_amount_score(transaction_data: List[Dict[str, Any]]) -> int:
        """Calculate score based on transaction amounts"""
        if not transaction_data:
            return 0
        
        total_amount = sum(t.get("amount", 0) for t in transaction_data)
        max_amount = max((t.get("amount", 0) for t in transaction_data), default=0)
        
        # Score based on total amount
        if total_amount >= 500000:
            score = 30
        elif total_amount >= 250000:
            score = 25
        elif total_amount >= 100000:
            score = 20
        elif total_amount >= 50000:
            score = 15
        elif total_amount >= 25000:
            score = 10
        else:
            score = 5
        
        # Bonus for single large transaction
        if max_amount >= 250000:
            score += 5
        
        return min(score, 30)  # Cap at 30
    
    @staticmethod
    def _calculate_frequency_score(transaction_data: List[Dict[str, Any]]) -> int:
        """Calculate score based on transaction frequency"""
        if not transaction_data:
            return 0
        
        count = len(transaction_data)
        
        if count >= 10:
            return 20
        elif count >= 7:
            return 17
        elif count >= 5:
            return 14
        elif count >= 3:
            return 10
        else:
            return 5
    
    @staticmethod
    def _calculate_customer_risk_score(kyc_data: Dict[str, Any]) -> int:
        """Calculate score based on customer risk profile"""
        if not kyc_data:
            return 5
        
        score = 0
        
        # PEP status
        if kyc_data.get("is_pep"):
            score += 8
        
        # High-risk jurisdiction
        if kyc_data.get("high_risk_jurisdiction"):
            score += 5
        
        # New account (less than 6 months)
        account_age = kyc_data.get("account_age_months", 12)
        if account_age < 6:
            score += 4
        
        # Complex ownership structure
        if kyc_data.get("complex_ownership"):
            score += 3
        
        # Shell company indicators
        if kyc_data.get("employees", 1) == 0:
            score += 3
        
        # Virtual office
        if kyc_data.get("physical_location") == "Virtual Office":
            score += 2
        
        return min(score, 15)  # Cap at 15
    
    @staticmethod
    def _calculate_red_flag_score(alert_reason: str) -> int:
        """Calculate score based on red flag keywords in alert reason"""
        if not alert_reason:
            return 0
        
        alert_reason_lower = alert_reason.lower()
        
        red_flags = {
            "offshore": 3,
            "cayman": 3,
            "shell": 3,
            "layering": 3,
            "structuring": 3,
            "smurfing": 3,
            "immediate": 2,
            "rapid": 2,
            "suspicious": 2,
            "unusual": 2,
            "threshold": 2,
            "cash": 1,
            "wire": 1,
            "foreign": 1,
            "cryptocurrency": 2,
            "pep": 3,
            "politically exposed": 3,
        }
        
        score = 0
        for keyword, points in red_flags.items():
            if keyword in alert_reason_lower:
                score += points
        
        return min(score, 10)  # Cap at 10
    
    @staticmethod
    def get_priority_explanation(
        transaction_data: List[Dict[str, Any]],
        alert_type: str,
        kyc_data: Dict[str, Any],
        alert_reason: str
    ) -> Dict[str, Any]:
        """
        Get detailed explanation of priority calculation
        
        Returns breakdown of scores and final priority
        """
        
        amount_score = PriorityCalculator._calculate_amount_score(transaction_data)
        frequency_score = PriorityCalculator._calculate_frequency_score(transaction_data)
        type_score = PriorityCalculator.ALERT_TYPE_SCORES.get(alert_type, 10)
        customer_score = PriorityCalculator._calculate_customer_risk_score(kyc_data)
        red_flag_score = PriorityCalculator._calculate_red_flag_score(alert_reason)
        
        total_score = amount_score + frequency_score + type_score + customer_score + red_flag_score
        priority = PriorityCalculator.calculate_priority(transaction_data, alert_type, kyc_data, alert_reason)
        
        return {
            "priority": priority,
            "total_score": total_score,
            "breakdown": {
                "transaction_amount": {"score": amount_score, "max": 30},
                "transaction_frequency": {"score": frequency_score, "max": 20},
                "alert_type_risk": {"score": type_score, "max": 25},
                "customer_risk_profile": {"score": customer_score, "max": 15},
                "red_flag_indicators": {"score": red_flag_score, "max": 10}
            },
            "thresholds": {
                "critical": "75-100",
                "high": "55-74",
                "medium": "35-54",
                "low": "0-34"
            }
        }


# Example usage
if __name__ == "__main__":
    # Test case
    sample_transactions = [
        {"date": "2024-01-15", "amount": 9800},
        {"date": "2024-01-16", "amount": 9500},
        {"date": "2024-01-17", "amount": 9900},
    ]
    
    sample_kyc = {
        "occupation": "Restaurant Owner",
        "annual_income": "75000",
        "account_age_months": 8
    }
    
    priority = PriorityCalculator.calculate_priority(
        transaction_data=sample_transactions,
        alert_type="Structuring/Smurfing",
        kyc_data=sample_kyc,
        alert_reason="Multiple cash deposits just below $10,000 threshold"
    )
    
    explanation = PriorityCalculator.get_priority_explanation(
        transaction_data=sample_transactions,
        alert_type="Structuring/Smurfing",
        kyc_data=sample_kyc,
        alert_reason="Multiple cash deposits just below $10,000 threshold"
    )
    
    print(f"Priority: {priority}")
    print(f"Explanation: {explanation}")
