"""
Attack Path Analysis

Analyzes potential attack paths in the knowledge graph and calculates:
- Attack likelihood
- Path difficulty
- Attacker skill required
- Detection probability
- Mitigation recommendations
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PathMetrics:
    """Metrics for an attack path"""
    likelihood: float  # 0-1: probability of successful exploitation
    difficulty: float  # 0-10: difficulty for attacker
    detectability: float  # 0-1: probability of detection
    impact: float  # 0-10: potential impact
    skill_required: str  # low, medium, high, expert
    time_estimate: str  # Time to exploit


class AttackPathAnalyzer:
    """
    Analyzes attack paths in the knowledge graph
    
    Calculates path feasibility, likelihood, and provides recommendations
    """
    
    # Relationship types and their exploitation difficulty
    RELATIONSHIP_DIFFICULTY = {
        "HAS_VULNERABILITY": 3.0,  # Exploiting vulnerabilities
        "ACCESSES": 2.0,           # Lateral movement
        "EXECUTES": 4.0,           # Code execution
        "CONTAINS": 1.0,           # Container relationships
        "PART_OF": 1.0,            # Hierarchical relationships
        "RESOLVES_TO": 2.0,        # Network relationships
        "TRUSTS": 5.0,             # Trust relationships (hard to abuse)
        "COMMUNICATES_WITH": 3.0,  # Network communication
    }
    
    # Vulnerability exploit difficulty
    EXPLOIT_DIFFICULTY = {
        "weaponized": 1.0,    # Easy - public exploits
        "poc": 3.0,           # Medium - PoC available
        "theoretical": 7.0,   # Hard - no known exploit
        "unknown": 5.0        # Moderate uncertainty
    }
    
    # Asset criticality impact
    ASSET_IMPACT = {
        "critical": 10.0,
        "high": 7.0,
        "medium": 5.0,
        "low": 3.0,
        "unknown": 5.0
    }
    
    def __init__(self):
        self.logger = logger
    
    def analyze_path(
        self,
        path: List[Dict[str, Any]],
        vulnerabilities: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single attack path
        
        Args:
            path: List of nodes in the attack path
            vulnerabilities: Associated vulnerabilities
        
        Returns:
            Path analysis with metrics and recommendations
        """
        if not path or len(path) < 2:
            return {
                "valid": False,
                "reason": "Path too short"
            }
        
        metrics = self._calculate_path_metrics(path, vulnerabilities)
        
        # Determine if path is viable
        viable = self._is_path_viable(metrics)
        
        # Generate recommendations
        recommendations = self._generate_path_recommendations(path, metrics, vulnerabilities)
        
        # Calculate overall risk
        path_risk = self._calculate_path_risk(metrics)
        
        return {
            "valid": True,
            "viable": viable,
            "path_length": len(path),
            "source": path[0].get("value", path[0].get("id")),
            "target": path[-1].get("value", path[-1].get("id")),
            "likelihood": round(metrics.likelihood, 3),
            "difficulty": round(metrics.difficulty, 2),
            "detectability": round(metrics.detectability, 3),
            "impact": round(metrics.impact, 2),
            "skill_required": metrics.skill_required,
            "estimated_time": metrics.time_estimate,
            "overall_risk": round(path_risk, 2),
            "risk_level": self._get_risk_level(path_risk),
            "nodes": [self._simplify_node(n) for n in path],
            "recommendations": recommendations,
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _calculate_path_metrics(
        self,
        path: List[Dict[str, Any]],
        vulnerabilities: Optional[List[Dict[str, Any]]]
    ) -> PathMetrics:
        """Calculate all metrics for the path"""
        
        # Calculate likelihood (probability of success at each step)
        likelihood = self._calculate_likelihood(path, vulnerabilities)
        
        # Calculate difficulty (skill/resources needed)
        difficulty = self._calculate_difficulty(path, vulnerabilities)
        
        # Calculate detectability (chance of being caught)
        detectability = self._calculate_detectability(path)
        
        # Calculate impact (damage if successful)
        impact = self._calculate_impact(path)
        
        # Determine skill level required
        skill_required = self._determine_skill_level(difficulty)
        
        # Estimate time to exploit
        time_estimate = self._estimate_exploitation_time(difficulty, len(path))
        
        return PathMetrics(
            likelihood=likelihood,
            difficulty=difficulty,
            detectability=detectability,
            impact=impact,
            skill_required=skill_required,
            time_estimate=time_estimate
        )
    
    def _calculate_likelihood(
        self,
        path: List[Dict[str, Any]],
        vulnerabilities: Optional[List[Dict[str, Any]]]
    ) -> float:
        """
        Calculate likelihood of successful exploitation
        
        Likelihood decreases with:
        - Path length (more steps = more chances to fail)
        - Exploit difficulty
        - Detection mechanisms
        """
        # Start with base likelihood
        base_likelihood = 0.9
        
        # Reduce for each step in the path
        path_length_factor = 0.95 ** (len(path) - 1)
        
        # Factor in exploit availability
        exploit_factor = 1.0
        if vulnerabilities:
            avg_exploit_difficulty = sum(
                self.EXPLOIT_DIFFICULTY.get(v.get("exploit_status", "unknown"), 5.0)
                for v in vulnerabilities
            ) / len(vulnerabilities)
            
            # Convert difficulty to likelihood (inverse relationship)
            exploit_factor = 1.0 - (avg_exploit_difficulty / 10.0)
        
        # Factor in security controls
        security_factor = self._assess_security_controls(path)
        
        # Calculate final likelihood
        likelihood = base_likelihood * path_length_factor * exploit_factor * security_factor
        
        return max(0.0, min(1.0, likelihood))
    
    def _calculate_difficulty(
        self,
        path: List[Dict[str, Any]],
        vulnerabilities: Optional[List[Dict[str, Any]]]
    ) -> float:
        """
        Calculate attack difficulty (0-10 scale)
        
        Higher difficulty means:
        - More skill required
        - More resources needed
        - More time required
        """
        # Base difficulty for path length
        path_difficulty = len(path) * 1.5
        
        # Add exploit difficulty
        exploit_difficulty = 0.0
        if vulnerabilities:
            exploit_difficulty = sum(
                self.EXPLOIT_DIFFICULTY.get(v.get("exploit_status", "unknown"), 5.0)
                for v in vulnerabilities
            ) / len(vulnerabilities)
        
        # Add relationship traversal difficulty
        # (would need relationship data from graph)
        traversal_difficulty = len(path) * 0.5
        
        total_difficulty = path_difficulty + exploit_difficulty + traversal_difficulty
        
        # Normalize to 0-10 scale
        return min(10.0, total_difficulty)
    
    def _calculate_detectability(self, path: List[Dict[str, Any]]) -> float:
        """
        Calculate probability of detection
        
        Higher detectability is better for defense
        """
        # Base detectability
        base_detect = 0.5
        
        # Increase detectability for longer paths (more activity = more noise)
        length_factor = min(0.3, len(path) * 0.05)
        
        # Check for monitoring indicators
        monitoring_factor = 0.0
        for node in path:
            tags = node.get("tags", [])
            if "monitored" in tags:
                monitoring_factor += 0.1
            if "logged" in tags:
                monitoring_factor += 0.05
        
        detectability = base_detect + length_factor + monitoring_factor
        
        return max(0.0, min(1.0, detectability))
    
    def _calculate_impact(self, path: List[Dict[str, Any]]) -> float:
        """
        Calculate potential impact if path is exploited
        
        Based on target asset criticality
        """
        if not path:
            return 0.0
        
        # Impact is primarily based on the target asset
        target = path[-1]
        criticality = target.get("criticality", "medium")
        
        base_impact = self.ASSET_IMPACT.get(criticality, 5.0)
        
        # Bonus impact if path reaches multiple critical assets
        critical_count = sum(1 for n in path if n.get("criticality") == "critical")
        bonus = min(2.0, critical_count * 0.5)
        
        return min(10.0, base_impact + bonus)
    
    def _assess_security_controls(self, path: List[Dict[str, Any]]) -> float:
        """Assess security controls along the path"""
        # Check for security controls in path
        controls = 0
        for node in path:
            tags = node.get("tags", [])
            if "waf" in tags or "firewall" in tags:
                controls += 1
            if "mfa" in tags or "2fa" in tags:
                controls += 1
            if "edr" in tags or "ids" in tags:
                controls += 1
        
        # More controls = lower likelihood
        control_factor = 0.9 ** controls
        return control_factor
    
    def _determine_skill_level(self, difficulty: float) -> str:
        """Determine skill level required based on difficulty"""
        if difficulty >= 8.0:
            return "expert"
        elif difficulty >= 6.0:
            return "high"
        elif difficulty >= 3.0:
            return "medium"
        else:
            return "low"
    
    def _estimate_exploitation_time(self, difficulty: float, path_length: int) -> str:
        """Estimate time required to exploit path"""
        # Base time on difficulty and path length
        hours = difficulty * path_length
        
        if hours < 1:
            return "< 1 hour"
        elif hours < 8:
            return f"{int(hours)} hours"
        elif hours < 40:
            return f"{int(hours/8)} days"
        elif hours < 160:
            return f"{int(hours/40)} weeks"
        else:
            return f"{int(hours/160)} months"
    
    def _is_path_viable(self, metrics: PathMetrics) -> bool:
        """Determine if path is realistically exploitable"""
        # Path is viable if:
        # - Likelihood is reasonable (> 0.1)
        # - Difficulty is not impossibly high (< 9.5)
        return metrics.likelihood > 0.1 and metrics.difficulty < 9.5
    
    def _calculate_path_risk(self, metrics: PathMetrics) -> float:
        """
        Calculate overall path risk
        
        Risk = Likelihood × Impact × (1 - Detectability)
        Scaled to 0-10
        """
        risk = metrics.likelihood * metrics.impact * (1 - metrics.detectability)
        return min(10.0, risk * 1.5)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level label"""
        if risk_score >= 7.0:
            return "critical"
        elif risk_score >= 5.0:
            return "high"
        elif risk_score >= 3.0:
            return "medium"
        else:
            return "low"
    
    def _simplify_node(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify node for output"""
        return {
            "id": node.get("id"),
            "type": node.get("type"),
            "value": node.get("value"),
            "criticality": node.get("criticality")
        }
    
    def _generate_path_recommendations(
        self,
        path: List[Dict[str, Any]],
        metrics: PathMetrics,
        vulnerabilities: Optional[List[Dict[str, Any]]]
    ) -> List[str]:
        """Generate mitigation recommendations for the path"""
        recommendations = []
        
        # High risk path recommendations
        if metrics.likelihood > 0.7:
            recommendations.append(
                "🚨 HIGH LIKELIHOOD: This attack path is highly exploitable - immediate action required"
            )
        
        if metrics.impact >= 8.0:
            recommendations.append(
                "⚠️ HIGH IMPACT: Target is critical asset - prioritize protection"
            )
        
        if metrics.detectability < 0.3:
            recommendations.append(
                "👁️ LOW DETECTABILITY: Implement monitoring and logging along this path"
            )
        
        # Vulnerability-specific recommendations
        if vulnerabilities:
            for vuln in vulnerabilities:
                if vuln.get("exploit_status") == "weaponized":
                    recommendations.append(
                        f"Patch {vuln.get('id', 'vulnerability')} immediately - public exploits available"
                    )
        
        # Path-specific recommendations
        if len(path) <= 2:
            recommendations.append(
                "Short attack path - implement defense in depth"
            )
        
        # Skill level recommendations
        if metrics.skill_required == "low":
            recommendations.append(
                "Low skill required - script kiddies could exploit this path"
            )
        
        # Detection recommendations
        recommendations.append(
            f"Estimated exploitation time: {metrics.time_estimate} - ensure detection within this window"
        )
        
        # General mitigations
        recommendations.append("Consider network segmentation to break attack path")
        recommendations.append("Implement principle of least privilege")
        
        return recommendations
    
    async def rank_attack_paths(
        self,
        paths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank multiple attack paths by risk
        
        Returns paths sorted by overall risk (highest first)
        """
        if not paths:
            return []
        
        # Sort by overall_risk descending
        ranked = sorted(
            paths,
            key=lambda p: p.get("overall_risk", 0.0),
            reverse=True
        )
        
        # Add rank numbers
        for idx, path in enumerate(ranked, 1):
            path["rank"] = idx
        
        return ranked
    
    async def identify_critical_nodes(
        self,
        paths: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify nodes that appear in multiple high-risk paths
        
        These are chokepoints that should be prioritized for hardening
        """
        node_frequency = {}
        node_total_risk = {}
        
        # Count node appearances in paths
        for path in paths:
            path_risk = path.get("overall_risk", 0.0)
            
            for node in path.get("nodes", []):
                node_id = node.get("id")
                if node_id:
                    node_frequency[node_id] = node_frequency.get(node_id, 0) + 1
                    node_total_risk[node_id] = node_total_risk.get(node_id, 0.0) + path_risk
        
        # Calculate criticality scores
        critical_nodes = []
        for node_id, frequency in node_frequency.items():
            if frequency > 1:  # Appears in multiple paths
                avg_risk = node_total_risk[node_id] / frequency
                criticality_score = frequency * avg_risk
                
                critical_nodes.append({
                    "node_id": node_id,
                    "frequency": frequency,
                    "average_risk": round(avg_risk, 2),
                    "criticality_score": round(criticality_score, 2),
                    "recommendation": f"Critical chokepoint - securing this node blocks {frequency} attack paths"
                })
        
        # Sort by criticality score
        return sorted(critical_nodes, key=lambda x: x["criticality_score"], reverse=True)
