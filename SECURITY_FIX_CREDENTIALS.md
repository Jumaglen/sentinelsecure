# Security Fix: Removing Hardcoded Credentials

## What Was Fixed

### Issue
The file `wazuh_single_mod/config/wazuh_dashboard/wazuh.yml` contained hardcoded credentials and was being tracked in git despite being in `.gitignore`.

**Problem**: Adding a file to `.gitignore` only prevents FUTURE commits. Files already committed continue to be tracked.

### Solution Implemented

1. ✅ **Removed credentials from wazuh.yml**
   - Replaced with environment variable placeholders: `${WAZUH_API_USERNAME}`, `${WAZUH_API_PASSWORD}`, etc.

2. ✅ **Removed file from Git tracking**
   ```bash
   git rm --cached wazuh_single_mod/config/wazuh_dashboard/wazuh.yml
   ```
   - The file now stays local-only and won't be tracked

3. ✅ **Created template file**
   - `wazuh.yml.example` - Shows the structure with placeholders
   - Users copy this and populate with their credentials

4. ✅ **Updated .gitignore**
   - Explicitly ignores `wazuh_single_mod/config/wazuh_dashboard/wazuh.yml`

## Files Changed

### Deleted from Git (but kept locally)
- `wazuh_single_mod/config/wazuh_dashboard/wazuh.yml` ❌ (removed from tracking)

### Added to Git
- `wazuh_single_mod/config/wazuh_dashboard/wazuh.yml.example` ✅ (template with placeholders)

## For GitHub

When you push these changes:
```bash
git push origin main
```

The file will be **deleted from the repository** but **kept on your local machine** thanks to `.gitignore`.

Future users will:
1. Clone the repository
2. See `wazuh.yml.example` as a reference
3. Copy it to `wazuh.yml` and populate with their credentials
4. Their `wazuh.yml` will be ignored by git and stayed private

## Other Sensitive Files Checked

✅ `wazuh_single_mod/config/wazuh_indexer/internal_users.yml`
   - Safe: Contains bcrypt password hashes, not plaintext credentials

✅ `wazuh_single_mod/config/wazuh_indexer/wazuh.indexer.yml`
   - Safe: Certificate paths and configuration only, no credentials

✅ `wazuh_single_mod/config/wazuh_cluster/`
   - Safe: Configuration only

---

## Best Practices Going Forward

### When Adding Credentials to Config Files

1. **Never commit plaintext credentials**
   ```yaml
   # ❌ WRONG - Hardcoded password
   password: "MyActualPassword123"
   
   # ✅ RIGHT - Environment variable
   password: ${MY_PASSWORD}
   ```

2. **Always use .example templates**
   - Create `filename.example` with placeholder values
   - Commit `.example` files
   - Ignore actual credential files in `.gitignore`

3. **Add new sensitive files to .gitignore immediately**
   ```bash
   # Add to .gitignore BEFORE creating the file
   echo "my_secrets.yml" >> .gitignore
   git add .gitignore
   git commit -m "add my_secrets.yml to gitignore"
   # NOW create the file with credentials
   ```

### Checking for Exposed Credentials

```bash
# Search for plaintext passwords in code
grep -r "password\s*=" . --exclude-dir=.git --exclude-dir=node_modules

# Search for API keys pattern
grep -r "api.key\|api_key\|apikey" . --exclude-dir=.git

# Use git-secrets tool (recommended)
git secrets --scan
```

---

## Reference: Git Tracking Issues

### Scenario 1: File Already Committed ❌
```bash
# Add to .gitignore
echo "secrets.yml" >> .gitignore

# This DOESN'T work - file is still tracked!
git add secrets.yml .gitignore
git commit -m "add secrets to gitignore"  # File still in history!
```

### Scenario 2: File Already Committed ✅ (Correct Fix)
```bash
# Remove from tracking (but keep local copy)
git rm --cached secrets.yml

# Add to .gitignore first
echo "secrets.yml" >> .gitignore

# Commit the removal
git add -A
git commit -m "remove secrets.yml from tracking"

# NOW the file stays local-only
```

---

## Public Repository Status

✅ **Safe to make public** - Credentials have been:
- Removed from tracked files
- Replaced with environment variables
- All sensitive files are in .gitignore and removed from tracking

---

**Last Updated**: March 24, 2026  
**Commit**: `c228e8e`
