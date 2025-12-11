# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Send an email to the project maintainers with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

## Security Measures

This project implements the following security practices:

### Code Security
- **Static Analysis**: GitHub CodeQL scans for vulnerabilities
- **Secret Scanning**: Enabled to detect accidentally committed secrets
- **Dependency Review**: Regular review of dependencies for known vulnerabilities

### CI/CD Security
- **Minimal Permissions**: GitHub Actions workflows use `contents: read` only
- **Pinned Actions**: Actions are pinned to specific versions
- **No Secrets in Logs**: Sensitive data is never logged

### Application Security
- **No Debug Mode**: Flask runs with `debug=False` in production
- **No Stack Traces**: Exceptions return generic error messages, not stack traces
- **Input Validation**: API endpoints validate input parameters

### Data Security
- **No PII Storage**: The system processes network metadata, not personal data
- **Local Processing**: All data processing happens locally
- **No External Data Transmission**: Model predictions stay local

## Security Best Practices for Users

When deploying this system:

1. **Network Isolation**: Run the system in an isolated network segment
2. **Access Control**: Restrict access to dashboards and API endpoints
3. **HTTPS**: Use HTTPS in production (configure reverse proxy)
4. **Secrets Management**: Never commit API keys or credentials
5. **Regular Updates**: Keep dependencies updated

## Dependencies

Key dependencies and their security status:

| Package | Purpose | Security Notes |
|---------|---------|----------------|
| Flask | REST API | Run with `debug=False` |
| Streamlit | Dashboards | Use authentication in production |
| scikit-learn | ML Model | No known vulnerabilities |
| pandas | Data processing | No known vulnerabilities |

## Vulnerability Disclosure Timeline

- **Day 0**: Vulnerability reported
- **Day 1-3**: Initial assessment and acknowledgment
- **Day 7-14**: Fix development and testing
- **Day 14-30**: Fix release and public disclosure

## Contact

For security concerns, contact the project maintainers through GitHub.

---

*This security policy was last updated on 2025-12-11.*
