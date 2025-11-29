# Project Proposal & Development Plan

## Real-Time Cyber Anomaly Detection System

**Version:** 1.0
**Date:** 2025-11-29
**Team:** Francesca Craievich (PM), Lucas Jakin (ML Engineer), Francesco Rumiz (Data Scientist)

---

## 1. Executive Summary

### 1.1 Project Overview
The Real-Time Cyber Anomaly Detection System is a machine learning-based platform designed to identify malicious network traffic patterns and security threats in real-time. By analyzing logs from multiple honeypot sources (Dionaea, Suricata, Cowrie) and normal network traffic, the system employs One-Class SVM to distinguish between benign and anomalous network behavior.

### 1.2 Business Value
- **Proactive Threat Detection**: Identify security threats before they cause damage
- **Reduced Response Time**: Real-time anomaly detection enables immediate action
- **Cost Efficiency**: Automated detection reduces manual security monitoring effort
- **Research Contribution**: Advances understanding of cyber attack patterns

### 1.3 Success Metrics
- Detection Rate (TPR) ≥ 85%
- False Positive Rate (FPR) ≤ 15%
- Processing Latency ≤ 100ms per event
- System Uptime ≥ 99%
- Throughput ≥ 1,000 events/second

---

## 2. Project Scope

### 2.1 In Scope
- Data collection from TPOT honeypot platform
- Feature engineering pipeline for network traffic logs
- One-Class SVM model training and deployment
- Anomaly detection inference engine
- Basic alert generation mechanism
- Documentation and testing infrastructure
- CI/CD pipeline for automated deployment

### 2.2 Out of Scope (Future Phases)
- Real-time stream processing (Kafka/MQTT integration)
- Interactive dashboard (Streamlit/Grafana)
- Multi-model ensemble approaches
- Cloud deployment infrastructure
- Advanced alert notification systems (email, Slack)
- User authentication and access control

### 2.3 Deliverables

| Deliverable | Description | Owner |
|-------------|-------------|-------|
| **D1: Data Collection Pipeline** | Scripts to extract and preprocess honeypot logs | Data Scientist |
| **D2: Feature Engineering Module** | Statistical feature extraction from network traffic | Data Scientist |
| **D3: ML Model** | Trained One-Class SVM anomaly detection model | ML Engineer |
| **D4: Inference Engine** | Real-time classification service | ML Engineer |
| **D5: Testing Suite** | Unit and integration tests (pytest) | All Team |
| **D6: Documentation** | Technical documentation (MkDocs) | Project Manager |
| **D7: CI/CD Pipeline** | GitHub Actions workflows | ML Engineer |
| **D8: System Specification** | SSD document | All Team |
| **D9: Development Plan** | This document | Project Manager |
| **D10: Operational Guide** | Governance and versioning document | Project Manager |

---

## 3. Project Timeline & Milestones

### 3.1 Development Phases

**Phase 1: Planning & Requirements (Week 1-2)**
- Requirements gathering and analysis
- System architecture design
- Technology stack selection
- Documentation setup

**Phase 2: Data Pipeline Development (Week 3-4)**
- Honeypot log collection from TPOT
- Data preprocessing and cleaning
- Feature engineering implementation
- DataFrame initialization modules

**Phase 3: Model Development (Week 5-6)**
- One-Class SVM implementation
- Model training and hyperparameter tuning
- Performance evaluation and validation
- Model persistence mechanism

**Phase 4: Integration & Testing (Week 7-8)**
- Component integration
- Unit and integration testing
- Performance benchmarking
- Bug fixing and optimization

**Phase 5: Documentation & Deployment (Week 9-10)**
- Technical documentation completion
- CI/CD pipeline setup
- GitHub Actions configuration
- Final testing and validation

### 3.2 Key Milestones

| Milestone | Target Date | Status | Deliverables |
|-----------|-------------|--------|--------------|
| M1: Project Kickoff | Week 1 | ✓ Completed | Requirements doc, team roles |
| M2: Data Collection Complete | Week 4 | ✓ Completed | Honeypot logs, normal traffic dataset |
| M3: Feature Engineering Ready | Week 5 | ✓ Completed | Feature extraction pipeline |
| M4: Model Training Complete | Week 6 | ✓ Completed | Trained OCSVM model (90.7% TPR) |
| M5: Testing Infrastructure | Week 7 | ✓ Completed | Pytest suite, CI/CD pipeline |
| M6: Documentation Published | Week 9 | In Progress | MkDocs site, SSD, proposal docs |
| M7: Final Delivery | Week 10 | Pending | Complete system, all documentation |

---

## 4. Work Breakdown Structure (WBS)

### 4.1 Level 1: Project Phases

```
1.0 Real-Time Cyber Anomaly Detection System
├── 1.1 Project Management
├── 1.2 Data Engineering
├── 1.3 Machine Learning
├── 1.4 Testing & Quality Assurance
├── 1.5 Documentation
└── 1.6 Deployment & Operations
```

### 4.2 Level 2: Detailed Tasks

**1.1 Project Management**
- 1.1.1 Requirements gathering and analysis
- 1.1.2 Team coordination and communication
- 1.1.3 Milestone tracking and reporting
- 1.1.4 Risk management
- 1.1.5 Documentation coordination

**1.2 Data Engineering**
- 1.2.1 Honeypot log collection (Dionaea, Suricata, Cowrie)
- 1.2.2 Normal traffic dataset acquisition
- 1.2.3 JSON parsing and preprocessing
- 1.2.4 Data validation and quality checks
- 1.2.5 Feature extraction pipeline
  - 1.2.5.1 Suricata feature extraction
  - 1.2.5.2 Normal traffic feature extraction
  - 1.2.5.3 Aggregation functions
  - 1.2.5.4 Precalculation utilities
- 1.2.6 DataFrame initialization modules
  - 1.2.6.1 Suricata DataFrame initializer
  - 1.2.6.2 Normal traffic DataFrame initializer
  - 1.2.6.3 Handler orchestration

**1.3 Machine Learning**
- 1.3.1 Algorithm selection and justification
- 1.3.2 One-Class SVM implementation
- 1.3.3 Hyperparameter tuning
  - 1.3.3.1 Kernel selection (RBF)
  - 1.3.3.2 Nu parameter optimization
  - 1.3.3.3 Gamma parameter tuning
- 1.3.4 Model training pipeline
- 1.3.5 Model evaluation and validation
- 1.3.6 Model persistence (pickle/joblib)
- 1.3.7 Inference engine development
- 1.3.8 Performance optimization

**1.4 Testing & Quality Assurance**
- 1.4.1 Unit test development (pytest)
- 1.4.2 Integration testing
- 1.4.3 Performance testing
- 1.4.4 Code quality checks
- 1.4.5 CI/CD pipeline configuration
  - 1.4.5.1 GitHub Actions workflow setup
  - 1.4.5.2 Automated testing jobs
  - 1.4.5.3 Documentation build jobs

**1.5 Documentation**
- 1.5.1 MkDocs setup and configuration
- 1.5.2 System Specification Document (SSD)
- 1.5.3 Project Proposal & Development Plan
- 1.5.4 Operational Governance Document
- 1.5.5 README and quick start guide
- 1.5.6 API documentation
- 1.5.7 Honeypot guide
- 1.5.8 Feature engineering documentation

**1.6 Deployment & Operations**
- 1.6.1 Environment setup (requirements.txt)
- 1.6.2 GitHub repository configuration
- 1.6.3 GitHub Pages deployment
- 1.6.4 Monitoring setup
- 1.6.5 Maintenance procedures

---

## 5. Sprint Planning (Agile Approach)

### 5.1 Sprint Overview
The project follows a 2-week sprint cycle with continuous delivery.

### Sprint 1: Foundation (Week 1-2)
**Goal**: Establish project infrastructure and data collection

**User Stories**:
- As a data scientist, I need to access honeypot logs so that I can analyze attack patterns
- As a team member, I need project documentation so that I understand system requirements

**Tasks**:
- Setup GitHub repository
- Configure development environment
- Extract logs from TPOT platform
- Create initial documentation structure

**Deliverables**: Project repository, raw log data, README

---

### Sprint 2: Data Pipeline (Week 3-4)
**Goal**: Build robust data processing pipeline

**User Stories**:
- As a data scientist, I need clean datasets so that I can train accurate models
- As a developer, I need modular code so that I can maintain the system

**Tasks**:
- Implement JSON parsing with ijson
- Create DataFrame initialization modules
- Handle gzip compression
- Add data validation

**Deliverables**: Data ingestion modules, preprocessed datasets

---

### Sprint 3: Feature Engineering (Week 5-6)
**Goal**: Extract meaningful features from network traffic

**User Stories**:
- As an ML engineer, I need statistical features so that I can train the model
- As a data scientist, I need feature documentation so that I understand the data

**Tasks**:
- Implement feature extraction functions
- Create aggregation utilities
- Build formatting pipeline
- Document feature definitions

**Deliverables**: Feature engineering module, feature documentation

---

### Sprint 4: Model Development (Week 7-8)
**Goal**: Train and validate One-Class SVM model

**User Stories**:
- As an ML engineer, I need a trained model so that I can detect anomalies
- As a security analyst, I need high accuracy so that I can trust the alerts

**Tasks**:
- Implement OCSVM training pipeline
- Tune hyperparameters
- Evaluate model performance
- Create model persistence mechanism

**Deliverables**: Trained model (90.7% TPR, 10% FPR, F1=0.885)

---

### Sprint 5: Testing & CI/CD (Week 9-10)
**Goal**: Ensure code quality and automated deployment

**User Stories**:
- As a developer, I need automated tests so that I can prevent regressions
- As a team lead, I need CI/CD so that deployment is reliable

**Tasks**:
- Write unit tests with pytest
- Configure GitHub Actions
- Setup documentation deployment
- Create test coverage reports

**Deliverables**: Test suite, CI/CD pipeline, deployed documentation

---

## 6. Definition of Done (DoD)

A task is considered complete when ALL criteria are met:

### 6.1 Code Criteria
- [ ] Code is written and follows Python best practices (PEP 8)
- [ ] Code is reviewed by at least one team member
- [ ] All functions have docstrings
- [ ] No hardcoded values (use configuration)
- [ ] Error handling is implemented

### 6.2 Testing Criteria
- [ ] Unit tests written and passing
- [ ] Test coverage ≥ 70% for new code
- [ ] Integration tests pass (if applicable)
- [ ] No regression in existing tests
- [ ] CI/CD pipeline passes all checks

### 6.3 Documentation Criteria
- [ ] Code is documented with clear comments
- [ ] README updated (if applicable)
- [ ] MkDocs documentation updated
- [ ] API documentation complete
- [ ] Examples/usage provided

### 6.4 Quality Criteria
- [ ] No critical bugs or security issues
- [ ] Performance requirements met
- [ ] Code is merged to main branch
- [ ] Feature is deployed (if applicable)

---

## 7. Definition of Ready (DoR)

A task can be started when ALL criteria are met:

### 7.1 Clarity Criteria
- [ ] User story is clearly defined
- [ ] Acceptance criteria are documented
- [ ] Dependencies are identified
- [ ] Technical approach is discussed

### 7.2 Resources Criteria
- [ ] Required data/resources are available
- [ ] Team member has capacity
- [ ] Necessary tools are accessible
- [ ] Blocking issues are resolved

### 7.3 Planning Criteria
- [ ] Task is properly estimated
- [ ] Priority is assigned
- [ ] Owner is identified
- [ ] Related tasks are understood

---

## 8. Resource Allocation

### 8.1 Team Structure

| Role | Team Member | Responsibilities | Time Allocation |
|------|-------------|------------------|-----------------|
| **Project Manager** | Francesca Craievich | Project planning, coordination, documentation, milestone tracking | 100% |
| **ML Engineer** | Lucas Jakin | Model development, deployment, CI/CD, performance optimization | 100% |
| **Data Scientist** | Francesco Rumiz | Data analysis, feature engineering, model validation, experimentation | 100% |

### 8.2 Tools & Infrastructure

**Development Tools**:
- Python 3.11+
- Visual Studio Code / PyCharm
- Git version control
- GitHub for collaboration

**Libraries & Frameworks**:
- pandas, numpy: Data processing
- scikit-learn: Machine learning
- pytest: Testing
- mkdocs: Documentation
- ijson: Streaming JSON parsing

**Infrastructure**:
- Local development machines
- GitHub repository: https://github.com/francescacraievich/real-time-cyber-anomaly-detection
- GitHub Actions: CI/CD
- GitHub Pages: Documentation hosting

### 8.3 Budget Considerations
This is an academic/research project with zero financial budget. All tools and services used are open-source or free-tier offerings.

---

## 9. Risk Management

### 9.1 Risk Register

| Risk ID | Description | Impact | Probability | Mitigation Strategy | Owner |
|---------|-------------|--------|-------------|---------------------|-------|
| R-01 | Team member unavailability | High | Medium | Cross-training, documentation | PM |
| R-02 | Data quality issues | High | Medium | Validation pipeline, quality checks | DS |
| R-03 | Model performance below target | High | Low | Hyperparameter tuning, algorithm exploration | ML |
| R-04 | Technical debt accumulation | Medium | Medium | Code reviews, refactoring sprints | All |
| R-05 | Scope creep | Medium | High | Strict scope management, backlog prioritization | PM |
| R-06 | Integration challenges | Medium | Low | Early integration testing, modular design | ML |
| R-07 | Documentation lag | Low | High | Continuous documentation, DoD enforcement | PM |

### 9.2 Dependency Management

**External Dependencies**:
- TPOT honeypot platform availability
- Python package ecosystem stability
- GitHub service uptime

**Internal Dependencies**:
- Data pipeline must complete before model training
- Feature engineering depends on data collection
- Testing requires completed implementations

---

## 10. Communication Plan

### 10.1 Team Meetings

**Daily Standups** (15 minutes)
- What did you do yesterday?
- What will you do today?
- Any blockers?

**Sprint Planning** (2 hours, bi-weekly)
- Review backlog
- Select sprint tasks
- Estimate effort
- Assign owners

**Sprint Review** (1 hour, bi-weekly)
- Demo completed work
- Gather feedback
- Update documentation

**Sprint Retrospective** (1 hour, bi-weekly)
- What went well?
- What needs improvement?
- Action items

### 10.2 Communication Channels

**Synchronous**:
- Video calls for meetings
- Pair programming sessions

**Asynchronous**:
- GitHub Issues for task tracking
- GitHub Pull Requests for code review
- GitHub Discussions for Q&A
- Email for formal communications

### 10.3 Documentation Repository

All project documentation is version-controlled in the `docs/` folder and published to GitHub Pages at:
https://francescacraievich.github.io/real-time-cyber-anomaly-detection/

---

## 11. Quality Assurance Plan

### 11.1 Code Quality Standards
- Follow PEP 8 style guide
- Use type hints where applicable
- Maximum function complexity: 10 (cyclomatic)
- Maximum file length: 500 lines
- Meaningful variable and function names

### 11.2 Testing Strategy

**Unit Testing**:
- Test coverage target: ≥70%
- Framework: pytest
- Automated via CI/CD

**Integration Testing**:
- End-to-end pipeline tests
- Module interaction validation

**Performance Testing**:
- Latency benchmarks (≤100ms)
- Throughput validation (≥1,000 events/sec)
- Memory profiling

### 11.3 Continuous Integration

**GitHub Actions Workflow**:
- Trigger: Push to main, pull requests
- Jobs:
  - Lint and format check
  - Unit tests (Python 3.11, 3.12)
  - Documentation build
  - Performance benchmarks

---

## 12. Success Criteria

The project is considered successful when:

### 12.1 Technical Criteria
- [ ] One-Class SVM model achieves ≥85% TPR with ≤15% FPR
- [ ] System processes ≥1,000 events/second
- [ ] Inference latency ≤100ms per event
- [ ] All unit tests pass with ≥70% coverage
- [ ] CI/CD pipeline is operational

### 12.2 Delivery Criteria
- [ ] All deliverables (D1-D10) are completed
- [ ] Documentation is published and accessible
- [ ] Code is merged to main branch
- [ ] System is deployable from repository

### 12.3 Documentation Criteria
- [ ] System Specification Document is complete
- [ ] Project Proposal & Development Plan is finalized
- [ ] Operational Governance Document is published
- [ ] All technical documentation is up-to-date

---

## 13. Future Roadmap

### 13.1 Version 2.0 Features
- Real-time stream processing with Kafka
- Interactive dashboard (Streamlit)
- Multi-model ensemble (Isolation Forest, Autoencoder)
- Advanced alert notification (Email, Slack, webhooks)

### 13.2 Version 3.0 Features
- Cloud deployment (AWS/Azure/GCP)
- Kubernetes orchestration
- Distributed processing with Apache Spark
- Time-series database integration (InfluxDB)
- Explainable AI (SHAP/LIME)

---

## Appendix A: Gantt Chart

```
Week  1  2  3  4  5  6  7  8  9  10
      |==|==|==|==|==|==|==|==|==|==|
Phase 1: Planning        [██]
Phase 2: Data Pipeline      [████]
Phase 3: Model Dev              [████]
Phase 4: Integration                [████]
Phase 5: Documentation                  [████]

Milestones:
M1 (Kickoff)             ▼
M2 (Data Complete)          ▼
M3 (Features Ready)             ▼
M4 (Model Trained)                  ▼
M5 (Testing Ready)                      ▼
M6 (Docs Published)                         ▼
M7 (Final Delivery)                             ▼
```

---

## Appendix B: Backlog Prioritization

### High Priority (Must Have)
- Data collection pipeline
- Feature engineering
- OCSVM model training
- Basic inference engine
- Core documentation

### Medium Priority (Should Have)
- Advanced feature extraction
- Model hyperparameter optimization
- Comprehensive testing
- Performance benchmarking
- CI/CD automation

### Low Priority (Could Have)
- Dashboard prototype
- Alert notification system
- Advanced logging
- Monitoring dashboards
- Model explainability

---

**Document Approval**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Manager | Francesca Craievich | | 2025-11-29 |
| ML Engineer | Lucas Jakin | | 2025-11-29 |
| Data Scientist | Francesco Rumiz | | 2025-11-29 |

---

**Document Version History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-29 | F. Craievich | Initial proposal creation |
