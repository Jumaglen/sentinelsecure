# Setup Guide for SentinelSecure Configuration Files

This guide explains how to properly configure SentinelSecure after cloning from GitHub.

## 📋 Configuration Steps

### 1. Environment Variables (.env)

```bash
# Copy the template
cp .env.example .env

# Edit with your credentials
nano .env
# OR
vi .env
```

**Key variables to update** (marked in .env.example):
- `GF_SECURITY_ADMIN_PASSWORD` - Grafana admin password
- `INDEXER_PASSWORD` - Wazuh admin password
- `API_PASSWORD` - Wazuh API password
- `DASHBOARD_PASSWORD` - Dashboard password
- Database credentials (if using MySQL)

### 2. Wazuh Dashboard Configuration

```bash
# Copy template to actual config
cp wazuh_single_mod/config/wazuh_dashboard/wazuh.yml.example \
   wazuh_single_mod/config/wazuh_dashboard/wazuh.yml

# Edit with your credentials
nano wazuh_single_mod/config/wazuh_dashboard/wazuh.yml
```

**Update these values**:
```yaml
hosts:
  - 1513629884013:
      url: "https://wazuh.manager"
      port: 55000
      username: wazuh-wui          # Change if using different user
      password: YOUR_API_PASSWORD  # From .env API_PASSWORD
      run_as: false
enrollment.dns: "your.server.ip"   # Your server's hostname/IP
```

### 3. Docker Compose Override (Optional)

```bash
# If you need environment-specific settings
cp docker-compose.example.yml docker-compose.override.yml

# Edit for your environment
nano docker-compose.override.yml
```

### 4. Generate SSL Certificates (Important!)

```bash
# Set system limits (required for Wazuh Indexer)
sudo sysctl -w vm.max_map_count=262144

# Generate Wazuh certificates
docker-compose -f wazuh_single_mod/generate-indexer-certs.yml run --rm generator
```

### 5. Start Services

```bash
# Start all containers
docker-compose up -d

# Wait about 1 minute for services to initialize
sleep 60

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 6. Access Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / (password from .env) |
| **Wazuh** | https://localhost:443 | admin / (password from .env) |
| **Prometheus** | http://localhost:9090 | (no auth) |
| **Loki** | http://localhost:3100 | (no auth) |

## ✅ Verification Checklist

- [ ] `.env` file created and edited with your credentials
- [ ] `wazuh.yml` file created in `wazuh_single_mod/config/wazuh_dashboard/`
- [ ] SSL certificates generated successfully
- [ ] All containers running: `docker-compose ps` shows all UP
- [ ] Grafana accessible at http://localhost:3000
- [ ] Wazuh Dashboard accessible at https://localhost:443

## 📝 Important Notes

### Security
- ✅ **Credentials stay private**: `.env` and `wazuh.yml` are in `.gitignore` and not tracked by git
- ✅ **Never commit credentials**: These files should NEVER be added to version control
- ✅ **Safe to modify locally**: Changes to these files won't affect the repository

### File Descriptions
| File | Purpose | Tracked by Git |
|------|---------|----------------|
| `.env` | Environment variables | ❌ No (.gitignore) |
| `.env.example` | Template for .env | ✅ Yes |
| `wazuh.yml` | Wazuh Dashboard config | ❌ No (.gitignore) |
| `wazuh.yml.example` | Template for wazuh.yml | ✅ Yes |
| `.gitignore` | Files to exclude from git | ✅ Yes |

### If You Accidentally Commit Credentials

```bash
# Remove from tracking (keeps local copy)
git rm --cached filename

# Add to .gitignore
echo "filename" >> .gitignore

# Commit the fix
git add .gitignore
git commit -m "remove credentials from tracking"
```

## 🔧 Customization

### Changing Service Ports
Edit `docker-compose.yml`:
```yaml
services:
  grafana:
    ports:
      - "3000:3000"  # Change first number to use different host port
```

### Adding Custom Volumes
```yaml
volumes:
  - /path/on/host:/path/in/container
```

### Using External Docker Networks
```yaml
networks:
  webhook_net:
    external: true
    name: my_existing_network
```

## 🆘 Troubleshooting

### Containers won't start
```bash
# Check logs
docker-compose logs alert-webhook

# Check system limits
sysctl vm.max_map_count  # Should be >= 262144
```

### Permission denied errors
```bash
# Run with proper permissions
sudo docker-compose up -d

# OR add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Existing port conflicts
```bash
# Check what's using port 3000
lsof -i :3000

# Change port in docker-compose.yml or .env
```

---

**Next Steps**:
1. Follow the step-by-step setup above
2. Verify all services are running
3. Access dashboards to confirm
4. Check [README.md](README.md) for detailed feature documentation
5. Review [SECURITY_POLICY.md](SECURITY_POLICY.md) for security best practices
