# Release Workflow

## Overview
Complete process for preparing, testing, and deploying a release.

## Workflow Steps

### 1. Release Planning
```bash
# Review milestone
Review all completed features and fixes

# Update version
Update version in pyproject.toml
```

**Planning Checklist:**
- [ ] All planned features complete
- [ ] All critical bugs fixed
- [ ] Release notes drafted
- [ ] Breaking changes documented
- [ ] Version number decided (SemVer)

### 2. Code Freeze
```bash
# Create release branch
git checkout -b release/v<x.y.z>

# No new features after this point
Only bug fixes and documentation updates allowed
```

**Freeze Rules:**
- No new features
- Bug fixes only for release blockers
- Documentation updates allowed
- Performance fixes if critical

### 3. Testing Phase
```bash
# Run full test suite
pytest tests/ -v --cov=src --cov-report=html

# Run integration tests
pytest tests/integration/ -v

# Run E2E tests
pytest tests/e2e/ -v

# Performance testing
python -m pytest tests/performance/ --benchmark-only
```

**Test Requirements:**
- [ ] Unit tests passing (100%)
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Performance benchmarks met
- [ ] Security scan clean
- [ ] Manual testing complete

### 4. Documentation Update
```bash
# Update documentation
/implement documentation update for release

# Files to update:
- README.md (version, features)
- CHANGELOG.md (release notes)
- docs/api/ (API changes)
- docs/migration/ (upgrade guide)
```

**Documentation Checklist:**
- [ ] CHANGELOG.md updated
- [ ] README.md version updated
- [ ] API docs regenerated
- [ ] Migration guide written
- [ ] Configuration changes documented
- [ ] Known issues listed

### 5. Build & Package
```bash
# Clean build directory
rm -rf dist/ build/

# Build distribution
python -m build

# Build Docker image
docker build -t rss-plex-manager:v<x.y.z> .

# Test installation
pip install dist/*.whl
python -c "import rss_plex_manager; print(rss_plex_manager.__version__)"
```

**Build Artifacts:**
- [ ] Python wheel built
- [ ] Source distribution created
- [ ] Docker image tagged
- [ ] Dependencies locked
- [ ] Checksums generated

### 6. Release Candidate
```bash
# Tag release candidate
git tag -a v<x.y.z>-rc1 -m "Release candidate 1"
git push origin v<x.y.z>-rc1

# Deploy to staging
Deploy to staging environment for final testing
```

**RC Testing:**
- [ ] Staging deployment successful
- [ ] Smoke tests passing
- [ ] User acceptance testing
- [ ] Performance validated
- [ ] Rollback tested

### 7. Final Release
```bash
# Merge to main
git checkout main
git merge --no-ff release/v<x.y.z>

# Tag release
git tag -a v<x.y.z> -m "Release version <x.y.z>"
git push origin main --tags

# Create GitHub release
gh release create v<x.y.z> \
  --title "Release v<x.y.z>" \
  --notes-file RELEASE_NOTES.md \
  dist/*
```

### 8. Deployment
```bash
# Deploy to production
./deploy.sh production v<x.y.z>

# Verify deployment
curl https://api.example.com/health
```

**Deployment Checklist:**
- [ ] Backup created
- [ ] Database migrations run
- [ ] Services restarted
- [ ] Health checks passing
- [ ] Monitoring alerts configured
- [ ] Rollback plan ready

### 9. Post-Release
```bash
# Merge back to develop
git checkout develop
git merge --no-ff main

# Update version for development
Update version to next development version

# Announce release
Post to relevant channels
```

**Communication:**
- [ ] Release notes published
- [ ] Team notified
- [ ] Users informed
- [ ] Social media updated
- [ ] Documentation site updated

## Release Types

### Major Release (x.0.0)
- Breaking changes
- Major features
- API incompatibilities
- Data migration required
- **Timeline**: 4-6 weeks

### Minor Release (0.x.0)
- New features
- Backward compatible
- Performance improvements
- **Timeline**: 2-3 weeks

### Patch Release (0.0.x)
- Bug fixes only
- Security patches
- No new features
- **Timeline**: 1-3 days

### Hotfix Release
- Critical bug fixes
- Security vulnerabilities
- Production issues
- **Timeline**: Hours

## Version Numbering

### Semantic Versioning
```
MAJOR.MINOR.PATCH

1.2.3
│ │ └── Patch: Bug fixes
│ └──── Minor: New features (backward compatible)
└────── Major: Breaking changes
```

### Pre-release Versions
- Alpha: `v1.0.0-alpha.1`
- Beta: `v1.0.0-beta.1`
- Release Candidate: `v1.0.0-rc.1`

## Release Notes Template
```markdown
# Release v<x.y.z>

Released: <date>

## 🎉 Highlights
- Major feature or improvement
- Another significant change

## ✨ Features
- feat: Add RSS feed filtering by quality (#123)
- feat: Implement Plex library organization (#124)

## 🐛 Bug Fixes
- fix: Resolve memory leak in feed parser (#125)
- fix: Handle malformed RSS feeds gracefully (#126)

## 🔧 Improvements
- perf: Optimize database queries (#127)
- refactor: Simplify configuration handling (#128)

## 📚 Documentation
- docs: Update API documentation (#129)
- docs: Add troubleshooting guide (#130)

## 💥 Breaking Changes
- API: Changed endpoint /feeds to /api/v2/feeds
- Config: Renamed setting 'feed_url' to 'feed_uri'

## 📦 Dependencies
- Upgraded fastapi from 0.104.0 to 0.105.0
- Added redis 5.0.0 for caching

## 🔄 Migration Guide
See [Migration Guide](docs/migration/v<x.y.z>.md)

## 🙏 Contributors
Thanks to all contributors who made this release possible!
```

## Rollback Plan

### Preparation
```bash
# Before deployment
- Backup database
- Save current version artifacts
- Document current configuration
- Test rollback procedure
```

### Rollback Steps
```bash
# If issues detected
1. Stop new deployments
2. Assess impact
3. Restore previous version
4. Restore database if needed
5. Verify services
6. Communicate status
```

### Post-Mortem
```markdown
## Incident Report
- **What happened**: Description
- **Impact**: Users/features affected
- **Root cause**: Technical explanation
- **Resolution**: How it was fixed
- **Prevention**: Future prevention measures
- **Timeline**: Key events and times
```

## Automation Scripts

### Release Script
```bash
#!/bin/bash
# release.sh

VERSION=$1
BRANCH="release/v${VERSION}"

# Create release branch
git checkout -b $BRANCH

# Update version
sed -i "s/version = .*/version = \"${VERSION}\"/" pyproject.toml

# Run tests
pytest tests/

# Build
python -m build

# Tag
git tag -a "v${VERSION}" -m "Release version ${VERSION}"

echo "Release v${VERSION} prepared"
```

## Quality Gates
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Release notes reviewed
- [ ] Security scan clean
- [ ] Performance validated
- [ ] Deployment tested in staging
- [ ] Rollback plan documented
- [ ] Team approval received
