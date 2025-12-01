# Operational Governance & Versioning Document

## Real-Time Cyber Anomaly Detection System

**Version:** 1.0
**Date:** 2025-11-29
**Authors:** Francesca Craievich, Lucas Jakin, Francesco Rumiz

---

## 1. Introduction

### 1.1 Purpose
This document defines the operational governance, version control strategy, CI/CD processes, model lifecycle management, and monitoring procedures for the Real-Time Cyber Anomaly Detection System.

### 1.2 Scope
This document covers:
- Version control and branching strategy
- Continuous Integration/Continuous Deployment (CI/CD) pipeline
- Model lifecycle governance
- Deployment procedures
- Monitoring and alerting
- Incident response
- Change management
- Rollback procedures

### 1.3 Audience
- Development team members
- ML engineers and data scientists
- Operations personnel
- Project stakeholders

---

## 2. Version Control Strategy

### 2.1 Version Control System
**System**: Git
**Platform**: GitHub
**Repository**: https://github.com/francescacraievich/real-time-cyber-anomaly-detection

### 2.2 Branching Strategy

We follow a simplified **GitHub Flow** branching model optimized for continuous delivery:

#### 2.2.1 Branch Types

**main**
- Protected branch containing production-ready code
- All code in `main` is deployable
- Direct commits are prohibited
- Requires pull request approval
- All tests must pass before merge

**feature branches**
- Created from `main` for new features
- Naming convention: `feature/<issue-number>-<short-description>`
- Example: `feature/14-fix-module-imports`
- Short-lived (merged within 1-2 weeks)
- Deleted after successful merge

**bugfix branches**
- Created from `main` for bug fixes
- Naming convention: `bugfix/<issue-number>-<short-description>`
- Example: `bugfix/23-fix-gzip-support`
- Merged via pull request
- Deleted after successful merge

**hotfix branches**
- Created from `main` for critical production issues
- Naming convention: `hotfix/<issue-number>-<short-description>`
- Expedited review process
- Merged immediately after approval

#### 2.2.2 Branch Protection Rules

**main branch protections**:
- Require pull request reviews (minimum 1 approval)
- Require status checks to pass before merging
- Require branches to be up-to-date before merging
- Prohibit force pushes
- Prohibit deletions

### 2.3 Commit Message Convention

We follow the **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no functional changes)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(model): add One-Class SVM implementation

Implement OCSVM anomaly detection with RBF kernel.
Achieves 90.7% TPR and 10% FPR on validation set.

Closes #42
```

```
fix(data): add gzip support for compressed JSON files

Modified init_normal_traffic_df.py to handle .gz files
using gzip.open() for compressed data reading.

Fixes #14
```

### 2.4 Pull Request Process

#### 2.4.1 Creating Pull Requests

1. Create feature/bugfix branch from `main`
2. Implement changes with clear commits
3. Push branch to GitHub
4. Open pull request with:
   - Clear title describing the change
   - Description of what was changed and why
   - Link to related issue(s)
   - Screenshots/examples (if applicable)
   - Checklist of completed tasks

#### 2.4.2 PR Template

```markdown
## Summary
[Brief description of changes]

## Changes Made
- Change 1
- Change 2
- Change 3

## Related Issues
Closes #[issue number]

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CI/CD pipeline passes
```

#### 2.4.3 Code Review Guidelines

**Reviewers must check**:
- Code correctness and logic
- Test coverage and quality
- Documentation completeness
- Performance implications
- Security considerations
- Style and consistency

**Review timeline**: Within 24 hours for feature PRs, within 4 hours for hotfixes

#### 2.4.4 Merge Process

1. PR receives required approvals
2. All CI/CD checks pass
3. Branch is up-to-date with `main`
4. **Squash and merge** to keep clean commit history
5. Delete feature branch after merge
6. Linked issues are automatically closed

### 2.5 Semantic Versioning

**Version Format**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Incompatible API changes, major architecture changes
- **MINOR**: New features, backwards-compatible changes
- **PATCH**: Bug fixes, performance improvements

**Current Version**: 1.0.0

**Version History**:
- 1.0.0 (2025-11-29): Initial release with OCSVM model

**Upcoming**:
- 1.1.0: Real-time stream processing
- 2.0.0: Dashboard and notification system
- 3.0.0: Cloud deployment and distributed processing

### 2.6 Tagging Strategy

**Release tags**: `v1.0.0`, `v1.1.0`, `v2.0.0`
- Created on `main` branch after successful deployment
- Annotated tags with release notes
- Immutable (never deleted or force-updated)

**Example**:
```bash
git tag -a v1.0.0 -m "Release 1.0.0: Initial OCSVM anomaly detection system"
git push origin v1.0.0
```

---

## 3. CI/CD Pipeline

### 3.1 Continuous Integration

**Platform**: GitHub Actions
**Configuration**: `.github/workflows/ci.yml`

#### 3.1.1 CI Workflow Triggers

- **Push to `main`**: Full test suite and deployment
- **Pull requests**: Full test suite (no deployment)
- **Manual trigger**: Via GitHub Actions UI

#### 3.1.2 CI Pipeline Stages

**Stage 1: Code Quality Checks**
- Python syntax validation
- PEP 8 style checking (flake8)
- Import sorting (isort)
- Code formatting (black)

**Stage 2: Testing**
- Unit tests (pytest)
- Test coverage reporting
- Integration tests
- Performance benchmarks

**Stage 3: Documentation Build**
- MkDocs build validation
- Link checking
- Markdown linting

**Stage 4: Security Scanning**
- Dependency vulnerability scanning
- Secret detection
- Code security analysis

#### 3.1.3 CI Configuration Example

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Build documentation
        run: mkdocs build --strict

      - name: Deploy to GitHub Pages
        if: github.ref == 'refs/heads/main'
        run: mkdocs gh-deploy --force
```

### 3.2 Continuous Deployment

#### 3.2.1 Deployment Strategy

**Environment**: GitHub Pages (Documentation)
**Deployment Trigger**: Push to `main` branch
**Deployment Target**: https://francescacraievich.github.io/real-time-cyber-anomaly-detection/

#### 3.2.2 Deployment Process

1. Code merged to `main`
2. CI pipeline runs all tests
3. Tests pass successfully
4. Documentation builds without errors
5. MkDocs deploys to GitHub Pages
6. Deployment verification
7. Notification sent (optional)

#### 3.2.3 Deployment Checklist

- [ ] All tests pass in CI
- [ ] Code review completed and approved
- [ ] Documentation updated
- [ ] Version number incremented (if applicable)
- [ ] Release notes prepared
- [ ] Stakeholders notified

### 3.3 Pipeline Monitoring

**Metrics Tracked**:
- Build success rate
- Test pass rate
- Build duration
- Deployment frequency
- Time to recovery (MTTR)

**Alerts**:
- Failed builds → GitHub notifications
- Failed deployments → Email notifications
- Security vulnerabilities → GitHub Security Alerts

---

## 4. Model Lifecycle Governance

### 4.1 Model Development Workflow

```
Research → Development → Training → Validation → Deployment → Monitoring
    ↓          ↓             ↓           ↓            ↓            ↓
Experiment   Code      Train Model   Evaluate    Deploy to    Track
 Phase      Review                   Metrics     Production  Performance
```

### 4.2 Model Versioning

**Model Artifacts**:
- Trained model file (`.pkl` or `.joblib`)
- Training configuration (hyperparameters)
- Feature engineering pipeline
- Performance metrics
- Training dataset metadata

**Versioning Convention**: `model-<algorithm>-v<version>-<date>.pkl`

**Example**: `model-ocsvm-v1.0-20251129.pkl`

### 4.3 Model Registry

**Location**: `model/` directory
**Metadata File**: `model/model_registry.json`

```json
{
  "models": [
    {
      "version": "1.0",
      "algorithm": "OneClassSVM",
      "file": "oneCSVM_model.pkl",
      "trained_date": "2025-11-29",
      "training_samples": 10000,
      "performance": {
        "tpr": 0.907,
        "fpr": 0.10,
        "f1_score": 0.885
      },
      "hyperparameters": {
        "kernel": "rbf",
        "nu": 0.1,
        "gamma": "scale"
      },
      "status": "production"
    }
  ]
}
```

### 4.4 Model Training Pipeline

#### 4.4.1 Training Process

1. **Data Preparation**
   - Load normal traffic dataset
   - Apply preprocessing
   - Extract features
   - Validate data quality

2. **Model Training**
   - Initialize OCSVM with hyperparameters
   - Train on normal traffic baseline
   - Validate on holdout set
   - Calculate performance metrics

3. **Model Validation**
   - Evaluate on test set
   - Check performance thresholds (TPR ≥85%, FPR ≤15%)
   - Compare with current production model
   - Document results

4. **Model Promotion**
   - If validation passes → promote to production
   - Update model registry
   - Archive previous model version
   - Document deployment

#### 4.4.2 Retraining Triggers

**Scheduled Retraining**: Monthly on 1st of each month
**Event-based Retraining**:
- Performance degradation (accuracy < 80%)
- Data drift detection
- New attack patterns observed
- Manual trigger by ML engineer

### 4.5 Model Performance Monitoring

**Metrics to Monitor**:
- True Positive Rate (TPR)
- False Positive Rate (FPR)
- F1 Score
- Prediction latency
- Throughput (events/second)

**Monitoring Frequency**:
- Real-time: Latency, throughput
- Daily: TPR, FPR, F1 score
- Weekly: Model drift analysis
- Monthly: Comprehensive performance review

**Alert Thresholds**:
- TPR drops below 85% → Warning
- TPR drops below 80% → Critical (trigger retraining)
- FPR exceeds 20% → Warning
- Latency exceeds 150ms → Warning

### 4.6 Model Rollback Procedure

If deployed model shows performance issues:

1. **Detect Issue**: Monitoring alerts trigger
2. **Assess Impact**: Evaluate severity and scope
3. **Decision**: Rollback or hotfix
4. **Execute Rollback**:
   - Restore previous model version from archive
   - Update model registry
   - Verify restored model performance
5. **Investigate**: Root cause analysis
6. **Document**: Incident report and lessons learned
7. **Prevent**: Fix underlying issue and redeploy

**Rollback Time Target**: < 15 minutes

---

## 5. Environment Management

### 5.1 Development Environment

**Purpose**: Local development and experimentation
**Location**: Developer workstations
**Configuration**: `requirements.txt`
**Data**: Sample datasets (< 1000 records)

### 5.2 Testing Environment

**Purpose**: Integration and system testing
**Location**: GitHub Actions runners
**Configuration**: Same as production
**Data**: Full test datasets

### 5.3 Production Environment

**Purpose**: Live anomaly detection
**Location**: Deployment server (future)
**Configuration**: `requirements.txt` + production configs
**Data**: Live network traffic streams

### 5.4 Environment Parity

- All environments use identical Python version (3.11+)
- All environments use same dependency versions
- Configuration managed via environment variables
- Secrets stored in GitHub Secrets (never in code)

---

## 6. Dependency Management

### 6.1 Dependency Tracking

**File**: `requirements.txt`
**Format**: Pinned versions for reproducibility

```
pandas==2.3.3
numpy==2.3.5
ijson==3.4.0.post0
pytest==9.0.1
mkdocs==1.6.1
mkdocs-material==9.7.0
```

### 6.2 Dependency Updates

**Security updates**: Immediately upon vulnerability disclosure
**Minor updates**: Monthly review and update cycle
**Major updates**: Quarterly evaluation with testing

**Update Process**:
1. Review changelog for breaking changes
2. Update dependency version in `requirements.txt`
3. Run full test suite locally
4. Create PR with dependency update
5. CI validates compatibility
6. Merge after approval

### 6.3 Dependency Security

**Scanning Tool**: GitHub Dependabot
**Scan Frequency**: Daily
**Response Time**:
- Critical vulnerabilities: < 24 hours
- High vulnerabilities: < 7 days
- Medium/Low vulnerabilities: Next sprint

---

## 7. Data Governance

### 7.1 Data Privacy

**Principle**: Minimal data collection and retention

**Anonymization**:
- IP addresses hashed or masked when not required
- No storage of personally identifiable information (PII)
- Honeypot logs contain simulated/attack traffic only

### 7.2 Data Retention

**Training Data**: Retained indefinitely for model reproducibility
**Logs**: Retained for 90 days, then archived
**Model Artifacts**: All versions retained for 1 year
**Performance Metrics**: Retained indefinitely

### 7.3 Data Quality

**Validation Checks**:
- JSON schema validation
- Required field presence
- Data type consistency
- Value range validation
- Duplicate detection

**Quality Metrics**:
- Completeness: % of records with all required fields
- Consistency: % of records passing validation
- Timeliness: Data freshness (lag from collection to processing)

---

## 8. Monitoring & Alerting

### 8.1 System Monitoring

**Metrics Collected**:
- CPU utilization
- Memory usage
- Disk I/O
- Network throughput
- Process health

**Monitoring Tools** (Future):
- Prometheus for metrics collection
- Grafana for visualization
- Alertmanager for notifications

### 8.2 Application Monitoring

**Metrics Collected**:
- Prediction latency (p50, p95, p99)
- Throughput (events/second)
- Error rate
- Model inference time
- Feature extraction time

### 8.3 Alert Definitions

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| High Error Rate | Error rate > 5% | Critical | Investigate immediately |
| Low TPR | TPR < 85% | Warning | Review model |
| High FPR | FPR > 20% | Warning | Tune threshold |
| High Latency | p95 > 150ms | Warning | Optimize code |
| Model Unavailable | Model file missing | Critical | Restore from backup |
| Data Quality Issue | Validation fail > 10% | Warning | Check data source |

### 8.4 Incident Response

**Severity Levels**:
- **P0 (Critical)**: System down, data loss, security breach
- **P1 (High)**: Major feature broken, performance severely degraded
- **P2 (Medium)**: Minor feature broken, performance issue
- **P3 (Low)**: Cosmetic issue, minor bug

**Response Times**:
- P0: Immediate (< 15 minutes)
- P1: < 1 hour
- P2: < 4 hours
- P3: Next sprint

**Incident Process**:
1. **Detection**: Alert triggered or issue reported
2. **Triage**: Assess severity and assign owner
3. **Investigation**: Diagnose root cause
4. **Mitigation**: Apply temporary fix if needed
5. **Resolution**: Implement permanent fix
6. **Documentation**: Write incident report
7. **Prevention**: Update monitoring/processes

---

## 9. Change Management

### 9.1 Change Types

**Standard Changes**: Pre-approved, low-risk (dependency updates, documentation)
**Normal Changes**: Require review and approval (feature additions, refactoring)
**Emergency Changes**: Urgent, expedited process (critical bug fixes, security patches)

### 9.2 Change Approval Process

**Standard Changes**:
- Developer implements change
- Create PR with clear description
- Automated tests pass
- Merge after 1 approval

**Normal Changes**:
- RFC (Request for Comments) if significant
- Design review (if architectural)
- Code review by 1+ team members
- Testing validation
- Stakeholder notification

**Emergency Changes**:
- Immediate notification to team
- Minimal viable fix implemented
- Expedited review (< 1 hour)
- Deploy with monitoring
- Post-mortem within 24 hours

### 9.3 Release Process

**Release Cadence**: Continuous delivery (every merge to `main`)
**Release Notes**: Auto-generated from commit messages
**Release Checklist**:
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number incremented
- [ ] Tag created
- [ ] Release notes published
- [ ] Stakeholders notified

---

## 10. Backup & Disaster Recovery

### 10.1 Backup Strategy

**Code**: Git repository on GitHub (remote backup)
**Models**: Versioned in `model/` directory, committed to Git
**Data**:
- Raw logs backed up to `tpot-data-backup.tar.gz`
- Processed datasets versioned with Git LFS (if large)

**Backup Frequency**:
- Code: Continuous (every commit)
- Models: On each new version
- Data: Weekly snapshots

### 10.2 Disaster Recovery

**Scenarios**:

**Scenario 1: Repository Deletion**
- **Recovery**: Clone from GitHub (remote backup)
- **RTO**: 5 minutes
- **RPO**: Last commit

**Scenario 2: Model File Corruption**
- **Recovery**: Restore from Git history
- **RTO**: 10 minutes
- **RPO**: Last model version

**Scenario 3: Data Loss**
- **Recovery**: Restore from `tpot-data-backup.tar.gz`
- **RTO**: 30 minutes
- **RPO**: Last backup (weekly)

**RTO**: Recovery Time Objective
**RPO**: Recovery Point Objective

### 10.3 Business Continuity

**Critical Functions**:
1. Anomaly detection capability
2. Model inference service
3. Alert generation

**Continuity Plan**:
- Keep production model file in separate secure location
- Maintain offline copy of critical data
- Document manual deployment procedure
- Test recovery procedures quarterly

---

## 11. Security & Compliance

### 11.1 Access Control

**Repository Access**:
- Public repository (open-source)
- Write access: Core team members only
- Admin access: Project manager

**Secrets Management**:
- Never commit secrets to repository
- Use GitHub Secrets for CI/CD credentials
- Rotate secrets quarterly

### 11.2 Security Best Practices

- Keep dependencies updated (Dependabot alerts)
- Run security scans on dependencies
- Code review for security issues
- Principle of least privilege
- Input validation and sanitization

### 11.3 Compliance

**Data Protection**:
- No PII collected or stored
- Honeypot data is non-personal (attack traffic)
- Comply with academic research ethics

**License**: Open-source (specify license in repository)

---

## 12. Documentation Standards

### 12.1 Documentation Types

**Code Documentation**:
- Docstrings for all functions and classes
- Inline comments for complex logic
- Type hints where applicable

**Technical Documentation**:
- System Specification Document (SSD)
- API documentation
- Architecture diagrams
- Deployment guides

**Operational Documentation**:
- This governance document
- Runbooks for common tasks
- Incident response playbooks
- Monitoring setup guides

**User Documentation**:
- README with quick start
- Tutorial notebooks
- Usage examples

### 12.2 Documentation Maintenance

- Update documentation with every code change
- Review documentation quarterly for accuracy
- Keep examples up-to-date and tested
- Version documentation alongside code

---

## 13. Performance Benchmarking

### 13.1 Benchmark Metrics

**System Performance**:
- Data loading time (target: < 5s for 10K samples)
- Feature extraction time (target: < 3s for 10K samples)
- Model training time (target: < 60s)
- Inference latency (target: < 100ms per event)
- Throughput (target: > 1000 events/sec)

### 13.2 Benchmarking Process

1. Define baseline metrics (current performance)
2. Run benchmarks on standard hardware
3. Document results in performance log
4. Track trends over time
5. Identify performance regressions in CI

### 13.3 Performance Regression Detection

- CI runs performance benchmarks on every PR
- Alert if performance degrades > 20%
- Investigate and optimize before merge
- Document performance-critical code sections

---

## 14. Maintenance & Support

### 14.1 Maintenance Windows

**Scheduled Maintenance**: First Sunday of each month, 2:00-4:00 AM UTC
**Duration**: Maximum 2 hours
**Notification**: 1 week advance notice

**Maintenance Activities**:
- Dependency updates
- Model retraining
- Database cleanup
- Log rotation
- Performance optimization

### 14.2 Support Procedures

**Issue Tracking**: GitHub Issues
**Response SLA**:
- Critical: < 4 hours
- High: < 1 day
- Medium: < 3 days
- Low: < 1 week

**Escalation Path**:
1. Developer → ML Engineer
2. ML Engineer → Data Scientist
3. Data Scientist → Project Manager

---

## 15. Glossary

| Term | Definition |
|------|------------|
| **CI/CD** | Continuous Integration/Continuous Deployment |
| **OCSVM** | One-Class Support Vector Machine |
| **TPR** | True Positive Rate (Detection Rate) |
| **FPR** | False Positive Rate (False Alarm Rate) |
| **RTO** | Recovery Time Objective |
| **RPO** | Recovery Point Objective |
| **SLA** | Service Level Agreement |
| **PR** | Pull Request |
| **DoD** | Definition of Done |
| **DoR** | Definition of Ready |

---

## Appendix A: Runbook Examples

### Runbook 1: Deploy New Model Version

```bash
# 1. Train new model
python model/oneCSVM_model.py

# 2. Validate performance
pytest tests/test_model_performance.py

# 3. Update model registry
# Edit model/model_registry.json

# 4. Commit changes
git add model/
git commit -m "feat(model): deploy OCSVM v1.1 with improved performance"

# 5. Create PR and merge
gh pr create --title "Deploy Model v1.1" --body "Performance: TPR=92%, FPR=8%"

# 6. Monitor deployment
# Check CI/CD pipeline status
```

### Runbook 2: Rollback Model

```bash
# 1. Identify previous working version
git log --oneline model/

# 2. Restore previous model file
git checkout <commit-hash> -- model/oneCSVM_model.pkl

# 3. Update model registry to mark as active
# Edit model/model_registry.json

# 4. Commit rollback
git commit -m "fix(model): rollback to v1.0 due to performance issue"

# 5. Push and deploy
git push origin main

# 6. Verify system health
# Check monitoring dashboards
```

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-29 | F. Craievich, L. Jakin, F. Rumiz | Initial governance document |
