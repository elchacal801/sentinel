"""
Intelligence-Informed Risk Scoring Engine

Calculates risk scores beyond CVSS by incorporating:
- Threat intelligence context
- Exploit availability
- Asset criticality
- Active targeting
- Environmental factors
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskFactors:
    """Factors that contribute to risk score"""
    cvss_score: float = 0.0
    threat_intel_factor: float = 1.0
    exploit_factor: float = 1.0
    asset_criticality_factor: float = 1.0
    exposure_factor: float = 1.0
    age_factor: float = 1.0
    active_targeting_factor: float = 1.0


class RiskScoringEngine:
    """
    Intelligence-informed risk scoring engine
    
    Goes beyond CVSS to provide contextual risk assessment
    """
    
    # Risk severity thresholds
    SEVERITY_THRESHOLDS = {
        "critical": 9.0,
        "high": 7.0,
        "medium": 4.0,
        "low": 0.0
    }
    
    # Asset criticality weights
    ASSET_CRITICALITY = {
        "critical": 1.5,   # Crown jewels (production DBs, auth servers)
        "high": 1.3,       # Important infrastructure
        "medium": 1.0,     # Standard systems
        "low": 0.7,        # Development/test systems
        "unknown": 1.0
    }
    
    # Exploit availability multipliers
    EXPLOIT_AVAILABILITY = {
        "weaponized": 2.0,      # Public exploit code available
        "poc": 1.5,             # Proof of concept exists
        "theoretical": 1.0,     # No known exploit
        "unknown": 1.2          # Assume moderate risk
    }
    
    # Threat intelligence multipliers
    THREAT_INTEL_WEIGHTS = {
        "active_exploitation": 2.5,   # Being exploited in the wild
        "targeted_campaign": 2.0,     # Part of targeted campaign
        "apt_linked": 1.8,           # Linked to APT activity
        "threat_mentioned": 1.3,     # Mentioned in threat intel
        "no_intel": 1.0              # No threat intelligence
    }
    
    def __init__(self):
        self.logger = logger
    
    def calculate_risk_score(
        self,
        asset: Dict[str, Any],
        vulnerability: Dict[str, Any],
        threat_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score for an asset/vulnerability pair
        
        Args:
            asset: Asset information
            vulnerability: Vulnerability details
            threat_context: Optional threat intelligence context
        
        Returns:
            Risk assessment with score, severity, and factors
        """
        factors = RiskFactors()
        
        # Base CVSS score
        factors.cvss_score = vulnerability.get("cvss_score", 0.0)
        
        # Asset criticality factor
        asset_criticality = asset.get("criticality", "medium")
        factors.asset_criticality_factor = self.ASSET_CRITICALITY.get(
            asset_criticality.lower(), 1.0
        )
        
        # Exploit availability factor
        exploit_status = vulnerability.get("exploit_status", "unknown")
        factors.exploit_factor = self.EXPLOIT_AVAILABILITY.get(
            exploit_status.lower(), 1.2
        )
        
        # Threat intelligence factor
        if threat_context:
            factors.threat_intel_factor = self._calculate_threat_factor(threat_context)
            factors.active_targeting_factor = self._calculate_targeting_factor(threat_context)
        
        # Exposure factor (internet-facing vs internal)
        factors.exposure_factor = self._calculate_exposure_factor(asset)
        
        # Age factor (newer vulns may be more dangerous due to lack of patches)
        factors.age_factor = self._calculate_age_factor(vulnerability)
        
        # Calculate final risk score
        risk_score = self._compute_final_score(factors)
        severity = self._get_severity(risk_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            risk_score, factors, vulnerability, threat_context
        )
        
        return {
            "risk_score": round(risk_score, 2),
            "severity": severity,
            "factors": {
                "cvss_base": factors.cvss_score,
                "asset_criticality": factors.asset_criticality_factor,
                "exploit_availability": factors.exploit_factor,
                "threat_intelligence": factors.threat_intel_factor,
                "exposure": factors.exposure_factor,
                "age": factors.age_factor,
                "active_targeting": factors.active_targeting_factor
            },
            "recommendations": recommendations,
            "priority": self._calculate_priority(risk_score, factors),
            "calculated_at": datetime.now().isoformat()
        }
    
    def _calculate_threat_factor(self, threat_context: Dict[str, Any]) -> float:
        """Calculate threat intelligence weight"""
        if threat_context.get("active_exploitation"):
            return self.THREAT_INTEL_WEIGHTS["active_exploitation"]
        elif threat_context.get("targeted_campaign"):
            return self.THREAT_INTEL_WEIGHTS["targeted_campaign"]
        elif threat_context.get("apt_linked"):
            return self.THREAT_INTEL_WEIGHTS["apt_linked"]
        elif threat_context.get("threat_mentions", 0) > 0:
            return self.THREAT_INTEL_WEIGHTS["threat_mentioned"]
        else:
            return self.THREAT_INTEL_WEIGHTS["no_intel"]
    
    def _calculate_targeting_factor(self, threat_context: Dict[str, Any]) -> float:
        """Calculate active targeting multiplier"""
        if threat_context.get("targeting_organization"):
            return 2.0  # Direct targeting of your organization
        elif threat_context.get("targeting_industry"):
            return 1.5  # Industry-wide targeting
        elif threat_context.get("targeting_region"):
            return 1.3  # Regional targeting
        else:
            return 1.0
    
    def _calculate_exposure_factor(self, asset: Dict[str, Any]) -> float:
        """Calculate exposure multiplier based on asset location"""
        tags = asset.get("tags", [])
        
        if "internet-facing" in tags or "public" in tags:
            return 1.5  # Higher risk for internet-exposed assets
        elif "dmz" in tags:
            return 1.3
        elif "internal" in tags:
            return 1.0
        else:
            return 1.2  # Assume moderate exposure if unknown
    
    def _calculate_age_factor(self, vulnerability: Dict[str, Any]) -> float:
        """Calculate age-based risk factor"""
        published = vulnerability.get("published_date")
        if not published:
            return 1.0
        
        try:
            if isinstance(published, str):
                pub_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
            else:
                pub_date = published
            
            age_days = (datetime.now() - pub_date.replace(tzinfo=None)).days
            
            if age_days < 7:
                return 1.4  # Very recent - limited patches available
            elif age_days < 30:
                return 1.2  # Recent - patches emerging
            elif age_days < 90:
                return 1.0  # Normal
            elif age_days < 365:
                return 0.9  # Older - more patches available
            else:
                return 0.8  # Old vulnerability
        except Exception as e:
            logger.warning(f"Error calculating age factor: {e}")
            return 1.0
    
    def _compute_final_score(self, factors: RiskFactors) -> float:
        """
        Compute final risk score from all factors
        
        Formula:
        Risk = CVSS × (Asset_Criticality) × (Exploit_Factor) × 
               (Threat_Intel) × (Exposure) × (Age) × (Targeting)
        
        Normalized to 0-10 scale
        """
        # Start with CVSS base
        score = factors.cvss_score
        
        # Apply multiplicative factors
        score *= factors.asset_criticality_factor
        score *= factors.exploit_factor
        score *= factors.threat_intel_factor
        score *= factors.exposure_factor
        score *= factors.age_factor
        score *= factors.active_targeting_factor
        
        # Cap at 10.0
        return min(score, 10.0)
    
    def _get_severity(self, risk_score: float) -> str:
        """Get severity label from risk score"""
        if risk_score >= self.SEVERITY_THRESHOLDS["critical"]:
            return "critical"
        elif risk_score >= self.SEVERITY_THRESHOLDS["high"]:
            return "high"
        elif risk_score >= self.SEVERITY_THRESHOLDS["medium"]:
            return "medium"
        else:
            return "low"
    
    def _calculate_priority(self, risk_score: float, factors: RiskFactors) -> str:
        """
        Calculate remediation priority
        
        Priority considers both risk score and specific high-impact factors
        """
        # Urgent if critical score OR active exploitation
        if risk_score >= 9.0 or factors.threat_intel_factor >= 2.5:
            return "urgent"
        elif risk_score >= 7.0:
            return "high"
        elif risk_score >= 4.0:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(
        self,
        risk_score: float,
        factors: RiskFactors,
        vulnerability: Dict[str, Any],
        threat_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations based on risk assessment"""
        recommendations = []
        
        # Critical/urgent recommendations
        if factors.threat_intel_factor >= 2.5:
            recommendations.append(
                "🚨 URGENT: Active exploitation detected - patch immediately"
            )
        
        if factors.active_targeting_factor >= 2.0:
            recommendations.append(
                "⚠️ WARNING: Your organization is being actively targeted"
            )
        
        # Exploit-based recommendations
        if factors.exploit_factor >= 2.0:
            recommendations.append(
                "Public exploit code available - prioritize patching"
            )
        elif factors.exploit_factor >= 1.5:
            recommendations.append(
                "Proof of concept exploit exists - monitor closely"
            )
        
        # Asset criticality recommendations
        if factors.asset_criticality_factor >= 1.5:
            recommendations.append(
                "Critical asset affected - consider emergency patching"
            )
        
        # Exposure recommendations
        if factors.exposure_factor >= 1.5:
            recommendations.append(
                "Internet-facing asset - consider firewall rules or WAF"
            )
        
        # Age-based recommendations
        if factors.age_factor >= 1.4:
            recommendations.append(
                "Recent vulnerability - patches may be limited"
            )
        
        # General recommendations based on severity
        if risk_score >= 9.0:
            recommendations.append("Patch within 24 hours")
        elif risk_score >= 7.0:
            recommendations.append("Patch within 7 days")
        elif risk_score >= 4.0:
            recommendations.append("Patch within 30 days")
        
        # Mitigation recommendations
        if vulnerability.get("patch_available"):
            recommendations.append("✅ Patch available - apply immediately")
        else:
            recommendations.append(
                "⚠️ No patch available - implement compensating controls"
            )
        
        return recommendations
    
    async def calculate_asset_risk_profile(
        self,
        asset: Dict[str, Any],
        vulnerabilities: List[Dict[str, Any]],
        threat_contexts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk profile for an asset
        
        Aggregates risk across all vulnerabilities
        """
        if not vulnerabilities:
            return {
                "asset_id": asset.get("id"),
                "overall_risk": 0.0,
                "severity": "none",
                "vulnerability_count": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0
            }
        
        # Calculate risk for each vulnerability
        risk_assessments = []
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for idx, vuln in enumerate(vulnerabilities):
            threat_ctx = None
            if threat_contexts and idx < len(threat_contexts):
                threat_ctx = threat_contexts[idx]
            
            assessment = self.calculate_risk_score(asset, vuln, threat_ctx)
            risk_assessments.append(assessment)
            
            severity = assessment["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate overall risk (weighted average with emphasis on high risks)
        risk_scores = [r["risk_score"] for r in risk_assessments]
        
        # Weight higher risks more heavily
        sorted_scores = sorted(risk_scores, reverse=True)
        if len(sorted_scores) >= 3:
            # Top 3 risks weighted more
            overall_risk = (
                sorted_scores[0] * 0.5 +
                sorted_scores[1] * 0.3 +
                sorted_scores[2] * 0.2
            )
        elif len(sorted_scores) == 2:
            overall_risk = (sorted_scores[0] * 0.6 + sorted_scores[1] * 0.4)
        else:
            overall_risk = sorted_scores[0]
        
        return {
            "asset_id": asset.get("id"),
            "asset_value": asset.get("value"),
            "overall_risk": round(overall_risk, 2),
            "severity": self._get_severity(overall_risk),
            "vulnerability_count": len(vulnerabilities),
            "critical_count": severity_counts["critical"],
            "high_count": severity_counts["high"],
            "medium_count": severity_counts["medium"],
            "low_count": severity_counts["low"],
            "top_risks": sorted(risk_assessments, key=lambda x: x["risk_score"], reverse=True)[:5],
            "urgent_actions_required": severity_counts["critical"] > 0 or any(
                r["priority"] == "urgent" for r in risk_assessments
            ),
            "calculated_at": datetime.now().isoformat()
        }
    
    async def calculate_organization_risk(
        self,
        asset_profiles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate organization-wide risk posture
        
        Aggregates risk across all assets
        """
        if not asset_profiles:
            return {
                "overall_risk": 0.0,
                "total_assets": 0,
                "total_vulnerabilities": 0,
                "risk_distribution": {}
            }
        
        total_vulns = sum(p["vulnerability_count"] for p in asset_profiles)
        
        # Count assets by risk severity
        risk_distribution = {
            "critical": len([p for p in asset_profiles if p["severity"] == "critical"]),
            "high": len([p for p in asset_profiles if p["severity"] == "high"]),
            "medium": len([p for p in asset_profiles if p["severity"] == "medium"]),
            "low": len([p for p in asset_profiles if p["severity"] == "low"]),
        }
        
        # Calculate organization risk (weighted average)
        if asset_profiles:
            org_risk = sum(p["overall_risk"] for p in asset_profiles) / len(asset_profiles)
        else:
            org_risk = 0.0
        
        # Get top risky assets
        top_risky_assets = sorted(
            asset_profiles,
            key=lambda x: x["overall_risk"],
            reverse=True
        )[:10]
        
        return {
            "overall_risk": round(org_risk, 2),
            "severity": self._get_severity(org_risk),
            "total_assets": len(asset_profiles),
            "total_vulnerabilities": total_vulns,
            "risk_distribution": risk_distribution,
            "critical_assets": risk_distribution["critical"],
            "high_risk_assets": risk_distribution["high"],
            "top_risky_assets": [
                {
                    "asset_id": a["asset_id"],
                    "asset_value": a["asset_value"],
                    "risk_score": a["overall_risk"],
                    "vulnerability_count": a["vulnerability_count"]
                }
                for a in top_risky_assets
            ],
            "urgent_actions_required": risk_distribution["critical"] > 0,
            "calculated_at": datetime.now().isoformat()
        }
