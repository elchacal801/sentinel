# SENTINEL INTELLIGENCE PLATFORM

**Classification:** UNCLASSIFIED//FOR OFFICIAL USE ONLY

---

## Executive Summary

**Sentinel** is an intelligence-driven security operations platform that applies Intelligence Community (IC) methodology to cybersecurity operations. It fuses attack surface management with multi-source intelligence collection and analysis to provide actionable intelligence products.

### Key Features

- 🎯 **Attack Surface Management** - Continuous discovery and monitoring of internet-facing assets
- 🔍 **Multi-INT Collection** - OSINT, SIGINT, CYBINT, GEOINT intelligence gathering
- 🧠 **Intelligence Fusion** - Neo4j-powered knowledge graph correlating disparate intelligence
- 📊 **Analytical Products** - Current intelligence, I&W alerts, target packages, executive briefings
- 🎲 **Predictive Risk Scoring** - Intelligence-informed risk assessment beyond CVSS
- 🗺️ **Attack Path Modeling** - Graph-based attack path discovery and likelihood scoring

---

## Current Status: Phase 3 Complete ✅

**Latest Release:** Phase 3 - Knowledge Graph & Fusion  
**Status:** Operational intelligence fusion with persistent graph storage  
**Last Updated:** 2025-10-01

**What's Working Now:**
- ✅ Subdomain discovery (passive + active methods)
- ✅ Port scanning and service fingerprinting
- ✅ Certificate Transparency log monitoring
- ✅ GitHub security advisory collection
- ✅ Vulnerability detection and CVE enrichment
- ✅ Async task execution with Celery
- ✅ **Neo4j knowledge graph persistence** ⬅️ NEW
- ✅ **Multi-INT correlation and fusion** ⬅️ NEW
- ✅ **IC-standard confidence scoring** ⬅️ NEW
- ✅ **Graph queries and visualization** ⬅️ NEW

**Try It:**
```bash
# Start services
docker-compose up -d

# Start API
cd backend && python api/main.py

# Start Celery worker (required for collection)
cd backend && celery -A workers.celery_app worker --loglevel=info

# Discover assets (stores in Neo4j automatically)
curl -X POST http://localhost:8000/api/v1/assets/discover \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "scan_type": "passive"}'

# Query discovered assets from graph
curl http://localhost:8000/api/v1/assets/

# Get graph statistics
curl http://localhost:8000/api/v1/analysis/graph/stats
```

---

## Table of Contents

- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Intelligence Operations](#intelligence-operations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)

---

## Architecture

Sentinel implements a microservices architecture mirroring the intelligence cycle:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Next.js    │  │   GraphQL    │  │   REST API   │      │
│  │     UI       │  │     API      │  │  (FastAPI)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Collection│  │  Fusion  │  │ Analysis │  │ Products │   │
│  │ Services │  │  Engine  │  │  Engine  │  │Generator │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                    MESSAGE LAYER                             │
│              ┌──────────────────────┐                       │
│              │   Apache Kafka       │                       │
│              │  Event Streaming     │                       │
│              └──────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                             │
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Neo4j   │  │PostgreSQL│  │   Redis  │  │  Elastic │   │
│  │  Graph   │  │   RDBMS  │  │  Cache   │  │  Search  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Python 3.11+** - Core language
- **FastAPI** - High-performance async API framework
- **Celery** - Distributed task queue for workers
- **SQLAlchemy** - ORM for relational databases
- **Neo4j** - Graph database for knowledge representation

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Animations
- **Recharts/D3.js** - Data visualizations

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **PostgreSQL** - Relational data storage
- **Neo4j** - Knowledge graph
- **Redis** - Caching and message broker
- **Elasticsearch** - Search and logging
- **Apache Kafka** - Event streaming
- **TimescaleDB** - Time-series data
- **MinIO** - S3-compatible object storage

---

## Quick Start

### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Git
- Python 3.11+ (for local backend development)
- Node.js 20+ (for local frontend development)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sentinel
```

### 2. Start Infrastructure Services

```bash
# Start all Docker services
docker-compose up -d

# Verify services are healthy
docker-compose ps

# View logs
docker-compose logs -f
```

**Services Started:**
- PostgreSQL: `localhost:5432`
- Neo4j: `localhost:7474` (HTTP), `localhost:7687` (Bolt)
- Redis: `localhost:6379`
- Elasticsearch: `localhost:9200`
- Kafka: `localhost:9092`
- TimescaleDB: `localhost:5433`
- MinIO: `localhost:9000` (API), `localhost:9001` (Console)

### 3. Start Backend API

```bash
cd backend

# Option 1: Using Poetry (recommended)
poetry install
poetry run python api/main.py

# Option 2: Using pip
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python api/main.py
```

Backend API will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/api/docs`

### 4. Start Celery Worker (NEW in Phase 2)

```bash
# In a new terminal, from backend directory
cd backend
celery -A workers.celery_app worker --loglevel=info
```

**Required for:** Asset discovery, port scanning, OSINT collection, vulnerability scanning

### 5. Start Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## Development Setup

### Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update credentials in `.env` for production deployments

3. Key environment variables:
   - `POSTGRES_PASSWORD` - PostgreSQL password
   - `NEO4J_PASSWORD` - Neo4j password
   - `SECRET_KEY` - Application secret key
   - `JWT_SECRET` - JWT signing secret

### Database Initialization

```bash
# PostgreSQL migrations (when implemented)
cd backend
alembic upgrade head

# Neo4j schema setup
# Access Neo4j Browser: http://localhost:7474
# Default credentials: neo4j/sentinel_dev_password
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Coverage report
pytest --cov=. --cov-report=html
```

---

## Project Structure

```
sentinel/
├── backend/                    # Python FastAPI backend
│   ├── api/                   # API layer
│   │   ├── main.py           # FastAPI application
│   │   └── routes/           # API endpoints
│   │       ├── assets.py     # Asset management (Neo4j queries) ✅
│   │       ├── intelligence.py # Intelligence collection routes
│   │       ├── analysis.py   # Analysis engine (graph viz) ✅
│   │       ├── products.py   # Intelligence products routes
│   │       └── tasks.py      # Task status endpoints ✅
│   ├── services/              # Intelligence services
│   │   ├── asm/              # Attack Surface Management ✅
│   │   │   ├── discovery.py  # Subdomain enumeration
│   │   │   └── scanner.py    # Port scanning, fingerprinting
│   │   ├── osint/            # OSINT Collection ✅
│   │   │   └── collectors.py # CT logs, GitHub advisories
│   │   ├── sigint/           # SIGINT Analysis (placeholder)
│   │   ├── cybint/           # CYBINT Scanning ✅
│   │   │   └── scanner.py    # Vuln detection, CVE enrichment
│   │   ├── fusion/           # Multi-INT Fusion ✅ NEW
│   │   │   └── correlator.py # Intelligence correlation, confidence scoring
│   │   ├── analytics/        # Analytics Engine (placeholder)
│   │   └── products/         # Product Generation (placeholder)
│   ├── workers/               # Celery workers ✅
│   │   ├── celery_app.py     # Celery configuration
│   │   └── tasks.py          # Async tasks (with Neo4j storage)
│   ├── models/                # Data models ✅
│   │   └── entities.py       # Pydantic models (Asset, Vuln, IOC, etc.)
│   ├── utils/                 # Utilities
│   │   ├── database.py       # Database connections ✅
│   │   └── graph.py          # Neo4j graph manager ✅
│   └── tests/                 # Test suite
├── frontend/                  # Next.js frontend
│   ├── app/                   # Next.js App Router
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Homepage
│   │   └── globals.css       # Global styles
│   ├── components/            # React components
│   ├── lib/                   # Utilities and helpers
│   └── public/                # Static assets
├── infrastructure/            # Infrastructure as Code
│   ├── kubernetes/           # K8s manifests
│   ├── terraform/            # Terraform configs
│   └── docker/               # Dockerfiles
├── docs/                      # Documentation
├── docker-compose.yml         # Local development services
├── .env.example              # Environment variables template
└── README.md                 # This file
```

---

## API Documentation

### Interactive API Docs

Once the backend is running, access:
- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

### Key Endpoints

#### Assets
- `GET /api/v1/assets` - List all assets
- `POST /api/v1/assets/discover` - Initiate asset discovery
- `GET /api/v1/assets/{id}` - Get asset details
- `GET /api/v1/assets/{id}/vulnerabilities` - Get asset vulnerabilities
- `GET /api/v1/assets/{id}/attack-paths` - Get attack paths

#### Intelligence
- `GET /api/v1/intelligence` - List intelligence reports
- `GET /api/v1/intelligence/osint` - OSINT reports
- `GET /api/v1/intelligence/sigint` - SIGINT reports
- `GET /api/v1/intelligence/cybint` - CYBINT reports
- `GET /api/v1/intelligence/iocs` - List IOCs
- `GET /api/v1/intelligence/threat-actors` - List threat actors

#### Analysis
- `GET /api/v1/analysis/risk-scores` - Get risk scores
- `POST /api/v1/analysis/attack-paths/generate` - Generate attack paths
- `GET /api/v1/analysis/predictions` - Predictive intelligence
- `GET /api/v1/analysis/graph/query` - Query knowledge graph

#### Products
- `GET /api/v1/products/current-intelligence` - Daily briefing
- `GET /api/v1/products/indications-warning` - I&W alerts
- `POST /api/v1/products/target-package/{asset_id}` - Generate target package
- `POST /api/v1/products/executive-briefing` - Generate executive briefing

#### Tasks (NEW in Phase 2)
- `GET /api/v1/tasks/{task_id}` - Check async task status
- `DELETE /api/v1/tasks/{task_id}` - Cancel running task

#### Graph & Fusion (NEW in Phase 3)
- `GET /api/v1/analysis/graph/visualize` - Get graph visualization data (nodes/edges)
- `GET /api/v1/analysis/graph/stats` - Knowledge graph statistics
- `GET /api/v1/assets/` - Now returns real data from Neo4j (with filtering)
- `GET /api/v1/assets/{id}` - Returns asset with vulnerabilities and threats from graph
- `GET /api/v1/assets/{id}/attack-paths` - Real graph traversal for attack paths

---

## Intelligence Operations

### Multi-INT Fusion (Phase 3)

Sentinel correlates intelligence from multiple sources using IC-standard methodologies:

**Correlation Types:**
- **IOC Correlation** - Groups same indicators across sources with confidence scoring
- **Vulnerability-Threat Correlation** - Links CVEs to active exploitation intelligence
- **Temporal Correlation** - Identifies events within time windows for campaign detection
- **Spatial Correlation** - Geographic clustering of entities and infrastructure
- **Campaign Identification** - Detects coordinated threat activity from patterns

**Confidence Scoring:**
- Follows Intelligence Community standards (High/Moderate/Low/Minimal)
- Multi-source corroboration increases confidence
- Source diversity adds weight (OSINT + SIGINT + CYBINT = higher confidence)
- Temporal decay accounts for intelligence age

**Example Fusion:**
```
Input: 
- OSINT: IOC "1.2.3.4" linked to APT99
- CYBINT: Same IP in vulnerability scan
- SIGINT: C2 beaconing detected from same IP

Output:
- Confidence: 0.92 (HIGH)
- Assessment: "Coordinated APT99 infrastructure"
- Recommendation: "Immediate blocking and investigation"
```

### Intelligence Cycle Implementation

Sentinel follows the six-phase intelligence cycle:

1. **Planning & Direction**
   - Define Priority Intelligence Requirements (PIRs)
   - Configure collection sources
   - Set collection schedules

2. **Collection**
   - OSINT: Dark web, paste sites, CT logs, GitHub advisories
   - SIGINT: Network traffic analysis, beaconing detection
   - CYBINT: Vulnerability scanning, exploit intelligence
   - GEOINT: Infrastructure mapping, cloud asset discovery

3. **Processing**
   - Data normalization and enrichment
   - Entity extraction
   - Deduplication and validation

4. **Analysis**
   - Multi-source correlation
   - Threat actor attribution
   - Attack path modeling
   - Predictive risk scoring

5. **Dissemination**
   - Current intelligence briefings
   - Indications & Warning (I&W) alerts
   - Target packages
   - Executive briefings

6. **Feedback**
   - Gap analysis
   - Collection adjustment
   - Model refinement

---

## Roadmap

### Phase 1: Infrastructure Setup ✅ COMPLETE
- [x] Project structure
- [x] Docker services (PostgreSQL, Neo4j, Redis, Elasticsearch, Kafka, TimescaleDB, MinIO)
- [x] FastAPI backend foundation
- [x] Next.js frontend foundation
- [x] API endpoint stubs
- [x] Intelligence-themed UI

### Phase 2: Core Collection ✅ COMPLETE
- [x] Attack Surface Management (ASM)
  - [x] Subdomain enumeration (passive CT logs + active DNS)
  - [x] Port scanning (async, concurrent)
  - [x] Service fingerprinting (HTTP, banner grabbing)
- [x] OSINT Collection
  - [x] Certificate Transparency logs (crt.sh integration)
  - [x] GitHub security advisories (API integration)
  - [x] Threat feed framework (Abuse.ch)
- [x] CYBINT Scanning
  - [x] Vulnerability detection engine
  - [x] CVE enrichment (NVD API)
  - [x] Security header analysis
- [x] Celery workers for async collection
- [x] Pydantic data models
- [x] Neo4j graph schema

### Phase 3: Knowledge Graph & Fusion ✅ COMPLETE
- [x] Neo4j schema implementation
- [x] Entity relationship mapping (assets, vulnerabilities, IPs)
- [x] Multi-INT correlation engine (IOC, vulnerability-threat, temporal, spatial)
- [x] Confidence scoring (IC-standard with high/moderate/low labels)
- [x] Temporal correlation (event clustering in time windows)
- [x] Campaign identification algorithms
- [x] Graph visualization endpoints
- [x] Workers persist to Neo4j automatically

### Phase 4: Analytics & Intelligence (Weeks 7-8)
- [ ] Risk scoring engine
- [ ] Attack path modeling
- [ ] Threat correlation
- [ ] Predictive analytics
- [ ] Anomaly detection

### Phase 5: Intelligence Products (Weeks 9-10)
- [ ] Current intelligence generator
- [ ] I&W alert system
- [ ] Target package generator
- [ ] Executive briefing generator
- [ ] PDF/PPTX export

### Phase 6: UI & Visualization (Weeks 11-12)
- [ ] Intelligence dashboard
- [ ] Knowledge graph visualization
- [ ] Attack path visualization
- [ ] Threat timeline
- [ ] Risk heatmap

### Phase 7: Production Readiness (Weeks 13-14)
- [ ] Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Security hardening

---

## Development Guidelines

### Code Style

**Python**
- Follow PEP 8
- Use Black for formatting
- Type hints required
- Docstrings for all public functions

**TypeScript/React**
- ESLint + Prettier
- Functional components with hooks
- TypeScript strict mode
- Component documentation

### Git Workflow

```bash
# Feature branches
git checkout -b feature/osint-collection

# Commits
git commit -m "feat: add certificate transparency log collection"

# Conventional commits:
# feat: new feature
# fix: bug fix
# docs: documentation
# style: formatting
# refactor: code restructuring
# test: adding tests
# chore: maintenance
```

### Testing Requirements

- Unit tests for all business logic
- Integration tests for API endpoints
- E2E tests for critical workflows
- Minimum 80% code coverage

---

## Security Considerations

### Data Protection
- All secrets in environment variables
- No hardcoded credentials
- Database credentials rotated regularly
- API keys stored in secure vault (production)

### Network Security
- Services isolated in Docker network
- API authentication required (production)
- Rate limiting on public endpoints
- HTTPS/TLS in production

### Intelligence Data
- Classification marking on all outputs
- Data retention policies
- Access control and audit logging
- Secure data deletion

---

## Troubleshooting

### Docker Services Not Starting

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>

# Clean restart
docker-compose down -v
docker-compose up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U sentinel

# Check Neo4j
docker-compose exec neo4j cypher-shell -u neo4j -p sentinel_dev_password "RETURN 1"

# Check Redis
docker-compose exec redis redis-cli ping
```

### Frontend Build Issues

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run dev
```

---

## Contributing

This is a portfolio/demonstration project. Contributions, suggestions, and feedback are welcome!

### Areas for Contribution
- Additional intelligence collection sources
- New analytical techniques
- UI/UX improvements
- Documentation
- Testing
- Performance optimization

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- Intelligence Community analytical tradecraft
- MITRE ATT&CK framework
- OWASP vulnerability standards
- Open source security community

---

## Contact

**Developer**: Diego Parra

**Project Status**: Active Development - Phase 1 Complete

**Classification**: UNCLASSIFIED//FOR OFFICIAL USE ONLY

---

## Disclaimer

This is a demonstration/portfolio project for educational purposes. It is not intended for operational intelligence collection without proper authorization, legal compliance, and ethical considerations. Always ensure compliance with applicable laws and regulations when collecting and analyzing data.

---

**Last Updated**: 2025-10-01

**Version**: 0.1.0 (Phase 1)
