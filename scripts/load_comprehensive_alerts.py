import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

# Comprehensive sample alerts data (15 alerts covering various typologies)
sample_alerts = [
    # Alert 1: Structuring
    {
        "customer_id": "CUS-445678",
        "customer_name": "Michael Rodriguez",
        "account_number": "ACC-2024-8891",
        "alert_type": "Structuring",
        "priority": "high",
        "alert_reason": "Multiple cash deposits just below $10,000 reporting threshold over 5 days, followed by large international wire transfer. Total deposits: $76,100. Pattern suggests structuring to avoid CTR filing.",
        "transaction_data": [
            {"date": "2024-02-01", "amount": 9500, "counterparty": "Self", "description": "Cash deposit at ATM"},
            {"date": "2024-02-01", "amount": 9800, "counterparty": "Self", "description": "Cash deposit at branch"},
            {"date": "2024-02-02", "amount": 9700, "counterparty": "Self", "description": "Cash deposit at ATM"},
            {"date": "2024-02-02", "amount": 9900, "counterparty": "Self", "description": "Cash deposit at branch"},
            {"date": "2024-02-03", "amount": 9600, "counterparty": "Self", "description": "Cash deposit at ATM"},
            {"date": "2024-02-03", "amount": 9850, "counterparty": "Self", "description": "Cash deposit at branch"},
            {"date": "2024-02-04", "amount": 9750, "counterparty": "Self", "description": "Cash deposit at ATM"},
            {"date": "2024-02-05", "amount": 58000, "counterparty": "Overseas Bank Ltd", "description": "International wire to Cayman Islands"}
        ],
        "kyc_data": {"occupation": "Restaurant Manager", "annual_income": "$45,000", "expected_activity": "$3,000-$5,000", "risk_rating": "Medium"},
        "customer_data": {"date_of_birth": "1985-03-15", "address": "456 Oak St, New York, NY", "phone": "+1-555-0123"}
    },
    
    # Alert 2: Layering
    {
        "customer_id": "CUS-889012",
        "customer_name": "Jennifer Chen",
        "account_number": "ACC-2024-7723",
        "alert_type": "Layering",
        "priority": "critical",
        "alert_reason": "Rapid movement of $85,000 received from multiple sources, then immediately transferred to three offshore accounts in high-risk jurisdictions within 48 hours.",
        "transaction_data": [
            {"date": "2024-02-05", "amount": 50000, "counterparty": "ABC Trading LLC", "description": "Wire transfer received"},
            {"date": "2024-02-05", "amount": 15000, "counterparty": "XYZ Imports Inc", "description": "Wire transfer received"},
            {"date": "2024-02-05", "amount": 20000, "counterparty": "Global Services", "description": "Wire transfer received"},
            {"date": "2024-02-06", "amount": 25000, "counterparty": "Swiss Account", "description": "International wire to Switzerland"},
            {"date": "2024-02-06", "amount": 30000, "counterparty": "Singapore Account", "description": "International wire to Singapore"},
            {"date": "2024-02-07", "amount": 30000, "counterparty": "UAE Account", "description": "International wire to UAE"}
        ],
        "kyc_data": {"occupation": "Freelance Consultant", "annual_income": "$60,000", "expected_activity": "$5,000-$8,000", "risk_rating": "Low"},
        "customer_data": {"date_of_birth": "1990-07-22", "address": "789 Pine Ave, Los Angeles, CA", "phone": "+1-555-0456"}
    },

    # Alert 3: Funnel Account
    {
        "customer_id": "CUS-223344",
        "customer_name": "David Thompson",
        "account_number": "ACC-2024-5544",
        "alert_type": "Funnel Account",
        "priority": "critical",
        "alert_reason": "Account received $55,000 from 8 different individuals via P2P transfers over 3 days, then entire amount wired internationally. Income inconsistent with volume.",
        "transaction_data": [
            {"date": "2024-02-08", "amount": 5000, "counterparty": "John Doe", "description": "P2P transfer"},
            {"date": "2024-02-08", "amount": 7500, "counterparty": "Jane Smith", "description": "P2P transfer"},
            {"date": "2024-02-08", "amount": 6200, "counterparty": "Bob Wilson", "description": "P2P transfer"},
            {"date": "2024-02-08", "amount": 8300, "counterparty": "Alice Brown", "description": "P2P transfer"},
            {"date": "2024-02-09", "amount": 4800, "counterparty": "Charlie Davis", "description": "P2P transfer"},
            {"date": "2024-02-09", "amount": 9100, "counterparty": "Emma Johnson", "description": "P2P transfer"},
            {"date": "2024-02-09", "amount": 6700, "counterparty": "Frank Miller", "description": "P2P transfer"},
            {"date": "2024-02-09", "amount": 7400, "counterparty": "Grace Lee", "description": "P2P transfer"},
            {"date": "2024-02-10", "amount": 55000, "counterparty": "Foreign Exchange", "description": "International wire to Hong Kong"}
        ],
        "kyc_data": {"occupation": "Retail Clerk", "annual_income": "$35,000", "expected_activity": "$2,000-$3,000", "risk_rating": "Low"},
        "customer_data": {"date_of_birth": "1978-11-30", "address": "321 Maple Dr, Chicago, IL", "phone": "+1-555-0789"}
    },
    
    # Alert 4: Trade-Based Money Laundering
    {
        "customer_id": "CUS-667788",
        "customer_name": "Sarah Martinez",
        "account_number": "ACC-2024-9988",
        "alert_type": "Trade-Based ML",
        "priority": "high",
        "alert_reason": "High-volume international trade transactions ($1.12M in 6 days) with rapid turnover. Invoices show overvalued goods (electronics 300% above market rate).",
        "transaction_data": [
            {"date": "2024-02-10", "amount": 150000, "counterparty": "Import Co Ltd", "description": "Wire received - Invoice INV-001"},
            {"date": "2024-02-11", "amount": 180000, "counterparty": "Export Trading", "description": "Wire sent - Payment for goods"},
            {"date": "2024-02-12", "amount": 200000, "counterparty": "Global Traders", "description": "Wire received - Invoice INV-002"},
            {"date": "2024-02-13", "amount": 220000, "counterparty": "Overseas Supplier", "description": "Wire sent - Payment for goods"},
            {"date": "2024-02-14", "amount": 175000, "counterparty": "Intl Trade Co", "description": "Wire received - Invoice INV-003"},
            {"date": "2024-02-15", "amount": 195000, "counterparty": "Foreign Vendor", "description": "Wire sent - Payment for goods"}
        ],
        "kyc_data": {"occupation": "Import/Export Business", "annual_income": "$120,000", "expected_activity": "$50,000-$80,000", "risk_rating": "Medium"},
        "customer_data": {"date_of_birth": "1982-05-18", "address": "555 Elm St, Miami, FL", "phone": "+1-555-0321"}
    },

    # Alert 5: Smurfing
    {
        "customer_id": "CUS-112233",
        "customer_name": "Robert Kim",
        "account_number": "ACC-2024-3366",
        "alert_type": "Smurfing",
        "priority": "medium",
        "alert_reason": "Multiple small cash deposits ($30,000 total) over 4 days from various ATM locations, followed by single large wire to cryptocurrency exchange.",
        "transaction_data": [
            {"date": "2024-02-15", "amount": 3000, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-15", "amount": 2500, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-15", "amount": 4000, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-16", "amount": 3500, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-16", "amount": 2800, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-16", "amount": 4200, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-17", "amount": 3300, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-17", "amount": 2900, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-17", "amount": 3800, "counterparty": "ATM Deposit", "description": "Cash deposit"},
            {"date": "2024-02-18", "amount": 30000, "counterparty": "Crypto Exchange", "description": "Wire transfer"}
        ],
        "kyc_data": {"occupation": "Student", "annual_income": "$15,000", "expected_activity": "$1,000-$2,000", "risk_rating": "Low"},
        "customer_data": {"date_of_birth": "1995-09-08", "address": "888 Cedar Ln, Seattle, WA", "phone": "+1-555-0654"}
    },
    
    # Alert 6: Round Dollar Transactions
    {
        "customer_id": "CUS-334455",
        "customer_name": "Patricia Williams",
        "account_number": "ACC-2024-6677",
        "alert_type": "Round Dollar",
        "priority": "medium",
        "alert_reason": "Unusual pattern of round dollar wire transfers ($50K, $75K, $100K) to multiple offshore entities. No business documentation provided.",
        "transaction_data": [
            {"date": "2024-02-12", "amount": 50000, "counterparty": "Offshore Corp A", "description": "Wire transfer"},
            {"date": "2024-02-13", "amount": 75000, "counterparty": "Offshore Corp B", "description": "Wire transfer"},
            {"date": "2024-02-14", "amount": 100000, "counterparty": "Offshore Corp C", "description": "Wire transfer"},
            {"date": "2024-02-15", "amount": 50000, "counterparty": "Offshore Corp D", "description": "Wire transfer"}
        ],
        "kyc_data": {"occupation": "Real Estate Agent", "annual_income": "$85,000", "expected_activity": "$10,000-$20,000", "risk_rating": "Medium"},
        "customer_data": {"date_of_birth": "1988-12-03", "address": "234 Birch Ave, Boston, MA", "phone": "+1-555-0987"}
    },
    
    # Alert 7: Rapid Account Turnover
    {
        "customer_id": "CUS-556677",
        "customer_name": "James Anderson",
        "account_number": "ACC-2024-8899",
        "alert_type": "Rapid Turnover",
        "priority": "high",
        "alert_reason": "Account opened 2 weeks ago. $250K deposited and withdrawn within 5 days. No legitimate business purpose identified.",
        "transaction_data": [
            {"date": "2024-02-10", "amount": 250000, "counterparty": "Unknown Source", "description": "Wire received"},
            {"date": "2024-02-11", "amount": 80000, "counterparty": "Entity A", "description": "Wire sent"},
            {"date": "2024-02-12", "amount": 85000, "counterparty": "Entity B", "description": "Wire sent"},
            {"date": "2024-02-13", "amount": 85000, "counterparty": "Entity C", "description": "Wire sent"}
        ],
        "kyc_data": {"occupation": "Consultant", "annual_income": "$70,000", "expected_activity": "$5,000-$10,000", "risk_rating": "Low"},
        "customer_data": {"date_of_birth": "1992-04-25", "address": "567 Willow St, Denver, CO", "phone": "+1-555-0234"}
    },

    # Alert 8: Shell Company Activity
    {
        "customer_id": "CUS-778899",
        "customer_name": "Global Ventures LLC",
        "account_number": "ACC-2024-1122",
        "alert_type": "Shell Company",
        "priority": "critical",
        "alert_reason": "Newly formed LLC with no employees. $500K in transactions within first month. Multiple international wires to high-risk jurisdictions.",
        "transaction_data": [
            {"date": "2024-02-01", "amount": 150000, "counterparty": "Unknown Entity", "description": "Wire received"},
            {"date": "2024-02-05", "amount": 120000, "counterparty": "Panama Corp", "description": "Wire sent"},
            {"date": "2024-02-10", "amount": 180000, "counterparty": "Unknown Entity", "description": "Wire received"},
            {"date": "2024-02-15", "amount": 150000, "counterparty": "BVI Company", "description": "Wire sent"}
        ],
        "kyc_data": {"occupation": "Business Entity", "annual_income": "N/A", "expected_activity": "Unknown", "risk_rating": "High"},
        "customer_data": {"date_of_birth": "N/A", "address": "PO Box 123, Delaware", "phone": "+1-555-0345"}
    },
    
    # Alert 9: Cryptocurrency Conversion
    {
        "customer_id": "CUS-990011",
        "customer_name": "Kevin Zhang",
        "account_number": "ACC-2024-3344",
        "alert_type": "Crypto Conversion",
        "priority": "high",
        "alert_reason": "Large cash deposits followed by immediate transfers to cryptocurrency exchanges. Total $95K in 10 days. Customer has no crypto business.",
        "transaction_data": [
            {"date": "2024-02-08", "amount": 15000, "counterparty": "Cash Deposit", "description": "Branch deposit"},
            {"date": "2024-02-09", "amount": 20000, "counterparty": "Cash Deposit", "description": "Branch deposit"},
            {"date": "2024-02-10", "amount": 35000, "counterparty": "Coinbase", "description": "Wire to crypto exchange"},
            {"date": "2024-02-12", "amount": 25000, "counterparty": "Cash Deposit", "description": "Branch deposit"},
            {"date": "2024-02-14", "amount": 60000, "counterparty": "Binance", "description": "Wire to crypto exchange"}
        ],
        "kyc_data": {"occupation": "Software Engineer", "annual_income": "$95,000", "expected_activity": "$8,000-$12,000", "risk_rating": "Low"},
        "customer_data": {"date_of_birth": "1987-06-14", "address": "890 Tech Blvd, San Francisco, CA", "phone": "+1-555-0456"}
    },
    
    # Alert 10: Elderly Exploitation
    {
        "customer_id": "CUS-112244",
        "customer_name": "Margaret Foster",
        "account_number": "ACC-2024-5566",
        "alert_type": "Elder Exploitation",
        "priority": "critical",
        "alert_reason": "85-year-old customer. Sudden large withdrawals ($120K) to unfamiliar beneficiaries. Pattern inconsistent with 20-year account history.",
        "transaction_data": [
            {"date": "2024-02-10", "amount": 40000, "counterparty": "Unknown Person A", "description": "Wire transfer"},
            {"date": "2024-02-12", "amount": 35000, "counterparty": "Unknown Person B", "description": "Wire transfer"},
            {"date": "2024-02-14", "amount": 45000, "counterparty": "Unknown Person C", "description": "Wire transfer"}
        ],
        "kyc_data": {"occupation": "Retired", "annual_income": "$30,000", "expected_activity": "$2,000-$3,000", "risk_rating": "Low"},
        "customer_data": {"date_of_birth": "1939-03-20", "address": "456 Senior Ln, Phoenix, AZ", "phone": "+1-555-0567"}
    },

    # Alert 11: Gambling Winnings
    {
        "customer_id": "CUS-334466",
        "customer_name": "Thomas Baker",
        "account_number": "ACC-2024-7788",
        "alert_type": "Suspicious Gambling",
        "priority": "medium",
        "alert_reason": "Multiple large deposits labeled as casino winnings ($180K total). No W-2G forms provided. Customer claims professional gambler status.",
        "transaction_data": [
            {"date": "2024-02-05", "amount": 45000, "counterparty": "Self", "description": "Casino winnings deposit"},
            {"date": "2024-02-08", "amount": 55000, "counterparty": "Self", "description": "Casino winnings deposit"},
            {"date": "2024-02-12", "amount": 40000, "counterparty": "Self", "description": "Casino winnings deposit"},
            {"date": "2024-02-15", "amount": 40000, "counterparty": "Self", "description": "Casino winnings deposit"}
        ],
        "kyc_data": {"occupation": "Professional Gambler", "annual_income": "$50,000", "expected_activity": "$5,000-$10,000", "risk_rating": "Medium"},
        "customer_data": {"date_of_birth": "1980-08-17", "address": "789 Lucky St, Las Vegas, NV", "phone": "+1-555-0678"}
    },
    
    # Alert 12: Loan Back Scheme
    {
        "customer_id": "CUS-556688",
        "customer_name": "Lisa Patel",
        "account_number": "ACC-2024-9900",
        "alert_type": "Loan Back",
        "priority": "high",
        "alert_reason": "Customer wired $200K to offshore entity, then received $180K back as 'loan'. Possible self-lending to legitimize illicit funds.",
        "transaction_data": [
            {"date": "2024-02-01", "amount": 200000, "counterparty": "Offshore Lending Co", "description": "Wire sent"},
            {"date": "2024-02-05", "amount": 180000, "counterparty": "Offshore Lending Co", "description": "Loan proceeds received"}
        ],
        "kyc_data": {"occupation": "Business Owner", "annual_income": "$150,000", "expected_activity": "$20,000-$30,000", "risk_rating": "Medium"},
        "customer_data": {"date_of_birth": "1985-11-22", "address": "234 Commerce Dr, Houston, TX", "phone": "+1-555-0789"}
    },
    
    # Alert 13: Payroll Fraud
    {
        "customer_id": "CUS-778800",
        "customer_name": "ABC Staffing Inc",
        "account_number": "ACC-2024-2233",
        "alert_type": "Payroll Fraud",
        "priority": "high",
        "alert_reason": "Payroll account shows 50 employees but only 10 active. $300K in payroll deposits, but $250K withdrawn to unknown accounts.",
        "transaction_data": [
            {"date": "2024-02-01", "amount": 300000, "counterparty": "Company Account", "description": "Payroll funding"},
            {"date": "2024-02-02", "amount": 50000, "counterparty": "Legitimate Payroll", "description": "Employee payments"},
            {"date": "2024-02-03", "amount": 80000, "counterparty": "Unknown Account A", "description": "Wire transfer"},
            {"date": "2024-02-04", "amount": 85000, "counterparty": "Unknown Account B", "description": "Wire transfer"},
            {"date": "2024-02-05", "amount": 85000, "counterparty": "Unknown Account C", "description": "Wire transfer"}
        ],
        "kyc_data": {"occupation": "Staffing Company", "annual_income": "N/A", "expected_activity": "$200,000-$400,000", "risk_rating": "Medium"},
        "customer_data": {"date_of_birth": "N/A", "address": "567 Business Park, Atlanta, GA", "phone": "+1-555-0890"}
    },

    # Alert 14: Real Estate Flip
    {
        "customer_id": "CUS-990022",
        "customer_name": "Richard Moore",
        "account_number": "ACC-2024-4455",
        "alert_type": "Real Estate ML",
        "priority": "medium",
        "alert_reason": "Property purchased for $500K cash, sold 2 weeks later for $450K. Loss inconsistent with profit motive. Possible value transfer.",
        "transaction_data": [
            {"date": "2024-02-01", "amount": 500000, "counterparty": "Title Company", "description": "Property purchase"},
            {"date": "2024-02-14", "amount": 450000, "counterparty": "Buyer Unknown", "description": "Property sale proceeds"}
        ],
        "kyc_data": {"occupation": "Real Estate Investor", "annual_income": "$120,000", "expected_activity": "$50,000-$100,000", "risk_rating": "Medium"},
        "customer_data": {"date_of_birth": "1975-02-28", "address": "890 Realty Rd, Orlando, FL", "phone": "+1-555-0901"}
    },
    
    # Alert 15: Hawala Network
    {
        "customer_id": "CUS-112255",
        "customer_name": "Ahmed Hassan",
        "account_number": "ACC-2024-6688",
        "alert_type": "Hawala Suspected",
        "priority": "critical",
        "alert_reason": "Multiple small deposits from various individuals ($150K total), followed by large international wires to Middle East. Pattern consistent with hawala.",
        "transaction_data": [
            {"date": "2024-02-01", "amount": 8000, "counterparty": "Person A", "description": "Deposit"},
            {"date": "2024-02-02", "amount": 12000, "counterparty": "Person B", "description": "Deposit"},
            {"date": "2024-02-03", "amount": 15000, "counterparty": "Person C", "description": "Deposit"},
            {"date": "2024-02-04", "amount": 10000, "counterparty": "Person D", "description": "Deposit"},
            {"date": "2024-02-05", "amount": 18000, "counterparty": "Person E", "description": "Deposit"},
            {"date": "2024-02-06", "amount": 14000, "counterparty": "Person F", "description": "Deposit"},
            {"date": "2024-02-07", "amount": 16000, "counterparty": "Person G", "description": "Deposit"},
            {"date": "2024-02-08", "amount": 13000, "counterparty": "Person H", "description": "Deposit"},
            {"date": "2024-02-09", "amount": 11000, "counterparty": "Person I", "description": "Deposit"},
            {"date": "2024-02-10", "amount": 12000, "counterparty": "Person J", "description": "Deposit"},
            {"date": "2024-02-11", "amount": 21000, "counterparty": "Person K", "description": "Deposit"},
            {"date": "2024-02-12", "amount": 145000, "counterparty": "Dubai Bank", "description": "International wire"}
        ],
        "kyc_data": {"occupation": "Money Service Business", "annual_income": "$80,000", "expected_activity": "$30,000-$50,000", "risk_rating": "High"},
        "customer_data": {"date_of_birth": "1983-07-10", "address": "123 Exchange St, Dearborn, MI", "phone": "+1-555-1012"}
    }
]

def load_alerts():
    """Load comprehensive sample alerts into the system"""
    
    print("=" * 60)
    print("Loading Comprehensive Sample Alerts")
    print("=" * 60)
    
    # Login first
    try:
        login_response = requests.post(
            "http://localhost:8000/api/v1/auth/login",
            data={"username": "admin@barclays.com", "password": "Admin@123"}
        )
        
        if login_response.status_code != 200:
            print("❌ Failed to login")
            print(f"   Status: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"\n✅ Logged in successfully")
        print(f"\nLoading {len(sample_alerts)} sample alerts...\n")
        
        success_count = 0
        for i, alert in enumerate(sample_alerts, 1):
            try:
                response = requests.post(
                    "http://localhost:8000/api/v1/alerts/",
                    json=alert,
                    headers=headers
                )
                
                if response.status_code == 200:
                    print(f"✅ [{i:2d}/15] {alert['customer_name']:25s} - {alert['alert_type']:20s} ({alert['priority'].upper()})")
                    success_count += 1
                else:
                    print(f"❌ [{i:2d}/15] {alert['customer_name']:25s} - Failed")
                    print(f"         Error: {response.text[:100]}")
            except Exception as e:
                print(f"❌ [{i:2d}/15] {alert['customer_name']:25s} - Exception: {str(e)[:50]}")
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully loaded {success_count}/{len(sample_alerts)} alerts!")
        print("=" * 60)
        print("\n📊 Alert Summary:")
        print(f"   - Structuring: 1")
        print(f"   - Layering: 1")
        print(f"   - Funnel Account: 1")
        print(f"   - Trade-Based ML: 1")
        print(f"   - Smurfing: 1")
        print(f"   - Round Dollar: 1")
        print(f"   - Rapid Turnover: 1")
        print(f"   - Shell Company: 1")
        print(f"   - Crypto Conversion: 1")
        print(f"   - Elder Exploitation: 1")
        print(f"   - Suspicious Gambling: 1")
        print(f"   - Loan Back: 1")
        print(f"   - Payroll Fraud: 1")
        print(f"   - Real Estate ML: 1")
        print(f"   - Hawala Suspected: 1")
        print("\n🌐 Access Alert Data at: http://localhost:3000/alerts")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("   Please start the backend server first:")
        print("   > .\\start-backend.ps1")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    load_alerts()
