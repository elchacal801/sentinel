"""
Database connection utilities for Sentinel
Manages connections to PostgreSQL, Neo4j, Redis, Elasticsearch, and TimescaleDB
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from neo4j import AsyncGraphDatabase
import redis.asyncio as redis
from elasticsearch import AsyncElasticsearch
import logging
import os

logger = logging.getLogger(__name__)

# Global database connection objects
postgres_engine = None
postgres_session_maker = None
neo4j_driver = None
redis_client = None
elasticsearch_client = None
timescaledb_engine = None


async def init_databases():
    """Initialize all database connections"""
    global postgres_engine, postgres_session_maker, neo4j_driver, redis_client, elasticsearch_client, timescaledb_engine
    
    try:
        # PostgreSQL - Main relational database
        postgres_url = os.getenv(
            "POSTGRES_URL",
            "postgresql+asyncpg://sentinel:sentinel_dev_password@localhost:5432/sentinel"
        )
        postgres_engine = create_async_engine(
            postgres_url,
            echo=False,
            pool_size=10,
            max_overflow=20
        )
        postgres_session_maker = sessionmaker(
            postgres_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("✓ PostgreSQL connection initialized")
        
        # Neo4j - Knowledge graph database
        neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD", "sentinel_dev_password")
        
        neo4j_driver = AsyncGraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )
        await neo4j_driver.verify_connectivity()
        logger.info("✓ Neo4j connection initialized")
        
        # Redis - Cache and task queue
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("✓ Redis connection initialized")
        
        # Elasticsearch - Search and logs
        es_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
        es_port = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
        elasticsearch_client = AsyncElasticsearch(
            [{"host": es_host, "port": es_port, "scheme": "http"}]
        )
        await elasticsearch_client.info()
        logger.info("✓ Elasticsearch connection initialized")
        
        # TimescaleDB - Time-series data
        timescale_url = os.getenv(
            "TIMESCALEDB_URL",
            "postgresql+asyncpg://sentinel:sentinel_dev_password@localhost:5433/sentinel_timeseries"
        )
        timescaledb_engine = create_async_engine(
            timescale_url,
            echo=False,
            pool_size=10,
            max_overflow=20
        )
        logger.info("✓ TimescaleDB connection initialized")
        
        logger.info("All database connections established successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        raise


async def close_databases():
    """Close all database connections"""
    global postgres_engine, neo4j_driver, redis_client, elasticsearch_client, timescaledb_engine
    
    try:
        if postgres_engine:
            await postgres_engine.dispose()
            logger.info("✓ PostgreSQL connection closed")
        
        if neo4j_driver:
            await neo4j_driver.close()
            logger.info("✓ Neo4j connection closed")
        
        if redis_client:
            await redis_client.close()
            logger.info("✓ Redis connection closed")
        
        if elasticsearch_client:
            await elasticsearch_client.close()
            logger.info("✓ Elasticsearch connection closed")
        
        if timescaledb_engine:
            await timescaledb_engine.dispose()
            logger.info("✓ TimescaleDB connection closed")
        
        logger.info("All database connections closed successfully")
        
    except Exception as e:
        logger.error(f"Error closing databases: {e}")


async def get_postgres_session():
    """Get PostgreSQL session (dependency injection)"""
    async with postgres_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_neo4j_session():
    """Get Neo4j session (dependency injection)"""
    async with neo4j_driver.session() as session:
        try:
            yield session
        finally:
            await session.close()


def get_redis():
    """Get Redis client"""
    return redis_client


def get_elasticsearch():
    """Get Elasticsearch client"""
    return elasticsearch_client


# Database health check functions
async def check_postgres_health():
    """Check PostgreSQL connection health"""
    try:
        async with postgres_session_maker() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL health check failed: {e}")
        return False


async def check_neo4j_health():
    """Check Neo4j connection health"""
    try:
        await neo4j_driver.verify_connectivity()
        return True
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        return False


async def check_redis_health():
    """Check Redis connection health"""
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False


async def check_elasticsearch_health():
    """Check Elasticsearch connection health"""
    try:
        await elasticsearch_client.cluster.health()
        return True
    except Exception as e:
        logger.error(f"Elasticsearch health check failed: {e}")
        return False


async def check_all_databases():
    """Check health of all database connections"""
    health_status = {
        "postgres": await check_postgres_health(),
        "neo4j": await check_neo4j_health(),
        "redis": await check_redis_health(),
        "elasticsearch": await check_elasticsearch_health()
    }
    return health_status
