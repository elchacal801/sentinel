# Sentinel Quickstart Guide

**Classification:** UNCLASSIFIED//FOUO

Get Sentinel Intelligence Platform running in 15 minutes with this step-by-step guide.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Option 1: Docker Compose (Recommended)](#option-1-docker-compose-recommended)
- [Option 2: Manual Setup](#option-2-manual-setup)
- [Verification](#verification)
- [First Run](#first-run)
- [Next Steps](#next-steps)

---

## Prerequisites

### Required Software

**Install these first:**

```bash
# Check if installed
docker --version        # Need 20.10+
docker-compose --version # Need 1.29+
python --version        # Need 3.11+
node --version          # Need 18+
git --version           # Any recent version

# If not installed:
# macOS:
brew install docker docker-compose python@3.11 node

# Ubuntu/Debian:
sudo apt update
sudo apt install docker.io docker-compose python3.11 nodejs npm

# Windows:
# Download Docker Desktop from docker.com
# Download Python from python.org
# Download Node.js from nodejs.org
```

### System Requirements

- **CPU:** 4 cores (minimum), 8 cores (recommended)
- **RAM:** 8GB (minimum), 16GB (recommended)
- **Disk:** 20GB free space
- **OS:** macOS, Linux, or Windows 10/11 with WSL2

---

## Option 1: Docker Compose (Recommended)

**This is the easiest and fastest way to get started.**

### Step 1: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/elchacal801/sentinel.git
cd sentinel
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
# (See "Environment Variables" section below for all options)

# Minimum required:
echo "NEO4J_USER=neo4j" >> .env
echo "NEO4J_PASSWORD=sentinel-secure-password" >> .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

### Step 3: Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# This will start:
# - Neo4j (graph database)
# - Redis (task queue)
# - PostgreSQL (optional, for logs)
# - Elasticsearch (optional, for search)

# Wait for services to be ready (30-60 seconds)
sleep 60
```

### Step 4: Verify Services

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                   STATUS
# sentinel-neo4j         Up
# sentinel-redis         Up
# sentinel-postgres      Up

# Test Neo4j
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel-secure-password "RETURN 1"
# Expected: 1

# Test Redis
docker exec sentinel-redis redis-cli ping
# Expected: PONG
```

### Step 5: Install Backend Dependencies

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Should take 2-3 minutes
```

### Step 6: Start Backend API

```bash
# Still in backend directory with venv activated

# Start Celery worker (for async tasks)
celery -A workers.celery_app worker --loglevel=info &

# Start FastAPI backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Backend will start on http://localhost:8000
# Leave this terminal running
```

### Step 7: Start Frontend

```bash
# Open NEW terminal
cd sentinel/frontend

# Install dependencies (one-time)
npm install
# Takes 3-5 minutes

# Start development server
npm run dev

# Frontend will start on http://localhost:3000
# Leave this terminal running
```

### Step 8: Access Sentinel

Open your browser:
- **Frontend:** http://localhost:3000
- **Dashboard:** http://localhost:3000/dashboard
- **API Docs:** http://localhost:8000/docs
- **Neo4j Browser:** http://localhost:7474

**Done! Sentinel is running.**

---

## Option 2: Manual Setup

**For those who prefer manual control or can't use Docker.**

### Step 1: Install Neo4j

```bash
# macOS (Homebrew)
brew install neo4j

# Ubuntu/Debian
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update
sudo apt install neo4j

# Start Neo4j
neo4j start

# Set password
neo4j-admin set-initial-password sentinel-secure-password
```

### Step 2: Install Redis

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# Windows
# Download from https://github.com/tporadowski/redis/releases
# Run redis-server.exe
```

### Step 3: Clone & Setup Backend

```bash
# Clone repository
git clone https://github.com/elchacal801/sentinel.git
cd sentinel/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your settings

# Update Neo4j connection
echo "NEO4J_URI=bolt://localhost:7687" >> ../.env
echo "NEO4J_USER=neo4j" >> ../.env
echo "NEO4J_PASSWORD=sentinel-secure-password" >> ../.env
```

### Step 4: Start Backend Services

```bash
# Terminal 1: Celery worker
cd backend
source venv/bin/activate
celery -A workers.celery_app worker --loglevel=info

# Terminal 2: FastAPI backend
cd backend
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Setup & Start Frontend

```bash
# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

### Step 6: Access Sentinel

Same as Docker Compose option:
- Frontend: http://localhost:3000
- Dashboard: http://localhost:3000/dashboard
- API: http://localhost:8000/docs

---

## Verification

### Check All Services

Run this verification script:

```bash
#!/bin/bash
echo "=== Sentinel Service Check ==="

# Check Neo4j
echo -n "Neo4j: "
curl -s http://localhost:7474 > /dev/null && echo "✓ Running" || echo "✗ Not running"

# Check Redis
echo -n "Redis: "
redis-cli ping 2>/dev/null | grep -q PONG && echo "✓ Running" || echo "✗ Not running"

# Check Backend API
echo -n "Backend API: "
curl -s http://localhost:8000/api/v1/health > /dev/null && echo "✓ Running" || echo "✗ Not running"

# Check Frontend
echo -n "Frontend: "
curl -s http://localhost:3000 > /dev/null && echo "✓ Running" || echo "✗ Not running"

echo ""
echo "If all services show ✓, you're ready to go!"
```

Save as `check_services.sh`, make executable, and run:
```bash
chmod +x check_services.sh
./check_services.sh
```

---

## First Run

### Collect Your First Data

**Step 1: Trigger Asset Discovery**

```bash
# Using curl
curl -X POST http://localhost:8000/api/v1/assets/discover \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# Using Python
python -c "
import requests
response = requests.post(
    'http://localhost:8000/api/v1/assets/discover',
    json={'domain': 'example.com'}
)
print(response.json())
"
```

**Step 2: Wait for Collection** (2-3 minutes)

```bash
# Monitor Celery worker logs
# You should see tasks being processed

# Check Neo4j for data
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel-secure-password \
  "MATCH (a:Asset) RETURN count(a) as count"
```

**Step 3: View in Dashboard**

1. Open http://localhost:3000/dashboard
2. Click "Knowledge Graph" tab
3. Should see discovered assets

**Step 4: Generate Intelligence Product**

```bash
# Generate current intelligence briefing
curl http://localhost:8000/api/v1/products/current-intelligence

# Or in dashboard:
# Click "Intel Products" tab
# Click "Current Intelligence" button
```

---

## Environment Variables

### Complete .env Configuration

Create `.env` file in project root with these variables:

```bash
# ===========================================
# NEO4J CONFIGURATION (REQUIRED)
# ===========================================
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=sentinel-secure-password-change-me

# ===========================================
# REDIS CONFIGURATION (REQUIRED)
# ===========================================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Leave empty if no password

# ===========================================
# POSTGRESQL (OPTIONAL - for logging)
# ===========================================
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=sentinel
POSTGRES_USER=sentinel
POSTGRES_PASSWORD=secure-postgres-password

# ===========================================
# APPLICATION SECRETS (REQUIRED)
# ===========================================
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
JWT_SECRET=your-jwt-secret-generate-with-openssl-rand-hex-32

# ===========================================
# API KEYS (OPTIONAL - improves collection)
# ===========================================
# GitHub Personal Access Token (for advisories)
GITHUB_TOKEN=ghp_your_token_here

# NVD API Key (for CVE data)
NVD_API_KEY=your-nvd-api-key

# Shodan API Key (for OSINT)
SHODAN_API_KEY=your-shodan-key

# VirusTotal API Key (for malware intel)
VIRUSTOTAL_API_KEY=your-virustotal-key

# ===========================================
# COLLECTION SETTINGS
# ===========================================
# Rate limiting (requests per second)
RATE_LIMIT_ASM=10
RATE_LIMIT_OSINT=5
RATE_LIMIT_CYBINT=20

# Collection intervals (seconds)
ASM_INTERVAL=3600          # 1 hour
OSINT_INTERVAL=21600       # 6 hours
CYBINT_INTERVAL=86400      # 24 hours

# ===========================================
# LOGGING
# ===========================================
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/sentinel.log

# ===========================================
# SECURITY
# ===========================================
# JWT token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# ===========================================
# FRONTEND
# ===========================================
NEXT_PUBLIC_API_URL=http://localhost:8000

# ===========================================
# CELERY
# ===========================================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ===========================================
# ELASTICSEARCH (OPTIONAL)
# ===========================================
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=elastic-password

# ===========================================
# KAFKA (OPTIONAL - for streaming)
# ===========================================
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_INTELLIGENCE=sentinel-intelligence

# ===========================================
# TIMESCALEDB (OPTIONAL - for time-series)
# ===========================================
TIMESCALE_HOST=localhost
TIMESCALE_PORT=5432
TIMESCALE_DB=sentinel_timeseries
TIMESCALE_USER=sentinel
TIMESCALE_PASSWORD=timescale-password

# ===========================================
# MINIO (OPTIONAL - for object storage)
# ===========================================
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=sentinel-data

# ===========================================
# MONITORING
# ===========================================
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# ===========================================
# DEPLOYMENT
# ===========================================
ENVIRONMENT=development    # development, staging, production
DEBUG=True                 # False in production
```

### Generating Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET
openssl rand -hex 32

# Generate strong password
openssl rand -base64 32
```

### Minimum Required Variables

**For basic functionality, you only need:**

```bash
# .env (minimum)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password
SECRET_KEY=$(openssl rand -hex 32)
REDIS_HOST=localhost
```

### Optional API Keys

**Get these for enhanced collection:**

1. **GitHub Token** (Free)
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `public_repo`, `read:org`
   - Copy token to `GITHUB_TOKEN`

2. **NVD API Key** (Free)
   - Go to: https://nvd.nist.gov/developers/request-an-api-key
   - Request API key
   - Copy to `NVD_API_KEY`

3. **Shodan API Key** (Free tier available)
   - Sign up: https://account.shodan.io/register
   - Copy API key from account page
   - Add to `SHODAN_API_KEY`

4. **VirusTotal API Key** (Free tier available)
   - Sign up: https://www.virustotal.com/gui/join-us
   - Get API key from profile
   - Add to `VIRUSTOTAL_API_KEY`

---

## Next Steps

### 1. Explore the Dashboard

- Visit http://localhost:3000/dashboard
- Click through all 6 tabs
- Try generating intelligence products

### 2. Collect More Data

```bash
# Run full collection suite
cd backend
source venv/bin/activate

# ASM
python -m services.asm.scanner

# OSINT
python -m services.osint.collector

# CYBINT
python -m services.cybint.vuln_scanner

# Threat Intel
python -m services.cybint.threat_collector
```

### 3. Review Documentation

- **USER_GUIDE.md** - How to use the platform
- **TESTING.md** - End-to-end testing procedures
- **DEPLOYMENT.md** - Production deployment guide
- **README.md** - Project overview

### 4. Set Up Automation

```bash
# Add to crontab for automated collection
crontab -e

# Add these lines:
0 2 * * * cd /path/to/sentinel/backend && /path/to/venv/bin/python -m services.asm.scanner
0 */6 * * * cd /path/to/sentinel/backend && /path/to/venv/bin/python -m services.osint.collector
0 3 * * * cd /path/to/sentinel/backend && /path/to/venv/bin/python -m services.cybint.threat_collector
```

### 5. Production Deployment

When ready for production:

1. Review **DEPLOYMENT.md** for Kubernetes setup
2. Use production Docker images (`docker-compose.prod.yml`)
3. Set up monitoring (Prometheus/Grafana)
4. Configure backups
5. Harden security (SSL, secrets, firewalls)

---

## Troubleshooting

### Issue: Docker containers won't start

```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Issue: Backend API errors

```bash
# Check logs
cd backend
tail -f logs/backend.log  # if configured

# Verify .env file
cat .env | grep -E "NEO4J|REDIS|SECRET"

# Test manually
python -c "from api.main import app; print('Import OK')"
```

### Issue: Frontend won't start

```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Try different port
PORT=3001 npm run dev
```

### Issue: No data in dashboard

**This is expected if you haven't run collection services!**

```bash
# Check if data exists in Neo4j
docker exec sentinel-neo4j cypher-shell -u neo4j -p your-password \
  "MATCH (n) RETURN labels(n), count(n)"

# If empty, run collection
cd backend
python -m services.asm.scanner
```

---

## Quick Reference

### Start Services (Docker)
```bash
docker-compose up -d
cd backend && uvicorn api.main:app --reload &
cd frontend && npm run dev &
```

### Stop Services
```bash
# Stop frontend/backend (Ctrl+C in terminals)
docker-compose down
```

### View Logs
```bash
docker-compose logs -f       # All services
docker-compose logs neo4j    # Specific service
```

### Reset Everything
```bash
# WARNING: Deletes all data
docker-compose down -v
rm -rf backend/venv frontend/node_modules
# Then start fresh from Step 1
```

### Check Status
```bash
docker-compose ps
curl http://localhost:8000/api/v1/health
curl http://localhost:3000/
```

---

## Support

**Need help?**
- Check **TESTING.md** for detailed troubleshooting
- Review **USER_GUIDE.md** for usage questions
- See **DEPLOYMENT.md** for production setup
- Open issue on GitHub: https://github.com/elchacal801/sentinel/issues

---

**Classification:** UNCLASSIFIED//FOUO  
**Version:** 1.0.0  
**Last Updated:** 2025-10-02

**You're now ready to use Sentinel! 🎉**
