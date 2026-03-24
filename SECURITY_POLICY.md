# Security Policy & Secret Management Guidelines
# For SentinelSecure Project

## ⚠️ CRITICAL: Before Making Public

### Files to NEVER Commit
These files contain sensitive credentials and must NEVER be added to version control:

```
.env                              # Environment variables with passwords
docker-compose.yml                # Unless sanitized of all credentials
*.pem, *.key, *.crt              # SSL certificates and private keys
wazuh_single_mod/config/wazuh_indexer_ssl_certs/  # Generated certificates
credentials.json                  # API credentials
secrets.json                       # Any secrets file
```

### Files to Sanitize Before Committing

**If committing docker-compose.yml, use environment variables:**
```yaml
# ❌ WRONG - Hardcoded secret
environment:
  - ADMIN_PASSWORD=MyActualPassword123

# ✅ RIGHT - Use environment variable
environment:
  - ADMIN_PASSWORD=${ADMIN_PASSWORD}
```

Then define actual values in `.env` (which is gitignored).

## 🔐 Proper Setup Workflow

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/sentinelsecure.git
   cd sentinelsecure
   ```

2. **Create .env from template:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your actual values
   ```

3. **Create docker-compose override (optional):**
   ```bash
   cp docker-compose.example.yml docker-compose.override.yml
   # Edit if you need environment-specific changes
   ```

4. **Verify .env is not tracked:**
   ```bash
   git status | grep .env  # Should show nothing
   ```

5. **Generate SSL certificates:**
   ```bash
   docker-compose -f wazuh_single_mod/generate-indexer-certs.yml run --rm generator
   ```

6. **Start services:**
   ```bash
   docker-compose up -d
   ```

## 📋 Gitignore Coverage

The `.gitignore` file in this repository covers:

- ✅ Environment variables (`.env*`)
- ✅ SSL certificates and keys (`*.pem`, `*.key`, `*.crt`)
- ✅ Generated Wazuh configuration
- ✅ Docker volumes and persistent data
- ✅ Python cache files
- ✅ IDE/editor files
- ✅ OS-specific files
- ✅ API keys and credentials
- ✅ Log files

## 🔍 Pre-Commit Security Check

Run these commands before committing:

```bash
# Check for .env files
git add . --dry-run | grep -i ".env" && echo "⚠️  .env files detected!"

# Check for common secret patterns
git diff --cached | grep -i "password\|secret\|key\|token" && echo "⚠️  Potential secrets found!"

# Check for *.pem files
git status --porcelain | grep -E "\.pem$|\.key$|\.crt$" && echo "⚠️  Certificates detected!"

# Verify no secrets in commit
git diff --cached -- . | head -50  # Review changes before committing
```

## 🛡️ If Secrets Are Accidentally Committed

**IMMEDIATE ACTION REQUIRED:**

1. **Revoke all credentials immediately** - Change all passwords and API keys
2. **Remove file from history:**
   ```bash
   # Remove from all history
   git filter-branch --tree-filter 'rm -f .env' HEAD
   
   # Force push (⚠️ Requires coordination with team)
   git push --force
   ```
3. **Audit who accessed the secrets**
4. **Update all services with new credentials**

**Or use GitHub's built-in secret scanning:**
- Go to Settings → Security → Secret scanning
- GitHub will alert if secrets are pushed

## 🚀 Recommended Secret Management

For production deployments, use:

### Option 1: HashiCorp Vault
```bash
# Store secrets in Vault, not .env
vault write secret/sentinelsecure \
  admin_password="$(openssl rand -base64 32)" \
  indexer_password="$(openssl rand -base64 32)"
```

### Option 2: Docker Secrets (Swarm)
```bash
echo "MySecretPassword" | docker secret create admin_pass -
```

### Option 3: Kubernetes Secrets
```bash
kubectl create secret generic sentinelsecure-secrets \
  --from-literal=admin-password=<password>
```

### Option 4: AWS Systems Manager Parameter Store
```bash
aws ssm put-parameter \
  --name /sentinelsecure/admin_password \
  --value <password> \
  --type SecureString
```

## 📊 Audit & Compliance

### Regular Audits
```bash
# List all secrets access
git log --all -S'password' -S'secret' -S'key'

# Check for commits with secrets
git log -p | grep -i "password\|secret\|key" | head -20
```

### Enable Git Hooks
Add pre-commit hook to prevent secret commits:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for dangerous patterns
if git diff --cached | grep -qE "password\s*=|secret\s*=|api[_-]?key"; then
  echo "❌ ERROR: Possible secrets detected in commit!"
  echo "Commit rejected. Please remove secrets before committing."
  exit 1
fi

# Check for .env files
if git diff --cached --name-only | grep -qE "\.env$"; then
  echo "❌ ERROR: .env file cannot be committed!"
  echo "Add to .gitignore if not already done."
  exit 1
fi
```

Enable it:
```bash
chmod +x .git/hooks/pre-commit
```

## 🔗 Links & Resources

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [git-secrets Tool](https://github.com/awslabs/git-secrets)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [HashiCorp Vault](https://www.vaultproject.io/)

## ❓ Questions & Support

If you suspect secrets were exposed:
1. Review git history for exposed data
2. Contact security team immediately
3. Execute credential rotation procedures
4. File incident report

---

**Last Updated**: March 24, 2026  
**Version**: 1.0.0
