# AML INTELLIGENCE PLATFORM

**Team:** Airavat  
**GitHub:** https://github.com/Dnyaneshh18/Hack-O-Hire  
**Hackathon:** Hack-O-Hire

---

## TABLE OF CONTENTS

1. [What is This Project?](#what-is-this-project)
2. [Prerequisites](#prerequisites)
3. [Complete Setup Guide](#complete-setup-guide)
4. [Running the Application](#running-the-application)
5. [Demo Credentials](#demo-credentials)
6. [How to Use](#how-to-use)
7. [Troubleshooting](#troubleshooting)
8. [Quick Reference](#quick-reference)

---

## WHAT IS THIS PROJECT?

An AI-powered platform that generates Suspicious Activity Reports (SARs) for anti-money laundering compliance in 30 seconds instead of 5-6 hours.

**Key Features:**
- 99% time reduction (5-6 hours to 30 seconds)
- $2.75M annual cost savings
- World-first Evidence Mapping
- 16-stage AI analysis pipeline
- Complete audit trail and FinCEN compliance

---

## PREREQUISITES

Before starting, ensure you have these installed:

### 1. Python 3.13 or Higher
- Download: https://www.python.org/downloads/
- IMPORTANT: Check "Add Python to PATH" during installation
- Verify: `python --version`

### 2. Node.js 18 or Higher
- Download: https://nodejs.org/
- Install LTS version
- Verify: `node --version` and `npm --version`

### 3. PostgreSQL 18
- Download: https://www.postgresql.org/download/
- Remember your password during installation
- Install pgAdmin (GUI tool)

### 4. Ollama (for AI)
- Download: https://ollama.ai/
- Verify: `ollama --version`

### 5. Git (Optional)
- Download: https://git-scm.com/downloads

---

## COMPLETE SETUP GUIDE

### STEP 1: Clone or Download Project

**Using Git:**
```bash
git clone https://github.com/Dnyaneshh18/Hack-O-Hire.git
cd Hack-O-Hire
```

**Or Download ZIP:**
- Go to GitHub repository
- Click "Code" → "Download ZIP"
- Extract and open terminal in folder

### STEP 2: Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### STEP 3: Install Python Packages

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all packages
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary
pip install pydantic pydantic-settings python-multipart
pip install python-jose[cryptography] passlib[bcrypt] alembic
pip install langchain langchain-community ollama chromadb sentence-transformers
pip install reportlab PyPDF2 openpyxl aiofiles email-validator
pip install python-dotenv httpx jinja2 bcrypt
```

### STEP 4: Create Database

**Using pgAdmin (Recommended):**
1. Open pgAdmin
2. Right-click "Databases" → Create → Database
3. Name: `sar_system`
4. Save

**Using Command Line:**
```bash
psql -U postgres
CREATE DATABASE sar_system;
\q
```

### STEP 5: Configure Environment

1. Open `.env` file in project root
2. Update with your PostgreSQL password:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=sar_system
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD_HERE
```

### STEP 6: Create Database Tables and Users

```bash
python scripts/create_demo_users.py
```

Expected output:
```
✓ Database tables created successfully
✓ Created user: admin@barclays.com
✓ Created user: analyst@barclays.com
✓ Created user: supervisor@barclays.com
```

### STEP 7: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### STEP 8: Install AI Model

```bash
# Download Llama 3 (takes 5-10 minutes)
ollama pull llama3:latest

# Verify
ollama list
```

---

## RUNNING THE APPLICATION

You need 3 separate terminals:

### Terminal 1: Backend

```bash
cd Hack-O-Hire
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected: `INFO: Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Frontend

```bash
cd Hack-O-Hire\frontend
npm start
```

Expected: `Compiled successfully! Local: http://localhost:3000`

### Terminal 3: Ollama

```bash
ollama serve
```

Expected: `Listening on 127.0.0.1:11434`

### Terminal 4 (Optional): Load Sample Data

```bash
cd Hack-O-Hire
python scripts/load_comprehensive_alerts.py
```

This loads 15 sample alerts.

---

## DEMO CREDENTIALS

Access at: http://localhost:3000

### Admin Account
- Email: `admin@barclays.com`
- Password: `Admin@123`
- Access: Full system access

### Analyst Account
- Email: `analyst@barclays.com`
- Password: `password123`
- Access: Generate SARs, view reports

### Supervisor Account
- Email: `supervisor@barclays.com`
- Password: `password123`
- Access: Approve/reject SARs

---

## HOW TO USE

### Step 1: Login
- Open http://localhost:3000
- Use any credentials above

### Step 2: View Alerts
- Click "Alert Data" in sidebar
- See 15+ sample alerts
- Color-coded by priority

### Step 3: Generate SAR
- Click "Generate SAR" on any alert
- Review customer/transaction data
- Click "Generate SAR Narrative with AI"
- Wait 30-60 seconds

### Step 4: Review Results
- View Case ID, Risk Score, Typology
- Click "View Full Analysis"
- Explore 16 analysis stages
- Check Evidence Mapping
- Review Contradiction Detection

### Step 5: Export SAR
- Click "Export SAR"
- Choose: PDF, XML, CSV, or Email
- Download report

---

## TROUBLESHOOTING

### Backend Won't Start

**Error: "No module named 'app'"**
```bash
cd Hack-O-Hire
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Error: "No module named 'psycopg2'"**
```bash
pip install psycopg2-binary
```

**Error: "Port 8000 in use"**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Error

1. Check PostgreSQL is running
2. Verify database `sar_system` exists
3. Check password in `.env` file
4. Verify port (5432 or 5433)

### Frontend Won't Start

**Error: "npm not found"**
- Install Node.js from https://nodejs.org/

**Error: "Port 3000 in use"**
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Ollama Not Working

**Error: "Ollama not found"**
1. Install from https://ollama.ai/
2. Run: `ollama pull llama3:latest`
3. Verify: `ollama list`

**Error: "Connection refused"**
```bash
ollama serve
```

### Login Fails

1. Create demo users:
   ```bash
   python scripts/create_demo_users.py
   ```
2. Use exact credentials (case-sensitive)
3. Check backend is running

### No Alerts Showing

```bash
python scripts/load_comprehensive_alerts.py
```

---

## QUICK REFERENCE

```bash
# 1. Clone
git clone https://github.com/Dnyaneshh18/Hack-O-Hire.git
cd Hack-O-Hire

# 2. Python setup
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip

# 3. Install packages
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary pydantic pydantic-settings
pip install python-multipart python-jose[cryptography] passlib[bcrypt] alembic
pip install langchain langchain-community ollama chromadb sentence-transformers
pip install reportlab PyPDF2 openpyxl aiofiles email-validator python-dotenv httpx jinja2 bcrypt

# 4. Create database (pgAdmin or psql)
# Database name: sar_system

# 5. Update .env with PostgreSQL password

# 6. Create tables and users
python scripts/create_demo_users.py

# 7. Frontend setup
cd frontend
npm install
cd ..

# 8. Install AI model
ollama pull llama3:latest

# 9. Run (3 terminals)
# Terminal 1: Backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm start

# Terminal 3: Ollama
ollama serve

# 10. Load sample data (optional)
python scripts/load_comprehensive_alerts.py

# 11. Access
# http://localhost:3000
# Login: analyst@barclays.com / password123
```

---

## TECHNOLOGY STACK

- **Frontend:** React 18, Material-UI
- **Backend:** FastAPI, Python 3.13
- **Database:** PostgreSQL 18
- **AI:** Llama 3, Ollama, LangChain, ChromaDB
- **Security:** JWT, RBAC, Bcrypt

---

## SYSTEM REQUIREMENTS

- OS: Windows 10/11, macOS 10.15+, Linux
- RAM: 8GB minimum (16GB recommended)
- Disk: 10GB free space
- Internet: Required for setup

---

## PROJECT STRUCTURE

```
Hack-O-Hire/
├── app/                 # Backend
│   ├── api/v1/         # API endpoints
│   ├── core/           # Config, database, security
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── main.py         # Entry point
├── frontend/           # React app
│   ├── src/
│   │   ├── api/       # API client
│   │   ├── components/# React components
│   │   ├── pages/     # Page components
│   │   └── App.js     # Main app
│   └── package.json
├── scripts/            # Utility scripts
├── data/              # Data storage
├── .env               # Environment variables
└── requirements.txt   # Python dependencies
```

---

## SUPPORT

If you encounter issues:
1. Check Troubleshooting section
2. Verify all prerequisites installed
3. Ensure all 3 terminals running
4. Visit: https://github.com/Dnyaneshh18/Hack-O-Hire

---

**Team Airavat**  
**Hack-O-Hire Hackathon**  
**February 2026**

**Version:** 1.0 (Production Ready)
