# Operational Governance Document

## Real-Time Cyber Anomaly Detection System

**Version:** 1.1
**Date:** 2025-12-11
**Authors:** Francesca Craievich, Lucas Jakin, Francesco Rumiz

---

## 1. Introduction

This document describes how the team managed version control, branching, and collaboration throughout the project development.

---

## 2. Version Control

**System**: Git
**Platform**: GitHub
**Repository**: https://github.com/francescacraievich/real-time-cyber-anomaly-detection

---

## 3. Branching Strategy

The team followed a **feature branch workflow** with the following branch structure:

### 3.1 Main Branch
- `main`: Production-ready code, protected branch

### 3.2 Feature Branches Used

| Branch | Purpose |
|--------|---------|
| `feature/5-anomaly-detection-model-implementation` | OCSVM model development and training |
| `feature/4-add-new-features-for-data-engineering` | Feature engineering functions |
| `feature/streamlit-flask-integration` | Dashboard and API development |
| `feature/fix-module-imports` | Fix import issues and gzip support |

### 3.3 Other Branches

| Branch | Purpose |
|--------|---------|
| `docs/8-update-documentation` | Documentation updates (SSD, proposal, governance) |
| `fix/7-fix-formatter-classes` | Bug fixes for formatter classes |
| `test/6-add-tests-for-initializer-and-formatter-classes` | Unit tests for data processing |

### 3.4 Naming Convention
- `feature/<issue-number>-<description>` for new features
- `fix/<issue-number>-<description>` for bug fixes
- `docs/<issue-number>-<description>` for documentation
- `test/<issue-number>-<description>` for tests

---

## 4. Commit History (Examples)

Representative commits from the project:

```
docs: add MLOps exam documentation (SSD, proposal, governance)
code cleaning. Refactoring
model w/ hyper-parameter tuning and multiclass distinction (files) v4
Working model with hyper-parameter tuning. GridSearch
oneCSVM_model v3. Model tested with different parameters and samples of data
One Class SVM v2 with additional contamination parameter. Decent Performance
Data into csv. Working One Class SVM model
Fix module import errors and add gzip support
changes to df_formatting. Datasets ready
add calculate_ip_geolocation_features functions
add calculate_total_malicious_events_per_protocol function
```

---

## 5. Pull Requests

The team used Pull Requests for code integration:

| PR | Description |
|----|-------------|
| #15 | `feature/fix-module-imports` - Fix module import errors and add gzip support |
| #13 | `feature/4-add-new-features-for-data-engineering` - Feature engineering functions |

---

## 6. Issue Tracking

The team used **GitHub Issues** to track work items:

- Issues are linked to branches via naming convention (e.g., `feature/5-...` links to issue #5)
- Issues track features, bugs, documentation, and tests
- Branches are deleted after merge

---

## 7. CI/CD Pipeline

**Platform**: GitHub Actions

### 7.1 Workflows

**CI Workflow** (`.github/workflows/ci.yml`):
- **Trigger**: Push to all branches, Pull requests to `main`
- **Jobs**:
  - `docs`: Validates MkDocs documentation build
  - `test`: Runs linting and tests on Python 3.11 and 3.12

### 7.2 CI Jobs Details

**Documentation Job**:
- Checkout code
- Setup Python 3.11
- Install dependencies
- Run `mkdocs build --strict`

**Test Job**:
- Matrix strategy: Python 3.11, 3.12
- Install dependencies from `requirements.txt` and `requirements-dev.txt`
- **Linting**: black, isort, flake8 checks on `src/` and `tests/`
- **Testing**: pytest with coverage reporting
- **Coverage**: Upload to Codecov

### 7.3 Code Quality Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Black** | Code formatter | `pyproject.toml` (line-length: 88) |
| **isort** | Import sorter | `pyproject.toml` (profile: black) |
| **flake8** | Linter | `.flake8` (max-line-length: 88) |
| **Codecov** | Coverage reporting | `.codecov.yml` (patch target: 40%) |

### 7.4 Documentation Deployment
- **Target**: https://francescacraievich.github.io/real-time-cyber-anomaly-detection/
- **Trigger**: Push to `main` branch
- **Build**: MkDocs with Material theme

---

## 8. Model Versioning

Model artifacts are stored in `model/` directory:

| File | Description |
|------|-------------|
| `oneclass_svm_model.pkl` | Trained OCSVM model |
| `oneclass_svm_preprocessor.pkl` | Preprocessing pipeline (scaler + encoder) |
| `oneclass_svm_config.pkl` | Model configuration and hyperparameters |

---

## 9. Monitoring Stack

### 9.1 Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Prometheus** | Metrics collection | Docker container |
| **Grafana** | Visualization dashboards | Docker container |
| **prometheus-client** | Python metrics library | `src/monitoring/metrics.py` |

### 9.2 Docker Setup

```bash
# Start monitoring stack
cd monitoring/
docker-compose up -d
```

### 9.3 Dashboards

**Streamlit Dashboards** (deployed on Streamlit Cloud):
- [Real-time Anomaly Dashboard](https://dashboard-alerts.streamlit.app/) - Main visualization
- [ML Monitoring Dashboard](https://monitoring-model.streamlit.app/) - Model performance

---

## 10. Project Structure

```
├── src/                        # Source code
│   ├── dashboard/              # Streamlit apps and Flask API
│   ├── model/                  # ML model implementation
│   ├── monitoring/             # Prometheus metrics
│   └── feature_engineering/    # Data processing
├── tests/                      # Unit tests (116 tests)
├── monitoring/                 # Docker monitoring stack
├── data/                       # Datasets
└── docs/                       # Documentation
```

---

## 11. Testing

### 11.1 Test Structure

| Test Suite | Coverage |
|------------|----------|
| `test_precalculations/` | Feature calculation functions |
| `test_aggregations/` | Aggregation metrics |
| `test_formatters/` | Data formatters |
| `test_model/` | ML model and drift detection |
| `test_dashboard/` | Flask API tests |

### 11.2 Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=term

# Run specific test suite
pytest tests/test_model/
```

---

## 12. Security

### 12.1 Security Policy

The project includes a [SECURITY.md](https://github.com/francescacraievich/real-time-cyber-anomaly-detection/blob/main/SECURITY.md) file that defines:

- How to report vulnerabilities responsibly
- Security measures implemented
- Best practices for deployment

### 12.2 GitHub Security Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Code Scanning (CodeQL)** | Enabled | Automatic vulnerability detection |
| **Secret Scanning** | Enabled | Detects committed secrets |
| **Security Advisories** | Enabled | Vulnerability disclosure |
| **Dependabot Alerts** | Available | Dependency vulnerability alerts |

### 12.3 CI/CD Security

The CI workflow implements security best practices:

```yaml
permissions:
  contents: read  # Minimal permissions
```

This restricts the workflow to read-only access, preventing malicious code from modifying the repository.

### 12.4 Application Security Measures

| Measure | Implementation |
|---------|----------------|
| **No Debug Mode** | Flask runs with `debug=False` |
| **No Stack Traces** | Exceptions return generic messages |
| **Input Validation** | API endpoints validate parameters |
| **CORS Configuration** | Controlled cross-origin access |

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-29 | F. Craievich, L. Jakin, F. Rumiz | Initial governance document |
| 1.1 | 2025-12-11 | F. Craievich | Added CI/CD details, monitoring stack, testing section, project structure |
| 1.2 | 2025-12-11 | F. Craievich | Added security section |
