"""
Sentinel Intelligence Platform - Main API Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from api.routes import assets, intelligence, analysis, products
from utils.database import init_databases, close_databases

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("╔═══════════════════════════════════════════════════════╗")
    logger.info("║        SENTINEL INTELLIGENCE PLATFORM                 ║")
    logger.info("║        Classification: UNCLASSIFIED//FOUO             ║")
    logger.info("╚═══════════════════════════════════════════════════════╝")
    logger.info("Starting Sentinel API...")
    
    try:
        await init_databases()
        logger.info("✓ Database connections initialized")
        logger.info("✓ Sentinel API ready for operations")
    except Exception as e:
        logger.error(f"✗ Failed to initialize databases: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Sentinel API...")
    await close_databases()
    logger.info("✓ Database connections closed")
    logger.info("✓ Sentinel API shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Sentinel Intelligence Platform",
    description="Intelligence-driven security operations API applying IC methodology to cybersecurity",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(assets.router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(intelligence.router, prefix="/api/v1/intelligence", tags=["Intelligence"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Intelligence Products"])


@app.get("/")
async def root():
    """Root endpoint - System identification"""
    return {
        "system": "Sentinel Intelligence Platform",
        "classification": "UNCLASSIFIED//FOUO",
        "version": "0.1.0",
        "status": "operational",
        "description": "Intelligence-driven security operations platform",
        "api_docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # TODO: Add actual health checks for databases
    return {
        "status": "healthy",
        "classification": "UNCLASSIFIED",
        "services": {
            "api": "operational",
            "database": "operational",
            "cache": "operational",
            "queue": "operational"
        },
        "timestamp": "2025-10-01T21:08:11-04:00"
    }


@app.get("/api/v1/status")
async def system_status():
    """Detailed system status"""
    return {
        "classification": "UNCLASSIFIED//FOUO",
        "system": "Sentinel Intelligence Platform",
        "status": "operational",
        "components": {
            "asm_service": {"status": "standby", "description": "Attack Surface Management"},
            "osint_service": {"status": "standby", "description": "Open Source Intelligence"},
            "sigint_service": {"status": "standby", "description": "Signals Intelligence"},
            "cybint_service": {"status": "standby", "description": "Cyber Intelligence"},
            "fusion_engine": {"status": "standby", "description": "Multi-INT Fusion"},
            "analytics_engine": {"status": "standby", "description": "Intelligence Analytics"},
            "product_generator": {"status": "standby", "description": "Intelligence Products"}
        },
        "statistics": {
            "assets_monitored": 0,
            "threats_tracked": 0,
            "intelligence_reports": 0,
            "active_collections": 0
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
