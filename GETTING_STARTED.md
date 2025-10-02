# Getting Started with Sentinel

This guide will help you get Sentinel up and running on your local machine in under 10 minutes.

## Prerequisites

Before you begin, ensure you have:

- ✅ **Docker Desktop** installed and running
  - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
- ✅ **Python 3.11+** installed
  - Check: `python --version`
- ✅ **Node.js 20+** installed
  - Check: `node --version`

## Step-by-Step Setup

### 1. Start Infrastructure Services (2 minutes)

Open a terminal in the `sentinel` directory and run:

```bash
# Start all 8 database services
docker-compose up -d

# This will start:
# - PostgreSQL (port 5432)
# - Neo4j (ports 7474, 7687)
# - Redis (port 6379)
# - Elasticsearch (port 9200)
# - Kafka + Zookeeper (port 9092)
# - TimescaleDB (port 5433)
# - MinIO (ports 9000, 9001)
```

**Wait ~30 seconds** for all services to initialize.

Verify services are running:
```bash
docker-compose ps
```

All services should show as "Up (healthy)".

### 2. Start Backend API (1 minute)

Open a **new terminal** window:

```bash
cd backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the API server
python api/main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     ✓ Database connections initialized
INFO:     ✓ Sentinel API ready for operations
```

**Test it:** Open http://localhost:8000 in your browser

You should see:
```json
{
  "system": "Sentinel Intelligence Platform",
  "classification": "UNCLASSIFIED//FOUO",
  "version": "0.1.0",
  "status": "operational"
}
```

### 3. Start Frontend (2 minutes)

Open **another new terminal** window:

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

You should see:
```
✓ Ready in 2.5s
○ Local:   http://localhost:3000
```

**Open it:** Go to http://localhost:3000

You should see the Sentinel intelligence-themed dashboard! 🎉

## What You Should See

### Frontend (http://localhost:3000)
- Classification banner at top and bottom
- "SENTINEL" header in cyan
- System status showing "OPERATIONAL"
- Grid of intelligence services (ASM, OSINT, SIGINT, etc.)
- Dark theme with intelligence aesthetic

### Backend API Docs (http://localhost:8000/api/docs)
- Interactive Swagger documentation
- All API endpoints organized by category:
  - Assets
  - Intelligence
  - Analysis
  - Intelligence Products

### Neo4j Browser (http://localhost:7474)
- Login with: `neo4j` / `sentinel_dev_password`
- Empty graph (ready for data)

### MinIO Console (http://localhost:9001)
- Login with: `sentinel` / `sentinel_dev_password`
- S3-compatible object storage

## Next Steps

Now that everything is running, you can:

1. **Explore the API**
   - Visit http://localhost:8000/api/docs
   - Try the `/health` endpoint
   - Check `/api/v1/status` for system status

2. **Review the Architecture**
   - Open `README.md` for detailed documentation
   - Check `project_guide.md` for implementation details

3. **Start Development**
   - Backend code is in `backend/`
   - Frontend code is in `frontend/`
   - See `README.md` for development guidelines

## Troubleshooting

### Problem: Docker services won't start

**Solution:**
```bash
# Check if ports are in use
docker-compose down
docker-compose up -d

# Check logs
docker-compose logs
```

### Problem: Backend can't connect to databases

**Solution:**
```bash
# Verify databases are healthy
docker-compose ps

# Check environment variables
cat .env

# Ensure .env exists (copy from .env.example if needed)
cp .env.example .env
```

### Problem: Frontend shows errors

**Solution:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Problem: Port already in use

**Solution:**
```bash
# Find what's using the port (example: port 8000)
# Windows:
netstat -ano | findstr :8000

# Mac/Linux:
lsof -i :8000

# Kill the process or change the port in .env
```

## Quick Commands Reference

```bash
# Stop all services
docker-compose down

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart a specific service
docker-compose restart postgres

# Remove all data (fresh start)
docker-compose down -v
```

## Development Workflow

**Typical development session:**

```bash
# Terminal 1: Infrastructure
docker-compose up -d

# Terminal 2: Backend
cd backend
python api/main.py

# Terminal 3: Frontend
cd frontend
npm run dev

# Now code! Changes auto-reload.
```

## Success Checklist

After setup, you should have:

- ✅ 8 Docker containers running
- ✅ Backend API at http://localhost:8000
- ✅ Frontend UI at http://localhost:3000
- ✅ API docs at http://localhost:8000/api/docs
- ✅ Neo4j browser at http://localhost:7474

## What's Next?

Sentinel is currently in **Phase 1: Infrastructure Setup**.

The foundation is complete! Future phases will implement:
- Asset discovery and attack surface management
- Intelligence collection (OSINT, SIGINT, CYBINT)
- Knowledge graph correlation
- Risk scoring and analytics
- Intelligence product generation

Check `README.md` for the full roadmap.

---

**Need Help?**

- Check `README.md` for detailed documentation
- Review `project_guide.md` for architecture details
- Examine the code - it's well-commented!

**Ready to Start Developing?**

See `CONTRIBUTING.md` (coming soon) for development guidelines.

---

**Classification:** UNCLASSIFIED//FOUO

*Last Updated: 2025-10-01*
