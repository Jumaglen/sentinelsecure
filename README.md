# SentinelSecure - Security Visibility Suite

This is a self-hosted security monitoring and compliance solution built using Grafana Stack, Wazuh, and Bitdefender.

# SentinelSecure Repository Structure

This document explains the folder and file structure of the SentinelSecure project. It helps developers, maintainers, and contributors understand the purpose of each component and how they fit into the overall architecture.

---

## Directory Tree

```
sentinelsecure/
├── README.md
├── docker-compose.yml
├── logsentinel/
│   └── api.py
├── integrations/
│   ├── bitdefender_webhook.py
│   └── wazuh_alert_parser.py
├── prometheus/
│   └── prometheus.yml
├── promtail/
│   └── config.yml
└── .gitignore
```

---

## Component Explanation

### Root Files

- **README.md**
  - Introduction to the project.
  - Basic setup and usage instructions.

- **docker-compose.yml**
  - Defines the entire SentinelSecure stack.
  - Orchestrates services like Grafana, Prometheus, Loki, and custom services.

- **.gitignore**
  - Specifies files and directories to exclude from version control.

---

### Directories

### logsentinel/
- Contains the **Log API** that accepts custom security events from internal apps.
- `api.py`: Flask-based service that listens for event logs and writes them to a file.

### integrations/
- Contains **connectors for external tools**.
- `bitdefender_webhook.py`: Accepts and processes Bitdefender alerts.
- `wazuh_alert_parser.py`: Accepts and processes Wazuh alerts.

### prometheus/
- Contains Prometheus configuration.
- `prometheus.yml`: Defines Prometheus scrape targets (e.g., Docker services).

### promtail/
- Contains Promtail configuration.
- `config.yml`: Defines which log files to watch and how to label logs before sending to Loki.

---

## Visual Architecture Diagram

```
                          +------------------+
                          | Grafana Dashboard |
                          +------------------+
                                     ▲
           +-------------------------+-------------------------+
           |                                                   |
 +-----------------+                               +-------------------+
 | Prometheus      |                               | Loki               |
 | (Metrics)       |                               | (Log Aggregation) |
 +-----------------+                               +-------------------+
          ▲                                                ▲
+----------------------+                    +---------------------------------+
| Docker, Host Metrics |                    | Promtail (Log Shipper)          |
+----------------------+                    | Parses Logs:                    |
                                            | - Syslog                        |
                                            | - Security Events               |
                                            | - Wazuh & Bitdefender Alerts    |
                                            +---------------------------------+
                                                                         ▲
                                                      +-----------------+-----------------+
                                                      |                                 |
                                   +-------------------+-------------------+ +---------------------+
                                   | LogSentinel API                         | Wazuh + Bitdefender  |
                                   | (Custom Event Collector)                | Alert Parsers        |
                                   +-------------------+-------------------+ +---------------------+
                                                               ▲
                                                  +--------------------+
                                                  | External Systems   |
                                                  | (Firewalls, Apps)  |
                                                  +--------------------+
```

---

## Summary of Data Flow

1. **System Metrics** (CPU, RAM, Disk) flow from hosts into **Prometheus**.
2. **System Logs** (auth logs, syslog) flow into **Promtail**, then to **Loki**.
3. **Security Alerts** from **Wazuh** and **Bitdefender** flow into dedicated parsers, then into **Loki**.
4. **Custom Events** flow into **LogSentinel API**, then into **Loki**.
5. **Grafana** queries Prometheus (metrics) and Loki (logs) to display everything in unified dashboards.

---

**Tip:** If adding new integrations, place them inside the `integrations/` folder and configure them to forward data into Loki, Prometheus, or other chosen stores.

