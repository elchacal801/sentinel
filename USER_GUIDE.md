# Sentinel User Guide

**Classification:** UNCLASSIFIED//FOUO

Welcome to Sentinel - an intelligence-driven security operations platform. This guide will help you understand and use the platform effectively.

---

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Dashboard Navigation](#dashboard-navigation)
- [Intelligence Collection](#intelligence-collection)
- [Analysis & Analytics](#analysis--analytics)
- [Intelligence Products](#intelligence-products)
- [Visualizations](#visualizations)
- [Best Practices](#best-practices)
- [Common Workflows](#common-workflows)

---

## Overview

### What is Sentinel?

Sentinel is an intelligence platform that:
- **Discovers** your attack surface (subdomains, ports, services)
- **Collects** intelligence from multiple sources (OSINT, threat feeds)
- **Correlates** data in a knowledge graph
- **Analyzes** risks and attack paths
- **Generates** IC-standard intelligence products

### Key Concepts

**Attack Surface Management (ASM)**
- Discovers what assets you have exposed to the internet
- Identifies subdomains, open ports, running services

**Multi-INT Collection**
- OSINT: Open Source Intelligence (public data)
- CYBINT: Cyber Intelligence (vulnerabilities, CVEs)
- SIGINT: Signals Intelligence (network traffic patterns)

**Knowledge Graph**
- Neo4j database storing relationships between:
  - Assets (servers, domains)
  - Vulnerabilities (CVEs)
  - Threats (threat actors, campaigns)
  - Indicators of Compromise (IOCs)

**Intelligence Products**
- Current Intelligence: Daily threat briefings
- I&W Alerts: Tactical warnings for imminent threats
- Target Packages: Comprehensive asset intelligence
- Executive Briefings: Strategic assessments for leadership

---

## Getting Started

### Step 1: Access the Dashboard

```
URL: http://localhost:3000 (local)
      or https://yourdomain.com (production)
```

**Login:** (If authentication enabled)
- Username: admin
- Password: (set in .env)

### Step 2: Understand the Layout

**Home Page:**
- System status indicator
- Quick access links (API docs, Dashboard)
- Platform capabilities overview

**Dashboard (6 Tabs):**
1. Overview - Executive summary
2. Knowledge Graph - Relationship visualization
3. Attack Paths - Attack vector analysis
4. Threat Timeline - Chronological events
5. Risk Analysis - Asset risk assessment
6. Intel Products - Generate/view products

---

## Dashboard Navigation

### Tab 1: Overview

**Purpose:** High-level view of security posture

**What You See:**
- **Metrics Grid** - 8 key indicators:
  - Assets Monitored
  - Active Threats
  - Critical Vulnerabilities
  - Average Risk Score
  - Intelligence Sources
  - Graph Nodes
  - Active Collections
  - I&W Alerts

- **Mini Visualizations:**
  - Knowledge Graph preview
  - Risk Distribution overview
  - Recent Threat Activity (last 3 events)

**How to Use:**
- Review metrics for overall health
- Look for anomalies (sudden increases)
- Click on preview cards to go to full view

---

### Tab 2: Knowledge Graph

**Purpose:** Visualize relationships between entities

**What You See:**
- Interactive graph with colored nodes:
  - **Green** = Assets (servers, domains)
  - **Red** = Vulnerabilities (CVEs)
  - **Yellow** = Threats (threat actors)
  - **Purple** = IOCs (IPs, hashes)
- Lines connecting related entities

**How to Use:**
1. **Filter by Type:** Use dropdown to show only specific node types
2. **Search:** Find specific assets or CVEs
3. **Click Nodes:** View detailed information in side panel
4. **Zoom:** Use zoom controls for better view

**What It Tells You:**
- Which assets have which vulnerabilities
- Which threats target which vulnerabilities
- Relationships between different entities

---

### Tab 3: Attack Paths

**Purpose:** Understand how attackers could compromise your systems

**What You See:**
- **Ranked List:** Attack paths sorted by risk (0-10 scale)
- **Metrics per Path:**
  - Likelihood: Probability of success
  - Difficulty: Skill required
  - Detectability: Chance of detection
  - Impact: Potential damage

**How to Use:**
1. **Select Path:** Click on a path in the list
2. **View Flow:** See visual diagram of attack progression
3. **Read Recommendations:** Review mitigation steps
4. **Prioritize:** Focus on highest risk paths first

**Example Path:**
```
Internet → Web Server → App Server → Database
Risk: 9.3/10
Likelihood: 85%
Recommendations:
1. Implement network segmentation
2. Deploy WAF on web server
3. Enable MFA for database access
```

---

### Tab 4: Threat Timeline

**Purpose:** Track threat activity over time

**What You See:**
- Chronological list of threat events
- Severity indicators (Critical/High/Medium/Low)
- Event types:
  - Active Exploitation
  - New Vulnerabilities
  - Targeted Activity
  - Anomalies
  - Threat Intel

**How to Use:**
1. **Filter by Severity:** Show only Critical/High threats
2. **Review Events:** Read descriptions and details
3. **Check Timestamps:** See when threats emerged
4. **Identify Patterns:** Look for clustering or campaigns

**Event Information:**
- Timestamp (relative: "2h ago")
- Threat actor (if known)
- CVE ID (if applicable)
- Affected assets count

---

### Tab 5: Risk Analysis

**Purpose:** Assess risk across your asset portfolio

**What You See:**
- **Summary Cards:**
  - Critical Risk assets (9.0+)
  - High Risk assets (7.0-8.9)
  - Medium Risk assets (5.0-6.9)
  - Low Risk assets (<5.0)

- **Heatmap:** Color-coded grid of assets by category
  - Red = Critical
  - Orange = High
  - Yellow = Medium
  - Gray = Low

**How to Use:**
1. **Review Summary:** Check distribution of risk
2. **Click Assets:** Select asset in heatmap for details
3. **View Details Panel:**
   - Asset name and ID
   - Risk score
   - Criticality rating
   - Vulnerability counts

**Take Action:**
- Prioritize Critical/High risk assets
- Review vulnerabilities causing high scores
- Plan remediation efforts

---

### Tab 6: Intel Products

**Purpose:** Generate and view intelligence reports

**What You See:**
- **Generation Cards:** 4 product types
  - Current Intelligence
  - I&W Alerts
  - Target Package
  - Executive Briefing

- **Recent Products List:** Previously generated reports

**How to Use:**

**Generate Products:**
1. Click product type card
2. Wait for generation (usually <5 seconds)
3. View in JSON viewer or export

**View Recent Products:**
1. Click "View" on product in list
2. Read generated content
3. Click "Export" to save

---

## Intelligence Collection

### Running Collection Services

**From API:**
```bash
# Discover assets for a domain
curl -X POST http://localhost:8000/api/v1/assets/discover \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'

# Collect threat intelligence
curl -X POST http://localhost:8000/api/v1/intelligence/threats/collect

# Scan for vulnerabilities
curl -X POST http://localhost:8000/api/v1/vulnerabilities/scan
```

**From Command Line:**
```bash
cd backend

# Run ASM discovery
python -m services.asm.scanner

# Run OSINT collection
python -m services.osint.collector

# Run vulnerability scanning
python -m services.cybint.vuln_scanner

# Run threat collection
python -m services.cybint.threat_collector
```

### What Gets Collected

**ASM (Attack Surface Management):**
- Subdomains via Certificate Transparency logs
- Active DNS resolution
- Open ports (common ports: 21, 22, 80, 443, 3306, etc.)
- Service fingerprinting (HTTP headers, banners)

**OSINT (Open Source Intelligence):**
- Certificate Transparency (crt.sh)
- GitHub security advisories
- Public threat feeds (Abuse.ch)

**CYBINT (Cyber Intelligence):**
- Vulnerability detection
- CVE enrichment from NVD
- Security header analysis
- Technology stack identification

### Collection Frequency

**Recommended:**
- ASM: Daily
- OSINT: Every 6 hours
- CYBINT: Weekly
- Threat Intel: Daily

**Setup Automated Collection:**
```bash
# Add to crontab
crontab -e

# Run ASM daily at 2 AM
0 2 * * * cd /path/to/backend && python -m services.asm.scanner

# Run OSINT every 6 hours
0 */6 * * * cd /path/to/backend && python -m services.osint.collector

# Run threat intel daily at 3 AM
0 3 * * * cd /path/to/backend && python -m services.cybint.threat_collector
```

---

## Analysis & Analytics

### Risk Scoring

**How It Works:**
Sentinel calculates intelligence-informed risk scores (0-10) based on:
- Vulnerability severity (CVSS)
- Asset criticality
- Threat intelligence (active exploitation)
- Attack path analysis
- Historical context

**Trigger Risk Analysis:**
```bash
# Via API
curl -X POST http://localhost:8000/api/v1/analysis/risk-scores

# Check results
curl http://localhost:8000/api/v1/analysis/risk-scores
```

**Interpreting Scores:**
- **9.0-10.0:** Critical - Immediate action required
- **7.0-8.9:** High - Address within 24-48 hours
- **5.0-6.9:** Medium - Address within 1 week
- **0-4.9:** Low - Address in normal cycle

### Attack Path Modeling

**How It Works:**
Graph-based analysis finding potential attack chains from entry points to critical assets.

**Factors Analyzed:**
- Likelihood of success
- Difficulty (skill required)
- Detectability (chance of detection)
- Impact (damage potential)

**Trigger Analysis:**
```bash
curl -X POST http://localhost:8000/api/v1/analysis/attack-paths/generate
```

**What to Do:**
1. Review high-risk paths (7.0+)
2. Implement recommended mitigations
3. Re-run analysis to verify improvement

### Anomaly Detection

**How It Works:**
Statistical analysis detecting outliers and unusual patterns.

**What It Finds:**
- Unusual port activity
- Spike in vulnerabilities
- New threat actors
- Abnormal network behavior

**View Anomalies:**
```bash
curl http://localhost:8000/api/v1/analysis/anomalies
```

---

## Intelligence Products

### Current Intelligence Briefing

**Purpose:** Daily situation report on threat landscape

**Contains:**
- Key Judgments (IC-standard)
- Threat Landscape Summary
- New Developments
- Critical Findings
- Recommendations with timelines
- Executive Summary

**When to Use:**
- Daily morning briefing
- Security team standup
- Status reports to management

**Generate:**
```bash
# Via API
curl http://localhost:8000/api/v1/products/current-intelligence

# Via Dashboard
Dashboard → Intel Products → Click "Current Intelligence"
```

---

### Indications & Warning (I&W) Alerts

**Purpose:** Tactical warnings for imminent threats

**Alert Levels:**
- **RED (Critical):** Immediate action - Active exploitation
- **ORANGE (High):** 24-hour response - High-risk vulnerabilities
- **YELLOW (Medium):** 72-hour response - Suspicious activity
- **GREEN (Low):** Informational - General awareness

**Contains:**
- Alert Status (overall)
- Individual Alerts with:
  - Severity
  - Response time
  - Description
  - Affected assets
  - Recommended actions

**When to Use:**
- Real-time threat monitoring
- Incident response prioritization
- Security operations center (SOC)

**Generate:**
```bash
curl http://localhost:8000/api/v1/products/indications-warning
```

---

### Target Package

**Purpose:** Comprehensive intelligence on specific asset

**Contains:**
- Executive Summary
- Target Profile (asset details)
- Vulnerability Assessment
  - Critical vulnerabilities list
  - Exploitability analysis
- Threat Assessment
  - Known targeting
  - Threat actor interest
- Attack Surface Analysis
  - Exposed services
  - Entry points
- Attack Path Analysis
  - Possible attack chains
- Risk Analysis
  - Overall risk score
  - Business impact
- Defensive Posture
  - Current controls
  - Gaps
- Recommendations
  - Prioritized actions

**When to Use:**
- Pre-deployment security review
- Incident investigation
- Penetration test planning
- Executive risk briefings

**Generate:**
```bash
# Get asset ID first
curl http://localhost:8000/api/v1/assets/

# Generate package
curl -X POST http://localhost:8000/api/v1/products/target-package/ASSET_ID
```

---

### Executive Briefing

**Purpose:** Strategic assessment for leadership

**Contains:**
- Executive Summary (no technical jargon)
- Security Posture Assessment
  - Overall status: AT RISK / NEEDS IMPROVEMENT / ACCEPTABLE
- Critical Risks (top 5)
  - Business impact perspective
  - Financial exposure estimates
- Strategic Intelligence
  - Industry threats
  - Threat actor targeting
  - Emerging risks
- Business Impact Analysis
  - Revenue risk
  - Reputational risk
  - Operational risk
- Trend Analysis
  - Improving / Stable / Degrading
- Strategic Recommendations
  - High-level actions
  - ROI considerations
- Bottom Line Assessment

**When to Use:**
- Board presentations
- Executive leadership updates
- Budget justifications
- Strategic planning

**Generate:**
```bash
curl -X POST http://localhost:8000/api/v1/products/executive-briefing
```

---

## Visualizations

### Reading the Knowledge Graph

**Node Types:**
- **Circle = Entity**
- **Line = Relationship**

**Colors:**
- Green = Asset (your infrastructure)
- Red = Vulnerability (CVEs, weaknesses)
- Yellow = Threat (threat actors, campaigns)
- Purple = IOC (indicators of compromise)

**Relationships:**
- Asset → Vulnerability: "HAS_VULNERABILITY"
- Threat → Vulnerability: "EXPLOITS"
- Asset → Asset: "CONNECTS_TO"
- Threat → IOC: "USES"

**Analysis Tips:**
- Look for clusters (many vulnerabilities on one asset)
- Identify critical paths (threats → vulns → assets)
- Find isolated assets (may be unknown/shadow IT)

---

### Understanding Attack Path Diagrams

**Visual Elements:**
- **Red circle** = Entry point (e.g., Internet)
- **Gray circles** = Intermediate steps
- **Purple circle** = Target (e.g., Database)
- **Arrows** = Attack progression

**Metrics:**
- **Likelihood:** Higher = more probable
- **Difficulty:** Lower = easier to execute
- **Detectability:** Lower = harder to detect
- **Impact:** Higher = more damage

**Reading Example:**
```
Internet → Web Server → App Server → Database
  ↓           ↓              ↓             ↓
Entry      Exploit       Lateral      Crown
Point      CVE-2024-1   Movement     Jewels
```

---

### Interpreting the Threat Timeline

**Event Flow:**
- **Top = Most Recent**
- **Bottom = Oldest**
- Vertical line connects events chronologically

**Severity Indicators:**
- Red dot = Critical
- Orange dot = High
- Yellow dot = Medium
- Blue dot = Low

**What to Look For:**
- Clustering of events (campaign)
- Escalation patterns (low → high)
- Threat actor persistence
- Vulnerability windows

---

## Best Practices

### Daily Operations

**Morning Routine:**
1. Check Dashboard → Overview tab
2. Review metrics for anomalies
3. Generate Current Intelligence briefing
4. Check I&W alerts for Critical/High
5. Review Threat Timeline for overnight activity

**Weekly Review:**
1. Run full ASM scan
2. Generate Executive Briefing
3. Review attack paths
4. Update risk assessments
5. Plan remediation efforts

**Monthly Assessment:**
1. Comprehensive vulnerability scan
2. Update threat intelligence feeds
3. Review all Critical/High risk assets
4. Generate target packages for key assets
5. Present to leadership

---

### Prioritization Framework

**Use this order:**
1. **Critical I&W Alerts** - Handle immediately
2. **Critical Risk Assets** (9.0+) - Within 24 hours
3. **High-Risk Attack Paths** (7.0+) - Within 48 hours
4. **High Risk Assets** (7.0-8.9) - Within 1 week
5. **Active Exploitation** - Emergency response
6. **Everything Else** - Normal cycle

---

### Common Mistakes to Avoid

❌ **Ignoring "No Data" Errors**
- If dashboard shows errors, backend isn't running or no data collected
- Don't assume it's working - check and fix

❌ **Not Running Collection Services**
- Dashboard is only useful if you collect data
- Set up automated collection (cron jobs)

❌ **Focusing Only on CVSS Scores**
- Sentinel provides context (active exploitation, attack paths)
- Use intelligence-informed risk scores

❌ **Generating Products Without Data**
- Products need data from Neo4j to be useful
- Collect intelligence first, then generate products

❌ **Not Acting on I&W Alerts**
- Critical alerts require immediate response
- Have an incident response plan

---

## Common Workflows

### Workflow 1: Onboarding New Asset

**Goal:** Discover and assess a new domain

**Steps:**
1. **Trigger Discovery**
   ```bash
   curl -X POST http://localhost:8000/api/v1/assets/discover \
     -d '{"domain": "newdomain.com"}'
   ```

2. **Wait for Collection** (2-3 minutes)

3. **View in Graph**
   - Dashboard → Knowledge Graph
   - Search for "newdomain.com"

4. **Assess Risk**
   - Dashboard → Risk Analysis
   - Find asset in heatmap
   - Review risk score and vulnerabilities

5. **Generate Target Package**
   - Dashboard → Intel Products
   - Click "Target Package"
   - Select asset

6. **Review Recommendations**
   - Read target package
   - Prioritize actions
   - Assign remediation tasks

---

### Workflow 2: Responding to Critical Vulnerability

**Goal:** Assess impact of newly disclosed CVE

**Steps:**
1. **Check I&W Alerts**
   - Dashboard → Intel Products
   - Generate I&W Alerts
   - Look for CVE in alerts

2. **Search Knowledge Graph**
   - Dashboard → Knowledge Graph
   - Search for "CVE-2024-XXXX"
   - See which assets are affected

3. **Assess Attack Paths**
   - Dashboard → Attack Paths
   - Look for paths using this CVE
   - Check risk scores

4. **Generate Current Intel Brief**
   - Get full context on threat landscape
   - See if exploitation is active

5. **Take Action**
   - Prioritize affected assets
   - Apply patches immediately
   - Monitor for exploitation attempts

---

### Workflow 3: Monthly Executive Report

**Goal:** Brief leadership on security posture

**Steps:**
1. **Generate Executive Briefing**
   ```bash
   curl -X POST http://localhost:8000/api/v1/products/executive-briefing
   ```

2. **Capture Dashboard Screenshots**
   - Overview tab (metrics)
   - Risk Analysis (heatmap)
   - Attack Paths (top 3)

3. **Prepare Presentation**
   - Executive Summary
   - Key Metrics Trend
   - Top Risks
   - Recommendations
   - Budget/Resource Needs

4. **Present to Leadership**
   - Focus on business impact
   - Use simple language
   - Provide clear action items

---

## Getting Help

### Troubleshooting

**Dashboard Shows Errors:**
- Check backend API is running: `curl http://localhost:8000/api/v1/health`
- Check Neo4j is running: `docker ps | grep neo4j`
- Check logs for errors

**No Data in Visualizations:**
- Verify data in Neo4j: Visit http://localhost:7474
- Run collection services
- Wait for data to populate (2-3 minutes)

**Collection Services Fail:**
- Check Celery worker is running
- Check Redis is accessible
- Review Celery logs
- Verify network connectivity

### Resources

- **Documentation:** See README.md, DEPLOYMENT.md
- **API Docs:** http://localhost:8000/docs
- **Neo4j Browser:** http://localhost:7474
- **GitHub Issues:** Report bugs or request features

---

## Glossary

**ASM** - Attack Surface Management  
**CVSS** - Common Vulnerability Scoring System  
**CVE** - Common Vulnerabilities and Exposures  
**IC** - Intelligence Community  
**IOC** - Indicator of Compromise  
**I&W** - Indications & Warning  
**OSINT** - Open Source Intelligence  
**SIGINT** - Signals Intelligence  
**CYBINT** - Cyber Intelligence

---

**Classification:** UNCLASSIFIED//FOUO  
**Version:** 1.0.0  
**Last Updated:** 2025-10-02

---

**Need More Help?** See TESTING.md for detailed testing procedures and troubleshooting.
