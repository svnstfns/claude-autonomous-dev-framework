# Security Audit Workflow

## Overview
Comprehensive security review to identify and fix vulnerabilities.

## Workflow Steps

### 1. Dependency Scanning
```bash
# Check for known vulnerabilities
pip-audit

# Check with safety
safety check

# Review dependency licenses
pip-licenses

# Check for outdated packages
pip list --outdated
```

**Vulnerability Categories:**
- [ ] Critical vulnerabilities (CVSS >= 9.0)
- [ ] High vulnerabilities (CVSS >= 7.0)
- [ ] Medium vulnerabilities (CVSS >= 4.0)
- [ ] Low vulnerabilities (CVSS < 4.0)

### 2. Code Security Analysis
```bash
# Run bandit security linter
bandit -r src/ -ll

# Check for hardcoded secrets
detect-secrets scan --baseline .secrets.baseline

# SQL injection detection
semgrep --config=auto src/

# Check for insecure functions
grep -r "eval\|exec\|compile" src/
```

**Security Checklist:**
- [ ] No hardcoded credentials
- [ ] No SQL injection vulnerabilities
- [ ] No command injection risks
- [ ] No path traversal vulnerabilities
- [ ] No XML/XXE vulnerabilities
- [ ] No insecure deserialization
- [ ] No weak cryptography

### 3. Authentication & Authorization Review
```bash
# Review auth implementation
/review authentication system

# Check for issues:
- Weak password policies
- Missing rate limiting
- Session management flaws
- Privilege escalation paths
```

**Auth Security:**
- [ ] Strong password requirements
- [ ] Secure password storage (bcrypt/argon2)
- [ ] Multi-factor authentication available
- [ ] Session timeout implemented
- [ ] CSRF protection enabled
- [ ] Rate limiting on login attempts
- [ ] Secure token generation

### 4. Input Validation Audit
```python
# Review all input points
def audit_input_validation():
    """
    Check all API endpoints, forms, and data inputs
    for proper validation and sanitization.
    """
    endpoints = find_all_endpoints()
    
    for endpoint in endpoints:
        check_input_validation(endpoint)
        check_output_encoding(endpoint)
        check_parameter_binding(endpoint)
```

**Validation Requirements:**
- [ ] All inputs validated
- [ ] Length limits enforced
- [ ] Type checking implemented
- [ ] Format validation (regex)
- [ ] Whitelist approach used
- [ ] Output properly encoded

### 5. API Security Review
```bash
# Check API security
/review API security

# Verify:
- Authentication required
- Authorization checks
- Rate limiting
- Input validation
- Error handling
- CORS configuration
```

**API Security Checklist:**
- [ ] All endpoints authenticated
- [ ] Proper authorization checks
- [ ] Rate limiting implemented
- [ ] API versioning in place
- [ ] Secure headers set
- [ ] HTTPS enforced
- [ ] API keys rotatable

### 6. Database Security
```sql
-- Check for SQL injection risks
-- Review all queries for parameterization

-- Check database permissions
SELECT * FROM information_schema.role_table_grants;

-- Review sensitive data encryption
-- Ensure PII is encrypted at rest
```

**Database Security:**
- [ ] Parameterized queries only
- [ ] Least privilege access
- [ ] Encrypted connections
- [ ] Sensitive data encrypted
- [ ] Regular backups
- [ ] Audit logging enabled

### 7. Infrastructure Security
```bash
# Docker security scan
docker scan rss-plex-manager:latest

# Check for exposed ports
netstat -tuln

# Review environment variables
printenv | grep -E "KEY|SECRET|PASSWORD|TOKEN"

# File permissions audit
find . -type f -perm 0777
```

**Infrastructure Checklist:**
- [ ] Containers run as non-root
- [ ] Minimal base images used
- [ ] Secrets in secure storage
- [ ] Network segmentation
- [ ] Firewall rules configured
- [ ] Monitoring in place

### 8. Security Headers
```python
# Required security headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000',
    'Content-Security-Policy': "default-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}
```

### 9. Penetration Testing
```bash
# Automated security testing
# OWASP ZAP scan
zap-cli quick-scan --self-contained \
  --start-options '-config api.disablekey=true' \
  http://localhost:8000

# Nikto web scanner
nikto -h http://localhost:8000

# SQLMap for SQL injection
sqlmap -u "http://localhost:8000/api/endpoint?id=1"
```

### 10. Fix Implementation
```bash
# Prioritize fixes by severity
/implement security fix for <vulnerability>

# Test fix
Run security tests again to verify

# Document fix
Update security documentation
```

## Common Vulnerabilities & Fixes

### SQL Injection
```python
# Vulnerable
query = f"SELECT * FROM users WHERE id = {user_id}"

# Secure
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

### XSS (Cross-Site Scripting)
```python
# Vulnerable
return f"<h1>Welcome {username}</h1>"

# Secure
from markupsafe import Markup, escape
return Markup(f"<h1>Welcome {escape(username)}</h1>")
```

### CSRF (Cross-Site Request Forgery)
```python
# Add CSRF protection
from fastapi_csrf import FastAPICSRF

csrf = FastAPICSRF()
csrf.setup(app)
```

### Insecure Direct Object References
```python
# Vulnerable
@app.get("/file/{file_id}")
def get_file(file_id: int):
    return get_file_by_id(file_id)

# Secure
@app.get("/file/{file_id}")
def get_file(file_id: int, user: User = Depends(get_current_user)):
    file = get_file_by_id(file_id)
    if file.owner_id != user.id:
        raise HTTPException(403, "Access denied")
    return file
```

### Weak Cryptography
```python
# Vulnerable
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# Secure
import bcrypt
password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

## Security Testing Tools

### Static Analysis
- **bandit**: Python security linter
- **semgrep**: Pattern-based static analysis
- **safety**: Dependency vulnerability scanner
- **detect-secrets**: Hardcoded secret detection

### Dynamic Analysis
- **OWASP ZAP**: Web application scanner
- **Nikto**: Web server scanner
- **SQLMap**: SQL injection tool
- **Burp Suite**: Comprehensive testing

### Dependency Scanning
- **pip-audit**: Python vulnerability scanner
- **snyk**: Comprehensive dependency scanning
- **dependabot**: Automated dependency updates

## Security Metrics

### Track Security Posture
```python
security_metrics = {
    'vulnerabilities': {
        'critical': 0,
        'high': 0,
        'medium': 2,
        'low': 5
    },
    'coverage': {
        'static_analysis': 100,
        'dependency_scan': 100,
        'penetration_test': 85
    },
    'compliance': {
        'owasp_top_10': True,
        'pci_dss': False,
        'gdpr': True
    },
    'last_audit': '2024-01-15',
    'next_audit': '2024-04-15'
}
```

## Incident Response Plan

### Detection
1. Monitor security alerts
2. Review logs regularly
3. Set up intrusion detection

### Response
1. Isolate affected systems
2. Assess impact and scope
3. Collect evidence
4. Fix vulnerability
5. Test and deploy fix

### Recovery
1. Restore normal operations
2. Monitor for recurrence
3. Update documentation

### Post-Incident
1. Conduct post-mortem
2. Update security measures
3. Train team on lessons learned
4. Update incident response plan

## Security Documentation

### Security Policy Template
```markdown
# Security Policy

## Supported Versions
| Version | Supported |
|---------|-----------|
| 1.x     | ✅        |
| 0.x     | ❌        |

## Reporting a Vulnerability
Email: security@example.com
PGP Key: [public key]

## Response Time
- Critical: 24 hours
- High: 3 days
- Medium: 1 week
- Low: 2 weeks

## Disclosure Policy
Responsible disclosure with 90-day deadline
```

## Quality Gates
- [ ] No critical vulnerabilities
- [ ] No high vulnerabilities in production
- [ ] All dependencies updated
- [ ] Security headers configured
- [ ] Authentication properly implemented
- [ ] Input validation comprehensive
- [ ] Security tests passing
- [ ] Documentation updated
