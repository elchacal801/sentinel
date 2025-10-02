"""
Entity data models for Sentinel Intelligence Platform
These models represent entities in the knowledge graph and API responses
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


# Enums
class AssetType(str, Enum):
    """Asset types in the knowledge graph"""
    DOMAIN = "domain"
    SUBDOMAIN = "subdomain"
    IP_ADDRESS = "ip"
    SERVICE = "service"
    CLOUD_RESOURCE = "cloud_resource"
    CERTIFICATE = "certificate"


class CriticalityLevel(str, Enum):
    """Asset criticality levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class AssetStatus(str, Enum):
    """Asset operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class IntelSourceType(str, Enum):
    """Intelligence source types (Multi-INT)"""
    OSINT = "osint"
    SIGINT = "sigint"
    CYBINT = "cybint"
    GEOINT = "geoint"
    HUMINT = "humint"


class IOCType(str, Enum):
    """Indicator of Compromise types"""
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH_MD5 = "hash_md5"
    HASH_SHA1 = "hash_sha1"
    HASH_SHA256 = "hash_sha256"
    EMAIL = "email"
    MUTEX = "mutex"
    REGISTRY_KEY = "registry_key"


# Asset Models
class AssetBase(BaseModel):
    """Base asset model"""
    type: AssetType
    value: str
    criticality: CriticalityLevel = CriticalityLevel.UNKNOWN
    status: AssetStatus = AssetStatus.UNKNOWN
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class AssetCreate(AssetBase):
    """Asset creation request"""
    pass


class Asset(AssetBase):
    """Complete asset model"""
    id: str
    discovered: datetime
    last_seen: datetime
    first_seen: Optional[datetime] = None
    ports: List[int] = []
    services: List[str] = []
    technologies: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "asset-123",
                "type": "subdomain",
                "value": "api.example.com",
                "criticality": "high",
                "status": "active",
                "discovered": "2025-10-01T00:00:00Z",
                "last_seen": "2025-10-01T22:00:00Z",
                "ports": [80, 443, 8080],
                "services": ["http", "https"],
                "technologies": ["nginx", "python"],
                "tags": ["production", "api"],
            }
        }


class AssetResponse(BaseModel):
    """API response wrapper for assets"""
    classification: str = "UNCLASSIFIED"
    asset: Asset
    vulnerabilities_count: int = 0
    threats_count: int = 0


# Vulnerability Models
class Vulnerability(BaseModel):
    """Vulnerability/CVE model"""
    id: str  # CVE-ID or custom ID
    title: str
    description: str
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    severity: str  # critical, high, medium, low
    cwe_id: Optional[str] = None
    published_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    exploit_available: bool = False
    exploit_maturity: Optional[str] = None
    patch_available: bool = False
    affected_products: List[str] = []
    references: List[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "CVE-2024-12345",
                "title": "Remote Code Execution in Example Software",
                "description": "A critical vulnerability allowing...",
                "cvss_score": 9.8,
                "severity": "critical",
                "exploit_available": True,
                "patch_available": False,
            }
        }


# IOC Models
class IOC(BaseModel):
    """Indicator of Compromise model"""
    id: str
    type: IOCType
    value: str
    first_seen: datetime
    last_seen: datetime
    confidence: float = Field(ge=0.0, le=1.0)
    sources: List[str] = []
    tags: List[str] = []
    threat_actor: Optional[str] = None
    malware_family: Optional[str] = None
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v


# Threat Actor Models
class ThreatActor(BaseModel):
    """Threat actor/APT group model"""
    id: str
    name: str
    aliases: List[str] = []
    country: Optional[str] = None
    motivation: Optional[str] = None  # espionage, financial, destructive
    sophistication: Optional[str] = None  # low, medium, high, advanced
    first_observed: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    ttps: List[str] = []  # MITRE ATT&CK technique IDs
    target_industries: List[str] = []
    target_countries: List[str] = []
    tools: List[str] = []
    infrastructure: List[str] = []


# Intelligence Report Models
class IntelligenceReport(BaseModel):
    """Intelligence collection report"""
    id: str
    source_type: IntelSourceType
    classification: str = "UNCLASSIFIED"
    title: str
    summary: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime
    collectors: List[str] = []
    indicators: List[str] = []  # IOC IDs
    entities: List[str] = []  # Related entity IDs
    raw_data: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v


# Discovery/Scan Models
class ScanRequest(BaseModel):
    """Request to initiate a scan"""
    target: str
    scan_type: str = "passive"  # passive, active, comprehensive
    options: Dict[str, Any] = {}


class ScanResult(BaseModel):
    """Scan result"""
    scan_id: str
    target: str
    status: str  # initiated, running, completed, failed
    started_at: datetime
    completed_at: Optional[datetime] = None
    assets_discovered: int = 0
    results: Dict[str, Any] = {}


# Risk Scoring Models
class RiskScore(BaseModel):
    """Risk score for an entity"""
    entity_id: str
    entity_type: str
    risk_score: float = Field(ge=0.0, le=10.0)
    severity: str  # critical, high, medium, low
    factors: Dict[str, Any]
    confidence: float = Field(ge=0.0, le=1.0)
    calculated_at: datetime
    recommendation: Optional[str] = None
    
    @validator('risk_score')
    def validate_risk_score(cls, v):
        if not 0.0 <= v <= 10.0:
            raise ValueError('Risk score must be between 0.0 and 10.0')
        return v
