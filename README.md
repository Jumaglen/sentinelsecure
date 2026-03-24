# SentinelSecure - Project Analysis & Functionality Guide

## 📋 Project Overview

**SentinelSecure** is a self-hosted, containerized **security monitoring and compliance solution** that aggregates security events, logs, and metrics from multiple sources into a unified dashboard. It combines industry-standard open-source tools (Grafana, Wazuh, Prometheus, Loki) with custom integrations.

**Purpose**: Real-time security visibility, threat detection, and incident response across enterprise infrastructure.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    GRAFANA DASHBOARD (Port 3000)                │
│                   Central Visualization & Alerting              │
└─────────────────────────────────────────────────────────────────┘
                              ▲
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼─────┐        ┌────▼──────┐    ┌───────▼────────┐
    │Prometheus │        │   Loki    │    │ Wazuh Dashboard│
    │(Metrics)  │        │(Log Store)│    │ Portal (HTTPS) │
    └────▲─────┘        └────▲──────┘    └────────────────┘
         │                    │
    ┌────┴────┐        ┌─────┴────────────────┐
    │Docker   │        │Alert Parsers & Logs │
    │Metrics  │        │  - Promtail (Shipper)
    └────────┘        │  - Bitdefender Parser
                      │  - Wazuh Parser
                      │  - LogSentinel API
                      └─────┬────────────────┘
                            ▲
              ┌─────────────┬┴──────────────┐
              │             │               │
        ┌─────▼──┐    ┌────▼─────┐   ┌────▼──────┐
        │Wazuh   │    │Bitdefender    │External
        │Manager │    │Alerts    │    │Systems
        └────────┘    └──────────┘    │(Firewalls)
```

---

## 🔧 Core Components

### 1. **Grafana** (Port 3000) - Central Dashboard
- **Role**: Unified visualization platform
- **Connected to**:
  - Prometheus (metrics visualization)
  - Loki (log visualization)
  - Wazuh (security events)
- **Functionality**:
  - Real-time dashboards
  - Alert rule configuration
  - User authentication & RBAC
  - Data source management

### 2. **Wazuh** (Port 55000 API, 1514-1515 Agents) - SIEM & Threat Detection
Three-component architecture:

#### a) **Wazuh Manager** (Port 55000)
- Collects alerts from Wazuh agents
- Processes security events
- Applies detection rules
- Communicates with indexer via SSL

#### b) **Wazuh Indexer** (Port 9200) - OpenSearch Backend
- Elasticsearch-compatible data store
- Indexes security events
- Provides full-text search capabilities
- Stores alert history

#### c) **Wazuh Dashboard** (Port 443 HTTPS)
- Web UI for Wazuh management
- Alert visualization
- Agent management
- Compliance reports

**Functionality**:
- Host-based intrusion detection
- File integrity monitoring
- Policy compliance checking
- Cloud security monitoring
- Vulnerability detection

### 3. **Prometheus** (Port 9090) - Metrics Collection
- **Role**: Time-series metrics database
- **Collects**:
  - Docker container metrics
  - Host system metrics
  - Application performance data
- **Scrape Interval**: 15 seconds (configurable)
- **Data Retention**: Configurable (default: 15 days)

### 4. **Loki** (Port 3100) - Log Aggregation
- **Role**: Lightweight log aggregation engine
- **Advantages**:
  - Index by labels only (efficient storage)
  - Lower resource footprint than ELK
  - Fast log querying
- **Receives logs from**:
  - Promtail (log shipper)
  - Custom webhook parsers

### 5. **Promtail** (Port 9080) - Log Shipper
- **Role**: Tail logs and send to Loki
- **Monitors**:
  - `/var/log/syslog` - System logs
  - `/var/log/auth.log` - Authentication events
  - `/var/logs/` - Custom application logs (mounted volume)
- **Adds Labels**:
  - `job`: system-logs
  - `host`: app-server-1
  - `source`: syslog

---

## 🔌 Custom Integration Services

### 1. **LogSentinel API** (Port 5000)
**Purpose**: Accept custom security events from internal applications

**Code**:
```python
POST /log_event
{
  "event_type": "authentication_failure",
  "source": "web-app-01",
  "timestamp": "2025-03-24T12:30:00Z",
  "user": "john.doe",
  "description": "Failed login attempt"
}
```

**Destination**: Writes to `/app/logs/security_events.log`

**Use Cases**:
- Custom application security events
- Business logic violations
- Unauthorized access attempts
- API abuse detection

---

### 2. **Bitdefender Webhook Parser** (Port 5001)
**Purpose**: Ingest antivirus/EDR alerts from Bitdefender Endpoint

**Functionality**:
```
Bitdefender Alert 
    ↓
POST /bitdefender-alert 
    ↓
Parse & Transform
    ↓
Forward to Loki (label: source="bitdefender")
    ↓
Visualize in Grafana
```

**Captured Alerts**:
- Malware threats detected
- Quarantine actions
- Vulnerability detections
- Behavioral anomalies

---

### 3. **Wazuh Alert Parser** (Port 5002)
**Purpose**: Enhance Wazuh alerts and enrich data before storage

**Flow**:
```
Wazuh Manager Alert
    ↓
POST /wazuh-alert
    ↓
Parse & Enrich (if needed)
    ↓
Forward to Loki (label: source="wazuh")
    ↓
Indexed & Searchable
```

**Why Duplicate Storage?**
- Wazuh Indexer: Native Wazuh queries & compliance reports
- Loki: Unified log search across all sources
- Grafana: Dashboard visualization of unified logs

---

## 📊 Data Flow & Integration Points

```
SECURITY EVENT SOURCES
    ↓
┌───────────────────────────────────────────┐
│  1. Wazuh Agents (Host Monitoring)       │
│  2. Bitdefender Endpoints (Antivirus)    │
│  3. Internal Apps (LogSentinel API)      │
│  4. System Logs (Promtail)               │
│  5. Firewalls/Network (Future)           │
└───────────────────────────────────────────┘
    ↓
AGGREGATION LAYER
    ↓
┌───────────────────────────────────────────┐
│  - Wazuh Manager (processes alerts)      │
│  - Loki (aggregates all logs)            │
│  - Prometheus (collects metrics)         │
└───────────────────────────────────────────┘
    ↓
STORAGE & INDEXING
    ↓
┌───────────────────────────────────────────┐
│  - Wazuh Indexer (OpenSearch)            │
│  - Loki Storage                          │
│  - Prometheus Time-Series DB             │
└───────────────────────────────────────────┘
    ↓
VISUALIZATION & ANALYTICS
    ↓
┌───────────────────────────────────────────┐
│  - Grafana Dashboard (unified view)      │
│  - Wazuh Dashboard (compliance reports)  │
│  - Alerts & Notifications                │
└───────────────────────────────────────────┘
```

---

## 🔐 Security Features

### Wazuh Capabilities
- ✅ **Host-based IDS/IPS**: Real-time threat detection
- ✅ **FIM (File Integrity Monitoring)**: Detects unauthorized file changes
- ✅ **Vulnerability Scanning**: Identifies missing patches
- ✅ **Compliance Checking**: CIS, PCI-DSS, HIPAA, SOC 2
- ✅ **Log Analysis**: Pattern matching & behavioral analysis
- ✅ **Active Response**: Automated remediation actions

### Network Security
- ✅ SSL/TLS encryption for all inter-service communication
- ✅ Self-signed certificates for Wazuh Dashboard
- ✅ Grafana authentication (admin password required)
- ✅ API authentication for custom parsers

---

## 📁 Directory Structure & Key Files

```
sentinelsecure/
├── README.md                          # Project documentation
├── docker-compose.yml                 # Main orchestration file
│
├── integrations/                      # Custom webhook parsers
│   ├── Dockerfile                     # Build definitions
│   ├── bitdefender_webhook.py         # Bitdefender → Loki
│   └── wazuh_alert_parser.py          # Wazuh → Loki (enrichment)
│
├── logsentinel/                       # Custom event collection
│   └── api.py                         # Flask API for app events
│
├── prometheus/                        # Metrics configuration
│   └── prometheus.yml                 # Scrape job definitions
│
├── promtail/                          # Log shipping config
│   └── config.yml                     # Log file watchers & labels
│
├── wazuh_single_mod/                  # Wazuh deployment config
│   ├── README.md                      # Setup instructions
│   ├── docker-compose.demo.yml        # Demo configuration
│   ├── generate-indexer-certs.yml     # SSL certificate generation
│   └── config/                        # YAML configs
│       ├── certs.yml                  # Certificate specs
│       ├── wazuh_cluster/             # Cluster configuration
│       ├── wazuh_dashboard/           # Dashboard settings
│       └── wazuh_indexer/             # Indexer settings
│
└── .git/                              # Version control
```

---

## 🚀 Container Services & Ports

| Service | Image | Port(s) | Purpose |
|---------|-------|---------|---------|
| **grafana** | grafana/grafana:latest | 3000 | Dashboard & visualization |
| **prometheus** | prom/prometheus:latest | 9090 | Metrics collection |
| **loki** | grafana/loki:latest | 3100 | Log aggregation |
| **promtail** | grafana/promtail:latest | 9080 | Log shipper |
| **wazuh.manager** | wazuh/wazuh-manager:4.11.0 | 55000 (API), 1514-1515 (agents) | SIEM core |
| **wazuh.indexer** | wazuh/wazuh-indexer:4.11.0 | 9200 | Log storage (OpenSearch) |
| **wazuh.dashboard** | wazuh/wazuh-dashboard:4.11.0 | 443 | Wazuh web UI |
| **bitdefender-webhook** | custom (Flask) | 5001 | Bitdefender integration |
| **wazuh-alert-parser** | custom (Flask) | 5002 | Wazuh enrichment |
| **logsentinel-api** | custom (Flask) | 5000 | Custom event API |

---

## 🔄 Deployment Architecture

### Single Node Setup
- All services run on one Docker host
- Suitable for: SMBs, labs, POCs
- Resource requirement: 8GB+ RAM, 4+ CPU cores

### Scalable Architecture (Future)
- Multiple Wazuh agents on remote hosts
- Elasticsearch cluster (multiple nodes)
- Grafana HA with reverse proxy
- Prometheus remote storage

---

## 📈 Key Metrics & Data Captured

### From Docker/Host
- CPU usage, memory, disk I/O
- Container status & resource consumption
- Network throughput

### From Wazuh
- Failed login attempts
- Root privilege escalations
- File modifications
- Policy violations
- Vulnerability findings
- Integrity violations

### From Bitdefender
- Malware threats
- Suspicious files quarantined
- Vulnerability detections
- Behavioral anomalies

### From Applications
- Custom business logic violations
- API abuse attempts
- Unauthorized access attempts
- Transaction anomalies

---

## 🛠️ Configuration Files Explained

### docker-compose.yml
- Defines all services and their dependencies
- Mount volumes for persistent data
- Environment variables for credentials
- Network bridges (core_net, infra_net)

### prometheus.yml
```yaml
scrape_interval: 15s              # Query metrics every 15 seconds
scrape_configs:
  - job_name: 'prometheus'        # Monitor Prometheus itself
    targets: ['localhost:9090']   # At this endpoint
```

### promtail/config.yml
```yaml
scrape_configs:
  - job_name: system-logs
    files:
      - /var/log/syslog           # Watch these log files
      - /var/log/auth.log
    labels:
      source: syslog              # Label for Loki search
      host: app-server-1
```

### Wazuh Configs
- **wazuh.indexer.yml**: OpenSearch indexer settings
- **opensearch_dashboards.yml**: Dashboard UI config
- **wazuh.yml**: Grafana Wazuh plugin config

---

## 🔌 Integration Points for Enhancement

### Extend with Additional Sources
1. **Firewall Logs**: pfSense, Cisco, Fortinet
2. **Database Audits**: MySQL, PostgreSQL audit logs
3. **Cloud Logs**: AWS CloudTrail, Azure Activity Logs
4. **VPN/IAM**: Okta, Auth0 events

### Extend with Additional Outputs
1. **SIEM Forwarding**: Send to external SIEM
2. **Slack/Teams**: Alert notifications
3. **Ticket System**: Auto-create tickets from alerts
4. **Email Alerts**: Daily/weekly digests

---

## 📝 Setup Workflow

```bash
# 1. Increase system limits (for Wazuh Indexer)
sysctl -w vm.max_map_count=262144

# 2. Generate SSL certificates
docker-compose -f wazuh_single_mod/generate-indexer-certs.yml run --rm generator

# 3. Start all services
docker-compose up -d

# 4. Wait for services to stabilize (~1 minute)
docker-compose logs -f

# 5. Access dashboards
# Grafana: http://localhost:3000 (admin / StrongPassword123)
# Wazuh: https://localhost:443 (admin / admin)
# Prometheus: http://localhost:9090
```

---

## 💾 Data Persistence

### Volumes
- `wazuh_api_configuration`: Wazuh API config
- `wazuh_etc`: Wazuh agent configs
- `wazuh_logs`: Alert logs
- `wazuh-indexer-data`: OpenSearch data (security events)
- `filebeat_var`: Filebeat state
- `wazuh-dashboard-config`: Dashboard settings

---

## 🎯 Common Use Cases

### 1. **Threat Detection & Response**
- Monitor alerts in real-time
- Investigate incidents via Grafana dashboard
- Use Wazuh active response for remediation

### 2. **Compliance Reporting**
- Generate PCI-DSS, HIPAA compliance reports
- Track policy violations
- Audit file integrity changes

### 3. **Security Posture Assessment**
- Identify vulnerable systems
- Monitor patch management
- Track unauthorized access attempts

### 4. **Forensics & Investigation**
- Search logs across all systems
- Correlate events from multiple sources
- Timeline reconstruction of incidents

---

## 🔒 Security Considerations

### ⚠️ Default Credentials (Change Immediately)
- **Grafana Admin**: admin / StrongPassword123
- **Wazuh Indexer**: admin / yWrBQ11Ib1BCVJwnj1F8xipNsVSvdT
- **Wazuh API**: wazuh-wui / MyS3cr37P450r.*-

### 🛡️ Before Production
1. ✅ Rotate all default passwords
2. ✅ Configure SSL/TLS certificates
3. ✅ Set up network segmentation
4. ✅ Configure firewall rules
5. ✅ Set up authentication backends (LDAP/OAuth)
6. ✅ Configure audit logging
7. ✅ Plan backup & disaster recovery

---

## 📊 Performance & Sizing

| Component | Min Resources | Recommended |
|-----------|---------------|-------------|
| **Grafana** | 512MB RAM | 1GB RAM |
| **Prometheus** | 512MB RAM | 2GB RAM |
| **Loki** | 512MB RAM | 2GB RAM |
| **Wazuh Manager** | 2GB RAM | 4GB RAM |
| **Wazuh Indexer** | 2GB RAM | 4GB RAM+ |
| **Total (all)** | **8GB** | **16GB+** |

---

## 🚀 Upgrade Path

- **Wazuh**: Maintains backward compatibility across minor versions
- **Grafana**: Supports plugin updates independently
- **Prometheus/Loki**: Zero-downtime upgrades possible with proper ingestion

---

## 📚 Documentation References

- Wazuh Docs: https://documentation.wazuh.com/
- Grafana Docs: https://grafana.com/docs/
- Prometheus Docs: https://prometheus.io/docs/
- Loki Docs: https://grafana.com/docs/loki/

---

## 🎓 Key Takeaways

✅ **Unified Security Platform**: Integrates SIEM, log aggregation, and metrics  
✅ **Real-time Visibility**: Dashboard shows current security state  
✅ **Extensible Architecture**: Easy to add new data sources  
✅ **Compliance-Ready**: Pre-built rules for compliance frameworks  
✅ **Container-Native**: Deploys easily via Docker Compose  
✅ **Open-Source**: Leverages battle-tested security tools  

---

**Last Updated**: March 24, 2026
