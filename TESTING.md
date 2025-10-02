# Sentinel Testing Guide

**Classification:** UNCLASSIFIED//FOUO

This guide walks you through testing Sentinel end-to-end to verify all workflows and processes work correctly.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Validation](#quick-validation)
- [Component Testing](#component-testing)
- [End-to-End Workflows](#end-to-end-workflows)
- [Integration Testing](#integration-testing)
- [Performance Testing](#performance-testing)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services Running

```bash
# Check Docker containers are running
docker ps

# Should see:
# - sentinel-neo4j
# - sentinel-redis
# - sentinel-postgres (optional)
```

### Test Tools

```bash
# Install testing tools
pip install pytest requests httpx

# For frontend testing
cd frontend
npm install
```

---

## Quick Validation

### 1. Database Connectivity

```bash
# Test Neo4j connection
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel "RETURN 1"
# Expected: Should return "1"

# Test Redis connection
docker exec sentinel-redis redis-cli ping
# Expected: "PONG"
```

### 2. Backend Health Check

```bash
# Start backend (if not running)
cd backend
uvicorn api.main:app --reload

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "timestamp": "2025-10-02T00:00:00Z"
# }
```

### 3. Frontend Accessibility

```bash
# Start frontend (if not running)
cd frontend
npm run dev

# Test frontend
curl http://localhost:3000/

# Expected: HTML response with status 200

# Visit in browser
# http://localhost:3000
# Should see Sentinel home page
```

---

## Component Testing

### Test 1: Attack Surface Management (ASM)

**Purpose:** Verify subdomain discovery and port scanning work

```bash
# Start Celery worker
cd backend
celery -A workers.celery_app worker --loglevel=info

# In another terminal, test ASM
python -c "
from services.asm.scanner import AttackSurfaceScanner
import asyncio

async def test():
    scanner = AttackSurfaceScanner()
    # Test subdomain discovery
    subdomains = await scanner.discover_subdomains('example.com')
    print(f'Found {len(subdomains)} subdomains')
    
    # Test port scanning
    if subdomains:
        results = await scanner.scan_ports(subdomains[0], [80, 443])
        print(f'Port scan results: {results}')

asyncio.run(test())
"
```

**Expected Output:**
```
Found X subdomains
Port scan results: {...}
```

**Verify in Neo4j:**
```bash
# Connect to Neo4j browser: http://localhost:7474
# Run query:
MATCH (a:Asset) RETURN a LIMIT 10
# Should see discovered assets
```

### Test 2: OSINT Collection

**Purpose:** Verify Certificate Transparency and threat feed collection

```bash
# Test CT log collection
python -c "
from services.osint.ct_logs import CertificateTransparencyCollector
import asyncio

async def test():
    collector = CertificateTransparencyCollector()
    results = await collector.search_domain('example.com')
    print(f'Found {len(results)} certificates')
    for cert in results[:5]:
        print(f'  - {cert.get(\"name_value\")}')

asyncio.run(test())
"
```

**Expected Output:**
```
Found X certificates
  - example.com
  - www.example.com
  - ...
```

### Test 3: Vulnerability Detection

**Purpose:** Verify CVE enrichment and vulnerability scanning

```bash
# Test CVE enrichment
python -c "
from services.cybint.vuln_scanner import VulnerabilityScanner
import asyncio

async def test():
    scanner = VulnerabilityScanner()
    vuln_data = await scanner.enrich_cve('CVE-2024-1234')
    print(f'CVE: {vuln_data.get(\"cve_id\")}')
    print(f'CVSS: {vuln_data.get(\"cvss_score\")}')
    print(f'Description: {vuln_data.get(\"description\", \"\")[:100]}...')

asyncio.run(test())
"
```

**Expected Output:**
```
CVE: CVE-2024-1234
CVSS: X.X
Description: ...
```

### Test 4: Knowledge Graph Operations

**Purpose:** Verify Neo4j graph operations work

```bash
# Test graph queries
python -c "
from utils.graph import KnowledgeGraphManager
import asyncio

async def test():
    graph = KnowledgeGraphManager()
    
    # Get Neo4j session
    from utils.database import get_neo4j_driver
    driver = get_neo4j_driver()
    
    async with driver.session() as session:
        # Test creating an asset
        query = '''
        CREATE (a:Asset {
            id: 'test-asset-1',
            name: 'test.example.com',
            type: 'web_server',
            created_at: datetime()
        })
        RETURN a
        '''
        result = await graph.query_graph(session, query, {})
        print(f'Created asset: {result}')
        
        # Test querying assets
        query = 'MATCH (a:Asset) RETURN count(a) as count'
        result = await graph.query_graph(session, query, {})
        print(f'Total assets: {result[0][\"count\"]}')
        
        # Cleanup
        query = 'MATCH (a:Asset {id: \"test-asset-1\"}) DELETE a'
        await graph.query_graph(session, query, {})
        print('Cleaned up test data')

asyncio.run(test())
"
```

**Expected Output:**
```
Created asset: [...]
Total assets: X
Cleaned up test data
```

### Test 5: Intelligence Products

**Purpose:** Verify intelligence product generation

```bash
# Test current intelligence briefing
curl http://localhost:8000/api/v1/products/current-intelligence

# Expected: JSON intelligence brief with key_judgments, threat_landscape, etc.

# Test I&W alerts
curl http://localhost:8000/api/v1/products/indications-warning

# Expected: JSON with alert_status, alerts array

# Test executive briefing
curl -X POST http://localhost:8000/api/v1/products/executive-briefing

# Expected: JSON executive briefing with security_posture, critical_risks, etc.
```

### Test 6: Dashboard Visualization

**Purpose:** Verify frontend dashboard works

```bash
# Visit dashboard
# http://localhost:3000/dashboard

# Manual tests:
# 1. Click each tab (Overview, Graph, Attack Paths, Threats, Risk, Products)
# 2. Verify visualizations load or show error messages
# 3. Check console for errors (F12)
# 4. Try generating intelligence products
# 5. Test filters and interactions
```

**Expected:**
- Each tab loads without crashes
- If backend unavailable, shows clear error messages (not mock data)
- Console has no critical errors
- Interactions work (click, hover, filter)

---

## End-to-End Workflows

### Workflow 1: Complete Asset Discovery → Intelligence Product

**Purpose:** Test full pipeline from discovery to intelligence briefing

**Steps:**

1. **Discover Assets**
```bash
# Start services
docker-compose up -d
cd backend

# Start Celery worker
celery -A workers.celery_app worker --loglevel=info &

# Start API
uvicorn api.main:app --reload &

# Trigger asset discovery
curl -X POST http://localhost:8000/api/v1/assets/discover \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```

2. **Wait for Collection** (2-3 minutes)
```bash
# Monitor Celery logs
# Should see tasks being processed

# Check Redis queue
docker exec sentinel-redis redis-cli LLEN celery

# Check Neo4j for assets
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel \
  "MATCH (a:Asset) RETURN count(a)"
```

3. **Verify Data in Graph**
```bash
# Query all entities
curl http://localhost:8000/api/v1/assets/

# Should see discovered assets
```

4. **Run Analytics**
```bash
# Calculate risk scores
curl -X POST http://localhost:8000/api/v1/analysis/risk-scores

# Generate attack paths
curl -X POST http://localhost:8000/api/v1/analysis/attack-paths/generate
```

5. **Generate Intelligence Product**
```bash
# Generate current intelligence briefing
curl http://localhost:8000/api/v1/products/current-intelligence

# Expected: Full briefing with data from discovered assets
```

6. **View in Dashboard**
```bash
# Visit dashboard
open http://localhost:3000/dashboard

# Navigate to each tab:
# - Overview: Should show metrics
# - Graph: Should show discovered assets and relationships
# - Attack Paths: Should show generated paths
# - Products: Generate and view products
```

**Success Criteria:**
- ✅ Assets discovered and in Neo4j
- ✅ Vulnerabilities detected
- ✅ Risk scores calculated
- ✅ Attack paths generated
- ✅ Intelligence products contain real data
- ✅ Dashboard displays all data

---

### Workflow 2: Threat Intelligence Collection → Alert

**Purpose:** Test threat intel collection and I&W alert generation

**Steps:**

1. **Collect Threat Intel**
```bash
# Run threat collector
python -m services.cybint.threat_collector

# Or via API
curl -X POST http://localhost:8000/api/v1/intelligence/threats/collect
```

2. **Verify Threat Data**
```bash
# Check Neo4j
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel \
  "MATCH (t:ThreatActor) RETURN t LIMIT 5"

# Query via API
curl http://localhost:8000/api/v1/intelligence/threats/
```

3. **Generate I&W Alerts**
```bash
# Generate alerts
curl http://localhost:8000/api/v1/products/indications-warning

# Expected: Alert summary with severity levels
```

4. **View Timeline**
```bash
# Visit dashboard threats tab
open http://localhost:3000/dashboard

# Click "Threat Timeline" tab
# Should see threat events chronologically
```

**Success Criteria:**
- ✅ Threat actors in Neo4j
- ✅ I&W alerts generated
- ✅ Timeline displays events
- ✅ Severity filtering works

---

### Workflow 3: Target Package Generation

**Purpose:** Test comprehensive target intelligence package

**Steps:**

1. **Ensure Asset Exists**
```bash
# List assets
curl http://localhost:8000/api/v1/assets/

# Pick an asset ID
ASSET_ID="asset-1"
```

2. **Generate Target Package**
```bash
# Generate package
curl -X POST http://localhost:8000/api/v1/products/target-package/$ASSET_ID

# Expected: Comprehensive target package with:
# - Executive summary
# - Target profile
# - Vulnerability assessment
# - Threat assessment
# - Attack surface analysis
# - Risk analysis
# - Recommendations
```

3. **View in Dashboard**
```bash
# Visit products tab
open http://localhost:3000/dashboard

# Click "Products" tab
# Click "Target Package" button
# View generated package
```

**Success Criteria:**
- ✅ Package generated successfully
- ✅ Contains asset details
- ✅ Includes vulnerabilities
- ✅ Shows threat intelligence
- ✅ Provides recommendations

---

## Integration Testing

### API Integration Tests

Create `backend/tests/test_integration.py`:

```python
import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_assets_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/assets/")
        assert response.status_code == 200
        # Should return list of assets or empty array

@pytest.mark.asyncio
async def test_current_intelligence():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/products/current-intelligence")
        # If backend/data available: status 200
        # If not: should still return structured error

@pytest.mark.asyncio
async def test_iw_alerts():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/products/indications-warning")
        # Should return alert structure

# Run tests
# pytest tests/test_integration.py -v
```

### Frontend Integration Tests

```bash
# In frontend directory
cd frontend

# Run type check
npm run type-check

# Run linter
npm run lint

# Run build (verifies no errors)
npm run build
```

---

## Performance Testing

### Load Testing

```bash
# Install hey (HTTP load generator)
# macOS: brew install hey
# Linux: Download from https://github.com/rakyll/hey

# Test API health endpoint
hey -n 1000 -c 10 http://localhost:8000/api/v1/health

# Expected: All requests successful, <100ms p99 latency

# Test assets endpoint
hey -n 500 -c 5 http://localhost:8000/api/v1/assets/

# Monitor resource usage
docker stats
```

### Database Performance

```bash
# Test Neo4j query performance
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel \
  "PROFILE MATCH (a:Asset) RETURN a LIMIT 100"

# Check db.stats
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel \
  "CALL dbms.queryJmx('org.neo4j:*') YIELD name, attributes"
```

---

## Troubleshooting

### Issue: Backend API Not Responding

**Symptoms:** `curl http://localhost:8000/api/v1/health` fails

**Diagnosis:**
```bash
# Check if backend is running
ps aux | grep uvicorn

# Check logs
tail -f logs/backend.log  # if logging configured

# Check Python errors
cd backend
python -c "from api.main import app; print('Import successful')"
```

**Solution:**
```bash
# Restart backend
cd backend
uvicorn api.main:app --reload
```

---

### Issue: Neo4j Connection Failed

**Symptoms:** "Unable to connect to Neo4j"

**Diagnosis:**
```bash
# Check Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs sentinel-neo4j

# Test connection
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel "RETURN 1"
```

**Solution:**
```bash
# Restart Neo4j
docker restart sentinel-neo4j

# Or restart all services
docker-compose restart
```

---

### Issue: Frontend Shows Errors

**Symptoms:** Dashboard tabs show error messages

**Expected Behavior:** This is correct! If backend is unavailable, it should show clear error messages (not mock data)

**Diagnosis:**
```bash
# Check browser console (F12)
# Look for API connection errors

# Verify backend is running
curl http://localhost:8000/api/v1/health
```

**Solution:**
```bash
# Start backend if not running
cd backend
uvicorn api.main:app --reload

# Verify API accessibility
curl http://localhost:8000/api/v1/health

# Refresh browser
```

---

### Issue: No Data in Dashboard

**Symptoms:** Everything loads but no data displayed

**Diagnosis:**
```bash
# Check if data exists in Neo4j
docker exec sentinel-neo4j cypher-shell -u neo4j -p sentinel \
  "MATCH (n) RETURN labels(n), count(n)"

# Should show counts for Asset, Vulnerability, ThreatActor, etc.
```

**Solution:**
```bash
# Run collection services
cd backend

# Start Celery
celery -A workers.celery_app worker --loglevel=info &

# Trigger discovery
curl -X POST http://localhost:8000/api/v1/assets/discover \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# Wait 2-3 minutes, then check again
```

---

## Test Checklist

Use this checklist to verify all components work:

### Infrastructure
- [ ] Docker containers running (Neo4j, Redis)
- [ ] Neo4j accessible at http://localhost:7474
- [ ] Redis responding to PING
- [ ] Network connectivity between services

### Backend
- [ ] API starts without errors
- [ ] Health endpoint returns {"status": "healthy"}
- [ ] Can query assets endpoint
- [ ] Can query intelligence endpoints
- [ ] Celery worker starts without errors

### Frontend
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Development server starts (`npm run dev`)
- [ ] Home page accessible at http://localhost:3000
- [ ] Dashboard accessible at http://localhost:3000/dashboard
- [ ] All 6 tabs load without crashes
- [ ] Error messages shown when backend unavailable

### Data Collection
- [ ] ASM subdomain discovery works
- [ ] Port scanning completes
- [ ] OSINT CT log collection works
- [ ] Vulnerability scanning works
- [ ] Data persists to Neo4j
- [ ] Can query data via API

### Intelligence Products
- [ ] Current intelligence briefing generates
- [ ] I&W alerts generate
- [ ] Target packages generate
- [ ] Executive briefings generate
- [ ] Products contain real data (not mock)

### Visualizations
- [ ] Knowledge graph renders
- [ ] Attack path visualization works
- [ ] Threat timeline displays
- [ ] Risk heatmap shows data
- [ ] Metrics grid displays
- [ ] Filters and interactions work

### End-to-End
- [ ] Complete workflow: Discovery → Analytics → Product
- [ ] Data flows from collection to visualization
- [ ] No critical errors in logs
- [ ] Performance acceptable (<2s page loads)

---

## Automated Test Suite

### Run All Tests

```bash
# Backend unit tests
cd backend
pytest tests/ -v --cov=.

# Frontend tests
cd frontend
npm test
npm run lint
npm run type-check
npm run build

# Integration tests
pytest tests/test_integration.py -v

# Performance tests
hey -n 1000 -c 10 http://localhost:8000/api/v1/health
```

### CI/CD Verification

```bash
# Trigger GitHub Actions locally (if using act)
act -j test-backend
act -j test-frontend

# Or push to trigger
git push origin master

# Monitor at: https://github.com/yourusername/sentinel/actions
```

---

## Success Criteria

**Project is fully functional if:**

1. ✅ All infrastructure services start
2. ✅ Backend API responds to health checks
3. ✅ Frontend dashboard loads
4. ✅ At least one collection service works (ASM/OSINT/CYBINT)
5. ✅ Data persists to Neo4j
6. ✅ Intelligence products generate
7. ✅ Dashboard visualizations display (or show appropriate errors)
8. ✅ No critical errors in logs
9. ✅ End-to-end workflow completes

**Optional (Production):**
10. ✅ Kubernetes deployment works
11. ✅ CI/CD pipeline passes
12. ✅ Load tests meet SLAs
13. ✅ Monitoring dashboards functional
14. ✅ Backups running

---

**Classification:** UNCLASSIFIED//FOUO  
**Version:** 1.0.0  
**Last Updated:** 2025-10-02
