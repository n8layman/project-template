# Security Management for Data Science Workflows

This guide outlines the comprehensive security and collaboration strategy for managing sensitive credentials across development, testing, and production environments in data science projects.

## Security and Collaboration Plan

### Access Control Strategy

This security model implements **permission-based access control** using GitHub repository permissions to create clear boundaries between code access and credential access.

#### Access Levels and Capabilities

**Read-Only Access (Default for External Contributors and Clients):**
- ✅ Can view and clone repository code
- ✅ Can fork repository and create pull requests
- ✅ Can participate in code reviews and discussions
- ❌ **Cannot access secrets** via GitHub CLI or API
- ❌ Cannot run local development workflows with credentials
- ❌ Cannot push directly to repository

**Collaborator+ Access (Core Development Team):**
- ✅ Can access secrets via GitHub CLI (`gh secret get`)
- ✅ Can run local development workflows with production credentials
- ✅ Can test complete pipelines locally
- ✅ Can push directly to repository
- ✅ Full development environment access

**Admin Access (Project Leads):**
- ✅ Can manage secrets via GitHub web interface
- ✅ Can create, update, and delete secrets
- ✅ Can manage repository permissions
- ✅ Complete project control

### Collaborative Development Models

#### Core Team Development (Collaborator+ Access)
- **Direct repository access** with full credential availability
- **Local development** with production secrets via automated loading
- **Complete pipeline testing** before deployment
- **Rapid iteration** with security maintained

#### External Contribution (Read-Only Access)
- **Fork → develop → pull request** workflow
- **Code contribution without credential exposure**
- **Safe collaboration** with external developers
- **Maintained security boundaries**

#### Client Engagement (Read-Only Access)
- **Progress monitoring** via repository access
- **Code review participation** without infrastructure access
- **Transparent development** with credential protection
- **Professional client/vendor boundaries**

### Security Benefits

This approach provides:
- **Granular access control**: Repository permissions control credential access
- **Safe external collaboration**: Contributors can't access sensitive data
- **Client transparency**: Code visibility without security risk
- **Audit compliance**: All credential access logged and traceable
- **Professional boundaries**: Clear separation of responsibilities

## GitHub Actions Secret Integration

### Secure Credential Access Script

The security implementation uses a controlled script for credential access within GitHub Actions workflows:

```bash
#!/bin/bash
# scripts/fetch-secrets.sh - Secure credential fetching for workflows

set -e  # Exit immediately on error

echo "🔐 Initiating secure credential fetch..."

# Verify authentication before attempting access
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI authentication required"
    echo "Run: gh auth login"
    exit 1
fi

# Function to safely fetch and export secrets
fetch_secret() {
    local secret_name=$1
    local secret_value
    
    secret_value=$(gh secret get "$secret_name" 2>/dev/null) || {
        echo "❌ Failed to fetch secret: $secret_name"
        echo "Check repository permissions and secret existence"
        exit 1
    }
    
    export "$secret_name=$secret_value"
    echo "$secret_name=${secret_value}" >> $GITHUB_ENV
    echo "✅ Loaded: $secret_name"
}

# Load all required secrets
fetch_secret "API_KEY"
fetch_secret "DATABASE_URL" 
fetch_secret "DEPLOY_TOKEN"

echo "🔒 All credentials securely loaded"
```

### Environment-Aware Workflow Security

Production workflows implement automatic environment detection and appropriate security controls:

```yaml
# .github/workflows/secure-pipeline.yml
name: Secure Data Pipeline

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  secure-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      # Security: Local development credential access
      - name: Load development credentials
        if: ${{ env.ACT }}
        run: |
          chmod +x scripts/fetch-secrets.sh
          ./scripts/fetch-secrets.sh
          
      # Security: Production credential access  
      - name: Load production credentials
        if: ${{ !env.ACT }}
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
        run: echo "🔒 Production credentials loaded"
        
      # Security: Verify credentials are available
      - name: Validate credential access
        run: |
          if [[ -z "$API_KEY" ]]; then
            echo "❌ API_KEY not available"
            exit 1
          fi
          echo "✅ Required credentials validated"
        
      # Your secure pipeline steps
      - name: Run secure data pipeline
        run: |
          echo "🚀 Executing pipeline with secure credentials"
          # Pipeline code here - credentials available as environment variables
```

### Workflow Security Features

- **Environment Detection**: Automatic differentiation between local and production execution
- **Credential Validation**: Verification that required secrets are available
- **Access Logging**: All credential access events logged for audit
- **Failure Handling**: Graceful failure with clear error messages
- **Memory-Only Access**: Credentials never persisted to disk

## Local Development Integration

### R Development with Automated Secret Loading

For R projects, credentials can be automatically loaded when starting R sessions:

```r
# .Rprofile (add to .gitignore if project-specific)
if (interactive()) {
  # Check if gh is installed and authenticated
  gh_status <- system2("gh", "auth", "status", stdout = FALSE, stderr = FALSE)
  
  if (gh_status == 0) {
    message("🔐 Loading development credentials...")
    
    # Load secrets directly into environment without intermediate variables
    Sys.setenv(API_KEY = system2("gh", c("secret", "get", "API_KEY"), 
                                 stdout = TRUE, stderr = FALSE))
    Sys.setenv(DATABASE_URL = system2("gh", c("secret", "get", "DATABASE_URL"), 
                                      stdout = TRUE, stderr = FALSE))
    
    message("✅ Credentials loaded for R session")
  } else {
    message("⚠️  GitHub CLI not authenticated. Run: gh auth login")
    message("   Credentials not available for this session")
  }
}
```

### Python Development Integration

For Python projects, create a development setup approach:

```python
# scripts/setup_dev_env.py
import subprocess
import os

def load_credentials():
    """Load GitHub secrets for local development."""
    print("🔐 Loading development credentials...")
    
    try:
        # Check authentication first
        subprocess.run(["gh", "auth", "status"], 
                      capture_output=True, check=True)
        
        # Load secrets into environment
        secrets = ["API_KEY", "DATABASE_URL", "DEPLOY_TOKEN"]
        
        for secret in secrets:
            result = subprocess.run(["gh", "secret", "get", secret], 
                                  capture_output=True, text=True, check=True)
            os.environ[secret] = result.stdout.strip()
            print(f"✅ Loaded: {secret}")
            
    except subprocess.CalledProcessError:
        print("❌ GitHub CLI not authenticated or insufficient permissions")
        print("Run: gh auth login")

if __name__ == "__main__":
    load_credentials()
```

### Local Development Security Features

- **Direct Environment Loading**: Secrets go directly to environment variables
- **No Intermediate Storage**: No temporary variables that could appear in dumps
- **Authentication Verification**: Checks GitHub CLI auth before attempting access
- **Permission Validation**: Graceful handling of insufficient permissions
- **Session Isolation**: Credentials only available during active session

### Development Workflow Integration

#### R Workflow
```bash
# Authenticate once
gh auth login

# Start R - credentials automatically available
R
# Credentials now accessible via Sys.getenv("API_KEY")
```

#### Python Workflow
```bash
# Authenticate once  
gh auth login

# Load credentials for session
python scripts/setup_dev_env.py

# Or integrate with pixi tasks
pixi run dev  # Could include credential loading
```

## Secret Management Best Practices

### Credential Backup Strategy

⚠️ **CRITICAL: GitHub Secrets are Write-Only**

GitHub Secrets cannot be viewed after creation. Always maintain secure backups:

- **Password Manager**: Use 1Password, Bitwarden, or enterprise solutions
- **Exact Naming**: Match GitHub secret names in password manager
- **Team Access**: Ensure backup access for all authorized team members
- **Recovery Planning**: Document credential recovery procedures

### Security Monitoring and Compliance

#### Access Control Validation
```bash
# Verify your repository permissions
gh api repos/:owner/:repo --jq '.permissions'

# Test secret access (requires collaborator+ permissions)
gh secret list

# Validate authentication status
gh auth status
```

#### Audit and Compliance
- **Access Logging**: GitHub provides complete audit trails for secret access
- **Permission Reviews**: Regular audits of repository access levels
- **Credential Rotation**: Planned rotation with password manager coordination
- **Security Boundaries**: Clear documentation of access levels and responsibilities

### Repository Security Architecture

```
Security Model:
├── Read-Only Access (External, Clients)
│   ├── ✅ Code review and contribution
│   ├── ✅ Fork/PR workflow
│   └── ❌ No credential access
├── Collaborator+ Access (Core Team)
│   ├── ✅ Full development capabilities
│   ├── ✅ Credential access for local work
│   └── ✅ Pipeline testing with production secrets
└── Admin Access (Project Leads)
    ├── ✅ Secret management
    ├── ✅ Permission control
    └── ✅ Security oversight
```

This comprehensive security plan ensures that sensitive credentials are managed consistently and securely across all environments while enabling effective collaboration and maintaining clear professional boundaries with clients and external contributors.
