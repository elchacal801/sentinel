# Sentinel Deployment Guide

**Classification:** UNCLASSIFIED//FOUO

This guide covers deploying the Sentinel Intelligence Platform to production.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Security Hardening](#security-hardening)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)

---

## Prerequisites

### Required Tools
- **Docker** 20.10+
- **Kubernetes** 1.25+ (for K8s deployment)
- **kubectl** 1.25+
- **Helm** 3.10+ (optional)
- **Git**

### Required Services
- **Container Registry** (GitHub Container Registry, Docker Hub, or private registry)
- **Kubernetes Cluster** (EKS, GKE, AKS, or on-prem)
- **SSL Certificate** (Let's Encrypt or commercial)

---

## Docker Deployment

### 1. Build Production Images

```bash
# Build backend
cd backend
docker build -f Dockerfile.prod -t sentinel/backend:latest .

# Build frontend
cd ../frontend
docker build -f Dockerfile.prod -t sentinel/frontend:latest .
```

### 2. Run with Docker Compose

```bash
# Production compose
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Verify Deployment

```bash
# Check containers
docker ps

# Check logs
docker logs sentinel-backend
docker logs sentinel-frontend

# Access services
curl http://localhost:8000/api/v1/health
curl http://localhost:3000/
```

---

## Kubernetes Deployment

### 1. Prepare Cluster

```bash
# Create namespace
kubectl apply -f infrastructure/kubernetes/namespace.yaml

# Verify namespace
kubectl get namespace sentinel
```

### 2. Configure Secrets

```bash
# Create Neo4j credentials
kubectl create secret generic neo4j-credentials \
  --from-literal=auth=neo4j/your-secure-password \
  --from-literal=password=your-secure-password \
  -n sentinel

# Verify secrets
kubectl get secrets -n sentinel
```

### 3. Deploy Database

```bash
# Deploy Neo4j
kubectl apply -f infrastructure/kubernetes/neo4j-deployment.yaml

# Wait for Neo4j to be ready
kubectl wait --for=condition=ready pod -l app=neo4j -n sentinel --timeout=300s

# Verify deployment
kubectl get pods -n sentinel
kubectl logs -l app=neo4j -n sentinel
```

### 4. Deploy Backend

```bash
# Deploy backend API
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml

# Wait for backend
kubectl wait --for=condition=ready pod -l app=backend -n sentinel --timeout=300s

# Verify deployment
kubectl get pods -n sentinel
kubectl logs -l app=backend -n sentinel
```

### 5. Deploy Frontend

```bash
# Deploy frontend
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml

# Wait for frontend
kubectl wait --for=condition=ready pod -l app=frontend -n sentinel --timeout=300s

# Verify deployment
kubectl get pods -n sentinel
kubectl logs -l app=frontend -n sentinel
```

### 6. Configure Ingress

```bash
# Apply ingress (update sentinel.example.com with your domain)
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml

# Get ingress IP
kubectl get ingress -n sentinel
```

### 7. Verify Full Stack

```bash
# Check all resources
kubectl get all -n sentinel

# Check services
kubectl get svc -n sentinel

# Test backend health
kubectl port-forward svc/backend 8000:8000 -n sentinel
curl http://localhost:8000/api/v1/health

# Test frontend
kubectl port-forward svc/frontend 3000:3000 -n sentinel
curl http://localhost:3000/
```

---

## Using Kustomize

```bash
# Deploy with kustomize
kubectl apply -k infrastructure/kubernetes/

# Update image tags
cd infrastructure/kubernetes/
kustomize edit set image sentinel/backend=ghcr.io/yourusername/sentinel/backend:v1.0.0
kustomize edit set image sentinel/frontend=ghcr.io/yourusername/sentinel/frontend:v1.0.0

# Apply changes
kubectl apply -k .
```

---

## CI/CD Pipeline

### GitHub Actions Setup

1. **Enable GitHub Container Registry**
   - Go to Settings > Packages
   - Enable package publishing

2. **Configure Secrets** (if deploying to cluster)
   ```
   KUBE_CONFIG_DATA: Base64-encoded kubeconfig
   ```

3. **Push to trigger pipeline**
   ```bash
   git push origin master
   ```

4. **Monitor workflow**
   - Go to Actions tab in GitHub
   - Watch CI/CD pipeline execution

### Pipeline Stages

1. **Test** - Run backend and frontend tests
2. **Security Scan** - Trivy vulnerability scanning
3. **Build** - Build Docker images
4. **Push** - Push images to registry
5. **Deploy** - Deploy to Kubernetes (optional)

---

## Security Hardening

### 1. Update Secrets

```bash
# Generate strong password
openssl rand -base64 32

# Update Neo4j secret
kubectl create secret generic neo4j-credentials \
  --from-literal=auth=neo4j/$(openssl rand -base64 32) \
  --from-literal=password=$(openssl rand -base64 32) \
  -n sentinel \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 2. Network Policies

```bash
# Apply network policies (create them first based on your needs)
kubectl apply -f infrastructure/kubernetes/network-policies.yaml
```

### 3. Pod Security Standards

```bash
# Label namespace for pod security
kubectl label namespace sentinel \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

### 4. RBAC Configuration

```bash
# Create service accounts and roles
kubectl apply -f infrastructure/kubernetes/rbac.yaml
```

---

## Monitoring

### Prometheus & Grafana

```bash
# Install Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace

# Create ServiceMonitors for Sentinel
kubectl apply -f infrastructure/kubernetes/monitoring/
```

### Logging

```bash
# Install Loki stack
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace logging \
  --create-namespace \
  --set grafana.enabled=true
```

### Access Monitoring

```bash
# Port forward Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access at http://localhost:3000
# Default credentials: admin/prom-operator
```

---

## Backup and Recovery

### Neo4j Backup

```bash
# Manual backup
kubectl exec -n sentinel $(kubectl get pod -n sentinel -l app=neo4j -o jsonpath='{.items[0].metadata.name}') -- \
  neo4j-admin database dump neo4j --to-path=/data/backups

# Copy backup locally
kubectl cp sentinel/$(kubectl get pod -n sentinel -l app=neo4j -o jsonpath='{.items[0].metadata.name}'):/data/backups/neo4j.dump \
  ./neo4j-backup-$(date +%Y%m%d).dump
```

### Automated Backups

```bash
# Create CronJob for automated backups
kubectl apply -f infrastructure/kubernetes/backup-cronjob.yaml
```

### Restore from Backup

```bash
# Stop Neo4j
kubectl scale deployment neo4j --replicas=0 -n sentinel

# Copy backup to pod
kubectl cp ./neo4j-backup.dump \
  sentinel/$(kubectl get pod -n sentinel -l app=neo4j -o jsonpath='{.items[0].metadata.name}'):/data/backups/

# Restore
kubectl exec -n sentinel $(kubectl get pod -n sentinel -l app=neo4j -o jsonpath='{.items[0].metadata.name}') -- \
  neo4j-admin database load neo4j --from-path=/data/backups

# Restart Neo4j
kubectl scale deployment neo4j --replicas=1 -n sentinel
```

---

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n sentinel

# Scale frontend
kubectl scale deployment frontend --replicas=5 -n sentinel
```

### Auto-scaling (HPA already configured)

```bash
# View HPA status
kubectl get hpa -n sentinel

# Describe HPA
kubectl describe hpa backend-hpa -n sentinel
kubectl describe hpa frontend-hpa -n sentinel
```

---

## Troubleshooting

### Check Pod Status

```bash
# Get pods
kubectl get pods -n sentinel

# Describe problematic pod
kubectl describe pod <pod-name> -n sentinel

# View logs
kubectl logs <pod-name> -n sentinel

# Follow logs
kubectl logs -f <pod-name> -n sentinel

# Previous container logs
kubectl logs <pod-name> -n sentinel --previous
```

### Check Services

```bash
# Get services
kubectl get svc -n sentinel

# Test service connectivity
kubectl run test --rm -it --image=busybox -n sentinel -- sh
wget -O- http://backend:8000/api/v1/health
```

### Check Ingress

```bash
# Get ingress
kubectl get ingress -n sentinel

# Describe ingress
kubectl describe ingress sentinel-ingress -n sentinel

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

### Database Issues

```bash
# Connect to Neo4j
kubectl port-forward svc/neo4j 7474:7474 -n sentinel

# Access Neo4j browser at http://localhost:7474

# Check Neo4j logs
kubectl logs -l app=neo4j -n sentinel

# Restart Neo4j
kubectl rollout restart deployment/neo4j -n sentinel
```

---

## Upgrade Strategy

### Rolling Update

```bash
# Update backend image
kubectl set image deployment/backend backend=sentinel/backend:v1.1.0 -n sentinel

# Watch rollout
kubectl rollout status deployment/backend -n sentinel

# Rollback if needed
kubectl rollout undo deployment/backend -n sentinel
```

### Blue-Green Deployment

```bash
# Deploy new version with different label
kubectl apply -f infrastructure/kubernetes/backend-v2.yaml

# Test new version
kubectl port-forward svc/backend-v2 8000:8000 -n sentinel

# Switch traffic by updating service selector
kubectl patch service backend -n sentinel -p '{"spec":{"selector":{"version":"v2"}}}'

# Remove old version
kubectl delete deployment backend-v1 -n sentinel
```

---

## Health Checks

### Backend Health

```bash
# Health endpoint
curl http://backend-url/api/v1/health

# Expected response
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2025-10-02T00:00:00Z"
}
```

### Frontend Health

```bash
# Root endpoint
curl http://frontend-url/

# Expected: HTML response with status 200
```

### Neo4j Health

```bash
# Cypher query
echo "RETURN 1" | cypher-shell -u neo4j -p password
```

---

## Performance Tuning

### Backend Optimization

```yaml
# Update backend deployment
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"

# Workers (in Dockerfile.prod or deployment)
CMD ["uvicorn", "api.main:app", "--workers", "8"]
```

### Database Optimization

```yaml
# Update Neo4j env vars
- name: NEO4J_server_memory_heap_max__size
  value: "4G"
- name: NEO4J_server_memory_pagecache_size
  value: "2G"
```

### Frontend Optimization

- Enable Next.js caching
- Use CDN for static assets
- Enable compression in ingress

---

## Production Checklist

- [ ] Strong passwords configured
- [ ] SSL/TLS certificates installed
- [ ] Network policies applied
- [ ] RBAC configured
- [ ] Resource limits set
- [ ] Monitoring installed
- [ ] Logging configured
- [ ] Backup jobs scheduled
- [ ] Health checks configured
- [ ] HPA configured
- [ ] Documentation updated
- [ ] Team trained

---

## Support

For issues or questions:
- **GitHub Issues**: https://github.com/elchacal801/sentinel/issues
- **Documentation**: See main README.md

---

**Classification:** UNCLASSIFIED//FOUO  
**Last Updated:** 2025-10-02  
**Version:** 1.0.0
