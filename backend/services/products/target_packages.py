"""
Target Package Generator

Generates comprehensive intelligence packages on specific targets:
- Asset profiles
- Vulnerability analysis
- Threat assessments
- Attack surface mapping
- Risk analysis
- Recommendations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


class TargetPackageGenerator:
    """
    Generates comprehensive target intelligence packages
    
    Follows IC standards for target analysis and packaging
    """
    
    def __init__(self):
        self.logger = logger
    
    async def generate_target_package(
        self,
        target_asset: Dict[str, Any],
        related_assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        attack_paths: Optional[List[Dict[str, Any]]] = None,
        risk_assessment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive target package
        
        Args:
            target_asset: Primary target asset
            related_assets: Related/connected assets
            vulnerabilities: Vulnerability data
            threats: Threat intelligence
            attack_paths: Attack path analysis
            risk_assessment: Risk assessment data
        
        Returns:
            Formatted target package
        """
        # Executive summary
        exec_summary = self._generate_executive_summary(
            target_asset, vulnerabilities, threats, risk_assessment
        )
        
        # Target profile
        target_profile = self._build_target_profile(target_asset, related_assets)
        
        # Vulnerability assessment
        vuln_assessment = self._analyze_vulnerabilities(vulnerabilities)
        
        # Threat assessment
        threat_assessment = self._analyze_threats(threats, target_asset)
        
        # Attack surface analysis
        attack_surface = self._analyze_attack_surface(
            target_asset, related_assets, vulnerabilities
        )
        
        # Attack paths
        attack_path_analysis = None
        if attack_paths:
            attack_path_analysis = self._analyze_attack_paths(attack_paths)
        
        # Risk analysis
        risk_analysis = self._analyze_risk(
            target_asset, vulnerabilities, threats, risk_assessment
        )
        
        # Defensive posture
        defensive_posture = self._assess_defensive_posture(target_asset, related_assets)
        
        # Recommendations
        recommendations = self._generate_recommendations(
            vuln_assessment, threat_assessment, risk_analysis, attack_path_analysis
        )
        
        return {
            "classification": "UNCLASSIFIED//FOUO",
            "product_type": "Target Intelligence Package",
            "target_id": target_asset.get("id"),
            "target_name": target_asset.get("value"),
            "generated_at": datetime.now().isoformat(),
            "executive_summary": exec_summary,
            "target_profile": target_profile,
            "vulnerability_assessment": vuln_assessment,
            "threat_assessment": threat_assessment,
            "attack_surface": attack_surface,
            "attack_paths": attack_path_analysis,
            "risk_analysis": risk_analysis,
            "defensive_posture": defensive_posture,
            "recommendations": recommendations,
            "confidence": "high"
        }
    
    def _generate_executive_summary(
        self,
        target_asset: Dict[str, Any],
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        risk_assessment: Optional[Dict[str, Any]]
    ) -> str:
        """Generate executive summary for target package"""
        parts = []
        
        asset_name = target_asset.get("value", "Unknown Asset")
        asset_type = target_asset.get("type", "asset")
        criticality = target_asset.get("criticality", "medium")
        
        # Opening statement
        parts.append(
            f"This intelligence package provides comprehensive analysis of {asset_name} "
            f"({asset_type}), assessed as {criticality.upper()} criticality."
        )
        
        # Vulnerability summary
        critical_vulns = len([v for v in vulnerabilities if v.get("severity") == "critical"])
        high_vulns = len([v for v in vulnerabilities if v.get("severity") == "high"])
        
        if critical_vulns > 0:
            parts.append(
                f"The target has {critical_vulns} critical and {high_vulns} high-severity "
                f"vulnerabilities requiring immediate attention."
            )
        elif high_vulns > 0:
            parts.append(
                f"The target has {high_vulns} high-severity vulnerabilities requiring remediation."
            )
        else:
            parts.append("No critical vulnerabilities identified at this time.")
        
        # Threat summary
        if threats:
            threat_actors = set(t.get("threat_actor") for t in threats if t.get("threat_actor"))
            if threat_actors:
                parts.append(
                    f"Threat intelligence indicates potential interest from {len(threat_actors)} "
                    f"threat actor(s)."
                )
        
        # Risk summary
        if risk_assessment:
            risk_score = risk_assessment.get("overall_risk", 0)
            if risk_score >= 9.0:
                parts.append("CRITICAL RISK: Immediate action required.")
            elif risk_score >= 7.0:
                parts.append("HIGH RISK: Urgent remediation recommended.")
        
        return " ".join(parts)
    
    def _build_target_profile(
        self,
        target_asset: Dict[str, Any],
        related_assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build comprehensive target profile"""
        return {
            "asset_id": target_asset.get("id"),
            "asset_name": target_asset.get("value"),
            "asset_type": target_asset.get("type"),
            "criticality": target_asset.get("criticality", "medium"),
            "status": target_asset.get("status", "active"),
            "discovered": target_asset.get("discovered"),
            "last_seen": target_asset.get("last_seen"),
            "tags": target_asset.get("tags", []),
            "properties": {
                "ports": target_asset.get("ports", []),
                "services": target_asset.get("services", []),
                "technologies": target_asset.get("technologies", []),
            },
            "exposure": self._assess_exposure(target_asset),
            "relationships": {
                "related_asset_count": len(related_assets),
                "related_assets": [
                    {
                        "id": a.get("id"),
                        "value": a.get("value"),
                        "type": a.get("type"),
                        "relationship": "connected"
                    }
                    for a in related_assets[:10]  # Top 10
                ]
            }
        }
    
    def _assess_exposure(self, asset: Dict[str, Any]) -> Dict[str, Any]:
        """Assess target exposure level"""
        tags = asset.get("tags", [])
        
        if "internet-facing" in tags or "public" in tags:
            level = "high"
            description = "Internet-facing asset with public exposure"
        elif "dmz" in tags:
            level = "medium"
            description = "DMZ asset with limited public exposure"
        elif "internal" in tags:
            level = "low"
            description = "Internal asset without direct internet exposure"
        else:
            level = "unknown"
            description = "Exposure level not determined"
        
        return {
            "level": level,
            "description": description,
            "public_ip": "internet-facing" in tags,
            "accessible_from": "internet" if "internet-facing" in tags else "internal"
        }
    
    def _analyze_vulnerabilities(
        self,
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze vulnerabilities for target"""
        if not vulnerabilities:
            return {
                "total": 0,
                "by_severity": {},
                "critical_findings": [],
                "summary": "No vulnerabilities identified"
            }
        
        # Count by severity
        by_severity = Counter(v.get("severity") for v in vulnerabilities)
        
        # Critical findings
        critical_findings = []
        for vuln in vulnerabilities:
            if vuln.get("severity") == "critical":
                critical_findings.append({
                    "cve_id": vuln.get("id"),
                    "title": vuln.get("title"),
                    "cvss_score": vuln.get("cvss_score"),
                    "exploit_available": vuln.get("exploit_available", False),
                    "patch_available": vuln.get("patch_available", False)
                })
        
        # Top CVEs by CVSS
        top_cves = sorted(
            vulnerabilities,
            key=lambda v: v.get("cvss_score", 0),
            reverse=True
        )[:10]
        
        return {
            "total": len(vulnerabilities),
            "by_severity": dict(by_severity),
            "critical_count": by_severity.get("critical", 0),
            "high_count": by_severity.get("high", 0),
            "medium_count": by_severity.get("medium", 0),
            "low_count": by_severity.get("low", 0),
            "critical_findings": critical_findings,
            "top_cves": [
                {
                    "cve_id": v.get("id"),
                    "cvss_score": v.get("cvss_score"),
                    "severity": v.get("severity")
                }
                for v in top_cves
            ],
            "exploitable_count": len([v for v in vulnerabilities if v.get("exploit_available")]),
            "patchable_count": len([v for v in vulnerabilities if v.get("patch_available")]),
            "summary": f"{len(vulnerabilities)} total vulnerabilities, {by_severity.get('critical', 0)} critical"
        }
    
    def _analyze_threats(
        self,
        threats: List[Dict[str, Any]],
        target_asset: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze threat intelligence for target"""
        if not threats:
            return {
                "total": 0,
                "threat_level": "low",
                "summary": "No specific threats identified"
            }
        
        # Threat actors
        threat_actors = [t.get("threat_actor") for t in threats if t.get("threat_actor")]
        actor_counts = Counter(threat_actors)
        
        # Malware families
        malware = [t.get("malware_family") for t in threats if t.get("malware_family")]
        malware_counts = Counter(malware)
        
        # Active exploitation
        active_count = len([t for t in threats if t.get("active_exploitation")])
        
        # Targeted threats
        targeted = [
            t for t in threats
            if t.get("targeting_organization") or t.get("targeting_industry")
        ]
        
        # Determine threat level
        if len(targeted) > 0 and active_count > 0:
            threat_level = "critical"
        elif active_count > 5:
            threat_level = "high"
        elif active_count > 0:
            threat_level = "elevated"
        else:
            threat_level = "moderate"
        
        return {
            "total": len(threats),
            "threat_level": threat_level,
            "active_exploitation_count": active_count,
            "targeted_threat_count": len(targeted),
            "threat_actors": [
                {"name": actor, "mentions": count}
                for actor, count in actor_counts.most_common(10)
            ],
            "malware_families": [
                {"family": mal, "mentions": count}
                for mal, count in malware_counts.most_common(10)
            ],
            "targeting_indicators": [
                {
                    "threat_actor": t.get("threat_actor"),
                    "targeting_type": "organization" if t.get("targeting_organization") else "industry",
                    "observed_at": t.get("observed_at")
                }
                for t in targeted[:5]
            ],
            "summary": f"Threat level: {threat_level.upper()}, {active_count} active exploitation indicators"
        }
    
    def _analyze_attack_surface(
        self,
        target_asset: Dict[str, Any],
        related_assets: List[Dict[str, Any]],
        vulnerabilities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze attack surface"""
        # Exposed services
        services = target_asset.get("services", [])
        ports = target_asset.get("ports", [])
        
        # Technology stack
        technologies = target_asset.get("technologies", [])
        
        # Entry points
        entry_points = []
        if "internet-facing" in target_asset.get("tags", []):
            entry_points.append("Direct internet access")
        if services:
            entry_points.extend([f"Service: {s}" for s in services[:5]])
        if ports:
            entry_points.extend([f"Port: {p}" for p in ports[:5]])
        
        # Vulnerability exposure
        vuln_exposure = {
            "vulnerable_services": [],
            "vulnerable_components": []
        }
        
        for vuln in vulnerabilities:
            if vuln.get("affected_service"):
                vuln_exposure["vulnerable_services"].append(vuln["affected_service"])
            if vuln.get("affected_component"):
                vuln_exposure["vulnerable_components"].append(vuln["affected_component"])
        
        return {
            "exposed_services": services,
            "open_ports": ports,
            "technologies": technologies,
            "entry_points": entry_points[:10],
            "attack_vectors": self._identify_attack_vectors(target_asset, vulnerabilities),
            "vulnerability_exposure": vuln_exposure,
            "related_assets": len(related_assets),
            "summary": f"{len(entry_points)} potential entry points identified"
        }
    
    def _identify_attack_vectors(
        self,
        asset: Dict[str, Any],
        vulnerabilities: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify potential attack vectors"""
        vectors = []
        
        if "internet-facing" in asset.get("tags", []):
            vectors.append("External network access")
        
        if vulnerabilities:
            vectors.append("Vulnerability exploitation")
        
        services = asset.get("services", [])
        if "web" in str(services).lower() or "http" in str(services).lower():
            vectors.append("Web application attacks")
        
        if "ssh" in str(services).lower():
            vectors.append("SSH brute force")
        
        if "database" in str(asset.get("type", "")).lower():
            vectors.append("SQL injection / data exfiltration")
        
        return vectors
    
    def _analyze_attack_paths(
        self,
        attack_paths: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze attack paths to target"""
        if not attack_paths:
            return None
        
        # High-risk paths
        high_risk_paths = [
            p for p in attack_paths
            if p.get("overall_risk", 0) >= 7.0
        ]
        
        # Most likely path
        most_likely = max(attack_paths, key=lambda p: p.get("likelihood", 0))
        
        # Least detectable path
        least_detectable = min(attack_paths, key=lambda p: p.get("detectability", 1))
        
        return {
            "total_paths": len(attack_paths),
            "high_risk_paths": len(high_risk_paths),
            "most_likely_path": {
                "likelihood": most_likely.get("likelihood"),
                "path_length": most_likely.get("path_length"),
                "difficulty": most_likely.get("difficulty")
            },
            "least_detectable_path": {
                "detectability": least_detectable.get("detectability"),
                "path_length": least_detectable.get("path_length"),
                "likelihood": least_detectable.get("likelihood")
            },
            "average_likelihood": sum(p.get("likelihood", 0) for p in attack_paths) / len(attack_paths),
            "average_detectability": sum(p.get("detectability", 0) for p in attack_paths) / len(attack_paths),
            "summary": f"{len(high_risk_paths)} high-risk attack paths identified"
        }
    
    def _analyze_risk(
        self,
        target_asset: Dict[str, Any],
        vulnerabilities: List[Dict[str, Any]],
        threats: List[Dict[str, Any]],
        risk_assessment: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Comprehensive risk analysis"""
        # Use provided risk assessment if available
        if risk_assessment:
            base_risk = risk_assessment.get("overall_risk", 5.0)
            severity = risk_assessment.get("severity", "medium")
        else:
            # Calculate basic risk
            vuln_risk = len([v for v in vulnerabilities if v.get("severity") in ["critical", "high"]]) * 0.5
            threat_risk = len([t for t in threats if t.get("active_exploitation")]) * 1.0
            base_risk = min(10.0, vuln_risk + threat_risk + 3.0)
            
            if base_risk >= 9.0:
                severity = "critical"
            elif base_risk >= 7.0:
                severity = "high"
            elif base_risk >= 4.0:
                severity = "medium"
            else:
                severity = "low"
        
        # Risk factors
        risk_factors = []
        
        criticality = target_asset.get("criticality")
        if criticality in ["critical", "high"]:
            risk_factors.append(f"{criticality.capitalize()} asset criticality")
        
        if "internet-facing" in target_asset.get("tags", []):
            risk_factors.append("Internet exposure")
        
        critical_vulns = len([v for v in vulnerabilities if v.get("severity") == "critical"])
        if critical_vulns > 0:
            risk_factors.append(f"{critical_vulns} critical vulnerabilities")
        
        active_threats = len([t for t in threats if t.get("active_exploitation")])
        if active_threats > 0:
            risk_factors.append(f"{active_threats} active exploitation indicators")
        
        return {
            "overall_risk_score": round(base_risk, 2),
            "severity": severity,
            "risk_factors": risk_factors,
            "confidence": "high",
            "assessment": self._risk_assessment_text(base_risk, severity),
            "timeline": self._risk_timeline(severity)
        }
    
    def _risk_assessment_text(self, risk_score: float, severity: str) -> str:
        """Generate risk assessment text"""
        if severity == "critical":
            return f"CRITICAL RISK (Score: {risk_score:.1f}): Immediate compromise highly probable without urgent intervention"
        elif severity == "high":
            return f"HIGH RISK (Score: {risk_score:.1f}): Significant exploitation risk requiring urgent remediation"
        elif severity == "medium":
            return f"MODERATE RISK (Score: {risk_score:.1f}): Exploitation possible with prioritized remediation recommended"
        else:
            return f"LOW RISK (Score: {risk_score:.1f}): Limited immediate risk with routine maintenance recommended"
    
    def _risk_timeline(self, severity: str) -> str:
        """Determine risk timeline"""
        timelines = {
            "critical": "Immediate action required (0-24 hours)",
            "high": "Urgent action required (24-72 hours)",
            "medium": "Priority action required (1-2 weeks)",
            "low": "Routine maintenance (30 days)"
        }
        return timelines.get(severity, "Unknown")
    
    def _assess_defensive_posture(
        self,
        target_asset: Dict[str, Any],
        related_assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess defensive posture"""
        tags = target_asset.get("tags", [])
        
        # Check for security controls
        controls = []
        if "waf" in tags or "firewall" in tags:
            controls.append("Web Application Firewall / Firewall")
        if "mfa" in tags or "2fa" in tags:
            controls.append("Multi-Factor Authentication")
        if "edr" in tags or "ids" in tags:
            controls.append("Endpoint Detection / Intrusion Detection")
        if "monitored" in tags:
            controls.append("Active Monitoring")
        if "logged" in tags:
            controls.append("Logging Enabled")
        
        # Defensive posture rating
        control_count = len(controls)
        if control_count >= 4:
            posture = "strong"
        elif control_count >= 2:
            posture = "moderate"
        else:
            posture = "weak"
        
        return {
            "posture_rating": posture,
            "security_controls": controls,
            "control_count": control_count,
            "gaps": self._identify_defensive_gaps(target_asset, controls),
            "recommendations": self._defensive_recommendations(posture, controls)
        }
    
    def _identify_defensive_gaps(
        self,
        asset: Dict[str, Any],
        existing_controls: List[str]
    ) -> List[str]:
        """Identify defensive gaps"""
        gaps = []
        
        if "internet-facing" in asset.get("tags", []) and not any("firewall" in c.lower() for c in existing_controls):
            gaps.append("No perimeter firewall detected")
        
        if not any("monitoring" in c.lower() for c in existing_controls):
            gaps.append("No active monitoring detected")
        
        if not any("logging" in c.lower() for c in existing_controls):
            gaps.append("Logging not enabled")
        
        if not any("mfa" in c.lower() or "2fa" in c.lower() for c in existing_controls):
            gaps.append("No multi-factor authentication")
        
        return gaps
    
    def _defensive_recommendations(
        self,
        posture: str,
        controls: List[str]
    ) -> List[str]:
        """Generate defensive recommendations"""
        recommendations = []
        
        if posture == "weak":
            recommendations.append("Immediate implementation of baseline security controls required")
        
        if not any("monitoring" in c.lower() for c in controls):
            recommendations.append("Implement 24/7 monitoring and alerting")
        
        if not any("firewall" in c.lower() for c in controls):
            recommendations.append("Deploy firewall/WAF protection")
        
        recommendations.append("Regular security assessments and penetration testing")
        recommendations.append("Implement defense-in-depth strategy")
        
        return recommendations
    
    def _generate_recommendations(
        self,
        vuln_assessment: Dict[str, Any],
        threat_assessment: Dict[str, Any],
        risk_analysis: Dict[str, Any],
        attack_path_analysis: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Vulnerability-based recommendations
        if vuln_assessment.get("critical_count", 0) > 0:
            recommendations.append({
                "priority": "critical",
                "category": "vulnerability_management",
                "action": "Emergency Patching",
                "description": f"Patch {vuln_assessment['critical_count']} critical vulnerabilities immediately",
                "timeline": risk_analysis.get("timeline", "24-48 hours")
            })
        
        # Threat-based recommendations
        threat_level = threat_assessment.get("threat_level", "low")
        if threat_level in ["critical", "high"]:
            recommendations.append({
                "priority": "high",
                "category": "threat_response",
                "action": "Enhanced Threat Hunting",
                "description": "Conduct proactive threat hunting given elevated threat level",
                "timeline": "Immediate"
            })
        
        # Attack path recommendations
        if attack_path_analysis and attack_path_analysis.get("high_risk_paths", 0) > 0:
            recommendations.append({
                "priority": "high",
                "category": "network_security",
                "action": "Network Segmentation",
                "description": "Implement segmentation to disrupt high-risk attack paths",
                "timeline": "1-2 weeks"
            })
        
        # General recommendations
        recommendations.extend([
            {
                "priority": "medium",
                "category": "monitoring",
                "action": "Monitoring Enhancement",
                "description": "Enhance monitoring coverage for this critical asset",
                "timeline": "1 week"
            },
            {
                "priority": "medium",
                "category": "hardening",
                "action": "Asset Hardening",
                "description": "Apply security hardening guidelines and remove unnecessary services",
                "timeline": "2 weeks"
            }
        ])
        
        return recommendations
