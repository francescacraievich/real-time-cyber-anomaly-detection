# Operational Governance Document

## Real-Time Cyber Anomaly Detection System

**Version:** 1.0
**Date:** 2025-11-29
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
- **CI**: Runs tests on push to `main` and pull requests
- **Documentation**: Builds and deploys MkDocs to GitHub Pages

### 7.2 Documentation Deployment
- **Target**: https://francescacraievich.github.io/real-time-cyber-anomaly-detection/
- **Trigger**: Push to `main` branch

---

## 8. Model Versioning

Model artifacts are stored in `model/` directory:

| File | Description |
|------|-------------|
| `oneclass_svm_model.pkl` | Trained OCSVM model |
| `oneclass_svm_preprocessor.pkl` | Preprocessing pipeline (scaler + encoder) |
| `oneclass_svm_config.pkl` | Model configuration and hyperparameters |

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-29 | F. Craievich, L. Jakin, F. Rumiz | Initial governance document |
