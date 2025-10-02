# Sentinel Credentials & Configuration

**Classification:** UNCLASSIFIED//FOUO

Complete list of all credentials, API keys, and configuration needed for Sentinel Intelligence Platform.

---

## Table of Contents

- [Required Credentials](#required-credentials)
- [Optional API Keys](#optional-api-keys)
- [Security Best Practices](#security-best-practices)
- [Quick Setup](#quick-setup)

---

## Required Credentials

**These are REQUIRED for Sentinel to function:**

### 1. Neo4j Database

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-neo4j-password
```

**How to set:**
```bash
# Docker (default password: neo4j)
# Change on first login or use:
docker exec sentinel-neo4j neo4j-admin set-initial-password your-secure-neo4j-password

# Manual install:
neo4j-admin set-initial-password your-secure-neo4j-password
```

**Generate strong password:**
```bash
openssl rand -base64 32
```

---

### 2. Application Secrets

```bash
SECRET_KEY=your-secret-key-32-or-more-characters
JWT_SECRET=your-jwt-secret-32-or-more-characters
```

**How to generate:**
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET
openssl rand -hex 32

# Add to .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "JWT_SECRET=$(openssl rand -hex 32)" >> .env
```

**Purpose:**
- `SECRET_KEY`: Encrypts session data and sensitive information
- `JWT_SECRET`: Signs JWT tokens for authentication

---

### 3. Redis (Required for Celery)

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=  # Optional, leave empty for local dev
```

**For production with password:**
```bash
# Generate Redis password
REDIS_PASSWORD=$(openssl rand -base64 32)

# Update Redis URL
REDIS_URL=redis://:${REDIS_PASSWORD}@localhost:6379/0

# Configure Redis server
# Edit redis.conf:
requirepass your-redis-password
```

---

## Optional API Keys

**These enhance functionality but aren't required:**

### 1. GitHub Token (Recommended)

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Purpose:** Collect GitHub Security Advisories

**How to get:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `public_repo` (read public repositories)
   - `read:org` (read organization data)
4. Generate and copy token
5. Add to `.env`

**Free tier:** Yes  
**Rate limits:** 5,000 requests/hour (authenticated)

---

### 2. NVD API Key (Recommended)

```bash
NVD_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Purpose:** Enrich CVE data from National Vulnerability Database

**How to get:**
1. Go to https://nvd.nist.gov/developers/request-an-api-key
2. Fill out the form
3. Receive API key via email (usually within minutes)
4. Add to `.env`

**Free tier:** Yes  
**Rate limits:** 
- Without key: 5 requests / 30 seconds
- With key: 50 requests / 30 seconds

---

### 3. Shodan API Key (Optional)

```bash
SHODAN_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Purpose:** Internet-wide scanning and asset discovery

**How to get:**
1. Sign up at https://account.shodan.io/register
2. Go to https://account.shodan.io/
3. Copy API key from account page
4. Add to `.env`

**Free tier:** 100 API credits/month  
**Paid:** $59/month for more credits

---

### 4. VirusTotal API Key (Optional)

```bash
VIRUSTOTAL_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Purpose:** Malware analysis and threat intelligence

**How to get:**
1. Sign up at https://www.virustotal.com/gui/join-us
2. Go to your profile
3. Copy API key
4. Add to `.env`

**Free tier:** 4 requests/minute  
**Paid:** Premium for higher limits

---

### 5. Censys API (Optional)

```bash
CENSYS_API_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CENSYS_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Purpose:** Internet-wide asset discovery and analysis

**How to get:**
1. Sign up at https://censys.io/register
2. Go to Account → API
3. Copy API ID and Secret
4. Add to `.env`

**Free tier:** 250 queries/month

---

### 6. GreyNoise API Key (Optional)

```bash
GREYNOISE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Purpose:** Identify mass-scanning IPs (benign scanners vs threats)

**How to get:**
1. Sign up at https://www.greynoise.io/
2. Get API key from dashboard
3. Add to `.env`

**Free tier:** Limited queries

---

## Optional Database Credentials

### PostgreSQL (Optional - for logging/structured data)

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=sentinel
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_DB=sentinel
POSTGRES_URL=postgresql+asyncpg://sentinel:your-postgres-password@localhost:5432/sentinel
```

**Generate password:**
```bash
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env
```

---

### Elasticsearch (Optional - for log aggregation)

```bash
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=your-elastic-password
```

**Set password:**
```bash
# Docker Compose will auto-generate
# Or set manually:
docker exec sentinel-elasticsearch \
  elasticsearch-reset-password -u elastic -i
```

---

### TimescaleDB (Optional - for time-series data)

```bash
TIMESCALEDB_HOST=localhost
TIMESCALEDB_PORT=5433
TIMESCALEDB_USER=sentinel
TIMESCALEDB_PASSWORD=your-timescale-password
TIMESCALEDB_DB=sentinel_timeseries
TIMESCALEDB_URL=postgresql+asyncpg://sentinel:your-timescale-password@localhost:5433/sentinel_timeseries
```

---

## Optional Services

### Kafka (Optional - for streaming)

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPICS_OSINT=collection.osint
KAFKA_TOPICS_CYBINT=collection.cybint
```

**No authentication needed for local development**

---

### MinIO (Optional - for S3-compatible storage)

```bash
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=sentinel
MINIO_SECRET_KEY=your-minio-secret-key
MINIO_BUCKET=sentinel-artifacts
MINIO_SECURE=false
```

**Default credentials:** minioadmin / minioadmin (change in production)

---

### Notification Services (Optional)

**Slack:**
```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**How to get:**
1. Go to https://api.slack.com/messaging/webhooks
2. Create incoming webhook
3. Copy URL

**Email (SMTP):**
```bash
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email@gmail.com
EMAIL_SMTP_PASSWORD=your-app-password
EMAIL_FROM=sentinel@yourcompany.com
```

**Gmail App Password:**
1. Enable 2FA on Google account
2. Go to https://myaccount.google.com/apppasswords
3. Generate app password
4. Use that instead of regular password

---

## Security Best Practices

### 1. Use Strong Passwords

**Minimum requirements:**
- 32+ characters
- Random (use `openssl rand`)
- Unique per service
- Never commit to git

**Generate strong password:**
```bash
# 32-character random string
openssl rand -base64 32

# Hex format (64 characters)
openssl rand -hex 32
```

---

### 2. Never Commit Credentials

**Add to .gitignore:**
```bash
.env
.env.local
.env.production
*.key
*.pem
secrets/
```

**Verify not in git:**
```bash
git ls-files | grep .env
# Should return nothing
```

---

### 3. Use Environment-Specific Files

```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production

# Load appropriate file
source .env.production
```

---

### 4. Rotate Credentials Regularly

**Recommended schedule:**
- Development: Every 6 months
- Production: Every 90 days
- After security incident: Immediately

**Rotation script example:**
```bash
#!/bin/bash
# rotate_secrets.sh

# Generate new secrets
NEW_SECRET_KEY=$(openssl rand -hex 32)
NEW_JWT_SECRET=$(openssl rand -hex 32)

# Update .env
sed -i "s/SECRET_KEY=.*/SECRET_KEY=${NEW_SECRET_KEY}/" .env
sed -i "s/JWT_SECRET=.*/JWT_SECRET=${NEW_JWT_SECRET}/" .env

# Restart services
docker-compose restart backend
```

---

### 5. Use Secrets Management in Production

**Options:**

**Kubernetes Secrets:**
```bash
kubectl create secret generic sentinel-secrets \
  --from-literal=neo4j-password='your-password' \
  --from-literal=secret-key='your-secret-key' \
  -n sentinel
```

**HashiCorp Vault:**
```bash
vault kv put secret/sentinel \
  neo4j_password='your-password' \
  secret_key='your-secret-key'
```

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name sentinel/production \
  --secret-string '{"neo4j_password":"xxx","secret_key":"xxx"}'
```

---

## Quick Setup

### Minimum .env for Development

```bash
# Copy this to .env file

# === REQUIRED ===
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=sentinel-dev-password-change-in-production

REDIS_HOST=localhost
REDIS_PORT=6379

SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# === RECOMMENDED (Optional) ===
GITHUB_TOKEN=  # Add if you have it
NVD_API_KEY=   # Add if you have it

# === OPTIONAL ===
SHODAN_API_KEY=
VIRUSTOTAL_API_KEY=
```

---

### Complete .env for Production

```bash
# === DATABASE (REQUIRED) ===
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=$(openssl rand -base64 32)

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=$(openssl rand -base64 32)

POSTGRES_URL=postgresql+asyncpg://sentinel:$(openssl rand -base64 32)@postgres:5432/sentinel

# === SECURITY (REQUIRED) ===
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# === APPLICATION ===
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=INFO

# === API KEYS (RECOMMENDED) ===
GITHUB_TOKEN=your-github-token
NVD_API_KEY=your-nvd-api-key

# === API KEYS (OPTIONAL) ===
SHODAN_API_KEY=your-shodan-key
VIRUSTOTAL_API_KEY=your-virustotal-key
CENSYS_API_ID=your-censys-id
CENSYS_API_SECRET=your-censys-secret
GREYNOISE_API_KEY=your-greynoise-key

# === MONITORING ===
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# === NOTIFICATIONS (OPTIONAL) ===
SLACK_WEBHOOK_URL=your-slack-webhook
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_SMTP_USER=your-email
EMAIL_SMTP_PASSWORD=your-app-password
```

---

## Credential Checklist

Use this checklist when setting up:

### Development Setup
- [ ] Neo4j password set
- [ ] SECRET_KEY generated
- [ ] JWT_SECRET generated
- [ ] Redis accessible (no password needed)
- [ ] .env file created from .env.example
- [ ] .env added to .gitignore

### Production Setup
- [ ] All development items above
- [ ] Strong passwords (32+ characters) generated
- [ ] Redis password set
- [ ] PostgreSQL password set (if used)
- [ ] All secrets stored in secrets manager
- [ ] Kubernetes secrets created (if K8s)
- [ ] API keys added to .env
- [ ] Notifications configured
- [ ] SSL/TLS certificates obtained
- [ ] Firewall rules configured
- [ ] Backup credentials secured

### Optional Enhancements
- [ ] GitHub token added
- [ ] NVD API key added
- [ ] Shodan API key added (if purchased)
- [ ] VirusTotal API key added
- [ ] Censys credentials added
- [ ] GreyNoise API key added
- [ ] Slack webhook configured
- [ ] Email SMTP configured

---

## Troubleshooting

### Issue: Neo4j connection failed

**Error:** "Unable to connect to Neo4j"

**Check:**
```bash
# Verify Neo4j is running
docker ps | grep neo4j

# Test connection
docker exec sentinel-neo4j cypher-shell -u neo4j -p your-password "RETURN 1"

# Check .env
cat .env | grep NEO4J
```

**Fix:**
- Verify password matches
- Restart Neo4j: `docker restart sentinel-neo4j`
- Check URI format: `bolt://hostname:7687`

---

### Issue: Invalid JWT token

**Error:** "JWT signature verification failed"

**Cause:** JWT_SECRET changed but tokens still cached

**Fix:**
```bash
# Flush Redis cache
docker exec sentinel-redis redis-cli FLUSHALL

# Restart backend
docker-compose restart backend
```

---

### Issue: API rate limit exceeded

**Error:** "Rate limit exceeded" from external API

**Cause:** Using free tier without API key

**Fix:**
- Get API key from provider
- Add to .env
- Restart services: `docker-compose restart`

---

## Summary

**Absolute minimum to run Sentinel:**
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
REDIS_HOST=localhost
```

**Recommended for full functionality:**
- Add GitHub token (free)
- Add NVD API key (free)
- Consider Shodan ($59/month) for enhanced OSINT

**Production-ready:**
- All minimum + recommended
- Strong passwords (32+ characters)
- Secrets manager (Vault, K8s Secrets, AWS Secrets Manager)
- Regular rotation schedule
- Monitoring and alerting
- Backup credentials secured

---

**Classification:** UNCLASSIFIED//FOUO  
**Version:** 1.0.0  
**Last Updated:** 2025-10-02

**Related Documentation:**
- **QUICKSTART.md** - Step-by-step setup guide
- **DEPLOYMENT.md** - Production deployment procedures
- **.env.example** - Complete template with all options
